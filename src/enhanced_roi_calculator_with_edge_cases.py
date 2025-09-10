"""
Enhanced ROI Calculator with Comprehensive Edge Case Handling
Integrates the EdgeCaseHandler with the main ROI Calculator for robust operation
"""

import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from decimal import Decimal

from roi_calculator import ROICalculator
from edge_case_handler import EdgeCaseHandler

logger = logging.getLogger(__name__)


class EnhancedROICalculator(ROICalculator):
    """
    Enhanced ROI Calculator with comprehensive edge case handling
    
    This class extends the base ROI Calculator with:
    - Input validation and sanitization
    - Edge case handling
    - Chilean market-specific validations
    - Error recovery and graceful degradation
    - Memory and performance monitoring
    """
    
    def __init__(self, strict_validation: bool = True, max_memory_mb: int = 1024):
        """
        Initialize Enhanced ROI Calculator
        
        Args:
            strict_validation: If True, fail on validation errors. If False, use corrected values.
            max_memory_mb: Maximum memory usage allowed
        """
        super().__init__()
        self.edge_handler = EdgeCaseHandler()
        self.strict_validation = strict_validation
        self.max_memory_mb = max_memory_mb
        self.validation_log = []
        self.calculation_start_time = None
        
    def calculate_roi(self, inputs: Dict) -> Dict:
        """
        Enhanced ROI calculation with comprehensive edge case handling
        
        Args:
            inputs: Dictionary of input parameters
            
        Returns:
            Dictionary with calculation results and validation information
        """
        self.calculation_start_time = time.time()
        
        try:
            # Step 1: Comprehensive input validation
            validation_result = self._validate_and_sanitize_inputs(inputs)
            
            if not validation_result['is_valid'] and self.strict_validation:
                return self._create_error_result(
                    "Input validation failed", 
                    validation_result['errors'],
                    validation_result['warnings']
                )
            
            # Step 2: Use validated/corrected inputs
            validated_inputs = validation_result['validated_inputs']
            
            # Step 3: Handle Chilean market specifics
            validated_inputs = self.edge_handler.handle_chilean_specifics(validated_inputs)
            
            # Step 4: Check memory usage before calculation
            if not self.edge_handler.check_memory_usage():
                logger.warning("High memory usage detected before calculation")
            
            # Step 5: Perform robust ROI calculation
            result = self._robust_roi_calculation(validated_inputs)
            
            # Step 6: Add validation information to result
            result['validation_info'] = {
                'input_errors': validation_result['errors'],
                'input_warnings': validation_result['warnings'] + self.edge_handler.warnings,
                'validation_passed': validation_result['is_valid'],
                'corrected_inputs': not validation_result['is_valid'],
                'processing_time_ms': (time.time() - self.calculation_start_time) * 1000,
                'memory_ok': self.edge_handler.check_memory_usage()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Unexpected error in enhanced ROI calculation: {e}")
            return self._create_error_result(
                f"Calculation failed: {str(e)}", 
                [str(e)],
                self.edge_handler.warnings
            )
    
    def _validate_and_sanitize_inputs(self, inputs: Dict) -> Dict:
        """
        Comprehensive validation and sanitization of inputs
        
        Args:
            inputs: Raw input dictionary
            
        Returns:
            Validation result with sanitized inputs
        """
        validation_result = self.edge_handler.validate_roi_inputs(inputs)
        
        # Additional business logic validation
        self._apply_business_rules_validation(validation_result)
        
        return validation_result
    
    def _apply_business_rules_validation(self, validation_result: Dict) -> None:
        """
        Apply business-specific validation rules
        
        Args:
            validation_result: Validation result to modify
        """
        validated_inputs = validation_result['validated_inputs']
        
        # Rule 1: Minimum viable business size
        annual_revenue = validated_inputs.get('annual_revenue', 0)
        if 0 < annual_revenue < 100000:  # Less than $100K
            validation_result['warnings'].append(
                f"Very small business size (${annual_revenue:,.0f} annual revenue). "
                "ROI calculations may not be meaningful."
            )
        
        # Rule 2: Service investment reasonableness
        service_investment = validated_inputs.get('service_investment', 0)
        if annual_revenue > 0:
            investment_ratio = service_investment / annual_revenue
            if investment_ratio > 0.5:  # More than 50% of revenue
                validation_result['warnings'].append(
                    f"Service investment ({service_investment:,.0f}) is {investment_ratio*100:.1f}% "
                    f"of annual revenue. This is unusually high."
                )
        
        # Rule 3: Order volume consistency
        monthly_orders = validated_inputs.get('monthly_orders', 0)
        avg_order_value = validated_inputs.get('avg_order_value', 0)
        if monthly_orders > 0 and avg_order_value > 0:
            calculated_monthly_revenue = monthly_orders * avg_order_value
            expected_monthly_revenue = annual_revenue / 12
            
            if expected_monthly_revenue > 0:
                revenue_variance = abs(calculated_monthly_revenue - expected_monthly_revenue) / expected_monthly_revenue
                if revenue_variance > 0.3:  # More than 30% variance
                    validation_result['warnings'].append(
                        f"Revenue calculation inconsistency: "
                        f"Orders×AOV = ${calculated_monthly_revenue:,.0f}/month, "
                        f"but annual revenue implies ${expected_monthly_revenue:,.0f}/month"
                    )
        
        # Rule 4: Cost structure reasonableness for industry
        industry = validated_inputs.get('industry', '').lower()
        total_monthly_costs = (
            validated_inputs.get('labor_costs', 0) +
            validated_inputs.get('shipping_costs', 0) +
            validated_inputs.get('error_costs', 0) +
            validated_inputs.get('inventory_costs', 0)
        )
        
        if annual_revenue > 0 and total_monthly_costs > 0:
            cost_ratio = (total_monthly_costs * 12) / annual_revenue
            
            # Industry-specific cost ratio expectations
            expected_cost_ratios = {
                'retail': (0.7, 0.9),
                'wholesale': (0.8, 0.95),
                'services': (0.6, 0.85),
                'manufacturing': (0.75, 0.9),
                'ecommerce': (0.65, 0.85),
                'e-commerce': (0.65, 0.85)
            }
            
            expected_range = expected_cost_ratios.get(industry, (0.6, 0.9))
            
            if cost_ratio < expected_range[0]:
                validation_result['warnings'].append(
                    f"Cost ratio ({cost_ratio*100:.1f}%) seems low for {industry} industry. "
                    f"Expected {expected_range[0]*100:.1f}%-{expected_range[1]*100:.1f}%"
                )
            elif cost_ratio > expected_range[1]:
                validation_result['warnings'].append(
                    f"Cost ratio ({cost_ratio*100:.1f}%) seems high for {industry} industry. "
                    f"Expected {expected_range[0]*100:.1f}%-{expected_range[1]*100:.1f}%"
                )
    
    def _robust_roi_calculation(self, inputs: Dict) -> Dict:
        """
        Perform ROI calculation with error handling and recovery
        
        Args:
            inputs: Validated input dictionary
            
        Returns:
            ROI calculation results
        """
        try:
            # Use the parent class calculation with error handling
            result = super().calculate_roi(inputs)
            
            # Add enhanced metrics
            result['enhanced_metrics'] = self._calculate_enhanced_metrics(inputs, result)
            
            # Add risk analysis
            result['risk_analysis'] = self._calculate_risk_analysis(inputs, result)
            
            return result
            
        except ZeroDivisionError as e:
            logger.error(f"Division by zero in ROI calculation: {e}")
            return self._create_fallback_calculation(inputs)
            
        except OverflowError as e:
            logger.error(f"Numerical overflow in ROI calculation: {e}")
            return self._create_fallback_calculation(inputs, "Numerical overflow - values too large")
            
        except Exception as e:
            logger.error(f"Unexpected error in robust ROI calculation: {e}")
            return self._create_fallback_calculation(inputs, str(e))
    
    def _calculate_enhanced_metrics(self, inputs: Dict, base_result: Dict) -> Dict:
        """
        Calculate additional metrics for enhanced analysis
        
        Args:
            inputs: Input parameters
            base_result: Base ROI calculation results
            
        Returns:
            Dictionary of enhanced metrics
        """
        enhanced = {}
        
        try:
            # Customer acquisition cost impact
            monthly_orders = inputs.get('monthly_orders', 0)
            if monthly_orders > 0:
                monthly_savings = base_result.get('roi_metrics', {}).get('monthly_savings', 0)
                savings_per_order = monthly_savings / monthly_orders
                enhanced['savings_per_order'] = savings_per_order
                enhanced['annual_orders'] = monthly_orders * 12
            
            # Revenue efficiency metrics
            annual_revenue = inputs.get('annual_revenue', 0)
            if annual_revenue > 0:
                annual_savings = base_result.get('roi_metrics', {}).get('annual_savings', 0)
                enhanced['savings_as_revenue_percentage'] = (annual_savings / annual_revenue) * 100
                enhanced['revenue_per_savings_dollar'] = annual_revenue / annual_savings if annual_savings > 0 else 0
            
            # Operational efficiency
            total_costs = (
                inputs.get('labor_costs', 0) +
                inputs.get('shipping_costs', 0) +
                inputs.get('error_costs', 0) +
                inputs.get('inventory_costs', 0)
            ) * 12
            
            if total_costs > 0:
                enhanced['cost_reduction_percentage'] = (base_result.get('roi_metrics', {}).get('annual_savings', 0) / total_costs) * 100
            
            # Investment efficiency
            service_investment = inputs.get('service_investment', 0)
            if service_investment > 0:
                annual_savings = base_result.get('roi_metrics', {}).get('annual_savings', 0)
                enhanced['savings_multiplier'] = annual_savings / service_investment
                enhanced['investment_recovery_years'] = service_investment / annual_savings if annual_savings > 0 else float('inf')
            
        except Exception as e:
            logger.warning(f"Error calculating enhanced metrics: {e}")
            enhanced['calculation_error'] = str(e)
        
        return enhanced
    
    def _calculate_risk_analysis(self, inputs: Dict, base_result: Dict) -> Dict:
        """
        Calculate risk factors and sensitivity analysis
        
        Args:
            inputs: Input parameters  
            base_result: Base ROI calculation results
            
        Returns:
            Dictionary of risk analysis results
        """
        risk_analysis = {}
        
        try:
            # Market risk factors
            annual_revenue = inputs.get('annual_revenue', 0)
            monthly_orders = inputs.get('monthly_orders', 0)
            
            # Revenue concentration risk
            if monthly_orders > 0:
                avg_order_value = inputs.get('avg_order_value', 0)
                if avg_order_value > 1000:  # High-value orders
                    risk_analysis['revenue_concentration_risk'] = 'High'
                    risk_analysis['risk_factors'] = risk_analysis.get('risk_factors', []) + [
                        'High average order value increases customer loss impact'
                    ]
                else:
                    risk_analysis['revenue_concentration_risk'] = 'Low'
            
            # Investment payback risk
            payback_months = base_result.get('roi_metrics', {}).get('payback_period_months', 0)
            if payback_months > 24:
                risk_analysis['payback_risk'] = 'High'
                risk_analysis['risk_factors'] = risk_analysis.get('risk_factors', []) + [
                    f'Long payback period ({payback_months:.1f} months) increases investment risk'
                ]
            elif payback_months > 12:
                risk_analysis['payback_risk'] = 'Medium'
            else:
                risk_analysis['payback_risk'] = 'Low'
            
            # Cost structure risk
            total_costs = (
                inputs.get('labor_costs', 0) +
                inputs.get('shipping_costs', 0) +
                inputs.get('error_costs', 0) +
                inputs.get('inventory_costs', 0)
            ) * 12
            
            if total_costs > 0 and annual_revenue > 0:
                cost_ratio = total_costs / annual_revenue
                if cost_ratio > 0.9:
                    risk_analysis['cost_structure_risk'] = 'High'
                    risk_analysis['risk_factors'] = risk_analysis.get('risk_factors', []) + [
                        f'High cost ratio ({cost_ratio*100:.1f}%) leaves little margin for error'
                    ]
                elif cost_ratio > 0.8:
                    risk_analysis['cost_structure_risk'] = 'Medium'
                else:
                    risk_analysis['cost_structure_risk'] = 'Low'
            
            # Sensitivity analysis
            risk_analysis['sensitivity_analysis'] = self._perform_sensitivity_analysis(inputs, base_result)
            
        except Exception as e:
            logger.warning(f"Error in risk analysis: {e}")
            risk_analysis['analysis_error'] = str(e)
        
        return risk_analysis
    
    def _perform_sensitivity_analysis(self, inputs: Dict, base_result: Dict) -> Dict:
        """
        Perform sensitivity analysis on key variables
        
        Args:
            inputs: Input parameters
            base_result: Base calculation results
            
        Returns:
            Sensitivity analysis results
        """
        sensitivity = {}
        
        try:
            base_roi = base_result.get('roi_metrics', {}).get('first_year_roi', 0)
            
            # Test sensitivity to key variables
            sensitivity_scenarios = {
                'revenue_down_20%': {'annual_revenue': inputs.get('annual_revenue', 0) * 0.8},
                'costs_up_20%': {
                    'labor_costs': inputs.get('labor_costs', 0) * 1.2,
                    'shipping_costs': inputs.get('shipping_costs', 0) * 1.2,
                    'error_costs': inputs.get('error_costs', 0) * 1.2,
                    'inventory_costs': inputs.get('inventory_costs', 0) * 1.2
                },
                'investment_up_50%': {'service_investment': inputs.get('service_investment', 0) * 1.5}
            }
            
            for scenario_name, changes in sensitivity_scenarios.items():
                try:
                    test_inputs = inputs.copy()
                    test_inputs.update(changes)
                    
                    # Quick calculation for sensitivity
                    test_calculator = ROICalculator()
                    test_result = test_calculator.calculate_roi(test_inputs)
                    
                    scenario_roi = test_result.get('roi_metrics', {}).get('first_year_roi', 0)
                    roi_change = scenario_roi - base_roi
                    
                    sensitivity[scenario_name] = {
                        'new_roi': scenario_roi,
                        'roi_change': roi_change,
                        'impact': 'High' if abs(roi_change) > 50 else 'Medium' if abs(roi_change) > 20 else 'Low'
                    }
                    
                except Exception as e:
                    sensitivity[scenario_name] = {'error': str(e)}
            
        except Exception as e:
            sensitivity['analysis_error'] = str(e)
        
        return sensitivity
    
    def _create_error_result(self, error_message: str, errors: List[str], warnings: List[str]) -> Dict:
        """
        Create standardized error result
        
        Args:
            error_message: Main error message
            errors: List of validation errors
            warnings: List of warnings
            
        Returns:
            Standardized error result dictionary
        """
        return {
            'success': False,
            'error': error_message,
            'validation_info': {
                'input_errors': errors,
                'input_warnings': warnings,
                'validation_passed': False,
                'processing_time_ms': (time.time() - self.calculation_start_time) * 1000 if self.calculation_start_time else 0,
                'memory_ok': self.edge_handler.check_memory_usage()
            },
            'calculation_date': datetime.now().isoformat()
        }
    
    def _create_fallback_calculation(self, inputs: Dict, error_msg: str = None) -> Dict:
        """
        Create fallback calculation when main calculation fails
        
        Args:
            inputs: Input parameters
            error_msg: Optional error message
            
        Returns:
            Fallback calculation result
        """
        try:
            # Simple fallback calculation
            annual_revenue = inputs.get('annual_revenue', 0)
            total_costs = (
                inputs.get('labor_costs', 0) +
                inputs.get('shipping_costs', 0) +
                inputs.get('error_costs', 0) +
                inputs.get('inventory_costs', 0)
            ) * 12
            
            service_investment = inputs.get('service_investment', 1)  # Avoid division by zero
            
            # Conservative estimates
            estimated_savings = total_costs * 0.3  # 30% savings estimate
            estimated_roi = ((estimated_savings - service_investment) / service_investment) * 100
            estimated_payback = service_investment / (estimated_savings / 12) if estimated_savings > 0 else 0
            
            return {
                'success': True,
                'fallback_calculation': True,
                'inputs': inputs,
                'roi_metrics': {
                    'first_year_roi': max(estimated_roi, -100),  # Cap negative ROI
                    'annual_savings': estimated_savings,
                    'monthly_savings': estimated_savings / 12,
                    'payback_period_months': min(estimated_payback, 120),  # Cap at 10 years
                    'payback_period_text': self._format_payback_period(estimated_payback)
                },
                'validation_info': {
                    'input_errors': [error_msg] if error_msg else [],
                    'input_warnings': ['Using fallback calculation due to calculation error'],
                    'validation_passed': False,
                    'fallback_used': True,
                    'processing_time_ms': (time.time() - self.calculation_start_time) * 1000 if self.calculation_start_time else 0,
                    'memory_ok': self.edge_handler.check_memory_usage()
                },
                'calculation_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Even fallback calculation failed: {e}")
            return self._create_error_result(
                "All calculation methods failed",
                [f"Fallback calculation error: {str(e)}"],
                ["System unable to perform any calculations"]
            )
    
    def get_validation_summary(self) -> Dict:
        """
        Get comprehensive validation summary
        
        Returns:
            Validation summary from edge case handler
        """
        return self.edge_handler.get_validation_summary()


def main():
    """Test the enhanced ROI calculator with various edge cases"""
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    calculator = EnhancedROICalculator()
    
    # Test cases with various edge conditions
    test_cases = [
        {
            'name': 'Normal case',
            'inputs': {
                'annual_revenue': 2000000,
                'monthly_orders': 5000,
                'avg_order_value': 33.33,
                'labor_costs': 8000,
                'shipping_costs': 5000,
                'error_costs': 2000,
                'inventory_costs': 3000,
                'service_investment': 50000,
                'company_name': 'Normal Company',
                'currency': 'USD'
            }
        },
        {
            'name': 'Chilean company with special characters',
            'inputs': {
                'annual_revenue': 5000000000,  # 5B CLP
                'monthly_orders': 10000,
                'avg_order_value': 41667,
                'labor_costs': 50000000,
                'shipping_costs': 30000000,
                'error_costs': 15000000,
                'inventory_costs': 20000000,
                'service_investment': 500000000,
                'company_name': 'José María & Asociados S.A.',
                'industry': 'Comercio Electrónico',
                'currency': 'CLP',
                'uf_amount': 1000,
                'inflation_rate': 0.15
            }
        },
        {
            'name': 'Zero revenue edge case',
            'inputs': {
                'annual_revenue': 0,
                'monthly_orders': 0,
                'avg_order_value': 0,
                'labor_costs': 5000,
                'shipping_costs': 3000,
                'error_costs': 2000,
                'inventory_costs': 2500,
                'service_investment': 25000,
                'company_name': 'Startup Company'
            }
        },
        {
            'name': 'Extreme values',
            'inputs': {
                'annual_revenue': float('inf'),
                'monthly_orders': -1000,
                'avg_order_value': 'invalid',
                'labor_costs': 1e20,
                'shipping_costs': None,
                'error_costs': '',
                'inventory_costs': '5,000.00',
                'service_investment': 'fifty thousand',
                'company_name': '<script>alert("XSS")</script>',
                'currency': 'INVALID'
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\n{'='*60}")
        print(f"Testing: {test_case['name']}")
        print('='*60)
        
        result = calculator.calculate_roi(test_case['inputs'])
        
        if result.get('success', True):
            print(f"✅ Calculation successful")
            if 'roi_metrics' in result:
                roi = result['roi_metrics']
                print(f"   ROI: {roi.get('first_year_roi', 'N/A'):.1f}%")
                print(f"   Annual Savings: ${roi.get('annual_savings', 0):,.2f}")
                print(f"   Payback: {roi.get('payback_period_text', 'N/A')}")
        else:
            print(f"❌ Calculation failed: {result.get('error', 'Unknown error')}")
        
        # Validation info
        validation = result.get('validation_info', {})
        if validation.get('input_errors'):
            print(f"   Errors: {len(validation['input_errors'])}")
        if validation.get('input_warnings'):
            print(f"   Warnings: {len(validation['input_warnings'])}")
        if validation.get('corrected_inputs'):
            print(f"   ⚠️  Inputs were corrected")
        
        print(f"   Processing time: {validation.get('processing_time_ms', 0):.1f}ms")
        print(f"   Memory OK: {validation.get('memory_ok', True)}")


if __name__ == "__main__":
    main()
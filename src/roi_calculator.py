"""
E-commerce Operations ROI Calculator
Comprehensive tool for calculating ROI on e-commerce operations consulting services
Includes Chilean market-specific calculations and 3-year projections
"""

import math
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

# Try to import numpy, but work without it if not available
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


class ROICalculator:
    """Main ROI Calculator class with Chilean market specifics"""
    
    # Chilean market constants
    IVA_RATE = 0.19  # 19% IVA in Chile
    INFLATION_RATE = 0.035  # Approximate Chilean inflation rate
    DISCOUNT_RATE = 0.12  # Cost of capital for NPV calculations
    
    # Industry improvement rates
    LABOR_REDUCTION_RATE = 0.60  # 60% labor cost reduction
    SHIPPING_OPTIMIZATION_RATE = 0.25  # 25% shipping cost reduction
    ERROR_ELIMINATION_RATE = 0.80  # 80% error cost reduction
    INVENTORY_OPTIMIZATION_RATE = 0.30  # 30% inventory cost reduction
    
    def __init__(self):
        self.results = {}
        
    def calculate_roi(self, inputs: Dict) -> Dict:
        """Main ROI calculation method"""
        
        # Validate inputs
        self._validate_inputs(inputs)
        
        # Extract and process inputs
        annual_revenue = inputs['annual_revenue']
        monthly_orders = inputs['monthly_orders']
        avg_order_value = inputs['avg_order_value']
        labor_costs = inputs['labor_costs']
        shipping_costs = inputs['shipping_costs']
        error_costs = inputs['error_costs']
        inventory_costs = inputs['inventory_costs']
        service_investment = inputs['service_investment']
        
        # Calculate current operational costs
        current_costs = self._calculate_current_costs(
            labor_costs, shipping_costs, error_costs, inventory_costs
        )
        
        # Calculate optimized costs after our intervention
        optimized_costs = self._calculate_optimized_costs(current_costs)
        
        # Calculate savings
        savings = self._calculate_savings(current_costs, optimized_costs)
        
        # Calculate ROI metrics
        roi_metrics = self._calculate_roi_metrics(
            savings, service_investment, annual_revenue
        )
        
        # Calculate 3-year projections
        projections = self._calculate_projections(
            savings, service_investment, annual_revenue
        )
        
        # Calculate NPV and IRR
        financial_metrics = self._calculate_financial_metrics(
            savings, service_investment
        )
        
        # Compile results
        self.results = {
            'inputs': inputs,
            'current_costs': current_costs,
            'optimized_costs': optimized_costs,
            'savings': savings,
            'roi_metrics': roi_metrics,
            'projections': projections,
            'financial_metrics': financial_metrics,
            'calculation_date': datetime.now().isoformat(),
            'chilean_specifics': {
                'iva_rate': self.IVA_RATE,
                'inflation_rate': self.INFLATION_RATE,
                'savings_with_iva': self._apply_iva(savings['annual_total'])
            }
        }
        
        return self.results
    
    def _validate_inputs(self, inputs: Dict) -> None:
        """Validate input parameters"""
        required_fields = [
            'annual_revenue', 'monthly_orders', 'avg_order_value',
            'labor_costs', 'shipping_costs', 'error_costs',
            'inventory_costs', 'service_investment'
        ]
        
        for field in required_fields:
            if field not in inputs:
                raise ValueError(f"Missing required field: {field}")
            if not isinstance(inputs[field], (int, float)) or inputs[field] < 0:
                raise ValueError(f"Invalid value for {field}: must be a positive number")
    
    def _calculate_current_costs(self, labor: float, shipping: float, 
                                errors: float, inventory: float) -> Dict:
        """Calculate current operational costs"""
        annual_labor = labor * 12
        annual_shipping = shipping * 12
        annual_errors = errors * 12
        annual_inventory = inventory * 12
        
        total_annual = annual_labor + annual_shipping + annual_errors + annual_inventory
        
        return {
            'labor': {
                'monthly': labor,
                'annual': annual_labor
            },
            'shipping': {
                'monthly': shipping,
                'annual': annual_shipping
            },
            'errors': {
                'monthly': errors,
                'annual': annual_errors
            },
            'inventory': {
                'monthly': inventory,
                'annual': annual_inventory
            },
            'total': {
                'monthly': total_annual / 12,
                'annual': total_annual
            }
        }
    
    def _calculate_optimized_costs(self, current_costs: Dict) -> Dict:
        """Calculate costs after optimization"""
        optimized = {}
        
        # Apply improvement rates
        labor_optimized = current_costs['labor']['annual'] * (1 - self.LABOR_REDUCTION_RATE)
        shipping_optimized = current_costs['shipping']['annual'] * (1 - self.SHIPPING_OPTIMIZATION_RATE)
        errors_optimized = current_costs['errors']['annual'] * (1 - self.ERROR_ELIMINATION_RATE)
        inventory_optimized = current_costs['inventory']['annual'] * (1 - self.INVENTORY_OPTIMIZATION_RATE)
        
        total_optimized = labor_optimized + shipping_optimized + errors_optimized + inventory_optimized
        
        return {
            'labor': {
                'monthly': labor_optimized / 12,
                'annual': labor_optimized
            },
            'shipping': {
                'monthly': shipping_optimized / 12,
                'annual': shipping_optimized
            },
            'errors': {
                'monthly': errors_optimized / 12,
                'annual': errors_optimized
            },
            'inventory': {
                'monthly': inventory_optimized / 12,
                'annual': inventory_optimized
            },
            'total': {
                'monthly': total_optimized / 12,
                'annual': total_optimized
            }
        }
    
    def _calculate_savings(self, current: Dict, optimized: Dict) -> Dict:
        """Calculate savings from optimization"""
        return {
            'labor': {
                'monthly': current['labor']['monthly'] - optimized['labor']['monthly'],
                'annual': current['labor']['annual'] - optimized['labor']['annual'],
                'percentage': self.LABOR_REDUCTION_RATE
            },
            'shipping': {
                'monthly': current['shipping']['monthly'] - optimized['shipping']['monthly'],
                'annual': current['shipping']['annual'] - optimized['shipping']['annual'],
                'percentage': self.SHIPPING_OPTIMIZATION_RATE
            },
            'errors': {
                'monthly': current['errors']['monthly'] - optimized['errors']['monthly'],
                'annual': current['errors']['annual'] - optimized['errors']['annual'],
                'percentage': self.ERROR_ELIMINATION_RATE
            },
            'inventory': {
                'monthly': current['inventory']['monthly'] - optimized['inventory']['monthly'],
                'annual': current['inventory']['annual'] - optimized['inventory']['annual'],
                'percentage': self.INVENTORY_OPTIMIZATION_RATE
            },
            'monthly_total': current['total']['monthly'] - optimized['total']['monthly'],
            'annual_total': current['total']['annual'] - optimized['total']['annual']
        }
    
    def _calculate_roi_metrics(self, savings: Dict, investment: float, 
                              annual_revenue: float) -> Dict:
        """Calculate ROI metrics"""
        annual_savings = savings['annual_total']
        
        # Basic ROI calculations
        roi_percentage = ((annual_savings - investment) / investment) * 100
        payback_period_months = investment / savings['monthly_total']
        
        # Revenue impact
        savings_as_revenue_percentage = (annual_savings / annual_revenue) * 100
        
        return {
            'first_year_roi': roi_percentage,
            'payback_period_months': payback_period_months,
            'payback_period_text': self._format_payback_period(payback_period_months),
            'annual_savings': annual_savings,
            'monthly_savings': savings['monthly_total'],
            'savings_vs_revenue_percentage': savings_as_revenue_percentage,
            'break_even_month': payback_period_months
        }
    
    def _calculate_projections(self, savings: Dict, investment: float, 
                             annual_revenue: float) -> Dict:
        """Calculate 3-year projections with inflation"""
        projections = {}
        cumulative_savings = 0
        
        for year in range(1, 4):
            # Apply inflation to savings (costs typically grow with inflation)
            inflated_savings = savings['annual_total'] * ((1 + self.INFLATION_RATE) ** year)
            cumulative_savings += inflated_savings
            
            # Net benefit (savings minus investment in year 1)
            net_benefit = inflated_savings - (investment if year == 1 else 0)
            cumulative_net_benefit = cumulative_savings - investment
            
            # ROI for this year
            year_roi = ((cumulative_net_benefit) / investment) * 100
            
            projections[f'year_{year}'] = {
                'savings': inflated_savings,
                'net_benefit': net_benefit,
                'cumulative_savings': cumulative_savings,
                'cumulative_net_benefit': cumulative_net_benefit,
                'roi_percentage': year_roi
            }
        
        return projections
    
    def _calculate_financial_metrics(self, savings: Dict, investment: float) -> Dict:
        """Calculate NPV and IRR"""
        annual_savings = savings['annual_total']
        
        # Cash flows: initial investment (negative) + 3 years of savings
        cash_flows = [-investment]
        for year in range(1, 4):
            inflated_savings = annual_savings * ((1 + self.INFLATION_RATE) ** year)
            cash_flows.append(inflated_savings)
        
        # Calculate NPV
        npv = self._calculate_npv(cash_flows, self.DISCOUNT_RATE)
        
        # Calculate IRR
        irr = self._calculate_irr(cash_flows)
        
        return {
            'npv': npv,
            'irr': irr,
            'cash_flows': cash_flows,
            'discount_rate': self.DISCOUNT_RATE
        }
    
    def _calculate_npv(self, cash_flows: List[float], discount_rate: float) -> float:
        """Calculate Net Present Value"""
        npv = 0
        for i, cash_flow in enumerate(cash_flows):
            npv += cash_flow / ((1 + discount_rate) ** i)
        return npv
    
    def _calculate_irr(self, cash_flows: List[float]) -> float:
        """Calculate Internal Rate of Return using Newton-Raphson method"""
        def npv_function(rate):
            return sum(cf / ((1 + rate) ** i) for i, cf in enumerate(cash_flows))
        
        def npv_derivative(rate):
            return sum(-i * cf / ((1 + rate) ** (i + 1)) for i, cf in enumerate(cash_flows))
        
        # Initial guess
        rate = 0.1
        
        # Newton-Raphson iteration
        for _ in range(100):
            npv_val = npv_function(rate)
            npv_deriv = npv_derivative(rate)
            
            if abs(npv_deriv) < 1e-10:
                break
                
            new_rate = rate - npv_val / npv_deriv
            
            if abs(new_rate - rate) < 1e-10:
                break
                
            rate = new_rate
        
        return rate
    
    def _apply_iva(self, amount: float) -> Dict:
        """Apply Chilean IVA calculations"""
        return {
            'amount_before_iva': amount,
            'iva_amount': amount * self.IVA_RATE,
            'amount_with_iva': amount * (1 + self.IVA_RATE)
        }
    
    def _format_payback_period(self, months: float) -> str:
        """Format payback period in human-readable format"""
        if months < 1:
            return f"{months * 30:.0f} days"
        elif months < 12:
            return f"{months:.1f} months"
        else:
            years = months / 12
            remaining_months = months % 12
            if remaining_months < 0.5:
                return f"{years:.1f} years"
            else:
                return f"{int(years)} years, {remaining_months:.1f} months"
    
    def get_summary_text(self) -> str:
        """Generate a summary text of the ROI calculation"""
        if not self.results:
            return "No calculation results available. Please run calculate_roi() first."
        
        roi = self.results['roi_metrics']
        projections = self.results['projections']
        financial = self.results['financial_metrics']
        
        summary = f"""
ROI CALCULATION SUMMARY
======================

Investment: ${self.results['inputs']['service_investment']:,.2f}
Annual Savings: ${roi['annual_savings']:,.2f}
Monthly Savings: ${roi['monthly_savings']:,.2f}

PAYBACK & ROI:
- Payback Period: {roi['payback_period_text']}
- First Year ROI: {roi['first_year_roi']:.1f}%
- 3-Year ROI: {projections['year_3']['roi_percentage']:.1f}%

FINANCIAL METRICS:
- Net Present Value: ${financial['npv']:,.2f}
- Internal Rate of Return: {financial['irr']*100:.1f}%

SAVINGS BREAKDOWN:
- Labor Reduction (60%): ${self.results['savings']['labor']['annual']:,.2f}/year
- Shipping Optimization (25%): ${self.results['savings']['shipping']['annual']:,.2f}/year
- Error Elimination (80%): ${self.results['savings']['errors']['annual']:,.2f}/year
- Inventory Optimization (30%): ${self.results['savings']['inventory']['annual']:,.2f}/year

Chilean Market Specifics:
- Savings with IVA (19%): ${self.results['chilean_specifics']['savings_with_iva']['amount_with_iva']:,.2f}
"""
        return summary
    
    def export_to_json(self, filename: Optional[str] = None) -> str:
        """Export results to JSON file"""
        if not filename:
            filename = f"roi_calculation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        return filename


if __name__ == "__main__":
    # Example usage
    calculator = ROICalculator()
    
    sample_inputs = {
        'annual_revenue': 2000000,  # $2M USD
        'monthly_orders': 5000,
        'avg_order_value': 33.33,
        'labor_costs': 8000,  # Monthly labor costs
        'shipping_costs': 5000,  # Monthly shipping costs
        'error_costs': 2000,  # Monthly error costs
        'inventory_costs': 3000,  # Monthly inventory costs
        'service_investment': 50000  # One-time service investment
    }
    
    results = calculator.calculate_roi(sample_inputs)
    print(calculator.get_summary_text())
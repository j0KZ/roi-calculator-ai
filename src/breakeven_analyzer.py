"""
Break-Even Analysis for ROI Calculator
Calculates break-even points, minimum viable metrics, and time-to-breakeven projections
"""

import math
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import logging

logger = logging.getLogger(__name__)


class BreakEvenAnalyzer:
    """Comprehensive break-even analysis for ROI calculations"""
    
    def __init__(self):
        """Initialize the break-even analyzer"""
        self.analysis_results = {}
    
    def analyze_breakeven_scenarios(self, roi_inputs: Dict, 
                                  variable_ranges: Optional[Dict] = None) -> Dict:
        """
        Comprehensive break-even analysis for all key variables
        
        Args:
            roi_inputs: Base ROI calculation inputs
            variable_ranges: Optional dict specifying ranges for sensitivity analysis
            
        Returns:
            Complete break-even analysis results
        """
        # Set default variable ranges if not provided
        if not variable_ranges:
            variable_ranges = self._get_default_variable_ranges(roi_inputs)
        
        analysis = {
            'base_scenario': roi_inputs.copy(),
            'breakeven_points': {},
            'minimum_viable_metrics': {},
            'time_to_breakeven': {},
            'sensitivity_analysis': {},
            'scenario_comparisons': [],
            'risk_assessment': {},
            'analysis_date': datetime.now().isoformat()
        }
        
        # Calculate break-even points for each variable
        analysis['breakeven_points'] = self._calculate_breakeven_points(roi_inputs)
        
        # Calculate minimum viable metrics
        analysis['minimum_viable_metrics'] = self._calculate_minimum_viable_metrics(roi_inputs)
        
        # Time-to-breakeven projections
        analysis['time_to_breakeven'] = self._calculate_time_to_breakeven(roi_inputs)
        
        # Sensitivity analysis
        analysis['sensitivity_analysis'] = self._perform_sensitivity_analysis(
            roi_inputs, variable_ranges
        )
        
        # Scenario comparisons
        analysis['scenario_comparisons'] = self._generate_scenario_comparisons(
            roi_inputs, variable_ranges
        )
        
        # Risk assessment
        analysis['risk_assessment'] = self._assess_breakeven_risks(roi_inputs, analysis)
        
        # Monte Carlo simulation for uncertainty analysis
        analysis['uncertainty_analysis'] = self._monte_carlo_breakeven_analysis(roi_inputs)
        
        self.analysis_results = analysis
        return analysis
    
    def _get_default_variable_ranges(self, roi_inputs: Dict) -> Dict:
        """Get default ranges for sensitivity analysis based on input values"""
        return {
            'annual_revenue': {
                'min': roi_inputs['annual_revenue'] * 0.5,
                'max': roi_inputs['annual_revenue'] * 2.0,
                'steps': 20
            },
            'service_investment': {
                'min': roi_inputs['service_investment'] * 0.5,
                'max': roi_inputs['service_investment'] * 2.0,
                'steps': 20
            },
            'labor_costs': {
                'min': roi_inputs['labor_costs'] * 0.5,
                'max': roi_inputs['labor_costs'] * 2.0,
                'steps': 15
            },
            'shipping_costs': {
                'min': roi_inputs['shipping_costs'] * 0.3,
                'max': roi_inputs['shipping_costs'] * 2.0,
                'steps': 15
            },
            'error_costs': {
                'min': roi_inputs['error_costs'] * 0.2,
                'max': roi_inputs['error_costs'] * 3.0,
                'steps': 15
            },
            'inventory_costs': {
                'min': roi_inputs['inventory_costs'] * 0.3,
                'max': roi_inputs['inventory_costs'] * 2.5,
                'steps': 15
            }
        }
    
    def _calculate_breakeven_points(self, roi_inputs: Dict) -> Dict:
        """Calculate break-even points for each key variable"""
        from roi_calculator import ROICalculator
        
        breakeven_points = {}
        base_calculator = ROICalculator()
        
        # Variables to analyze for break-even
        variables_to_analyze = [
            'service_investment', 'labor_costs', 'shipping_costs', 
            'error_costs', 'inventory_costs', 'annual_revenue'
        ]
        
        for variable in variables_to_analyze:
            try:
                breakeven_point = self._find_breakeven_point(
                    roi_inputs, variable, base_calculator
                )
                breakeven_points[variable] = breakeven_point
            except Exception as e:
                logger.error(f"Error calculating break-even for {variable}: {e}")
                breakeven_points[variable] = {
                    'error': str(e),
                    'breakeven_value': None
                }
        
        return breakeven_points
    
    def _find_breakeven_point(self, roi_inputs: Dict, variable: str, 
                            calculator: Any) -> Dict:
        """Find break-even point for a specific variable using binary search"""
        inputs = roi_inputs.copy()
        original_value = inputs[variable]
        
        # Define search range based on variable type
        if variable == 'service_investment':
            # For investment, find point where ROI = 0%
            min_val, max_val = original_value * 0.1, original_value * 10.0
        elif variable == 'annual_revenue':
            # For revenue, find minimum revenue needed for positive ROI
            min_val, max_val = original_value * 0.1, original_value * 3.0
        else:
            # For cost variables, find maximum cost that maintains positive ROI
            min_val, max_val = 0.0, original_value * 5.0
        
        # Binary search for break-even point
        tolerance = 0.01  # 1% tolerance
        max_iterations = 50
        
        for iteration in range(max_iterations):
            mid_val = (min_val + max_val) / 2.0
            inputs[variable] = mid_val
            
            try:
                results = calculator.calculate_roi(inputs)
                roi_percentage = results['roi_metrics']['first_year_roi']
                
                # Determine if we're above or below break-even
                if variable == 'service_investment':
                    # Higher investment = lower ROI
                    if roi_percentage > 0:
                        min_val = mid_val  # Can afford higher investment
                    else:
                        max_val = mid_val  # Investment too high
                elif variable == 'annual_revenue':
                    # Higher revenue = higher ROI
                    if roi_percentage > 0:
                        max_val = mid_val  # Can work with lower revenue
                    else:
                        min_val = mid_val  # Need higher revenue
                else:
                    # Higher costs = lower ROI
                    if roi_percentage > 0:
                        min_val = mid_val  # Can handle higher costs
                    else:
                        max_val = mid_val  # Costs too high
                
                # Check convergence
                if abs(max_val - min_val) < tolerance * original_value:
                    break
                    
            except Exception as e:
                # If calculation fails, adjust search bounds
                if variable in ['service_investment', 'annual_revenue']:
                    max_val = mid_val
                else:
                    min_val = mid_val
        
        breakeven_value = (min_val + max_val) / 2.0
        
        # Calculate final results at break-even point
        inputs[variable] = breakeven_value
        final_results = calculator.calculate_roi(inputs)
        
        return {
            'breakeven_value': round(breakeven_value, 2),
            'original_value': round(original_value, 2),
            'change_amount': round(breakeven_value - original_value, 2),
            'change_percentage': round(((breakeven_value - original_value) / original_value) * 100, 2),
            'roi_at_breakeven': round(final_results['roi_metrics']['first_year_roi'], 2),
            'payback_at_breakeven': round(final_results['roi_metrics']['payback_period_months'], 1),
            'interpretation': self._interpret_breakeven_point(variable, breakeven_value, original_value)
        }
    
    def _interpret_breakeven_point(self, variable: str, breakeven_value: float, 
                                 original_value: float) -> str:
        """Provide business interpretation of break-even point"""
        change_pct = ((breakeven_value - original_value) / original_value) * 100
        
        interpretations = {
            'service_investment': {
                'positive': f"Investment can increase by {abs(change_pct):.1f}% while maintaining positive ROI",
                'negative': f"Investment must decrease by {abs(change_pct):.1f}% to achieve break-even"
            },
            'annual_revenue': {
                'positive': f"Revenue can decrease by {abs(change_pct):.1f}% while maintaining positive ROI",
                'negative': f"Revenue must increase by {abs(change_pct):.1f}% to achieve break-even"
            },
            'labor_costs': {
                'positive': f"Labor costs can increase by {abs(change_pct):.1f}% while maintaining positive ROI",
                'negative': f"Labor costs must decrease by {abs(change_pct):.1f}% to achieve break-even"
            },
            'shipping_costs': {
                'positive': f"Shipping costs can increase by {abs(change_pct):.1f}% while maintaining positive ROI",
                'negative': f"Shipping costs must decrease by {abs(change_pct):.1f}% to achieve break-even"
            },
            'error_costs': {
                'positive': f"Error costs can increase by {abs(change_pct):.1f}% while maintaining positive ROI",
                'negative': f"Error costs must decrease by {abs(change_pct):.1f}% to achieve break-even"
            },
            'inventory_costs': {
                'positive': f"Inventory costs can increase by {abs(change_pct):.1f}% while maintaining positive ROI",
                'negative': f"Inventory costs must decrease by {abs(change_pct):.1f}% to achieve break-even"
            }
        }
        
        direction = 'positive' if change_pct >= 0 else 'negative'
        return interpretations.get(variable, {}).get(direction, "Break-even analysis completed")
    
    def _calculate_minimum_viable_metrics(self, roi_inputs: Dict) -> Dict:
        """Calculate minimum viable business metrics"""
        from roi_calculator import ROICalculator
        
        calculator = ROICalculator()
        base_results = calculator.calculate_roi(roi_inputs)
        
        # Calculate minimum viable metrics for different ROI targets
        roi_targets = [0, 15, 25, 50, 100]  # ROI percentages
        viable_metrics = {}
        
        for target_roi in roi_targets:
            metrics = self._find_minimum_metrics_for_roi(roi_inputs, target_roi, calculator)
            viable_metrics[f'roi_{target_roi}pct'] = metrics
        
        # Calculate minimum order volume and revenue
        viable_metrics['minimum_scale'] = self._calculate_minimum_scale_requirements(
            roi_inputs, calculator
        )
        
        return viable_metrics
    
    def _find_minimum_metrics_for_roi(self, roi_inputs: Dict, target_roi: float, 
                                    calculator: Any) -> Dict:
        """Find minimum metrics needed to achieve target ROI"""
        # This is a simplified approach - in practice, you might use optimization algorithms
        inputs = roi_inputs.copy()
        
        # Try different combinations to achieve target ROI
        scenarios = []
        
        # Scenario 1: Reduce investment
        try:
            min_investment = self._binary_search_for_target_roi(
                inputs, 'service_investment', target_roi, calculator, 'decrease'
            )
            scenarios.append({
                'approach': 'Reduce Investment',
                'service_investment': min_investment,
                'change_from_base': min_investment - inputs['service_investment']
            })
        except:
            pass
        
        # Scenario 2: Increase revenue
        try:
            min_revenue = self._binary_search_for_target_roi(
                inputs, 'annual_revenue', target_roi, calculator, 'increase'
            )
            scenarios.append({
                'approach': 'Increase Revenue',
                'annual_revenue': min_revenue,
                'change_from_base': min_revenue - inputs['annual_revenue']
            })
        except:
            pass
        
        # Scenario 3: Reduce labor costs
        try:
            max_labor_costs = self._binary_search_for_target_roi(
                inputs, 'labor_costs', target_roi, calculator, 'decrease'
            )
            scenarios.append({
                'approach': 'Reduce Labor Costs',
                'labor_costs': max_labor_costs,
                'change_from_base': max_labor_costs - inputs['labor_costs']
            })
        except:
            pass
        
        return {
            'target_roi_percentage': target_roi,
            'viable_scenarios': scenarios,
            'most_feasible': self._identify_most_feasible_scenario(scenarios) if scenarios else None
        }
    
    def _binary_search_for_target_roi(self, inputs: Dict, variable: str, 
                                    target_roi: float, calculator: Any,
                                    direction: str) -> float:
        """Binary search to find value that achieves target ROI"""
        original_value = inputs[variable]
        
        if direction == 'increase':
            min_val, max_val = original_value, original_value * 3.0
        else:
            min_val, max_val = original_value * 0.1, original_value
        
        tolerance = 0.01
        max_iterations = 30
        
        for _ in range(max_iterations):
            mid_val = (min_val + max_val) / 2.0
            test_inputs = inputs.copy()
            test_inputs[variable] = mid_val
            
            try:
                results = calculator.calculate_roi(test_inputs)
                actual_roi = results['roi_metrics']['first_year_roi']
                
                if abs(actual_roi - target_roi) < tolerance:
                    return mid_val
                
                if actual_roi < target_roi:
                    if direction == 'increase':
                        min_val = mid_val
                    else:
                        max_val = mid_val
                else:
                    if direction == 'increase':
                        max_val = mid_val
                    else:
                        min_val = mid_val
                        
            except:
                if direction == 'increase':
                    min_val = mid_val
                else:
                    max_val = mid_val
        
        return (min_val + max_val) / 2.0
    
    def _identify_most_feasible_scenario(self, scenarios: List[Dict]) -> Dict:
        """Identify the most feasible scenario based on business logic"""
        if not scenarios:
            return None
        
        # Score scenarios based on feasibility (lower change percentage is more feasible)
        for scenario in scenarios:
            change = abs(scenario.get('change_from_base', float('inf')))
            # Convert to percentage change (rough estimate)
            scenario['feasibility_score'] = change
        
        # Return scenario with lowest feasibility score (smallest change required)
        most_feasible = min(scenarios, key=lambda x: x.get('feasibility_score', float('inf')))
        return most_feasible
    
    def _calculate_minimum_scale_requirements(self, roi_inputs: Dict, 
                                           calculator: Any) -> Dict:
        """Calculate minimum scale requirements for viability"""
        # Calculate minimum monthly orders and revenue for break-even
        min_revenue = self._binary_search_for_target_roi(
            roi_inputs, 'annual_revenue', 0, calculator, 'decrease'
        )
        
        # Calculate corresponding minimum monthly orders
        avg_order_value = roi_inputs.get('avg_order_value', 1)
        min_monthly_orders = (min_revenue / 12) / avg_order_value if avg_order_value > 0 else 0
        
        return {
            'minimum_annual_revenue': round(min_revenue, 2),
            'minimum_monthly_revenue': round(min_revenue / 12, 2),
            'minimum_monthly_orders': round(min_monthly_orders, 0),
            'current_annual_revenue': roi_inputs['annual_revenue'],
            'revenue_gap': round(min_revenue - roi_inputs['annual_revenue'], 2),
            'revenue_gap_percentage': round(((min_revenue - roi_inputs['annual_revenue']) / roi_inputs['annual_revenue']) * 100, 2)
        }
    
    def _calculate_time_to_breakeven(self, roi_inputs: Dict) -> Dict:
        """Calculate detailed time-to-breakeven projections"""
        from roi_calculator import ROICalculator
        
        calculator = ROICalculator()
        results = calculator.calculate_roi(roi_inputs)
        
        monthly_savings = results['savings']['monthly_total']
        investment = roi_inputs['service_investment']
        
        if monthly_savings <= 0:
            return {
                'breakeven_impossible': True,
                'reason': 'Negative or zero monthly savings'
            }
        
        # Basic payback calculation
        basic_payback_months = investment / monthly_savings
        
        # More detailed month-by-month analysis
        monthly_analysis = []
        cumulative_savings = 0
        
        for month in range(1, int(basic_payback_months) + 12):  # Go a bit beyond basic payback
            # Apply inflation and learning curve effects
            monthly_savings_adjusted = monthly_savings * (1 + 0.003) ** month  # 0.3% monthly inflation
            cumulative_savings += monthly_savings_adjusted
            
            net_position = cumulative_savings - investment
            
            monthly_analysis.append({
                'month': month,
                'monthly_savings': round(monthly_savings_adjusted, 2),
                'cumulative_savings': round(cumulative_savings, 2),
                'net_position': round(net_position, 2),
                'breakeven_achieved': net_position >= 0
            })
        
        # Find exact breakeven month
        breakeven_month = None
        for analysis in monthly_analysis:
            if analysis['breakeven_achieved']:
                breakeven_month = analysis['month']
                break
        
        # Calculate different breakeven scenarios
        scenarios = {
            'conservative': self._calculate_scenario_breakeven(roi_inputs, 0.8),  # 80% of expected savings
            'realistic': self._calculate_scenario_breakeven(roi_inputs, 1.0),    # 100% of expected savings
            'optimistic': self._calculate_scenario_breakeven(roi_inputs, 1.2)    # 120% of expected savings
        }
        
        return {
            'basic_payback_months': round(basic_payback_months, 1),
            'detailed_breakeven_month': breakeven_month,
            'monthly_analysis': monthly_analysis[:24],  # First 24 months
            'scenario_analysis': scenarios,
            'risk_factors': self._identify_breakeven_risks(roi_inputs, results)
        }
    
    def _calculate_scenario_breakeven(self, roi_inputs: Dict, savings_multiplier: float) -> Dict:
        """Calculate breakeven for a specific savings scenario"""
        from roi_calculator import ROICalculator
        
        # Adjust inputs for scenario
        adjusted_inputs = roi_inputs.copy()
        
        calculator = ROICalculator()
        results = calculator.calculate_roi(adjusted_inputs)
        
        adjusted_monthly_savings = results['savings']['monthly_total'] * savings_multiplier
        investment = adjusted_inputs['service_investment']
        
        if adjusted_monthly_savings <= 0:
            return {'breakeven_months': float('inf'), 'feasible': False}
        
        breakeven_months = investment / adjusted_monthly_savings
        
        return {
            'savings_multiplier': savings_multiplier,
            'monthly_savings': round(adjusted_monthly_savings, 2),
            'breakeven_months': round(breakeven_months, 1),
            'feasible': True
        }
    
    def _identify_breakeven_risks(self, roi_inputs: Dict, results: Dict) -> List[str]:
        """Identify potential risks to achieving breakeven"""
        risks = []
        
        payback_months = results['roi_metrics']['payback_period_months']
        
        if payback_months > 24:
            risks.append("Long payback period (>24 months) increases business risk")
        
        if payback_months > 12:
            risks.append("Payback period exceeds 12 months - monitor cash flow carefully")
        
        # Check if savings are heavily dependent on one area
        savings = results['savings']
        total_savings = savings['annual_total']
        
        if savings['labor']['annual'] / total_savings > 0.7:
            risks.append("Heavy dependence on labor cost savings - ensure reliable implementation")
        
        if savings['errors']['annual'] / total_savings > 0.5:
            risks.append("Significant dependence on error reduction - may take time to achieve")
        
        # Check investment size relative to revenue
        investment_to_revenue_ratio = roi_inputs['service_investment'] / roi_inputs['annual_revenue']
        if investment_to_revenue_ratio > 0.1:
            risks.append("Investment represents >10% of annual revenue - ensure adequate cash flow")
        
        return risks
    
    def _perform_sensitivity_analysis(self, roi_inputs: Dict, 
                                    variable_ranges: Dict) -> Dict:
        """Perform sensitivity analysis on break-even points"""
        from roi_calculator import ROICalculator
        
        calculator = ROICalculator()
        sensitivity_results = {}
        
        for variable, range_config in variable_ranges.items():
            if variable not in roi_inputs:
                continue
            
            variable_analysis = []
            min_val = range_config['min']
            max_val = range_config['max']
            steps = range_config['steps']
            
            step_size = (max_val - min_val) / (steps - 1)
            
            for i in range(steps):
                test_value = min_val + i * step_size
                test_inputs = roi_inputs.copy()
                test_inputs[variable] = test_value
                
                try:
                    results = calculator.calculate_roi(test_inputs)
                    
                    variable_analysis.append({
                        'value': round(test_value, 2),
                        'roi_percentage': round(results['roi_metrics']['first_year_roi'], 2),
                        'payback_months': round(results['roi_metrics']['payback_period_months'], 1),
                        'annual_savings': round(results['savings']['annual_total'], 2),
                        'npv': round(results['financial_metrics']['npv'], 2)
                    })
                    
                except Exception as e:
                    logger.warning(f"Sensitivity analysis failed for {variable}={test_value}: {e}")
            
            if variable_analysis:
                sensitivity_results[variable] = {
                    'analysis_points': variable_analysis,
                    'sensitivity_score': self._calculate_sensitivity_score(variable_analysis),
                    'critical_thresholds': self._find_critical_thresholds(variable_analysis)
                }
        
        return sensitivity_results
    
    def _calculate_sensitivity_score(self, analysis_points: List[Dict]) -> float:
        """Calculate how sensitive ROI is to changes in this variable"""
        if len(analysis_points) < 2:
            return 0.0
        
        # Calculate coefficient of variation for ROI
        roi_values = [point['roi_percentage'] for point in analysis_points]
        mean_roi = sum(roi_values) / len(roi_values)
        
        if mean_roi == 0:
            return float('inf')
        
        variance = sum((roi - mean_roi) ** 2 for roi in roi_values) / len(roi_values)
        std_deviation = math.sqrt(variance)
        
        coefficient_of_variation = std_deviation / abs(mean_roi)
        return round(coefficient_of_variation, 4)
    
    def _find_critical_thresholds(self, analysis_points: List[Dict]) -> Dict:
        """Find critical thresholds (where ROI goes negative, etc.)"""
        thresholds = {}
        
        # Find break-even point (ROI = 0)
        for i, point in enumerate(analysis_points):
            if point['roi_percentage'] <= 0:
                if i > 0:
                    # Interpolate to find more precise break-even point
                    prev_point = analysis_points[i-1]
                    breakeven_value = self._interpolate_breakeven(
                        prev_point, point, 'roi_percentage', 0
                    )
                    thresholds['roi_breakeven'] = breakeven_value
                break
        
        # Find point where payback exceeds 24 months
        for point in analysis_points:
            if point['payback_months'] > 24:
                thresholds['long_payback_threshold'] = point['value']
                break
        
        return thresholds
    
    def _interpolate_breakeven(self, point1: Dict, point2: Dict, 
                             metric: str, target_value: float) -> float:
        """Interpolate to find precise break-even point"""
        y1, y2 = point1[metric], point2[metric]
        x1, x2 = point1['value'], point2['value']
        
        if y2 == y1:
            return x1
        
        # Linear interpolation
        x_target = x1 + (target_value - y1) * (x2 - x1) / (y2 - y1)
        return round(x_target, 2)
    
    def _generate_scenario_comparisons(self, roi_inputs: Dict, 
                                     variable_ranges: Dict) -> List[Dict]:
        """Generate comparison scenarios for break-even analysis"""
        from roi_calculator import ROICalculator
        
        calculator = ROICalculator()
        base_results = calculator.calculate_roi(roi_inputs)
        
        scenarios = [
            {
                'name': 'Base Case',
                'description': 'Current input assumptions',
                'inputs': roi_inputs.copy(),
                'results': base_results
            }
        ]
        
        # Conservative scenario (worse conditions)
        conservative_inputs = roi_inputs.copy()
        conservative_inputs['labor_costs'] *= 1.2
        conservative_inputs['shipping_costs'] *= 1.15
        conservative_inputs['error_costs'] *= 1.3
        conservative_inputs['service_investment'] *= 1.1
        
        try:
            conservative_results = calculator.calculate_roi(conservative_inputs)
            scenarios.append({
                'name': 'Conservative',
                'description': 'Higher costs and investment assumptions',
                'inputs': conservative_inputs,
                'results': conservative_results
            })
        except Exception as e:
            logger.warning(f"Conservative scenario calculation failed: {e}")
        
        # Optimistic scenario (better conditions)
        optimistic_inputs = roi_inputs.copy()
        optimistic_inputs['annual_revenue'] *= 1.2
        optimistic_inputs['labor_costs'] *= 0.9
        optimistic_inputs['shipping_costs'] *= 0.85
        optimistic_inputs['error_costs'] *= 0.8
        
        try:
            optimistic_results = calculator.calculate_roi(optimistic_inputs)
            scenarios.append({
                'name': 'Optimistic',
                'description': 'Higher revenue and lower cost assumptions',
                'inputs': optimistic_inputs,
                'results': optimistic_results
            })
        except Exception as e:
            logger.warning(f"Optimistic scenario calculation failed: {e}")
        
        # Add comparison metrics
        for scenario in scenarios[1:]:  # Skip base case
            scenario['comparison'] = self._compare_scenarios(
                base_results, scenario['results']
            )
        
        return scenarios
    
    def _compare_scenarios(self, base_results: Dict, scenario_results: Dict) -> Dict:
        """Compare scenario results to base case"""
        return {
            'roi_difference': round(
                scenario_results['roi_metrics']['first_year_roi'] - 
                base_results['roi_metrics']['first_year_roi'], 2
            ),
            'payback_difference': round(
                scenario_results['roi_metrics']['payback_period_months'] - 
                base_results['roi_metrics']['payback_period_months'], 1
            ),
            'savings_difference': round(
                scenario_results['savings']['annual_total'] - 
                base_results['savings']['annual_total'], 2
            ),
            'npv_difference': round(
                scenario_results['financial_metrics']['npv'] - 
                base_results['financial_metrics']['npv'], 2
            )
        }
    
    def _assess_breakeven_risks(self, roi_inputs: Dict, analysis: Dict) -> Dict:
        """Assess risks related to achieving break-even"""
        risks = {
            'high_risk_factors': [],
            'medium_risk_factors': [],
            'low_risk_factors': [],
            'overall_risk_score': 0
        }
        
        # Analyze payback period risk
        if 'time_to_breakeven' in analysis:
            payback_months = analysis['time_to_breakeven'].get('basic_payback_months', 0)
            
            if payback_months > 36:
                risks['high_risk_factors'].append("Very long payback period (>36 months)")
                risks['overall_risk_score'] += 3
            elif payback_months > 18:
                risks['medium_risk_factors'].append("Long payback period (>18 months)")
                risks['overall_risk_score'] += 2
            elif payback_months > 12:
                risks['low_risk_factors'].append("Moderate payback period (>12 months)")
                risks['overall_risk_score'] += 1
        
        # Analyze sensitivity risks
        if 'sensitivity_analysis' in analysis:
            for variable, sensitivity_data in analysis['sensitivity_analysis'].items():
                sensitivity_score = sensitivity_data.get('sensitivity_score', 0)
                
                if sensitivity_score > 2.0:
                    risks['high_risk_factors'].append(f"High sensitivity to {variable}")
                    risks['overall_risk_score'] += 2
                elif sensitivity_score > 1.0:
                    risks['medium_risk_factors'].append(f"Moderate sensitivity to {variable}")
                    risks['overall_risk_score'] += 1
        
        # Analyze investment size risk
        investment_ratio = roi_inputs['service_investment'] / roi_inputs['annual_revenue']
        if investment_ratio > 0.15:
            risks['high_risk_factors'].append("Investment >15% of annual revenue")
            risks['overall_risk_score'] += 2
        elif investment_ratio > 0.1:
            risks['medium_risk_factors'].append("Investment >10% of annual revenue")
            risks['overall_risk_score'] += 1
        
        # Overall risk assessment
        if risks['overall_risk_score'] >= 6:
            risks['risk_level'] = 'HIGH'
        elif risks['overall_risk_score'] >= 3:
            risks['risk_level'] = 'MEDIUM'
        else:
            risks['risk_level'] = 'LOW'
        
        return risks
    
    def _monte_carlo_breakeven_analysis(self, roi_inputs: Dict, 
                                      n_simulations: int = 1000) -> Dict:
        """Perform Monte Carlo simulation for break-even uncertainty analysis"""
        import random
        from roi_calculator import ROICalculator
        
        calculator = ROICalculator()
        simulation_results = []
        
        for _ in range(n_simulations):
            # Add random variations to inputs (normal distribution with 10% std dev)
            simulated_inputs = {}
            for key, value in roi_inputs.items():
                if isinstance(value, (int, float)) and value > 0:
                    # Add random variation (±20% with normal distribution)
                    std_dev = value * 0.1  # 10% standard deviation
                    simulated_value = max(0, random.gauss(value, std_dev))
                    simulated_inputs[key] = simulated_value
                else:
                    simulated_inputs[key] = value
            
            try:
                results = calculator.calculate_roi(simulated_inputs)
                simulation_results.append({
                    'roi_percentage': results['roi_metrics']['first_year_roi'],
                    'payback_months': results['roi_metrics']['payback_period_months'],
                    'annual_savings': results['savings']['annual_total'],
                    'npv': results['financial_metrics']['npv']
                })
            except:
                # Skip failed simulations
                continue
        
        if not simulation_results:
            return {'error': 'Monte Carlo simulation failed'}
        
        # Analyze simulation results
        roi_values = [r['roi_percentage'] for r in simulation_results]
        payback_values = [r['payback_months'] for r in simulation_results]
        
        return {
            'simulations_run': len(simulation_results),
            'roi_statistics': {
                'mean': round(sum(roi_values) / len(roi_values), 2),
                'min': round(min(roi_values), 2),
                'max': round(max(roi_values), 2),
                'percentile_10': round(sorted(roi_values)[int(len(roi_values) * 0.1)], 2),
                'percentile_90': round(sorted(roi_values)[int(len(roi_values) * 0.9)], 2)
            },
            'payback_statistics': {
                'mean': round(sum(payback_values) / len(payback_values), 1),
                'min': round(min(payback_values), 1),
                'max': round(max(payback_values), 1),
                'percentile_10': round(sorted(payback_values)[int(len(payback_values) * 0.1)], 1),
                'percentile_90': round(sorted(payback_values)[int(len(payback_values) * 0.9)], 1)
            },
            'probability_positive_roi': round(
                len([r for r in roi_values if r > 0]) / len(roi_values) * 100, 1
            ),
            'probability_payback_under_12m': round(
                len([p for p in payback_values if p <= 12]) / len(payback_values) * 100, 1
            )
        }
    
    def export_analysis(self, filename: Optional[str] = None) -> str:
        """Export break-even analysis results to JSON file"""
        if not filename:
            filename = f"breakeven_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(self.analysis_results, f, indent=2)
            logger.info(f"Break-even analysis exported to {filename}")
            return filename
        except Exception as e:
            logger.error(f"Error exporting analysis: {e}")
            raise
    
    def get_summary(self) -> str:
        """Get a text summary of the break-even analysis"""
        if not self.analysis_results:
            return "No analysis results available. Please run analyze_breakeven_scenarios() first."
        
        summary_lines = ["BREAK-EVEN ANALYSIS SUMMARY", "=" * 30, ""]
        
        # Time to break-even
        if 'time_to_breakeven' in self.analysis_results:
            time_data = self.analysis_results['time_to_breakeven']
            if 'basic_payback_months' in time_data:
                months = time_data['basic_payback_months']
                summary_lines.append(f"Payback Period: {months:.1f} months")
        
        # Risk assessment
        if 'risk_assessment' in self.analysis_results:
            risk_data = self.analysis_results['risk_assessment']
            risk_level = risk_data.get('risk_level', 'UNKNOWN')
            summary_lines.append(f"Risk Level: {risk_level}")
        
        # Key break-even points
        if 'breakeven_points' in self.analysis_results:
            summary_lines.append("\nKey Break-Even Points:")
            for variable, data in self.analysis_results['breakeven_points'].items():
                if 'breakeven_value' in data and data['breakeven_value'] is not None:
                    change_pct = data.get('change_percentage', 0)
                    summary_lines.append(f"  {variable}: {change_pct:+.1f}% change tolerance")
        
        # Monte Carlo results if available
        if 'uncertainty_analysis' in self.analysis_results:
            mc_data = self.analysis_results['uncertainty_analysis']
            if 'probability_positive_roi' in mc_data:
                prob = mc_data['probability_positive_roi']
                summary_lines.append(f"\nProbability of Positive ROI: {prob}%")
        
        return "\n".join(summary_lines)


def main():
    """Test the break-even analyzer"""
    analyzer = BreakEvenAnalyzer()
    
    # Sample inputs
    sample_inputs = {
        'annual_revenue': 2000000,
        'monthly_orders': 5000,
        'avg_order_value': 33.33,
        'labor_costs': 8000,
        'shipping_costs': 5000,
        'error_costs': 2000,
        'inventory_costs': 3000,
        'service_investment': 50000
    }
    
    print("Running break-even analysis...")
    results = analyzer.analyze_breakeven_scenarios(sample_inputs)
    
    print("\n" + analyzer.get_summary())
    
    # Show some key break-even points
    if 'breakeven_points' in results:
        print("\nDetailed Break-Even Points:")
        for variable, data in results['breakeven_points'].items():
            if 'interpretation' in data:
                print(f"  {variable}: {data['interpretation']}")


if __name__ == "__main__":
    main()
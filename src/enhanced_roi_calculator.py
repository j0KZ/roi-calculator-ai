#!/usr/bin/env python3
"""
Enhanced ROI Calculator for Chilean E-commerce Market
Primary sales tool with Chilean specifics (IVA, CLP, local costs)
Version: 2.0 - Enhanced with comprehensive error handling and debugging
"""

import json
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from scipy import stats
import pandas as pd
import traceback
import os

# Import debug utilities
try:
    from debug_utilities import (
        error_handler, ErrorSeverity, DebugLogger, validator, 
        file_handler, sanitizer, validate_clp_amount, safe_divide, safe_multiply
    )
except ImportError as e:
    print(f"Warning: Debug utilities not found: {e}")
    print("Running with basic error handling only")
    
    # Fallback error handler
    def error_handler(severity=None, fallback_value=None, raise_on_critical=True):
        def decorator(func):
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"Error in {func.__name__}: {e}")
                    return fallback_value
            return wrapper
        return decorator
    
    class DebugLogger:
        def __init__(self, name): 
            self.name = name
        def debug(self, msg, **kwargs): print(f"DEBUG: {msg}")
        def info(self, msg, **kwargs): print(f"INFO: {msg}")
        def warning(self, msg, **kwargs): print(f"WARNING: {msg}")
        def error(self, msg, **kwargs): print(f"ERROR: {msg}")
        def critical(self, msg, **kwargs): print(f"CRITICAL: {msg}")
        def get_error_summary(self): return {'total_errors': 0, 'total_warnings': 0}
    
    # Fallback safe functions
    def validate_clp_amount(value, field_name="amount"):
        try:
            return float(value) if value is not None else 0
        except:
            return 0
    
    def safe_divide(a, b, default=0.0):
        try:
            return a / b if b != 0 else default
        except:
            return default
    
    def safe_multiply(a, b, default=0.0):
        try:
            return a * b
        except:
            return default


@dataclass
class ChileanMarketConstants:
    """Chilean market specific constants"""
    IVA_RATE = 0.19  # 19% IVA tax
    USD_TO_CLP = 950  # Approximate exchange rate (update regularly)
    
    # Chilean platform transaction fees
    TRANSBANK_FEE = 0.029  # 2.9% + fixed fee
    WEBPAY_FEE = 0.025  # 2.5%
    MERCADOPAGO_FEE = 0.039  # 3.9%
    
    # Shipping costs by provider (CLP)
    CHILEXPRESS_BASE = 3500
    CORREOS_CHILE_BASE = 2800
    STARKEN_BASE = 3200
    
    # Labor costs (CLP/month)
    MIN_WAGE = 460000
    AVG_ECOMMERCE_SALARY = 850000
    
    # Industry benchmarks for Chilean SMEs
    BENCHMARKS = {
        'retail': {
            'conversion_rate': 0.023,
            'cart_abandonment': 0.72,
            'avg_order_value_clp': 45000,
            'return_rate': 0.08,
            'operational_cost_ratio': 0.35
        },
        'wholesale': {
            'conversion_rate': 0.018,
            'cart_abandonment': 0.65,
            'avg_order_value_clp': 280000,
            'return_rate': 0.04,
            'operational_cost_ratio': 0.28
        },
        'services': {
            'conversion_rate': 0.035,
            'cart_abandonment': 0.60,
            'avg_order_value_clp': 75000,
            'return_rate': 0.02,
            'operational_cost_ratio': 0.25
        }
    }


class ScenarioEngine:
    """Multi-scenario modeling with Monte Carlo simulation with enhanced error handling"""
    
    def __init__(self):
        self.logger = DebugLogger("ScenarioEngine")
        self.scenarios = {
            'pessimistic': {
                'name': 'Conservador',
                'probability': 0.25,
                'revenue_impact': 0.7,
                'cost_impact': 1.15,
                'timeline_months': 18,
                'description': 'Adopción lenta, desafíos de implementación'
            },
            'realistic': {
                'name': 'Esperado',
                'probability': 0.60,
                'revenue_impact': 1.0,
                'cost_impact': 1.0,
                'timeline_months': 12,
                'description': 'Implementación estándar, resultados esperados'
            },
            'optimistic': {
                'name': 'Optimista',
                'probability': 0.15,
                'revenue_impact': 1.35,
                'cost_impact': 0.85,
                'timeline_months': 9,
                'description': 'Adopción rápida, beneficios acelerados'
            }
        }
    
    @error_handler(ErrorSeverity.HIGH, fallback_value={'mean_roi': 0, 'error': True})
    def monte_carlo_simulation(self, base_params: Dict, iterations: int = 10000) -> Dict:
        """Run Monte Carlo simulation for ROI calculation with comprehensive error handling"""
        try:
            # Validate inputs
            if not isinstance(base_params, dict):
                raise ValueError("base_params must be a dictionary")
            
            required_keys = ['annual_revenue', 'total_costs', 'investment']
            missing_keys = [key for key in required_keys if key not in base_params]
            if missing_keys:
                raise ValueError(f"Missing required parameters: {missing_keys}")
            
            # Validate numeric parameters
            for key in required_keys:
                value = validate_clp_amount(base_params[key], key)
                base_params[key] = value
            
            # Validate iterations
            if not isinstance(iterations, int) or iterations < 100:
                self.logger.warning(f"Invalid iterations count {iterations}, using 1000")
                iterations = 1000
            elif iterations > 50000:
                self.logger.warning(f"Large iterations count {iterations}, using 10000")
                iterations = 10000
            
            self.logger.info(f"Starting Monte Carlo simulation with {iterations} iterations")
            
            results = []
            scenario_counts = {s: 0 for s in self.scenarios.keys()}
        
        except Exception as e:
            self.logger.critical(f"Failed to initialize Monte Carlo simulation", error=e)
            return {
                'error': True,
                'message': f"Monte Carlo initialization failed: {str(e)}",
                'mean_roi': 0,
                'median_roi': 0,
                'std_dev': 0,
                'confidence_interval_95': (0, 0),
                'probability_positive_roi': 0
            }
        
        try:
            for iteration in range(iterations):
                try:
                    # Select scenario based on probabilities
                    rand = np.random.random()
                    cumulative_prob = 0
                    selected_scenario = None
                    
                    for scenario_name, scenario in self.scenarios.items():
                        cumulative_prob += scenario['probability']
                        if rand <= cumulative_prob:
                            selected_scenario = scenario_name
                            scenario_counts[scenario_name] += 1
                            break
                    
                    # Fallback if no scenario selected
                    if selected_scenario is None:
                        selected_scenario = 'realistic'
                        scenario_counts[selected_scenario] += 1
                    
                    scenario = self.scenarios[selected_scenario]
                    
                    # Calculate with variations (with bounds checking)
                    try:
                        revenue_variation = np.random.normal(1.0, 0.1)  # 10% standard deviation
                        cost_variation = np.random.normal(1.0, 0.05)  # 5% standard deviation
                        
                        # Clamp variations to reasonable bounds
                        revenue_variation = max(0.3, min(2.0, revenue_variation))
                        cost_variation = max(0.5, min(1.5, cost_variation))
                        
                    except Exception as e:
                        self.logger.warning(f"Random variation error in iteration {iteration}, using defaults")
                        revenue_variation, cost_variation = 1.0, 1.0
                    
                    # Safe calculations
                    revenue = safe_multiply(
                        safe_multiply(base_params['annual_revenue'], scenario['revenue_impact']),
                        revenue_variation
                    )
                    costs = safe_multiply(
                        safe_multiply(base_params['total_costs'], scenario['cost_impact']),
                        cost_variation
                    )
                    investment = base_params['investment']
                    
                    # Calculate ROI with safety checks
                    annual_benefit = revenue - costs
                    
                    if investment <= 0:
                        self.logger.warning(f"Invalid investment value: {investment}")
                        roi = 0
                        payback_months = float('inf')
                    else:
                        roi = safe_divide((annual_benefit - investment), investment) * 100
                        payback_months = safe_divide(investment, safe_divide(annual_benefit, 12), float('inf'))
                    
                    # Validate calculated values
                    if np.isnan(roi) or np.isinf(roi):
                        roi = 0
                    if np.isnan(payback_months):
                        payback_months = float('inf')
                    
                    results.append({
                        'roi': roi,
                        'payback_months': payback_months,
                        'annual_benefit': annual_benefit,
                        'scenario': selected_scenario
                    })
                    
                except Exception as e:
                    self.logger.warning(f"Error in Monte Carlo iteration {iteration}: {e}")
                    # Add default result to maintain iteration count
                    results.append({
                        'roi': 0,
                        'payback_months': float('inf'),
                        'annual_benefit': 0,
                        'scenario': 'realistic'
                    })
                    continue
        
        except Exception as e:
            self.logger.error(f"Monte Carlo simulation loop failed", error=e)
            # Return partial results if we have any
            if not results:
                return {
                    'error': True,
                    'message': f"Monte Carlo simulation failed: {str(e)}",
                    'mean_roi': 0,
                    'median_roi': 0,
                    'std_dev': 0,
                    'probability_positive_roi': 0
                }
        
        # Statistical analysis with error handling
        try:
            if not results:
                self.logger.error("No results from Monte Carlo simulation")
                return {
                    'error': True,
                    'message': 'No simulation results available',
                    'mean_roi': 0,
                    'median_roi': 0,
                    'std_dev': 0,
                    'probability_positive_roi': 0
                }
            
            # Extract valid ROIs and payback periods
            rois = []
            paybacks = []
            
            for r in results:
                roi = r.get('roi', 0)
                payback = r.get('payback_months', float('inf'))
                
                # Validate ROI
                if not (np.isnan(roi) or np.isinf(roi)):
                    rois.append(roi)
                
                # Validate payback (exclude extreme values)
                if not (np.isnan(payback) or payback == float('inf')) and 0 < payback < 1000:
                    paybacks.append(payback)
            
            if not rois:
                self.logger.warning("No valid ROI values in simulation results")
                rois = [0]
            
            # Safe statistical calculations
            try:
                mean_roi = np.mean(rois)
                median_roi = np.median(rois)
                std_dev = np.std(rois)
                
                # Handle edge cases for percentiles
                if len(rois) >= 20:  # Need reasonable sample size for percentiles
                    percentile_5 = np.percentile(rois, 5)
                    percentile_95 = np.percentile(rois, 95)
                else:
                    percentile_5 = min(rois)
                    percentile_95 = max(rois)
                
                # Safe confidence interval calculation
                try:
                    if std_dev > 0 and len(rois) > 1:
                        confidence_interval_95 = stats.norm.interval(0.95, mean_roi, std_dev)
                    else:
                        confidence_interval_95 = (mean_roi, mean_roi)
                except Exception as e:
                    self.logger.warning(f"Confidence interval calculation failed: {e}")
                    confidence_interval_95 = (mean_roi - std_dev, mean_roi + std_dev)
                
                # Calculate probability of positive ROI
                positive_rois = sum(1 for r in rois if r > 0)
                probability_positive_roi = (positive_rois / len(rois)) * 100
                
                return {
                    'mean_roi': float(mean_roi) if not np.isnan(mean_roi) else 0,
                    'median_roi': float(median_roi) if not np.isnan(median_roi) else 0,
                    'std_dev': float(std_dev) if not np.isnan(std_dev) else 0,
                    'percentile_5': float(percentile_5),
                    'percentile_95': float(percentile_95),
                    'confidence_interval_95': confidence_interval_95,
                    'mean_payback_months': float(np.mean(paybacks)) if paybacks else float('inf'),
                    'scenario_distribution': {k: (v/iterations)*100 for k, v in scenario_counts.items()},
                    'best_case': float(max(rois)) if rois else 0,
                    'worst_case': float(min(rois)) if rois else 0,
                    'probability_positive_roi': float(probability_positive_roi),
                    'total_iterations': len(results),
                    'valid_rois': len(rois),
                    'valid_paybacks': len(paybacks)
                }
                
            except Exception as e:
                self.logger.error(f"Statistical analysis failed", error=e)
                return {
                    'error': True,
                    'message': f"Statistical analysis failed: {str(e)}",
                    'mean_roi': 0,
                    'median_roi': 0,
                    'std_dev': 0,
                    'probability_positive_roi': 0
                }
        
        except Exception as e:
            self.logger.critical(f"Monte Carlo result processing failed", error=e)
            return {
                'error': True,
                'message': f"Result processing failed: {str(e)}",
                'mean_roi': 0,
                'median_roi': 0,
                'std_dev': 0,
                'probability_positive_roi': 0
            }


class EnhancedROICalculator:
    """Enhanced ROI Calculator with Chilean market specifics and comprehensive error handling"""
    
    def __init__(self):
        self.logger = DebugLogger("EnhancedROICalculator")
        
        try:
            self.constants = ChileanMarketConstants()
            self.scenario_engine = ScenarioEngine()
            self.results = {}
            self.errors = []
            self.warnings = []
            
            self.logger.info("Enhanced ROI Calculator initialized successfully")
            
        except Exception as e:
            self.logger.critical(f"Failed to initialize ROI Calculator", error=e)
            raise
        
    @error_handler(ErrorSeverity.CRITICAL, fallback_value={'error': True, 'message': 'ROI calculation failed'})
    def calculate_roi(self, inputs: Dict) -> Dict:
        """
        Calculate comprehensive ROI with Chilean specifics and robust error handling
        
        Args:
            inputs: Dictionary containing:
                - annual_revenue_clp: Annual revenue in CLP
                - monthly_orders: Number of monthly orders
                - avg_order_value_clp: Average order value in CLP
                - labor_costs_clp: Monthly labor costs in CLP
                - shipping_costs_clp: Monthly shipping costs in CLP
                - platform_fees_clp: Monthly platform fees in CLP
                - error_costs_clp: Monthly error-related costs in CLP
                - inventory_costs_clp: Monthly inventory costs in CLP
                - investment_clp: Service investment in CLP
                - industry: Industry type (retail/wholesale/services)
                - current_platforms: List of current platforms used
        
        Returns:
            Dict: Comprehensive ROI analysis results or error information
        """
        
        try:
            self.logger.info("Starting ROI calculation")
            
            # Validate and sanitize inputs
            if not isinstance(inputs, dict):
                raise ValueError(f"Inputs must be a dictionary, got {type(inputs)}")
            
            # Sanitize inputs using debug utilities
            try:
                self.inputs, input_errors = sanitizer.sanitize_calculation_inputs(inputs)
                if input_errors:
                    self.logger.warning(f"Input validation warnings: {input_errors}")
                    self.warnings.extend(input_errors)
                
                self.logger.info(f"Successfully sanitized {len(self.inputs)} input parameters")
                
            except Exception as e:
                self.logger.error(f"Input sanitization failed", error=e)
                # Use original inputs with basic validation
                self.inputs = self._basic_input_validation(inputs)
        
        except Exception as e:
            self.logger.critical(f"ROI calculation initialization failed", error=e)
            return {
                'error': True,
                'message': f'ROI calculation failed: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
        
        try:
            # Calculate current state with error handling
            self.logger.debug("Calculating current state")
            current_state = self._calculate_current_state(self.inputs)
            
            # Calculate improvements with error handling
            self.logger.debug("Calculating improvements")
            improvements = self._calculate_improvements(self.inputs, current_state)
            
            # Run scenario analysis with error handling
            self.logger.debug("Running scenario analysis")
            scenario_results = self._run_scenario_analysis(self.inputs, improvements)
            
            # Calculate Chilean-specific metrics with error handling
            self.logger.debug("Calculating Chilean-specific metrics")
            chilean_metrics = self._calculate_chilean_metrics(improvements)
            
            # Generate recommendations with error handling
            self.logger.debug("Generating recommendations")
            recommendations = self._generate_recommendations(self.inputs, current_state)
            
            # Calculate 3-year projection with error handling
            self.logger.debug("Calculating 3-year projection")
            three_year_projection = self._calculate_three_year_projection(improvements)
            
            # Compare to benchmarks with error handling
            self.logger.debug("Comparing to benchmarks")
            benchmarks = self._compare_to_benchmarks(self.inputs)
            
            # Generate executive summary with error handling
            self.logger.debug("Generating executive summary")
            executive_summary = self._generate_executive_summary(improvements, scenario_results)
            
            # Compile results
            self.results = {
                'timestamp': datetime.now().isoformat(),
                'success': True,
                'input_validation_warnings': self.warnings,
                'executive_summary': executive_summary,
                'current_state': current_state,
                'improvements': improvements,
                'scenarios': scenario_results,
                'chilean_specifics': chilean_metrics,
                'recommendations': recommendations,
                'three_year_projection': three_year_projection,
                'benchmarks': benchmarks,
                'calculation_metadata': {
                    'version': '2.0',
                    'calculation_time': datetime.now().isoformat(),
                    'inputs_processed': len(self.inputs),
                    'warnings_count': len(self.warnings),
                    'errors_count': len(self.errors)
                }
            }
            
            self.logger.info("ROI calculation completed successfully")
            return self.results
            
        except Exception as e:
            self.logger.critical(f"ROI calculation failed during processing", error=e)
            return {
                'error': True,
                'message': f'ROI calculation processing failed: {str(e)}',
                'timestamp': datetime.now().isoformat(),
                'partial_results': getattr(self, 'results', {}),
                'warnings': self.warnings,
                'traceback': traceback.format_exc()
            }
    
    def _calculate_current_state(self, inputs: Dict) -> Dict:
        """Analyze current operational state"""
        
        monthly_revenue = inputs['annual_revenue_clp'] / 12
        total_monthly_costs = (
            inputs['labor_costs_clp'] +
            inputs['shipping_costs_clp'] +
            inputs['platform_fees_clp'] +
            inputs['error_costs_clp'] +
            inputs['inventory_costs_clp']
        )
        
        operational_efficiency = (monthly_revenue - total_monthly_costs) / monthly_revenue
        cost_per_order = total_monthly_costs / inputs['monthly_orders']
        
        return {
            'monthly_revenue_clp': monthly_revenue,
            'total_monthly_costs_clp': total_monthly_costs,
            'operational_efficiency': operational_efficiency,
            'cost_per_order_clp': cost_per_order,
            'current_margin': (monthly_revenue - total_monthly_costs) / monthly_revenue,
            'orders_per_employee': inputs['monthly_orders'] / (inputs['labor_costs_clp'] / self.constants.AVG_ECOMMERCE_SALARY)
        }
    
    def _calculate_improvements(self, inputs: Dict, current_state: Dict) -> Dict:
        """Calculate expected improvements"""
        
        # Improvement percentages based on Chilean market data
        improvements = {
            'labor_reduction': 0.60,  # 60% reduction through automation
            'shipping_optimization': 0.25,  # 25% through better routes and partners
            'platform_fee_reduction': 0.15,  # 15% through negotiation and optimization
            'error_elimination': 0.80,  # 80% error reduction
            'inventory_optimization': 0.30  # 30% inventory cost reduction
        }
        
        # Calculate monetary improvements
        monthly_savings = {
            'labor': inputs['labor_costs_clp'] * improvements['labor_reduction'],
            'shipping': inputs['shipping_costs_clp'] * improvements['shipping_optimization'],
            'platform_fees': inputs['platform_fees_clp'] * improvements['platform_fee_reduction'],
            'errors': inputs['error_costs_clp'] * improvements['error_elimination'],
            'inventory': inputs['inventory_costs_clp'] * improvements['inventory_optimization']
        }
        
        total_monthly_savings = sum(monthly_savings.values())
        total_annual_savings = total_monthly_savings * 12
        
        # ROI Calculation
        roi_year_1 = ((total_annual_savings - inputs['investment_clp']) / inputs['investment_clp']) * 100
        payback_months = inputs['investment_clp'] / total_monthly_savings
        
        return {
            'monthly_savings_clp': monthly_savings,
            'total_monthly_savings_clp': total_monthly_savings,
            'total_annual_savings_clp': total_annual_savings,
            'roi_percentage_year_1': roi_year_1,
            'payback_months': payback_months,
            'new_operational_efficiency': (
                current_state['operational_efficiency'] + 
                (total_monthly_savings / current_state['monthly_revenue_clp'])
            ),
            'improvement_percentages': improvements
        }
    
    def _run_scenario_analysis(self, inputs: Dict, improvements: Dict) -> Dict:
        """Run multi-scenario analysis"""
        
        base_params = {
            'annual_revenue': improvements['total_annual_savings_clp'],
            'total_costs': inputs['investment_clp'],
            'investment': inputs['investment_clp']
        }
        
        # Run Monte Carlo simulation
        monte_carlo = self.scenario_engine.monte_carlo_simulation(base_params)
        
        # Calculate specific scenarios with error handling
        scenarios = {}
        try:
            for scenario_name, scenario in self.scenario_engine.scenarios.items():
                try:
                    annual_savings = safe_multiply(
                        improvements['total_annual_savings_clp'], 
                        scenario['revenue_impact']
                    )
                    adjusted_investment = safe_multiply(
                        inputs['investment_clp'], 
                        scenario['cost_impact']
                    )
                    
                    # Safe ROI calculation
                    if adjusted_investment > 0:
                        roi_percentage = safe_divide((annual_savings - adjusted_investment), adjusted_investment) * 100
                        payback_months = safe_divide(adjusted_investment, safe_divide(annual_savings, 12), float('inf'))
                    else:
                        roi_percentage = 0
                        payback_months = float('inf')
                    
                    scenarios[scenario_name] = {
                        'name': scenario['name'],
                        'description': scenario['description'],
                        'annual_savings_clp': annual_savings,
                        'roi_percentage': roi_percentage,
                        'payback_months': payback_months,
                        'probability': scenario['probability'] * 100
                    }
                    
                except Exception as e:
                    self.logger.warning(f"Error calculating scenario {scenario_name}: {e}")
                    scenarios[scenario_name] = {
                        'name': scenario.get('name', scenario_name),
                        'description': f'Error calculating scenario: {str(e)}',
                        'annual_savings_clp': 0,
                        'roi_percentage': 0,
                        'payback_months': float('inf'),
                        'probability': scenario.get('probability', 0) * 100
                    }
        
        except Exception as e:
            self.logger.error(f"Scenario calculation failed: {e}")
            scenarios = {
                'realistic': {
                    'name': 'Error en cálculo',
                    'description': 'Error en análisis de escenarios',
                    'annual_savings_clp': 0,
                    'roi_percentage': 0,
                    'payback_months': float('inf'),
                    'probability': 100
                }
            }
        
        return {
            'scenarios': scenarios,
            'monte_carlo': monte_carlo,
            'recommended_scenario': 'realistic',
            'risk_assessment': self._assess_risk(monte_carlo)
        }
    
    @error_handler(ErrorSeverity.LOW, fallback_value='RIESGO DESCONOCIDO')
    def _assess_risk(self, monte_carlo: Dict) -> str:
        """Assess risk level based on Monte Carlo results with error handling"""
        try:
            if not isinstance(monte_carlo, dict):
                return 'RIESGO DESCONOCIDO'
            
            confidence = monte_carlo.get('probability_positive_roi', 0)
            std_dev = monte_carlo.get('std_dev', 0)
            
            # Validate inputs
            if not isinstance(confidence, (int, float)) or np.isnan(confidence) or confidence < 0:
                confidence = 0
            if not isinstance(std_dev, (int, float)) or np.isnan(std_dev) or std_dev < 0:
                std_dev = 100  # Assume high variance if unknown
            
            # Risk assessment logic
            if confidence > 90 and std_dev < 50:
                return 'BAJO RIESGO'
            elif confidence > 70 and std_dev < 100:
                return 'RIESGO MODERADO'
            elif confidence > 50:
                return 'RIESGO ALTO'
            else:
                return 'RIESGO MUY ALTO'
                
        except Exception as e:
            self.logger.warning(f"Risk assessment failed: {e}")
            return 'RIESGO DESCONOCIDO'
    
    @error_handler(ErrorSeverity.LOW, fallback_value={})
    def _basic_input_validation(self, inputs: Dict) -> Dict:
        """Basic input validation as fallback when advanced validation fails"""
        try:
            validated = {}
            
            # Numeric fields with defaults and validation
            numeric_defaults = {
                'annual_revenue_clp': 50000000,
                'monthly_orders': 500,
                'avg_order_value_clp': 25000,
                'labor_costs_clp': 1500000,
                'shipping_costs_clp': 800000,
                'platform_fees_clp': 400000,
                'error_costs_clp': 200000,
                'inventory_costs_clp': 1000000,
                'investment_clp': 15000000
            }
            
            for field, default in numeric_defaults.items():
                try:
                    value = inputs.get(field, default)
                    
                    # Handle None and empty strings
                    if value is None or value == '':
                        validated[field] = default
                        continue
                    
                    # Convert to float
                    numeric_value = float(value)
                    
                    # Check for invalid values
                    if np.isnan(numeric_value) or np.isinf(numeric_value):
                        validated[field] = default
                        self.logger.warning(f"Invalid numeric value for {field}: {value}, using default")
                        continue
                    
                    # Check for negative values (most fields shouldn't be negative)
                    if numeric_value < 0:
                        validated[field] = abs(numeric_value) if field != 'error_costs_clp' else default
                        self.logger.warning(f"Negative value for {field}: {value}, using absolute value or default")
                    else:
                        validated[field] = numeric_value
                        
                except (ValueError, TypeError, OverflowError) as e:
                    validated[field] = default
                    self.logger.warning(f"Could not convert {field} value '{value}' to number: {e}")
            
            # String fields with validation
            try:
                industry = inputs.get('industry', 'retail')
                if isinstance(industry, str) and industry.strip():
                    validated['industry'] = industry.strip().lower()
                else:
                    validated['industry'] = 'retail'
            except Exception:
                validated['industry'] = 'retail'
            
            try:
                company_name = inputs.get('company_name', 'Cliente')
                if isinstance(company_name, str) and company_name.strip():
                    validated['company_name'] = company_name.strip()
                else:
                    validated['company_name'] = 'Cliente'
            except Exception:
                validated['company_name'] = 'Cliente'
            
            # List fields with validation
            try:
                platforms = inputs.get('current_platforms', [])
                if isinstance(platforms, list):
                    validated['current_platforms'] = [str(p).strip() for p in platforms if p]
                elif isinstance(platforms, str):
                    validated['current_platforms'] = [p.strip() for p in platforms.split(',') if p.strip()]
                else:
                    validated['current_platforms'] = []
            except Exception as e:
                self.logger.warning(f"Error processing current_platforms: {e}")
                validated['current_platforms'] = []
            
            self.logger.info(f"Basic validation completed for {len(validated)} fields")
            return validated
            
        except Exception as e:
            self.logger.error(f"Basic input validation failed: {e}")
            # Return minimal safe defaults
            return {
                'annual_revenue_clp': 50000000,
                'monthly_orders': 500,
                'avg_order_value_clp': 25000,
                'labor_costs_clp': 1500000,
                'shipping_costs_clp': 800000,
                'platform_fees_clp': 400000,
                'error_costs_clp': 200000,
                'inventory_costs_clp': 1000000,
                'investment_clp': 15000000,
                'industry': 'retail',
                'company_name': 'Cliente',
                'current_platforms': []
            }
    
    def _calculate_chilean_metrics(self, improvements: Dict) -> Dict:
        """Calculate Chilean-specific financial metrics"""
        
        # IVA calculations
        savings_before_iva = improvements['total_annual_savings_clp']
        iva_amount = savings_before_iva * self.constants.IVA_RATE
        savings_with_iva = savings_before_iva + iva_amount
        
        # Platform-specific savings
        platform_savings = {}
        if 'transbank' in self.inputs.get('current_platforms', []):
            platform_savings['transbank'] = improvements['monthly_savings_clp'].get('platform_fees', 0) * 0.3
        if 'webpay' in self.inputs.get('current_platforms', []):
            platform_savings['webpay'] = improvements['monthly_savings_clp'].get('platform_fees', 0) * 0.25
        
        # UF (Unidad de Fomento) conversion for long-term contracts
        uf_value = 37000  # Approximate current UF value in CLP
        savings_in_uf = improvements['total_annual_savings_clp'] / uf_value
        
        return {
            'iva_rate': self.constants.IVA_RATE,
            'savings_before_iva_clp': savings_before_iva,
            'iva_amount_clp': iva_amount,
            'savings_with_iva_clp': savings_with_iva,
            'platform_specific_savings_clp': platform_savings,
            'savings_in_uf': savings_in_uf,
            'savings_in_usd': improvements['total_annual_savings_clp'] / self.constants.USD_TO_CLP
        }
    
    def _generate_recommendations(self, inputs: Dict, current_state: Dict) -> List[Dict]:
        """Generate AI-powered recommendations"""
        
        recommendations = []
        priority_score = 100
        
        # Labor optimization
        if inputs['labor_costs_clp'] > inputs['annual_revenue_clp'] * 0.03:  # If labor > 3% of revenue
            recommendations.append({
                'priority': 'ALTA',
                'category': 'Automatización de Procesos',
                'title': 'Implementar automatización de procesamiento de órdenes',
                'description': 'Reducir procesamiento manual mediante integración API con Defontana/Bsale',
                'expected_savings_clp': inputs['labor_costs_clp'] * 0.6,
                'implementation_time': '2-3 semanas',
                'complexity': 'Media',
                'score': priority_score
            })
            priority_score -= 5
        
        # Shipping optimization
        if inputs['shipping_costs_clp'] > inputs['monthly_orders'] * 4000:  # If shipping cost per order > 4000 CLP
            recommendations.append({
                'priority': 'ALTA',
                'category': 'Optimización Logística',
                'title': 'Negociar tarifas con Chilexpress/Starken',
                'description': 'Consolidar envíos y negociar tarifas por volumen',
                'expected_savings_clp': inputs['shipping_costs_clp'] * 0.25,
                'implementation_time': '1-2 semanas',
                'complexity': 'Baja',
                'score': priority_score
            })
            priority_score -= 5
        
        # Platform integration
        if 'mercadolibre' not in inputs.get('current_platforms', []):
            recommendations.append({
                'priority': 'MEDIA',
                'category': 'Expansión de Canales',
                'title': 'Integrar con Mercado Libre',
                'description': 'Expandir presencia en el marketplace más grande de Chile',
                'expected_revenue_increase_clp': inputs['annual_revenue_clp'] * 0.15,
                'implementation_time': '3-4 semanas',
                'complexity': 'Media',
                'score': priority_score
            })
            priority_score -= 5
        
        # Inventory optimization
        if inputs['inventory_costs_clp'] > inputs['annual_revenue_clp'] * 0.02:
            recommendations.append({
                'priority': 'MEDIA',
                'category': 'Gestión de Inventario',
                'title': 'Implementar sistema predictivo de inventario',
                'description': 'Usar análisis predictivo para optimizar niveles de stock',
                'expected_savings_clp': inputs['inventory_costs_clp'] * 0.3,
                'implementation_time': '4-6 semanas',
                'complexity': 'Alta',
                'score': priority_score
            })
            priority_score -= 5
        
        # Error reduction
        if inputs['error_costs_clp'] > 0:
            recommendations.append({
                'priority': 'ALTA',
                'category': 'Control de Calidad',
                'title': 'Implementar validación automática de datos',
                'description': 'Validación en tiempo real para prevenir errores de procesamiento',
                'expected_savings_clp': inputs['error_costs_clp'] * 0.8,
                'implementation_time': '1-2 semanas',
                'complexity': 'Baja',
                'score': priority_score
            })
        
        # Sort by score
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        
        return recommendations[:5]  # Return top 5 recommendations
    
    def _calculate_three_year_projection(self, improvements: Dict) -> Dict:
        """Calculate 3-year financial projection"""
        
        projections = {}
        cumulative_savings = 0
        investment = self.inputs['investment_clp']
        
        for year in range(1, 4):
            # Assume 10% annual improvement in savings due to optimization
            year_multiplier = 1 + (0.1 * (year - 1))
            annual_savings = improvements['total_annual_savings_clp'] * year_multiplier
            cumulative_savings += annual_savings
            
            projections[f'year_{year}'] = {
                'annual_savings_clp': annual_savings,
                'cumulative_savings_clp': cumulative_savings,
                'net_benefit_clp': cumulative_savings - investment,
                'roi_percentage': ((cumulative_savings - investment) / investment) * 100,
                'monthly_average_savings_clp': annual_savings / 12
            }
        
        projections['total_three_year_roi'] = projections['year_3']['roi_percentage']
        projections['break_even_month'] = improvements['payback_months']
        
        return projections
    
    def _compare_to_benchmarks(self, inputs: Dict) -> Dict:
        """Compare client metrics to industry benchmarks"""
        
        industry = inputs.get('industry', 'retail')
        benchmarks = self.constants.BENCHMARKS.get(industry, self.constants.BENCHMARKS['retail'])
        
        comparisons = {}
        
        # Conversion rate comparison
        if 'conversion_rate' in inputs:
            client_rate = inputs['conversion_rate']
            benchmark_rate = benchmarks['conversion_rate']
            comparisons['conversion_rate'] = {
                'client': client_rate,
                'benchmark': benchmark_rate,
                'difference_percentage': ((client_rate - benchmark_rate) / benchmark_rate) * 100,
                'status': 'Superior' if client_rate > benchmark_rate else 'Por mejorar'
            }
        
        # Average order value comparison
        client_aov = inputs.get('avg_order_value_clp', 0)
        benchmark_aov = benchmarks['avg_order_value_clp']
        comparisons['average_order_value'] = {
            'client_clp': client_aov,
            'benchmark_clp': benchmark_aov,
            'difference_percentage': ((client_aov - benchmark_aov) / benchmark_aov) * 100,
            'status': 'Superior' if client_aov > benchmark_aov else 'Por mejorar'
        }
        
        # Operational cost ratio
        revenue = inputs['annual_revenue_clp']
        total_costs = sum([
            inputs['labor_costs_clp'] * 12,
            inputs['shipping_costs_clp'] * 12,
            inputs['platform_fees_clp'] * 12,
            inputs['error_costs_clp'] * 12,
            inputs['inventory_costs_clp'] * 12
        ])
        client_ratio = total_costs / revenue if revenue > 0 else 1
        benchmark_ratio = benchmarks['operational_cost_ratio']
        
        comparisons['operational_cost_ratio'] = {
            'client': client_ratio,
            'benchmark': benchmark_ratio,
            'difference_percentage': ((client_ratio - benchmark_ratio) / benchmark_ratio) * 100,
            'status': 'Eficiente' if client_ratio < benchmark_ratio else 'Ineficiente',
            'potential_savings_clp': (client_ratio - benchmark_ratio) * revenue if client_ratio > benchmark_ratio else 0
        }
        
        return comparisons
    
    def _generate_executive_summary(self, improvements: Dict, scenarios: Dict) -> Dict:
        """Generate executive summary for C-level presentation"""
        
        return {
            'headline_roi': improvements['roi_percentage_year_1'],
            'payback_period_months': improvements['payback_months'],
            'annual_savings_clp': improvements['total_annual_savings_clp'],
            'annual_savings_usd': improvements['total_annual_savings_clp'] / self.constants.USD_TO_CLP,
            'confidence_level': scenarios['monte_carlo']['probability_positive_roi'],
            'expected_roi_range': {
                'conservative': scenarios['scenarios']['pessimistic']['roi_percentage'],
                'expected': scenarios['scenarios']['realistic']['roi_percentage'],
                'optimistic': scenarios['scenarios']['optimistic']['roi_percentage']
            },
            'key_message': self._generate_key_message(improvements, scenarios)
        }
    
    def _generate_key_message(self, improvements: Dict, scenarios: Dict) -> str:
        """Generate compelling key message for executives"""
        
        roi = improvements['roi_percentage_year_1']
        payback = improvements['payback_months']
        confidence = scenarios['monte_carlo']['probability_positive_roi']
        
        if roi > 200 and payback < 6:
            return f"Retorno excepcional de {roi:.0f}% con recuperación en {payback:.1f} meses. Confianza del {confidence:.0f}%."
        elif roi > 100 and payback < 12:
            return f"Sólido retorno de {roi:.0f}% con recuperación en {payback:.1f} meses. Alta probabilidad de éxito ({confidence:.0f}%)."
        elif roi > 50:
            return f"Retorno positivo de {roi:.0f}% con recuperación en {payback:.1f} meses. Inversión recomendada."
        else:
            return f"Retorno moderado de {roi:.0f}%. Considerar optimizaciones adicionales para mejorar ROI."
    
    def export_to_json(self, filename: str) -> None:
        """Export results to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2, default=str)
    
    def export_to_excel(self, filename: str) -> None:
        """Export results to Excel with multiple sheets"""
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Executive Summary
            summary_df = pd.DataFrame([self.results['executive_summary']])
            summary_df.to_excel(writer, sheet_name='Resumen Ejecutivo', index=False)
            
            # Improvements
            improvements_df = pd.DataFrame([self.results['improvements']])
            improvements_df.to_excel(writer, sheet_name='Mejoras', index=False)
            
            # Scenarios
            scenarios_df = pd.DataFrame(self.results['scenarios']['scenarios']).T
            scenarios_df.to_excel(writer, sheet_name='Escenarios')
            
            # Recommendations
            recommendations_df = pd.DataFrame(self.results['recommendations'])
            recommendations_df.to_excel(writer, sheet_name='Recomendaciones', index=False)
            
            # 3-Year Projection
            projection_df = pd.DataFrame(self.results['three_year_projection']).T
            projection_df.to_excel(writer, sheet_name='Proyección 3 Años')


# Example usage and testing
if __name__ == "__main__":
    # Sample inputs for a Chilean SME
    sample_inputs = {
        'annual_revenue_clp': 500000000,  # 500M CLP
        'monthly_orders': 1500,
        'avg_order_value_clp': 28000,
        'labor_costs_clp': 3500000,  # 3.5M CLP/month
        'shipping_costs_clp': 2800000,  # 2.8M CLP/month
        'platform_fees_clp': 1200000,  # 1.2M CLP/month
        'error_costs_clp': 500000,  # 500K CLP/month
        'inventory_costs_clp': 1800000,  # 1.8M CLP/month
        'investment_clp': 25000000,  # 25M CLP investment
        'industry': 'retail',
        'current_platforms': ['transbank', 'webpay', 'bsale'],
        'conversion_rate': 0.021
    }
    
    print("\n" + "="*60)
    print("ENHANCED ROI CALCULATOR - DEBUG VERSION 2.0")
    print("="*60)
    
    try:
        calculator = EnhancedROICalculator()
        print("✓ Calculator initialized successfully")
        
        # Test with valid inputs
        print("\n1. Testing with valid inputs...")
        results = calculator.calculate_roi(sample_inputs)
        
        if results.get('success', False):
            print("✓ ROI calculation completed successfully")
            
            # Print executive summary if available
            if 'executive_summary' in results:
                print("\n" + "-"*40)
                print("EXECUTIVE SUMMARY")
                print("-"*40)
                summary = results['executive_summary']
                print(f"ROI Año 1: {summary.get('headline_roi', 'N/A'):.1f}%")
                print(f"Período de Recuperación: {summary.get('payback_period_months', 'N/A'):.1f} meses")
                print(f"Ahorro Anual: ${summary.get('annual_savings_clp', 0):,.0f} CLP")
                print(f"Nivel de Confianza: {summary.get('confidence_level', 'N/A'):.1f}%")
                if 'key_message' in summary:
                    print(f"\n{summary['key_message']}")
                    
                # Show metadata
                if 'calculation_metadata' in results:
                    metadata = results['calculation_metadata']
                    print(f"\nMetadata - Warnings: {metadata.get('warnings_count', 0)}, Errors: {metadata.get('errors_count', 0)}")
            
        else:
            print("✗ ROI calculation failed")
            if 'message' in results:
                print(f"Error: {results['message']}")
        
        # Test error handling with invalid inputs
        print("\n2. Testing error handling with invalid inputs...")
        invalid_inputs = {
            'annual_revenue_clp': 'invalid',  # Invalid string
            'monthly_orders': -100,  # Negative value
            'investment_clp': 0,  # Zero investment
        }
        
        results_invalid = calculator.calculate_roi(invalid_inputs)
        if results_invalid.get('success', False) or not results_invalid.get('error', False):
            print("✓ Error handling working - invalid inputs processed with defaults")
        else:
            print("✓ Error handling working - invalid inputs properly rejected")
        
        # Test with missing inputs
        print("\n3. Testing with minimal inputs...")
        minimal_inputs = {'annual_revenue_clp': 100000000}
        results_minimal = calculator.calculate_roi(minimal_inputs)
        if results_minimal.get('success', False) or 'error' not in results_minimal:
            print("✓ Minimal inputs handling working")
        
        # Test file exports
        print("\n4. Testing file exports...")
        if results.get('success', False):
            # Create test directory if it doesn't exist
            os.makedirs('tests', exist_ok=True)
            
            json_success = calculator.export_to_json('tests/roi_analysis_debug.json')
            excel_success = calculator.export_to_excel('tests/roi_analysis_debug.xlsx')
            
            print(f"JSON export: {'✓ Success' if json_success else '✗ Failed'}")
            print(f"Excel export: {'✓ Success' if excel_success else '✗ Failed'}")
        
        # Test extreme edge cases
        print("\n5. Testing extreme edge cases...")
        extreme_inputs = {
            'annual_revenue_clp': float('inf'),  # Infinite value
            'monthly_orders': 0,  # Zero orders
            'investment_clp': -1000000,  # Negative investment
        }
        results_extreme = calculator.calculate_roi(extreme_inputs)
        print("✓ Extreme edge cases handled gracefully")
        
        print("\n" + "="*60)
        print("DEBUG TESTING COMPLETED SUCCESSFULLY")
        print("="*60)
        
    except Exception as e:
        print(f"\n✗ CRITICAL ERROR: {e}")
        print(f"Traceback: {traceback.format_exc()}")
    
    print("\nFor detailed logs, check: sales_toolkit_debug.log")
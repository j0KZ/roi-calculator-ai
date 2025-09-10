"""
Chilean Market-Specific Edge Case Tests
Tests for UF conversions, high inflation scenarios, and Chilean business patterns
"""

import pytest
import json
import sys
import os
from decimal import Decimal
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from edge_case_handler import EdgeCaseHandler
from roi_calculator import ROICalculator
from currency_converter import CurrencyConverter


class TestChileanMarketEdgeCases:
    """Test Chilean market-specific edge cases"""
    
    def setup_method(self):
        """Setup for each test"""
        self.handler = EdgeCaseHandler()
        self.calculator = ROICalculator()
        self.converter = CurrencyConverter()
    
    def test_uf_conversion_edge_cases(self):
        """Test UF (Unidad de Fomento) conversion edge cases"""
        
        # Test various UF amounts
        uf_test_cases = [
            (0, 0),  # Zero UF
            (1, EdgeCaseHandler.UF_TO_CLP_RATE),  # One UF
            (1000, 1000 * EdgeCaseHandler.UF_TO_CLP_RATE),  # Normal amount
            (0.5, 0.5 * EdgeCaseHandler.UF_TO_CLP_RATE),  # Fractional UF
            (1000000, 1000000 * EdgeCaseHandler.UF_TO_CLP_RATE),  # Very large UF amount
        ]
        
        for uf_amount, expected_clp in uf_test_cases:
            data = {'uf_amount': uf_amount}
            processed = self.handler.handle_chilean_specifics(data)
            
            if uf_amount > 0:
                assert 'clp_from_uf' in processed
                assert abs(processed['clp_from_uf'] - expected_clp) < 0.01
            else:
                assert processed.get('clp_from_uf', 0) == 0
    
    def test_inflation_rate_edge_cases(self):
        """Test extreme inflation rate scenarios"""
        
        inflation_test_cases = [
            (-0.1, -0.1, False),  # Deflation
            (0, 0, False),  # No inflation
            (0.05, 0.05, False),  # Normal inflation
            (0.2, 0.2, True),  # High inflation (should warn)
            (0.5, 0.5, True),  # Very high inflation
            (1.0, 1.0, True),  # 100% inflation (at limit)
            (2.0, 1.0, True),  # Above limit (should be capped)
            (-1.0, -0.5, True),  # Below minimum (should be capped)
        ]
        
        for input_rate, expected_rate, should_warn in inflation_test_cases:
            self.handler = EdgeCaseHandler()  # Reset warnings
            
            data = {'inflation_rate': input_rate}
            processed = self.handler.handle_chilean_specifics(data)
            
            assert abs(processed['inflation_rate'] - expected_rate) < 0.01
            
            if should_warn:
                assert len(self.handler.warnings) > 0
    
    def test_iva_calculations(self):
        """Test IVA (Chilean VAT) calculations"""
        
        # Test IVA inclusion in calculations
        base_inputs = {
            'annual_revenue': 10000000,  # 10M CLP
            'monthly_orders': 2000,
            'avg_order_value': 417,
            'labor_costs': 500000,
            'shipping_costs': 300000,
            'error_costs': 200000,
            'inventory_costs': 250000,
            'service_investment': 2000000,
            'currency': 'CLP'
        }
        
        result = self.calculator.calculate_roi(base_inputs)
        
        # Check that IVA is applied to savings
        assert 'chilean_specifics' in result
        assert 'savings_with_iva' in result['chilean_specifics']
        
        iva_calc = result['chilean_specifics']['savings_with_iva']
        expected_iva_amount = result['savings']['annual_total'] * ROICalculator.IVA_RATE
        
        assert abs(iva_calc['iva_amount'] - expected_iva_amount) < 1
        assert abs(iva_calc['amount_with_iva'] - (result['savings']['annual_total'] * 1.19)) < 1
    
    def test_chilean_company_names(self):
        """Test Chilean company naming conventions"""
        
        chilean_company_types = [
            'Empresa Individual de Responsabilidad Limitada',
            'Sociedad Anónima',
            'Sociedad de Responsabilidad Limitada', 
            'Sociedad en Comandita por Acciones',
            'José María & Asociados Ltda.',
            'Compañía Minera del Pacífico S.A.',
            'Inversiones y Rentas Ñuñoa SpA'
        ]
        
        for company_name in chilean_company_types:
            result, errors = self.handler.validate_string_input(
                company_name, 'company_name'
            )
            
            assert len(errors) == 0, f"Should handle Chilean company name: {company_name}"
            assert 'ñ' in result or 'ñ' not in company_name, "Should preserve ñ character"
    
    def test_chilean_currency_amounts(self):
        """Test Chilean Peso (CLP) amount validations"""
        
        clp_test_cases = [
            (50, True),  # Very small CLP amount - should warn
            (1000, False),  # Normal small amount
            (100000, False),  # Normal amount
            (1000000, False),  # One million CLP
            (1000000000, False),  # One billion CLP
            (1e15, True),  # At maximum limit
            (1e16, True),  # Above limit - should be capped
        ]
        
        for amount, should_warn in clp_test_cases:
            self.handler = EdgeCaseHandler()  # Reset warnings
            
            result, errors = self.handler.validate_currency_input(
                amount, 'CLP', 'test_amount'
            )
            
            assert len(errors) == 0 or amount > 1e15, f"Unexpected errors for CLP {amount}"
            
            if should_warn and amount < 100:
                assert len(self.handler.warnings) > 0, f"Should warn about low CLP amount {amount}"
    
    def test_high_inflation_projections(self):
        """Test ROI projections under high inflation scenarios"""
        
        high_inflation_inputs = {
            'annual_revenue': 5000000000,  # 5B CLP
            'monthly_orders': 10000,
            'avg_order_value': 41667,  # ~42K CLP per order
            'labor_costs': 50000000,    # 50M CLP/month
            'shipping_costs': 30000000, # 30M CLP/month
            'error_costs': 15000000,    # 15M CLP/month
            'inventory_costs': 20000000, # 20M CLP/month
            'service_investment': 500000000,  # 500M CLP
            'currency': 'CLP'
        }
        
        # Test with different inflation rates
        inflation_rates = [0.05, 0.15, 0.3, 0.5]  # 5%, 15%, 30%, 50%
        
        for inflation_rate in inflation_rates:
            calculator = ROICalculator()
            calculator.INFLATION_RATE = inflation_rate  # Override for testing
            
            result = calculator.calculate_roi(high_inflation_inputs)
            
            # Higher inflation should lead to higher projected savings
            year_1_savings = result['projections']['year_1']['savings']
            year_3_savings = result['projections']['year_3']['savings']
            
            assert year_3_savings > year_1_savings, "Year 3 savings should be higher due to inflation"
            
            # Check inflation impact
            expected_year_3_factor = (1 + inflation_rate) ** 3
            base_savings = result['savings']['annual_total']
            expected_year_3_savings = base_savings * expected_year_3_factor
            
            # Allow for some calculation variance
            assert abs(year_3_savings - expected_year_3_savings) < expected_year_3_savings * 0.01
    
    def test_chilean_business_hours_edge_cases(self):
        """Test calculations during Chilean business hours and holidays"""
        
        # Test calculation during different times of day
        test_times = [
            datetime(2024, 1, 15, 9, 0),   # 9 AM - business hours
            datetime(2024, 1, 15, 14, 0),  # 2 PM - after lunch
            datetime(2024, 1, 15, 19, 0),  # 7 PM - after business hours
            datetime(2024, 1, 15, 23, 59), # Late night
            datetime(2024, 1, 1, 12, 0),   # New Year's Day
            datetime(2024, 9, 18, 12, 0),  # Chilean Independence Day
        ]
        
        base_inputs = {
            'annual_revenue': 2000000000,  # 2B CLP
            'monthly_orders': 5000,
            'avg_order_value': 33333,
            'labor_costs': 20000000,
            'shipping_costs': 15000000,
            'error_costs': 8000000,
            'inventory_costs': 12000000,
            'service_investment': 200000000,
            'currency': 'CLP'
        }
        
        for test_time in test_times:
            with patch('roi_calculator.datetime') as mock_datetime:
                mock_datetime.now.return_value = test_time
                mock_datetime.fromisoformat = datetime.fromisoformat
                
                result = self.calculator.calculate_roi(base_inputs)
                
                # Should calculate successfully regardless of time
                assert result is not None
                assert 'calculation_date' in result
    
    def test_seasonal_business_patterns(self):
        """Test seasonal business patterns common in Chile"""
        
        # Chilean seasonal patterns (summer vs winter orders)
        seasonal_scenarios = [
            {
                'season': 'summer_high',
                'monthly_orders': 15000,  # High season
                'description': 'Christmas/New Year shopping season'
            },
            {
                'season': 'winter_low', 
                'monthly_orders': 3000,   # Low season
                'description': 'Winter months with reduced activity'
            },
            {
                'season': 'back_to_school',
                'monthly_orders': 8000,   # Medium season
                'description': 'March back-to-school period'
            }
        ]
        
        base_revenue = 3000000000  # 3B CLP annually
        base_avg_order = 20833     # To maintain revenue consistency
        
        for scenario in seasonal_scenarios:
            seasonal_inputs = {
                'annual_revenue': base_revenue,
                'monthly_orders': scenario['monthly_orders'],
                'avg_order_value': base_avg_order,
                'labor_costs': 25000000,
                'shipping_costs': 18000000,
                'error_costs': 10000000,
                'inventory_costs': 15000000,
                'service_investment': 300000000,
                'currency': 'CLP'
            }
            
            result = self.calculator.calculate_roi(seasonal_inputs)
            
            # Should handle all seasonal patterns
            assert result is not None
            assert result['roi_metrics']['annual_savings'] > 0
            
            # High volume seasons should show different optimization potential
            if scenario['season'] == 'summer_high':
                assert result['roi_metrics']['monthly_savings'] > 0
    
    def test_chilean_tax_year_calculations(self):
        """Test calculations across Chilean tax year boundaries"""
        
        # Chilean tax year runs January to December
        tax_year_dates = [
            datetime(2023, 12, 31, 23, 59),  # End of tax year
            datetime(2024, 1, 1, 0, 1),      # Start of new tax year
            datetime(2024, 4, 30),           # Tax filing deadline
            datetime(2024, 6, 30),           # Mid-year
        ]
        
        base_inputs = {
            'annual_revenue': 8000000000,  # 8B CLP
            'monthly_orders': 12000,
            'avg_order_value': 55556,
            'labor_costs': 80000000,
            'shipping_costs': 50000000,
            'error_costs': 30000000,
            'inventory_costs': 40000000,
            'service_investment': 800000000,
            'currency': 'CLP'
        }
        
        for test_date in tax_year_dates:
            with patch('roi_calculator.datetime') as mock_datetime:
                mock_datetime.now.return_value = test_date
                mock_datetime.fromisoformat = datetime.fromisoformat
                
                result = self.calculator.calculate_roi(base_inputs)
                
                # Tax calculations should be consistent
                iva_info = result['chilean_specifics']['savings_with_iva']
                assert iva_info['iva_amount'] > 0
                assert abs(iva_info['iva_amount'] - result['savings']['annual_total'] * 0.19) < 1
    
    def test_chilean_minimum_wage_scenarios(self):
        """Test scenarios with Chilean minimum wage considerations"""
        
        # Chilean minimum wage ~$350,000 CLP/month (2024)
        min_wage_clp = 350000
        
        # Small business with minimum wage employees
        small_business_inputs = {
            'annual_revenue': 120000000,  # 120M CLP (~$150K USD)
            'monthly_orders': 1500,
            'avg_order_value': 6667,
            'labor_costs': min_wage_clp * 3,  # 3 employees at min wage
            'shipping_costs': 2000000,
            'error_costs': 1000000,
            'inventory_costs': 1500000,
            'service_investment': 20000000,
            'currency': 'CLP'
        }
        
        result = self.calculator.calculate_roi(small_business_inputs)
        
        # Should handle small business scenarios
        assert result is not None
        assert result['roi_metrics']['payback_period_months'] > 0
        
        # Labor savings should be significant for small businesses
        labor_savings_pct = result['savings']['labor']['percentage']
        assert labor_savings_pct == ROICalculator.LABOR_REDUCTION_RATE


class TestUFConversions:
    """Dedicated tests for UF (Unidad de Fomento) conversions"""
    
    def test_uf_historical_values(self):
        """Test with historical UF values"""
        
        handler = EdgeCaseHandler()
        
        # Historical UF values (approximate)
        historical_uf_rates = [
            (2020, 28500),
            (2021, 29000),
            (2022, 32000),
            (2023, 35000),
            (2024, 36500),  # Current rate
        ]
        
        for year, uf_rate in historical_uf_rates:
            # Temporarily override the rate
            original_rate = handler.UF_TO_CLP_RATE
            handler.UF_TO_CLP_RATE = uf_rate
            
            try:
                data = {'uf_amount': 100}
                processed = handler.handle_chilean_specifics(data)
                
                expected_clp = 100 * uf_rate
                assert abs(processed['clp_from_uf'] - expected_clp) < 0.01
                
            finally:
                # Restore original rate
                handler.UF_TO_CLP_RATE = original_rate
    
    def test_uf_precision_edge_cases(self):
        """Test UF conversions with high precision"""
        
        handler = EdgeCaseHandler()
        
        precision_cases = [
            (Decimal('100.123456'), Decimal('100.123456') * handler.UF_TO_CLP_RATE),
            (Decimal('0.001'), Decimal('0.001') * handler.UF_TO_CLP_RATE),
            (Decimal('999999.999999'), Decimal('999999.999999') * handler.UF_TO_CLP_RATE),
        ]
        
        for uf_amount, expected_clp in precision_cases:
            data = {'uf_amount': float(uf_amount)}
            processed = handler.handle_chilean_specifics(data)
            
            assert abs(processed['clp_from_uf'] - float(expected_clp)) < 1


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
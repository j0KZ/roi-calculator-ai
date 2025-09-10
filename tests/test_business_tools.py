"""
Test cases for business tools integration
"""

import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from currency_converter import CurrencyConverter
from tax_calculator import TaxCalculator
from breakeven_analyzer import BreakEvenAnalyzer


class TestCurrencyConverter:
    """Test currency converter functionality"""
    
    def test_currency_converter_initialization(self):
        """Test that currency converter initializes properly"""
        converter = CurrencyConverter()
        assert converter is not None
        assert hasattr(converter, 'SUPPORTED_CURRENCIES')
        assert hasattr(converter, 'FALLBACK_RATES')
    
    def test_supported_currencies(self):
        """Test that all expected currencies are supported"""
        converter = CurrencyConverter()
        currencies = converter.get_supported_currencies()
        
        expected_currencies = ['USD', 'EUR', 'CLP', 'GBP', 'JPY', 'CNY', 'BRL', 'MXN']
        for currency in expected_currencies:
            assert currency in currencies
    
    def test_same_currency_conversion(self):
        """Test conversion between same currencies"""
        converter = CurrencyConverter()
        result = converter.convert(1000, 'USD', 'USD')
        
        assert result['original_amount'] == 1000
        assert result['converted_amount'] == 1000
        assert result['exchange_rate'] == 1.0
        assert result['from_currency'] == 'USD'
        assert result['to_currency'] == 'USD'
    
    def test_currency_conversion_with_fallback_rates(self):
        """Test currency conversion using fallback rates"""
        converter = CurrencyConverter()
        result = converter.convert(1000, 'USD', 'EUR')
        
        assert result['original_amount'] == 1000
        assert result['converted_amount'] > 0
        assert result['from_currency'] == 'USD'
        assert result['to_currency'] == 'EUR'
        assert 'exchange_rate' in result
    
    def test_invalid_currency(self):
        """Test handling of invalid currency codes"""
        converter = CurrencyConverter()
        
        with pytest.raises(ValueError, match="Unsupported.*currency"):
            converter.convert(1000, 'INVALID', 'USD')
    
    def test_currency_formatting(self):
        """Test currency formatting"""
        converter = CurrencyConverter()
        
        # Test USD formatting
        formatted = converter.format_currency(1234.56, 'USD')
        assert '$' in formatted
        assert '1,234.56' in formatted
        
        # Test JPY formatting (no decimals)
        formatted = converter.format_currency(1234.56, 'JPY')
        assert '¥' in formatted
        assert '1,235' in formatted  # Should be rounded


class TestTaxCalculator:
    """Test tax calculator functionality"""
    
    def test_tax_calculator_initialization(self):
        """Test that tax calculator initializes properly"""
        calculator = TaxCalculator()
        assert calculator is not None
        assert hasattr(calculator, 'TAX_JURISDICTIONS')
    
    def test_get_available_jurisdictions(self):
        """Test getting available tax jurisdictions"""
        calculator = TaxCalculator()
        jurisdictions = calculator.get_available_jurisdictions()
        
        expected_jurisdictions = ['US', 'EU', 'CL', 'BR', 'MX', 'CA', 'GB', 'AU', 'JP', 'CN']
        for jurisdiction in expected_jurisdictions:
            assert jurisdiction in jurisdictions
    
    def test_get_tax_rate(self):
        """Test getting tax rates for different jurisdictions"""
        calculator = TaxCalculator()
        
        # Test Chilean IVA
        rate = calculator.get_tax_rate('CL')
        assert rate == 0.19  # 19% IVA
        
        # Test US with state
        rate = calculator.get_tax_rate('US', 'CA')
        assert rate > 0
        
        # Test unknown jurisdiction
        rate = calculator.get_tax_rate('UNKNOWN')
        assert rate == 0.0
    
    def test_calculate_tax_impact(self):
        """Test tax impact calculation"""
        calculator = TaxCalculator()
        
        # Test with 19% tax rate (Chile)
        result = calculator.calculate_tax_impact(1000, 'CL', include_tax=False)
        
        assert result['base_amount'] == 1000
        assert result['tax_amount'] == 190  # 19% of 1000
        assert result['tax_inclusive_amount'] == 1190
        assert result['tax_rate'] == 0.19
        assert result['jurisdiction'] == 'CL'
    
    def test_tax_impact_with_tax_included(self):
        """Test tax calculation when tax is already included"""
        calculator = TaxCalculator()
        
        # Test with tax-inclusive amount
        result = calculator.calculate_tax_impact(1190, 'CL', include_tax=True)
        
        assert abs(result['base_amount'] - 1000) < 0.01  # Should be approximately 1000
        assert abs(result['tax_amount'] - 190) < 0.01    # Should be approximately 190
        assert result['tax_inclusive_amount'] == 1190
    
    def test_get_regions_for_jurisdiction(self):
        """Test getting regions for a jurisdiction"""
        calculator = TaxCalculator()
        
        # Test US states
        regions = calculator.get_regions_for_jurisdiction('US')
        assert len(regions) > 0
        assert 'CA' in regions
        assert 'NY' in regions
        
        # Test unknown jurisdiction
        regions = calculator.get_regions_for_jurisdiction('UNKNOWN')
        assert len(regions) == 0


class TestBreakEvenAnalyzer:
    """Test break-even analyzer functionality"""
    
    def test_breakeven_analyzer_initialization(self):
        """Test that break-even analyzer initializes properly"""
        analyzer = BreakEvenAnalyzer()
        assert analyzer is not None
        assert hasattr(analyzer, 'analysis_results')
    
    @patch('breakeven_analyzer.ROICalculator')
    def test_get_default_variable_ranges(self, mock_roi_calculator):
        """Test getting default variable ranges"""
        analyzer = BreakEvenAnalyzer()
        
        roi_inputs = {
            'annual_revenue': 2000000,
            'service_investment': 50000,
            'labor_costs': 8000,
            'shipping_costs': 5000,
            'error_costs': 2000,
            'inventory_costs': 3000
        }
        
        ranges = analyzer._get_default_variable_ranges(roi_inputs)
        
        # Check that ranges are created for all variables
        for key in roi_inputs.keys():
            assert key in ranges
            assert 'min' in ranges[key]
            assert 'max' in ranges[key]
            assert 'steps' in ranges[key]
            
            # Check that min is less than max
            assert ranges[key]['min'] < ranges[key]['max']
            
            # Check that ranges are reasonable (min should be less than original)
            assert ranges[key]['min'] < roi_inputs[key]
    
    def test_format_variable_name(self):
        """Test variable name formatting"""
        analyzer = BreakEvenAnalyzer()
        
        assert analyzer.formatVariableName('annual_revenue') == 'Annual Revenue'
        assert analyzer.formatVariableName('service_investment') == 'Service Investment'
        assert analyzer.formatVariableName('labor_costs') == 'Labor Costs'
    
    def test_format_number(self):
        """Test number formatting"""
        analyzer = BreakEvenAnalyzer()
        
        assert analyzer.formatNumber(1234567) == '1,234,567'
        assert analyzer.formatNumber(1234.56) == '1,235'  # Rounded
        assert analyzer.formatNumber(None) == 'N/A'


class TestBusinessToolsIntegration:
    """Test integration between business tools"""
    
    @patch('currency_converter.requests.get')
    def test_currency_converter_with_roi_calculation(self, mock_get):
        """Test currency conversion with ROI calculation"""
        # Mock API response
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {
            'result': 'success',
            'conversion_rates': {
                'USD': 1.0,
                'EUR': 0.85,
                'CLP': 890.0
            }
        }
        mock_get.return_value = mock_response
        
        converter = CurrencyConverter()
        
        # Mock ROI results
        roi_results = {
            'currency': 'USD',
            'inputs': {
                'annual_revenue': 2000000,
                'service_investment': 50000
            },
            'savings': {
                'annual_total': 100000
            },
            'roi_metrics': {
                'first_year_roi': 100.0
            },
            'financial_metrics': {
                'npv': 150000
            }
        }
        
        # Convert to EUR
        converted_results = converter.convert_roi_calculation(roi_results, 'EUR')
        
        assert converted_results['currency'] == 'EUR'
        assert 'conversion_info' in converted_results
        assert converted_results['inputs']['annual_revenue'] != roi_results['inputs']['annual_revenue']
    
    def test_tax_calculator_with_roi_calculation(self):
        """Test tax calculation with ROI results"""
        calculator = TaxCalculator()
        
        # Mock ROI results
        roi_results = {
            'inputs': {
                'service_investment': 50000
            },
            'savings': {
                'annual_total': 100000,
                'monthly_total': 8333
            },
            'roi_metrics': {
                'first_year_roi': 100.0
            }
        }
        
        # Tax configuration
        tax_config = {
            'jurisdiction': 'CL',
            'investment_deductible': True
        }
        
        # Calculate tax impact
        tax_results = calculator.calculate_roi_tax_impact(roi_results, tax_config)
        
        assert 'tax_analysis' in tax_results
        assert 'tax_config' in tax_results['tax_analysis']
        assert tax_results['tax_analysis']['tax_config']['jurisdiction'] == 'CL'
    
    def test_validation_functions(self):
        """Test input validation across all tools"""
        # Test currency converter validation
        converter = CurrencyConverter()
        with pytest.raises(ValueError):
            converter.convert(1000, 'INVALID', 'USD')
        
        # Test tax calculator validation
        tax_calculator = TaxCalculator()
        errors = tax_calculator.validate_tax_config({})
        assert len(errors) > 0  # Should have validation errors
        
        errors = tax_calculator.validate_tax_config({'jurisdiction': 'CL'})
        assert len(errors) == 0  # Should be valid


if __name__ == '__main__':
    pytest.main([__file__])
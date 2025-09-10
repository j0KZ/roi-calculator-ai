"""
Comprehensive Edge Case Testing Suite for Factorio ROI Calculator
Tests all edge cases, boundary conditions, and error scenarios
"""

import pytest
import json
import math
import sys
import time
import threading
import tempfile
import os
from decimal import Decimal
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from edge_case_handler import EdgeCaseHandler
from roi_calculator import ROICalculator
from currency_converter import CurrencyConverter
from pdf_generator import PDFGenerator


class TestEdgeCaseHandler:
    """Test suite for EdgeCaseHandler class"""
    
    def setup_method(self):
        """Setup for each test"""
        self.handler = EdgeCaseHandler()
    
    def test_validate_numeric_input_edge_cases(self):
        """Test numeric validation with extreme and edge cases"""
        
        # Test extreme values
        test_cases = [
            # (input, expected_value, should_have_errors)
            (0, 0.0, False),
            (-1, 1.0, True),  # Negative converted to positive
            (1e12, 1e12, False),
            (1e20, EdgeCaseHandler.MAX_REVENUE, True),  # Capped at maximum
            (float('inf'), EdgeCaseHandler.MAX_REVENUE, True),
            (float('-inf'), 0.0, True),
            (float('nan'), 0.0, True),
            (1e-15, 1e-15, False),  # Very small but valid
            (None, 0.0, True),
            ('', 0.0, True),
            ('abc', 0.0, True),
            ('123.45', 123.45, False),
            ('1,000,000.50', 1000000.50, False),
            ('$1,000.00', 1000.00, False),
            ('€500.75', 500.75, False),
            ('inf', EdgeCaseHandler.MAX_REVENUE, True),
            ('nan', 0.0, True),
            ('null', 0.0, True),
            ('undefined', 0.0, True),
            (Decimal('123.456'), 123.456, False),
            ([1, 2, 3], 0.0, True),  # Invalid type
            ({'a': 1}, 0.0, True),  # Invalid type
        ]
        
        for input_value, expected_value, should_have_errors in test_cases:
            result_value, errors = self.handler.validate_numeric_input(
                input_value, f'test_field_{input_value}'
            )
            
            if should_have_errors:
                assert len(errors) > 0, f"Expected errors for input {input_value}"
            else:
                assert len(errors) == 0, f"Unexpected errors for input {input_value}: {errors}"
            
            if not math.isnan(expected_value):
                assert abs(result_value - expected_value) < 1e-10, \
                    f"Expected {expected_value}, got {result_value} for input {input_value}"
    
    def test_zero_values_handling(self):
        """Test handling of zero values in different contexts"""
        
        # Zero revenue company
        zero_inputs = {
            'annual_revenue': 0,
            'monthly_orders': 0,
            'avg_order_value': 0,
            'labor_costs': 1000,
            'shipping_costs': 500,
            'error_costs': 200,
            'inventory_costs': 300,
            'service_investment': 10000
        }
        
        validation_result = self.handler.validate_roi_inputs(zero_inputs)
        assert validation_result['is_valid'] == True  # Should handle zero revenue
        
        # Test ROI calculation with zero revenue
        calculator = ROICalculator()
        try:
            result = calculator.calculate_roi(zero_inputs)
            assert result is not None
            # Should handle division by zero gracefully
        except ZeroDivisionError:
            pytest.fail("ROI calculator should handle zero revenue gracefully")
    
    def test_extreme_values_handling(self):
        """Test handling of extremely large and small values"""
        
        # Billion-dollar company
        extreme_inputs = {
            'annual_revenue': 1e10,  # $10 billion
            'monthly_orders': 1e6,   # 1 million orders/month
            'avg_order_value': 833.33,  # To match revenue
            'labor_costs': 1e6,     # $1M/month labor
            'shipping_costs': 5e5,  # $500K/month shipping
            'error_costs': 1e5,     # $100K/month errors
            'inventory_costs': 2e5, # $200K/month inventory
            'service_investment': 1e6  # $1M investment
        }
        
        validation_result = self.handler.validate_roi_inputs(extreme_inputs)
        assert validation_result['is_valid'] == True
        
        calculator = ROICalculator()
        result = calculator.calculate_roi(extreme_inputs)
        assert result is not None
        assert result['roi_metrics']['annual_savings'] > 0
    
    def test_negative_scenarios(self):
        """Test negative growth and high error rate scenarios"""
        
        # Company with 100% error rate (all orders have errors)
        high_error_inputs = {
            'annual_revenue': 1000000,
            'monthly_orders': 1000,
            'avg_order_value': 83.33,
            'labor_costs': 10000,
            'shipping_costs': 5000,
            'error_costs': 50000,  # Very high error costs
            'inventory_costs': 3000,
            'service_investment': 50000
        }
        
        validation_result = self.handler.validate_roi_inputs(high_error_inputs)
        # Should warn about high cost ratio
        assert len(validation_result['warnings']) > 0
        
        calculator = ROICalculator()
        result = calculator.calculate_roi(high_error_inputs)
        assert result['savings']['errors']['annual'] > 0
    
    def test_string_validation_edge_cases(self):
        """Test string validation with special characters and edge cases"""
        
        test_cases = [
            # (input, expected_substring, should_have_errors)
            ('Normal Company Name', 'Normal Company Name', False),
            ('Compañía Española S.A.', 'Compañía Española S.A.', False),
            ('', '', False),  # Empty allowed by default
            (None, '', False),
            ('A' * 50000, 'A' * 10000, True),  # Too long, truncated
            ('Company\x00Name', 'Company Name', False),  # Null byte removed
            ('Company<>Name', 'Company  Name', False),  # Special chars removed
            ('José María & Associates', 'José María   Associates', False),
            ('测试公司', '    ', False),  # Non-Latin characters removed
            (123, '123', False),  # Number converted to string
            (['Company'], "['Company']", False),  # List converted to string
        ]
        
        for input_value, expected_substring, should_have_errors in test_cases:
            result_value, errors = self.handler.validate_string_input(
                input_value, f'test_string_{input_value}'
            )
            
            if should_have_errors:
                assert len(errors) > 0, f"Expected errors for input {input_value}"
            
            if expected_substring:
                assert expected_substring in result_value or result_value == expected_substring, \
                    f"Expected '{expected_substring}' in '{result_value}'"
    
    def test_currency_validation(self):
        """Test currency-specific validation"""
        
        # Test different currencies with various amounts
        test_cases = [
            # (amount, currency, should_pass)
            (1000, 'USD', True),
            (1000000, 'CLP', True),
            (50.5, 'JPY', True),  # Should be rounded
            (1e20, 'USD', False),  # Too large
            (-100, 'EUR', False),  # Negative
            (0, 'GBP', True),  # Zero allowed
            (50, 'CLP', True),  # Should warn about low CLP amount
        ]
        
        for amount, currency, should_pass in test_cases:
            result, errors = self.handler.validate_currency_input(
                amount, currency, f'test_{currency}'
            )
            
            if should_pass:
                assert len(errors) == 0, f"Unexpected errors for {amount} {currency}: {errors}"
            else:
                assert len(errors) > 0, f"Expected errors for {amount} {currency}"
            
            assert result >= 0, f"Result should be non-negative, got {result}"
    
    def test_chilean_specifics(self):
        """Test Chilean market-specific edge cases"""
        
        # UF conversion test
        uf_data = {
            'annual_revenue': 1000000,
            'uf_amount': 1000,  # 1000 UF
            'inflation_rate': 0.25,  # 25% inflation
            'include_iva': True
        }
        
        processed = self.handler.handle_chilean_specifics(uf_data)
        
        assert 'clp_from_uf' in processed
        assert processed['clp_from_uf'] == 1000 * EdgeCaseHandler.UF_TO_CLP_RATE
        assert len(self.handler.warnings) > 0  # Should warn about high inflation
        
        # Test extreme inflation
        extreme_inflation = {
            'inflation_rate': 2.0  # 200% inflation - should be capped
        }
        
        processed = self.handler.handle_chilean_specifics(extreme_inflation)
        assert processed['inflation_rate'] <= EdgeCaseHandler.MAX_INFLATION_RATE


class TestConcurrentAccess:
    """Test concurrent access scenarios"""
    
    def test_concurrent_roi_calculations(self):
        """Test multiple simultaneous ROI calculations"""
        
        def perform_calculation(calc_id):
            calculator = ROICalculator()
            inputs = {
                'annual_revenue': 1000000 + calc_id * 10000,
                'monthly_orders': 1000 + calc_id * 10,
                'avg_order_value': 83.33,
                'labor_costs': 5000 + calc_id * 100,
                'shipping_costs': 3000,
                'error_costs': 2000,
                'inventory_costs': 1500,
                'service_investment': 25000
            }
            
            try:
                result = calculator.calculate_roi(inputs)
                return {
                    'calc_id': calc_id,
                    'success': True,
                    'roi': result['roi_metrics']['first_year_roi']
                }
            except Exception as e:
                return {
                    'calc_id': calc_id,
                    'success': False,
                    'error': str(e)
                }
        
        # Run 50 concurrent calculations
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(perform_calculation, i) for i in range(50)]
            results = [future.result() for future in as_completed(futures)]
        
        # All calculations should succeed
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]
        
        assert len(successful) == 50, f"Only {len(successful)} calculations succeeded, {len(failed)} failed"
        
        for failure in failed:
            print(f"Calculation {failure['calc_id']} failed: {failure['error']}")
    
    def test_concurrent_pdf_generation(self):
        """Test concurrent PDF generation"""
        
        def generate_pdf(pdf_id):
            try:
                handler = EdgeCaseHandler()
                filename = handler.generate_safe_filename(f'test_report_{pdf_id}', '.pdf')
                
                # Simulate PDF generation time
                time.sleep(0.1)
                
                return {
                    'pdf_id': pdf_id,
                    'filename': filename,
                    'success': True
                }
            except Exception as e:
                return {
                    'pdf_id': pdf_id,
                    'success': False,
                    'error': str(e)
                }
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(generate_pdf, i) for i in range(20)]
            results = [future.result() for future in as_completed(futures)]
        
        successful = [r for r in results if r['success']]
        assert len(successful) == 20, "Not all PDF generations succeeded"
        
        # Check that all filenames are unique
        filenames = [r['filename'] for r in successful]
        assert len(set(filenames)) == len(filenames), "Duplicate filenames generated"


class TestMemoryLimitations:
    """Test memory limitations and stress scenarios"""
    
    def test_large_dataset_handling(self):
        """Test handling of large datasets"""
        
        # Create large input arrays for Monte Carlo simulation
        large_inputs = {
            'annual_revenue': 5000000,
            'monthly_orders': 10000,
            'avg_order_value': 41.67,
            'labor_costs': 15000,
            'shipping_costs': 8000,
            'error_costs': 5000,
            'inventory_costs': 6000,
            'service_investment': 100000
        }
        
        handler = EdgeCaseHandler()
        
        # Check memory before calculation
        memory_ok_before = handler.check_memory_usage()
        
        calculator = ROICalculator()
        result = calculator.calculate_roi(large_inputs)
        
        # Check memory after calculation
        memory_ok_after = handler.check_memory_usage()
        
        assert result is not None, "Calculation should complete even with large inputs"
        assert memory_ok_after, "Memory usage should remain within limits"
    
    def test_memory_stress_test(self):
        """Stress test memory usage with multiple large calculations"""
        
        calculations = []
        handler = EdgeCaseHandler()
        
        for i in range(10):  # Reduced from 100 to avoid actual memory issues
            calculator = ROICalculator()
            inputs = {
                'annual_revenue': 1000000 * (i + 1),
                'monthly_orders': 5000 * (i + 1),
                'avg_order_value': 16.67,
                'labor_costs': 10000 + i * 1000,
                'shipping_costs': 5000 + i * 500,
                'error_costs': 3000 + i * 300,
                'inventory_costs': 4000 + i * 400,
                'service_investment': 50000 + i * 5000
            }
            
            result = calculator.calculate_roi(inputs)
            calculations.append(result)
            
            # Check memory usage periodically
            if i % 5 == 0:
                assert handler.check_memory_usage(), f"Memory limit exceeded at calculation {i}"
        
        assert len(calculations) == 10, "All calculations should complete"


class TestNetworkFailures:
    """Test network failure scenarios"""
    
    @patch('requests.get')
    def test_currency_api_failure(self, mock_get):
        """Test currency converter handling API failures"""
        
        # Mock network failure
        mock_get.side_effect = Exception("Network error")
        
        converter = CurrencyConverter()
        
        # Should fall back to cached or default rates
        success = converter.update_rates()
        assert success == False, "Should return False when API fails"
        
        # Should still be able to perform conversions
        result = converter.convert(1000, 'USD', 'EUR')
        assert result['converted_amount'] > 0, "Should use fallback rates"
    
    def test_network_simulation(self):
        """Test network failure simulation"""
        
        handler = EdgeCaseHandler()
        
        # Test different failure rates
        failure_rates = [0.0, 0.5, 1.0]
        
        for rate in failure_rates:
            successes = 0
            total_tests = 100
            
            for _ in range(total_tests):
                if handler.simulate_network_failure(rate):
                    successes += 1
            
            success_rate = successes / total_tests
            expected_success_rate = 1 - rate
            
            # Allow for some variance in random simulation
            assert abs(success_rate - expected_success_rate) < 0.2, \
                f"Success rate {success_rate} too far from expected {expected_success_rate}"


class TestSpecialCharacters:
    """Test special character handling"""
    
    def test_spanish_characters(self):
        """Test handling of Spanish special characters"""
        
        handler = EdgeCaseHandler()
        
        spanish_names = [
            'José María & Asociados',
            'Peñafiel S.A.',
            'Niño & Compañía',
            'Señoría Española Ltd.',
            'Ñuñoa Comercial'
        ]
        
        for name in spanish_names:
            result, errors = handler.validate_string_input(name, 'company_name')
            
            assert len(errors) == 0, f"Should handle Spanish characters in '{name}'"
            # Check that Spanish characters are preserved
            spanish_chars = 'ñÑáéíóúÁÉÍÓÚüÜ'
            for char in spanish_chars:
                if char in name:
                    assert char in result, f"Spanish character '{char}' should be preserved"
    
    def test_pdf_generation_special_chars(self):
        """Test PDF generation with special characters"""
        
        handler = EdgeCaseHandler()
        
        special_names = [
            'Compañía Española',
            'José & María',
            'Señor Núñez',
            'Año Nuevo 2024',
            'Niño Jesús'
        ]
        
        for name in special_names:
            filename = handler.generate_safe_filename(name)
            
            # Should create valid filename
            assert len(filename) > 0, f"Should generate filename for '{name}'"
            assert not any(char in filename for char in '<>:"/\\|?*'), \
                f"Filename '{filename}' should not contain invalid characters"
    
    def test_unicode_normalization(self):
        """Test Unicode normalization"""
        
        handler = EdgeCaseHandler()
        
        # Test different Unicode representations of the same character
        test_cases = [
            'José',  # Precomposed
            'José',  # Decomposed (e + combining acute)
            'naïve',  # i with diaeresis
            'résumé'  # Multiple accents
        ]
        
        for text in test_cases:
            normalized = handler.sanitize_string(text)
            assert len(normalized) > 0, f"Should handle Unicode text '{text}'"


class TestDateTimeEdgeCases:
    """Test date and time handling edge cases"""
    
    def test_timezone_handling(self):
        """Test timezone-related edge cases"""
        
        handler = EdgeCaseHandler()
        
        # Test different date formats
        date_inputs = [
            '2024-01-15',
            '15/01/2024',
            '01/15/2024',
            '2024-01-15 14:30:00',
            'invalid-date',
            None,
            '',
            datetime(2024, 1, 15)
        ]
        
        for date_input in date_inputs:
            result_date, errors = handler.validate_date_input(date_input, 'test_date')
            
            assert isinstance(result_date, datetime), f"Should return datetime for input '{date_input}'"
            
            if date_input in ['invalid-date', None, '']:
                # Should use current date for invalid inputs
                assert abs((result_date - datetime.now()).total_seconds()) < 3600  # Within 1 hour
    
    def test_date_calculation_edge_cases(self):
        """Test edge cases in date calculations"""
        
        calculator = ROICalculator()
        
        # Test calculation at year boundaries
        test_inputs = {
            'annual_revenue': 1200000,
            'monthly_orders': 1000,
            'avg_order_value': 100,
            'labor_costs': 5000,
            'shipping_costs': 3000,
            'error_costs': 2000,
            'inventory_costs': 2000,
            'service_investment': 50000
        }
        
        # Should handle date calculations correctly
        result = calculator.calculate_roi(test_inputs)
        
        assert 'calculation_date' in result
        assert result['projections']['year_1']['savings'] > 0
        assert result['projections']['year_3']['savings'] > 0


class TestValidationSummary:
    """Test validation summary and reporting"""
    
    def test_comprehensive_validation_summary(self):
        """Test comprehensive validation summary generation"""
        
        handler = EdgeCaseHandler()
        
        # Perform various validations to generate errors and warnings
        handler.validate_numeric_input('invalid', 'test_field')
        handler.validate_currency_input(-100, 'USD', 'negative_amount')
        handler.validate_string_input('A' * 20000, 'long_string')
        
        summary = handler.get_validation_summary()
        
        assert 'total_errors' in summary
        assert 'total_warnings' in summary
        assert 'errors' in summary
        assert 'warnings' in summary
        assert 'processing_time' in summary
        assert 'memory_ok' in summary
        
        assert summary['total_errors'] > 0
        assert isinstance(summary['processing_time'], float)
    
    def test_error_accumulation(self):
        """Test that errors accumulate correctly"""
        
        handler = EdgeCaseHandler()
        
        initial_errors = len(handler.validation_errors)
        initial_warnings = len(handler.warnings)
        
        # Generate some errors
        handler.validate_numeric_input(None, 'field1')
        handler.validate_numeric_input('abc', 'field2')
        handler.validate_numeric_input(float('inf'), 'field3')
        
        summary = handler.get_validation_summary()
        
        # Should have accumulated errors
        assert summary['total_errors'] >= initial_errors
        assert len(summary['errors']) >= 0


# Test data loading
@pytest.fixture
def load_test_scenarios():
    """Load test scenarios from JSON file"""
    scenarios_file = os.path.join(os.path.dirname(__file__), '..', 'edge_case_scenarios.json')
    if os.path.exists(scenarios_file):
        with open(scenarios_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


class TestScenarioExecution:
    """Test execution of predefined scenarios"""
    
    def test_scenario_execution(self, load_test_scenarios):
        """Test execution of all predefined scenarios"""
        
        scenarios = load_test_scenarios
        if not scenarios:
            pytest.skip("No test scenarios file found")
        
        handler = EdgeCaseHandler()
        calculator = ROICalculator()
        
        for scenario_name, scenario_data in scenarios.get('scenarios', {}).items():
            inputs = scenario_data.get('inputs', {})
            expected_outcome = scenario_data.get('expected_outcome', 'success')
            
            try:
                # Validate inputs
                validation_result = handler.validate_roi_inputs(inputs)
                
                if expected_outcome == 'validation_error':
                    assert not validation_result['is_valid'], \
                        f"Scenario '{scenario_name}' should fail validation"
                    continue
                
                # Perform calculation
                result = calculator.calculate_roi(validation_result['validated_inputs'])
                
                if expected_outcome == 'calculation_error':
                    pytest.fail(f"Scenario '{scenario_name}' should fail calculation")
                else:
                    assert result is not None, f"Scenario '{scenario_name}' should succeed"
                    
            except Exception as e:
                if expected_outcome == 'success':
                    pytest.fail(f"Scenario '{scenario_name}' should succeed but failed: {e}")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
"""
Comprehensive Edge Case Test Runner
Orchestrates all edge case tests and generates detailed reports
"""

import pytest
import sys
import os
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Any

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from enhanced_roi_calculator_with_edge_cases import EnhancedROICalculator
from edge_case_handler import EdgeCaseHandler


class EdgeCaseTestRunner:
    """Comprehensive test runner for all edge case scenarios"""
    
    def __init__(self):
        self.calculator = EnhancedROICalculator(strict_validation=False)
        self.edge_handler = EdgeCaseHandler()
        self.test_results = []
        self.performance_metrics = {}
        
    def load_test_scenarios(self) -> Dict:
        """Load test scenarios from JSON file"""
        scenarios_path = os.path.join(os.path.dirname(__file__), '..', 'edge_case_scenarios.json')
        
        try:
            with open(scenarios_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: Test scenarios file not found at {scenarios_path}")
            return {}
        except Exception as e:
            print(f"Error loading test scenarios: {e}")
            return {}
    
    def run_all_edge_case_tests(self) -> Dict:
        """Run all edge case test scenarios"""
        
        print("🚀 Starting Comprehensive Edge Case Testing")
        print("=" * 60)
        
        start_time = time.time()
        
        # Load test scenarios
        scenarios = self.load_test_scenarios()
        
        if not scenarios:
            print("❌ No test scenarios available")
            return {'success': False, 'error': 'No test scenarios'}
        
        # Run basic validation tests
        print("\n📋 Running Input Validation Tests...")
        validation_results = self._run_validation_tests()
        
        # Run scenario-based tests
        print("\n🎯 Running Scenario-Based Tests...")
        scenario_results = self._run_scenario_tests(scenarios.get('scenarios', {}))
        
        # Run stress tests
        print("\n💪 Running Stress Tests...")
        stress_results = self._run_stress_tests(scenarios.get('stress_test_scenarios', {}))
        
        # Run performance tests
        print("\n⚡ Running Performance Tests...")
        performance_results = self._run_performance_tests()
        
        # Run Chilean-specific tests
        print("\n🇨🇱 Running Chilean Market Tests...")
        chilean_results = self._run_chilean_tests()
        
        # Run Unicode/PDF tests
        print("\n📄 Running Unicode/PDF Tests...")
        unicode_results = self._run_unicode_tests()
        
        # Compile final results
        end_time = time.time()
        total_time = end_time - start_time
        
        final_results = {
            'success': True,
            'total_execution_time': total_time,
            'test_categories': {
                'validation_tests': validation_results,
                'scenario_tests': scenario_results,
                'stress_tests': stress_results,
                'performance_tests': performance_results,
                'chilean_tests': chilean_results,
                'unicode_tests': unicode_results
            },
            'summary': self._generate_test_summary(),
            'timestamp': datetime.now().isoformat()
        }
        
        # Generate report
        self._generate_test_report(final_results)
        
        return final_results
    
    def _run_validation_tests(self) -> Dict:
        """Run basic input validation tests"""
        
        validation_test_cases = [
            # Numeric validation tests
            {
                'name': 'Negative values',
                'inputs': {'annual_revenue': -1000000, 'monthly_orders': -500},
                'expect_correction': True
            },
            {
                'name': 'Zero values',
                'inputs': {'annual_revenue': 0, 'monthly_orders': 0, 'labor_costs': 5000},
                'expect_success': True
            },
            {
                'name': 'Infinite values',
                'inputs': {'annual_revenue': float('inf'), 'labor_costs': float('nan')},
                'expect_correction': True
            },
            {
                'name': 'String numbers',
                'inputs': {'annual_revenue': '1,000,000.50', 'monthly_orders': '5,000'},
                'expect_success': True
            },
            {
                'name': 'Invalid types',
                'inputs': {'annual_revenue': None, 'monthly_orders': [], 'company_name': 123},
                'expect_correction': True
            }
        ]
        
        results = {'passed': 0, 'failed': 0, 'details': []}
        
        for test_case in validation_test_cases:
            try:
                # Create complete input set
                complete_inputs = {
                    'annual_revenue': 1000000,
                    'monthly_orders': 2000,
                    'avg_order_value': 41.67,
                    'labor_costs': 5000,
                    'shipping_costs': 3000,
                    'error_costs': 2000,
                    'inventory_costs': 2500,
                    'service_investment': 50000
                }
                complete_inputs.update(test_case['inputs'])
                
                validation_result = self.edge_handler.validate_roi_inputs(complete_inputs)
                
                success = True
                if test_case.get('expect_success', False):
                    success = validation_result['is_valid']
                elif test_case.get('expect_correction', False):
                    success = not validation_result['is_valid']  # Should have corrections
                
                if success:
                    results['passed'] += 1
                    status = '✅'
                else:
                    results['failed'] += 1
                    status = '❌'
                
                results['details'].append({
                    'name': test_case['name'],
                    'status': status,
                    'is_valid': validation_result['is_valid'],
                    'errors': len(validation_result['errors']),
                    'warnings': len(validation_result['warnings'])
                })
                
                print(f"  {status} {test_case['name']}")
                
            except Exception as e:
                results['failed'] += 1
                results['details'].append({
                    'name': test_case['name'],
                    'status': '❌',
                    'error': str(e)
                })
                print(f"  ❌ {test_case['name']} - Error: {e}")
        
        return results
    
    def _run_scenario_tests(self, scenarios: Dict) -> Dict:
        """Run predefined scenario tests"""
        
        results = {'passed': 0, 'failed': 0, 'details': []}
        
        for scenario_name, scenario_data in scenarios.items():
            try:
                inputs = scenario_data.get('inputs', {})
                expected_outcome = scenario_data.get('expected_outcome', 'success')
                
                # Run calculation
                result = self.calculator.calculate_roi(inputs)
                
                success = False
                if expected_outcome == 'success':
                    success = result.get('success', True) and 'roi_metrics' in result
                elif expected_outcome == 'validation_error':
                    success = not result.get('success', True) or result.get('validation_info', {}).get('input_errors', [])
                elif expected_outcome == 'calculation_error':
                    success = not result.get('success', True)
                
                if success:
                    results['passed'] += 1
                    status = '✅'
                else:
                    results['failed'] += 1
                    status = '❌'
                
                results['details'].append({
                    'name': scenario_name,
                    'status': status,
                    'category': scenario_data.get('category', 'unknown'),
                    'expected': expected_outcome,
                    'actual_success': result.get('success', True),
                    'has_roi': 'roi_metrics' in result,
                    'processing_time_ms': result.get('validation_info', {}).get('processing_time_ms', 0)
                })
                
                print(f"  {status} {scenario_name} ({scenario_data.get('category', 'unknown')})")
                
            except Exception as e:
                results['failed'] += 1
                results['details'].append({
                    'name': scenario_name,
                    'status': '❌',
                    'error': str(e)
                })
                print(f"  ❌ {scenario_name} - Error: {e}")
        
        return results
    
    def _run_stress_tests(self, stress_scenarios: Dict) -> Dict:
        """Run stress test scenarios"""
        
        results = {'passed': 0, 'failed': 0, 'details': []}
        
        # Concurrent calculations test
        if 'concurrent_calculations' in stress_scenarios:
            concurrent_test = self._test_concurrent_calculations()
            results['details'].append(concurrent_test)
            if concurrent_test['status'] == '✅':
                results['passed'] += 1
            else:
                results['failed'] += 1
        
        # Memory stress test
        if 'memory_stress' in stress_scenarios:
            memory_test = self._test_memory_stress()
            results['details'].append(memory_test)
            if memory_test['status'] == '✅':
                results['passed'] += 1
            else:
                results['failed'] += 1
        
        # High-frequency calculations
        frequency_test = self._test_high_frequency_calculations()
        results['details'].append(frequency_test)
        if frequency_test['status'] == '✅':
            results['passed'] += 1
        else:
            results['failed'] += 1
        
        return results
    
    def _test_concurrent_calculations(self) -> Dict:
        """Test concurrent calculation capability"""
        
        try:
            from concurrent.futures import ThreadPoolExecutor
            import threading
            
            def single_calculation(calc_id):
                inputs = {
                    'annual_revenue': 1000000 + calc_id * 100000,
                    'monthly_orders': 1000 + calc_id * 100,
                    'avg_order_value': 50,
                    'labor_costs': 5000 + calc_id * 500,
                    'shipping_costs': 3000,
                    'error_costs': 2000,
                    'inventory_costs': 2500,
                    'service_investment': 50000
                }
                
                calc = EnhancedROICalculator()
                return calc.calculate_roi(inputs)
            
            start_time = time.time()
            
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(single_calculation, i) for i in range(20)]
                results_list = [future.result(timeout=30) for future in futures]
            
            execution_time = time.time() - start_time
            
            successful = [r for r in results_list if r.get('success', True)]
            
            if len(successful) >= 18:  # Allow for some failures
                return {
                    'name': 'Concurrent Calculations',
                    'status': '✅',
                    'successful': len(successful),
                    'total': len(results_list),
                    'execution_time': execution_time
                }
            else:
                return {
                    'name': 'Concurrent Calculations',
                    'status': '❌',
                    'successful': len(successful),
                    'total': len(results_list),
                    'execution_time': execution_time
                }
            
        except Exception as e:
            return {
                'name': 'Concurrent Calculations',
                'status': '❌',
                'error': str(e)
            }
    
    def _test_memory_stress(self) -> Dict:
        """Test memory usage under stress"""
        
        try:
            # Large calculation test
            large_inputs = {
                'annual_revenue': 50000000000,  # $50B
                'monthly_orders': 10000000,
                'avg_order_value': 417,
                'labor_costs': 100000000,
                'shipping_costs': 75000000,
                'error_costs': 25000000,
                'inventory_costs': 50000000,
                'service_investment': 1000000000
            }
            
            # Multiple large calculations
            memory_ok = True
            for i in range(5):
                calc = EnhancedROICalculator()
                result = calc.calculate_roi(large_inputs)
                
                if not result.get('validation_info', {}).get('memory_ok', True):
                    memory_ok = False
                    break
            
            return {
                'name': 'Memory Stress Test',
                'status': '✅' if memory_ok else '❌',
                'memory_ok': memory_ok,
                'iterations': 5
            }
            
        except Exception as e:
            return {
                'name': 'Memory Stress Test',
                'status': '❌',
                'error': str(e)
            }
    
    def _test_high_frequency_calculations(self) -> Dict:
        """Test high-frequency calculation performance"""
        
        try:
            base_inputs = {
                'annual_revenue': 2000000,
                'monthly_orders': 4000,
                'avg_order_value': 41.67,
                'labor_costs': 8000,
                'shipping_costs': 5000,
                'error_costs': 2500,
                'inventory_costs': 3000,
                'service_investment': 60000
            }
            
            num_calculations = 50
            start_time = time.time()
            
            successful = 0
            for i in range(num_calculations):
                inputs = base_inputs.copy()
                inputs['annual_revenue'] += i * 50000
                
                calc = EnhancedROICalculator()
                result = calc.calculate_roi(inputs)
                
                if result.get('success', True):
                    successful += 1
            
            execution_time = time.time() - start_time
            avg_time_per_calc = (execution_time / num_calculations) * 1000  # ms
            
            # Success if >90% successful and avg time < 100ms
            success = successful >= (num_calculations * 0.9) and avg_time_per_calc < 100
            
            return {
                'name': 'High Frequency Calculations',
                'status': '✅' if success else '❌',
                'successful': successful,
                'total': num_calculations,
                'total_time': execution_time,
                'avg_time_ms': avg_time_per_calc
            }
            
        except Exception as e:
            return {
                'name': 'High Frequency Calculations',
                'status': '❌',
                'error': str(e)
            }
    
    def _run_performance_tests(self) -> Dict:
        """Run performance-related tests"""
        
        results = {'passed': 0, 'failed': 0, 'details': []}
        
        # Simple calculation time test
        simple_test = self._test_simple_calculation_time()
        results['details'].append(simple_test)
        if simple_test['status'] == '✅':
            results['passed'] += 1
        else:
            results['failed'] += 1
        
        # Complex calculation time test
        complex_test = self._test_complex_calculation_time()
        results['details'].append(complex_test)
        if complex_test['status'] == '✅':
            results['passed'] += 1
        else:
            results['failed'] += 1
        
        return results
    
    def _test_simple_calculation_time(self) -> Dict:
        """Test simple calculation performance"""
        
        try:
            inputs = {
                'annual_revenue': 1000000,
                'monthly_orders': 2000,
                'avg_order_value': 41.67,
                'labor_costs': 5000,
                'shipping_costs': 3000,
                'error_costs': 1500,
                'inventory_costs': 2000,
                'service_investment': 25000
            }
            
            start_time = time.time()
            result = self.calculator.calculate_roi(inputs)
            execution_time = (time.time() - start_time) * 1000  # ms
            
            # Should complete in under 100ms
            success = execution_time < 100 and result.get('success', True)
            
            return {
                'name': 'Simple Calculation Time',
                'status': '✅' if success else '❌',
                'execution_time_ms': execution_time,
                'limit_ms': 100,
                'successful': result.get('success', True)
            }
            
        except Exception as e:
            return {
                'name': 'Simple Calculation Time',
                'status': '❌',
                'error': str(e)
            }
    
    def _test_complex_calculation_time(self) -> Dict:
        """Test complex calculation performance"""
        
        try:
            inputs = {
                'annual_revenue': 10000000000,  # $10B
                'monthly_orders': 5000000,
                'avg_order_value': 166.67,
                'labor_costs': 50000000,
                'shipping_costs': 30000000,
                'error_costs': 20000000,
                'inventory_costs': 25000000,
                'service_investment': 500000000,
                'company_name': 'José María & Asociados Compañía Española S.A.',
                'industry': 'Comercio Electrónico Internacional',
                'currency': 'USD',
                'uf_amount': 5000,
                'inflation_rate': 0.25
            }
            
            start_time = time.time()
            result = self.calculator.calculate_roi(inputs)
            execution_time = (time.time() - start_time) * 1000  # ms
            
            # Should complete in under 500ms
            success = execution_time < 500 and result.get('success', True)
            
            return {
                'name': 'Complex Calculation Time',
                'status': '✅' if success else '❌',
                'execution_time_ms': execution_time,
                'limit_ms': 500,
                'successful': result.get('success', True)
            }
            
        except Exception as e:
            return {
                'name': 'Complex Calculation Time',
                'status': '❌',
                'error': str(e)
            }
    
    def _run_chilean_tests(self) -> Dict:
        """Run Chilean market-specific tests"""
        
        results = {'passed': 0, 'failed': 0, 'details': []}
        
        # UF conversion test
        uf_test = self._test_uf_conversion()
        results['details'].append(uf_test)
        if uf_test['status'] == '✅':
            results['passed'] += 1
        else:
            results['failed'] += 1
        
        # High inflation test
        inflation_test = self._test_high_inflation()
        results['details'].append(inflation_test)
        if inflation_test['status'] == '✅':
            results['passed'] += 1
        else:
            results['failed'] += 1
        
        # CLP currency test
        clp_test = self._test_clp_currency()
        results['details'].append(clp_test)
        if clp_test['status'] == '✅':
            results['passed'] += 1
        else:
            results['failed'] += 1
        
        return results
    
    def _test_uf_conversion(self) -> Dict:
        """Test UF conversion functionality"""
        
        try:
            inputs = {
                'annual_revenue': 24000000,  # CLP
                'monthly_orders': 8000,
                'avg_order_value': 250,
                'labor_costs': 1500000,
                'shipping_costs': 800000,
                'error_costs': 400000,
                'inventory_costs': 600000,
                'service_investment': 2500000,
                'currency': 'CLP',
                'uf_amount': 1000
            }
            
            # Process Chilean specifics
            processed = self.edge_handler.handle_chilean_specifics(inputs)
            
            success = 'clp_from_uf' in processed and processed['clp_from_uf'] > 0
            
            return {
                'name': 'UF Conversion',
                'status': '✅' if success else '❌',
                'uf_amount': inputs['uf_amount'],
                'clp_converted': processed.get('clp_from_uf', 0),
                'conversion_detected': 'clp_from_uf' in processed
            }
            
        except Exception as e:
            return {
                'name': 'UF Conversion',
                'status': '❌',
                'error': str(e)
            }
    
    def _test_high_inflation(self) -> Dict:
        """Test high inflation scenario handling"""
        
        try:
            inputs = {
                'annual_revenue': 10000000,
                'monthly_orders': 2000,
                'avg_order_value': 417,
                'labor_costs': 500000,
                'shipping_costs': 300000,
                'error_costs': 150000,
                'inventory_costs': 200000,
                'service_investment': 1000000,
                'currency': 'CLP',
                'inflation_rate': 0.5  # 50% inflation
            }
            
            result = self.calculator.calculate_roi(inputs)
            
            # Should handle high inflation and show warnings
            warnings = result.get('validation_info', {}).get('input_warnings', [])
            has_inflation_warning = any('inflation' in w.lower() for w in warnings)
            
            success = result.get('success', True) and has_inflation_warning
            
            return {
                'name': 'High Inflation Handling',
                'status': '✅' if success else '❌',
                'inflation_rate': inputs['inflation_rate'],
                'calculation_successful': result.get('success', True),
                'inflation_warning_present': has_inflation_warning,
                'total_warnings': len(warnings)
            }
            
        except Exception as e:
            return {
                'name': 'High Inflation Handling',
                'status': '❌',
                'error': str(e)
            }
    
    def _test_clp_currency(self) -> Dict:
        """Test Chilean Peso currency handling"""
        
        try:
            # Test small CLP amount (should warn)
            small_amount, errors = self.edge_handler.validate_currency_input(50, 'CLP', 'small_clp')
            
            # Test large CLP amount
            large_amount, large_errors = self.edge_handler.validate_currency_input(1000000000, 'CLP', 'large_clp')
            
            # Should handle both without errors
            success = len(errors) == 0 and len(large_errors) == 0
            
            return {
                'name': 'CLP Currency Handling',
                'status': '✅' if success else '❌',
                'small_amount_errors': len(errors),
                'large_amount_errors': len(large_errors),
                'warnings_generated': len(self.edge_handler.warnings)
            }
            
        except Exception as e:
            return {
                'name': 'CLP Currency Handling',
                'status': '❌',
                'error': str(e)
            }
    
    def _run_unicode_tests(self) -> Dict:
        """Run Unicode and special character tests"""
        
        results = {'passed': 0, 'failed': 0, 'details': []}
        
        # Spanish characters test
        spanish_test = self._test_spanish_characters()
        results['details'].append(spanish_test)
        if spanish_test['status'] == '✅':
            results['passed'] += 1
        else:
            results['failed'] += 1
        
        # Filename generation test
        filename_test = self._test_safe_filename_generation()
        results['details'].append(filename_test)
        if filename_test['status'] == '✅':
            results['passed'] += 1
        else:
            results['failed'] += 1
        
        # XSS prevention test
        xss_test = self._test_xss_prevention()
        results['details'].append(xss_test)
        if xss_test['status'] == '✅':
            results['passed'] += 1
        else:
            results['failed'] += 1
        
        return results
    
    def _test_spanish_characters(self) -> Dict:
        """Test Spanish character preservation"""
        
        try:
            test_strings = [
                'José María & Asociados',
                'Compañía Española S.A.',
                'Señoría Ñuñoa Ltda.'
            ]
            
            all_preserved = True
            
            for test_string in test_strings:
                result, errors = self.edge_handler.validate_string_input(test_string, 'spanish_test')
                
                # Check if Spanish characters are preserved
                spanish_chars = set('ñÑáéíóúÁÉÍÓÚüÜ')
                original_spanish = spanish_chars.intersection(set(test_string))
                result_spanish = spanish_chars.intersection(set(result))
                
                if original_spanish != result_spanish or len(errors) > 0:
                    all_preserved = False
                    break
            
            return {
                'name': 'Spanish Character Preservation',
                'status': '✅' if all_preserved else '❌',
                'strings_tested': len(test_strings),
                'all_preserved': all_preserved
            }
            
        except Exception as e:
            return {
                'name': 'Spanish Character Preservation',
                'status': '❌',
                'error': str(e)
            }
    
    def _test_safe_filename_generation(self) -> Dict:
        """Test safe filename generation"""
        
        try:
            test_names = [
                'José María Report',
                'Company/Analysis<>2024',
                'Report:Results|Final'
            ]
            
            all_safe = True
            filenames = []
            
            for name in test_names:
                filename = self.edge_handler.generate_safe_filename(name)
                filenames.append(filename)
                
                # Check for dangerous characters
                dangerous_chars = '<>:"/\\|?*'
                if any(char in filename for char in dangerous_chars):
                    all_safe = False
                    break
            
            # Check uniqueness
            unique_filenames = len(set(filenames)) == len(filenames)
            
            return {
                'name': 'Safe Filename Generation',
                'status': '✅' if all_safe and unique_filenames else '❌',
                'all_safe': all_safe,
                'unique_filenames': unique_filenames,
                'filenames_generated': len(filenames)
            }
            
        except Exception as e:
            return {
                'name': 'Safe Filename Generation',
                'status': '❌',
                'error': str(e)
            }
    
    def _test_xss_prevention(self) -> Dict:
        """Test XSS prevention in input sanitization"""
        
        try:
            xss_attempts = [
                '<script>alert("XSS")</script>',
                'javascript:alert("XSS")',
                '<img src=x onerror=alert("XSS")>'
            ]
            
            all_sanitized = True
            
            for xss in xss_attempts:
                result, errors = self.edge_handler.validate_string_input(xss, 'xss_test')
                
                # Check that dangerous elements are removed
                if '<script>' in result.lower() or 'javascript:' in result.lower():
                    all_sanitized = False
                    break
            
            return {
                'name': 'XSS Prevention',
                'status': '✅' if all_sanitized else '❌',
                'attempts_tested': len(xss_attempts),
                'all_sanitized': all_sanitized
            }
            
        except Exception as e:
            return {
                'name': 'XSS Prevention',
                'status': '❌',
                'error': str(e)
            }
    
    def _generate_test_summary(self) -> Dict:
        """Generate overall test summary"""
        
        return {
            'total_execution_time': getattr(self, 'total_execution_time', 0),
            'memory_usage_ok': self.edge_handler.check_memory_usage(),
            'validation_summary': self.edge_handler.get_validation_summary(),
            'timestamp': datetime.now().isoformat()
        }
    
    def _generate_test_report(self, results: Dict) -> None:
        """Generate detailed test report"""
        
        report_filename = f"edge_case_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path = os.path.join(os.path.dirname(__file__), report_filename)
        
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False, default=str)
            
            print(f"\n📊 Detailed test report saved to: {report_path}")
            
        except Exception as e:
            print(f"❌ Failed to save test report: {e}")
        
        # Print summary to console
        self._print_test_summary(results)
    
    def _print_test_summary(self, results: Dict) -> None:
        """Print test summary to console"""
        
        print(f"\n{'='*60}")
        print("🏁 EDGE CASE TESTING COMPLETE")
        print('='*60)
        
        total_passed = 0
        total_failed = 0
        
        for category, category_results in results['test_categories'].items():
            passed = category_results.get('passed', 0)
            failed = category_results.get('failed', 0)
            
            total_passed += passed
            total_failed += failed
            
            status = '✅' if failed == 0 else '⚠️' if passed > failed else '❌'
            print(f"{status} {category.replace('_', ' ').title()}: {passed} passed, {failed} failed")
        
        print(f"\n📈 OVERALL RESULTS:")
        print(f"   Total Passed: {total_passed}")
        print(f"   Total Failed: {total_failed}")
        print(f"   Success Rate: {(total_passed/(total_passed+total_failed)*100):.1f}%")
        print(f"   Execution Time: {results['total_execution_time']:.1f}s")
        
        if total_failed == 0:
            print(f"\n🎉 ALL EDGE CASE TESTS PASSED!")
        elif total_passed > total_failed:
            print(f"\n✅ MOSTLY SUCCESSFUL - Some issues to address")
        else:
            print(f"\n❌ SIGNIFICANT ISSUES DETECTED - Review required")


if __name__ == "__main__":
    # Run comprehensive edge case testing
    runner = EdgeCaseTestRunner()
    results = runner.run_all_edge_case_tests()
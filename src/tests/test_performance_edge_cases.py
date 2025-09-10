"""
Performance and Memory Edge Case Tests
Tests for memory limitations, concurrent access, and performance under stress
"""

import pytest
import time
import threading
import multiprocessing
import sys
import os
import gc
import psutil
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from unittest.mock import patch, Mock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from edge_case_handler import EdgeCaseHandler
from roi_calculator import ROICalculator
from currency_converter import CurrencyConverter


class TestMemoryEdgeCases:
    """Test memory usage and limitations"""
    
    def setup_method(self):
        """Setup for each test"""
        self.handler = EdgeCaseHandler()
        gc.collect()  # Clean up before test
    
    def test_memory_usage_monitoring(self):
        """Test memory usage monitoring functionality"""
        
        initial_memory_ok = self.handler.check_memory_usage()
        assert initial_memory_ok is True or initial_memory_ok is False  # Should return boolean
        
        # Test with mock psutil to simulate high memory
        with patch('edge_case_handler.psutil') as mock_psutil:
            mock_process = Mock()
            mock_memory_info = Mock()
            mock_memory_info.rss = 2 * 1024 * 1024 * 1024  # 2GB in bytes
            mock_process.memory_info.return_value = mock_memory_info
            mock_psutil.Process.return_value = mock_process
            
            memory_ok = self.handler.check_memory_usage()
            assert memory_ok == False, "Should detect high memory usage"
    
    def test_large_calculation_memory_usage(self):
        """Test memory usage with large calculations"""
        
        # Large input scenario
        large_inputs = {
            'annual_revenue': 50000000000,  # $50B
            'monthly_orders': 10000000,     # 10M orders/month
            'avg_order_value': 417,
            'labor_costs': 100000000,       # $100M/month labor
            'shipping_costs': 75000000,     # $75M/month shipping
            'error_costs': 25000000,        # $25M/month errors
            'inventory_costs': 50000000,    # $50M/month inventory
            'service_investment': 1000000000 # $1B investment
        }
        
        memory_before = self._get_memory_usage()
        
        calculator = ROICalculator()
        result = calculator.calculate_roi(large_inputs)
        
        memory_after = self._get_memory_usage()
        
        # Check that calculation completed
        assert result is not None
        assert result['roi_metrics']['annual_savings'] > 0
        
        # Memory increase should be reasonable (less than 100MB for one calculation)
        memory_increase_mb = (memory_after - memory_before) / 1024 / 1024
        assert memory_increase_mb < 100, f"Memory increased by {memory_increase_mb:.1f}MB"
    
    def test_memory_leak_detection(self):
        """Test for memory leaks in repeated calculations"""
        
        base_inputs = {
            'annual_revenue': 2000000,
            'monthly_orders': 5000,
            'avg_order_value': 33.33,
            'labor_costs': 8000,
            'shipping_costs': 5000,
            'error_costs': 2000,
            'inventory_costs': 3000,
            'service_investment': 50000
        }
        
        memory_readings = []
        
        for i in range(20):  # 20 calculations
            calculator = ROICalculator()
            result = calculator.calculate_roi(base_inputs)
            
            # Force garbage collection
            del calculator
            del result
            gc.collect()
            
            memory_readings.append(self._get_memory_usage())
        
        # Memory usage should not consistently increase
        memory_trend = memory_readings[-5:]  # Last 5 readings
        memory_start = memory_readings[:5]   # First 5 readings
        
        avg_end = sum(memory_trend) / len(memory_trend)
        avg_start = sum(memory_start) / len(memory_start)
        
        # Allow for some memory increase but not excessive
        memory_increase_mb = (avg_end - avg_start) / 1024 / 1024
        assert memory_increase_mb < 50, f"Potential memory leak: {memory_increase_mb:.1f}MB increase"
    
    def _get_memory_usage(self):
        """Get current memory usage in bytes"""
        try:
            process = psutil.Process()
            return process.memory_info().rss
        except (ImportError, Exception):
            return 0  # If psutil not available, return 0


class TestConcurrentAccessEdgeCases:
    """Test concurrent access scenarios"""
    
    def test_thread_safety_roi_calculations(self):
        """Test thread safety of ROI calculations"""
        
        def perform_calculation(thread_id):
            try:
                calculator = ROICalculator()
                inputs = {
                    'annual_revenue': 1000000 + thread_id * 100000,
                    'monthly_orders': 1000 + thread_id * 100,
                    'avg_order_value': 50 + thread_id,
                    'labor_costs': 5000 + thread_id * 500,
                    'shipping_costs': 3000 + thread_id * 300,
                    'error_costs': 2000 + thread_id * 200,
                    'inventory_costs': 2500 + thread_id * 250,
                    'service_investment': 50000 + thread_id * 5000,
                    'company_name': f'Company_{thread_id}'
                }
                
                result = calculator.calculate_roi(inputs)
                
                return {
                    'thread_id': thread_id,
                    'success': True,
                    'roi': result['roi_metrics']['first_year_roi'],
                    'annual_savings': result['roi_metrics']['annual_savings']
                }
                
            except Exception as e:
                return {
                    'thread_id': thread_id,
                    'success': False,
                    'error': str(e)
                }
        
        # Run 30 concurrent calculations
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(perform_calculation, i) for i in range(30)]
            results = [future.result(timeout=30) for future in as_completed(futures)]
        
        # All should succeed
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]
        
        assert len(successful) == 30, f"Only {len(successful)}/30 calculations succeeded"
        
        # Results should be different (due to different inputs)
        roi_values = [r['roi'] for r in successful]
        unique_rois = set(roi_values)
        assert len(unique_rois) > 1, "All calculations returned the same ROI (potential race condition)"
    
    def test_concurrent_validation(self):
        """Test concurrent input validation"""
        
        def validate_inputs(validator_id):
            try:
                handler = EdgeCaseHandler()
                
                test_inputs = {
                    'annual_revenue': validator_id * 100000,
                    'monthly_orders': validator_id * 100,
                    'avg_order_value': 25.0 + validator_id,
                    'labor_costs': validator_id * 1000,
                    'shipping_costs': validator_id * 800,
                    'error_costs': validator_id * 500,
                    'inventory_costs': validator_id * 600,
                    'service_investment': validator_id * 10000,
                    'company_name': f'Validator_{validator_id}_CompañíaEspeciál'
                }
                
                validation_result = handler.validate_roi_inputs(test_inputs)
                
                return {
                    'validator_id': validator_id,
                    'success': True,
                    'is_valid': validation_result['is_valid'],
                    'error_count': len(validation_result['errors']),
                    'warning_count': len(validation_result['warnings'])
                }
                
            except Exception as e:
                return {
                    'validator_id': validator_id,
                    'success': False,
                    'error': str(e)
                }
        
        # Run 25 concurrent validations
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(validate_inputs, i) for i in range(1, 26)]
            results = [future.result(timeout=20) for future in as_completed(futures)]
        
        successful = [r for r in results if r['success']]
        assert len(successful) == 25, "All validations should succeed"
        
        # All should be valid (positive inputs)
        valid_results = [r for r in successful if r['is_valid']]
        assert len(valid_results) == 25, "All inputs should be valid"
    
    def test_deadlock_prevention(self):
        """Test that concurrent operations don't deadlock"""
        
        def mixed_operations(op_id):
            try:
                handler = EdgeCaseHandler()
                calculator = ROICalculator()
                
                # Mix of operations
                operations = [
                    lambda: handler.validate_numeric_input(op_id * 1000, f'field_{op_id}'),
                    lambda: handler.validate_string_input(f'Company_{op_id}', f'string_{op_id}'),
                    lambda: handler.validate_currency_input(op_id * 50000, 'USD', f'currency_{op_id}'),
                    lambda: calculator.calculate_roi({
                        'annual_revenue': op_id * 200000,
                        'monthly_orders': op_id * 200,
                        'avg_order_value': 83.33,
                        'labor_costs': op_id * 2000,
                        'shipping_costs': op_id * 1500,
                        'error_costs': op_id * 800,
                        'inventory_costs': op_id * 1200,
                        'service_investment': op_id * 20000
                    })
                ]
                
                # Execute all operations
                results = []
                for op in operations:
                    results.append(op())
                
                return {'op_id': op_id, 'success': True, 'results': len(results)}
                
            except Exception as e:
                return {'op_id': op_id, 'success': False, 'error': str(e)}
        
        start_time = time.time()
        
        # Run with timeout to detect deadlocks
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = [executor.submit(mixed_operations, i) for i in range(1, 16)]
            
            # Use timeout to prevent hanging
            results = []
            for future in as_completed(futures, timeout=45):
                results.append(future.result())
        
        execution_time = time.time() - start_time
        
        # Should complete in reasonable time (no deadlocks)
        assert execution_time < 40, f"Operations took too long ({execution_time:.1f}s), possible deadlock"
        
        successful = [r for r in results if r['success']]
        assert len(successful) == 15, f"Only {len(successful)}/15 operations succeeded"
    
    def test_resource_contention(self):
        """Test behavior under resource contention"""
        
        shared_counter = {'value': 0}
        lock = threading.Lock()
        
        def contended_calculation(calc_id):
            try:
                # Simulate resource contention
                with lock:
                    shared_counter['value'] += 1
                    current_count = shared_counter['value']
                
                # Perform calculation with unique inputs based on count
                calculator = ROICalculator()
                inputs = {
                    'annual_revenue': current_count * 150000,
                    'monthly_orders': current_count * 150,
                    'avg_order_value': 66.67,
                    'labor_costs': current_count * 3000,
                    'shipping_costs': current_count * 2200,
                    'error_costs': current_count * 1100,
                    'inventory_costs': current_count * 1800,
                    'service_investment': current_count * 30000
                }
                
                result = calculator.calculate_roi(inputs)
                
                return {
                    'calc_id': calc_id,
                    'count': current_count,
                    'success': True,
                    'roi': result['roi_metrics']['first_year_roi']
                }
                
            except Exception as e:
                return {
                    'calc_id': calc_id,
                    'success': False,
                    'error': str(e)
                }
        
        # High contention scenario
        with ThreadPoolExecutor(max_workers=12) as executor:
            futures = [executor.submit(contended_calculation, i) for i in range(40)]
            results = [future.result(timeout=30) for future in as_completed(futures)]
        
        successful = [r for r in results if r['success']]
        assert len(successful) == 40, "All calculations should succeed despite contention"
        
        # Verify counter incremented correctly
        assert shared_counter['value'] == 40


class TestPerformanceEdgeCases:
    """Test performance under various edge conditions"""
    
    def test_calculation_time_limits(self):
        """Test that calculations complete within reasonable time limits"""
        
        test_scenarios = [
            {
                'name': 'simple',
                'inputs': {
                    'annual_revenue': 1000000,
                    'monthly_orders': 2000,
                    'avg_order_value': 41.67,
                    'labor_costs': 5000,
                    'shipping_costs': 3000,
                    'error_costs': 1500,
                    'inventory_costs': 2000,
                    'service_investment': 25000
                },
                'max_time_ms': 100
            },
            {
                'name': 'complex',
                'inputs': {
                    'annual_revenue': 10000000000,  # $10B
                    'monthly_orders': 5000000,
                    'avg_order_value': 166.67,
                    'labor_costs': 50000000,
                    'shipping_costs': 30000000,
                    'error_costs': 20000000,
                    'inventory_costs': 25000000,
                    'service_investment': 500000000
                },
                'max_time_ms': 500
            }
        ]
        
        for scenario in test_scenarios:
            calculator = ROICalculator()
            
            start_time = time.time()
            result = calculator.calculate_roi(scenario['inputs'])
            end_time = time.time()
            
            execution_time_ms = (end_time - start_time) * 1000
            
            assert result is not None, f"{scenario['name']} calculation should succeed"
            assert execution_time_ms < scenario['max_time_ms'], \
                f"{scenario['name']} took {execution_time_ms:.1f}ms, limit is {scenario['max_time_ms']}ms"
    
    def test_high_frequency_calculations(self):
        """Test performance with high frequency calculations"""
        
        base_inputs = {
            'annual_revenue': 3000000,
            'monthly_orders': 6000,
            'avg_order_value': 41.67,
            'labor_costs': 12000,
            'shipping_costs': 8000,
            'error_costs': 4000,
            'inventory_costs': 6000,
            'service_investment': 75000
        }
        
        num_calculations = 100
        start_time = time.time()
        
        results = []
        for i in range(num_calculations):
            # Vary inputs slightly for each calculation
            inputs = base_inputs.copy()
            inputs['annual_revenue'] += i * 10000
            inputs['monthly_orders'] += i * 10
            
            calculator = ROICalculator()
            result = calculator.calculate_roi(inputs)
            results.append(result)
        
        end_time = time.time()
        total_time = end_time - start_time
        avg_time_per_calc = (total_time / num_calculations) * 1000  # ms
        
        assert len(results) == num_calculations, "All calculations should complete"
        assert avg_time_per_calc < 50, f"Average calculation time {avg_time_per_calc:.1f}ms is too slow"
        assert total_time < 5, f"Total time {total_time:.1f}s for {num_calculations} calculations is too slow"
    
    def test_stress_test_scenario(self):
        """Comprehensive stress test scenario"""
        
        def stress_worker(worker_id):
            try:
                results = []
                
                for calc_id in range(5):  # 5 calculations per worker
                    calculator = ROICalculator()
                    handler = EdgeCaseHandler()
                    
                    # Generate varied inputs
                    inputs = {
                        'annual_revenue': (worker_id + calc_id) * 500000,
                        'monthly_orders': (worker_id + calc_id) * 500,
                        'avg_order_value': 83.33 + calc_id,
                        'labor_costs': (worker_id + calc_id) * 2500,
                        'shipping_costs': (worker_id + calc_id) * 1800,
                        'error_costs': (worker_id + calc_id) * 900,
                        'inventory_costs': (worker_id + calc_id) * 1200,
                        'service_investment': (worker_id + calc_id) * 25000,
                        'company_name': f'StressTest_{worker_id}_{calc_id}_Compañía'
                    }
                    
                    # Validate inputs
                    validation = handler.validate_roi_inputs(inputs)
                    if not validation['is_valid']:
                        continue
                    
                    # Calculate ROI
                    result = calculator.calculate_roi(validation['validated_inputs'])
                    results.append({
                        'worker_id': worker_id,
                        'calc_id': calc_id,
                        'roi': result['roi_metrics']['first_year_roi'],
                        'savings': result['roi_metrics']['annual_savings']
                    })
                
                return {
                    'worker_id': worker_id,
                    'success': True,
                    'results': results,
                    'count': len(results)
                }
                
            except Exception as e:
                return {
                    'worker_id': worker_id,
                    'success': False,
                    'error': str(e)
                }
        
        num_workers = 8
        start_time = time.time()
        
        # Run stress test
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = [executor.submit(stress_worker, i) for i in range(num_workers)]
            worker_results = [future.result(timeout=60) for future in as_completed(futures)]
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Analyze results
        successful_workers = [r for r in worker_results if r['success']]
        total_calculations = sum(r['count'] for r in successful_workers)
        
        assert len(successful_workers) == num_workers, "All workers should complete successfully"
        assert total_calculations >= num_workers * 4, "Should complete most calculations"  # Allow for some validation failures
        assert total_time < 30, f"Stress test took {total_time:.1f}s, should complete faster"
        
        print(f"Stress test completed: {total_calculations} calculations by {num_workers} workers in {total_time:.1f}s")


if __name__ == "__main__":
    # Run performance tests
    pytest.main([__file__, "-v", "-s"])
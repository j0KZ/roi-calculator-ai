"""
Unit tests for ROI Calculator
"""

import unittest
import json
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from roi_calculator import ROICalculator


class TestROICalculator(unittest.TestCase):
    """Test cases for ROI Calculator"""
    
    def setUp(self):
        """Set up test data"""
        self.calculator = ROICalculator()
        self.sample_inputs = {
            'annual_revenue': 2000000,  # $2M
            'monthly_orders': 5000,
            'avg_order_value': 33.33,
            'labor_costs': 8000,
            'shipping_costs': 5000,
            'error_costs': 2000,
            'inventory_costs': 3000,
            'service_investment': 50000
        }
    
    def test_valid_calculation(self):
        """Test valid ROI calculation"""
        results = self.calculator.calculate_roi(self.sample_inputs)
        
        # Check that results are returned
        self.assertIsInstance(results, dict)
        
        # Check required sections
        required_sections = [
            'inputs', 'current_costs', 'optimized_costs', 'savings',
            'roi_metrics', 'projections', 'financial_metrics', 'chilean_specifics'
        ]
        for section in required_sections:
            self.assertIn(section, results)
    
    def test_savings_calculations(self):
        """Test savings calculations"""
        results = self.calculator.calculate_roi(self.sample_inputs)
        savings = results['savings']
        
        # Test labor savings (60% reduction)
        expected_labor_savings = self.sample_inputs['labor_costs'] * 0.60 * 12
        self.assertAlmostEqual(savings['labor']['annual'], expected_labor_savings, places=2)
        
        # Test shipping savings (25% reduction)
        expected_shipping_savings = self.sample_inputs['shipping_costs'] * 0.25 * 12
        self.assertAlmostEqual(savings['shipping']['annual'], expected_shipping_savings, places=2)
        
        # Test error savings (80% reduction)
        expected_error_savings = self.sample_inputs['error_costs'] * 0.80 * 12
        self.assertAlmostEqual(savings['errors']['annual'], expected_error_savings, places=2)
        
        # Test inventory savings (30% reduction)
        expected_inventory_savings = self.sample_inputs['inventory_costs'] * 0.30 * 12
        self.assertAlmostEqual(savings['inventory']['annual'], expected_inventory_savings, places=2)
    
    def test_roi_metrics(self):
        """Test ROI metrics calculation"""
        results = self.calculator.calculate_roi(self.sample_inputs)
        roi = results['roi_metrics']
        
        # Check payback period is positive
        self.assertGreater(roi['payback_period_months'], 0)
        
        # Check annual savings is positive
        self.assertGreater(roi['annual_savings'], 0)
        
        # Check first year ROI
        expected_roi = ((roi['annual_savings'] - self.sample_inputs['service_investment']) 
                       / self.sample_inputs['service_investment']) * 100
        self.assertAlmostEqual(roi['first_year_roi'], expected_roi, places=1)
    
    def test_financial_metrics(self):
        """Test financial metrics (NPV, IRR)"""
        results = self.calculator.calculate_roi(self.sample_inputs)
        financial = results['financial_metrics']
        
        # Check NPV exists and is reasonable
        self.assertIsInstance(financial['npv'], (int, float))
        
        # Check IRR exists and is reasonable (should be positive for good investment)
        self.assertIsInstance(financial['irr'], (int, float))
        self.assertGreater(financial['irr'], 0)
        
        # Check cash flows length (initial + 3 years)
        self.assertEqual(len(financial['cash_flows']), 4)
        
        # First cash flow should be negative (investment)
        self.assertLess(financial['cash_flows'][0], 0)
    
    def test_projections(self):
        """Test 3-year projections"""
        results = self.calculator.calculate_roi(self.sample_inputs)
        projections = results['projections']
        
        # Check all three years exist
        for year in range(1, 4):
            year_key = f'year_{year}'
            self.assertIn(year_key, projections)
            
            year_data = projections[year_key]
            
            # Check required fields
            required_fields = [
                'savings', 'net_benefit', 'cumulative_savings', 
                'cumulative_net_benefit', 'roi_percentage'
            ]
            for field in required_fields:
                self.assertIn(field, year_data)
        
        # Check cumulative values increase
        self.assertGreater(
            projections['year_2']['cumulative_savings'],
            projections['year_1']['cumulative_savings']
        )
        self.assertGreater(
            projections['year_3']['cumulative_savings'],
            projections['year_2']['cumulative_savings']
        )
    
    def test_chilean_specifics(self):
        """Test Chilean market calculations"""
        results = self.calculator.calculate_roi(self.sample_inputs)
        chilean = results['chilean_specifics']
        
        # Check IVA rate
        self.assertEqual(chilean['iva_rate'], 0.19)
        
        # Check IVA calculations
        iva_data = chilean['savings_with_iva']
        expected_iva_amount = results['savings']['annual_total'] * 0.19
        
        self.assertAlmostEqual(iva_data['iva_amount'], expected_iva_amount, places=2)
        self.assertAlmostEqual(
            iva_data['amount_with_iva'], 
            iva_data['amount_before_iva'] + iva_data['iva_amount'], 
            places=2
        )
    
    def test_input_validation(self):
        """Test input validation"""
        # Test missing required field
        invalid_inputs = self.sample_inputs.copy()
        del invalid_inputs['annual_revenue']
        
        with self.assertRaises(ValueError):
            self.calculator.calculate_roi(invalid_inputs)
        
        # Test negative value
        invalid_inputs = self.sample_inputs.copy()
        invalid_inputs['annual_revenue'] = -1000
        
        with self.assertRaises(ValueError):
            self.calculator.calculate_roi(invalid_inputs)
        
        # Test non-numeric value
        invalid_inputs = self.sample_inputs.copy()
        invalid_inputs['annual_revenue'] = "not a number"
        
        with self.assertRaises(ValueError):
            self.calculator.calculate_roi(invalid_inputs)
    
    def test_summary_text_generation(self):
        """Test summary text generation"""
        results = self.calculator.calculate_roi(self.sample_inputs)
        summary = self.calculator.get_summary_text()
        
        self.assertIsInstance(summary, str)
        self.assertIn('ROI CALCULATION SUMMARY', summary)
        self.assertIn('Investment:', summary)
        self.assertIn('Annual Savings:', summary)
    
    def test_json_export(self):
        """Test JSON export functionality"""
        results = self.calculator.calculate_roi(self.sample_inputs)
        
        # Export to JSON
        filename = self.calculator.export_to_json('test_export.json')
        
        # Check file was created
        self.assertTrue(os.path.exists(filename))
        
        # Check file content
        with open(filename, 'r') as f:
            exported_data = json.load(f)
        
        self.assertEqual(exported_data['inputs']['annual_revenue'], 
                        self.sample_inputs['annual_revenue'])
        
        # Clean up
        os.remove(filename)
    
    def test_edge_cases(self):
        """Test edge cases"""
        # Very small business
        small_inputs = {
            'annual_revenue': 100000,
            'monthly_orders': 500,
            'avg_order_value': 16.67,
            'labor_costs': 2000,
            'shipping_costs': 1000,
            'error_costs': 300,
            'inventory_costs': 500,
            'service_investment': 15000
        }
        
        results = self.calculator.calculate_roi(small_inputs)
        self.assertIsInstance(results, dict)
        
        # Very large business
        large_inputs = {
            'annual_revenue': 10000000,
            'monthly_orders': 25000,
            'avg_order_value': 33.33,
            'labor_costs': 50000,
            'shipping_costs': 30000,
            'error_costs': 10000,
            'inventory_costs': 20000,
            'service_investment': 200000
        }
        
        results = self.calculator.calculate_roi(large_inputs)
        self.assertIsInstance(results, dict)
    
    def test_payback_period_formatting(self):
        """Test payback period formatting"""
        # Test less than 1 month
        formatted = self.calculator._format_payback_period(0.5)
        self.assertIn('days', formatted)
        
        # Test months
        formatted = self.calculator._format_payback_period(6.5)
        self.assertIn('months', formatted)
        
        # Test years
        formatted = self.calculator._format_payback_period(18.5)
        self.assertIn('years', formatted)


class TestCalculatorBoundaryConditions(unittest.TestCase):
    """Test boundary conditions and error cases"""
    
    def setUp(self):
        self.calculator = ROICalculator()
    
    def test_zero_investment(self):
        """Test with zero investment (edge case)"""
        inputs = {
            'annual_revenue': 1000000,
            'monthly_orders': 3000,
            'avg_order_value': 27.78,
            'labor_costs': 5000,
            'shipping_costs': 3000,
            'error_costs': 1000,
            'inventory_costs': 2000,
            'service_investment': 0  # Zero investment
        }
        
        # Should still calculate but with infinite ROI
        results = self.calculator.calculate_roi(inputs)
        self.assertIsInstance(results, dict)
    
    def test_high_costs_vs_revenue(self):
        """Test when costs are very high relative to revenue"""
        inputs = {
            'annual_revenue': 500000,  # Low revenue
            'monthly_orders': 1000,
            'avg_order_value': 41.67,
            'labor_costs': 20000,  # Very high costs
            'shipping_costs': 15000,
            'error_costs': 5000,
            'inventory_costs': 10000,
            'service_investment': 75000
        }
        
        results = self.calculator.calculate_roi(inputs)
        
        # Should still calculate even if costs are high
        self.assertIsInstance(results, dict)
        
        # Savings should be significant due to high baseline costs
        self.assertGreater(results['savings']['annual_total'], 100000)


if __name__ == '__main__':
    unittest.main()
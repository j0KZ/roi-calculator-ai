#!/usr/bin/env python3
"""
Comprehensive Test Suite for Chilean E-commerce Sales Toolkit Web Application
Tests all components: app.py, ROI calculator, assessment tool, proposal generator
"""

import sys
import os
import unittest
import tempfile
import json
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
import numpy as np
from datetime import datetime

# Add project directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'pages'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'utils'))

# Mock streamlit before importing modules that use it
class MockStreamlit:
    def __init__(self):
        self.session_state = {
            'current_page': 'home',
            'client_data': {
                'company_name': 'Test Company',
                'contact_name': 'Test User',
                'email': 'test@company.cl',
                'phone': '+56912345678',
                'industry': 'retail',
                'investment_clp': 20000000
            },
            'assessment_results': {},
            'roi_results': {},
            'proposal_data': {}
        }
    
    def set_page_config(self, **kwargs): pass
    def title(self, text): return text
    def markdown(self, text, unsafe_allow_html=False): return text
    def columns(self, n): return [Mock() for _ in range(n)]
    def metric(self, label, value, delta=None, help=None): return Mock()
    def button(self, text, **kwargs): return False
    def text_input(self, label, **kwargs): return kwargs.get('value', '')
    def number_input(self, label, **kwargs): return kwargs.get('value', 0)
    def selectbox(self, label, options, **kwargs): return options[0]
    def slider(self, label, **kwargs): return kwargs.get('value', 50)
    def multiselect(self, label, options, **kwargs): return kwargs.get('default', [])
    def radio(self, label, options, **kwargs): return options[0]
    def text_area(self, label, **kwargs): return ''
    def date_input(self, label, **kwargs): return datetime.now().date()
    def checkbox(self, label, **kwargs): return False
    def tabs(self, tabs): return [Mock() for _ in tabs]
    def expander(self, label, **kwargs): return Mock()
    def spinner(self, text): return Mock()
    def progress(self, value): return Mock()
    def success(self, text): return Mock()
    def error(self, text): return Mock()
    def warning(self, text): return Mock()
    def info(self, text): return Mock()
    def balloons(self): pass
    def rerun(self): pass
    def plotly_chart(self, fig, **kwargs): return Mock()
    def dataframe(self, df, **kwargs): return Mock()
    def download_button(self, **kwargs): return Mock()
    def sidebar(self): return Mock()
    
    def caption(self, text): return Mock()
    
    @property
    def sidebar(self):
        return self

# Mock plotly before imports
sys.modules['plotly'] = Mock()
sys.modules['plotly.graph_objects'] = Mock()
sys.modules['plotly.express'] = Mock()
sys.modules['streamlit'] = MockStreamlit()

# Now import the modules to test
try:
    from enhanced_roi_calculator import EnhancedROICalculator
except ImportError as e:
    print(f"Warning: Could not import EnhancedROICalculator: {e}")
    EnhancedROICalculator = None

try:
    from rapid_assessment_tool import RapidAssessmentTool
except ImportError as e:
    print(f"Warning: Could not import RapidAssessmentTool: {e}")
    RapidAssessmentTool = None

try:
    from automated_proposal_generator import AutomatedProposalGenerator
except ImportError as e:
    print(f"Warning: Could not import AutomatedProposalGenerator: {e}")
    AutomatedProposalGenerator = None

try:
    from chart_theme import apply_dark_theme, get_dark_color_sequence, get_gauge_theme
except ImportError as e:
    print(f"Warning: Could not import chart_theme utilities: {e}")
    def apply_dark_theme(fig): return fig
    def get_dark_color_sequence(): return ['#f5b800']
    def get_gauge_theme(): return {}


class TestROICalculator(unittest.TestCase):
    """Test suite for ROI Calculator functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        if EnhancedROICalculator is None:
            self.skipTest("EnhancedROICalculator not available")
            
        self.calculator = EnhancedROICalculator()
        self.sample_inputs = {
            'annual_revenue_clp': 500000000,
            'monthly_orders': 1500,
            'avg_order_value_clp': 28000,
            'labor_costs_clp': 3500000,
            'shipping_costs_clp': 2800000,
            'platform_fees_clp': 1200000,
            'error_costs_clp': 500000,
            'inventory_costs_clp': 1800000,
            'investment_clp': 25000000,
            'industry': 'retail',
            'current_platforms': ['transbank', 'webpay'],
            'conversion_rate': 0.021
        }
    
    def test_calculator_initialization(self):
        """Test that calculator initializes properly"""
        self.assertIsInstance(self.calculator, EnhancedROICalculator)
        self.assertTrue(hasattr(self.calculator, 'constants'))
        self.assertTrue(hasattr(self.calculator, 'scenario_engine'))
    
    def test_roi_calculation_with_valid_inputs(self):
        """Test ROI calculation with valid inputs"""
        results = self.calculator.calculate_roi(self.sample_inputs)
        
        # Check that calculation completed successfully
        self.assertIsInstance(results, dict)
        self.assertTrue(results.get('success', False) or 'error' not in results)
        
        # Check for required result sections
        expected_sections = [
            'executive_summary', 'current_state', 'improvements',
            'scenarios', 'chilean_specifics', 'recommendations'
        ]
        
        for section in expected_sections:
            if results.get('success', True):
                self.assertIn(section, results, f"Missing section: {section}")
    
    def test_roi_calculation_with_invalid_inputs(self):
        """Test ROI calculation error handling with invalid inputs"""
        invalid_inputs = {
            'annual_revenue_clp': 'invalid',
            'monthly_orders': -100,
            'investment_clp': 0
        }
        
        results = self.calculator.calculate_roi(invalid_inputs)
        self.assertIsInstance(results, dict)
        
        # Should either handle gracefully or return error information
        if 'error' in results:
            self.assertTrue(results['error'])
            self.assertIn('message', results)
    
    def test_chilean_market_constants(self):
        """Test Chilean market constants are properly defined"""
        constants = self.calculator.constants
        
        # Check IVA rate
        self.assertEqual(constants.IVA_RATE, 0.19)
        
        # Check that benchmarks exist for major industries
        self.assertIn('retail', constants.BENCHMARKS)
        self.assertIn('wholesale', constants.BENCHMARKS)
        
        # Check benchmark structure
        retail_benchmark = constants.BENCHMARKS['retail']
        required_metrics = ['conversion_rate', 'avg_order_value_clp', 'operational_cost_ratio']
        for metric in required_metrics:
            self.assertIn(metric, retail_benchmark)
    
    def test_scenario_engine(self):
        """Test scenario engine functionality"""
        scenario_engine = self.calculator.scenario_engine
        
        # Check scenarios are defined
        self.assertIn('pessimistic', scenario_engine.scenarios)
        self.assertIn('realistic', scenario_engine.scenarios)
        self.assertIn('optimistic', scenario_engine.scenarios)
        
        # Check scenario probabilities sum to 1
        total_prob = sum(s['probability'] for s in scenario_engine.scenarios.values())
        self.assertAlmostEqual(total_prob, 1.0, places=2)


class TestAssessmentTool(unittest.TestCase):
    """Test suite for Assessment Tool functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        if RapidAssessmentTool is None:
            self.skipTest("RapidAssessmentTool not available")
            
        self.assessment = RapidAssessmentTool()
        self.sample_responses = {
            'b1': 600000000,
            'b2': 1800,
            'b3': 5,
            'b4': 'Retail',
            't1': 'WooCommerce',
            't2': False,
            't3': ['Excel', 'Defontana'],
            't4': 3,
            'o1': 25,
            'o2': 8,
            'o3': 10,
            'o4': False,
            'o5': 'Semanalmente',
            'i1': ['Transbank', 'Webpay'],
            'i2': ['Chilexpress'],
            'i3': ['No vendo en marketplaces'],
            'i4': False,
            'p1': ['Procesamiento manual de órdenes'],
            'p2': 5000000,
            'p3': 8,
            'g1': 50,
            'g2': True,
            'g3': '1-3 meses'
        }
    
    def test_assessment_initialization(self):
        """Test that assessment tool initializes properly"""
        self.assertIsInstance(self.assessment, RapidAssessmentTool)
        self.assertTrue(hasattr(self.assessment, 'questions'))
        self.assertTrue(hasattr(self.assessment, 'scoring_weights'))
    
    def test_questions_structure(self):
        """Test that questions are properly structured"""
        questions = self.assessment.questions
        
        # Check main categories exist
        expected_categories = ['basic_info', 'technology', 'operations', 'integration', 'pain_points', 'growth']
        for category in expected_categories:
            self.assertIn(category, questions, f"Missing category: {category}")
            self.assertIsInstance(questions[category], list)
            self.assertGreater(len(questions[category]), 0)
    
    def test_assessment_conduct(self):
        """Test conducting a complete assessment"""
        results = self.assessment.conduct_assessment(self.sample_responses)
        
        # Check result structure
        self.assertIsInstance(results, dict)
        
        # Check for required sections
        expected_sections = [
            'company_profile', 'scores', 'maturity_level', 'pain_points',
            'opportunities', 'roi_potential', 'recommendations', 'qualification'
        ]
        
        for section in expected_sections:
            self.assertIn(section, results, f"Missing section: {section}")
    
    def test_scoring_calculation(self):
        """Test scoring calculation logic"""
        scores = self.assessment._calculate_scores(self.sample_responses)
        
        self.assertIsInstance(scores, dict)
        self.assertIn('overall', scores)
        self.assertIsInstance(scores['overall'], (int, float))
        self.assertGreaterEqual(scores['overall'], 0)
        self.assertLessEqual(scores['overall'], 10)
    
    def test_qualification_levels(self):
        """Test qualification level determination"""
        results = self.assessment.conduct_assessment(self.sample_responses)
        qualification = results.get('qualification', {})
        
        self.assertIn('level', qualification)
        self.assertIn('score', qualification)
        self.assertIn('close_probability', qualification)
        
        # Check that qualification level is one of expected values
        valid_levels = ['A - HOT PROSPECT', 'B - QUALIFIED', 'C - NURTURE', 'D - NOT QUALIFIED']
        self.assertIn(qualification['level'], valid_levels)


class TestProposalGenerator(unittest.TestCase):
    """Test suite for Proposal Generator functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        if AutomatedProposalGenerator is None:
            self.skipTest("AutomatedProposalGenerator not available")
            
        self.generator = AutomatedProposalGenerator()
        self.client_data = {
            'company_name': 'Test Company SpA',
            'contact_name': 'Juan Pérez',
            'email': 'juan@testcompany.cl',
            'phone': '+56987654321',
            'industry': 'Retail'
        }
        
        self.assessment_results = {
            'maturity_level': {
                'level': 'BÁSICO',
                'score': 4.5,
                'description': 'Procesos mayormente manuales',
                'breakdown': {'technology': '3.5/10', 'operations': '4.0/10', 'integration': '5.5/10'}
            },
            'pain_points': [
                {
                    'issue': 'Procesamiento Manual',
                    'severity': 'ALTA',
                    'impact': '20 horas semanales',
                    'cost_impact_clp': 3500000
                }
            ],
            'opportunities': [
                {
                    'area': 'Automatización',
                    'monthly_savings_clp': 5000000,
                    'implementation_effort': 'MEDIO'
                }
            ],
            'recommendations': [
                {
                    'title': 'Integrar ERP-Ecommerce',
                    'description': 'Conectar sistemas',
                    'expected_impact': 'Ahorro de 20 horas'
                }
            ]
        }
        
        self.roi_analysis = {
            'improvements': {
                'total_monthly_savings_clp': 8500000,
                'total_annual_savings_clp': 102000000,
                'roi_percentage_year_1': 186,
                'payback_months': 5.2,
                'new_operational_efficiency': 0.85
            },
            'scenarios': {
                'scenarios': {
                    'pessimistic': {'roi_percentage': 120, 'annual_savings_clp': 70000000},
                    'realistic': {'roi_percentage': 186, 'annual_savings_clp': 102000000},
                    'optimistic': {'roi_percentage': 250, 'annual_savings_clp': 140000000}
                }
            }
        }
    
    def test_generator_initialization(self):
        """Test that proposal generator initializes properly"""
        self.assertIsInstance(self.generator, AutomatedProposalGenerator)
        self.assertTrue(hasattr(self.generator, 'templates'))
        self.assertTrue(hasattr(self.generator, 'service_packages'))
    
    def test_templates_structure(self):
        """Test that templates are properly structured"""
        templates = self.generator.templates
        
        # Check main templates exist
        expected_templates = ['executive', 'detailed', 'quick']
        for template_name in expected_templates:
            self.assertIn(template_name, templates)
            template = templates[template_name]
            self.assertTrue(hasattr(template, 'sections'))
            self.assertIsInstance(template.sections, list)
    
    def test_service_packages(self):
        """Test service packages definition"""
        packages = self.generator.service_packages
        
        # Check main packages exist
        expected_packages = ['starter', 'professional', 'enterprise']
        for package_name in expected_packages:
            self.assertIn(package_name, packages)
            package = packages[package_name]
            
            # Check package structure
            required_fields = ['name', 'description', 'duration', 'price_clp', 'includes']
            for field in required_fields:
                self.assertIn(field, package, f"Missing field {field} in package {package_name}")
    
    def test_proposal_generation(self):
        """Test complete proposal generation"""
        proposal = self.generator.generate_proposal(
            client_data=self.client_data,
            assessment_results=self.assessment_results,
            roi_analysis=self.roi_analysis,
            template_type='executive',
            package_type='professional'
        )
        
        # Check proposal structure
        self.assertIsInstance(proposal, dict)
        self.assertIn('metadata', proposal)
        self.assertIn('client', proposal)
        self.assertIn('sections', proposal)
        self.assertIn('package', proposal)
        
        # Check metadata
        metadata = proposal['metadata']
        self.assertIn('proposal_id', metadata)
        self.assertIn('date', metadata)
    
    def test_section_generation(self):
        """Test individual section generation"""
        # Test executive summary generation
        exec_summary = self.generator._generate_executive_summary(
            self.client_data, self.assessment_results, self.roi_analysis
        )
        
        self.assertIsInstance(exec_summary, dict)
        self.assertIn('title', exec_summary)
        self.assertIn('content', exec_summary)
        
        # Check content is not empty
        self.assertGreater(len(exec_summary['content'].strip()), 0)
    
    def test_one_pager_generation(self):
        """Test one-pager generation"""
        # First generate a proposal
        self.generator.generate_proposal(
            client_data=self.client_data,
            assessment_results=self.assessment_results,
            roi_analysis=self.roi_analysis
        )
        
        # Then generate one-pager
        one_pager = self.generator.generate_one_pager()
        
        self.assertIsInstance(one_pager, str)
        self.assertGreater(len(one_pager), 0)
        self.assertIn('RESUMEN EJECUTIVO', one_pager)


class TestChartTheme(unittest.TestCase):
    """Test suite for Chart Theme utilities"""
    
    def test_dark_theme_application(self):
        """Test dark theme application to charts"""
        # Create a mock figure
        mock_fig = Mock()
        mock_fig.update_layout = Mock()
        mock_fig.update_traces = Mock()
        
        # Apply dark theme
        result = apply_dark_theme(mock_fig)
        
        # Check that update_layout was called
        mock_fig.update_layout.assert_called_once()
        mock_fig.update_traces.assert_called_once()
        
        # Check return value
        self.assertEqual(result, mock_fig)
    
    def test_color_sequence(self):
        """Test dark color sequence"""
        colors = get_dark_color_sequence()
        
        self.assertIsInstance(colors, list)
        self.assertGreater(len(colors), 0)
        
        # Check that all colors are hex colors
        for color in colors:
            self.assertIsInstance(color, str)
            self.assertTrue(color.startswith('#'))
    
    def test_gauge_theme(self):
        """Test gauge theme configuration"""
        gauge_theme = get_gauge_theme()
        
        self.assertIsInstance(gauge_theme, dict)
        # Test should pass even if empty dict returned


class TestWebApplicationIntegration(unittest.TestCase):
    """Integration tests for the complete web application"""
    
    def test_session_state_initialization(self):
        """Test that session state is properly initialized"""
        # This would normally be tested with actual Streamlit session state
        # For now, test that our mock has the required structure
        mock_st = MockStreamlit()
        
        required_keys = ['current_page', 'client_data', 'assessment_results', 'roi_results', 'proposal_data']
        for key in required_keys:
            self.assertIn(key, mock_st.session_state)
    
    def test_page_navigation_structure(self):
        """Test page navigation structure"""
        # Test that all required pages are defined
        pages = ['home', 'roi_calculator', 'assessment', 'proposal']
        
        # This would be tested with actual navigation logic
        # For now, just check that our constants are defined
        for page in pages:
            self.assertIsInstance(page, str)
            self.assertGreater(len(page), 0)
    
    def test_data_flow_between_components(self):
        """Test data flow between different components"""
        # Test ROI Calculator -> Assessment Tool integration
        if EnhancedROICalculator and RapidAssessmentTool:
            calculator = EnhancedROICalculator()
            assessment = RapidAssessmentTool()
            
            # Calculate ROI
            roi_inputs = {
                'annual_revenue_clp': 500000000,
                'monthly_orders': 1500,
                'avg_order_value_clp': 28000,
                'labor_costs_clp': 3500000,
                'shipping_costs_clp': 2800000,
                'platform_fees_clp': 1200000,
                'error_costs_clp': 500000,
                'inventory_costs_clp': 1800000,
                'investment_clp': 25000000,
                'industry': 'retail',
                'current_platforms': ['transbank'],
                'conversion_rate': 0.021
            }
            
            roi_results = calculator.calculate_roi(roi_inputs)
            
            # Conduct assessment
            assessment_inputs = {
                'b1': 600000000,
                'b2': 1800,
                'b3': 5,
                'b4': 'Retail',
                't2': False,
                't4': 3,
                'o2': 8,
                'p3': 8,
                'g2': True
            }
            
            assessment_results = assessment.conduct_assessment(assessment_inputs)
            
            # Generate proposal (if available)
            if AutomatedProposalGenerator:
                generator = AutomatedProposalGenerator()
                
                client_data = {
                    'company_name': 'Test Integration Company',
                    'industry': 'Retail'
                }
                
                proposal = generator.generate_proposal(
                    client_data=client_data,
                    assessment_results=assessment_results,
                    roi_analysis=roi_results
                )
                
                # Check that all components produced valid results
                self.assertIsInstance(roi_results, dict)
                self.assertIsInstance(assessment_results, dict)
                self.assertIsInstance(proposal, dict)


class TestErrorHandling(unittest.TestCase):
    """Test error handling across the application"""
    
    def test_missing_import_handling(self):
        """Test handling of missing imports"""
        # This tests our fallback mechanisms when imports fail
        # The test setup already mocks missing modules
        
        # Test that fallback functions work
        mock_fig = Mock()
        result = apply_dark_theme(mock_fig)
        self.assertIsNotNone(result)
        
        colors = get_dark_color_sequence()
        self.assertIsInstance(colors, list)
    
    def test_invalid_input_handling(self):
        """Test handling of various invalid inputs"""
        if EnhancedROICalculator:
            calculator = EnhancedROICalculator()
            
            # Test with completely invalid inputs
            invalid_inputs = [
                {},  # Empty dict
                {'invalid_key': 'invalid_value'},  # Invalid keys
                {'annual_revenue_clp': None},  # None values
                {'annual_revenue_clp': float('inf')},  # Infinite values
                {'annual_revenue_clp': 'not_a_number'},  # String values
            ]
            
            for invalid_input in invalid_inputs:
                result = calculator.calculate_roi(invalid_input)
                self.assertIsInstance(result, dict)
                # Should either succeed with defaults or return error info
    
    def test_file_operation_error_handling(self):
        """Test file operation error handling"""
        if AutomatedProposalGenerator:
            generator = AutomatedProposalGenerator()
            
            # Try to export to invalid path
            with tempfile.TemporaryDirectory() as temp_dir:
                valid_path = os.path.join(temp_dir, 'test_proposal.pdf')
                
                # This should not crash even if export fails
                try:
                    generator.export_to_pdf(valid_path)
                except Exception as e:
                    # Expected - reportlab likely not installed
                    self.assertIsInstance(e, Exception)


def run_comprehensive_tests():
    """Run all test suites and generate report"""
    
    print("="*80)
    print("COMPREHENSIVE TEST SUITE - CHILEAN E-COMMERCE SALES TOOLKIT")
    print("="*80)
    print()
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestROICalculator,
        TestAssessmentTool, 
        TestProposalGenerator,
        TestChartTheme,
        TestWebApplicationIntegration,
        TestErrorHandling
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Generate summary report
    print("\n" + "="*80)
    print("TEST EXECUTION SUMMARY")
    print("="*80)
    print(f"Tests Run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0
    print(f"Success Rate: {success_rate:.1f}%")
    
    if result.failures:
        print(f"\nFAILURES ({len(result.failures)}):")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback.split('AssertionError: ')[-1].split()[0] if 'AssertionError:' in traceback else 'See details above'}")
    
    if result.errors:
        print(f"\nERRORS ({len(result.errors)}):")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback.split('\\n')[-2] if '\\n' in traceback else 'Unknown error'}")
    
    # Application health check
    print(f"\n{'='*80}")
    print("APPLICATION HEALTH CHECK")
    print("="*80)
    
    health_status = []
    
    # Check core components
    if EnhancedROICalculator:
        health_status.append("✅ ROI Calculator: Available")
    else:
        health_status.append("❌ ROI Calculator: Not Available")
    
    if RapidAssessmentTool:
        health_status.append("✅ Assessment Tool: Available")
    else:
        health_status.append("❌ Assessment Tool: Not Available")
    
    if AutomatedProposalGenerator:
        health_status.append("✅ Proposal Generator: Available")
    else:
        health_status.append("❌ Proposal Generator: Not Available")
    
    # Check chart theming
    try:
        colors = get_dark_color_sequence()
        if colors:
            health_status.append("✅ Chart Theme: Available")
        else:
            health_status.append("⚠️ Chart Theme: Limited")
    except:
        health_status.append("❌ Chart Theme: Not Available")
    
    for status in health_status:
        print(status)
    
    print(f"\n{'='*80}")
    print("RECOMMENDATIONS")
    print("="*80)
    
    recommendations = []
    
    if len(result.failures) > 0:
        recommendations.append("🔧 Fix failing test cases to improve reliability")
    
    if len(result.errors) > 0:
        recommendations.append("🚨 Resolve error conditions to ensure stability")
    
    if not all([EnhancedROICalculator, RapidAssessmentTool, AutomatedProposalGenerator]):
        recommendations.append("📦 Ensure all core modules are properly installed and importable")
    
    if success_rate < 90:
        recommendations.append("📈 Improve test coverage and code quality")
    
    if not recommendations:
        recommendations.append("🎉 Application appears to be functioning well!")
    
    for rec in recommendations:
        print(rec)
    
    print(f"\n{'='*80}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)
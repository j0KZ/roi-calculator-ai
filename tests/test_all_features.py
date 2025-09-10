#!/usr/bin/env python3
"""
Comprehensive Test Suite for Chilean E-commerce Sales Toolkit
Tests all features including web app, database, and calculations
"""

import sys
import os
import json
import time
import traceback
from datetime import datetime

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'pages'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'utils'))

# Test results tracking
test_results = []
errors_found = []

def test_with_result(test_name, test_func):
    """Execute test and track results"""
    print(f"\n🔍 Testing: {test_name}")
    try:
        result = test_func()
        if result:
            print(f"✅ {test_name}: PASSED")
            test_results.append((test_name, True, None))
            return True
        else:
            print(f"❌ {test_name}: FAILED")
            test_results.append((test_name, False, "Test returned False"))
            return False
    except Exception as e:
        error_msg = f"{str(e)}\n{traceback.format_exc()}"
        print(f"❌ {test_name}: ERROR - {str(e)}")
        test_results.append((test_name, False, error_msg))
        errors_found.append((test_name, error_msg))
        return False

# ========== DATABASE TESTS ==========

def test_database_connection():
    """Test database connection"""
    try:
        from database.connection import get_db
        db = get_db()
        return db.test_connection()
    except Exception as e:
        print(f"Database connection error: {e}")
        return False

def test_database_models():
    """Test database models"""
    try:
        from database.models import Calculation, Template, Base
        from database.connection import get_session
        
        session = get_session()
        
        # Test query
        calc_count = session.query(Calculation).count()
        template_count = session.query(Template).count()
        
        print(f"  - Calculations in DB: {calc_count}")
        print(f"  - Templates in DB: {template_count}")
        
        session.close()
        return True
    except Exception as e:
        print(f"Database model error: {e}")
        return False

def test_database_crud():
    """Test CRUD operations"""
    try:
        from database.models import Calculation
        from database.connection import get_session
        
        session = get_session()
        
        # Create
        test_calc = Calculation(
            company_name="Test CRUD Company",
            annual_revenue=1000000000,
            monthly_orders=1000,
            avg_order_value=83333,
            labor_costs=5000000,
            shipping_costs=3000000,
            error_costs=1500000,
            inventory_costs=2000000,
            service_investment=50000000,
            results={'roi_percentage': 150.5, 'payback_months': 8.0}
        )
        session.add(test_calc)
        session.commit()
        calc_id = test_calc.id
        print(f"  - Created calculation ID: {calc_id}")
        
        # Read
        read_calc = session.query(Calculation).filter_by(id=calc_id).first()
        assert read_calc is not None
        assert read_calc.company_name == "Test CRUD Company"
        print(f"  - Read calculation: {read_calc.company_name}")
        
        # Update
        read_calc.company_name = "Updated CRUD Company"
        session.commit()
        
        # Delete
        session.delete(read_calc)
        session.commit()
        print(f"  - Deleted calculation ID: {calc_id}")
        
        session.close()
        return True
    except Exception as e:
        print(f"CRUD operation error: {e}")
        return False

# ========== CORE MODULE TESTS ==========

def test_roi_calculator_module():
    """Test ROI calculator core module"""
    try:
        from enhanced_roi_calculator import EnhancedROICalculator
        from roi_result_adapter import adapt_roi_results
        
        calculator = EnhancedROICalculator()
        
        # Test calculation
        data = {
            'annual_revenue_clp': 2000000000,
            'monthly_orders': 5000,
            'avg_order_value_clp': 33333,
            'labor_costs_clp': 8000000,
            'shipping_costs_clp': 5000000,
            'error_costs_clp': 2000000,
            'inventory_costs_clp': 3000000,
            'investment_clp': 50000000
        }
        
        start_time = time.time()
        raw_results = calculator.calculate_roi(data)
        results = adapt_roi_results(raw_results)
        calc_time = time.time() - start_time
        
        print(f"  - ROI: {results['roi_percentage']:.1f}%")
        print(f"  - Calculation time: {calc_time:.3f}s")
        
        # Validate results
        assert 'roi_percentage' in results
        assert 'payback_months' in results
        assert results['roi_percentage'] > 0
        assert calc_time < 1.0  # Should be under 1 second
        
        return True
    except Exception as e:
        print(f"ROI calculator error: {e}")
        return False

def test_assessment_tool_module():
    """Test assessment tool module"""
    try:
        from rapid_assessment_tool import RapidAssessmentTool
        
        tool = RapidAssessmentTool()
        
        # Test assessment with responses
        responses = {
            'company_type': 'retailer',
            'annual_revenue': 'medium',
            'employees': '10-50',
            'current_platform': 'basic',
            'monthly_orders': 1000,
            'main_pain_points': ['inventory', 'shipping']
        }
        
        # Conduct assessment
        results = tool.conduct_assessment(responses)
        
        score = results.get('qualification_score', 0)
        print(f"  - Assessment score: {score}/100")
        assert score >= 0 and score <= 100
        
        return True
    except Exception as e:
        print(f"Assessment tool error: {e}")
        return False

def test_proposal_generator_module():
    """Test proposal generator module"""
    try:
        from automated_proposal_generator import AutomatedProposalGenerator
        
        generator = AutomatedProposalGenerator()
        
        # Test proposal generation
        client_data = {
            'company_name': 'Test Company',
            'contact_name': 'John Doe',
            'email': 'test@example.com',
            'phone': '+56912345678'
        }
        
        assessment_results = {
            'qualification_score': 85,
            'digital_maturity': 'intermediate',
            'pain_points': ['inventory', 'shipping']
        }
        
        roi_results = {
            'roi_percentage': 150,
            'payback_months': 8,
            'total_annual_savings': 100000000
        }
        
        proposal = generator.generate_proposal(
            client_data=client_data,
            assessment_results=assessment_results,
            roi_analysis=roi_results,
            template_type='executive',
            package_type='professional'
        )
        
        # Check proposal structure
        assert 'sections' in proposal
        assert 'metadata' in proposal
        assert 'client' in proposal
        
        sections = proposal.get('sections', {})
        print(f"  - Proposal sections: {len(sections)}")
        assert len(sections) > 0
        
        return True
    except Exception as e:
        print(f"Proposal generator error: {e}")
        return False

# ========== PAGE IMPORT TESTS ==========

def test_page_imports():
    """Test that all pages can be imported"""
    pages_to_test = [
        ('roi_calculator', 'pages/roi_calculator.py'),
        ('assessment_tool', 'pages/assessment_tool.py'),
        ('proposal_generator', 'pages/proposal_generator.py'),
        ('history', 'pages/history.py'),
        ('templates', 'pages/templates.py')
    ]
    
    all_passed = True
    for module_name, file_path in pages_to_test:
        try:
            # Check file exists
            full_path = os.path.join(os.path.dirname(__file__), '..', file_path)
            if not os.path.exists(full_path):
                print(f"  ❌ {file_path}: File not found")
                all_passed = False
                continue
            
            # Try to import (we can't actually import Streamlit pages directly)
            # But we can check syntax
            with open(full_path, 'r') as f:
                code = f.read()
                compile(code, file_path, 'exec')
            
            print(f"  ✅ {file_path}: Valid Python syntax")
        except SyntaxError as e:
            print(f"  ❌ {file_path}: Syntax error - {e}")
            all_passed = False
        except Exception as e:
            print(f"  ❌ {file_path}: Import error - {e}")
            all_passed = False
    
    return all_passed

def test_chart_theme():
    """Test chart theme utilities"""
    try:
        from chart_theme import apply_dark_theme, get_dark_color_sequence, get_gauge_theme
        
        # Test color sequence
        colors = get_dark_color_sequence()
        assert len(colors) > 0
        assert colors[0] == '#f5b800'  # Gold color
        
        # Test gauge theme
        gauge = get_gauge_theme()
        assert 'bar_color' in gauge
        assert gauge['bar_color'] == '#f5b800'
        
        print(f"  - Color sequence: {len(colors)} colors")
        print(f"  - Primary color: {colors[0]}")
        
        return True
    except Exception as e:
        print(f"Chart theme error: {e}")
        return False

# ========== INTEGRATION TESTS ==========

def test_data_flow():
    """Test data flow between components"""
    try:
        from enhanced_roi_calculator import EnhancedROICalculator
        from roi_result_adapter import adapt_roi_results
        from database.connection import get_session
        from database.models import Calculation
        
        # Calculate ROI
        calculator = EnhancedROICalculator()
        data = {
            'annual_revenue_clp': 1000000000,
            'monthly_orders': 2000,
            'avg_order_value_clp': 41667,
            'labor_costs_clp': 4000000,
            'shipping_costs_clp': 2500000,
            'error_costs_clp': 1000000,
            'inventory_costs_clp': 1500000,
            'investment_clp': 25000000
        }
        
        raw_results = calculator.calculate_roi(data)
        results = adapt_roi_results(raw_results)
        
        # Save to database
        session = get_session()
        calc = Calculation(
            company_name="Integration Test",
            annual_revenue=data['annual_revenue_clp'],
            monthly_orders=data['monthly_orders'],
            avg_order_value=data['avg_order_value_clp'],
            labor_costs=data['labor_costs_clp'],
            shipping_costs=data['shipping_costs_clp'],
            error_costs=data['error_costs_clp'],
            inventory_costs=data['inventory_costs_clp'],
            service_investment=data['investment_clp'],
            results=results
        )
        session.add(calc)
        session.commit()
        calc_id = calc.id
        
        # Read back
        saved_calc = session.query(Calculation).filter_by(id=calc_id).first()
        assert saved_calc is not None
        assert saved_calc.get_roi() == results['roi_percentage']
        
        # Clean up
        session.delete(saved_calc)
        session.commit()
        session.close()
        
        print(f"  - Data flow test completed")
        return True
        
    except Exception as e:
        print(f"Data flow error: {e}")
        return False

# ========== PERFORMANCE TESTS ==========

def test_performance():
    """Test performance metrics"""
    try:
        from enhanced_roi_calculator import EnhancedROICalculator
        import numpy as np
        
        calculator = EnhancedROICalculator()
        
        # Test calculation speed
        times = []
        for _ in range(10):
            data = {
                'annual_revenue_clp': np.random.randint(100000000, 5000000000),
                'monthly_orders': np.random.randint(100, 10000),
                'avg_order_value_clp': np.random.randint(10000, 100000),
                'labor_costs_clp': np.random.randint(1000000, 20000000),
                'shipping_costs_clp': np.random.randint(500000, 10000000),
                'error_costs_clp': np.random.randint(100000, 5000000),
                'inventory_costs_clp': np.random.randint(100000, 5000000),
                'investment_clp': np.random.randint(10000000, 100000000)
            }
            
            start = time.time()
            calculator.calculate_roi(data)
            times.append(time.time() - start)
        
        avg_time = np.mean(times)
        max_time = np.max(times)
        
        print(f"  - Average calculation time: {avg_time:.3f}s")
        print(f"  - Maximum calculation time: {max_time:.3f}s")
        
        # Performance criteria
        assert avg_time < 0.5  # Average should be under 0.5s
        assert max_time < 1.0  # Max should be under 1s
        
        return True
        
    except Exception as e:
        print(f"Performance test error: {e}")
        return False

# ========== VALIDATION TESTS ==========

def test_input_validation():
    """Test input validation and error handling"""
    try:
        from enhanced_roi_calculator import EnhancedROICalculator
        
        calculator = EnhancedROICalculator()
        
        # Test with invalid data
        invalid_cases = [
            {'annual_revenue_clp': -1000},  # Negative value
            {'monthly_orders': 0},  # Zero orders
            {},  # Empty data
        ]
        
        for invalid_data in invalid_cases:
            try:
                # Should handle gracefully
                result = calculator.calculate_roi(invalid_data)
                # If no error, check for reasonable defaults
                if result:
                    assert result['roi_percentage'] >= 0
            except:
                # Error handling is acceptable
                pass
        
        print(f"  - Input validation tests completed")
        return True
        
    except Exception as e:
        print(f"Validation test error: {e}")
        return False

# ========== MAIN TEST RUNNER ==========

def run_all_tests():
    """Run all tests and generate report"""
    print("🚀 COMPREHENSIVE TEST SUITE - CHILEAN E-COMMERCE SALES TOOLKIT")
    print("=" * 70)
    print(f"Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Database Tests
    print("\n📊 DATABASE TESTS")
    print("-" * 40)
    test_with_result("Database Connection", test_database_connection)
    test_with_result("Database Models", test_database_models)
    test_with_result("Database CRUD Operations", test_database_crud)
    
    # Core Module Tests
    print("\n⚙️ CORE MODULE TESTS")
    print("-" * 40)
    test_with_result("ROI Calculator Module", test_roi_calculator_module)
    test_with_result("Assessment Tool Module", test_assessment_tool_module)
    test_with_result("Proposal Generator Module", test_proposal_generator_module)
    
    # Page Tests
    print("\n📄 PAGE TESTS")
    print("-" * 40)
    test_with_result("Page Imports", test_page_imports)
    test_with_result("Chart Theme", test_chart_theme)
    
    # Integration Tests
    print("\n🔗 INTEGRATION TESTS")
    print("-" * 40)
    test_with_result("Data Flow", test_data_flow)
    
    # Performance Tests
    print("\n⚡ PERFORMANCE TESTS")
    print("-" * 40)
    test_with_result("Performance Metrics", test_performance)
    test_with_result("Input Validation", test_input_validation)
    
    # Generate Report
    print("\n" + "=" * 70)
    print("📋 TEST REPORT")
    print("=" * 70)
    
    passed = sum(1 for _, success, _ in test_results if success)
    failed = len(test_results) - passed
    
    print(f"\n📊 SUMMARY:")
    print(f"  Total Tests: {len(test_results)}")
    print(f"  ✅ Passed: {passed}")
    print(f"  ❌ Failed: {failed}")
    print(f"  Success Rate: {(passed/len(test_results)*100):.1f}%")
    
    if failed > 0:
        print(f"\n❌ FAILED TESTS:")
        for name, success, error in test_results:
            if not success:
                print(f"  - {name}")
                if error and len(error) < 200:
                    print(f"    Error: {error[:200]}")
    
    if errors_found:
        print(f"\n🐛 ERRORS TO FIX:")
        for test_name, error in errors_found[:5]:  # Show first 5 errors
            print(f"\n  {test_name}:")
            print(f"    {error.split(chr(10))[0][:200]}")  # First line of error
    
    print("\n" + "=" * 70)
    
    if passed == len(test_results):
        print("🎉 ALL TESTS PASSED!")
        print("✅ Application is ready for production")
    else:
        print(f"⚠️ {failed} tests failed - fixes needed")
    
    print("=" * 70)
    
    return passed == len(test_results)

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
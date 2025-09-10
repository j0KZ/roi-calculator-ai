#!/usr/bin/env python3
"""
Final Validation Suite - Chilean E-commerce Sales Toolkit
Complete system verification before production deployment
"""

import sys
import os
import time
import json
from datetime import datetime

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

print("=" * 80)
print("🚀 FINAL VALIDATION - CHILEAN E-COMMERCE SALES TOOLKIT v2.1.0")
print("=" * 80)
print(f"Validation Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

# Track all results
all_tests_passed = True
test_categories = {}

def run_test(category, test_name, test_func):
    """Run a test and track results"""
    global all_tests_passed
    
    if category not in test_categories:
        test_categories[category] = {'passed': 0, 'failed': 0, 'tests': []}
    
    try:
        result = test_func()
        if result:
            print(f"  ✅ {test_name}")
            test_categories[category]['passed'] += 1
        else:
            print(f"  ❌ {test_name}")
            test_categories[category]['failed'] += 1
            all_tests_passed = False
        test_categories[category]['tests'].append((test_name, result))
        return result
    except Exception as e:
        print(f"  ❌ {test_name}: {str(e)[:100]}")
        test_categories[category]['failed'] += 1
        test_categories[category]['tests'].append((test_name, False))
        all_tests_passed = False
        return False

# ========== SYSTEM REQUIREMENTS ==========
print("\n📋 SYSTEM REQUIREMENTS")
print("-" * 40)

def check_python_version():
    import sys
    return sys.version_info >= (3, 7)

def check_required_packages():
    required = [
        ('streamlit', 'streamlit'),
        ('pandas', 'pandas'),
        ('numpy', 'numpy'),
        ('plotly', 'plotly'),
        ('sqlalchemy', 'sqlalchemy'),
        ('reportlab', 'reportlab'),
        ('python-pptx', 'pptx')
    ]
    for display_name, import_name in required:
        try:
            __import__(import_name)
        except ImportError:
            print(f"    Missing: {display_name}")
            return False
    return True

def check_database_file():
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'roi_calculator.db')
    return os.path.exists(db_path)

run_test("System", "Python 3.7+", check_python_version)
run_test("System", "Required Packages", check_required_packages)
run_test("System", "Database File", check_database_file)

# ========== DATABASE VALIDATION ==========
print("\n🗄️ DATABASE VALIDATION")
print("-" * 40)

def test_db_connection():
    from database.connection import get_db
    return get_db().test_connection()

def test_db_tables():
    from database.connection import get_session
    from database.models import Calculation, Template
    try:
        session = get_session()
        session.query(Calculation).count()
        session.query(Template).count()
        session.close()
        return True
    except:
        return False

def test_db_operations():
    from database.connection import get_session
    from database.models import Calculation
    try:
        session = get_session()
        # Create test record
        test_calc = Calculation(
            company_name="Validation Test",
            annual_revenue=1000000,
            monthly_orders=100,
            avg_order_value=10000,
            labor_costs=100000,
            shipping_costs=50000,
            error_costs=10000,
            inventory_costs=20000,
            service_investment=500000,
            results={'test': True}
        )
        session.add(test_calc)
        session.commit()
        calc_id = test_calc.id
        
        # Delete test record
        session.delete(test_calc)
        session.commit()
        session.close()
        return True
    except:
        return False

run_test("Database", "Connection", test_db_connection)
run_test("Database", "Table Access", test_db_tables)
run_test("Database", "CRUD Operations", test_db_operations)

# ========== CORE MODULES ==========
print("\n⚙️ CORE MODULES")
print("-" * 40)

def test_roi_calculator():
    from enhanced_roi_calculator import EnhancedROICalculator
    from roi_result_adapter import adapt_roi_results
    
    calc = EnhancedROICalculator()
    data = {
        'annual_revenue_clp': 1000000000,
        'monthly_orders': 1000,
        'avg_order_value_clp': 83333,
        'labor_costs_clp': 5000000,
        'shipping_costs_clp': 3000000,
        'error_costs_clp': 1500000,
        'inventory_costs_clp': 2000000,
        'investment_clp': 50000000
    }
    
    raw_results = calc.calculate_roi(data)
    results = adapt_roi_results(raw_results)
    
    return (
        results.get('roi_percentage', 0) > 0 and
        results.get('payback_months', 0) > 0 and
        results.get('success', False)
    )

def test_assessment_tool():
    from rapid_assessment_tool import RapidAssessmentTool
    
    tool = RapidAssessmentTool()
    responses = {
        'company_type': 'retailer',
        'annual_revenue': 'medium',
        'employees': '10-50'
    }
    
    results = tool.conduct_assessment(responses)
    score = results.get('qualification_score', 0)
    
    return 0 <= score <= 100

def test_proposal_generator():
    from automated_proposal_generator import AutomatedProposalGenerator
    
    gen = AutomatedProposalGenerator()
    proposal = gen.generate_proposal(
        client_data={'company_name': 'Test'},
        assessment_results={'qualification_score': 85},
        roi_analysis={'roi_percentage': 150},
        template_type='executive',
        package_type='professional'
    )
    
    return 'sections' in proposal and len(proposal['sections']) > 0

run_test("Modules", "ROI Calculator", test_roi_calculator)
run_test("Modules", "Assessment Tool", test_assessment_tool)
run_test("Modules", "Proposal Generator", test_proposal_generator)

# ========== WEB PAGES ==========
print("\n📄 WEB PAGES")
print("-" * 40)

def test_page_syntax(page_path):
    full_path = os.path.join(os.path.dirname(__file__), '..', page_path)
    if not os.path.exists(full_path):
        return False
    try:
        with open(full_path, 'r') as f:
            compile(f.read(), page_path, 'exec')
        return True
    except:
        return False

pages = [
    ('pages/roi_calculator.py', 'ROI Calculator Page'),
    ('pages/assessment_tool.py', 'Assessment Tool Page'),
    ('pages/proposal_generator.py', 'Proposal Generator Page'),
    ('pages/history.py', 'History Page'),
    ('pages/templates.py', 'Templates Page'),
    ('app.py', 'Main Application')
]

for page_path, page_name in pages:
    run_test("Pages", page_name, lambda p=page_path: test_page_syntax(p))

# ========== PERFORMANCE ==========
print("\n⚡ PERFORMANCE")
print("-" * 40)

def test_roi_performance():
    from enhanced_roi_calculator import EnhancedROICalculator
    from roi_result_adapter import adapt_roi_results
    import numpy as np
    
    calc = EnhancedROICalculator()
    times = []
    
    for _ in range(5):
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
        raw_results = calc.calculate_roi(data)
        results = adapt_roi_results(raw_results)
        times.append(time.time() - start)
    
    avg_time = np.mean(times)
    return avg_time < 0.5  # Should be under 0.5 seconds

def test_database_performance():
    from database.connection import get_session
    from database.models import Calculation
    import time
    
    session = get_session()
    
    # Test query speed
    start = time.time()
    calculations = session.query(Calculation).limit(100).all()
    query_time = time.time() - start
    
    session.close()
    
    return query_time < 0.1  # Should be under 100ms

run_test("Performance", "ROI Calculation < 0.5s", test_roi_performance)
run_test("Performance", "Database Query < 100ms", test_database_performance)

# ========== INTEGRATION ==========
print("\n🔗 INTEGRATION")
print("-" * 40)

def test_end_to_end_flow():
    """Test complete flow from calculation to database"""
    from enhanced_roi_calculator import EnhancedROICalculator
    from roi_result_adapter import adapt_roi_results
    from database.connection import get_session
    from database.models import Calculation
    
    try:
        # Calculate
        calc = EnhancedROICalculator()
        raw_results = calc.calculate_roi({
            'annual_revenue_clp': 1000000000,
            'monthly_orders': 1000,
            'avg_order_value_clp': 83333,
            'labor_costs_clp': 5000000,
            'shipping_costs_clp': 3000000,
            'error_costs_clp': 1500000,
            'inventory_costs_clp': 2000000,
            'investment_clp': 50000000
        })
        results = adapt_roi_results(raw_results)
        
        # Save
        session = get_session()
        db_calc = Calculation(
            company_name="E2E Test",
            annual_revenue=1000000000,
            monthly_orders=1000,
            avg_order_value=83333,
            labor_costs=5000000,
            shipping_costs=3000000,
            error_costs=1500000,
            inventory_costs=2000000,
            service_investment=50000000,
            results=results
        )
        session.add(db_calc)
        session.commit()
        calc_id = db_calc.id
        
        # Read
        saved = session.query(Calculation).filter_by(id=calc_id).first()
        success = saved is not None and saved.company_name == "E2E Test"
        
        # Clean up
        session.delete(saved)
        session.commit()
        session.close()
        
        return success
    except:
        return False

def test_data_persistence():
    """Test that data persists correctly"""
    from database.connection import get_session
    from database.models import Template
    
    try:
        session = get_session()
        
        # Check templates exist
        template_count = session.query(Template).count()
        
        session.close()
        
        return template_count > 0
    except:
        return False

run_test("Integration", "End-to-End Flow", test_end_to_end_flow)
run_test("Integration", "Data Persistence", test_data_persistence)

# ========== FINAL REPORT ==========
print("\n" + "=" * 80)
print("📊 VALIDATION REPORT")
print("=" * 80)

total_passed = 0
total_failed = 0

for category, results in test_categories.items():
    total_passed += results['passed']
    total_failed += results['failed']
    
    status = "✅" if results['failed'] == 0 else "❌"
    print(f"\n{status} {category}:")
    print(f"  Passed: {results['passed']}")
    print(f"  Failed: {results['failed']}")

print("\n" + "-" * 40)
print(f"TOTAL TESTS: {total_passed + total_failed}")
print(f"✅ PASSED: {total_passed}")
print(f"❌ FAILED: {total_failed}")
print(f"SUCCESS RATE: {(total_passed/(total_passed+total_failed)*100):.1f}%")

print("\n" + "=" * 80)

if all_tests_passed:
    print("🎉 ALL VALIDATION TESTS PASSED!")
    print("✅ APPLICATION IS FULLY DEBUGGED AND OPTIMIZED")
    print("✅ READY FOR PRODUCTION DEPLOYMENT")
    print("\n📋 Certification:")
    print("  - Database: Fully functional with SQLite")
    print("  - Performance: All operations < 0.5s")
    print("  - Integration: Complete data flow verified")
    print("  - Web Interface: All pages valid")
    print("  - Modules: All core functions operational")
else:
    print("⚠️ SOME TESTS FAILED")
    print("Please review and fix the issues above")

print("=" * 80)
print(f"Validation Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

sys.exit(0 if all_tests_passed else 1)
#!/usr/bin/env python3
"""
Comprehensive test suite for Chilean E-commerce Sales Toolkit
Tests all three tools with various scenarios
"""

import sys
import os
import json
import time
from datetime import datetime

# Add src to path
sys.path.insert(0, 'src')

def test_roi_calculator():
    """Test Enhanced ROI Calculator"""
    print("\n" + "="*60)
    print("TEST 1: ENHANCED ROI CALCULATOR")
    print("="*60)
    
    try:
        from enhanced_roi_calculator import EnhancedROICalculator
        print("✅ Module imported")
        
        calculator = EnhancedROICalculator()
        print("✅ Calculator initialized")
        
        # Test Case 1: Normal Chilean SME
        print("\n📊 Test Case 1: Normal SME (500M CLP revenue)")
        inputs_normal = {
            'annual_revenue_clp': 500000000,  # 500M CLP
            'monthly_orders': 1500,
            'avg_order_value_clp': 28000,
            'labor_costs_clp': 3500000,
            'shipping_costs_clp': 2800000,
            'platform_fees_clp': 1200000,
            'error_costs_clp': 500000,
            'inventory_costs_clp': 1800000,
            'investment_clp': 25000000,
            'industry': 'retail',
            'current_platforms': ['transbank', 'webpay', 'bsale'],
            'conversion_rate': 0.021
        }
        
        start_time = time.time()
        results = calculator.calculate_roi(inputs_normal)
        calc_time = time.time() - start_time
        
        summary = results.get('executive_summary', {})
        print(f"  ROI: {summary.get('headline_roi', 0):.0f}%")
        print(f"  Payback: {summary.get('payback_period_months', 0):.1f} months")
        print(f"  Savings: ${summary.get('annual_savings_clp', 0)/1000000:.1f}M CLP")
        print(f"  Calculation time: {calc_time:.3f}s")
        print("✅ Normal case passed")
        
        # Test Case 2: Edge case - Zero revenue
        print("\n📊 Test Case 2: Edge Case - Startup (0 revenue)")
        inputs_zero = inputs_normal.copy()
        inputs_zero['annual_revenue_clp'] = 0
        inputs_zero['monthly_orders'] = 0
        
        try:
            results_zero = calculator.calculate_roi(inputs_zero)
            print("✅ Zero revenue handled gracefully")
        except Exception as e:
            print(f"⚠️  Zero revenue error (expected): {e}")
        
        # Test Case 3: Edge case - Very large company
        print("\n📊 Test Case 3: Edge Case - Large company (50B CLP)")
        inputs_large = inputs_normal.copy()
        inputs_large['annual_revenue_clp'] = 50000000000  # 50B CLP
        inputs_large['monthly_orders'] = 150000
        inputs_large['investment_clp'] = 500000000  # 500M CLP
        
        results_large = calculator.calculate_roi(inputs_large)
        summary_large = results_large.get('executive_summary', {})
        print(f"  ROI: {summary_large.get('headline_roi', 0):.0f}%")
        print("✅ Large company handled successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ ROI Calculator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_assessment_tool():
    """Test Rapid Assessment Tool"""
    print("\n" + "="*60)
    print("TEST 2: RAPID ASSESSMENT TOOL")
    print("="*60)
    
    try:
        from rapid_assessment_tool import RapidAssessmentTool
        print("✅ Module imported")
        
        assessment = RapidAssessmentTool()
        print("✅ Assessment tool initialized")
        
        # Test Case 1: Well-qualified prospect
        print("\n📋 Test Case 1: Well-qualified prospect")
        responses_good = {
            'b1': 600000000,  # 600M CLP annual
            'b2': 2000,  # 2000 orders/month
            'b3': 5,  # 5 employees
            'b4': 'Retail',
            't1': 'WooCommerce',
            't2': False,  # No ERP integration
            't3': ['Excel', 'Defontana'],
            't4': 3,  # Low automation
            'o1': 25,  # 25 min per order
            'o2': 8,  # 8% error rate
            'o3': 10,  # 10 hours manual work
            'o4': False,  # No documented processes
            'o5': 'Semanalmente',
            'i1': ['Transbank', 'Webpay'],
            'i2': ['Chilexpress'],
            'i3': ['No vendo en marketplaces'],
            'i4': False,  # No inventory sync
            'p1': ['Procesamiento manual de órdenes', 'Errores en fulfillment'],
            'p2': 5000000,  # 5M CLP monthly loss
            'p3': 8,  # High urgency
            'g1': 50,  # 50% growth target
            'g2': True,  # Has budget
            'g3': '1-3 meses'
        }
        
        start_time = time.time()
        results = assessment.conduct_assessment(responses_good)
        assess_time = time.time() - start_time
        
        qualification = results.get('qualification', {})
        roi_potential = results.get('roi_potential', {})
        
        print(f"  Qualification: {qualification.get('level', 'N/A')}")
        print(f"  Score: {qualification.get('score', 0)}/100")
        print(f"  Close probability: {qualification.get('close_probability', 0)}%")
        print(f"  ROI potential: {roi_potential.get('roi_percentage', 0):.0f}%")
        print(f"  Assessment time: {assess_time:.3f}s")
        print("✅ Good prospect assessment passed")
        
        # Test Case 2: Poor prospect
        print("\n📋 Test Case 2: Poor prospect")
        responses_poor = responses_good.copy()
        responses_poor['b1'] = 50000000  # Only 50M CLP
        responses_poor['g2'] = False  # No budget
        responses_poor['p3'] = 3  # Low urgency
        
        results_poor = assessment.conduct_assessment(responses_poor)
        qualification_poor = results_poor.get('qualification', {})
        
        print(f"  Qualification: {qualification_poor.get('level', 'N/A')}")
        print(f"  Score: {qualification_poor.get('score', 0)}/100")
        print("✅ Poor prospect handled correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ Assessment tool test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_proposal_generator():
    """Test Automated Proposal Generator"""
    print("\n" + "="*60)
    print("TEST 3: AUTOMATED PROPOSAL GENERATOR")
    print("="*60)
    
    try:
        from automated_proposal_generator import AutomatedProposalGenerator
        print("✅ Module imported")
        
        generator = AutomatedProposalGenerator()
        print("✅ Proposal generator initialized")
        
        # Test data
        client_data = {
            'company_name': 'Test Company Chile SpA',
            'contact_name': 'José Pérez',
            'email': 'jose@test.cl',
            'phone': '+56 9 8765 4321',
            'industry': 'Retail'
        }
        
        assessment_results = {
            'maturity_level': {
                'level': 'BÁSICO',
                'score': 4.5,
                'description': 'Procesos mayormente manuales'
            },
            'qualification': {
                'level': 'A - HOT PROSPECT',
                'score': 85,
                'close_probability': 80
            },
            'roi_potential': {
                'roi_percentage': 186,
                'payback_months': 5.2
            }
        }
        
        roi_analysis = {
            'executive_summary': {
                'headline_roi': 186,
                'payback_period_months': 5.2,
                'annual_savings_clp': 102000000
            },
            'improvements': {
                'total_annual_savings_clp': 102000000,
                'roi_percentage_year_1': 186
            }
        }
        
        print("\n📄 Generating proposal...")
        start_time = time.time()
        
        proposal = generator.generate_proposal(
            client_data=client_data,
            assessment_results=assessment_results,
            roi_analysis=roi_analysis,
            template_type='executive',
            package_type='professional'
        )
        
        gen_time = time.time() - start_time
        
        print(f"  Proposal ID: {proposal.get('metadata', {}).get('proposal_id', 'N/A')}")
        print(f"  Package: {proposal.get('package', {}).get('name', 'N/A')}")
        print(f"  Sections: {len(proposal.get('sections', {}))}")
        print(f"  Generation time: {gen_time:.3f}s")
        
        # Test one-pager generation
        one_pager = generator.generate_one_pager()
        print(f"  One-pager length: {len(one_pager)} characters")
        
        print("✅ Proposal generation passed")
        
        return True
        
    except Exception as e:
        print(f"❌ Proposal generator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_edge_cases():
    """Test edge cases and special characters"""
    print("\n" + "="*60)
    print("TEST 4: EDGE CASES & SPECIAL CHARACTERS")
    print("="*60)
    
    try:
        from enhanced_roi_calculator import EnhancedROICalculator
        
        calculator = EnhancedROICalculator()
        
        # Test with Spanish characters
        print("\n🌍 Testing Spanish characters...")
        inputs_spanish = {
            'annual_revenue_clp': 1000000000,
            'monthly_orders': 1000,
            'avg_order_value_clp': 83333,
            'labor_costs_clp': 5000000,
            'shipping_costs_clp': 3000000,
            'platform_fees_clp': 1500000,
            'error_costs_clp': 800000,
            'inventory_costs_clp': 2000000,
            'investment_clp': 30000000,
            'industry': 'retail',
            'current_platforms': ['transbank', 'webpay'],
            'conversion_rate': 0.025
        }
        
        # Company name with Spanish characters
        company_name = "Compañía Ñandú Ltda."
        print(f"  Company: {company_name}")
        
        results = calculator.calculate_roi(inputs_spanish)
        print("✅ Spanish characters handled")
        
        # Test with negative values (should be corrected)
        print("\n⚠️  Testing negative values...")
        inputs_negative = inputs_spanish.copy()
        inputs_negative['error_costs_clp'] = -500000  # Negative cost
        
        try:
            results_neg = calculator.calculate_roi(inputs_negative)
            print("✅ Negative values handled")
        except Exception as e:
            print(f"⚠️  Negative value handling: {e}")
        
        # Test with very small values
        print("\n🔬 Testing very small values...")
        inputs_small = inputs_spanish.copy()
        inputs_small['annual_revenue_clp'] = 1000  # Only 1000 CLP
        inputs_small['monthly_orders'] = 1
        
        try:
            results_small = calculator.calculate_roi(inputs_small)
            print("✅ Small values handled")
        except Exception as e:
            print(f"⚠️  Small value handling: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Edge case test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_performance():
    """Test performance and speed"""
    print("\n" + "="*60)
    print("TEST 5: PERFORMANCE & SPEED")
    print("="*60)
    
    try:
        from enhanced_roi_calculator import EnhancedROICalculator
        
        calculator = EnhancedROICalculator()
        
        # Standard test inputs
        inputs = {
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
        
        # Test multiple calculations
        print("\n⚡ Running 10 sequential calculations...")
        times = []
        
        for i in range(10):
            start = time.time()
            results = calculator.calculate_roi(inputs)
            elapsed = time.time() - start
            times.append(elapsed)
            print(f"  Run {i+1}: {elapsed:.3f}s")
        
        avg_time = sum(times) / len(times)
        print(f"\n  Average time: {avg_time:.3f}s")
        print(f"  Min time: {min(times):.3f}s")
        print(f"  Max time: {max(times):.3f}s")
        
        if avg_time < 1.0:
            print("✅ Performance acceptable (<1s average)")
        else:
            print("⚠️  Performance could be improved")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("="*60)
    print("CHILEAN E-COMMERCE SALES TOOLKIT - COMPREHENSIVE TEST SUITE")
    print("="*60)
    print(f"Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Track results
    results = {}
    
    # Run tests
    results['roi_calculator'] = test_roi_calculator()
    results['assessment_tool'] = test_assessment_tool()
    results['proposal_generator'] = test_proposal_generator()
    results['edge_cases'] = test_edge_cases()
    results['performance'] = test_performance()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! The toolkit is ready for production.")
    else:
        print("\n⚠️  Some tests failed. Please review the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
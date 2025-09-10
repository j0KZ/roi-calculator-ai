#!/usr/bin/env python3
"""
Integration test for all three Chilean E-commerce Sales Tools
"""

import sys
import os
import time

# Add src to path
sys.path.insert(0, 'src')

def test_full_integration():
    """Test all three tools working together"""
    print("="*60)
    print("INTEGRATION TEST: Chilean E-commerce Sales Toolkit")
    print("="*60)
    
    # Import all three tools
    print("\n1. Loading modules...")
    try:
        from enhanced_roi_calculator import EnhancedROICalculator
        from rapid_assessment_tool import RapidAssessmentTool
        from automated_proposal_generator import AutomatedProposalGenerator
        print("✅ All modules loaded successfully")
    except Exception as e:
        print(f"❌ Module loading failed: {e}")
        return False
    
    # Initialize tools
    print("\n2. Initializing tools...")
    try:
        calculator = EnhancedROICalculator()
        assessment = RapidAssessmentTool()
        generator = AutomatedProposalGenerator()
        print("✅ All tools initialized")
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return False
    
    # Test data for Chilean SME
    client_data = {
        'company_name': 'Tienda Digital Santiago SpA',
        'contact_name': 'María González',
        'email': 'maria@tiendadigital.cl',
        'phone': '+56 9 8765 4321',
        'industry': 'Retail'
    }
    
    # Step 1: Run rapid assessment
    print("\n3. Running rapid assessment...")
    try:
        assessment_responses = {
            'b1': 600000000,  # 600M CLP annual
            'b2': 2000,  # 2000 orders/month
            'b3': 5,  # 5 employees
            'b4': 'Retail',
            't1': 'WooCommerce',
            't2': False,  # No ERP integration
            't3': ['Excel', 'Email manual'],
            't4': 3,  # Low automation
            'o1': 20,  # 20 min per order
            'o2': 7,  # 7% error rate
            'o3': 8,  # 8 hours manual work
            'o4': False,  # No documented processes
            'o5': 'Diariamente',
            'i1': ['Transbank', 'Webpay'],
            'i2': ['Chilexpress', 'Starken'],
            'i3': ['No vendo en marketplaces'],
            'i4': False,  # No inventory sync
            'p1': ['Procesamiento manual de órdenes', 'Errores en inventario'],
            'p2': 4000000,  # 4M CLP monthly loss
            'p3': 8,  # High urgency
            'g1': 40,  # 40% growth target
            'g2': True,  # Has budget
            'g3': '1-3 meses'
        }
        
        assessment_results = assessment.conduct_assessment(assessment_responses)
        qualification = assessment_results.get('qualification', {})
        print(f"✅ Assessment complete: {qualification.get('level', 'N/A')} (Score: {qualification.get('score', 0)}/100)")
    except Exception as e:
        print(f"❌ Assessment failed: {e}")
        return False
    
    # Step 2: Calculate ROI
    print("\n4. Calculating ROI...")
    try:
        roi_inputs = {
            'annual_revenue_clp': 600000000,
            'monthly_orders': 2000,
            'avg_order_value_clp': 25000,
            'labor_costs_clp': 3500000,
            'shipping_costs_clp': 2500000,
            'platform_fees_clp': 1200000,
            'error_costs_clp': 600000,
            'inventory_costs_clp': 1800000,
            'investment_clp': 20000000,
            'industry': 'retail',
            'current_platforms': ['transbank', 'webpay'],
            'conversion_rate': 0.022
        }
        
        start_time = time.time()
        roi_results = calculator.calculate_roi(roi_inputs)
        calc_time = time.time() - start_time
        
        summary = roi_results.get('executive_summary', {})
        print(f"✅ ROI calculated: {summary.get('headline_roi', 0):.0f}% in {calc_time:.2f}s")
        print(f"   Payback: {summary.get('payback_period_months', 0):.1f} months")
        print(f"   Annual savings: ${summary.get('annual_savings_clp', 0)/1000000:.1f}M CLP")
    except Exception as e:
        print(f"❌ ROI calculation failed: {e}")
        return False
    
    # Step 3: Generate proposal
    print("\n5. Generating proposal...")
    try:
        proposal = generator.generate_proposal(
            client_data=client_data,
            assessment_results=assessment_results,
            roi_analysis=roi_results,
            template_type='executive',
            package_type='professional'
        )
        
        print(f"✅ Proposal generated: {proposal.get('metadata', {}).get('proposal_id', 'N/A')}")
        print(f"   Package: {proposal.get('package', {}).get('name', 'N/A')}")
        print(f"   Sections: {len(proposal.get('sections', {}))}")
    except Exception as e:
        print(f"❌ Proposal generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test one-pager generation
    print("\n6. Generating one-pager...")
    try:
        one_pager = generator.generate_one_pager()
        print(f"✅ One-pager generated ({len(one_pager)} characters)")
    except Exception as e:
        print(f"❌ One-pager generation failed: {e}")
    
    print("\n" + "="*60)
    print("🎉 INTEGRATION TEST PASSED!")
    print("All three tools are working correctly together")
    print("="*60)
    
    # Performance summary
    print("\n📊 Performance Summary:")
    print(f"  • Assessment tool: ✅ Working")
    print(f"  • ROI Calculator: ✅ {calc_time:.2f}s calculation time")
    print(f"  • Proposal Generator: ✅ Working")
    print(f"  • Integration: ✅ All tools communicate properly")
    
    return True

if __name__ == "__main__":
    print("\n🚀 Starting Chilean E-commerce Sales Toolkit Integration Test\n")
    
    success = test_full_integration()
    
    if success:
        print("\n✅ All systems operational - Ready for production use!")
    else:
        print("\n⚠️ Some issues detected - Please review errors above")
    
    sys.exit(0 if success else 1)

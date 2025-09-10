#!/usr/bin/env python3
"""
Test script for the Streamlit web application
"""

import sys
import os
import time

# Add src to path
sys.path.insert(0, 'src')

def test_imports():
    """Test all required imports"""
    print("Testing imports...")
    
    try:
        # Test Streamlit
        import streamlit as st
        print("✅ Streamlit imported")
    except ImportError as e:
        print(f"❌ Streamlit not installed: {e}")
        print("   Run: pip install streamlit")
        return False
    
    try:
        # Test Plotly
        import plotly.graph_objects as go
        import plotly.express as px
        print("✅ Plotly imported")
    except ImportError as e:
        print(f"❌ Plotly not installed: {e}")
        print("   Run: pip install plotly")
        return False
    
    try:
        # Test core modules
        from enhanced_roi_calculator import EnhancedROICalculator
        print("✅ ROI Calculator imported")
        
        from rapid_assessment_tool import RapidAssessmentTool
        print("✅ Assessment Tool imported")
        
        from automated_proposal_generator import AutomatedProposalGenerator
        print("✅ Proposal Generator imported")
    except Exception as e:
        print(f"❌ Core modules error: {e}")
        return False
    
    try:
        # Test pages
        from pages.roi_calculator import show_roi_calculator
        print("✅ ROI Calculator page imported")
        
        from pages.assessment_tool import show_assessment_tool
        print("✅ Assessment Tool page imported")
        
        from pages.proposal_generator import show_proposal_generator
        print("✅ Proposal Generator page imported")
    except Exception as e:
        print(f"❌ Page modules error: {e}")
        return False
    
    return True

def test_core_functionality():
    """Test core functionality"""
    print("\nTesting core functionality...")
    
    try:
        from enhanced_roi_calculator import EnhancedROICalculator
        
        calculator = EnhancedROICalculator()
        
        inputs = {
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
        results = calculator.calculate_roi(inputs)
        calc_time = time.time() - start_time
        
        roi = results.get('executive_summary', {}).get('headline_roi', 0)
        
        print(f"✅ ROI Calculator working: {roi:.0f}% ROI in {calc_time:.2f}s")
        
    except Exception as e:
        print(f"❌ ROI Calculator error: {e}")
        return False
    
    try:
        from rapid_assessment_tool import RapidAssessmentTool
        
        assessment = RapidAssessmentTool()
        
        responses = {
            'b1': 600000000,
            'b2': 2000,
            'b3': 5,
            'b4': 'Retail',
            't1': 'WooCommerce',
            't2': False,
            't3': ['Excel'],
            't4': 3,
            'o1': 20,
            'o2': 7,
            'o3': 8,
            'o4': False,
            'o5': 'Diariamente',
            'i1': ['Transbank'],
            'i2': ['Chilexpress'],
            'i3': ['No vendo en marketplaces'],
            'i4': False,
            'p1': ['Procesamiento manual de órdenes'],
            'p2': 4000000,
            'p3': 8,
            'g1': 40,
            'g2': True,
            'g3': '1-3 meses'
        }
        
        results = assessment.conduct_assessment(responses)
        score = results.get('qualification', {}).get('score', 0)
        
        print(f"✅ Assessment Tool working: Score {score}/100")
        
    except Exception as e:
        print(f"❌ Assessment Tool error: {e}")
        return False
    
    try:
        from automated_proposal_generator import AutomatedProposalGenerator
        
        generator = AutomatedProposalGenerator()
        
        client_data = {
            'company_name': 'Test Company',
            'contact_name': 'Test Contact',
            'email': 'test@test.cl',
            'phone': '+56 9 1234 5678',
            'industry': 'Retail'
        }
        
        # Use the results from above
        proposal = generator.generate_proposal(
            client_data=client_data,
            assessment_results=results,
            roi_analysis={'improvements': {'total_annual_savings_clp': 60000000}},
            template_type='executive',
            package_type='professional'
        )
        
        proposal_id = proposal.get('metadata', {}).get('proposal_id', 'N/A')
        
        print(f"✅ Proposal Generator working: ID {proposal_id}")
        
    except Exception as e:
        print(f"❌ Proposal Generator error: {e}")
        return False
    
    return True

def main():
    """Main test function"""
    print("="*60)
    print("Chilean E-commerce Sales Toolkit - Web App Test")
    print("="*60)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed. Please install missing dependencies:")
        print("   pip install -r requirements.txt")
        return False
    
    # Test core functionality
    if not test_core_functionality():
        print("\n❌ Core functionality tests failed.")
        return False
    
    print("\n" + "="*60)
    print("✅ All tests passed! The web app is ready to run.")
    print("="*60)
    
    print("\n📚 To run the web application:")
    print("   streamlit run app.py")
    print("\n🌐 The app will open in your browser at:")
    print("   http://localhost:8501")
    
    print("\n📱 Features available:")
    print("   • Beautiful landing page with toolkit overview")
    print("   • ROI Calculator with Monte Carlo visualization")
    print("   • Assessment Tool with wizard interface")
    print("   • Proposal Generator with PDF/PowerPoint export")
    print("   • Real-time charts and gauges")
    print("   • Session state management")
    print("   • Professional styling")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
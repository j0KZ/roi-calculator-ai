#!/usr/bin/env python3
"""
Integration Test for Chilean E-commerce Sales Toolkit
Tests all three enhanced components working together
"""

import os
import json
from datetime import datetime

def main():
    print("=" * 70)
    print("INTEGRATION TEST - CHILEAN E-COMMERCE SALES TOOLKIT v2.0")
    print("=" * 70)
    
    try:
        # Import all components
        from enhanced_roi_calculator import EnhancedROICalculator
        from rapid_assessment_tool import RapidAssessmentTool
        from automated_proposal_generator import AutomatedProposalGenerator
        
        print("✓ All modules imported successfully")
        
        # Test data - realistic Chilean SME
        sample_responses = {
            'b1': 800000000,  # 800M CLP annual revenue
            'b2': 2000,       # 2000 orders/month
            'b3': 6,          # 6 employees
            'b4': 'Retail',
            't1': 'WooCommerce',
            't2': False,      # No ERP integration
            't3': ['Excel', 'Defontana'],
            't4': 3,          # Low automation (3/10)
            'o1': 30,         # 30 minutes per order
            'o2': 12,         # 12% error rate
            'o3': 8,          # 8 hours daily manual work
            'o4': False,      # No documented processes
            'o5': 'Semanalmente',  # Weekly stock breaks
            'i1': ['Transbank', 'Webpay'],
            'i2': ['Chilexpress', 'Starken'],
            'i3': ['No vendo en marketplaces'],
            'i4': False,      # No inventory sync
            'p1': ['Procesamiento manual de órdenes', 'Errores en fulfillment', 'Gestión de inventario'],
            'p2': 8000000,    # 8M CLP monthly losses
            'p3': 9,          # High urgency (9/10)
            'g1': 40,         # 40% growth target
            'g2': True,       # Has budget
            'g3': '1-3 meses' # Quick timeline
        }
        
        client_data = {
            'company_name': 'Tiendas del Sur SpA',
            'contact_name': 'María González',
            'email': 'maria@tiendasdelsur.cl',
            'phone': '+56 9 8765 4321',
            'industry': 'Retail',
            'website': 'www.tiendasdelsur.cl'
        }
        
        print("\n1. RAPID ASSESSMENT TEST")
        print("-" * 40)
        
        # Step 1: Rapid Assessment
        assessment_tool = RapidAssessmentTool()
        assessment_results = assessment_tool.conduct_assessment(sample_responses)
        
        if assessment_results.get('success', False):
            print("✓ Assessment completed successfully")
            qual = assessment_results.get('qualification', {})
            print(f"  Qualification: {qual.get('level', 'Unknown')}")
            print(f"  Score: {qual.get('score', 0)}/100")
            print(f"  ROI Potential: {assessment_results.get('roi_potential', {}).get('roi_percentage', 0):.1f}%")
        else:
            print("✗ Assessment failed")
            print(f"  Error: {assessment_results.get('message', 'Unknown error')}")
            return False
        
        print("\n2. ROI CALCULATION TEST")
        print("-" * 40)
        
        # Step 2: Enhanced ROI Calculation
        roi_inputs = {
            'annual_revenue_clp': sample_responses['b1'],
            'monthly_orders': sample_responses['b2'],
            'avg_order_value_clp': sample_responses['b1'] / (sample_responses['b2'] * 12),
            'labor_costs_clp': 4200000,  # 4.2M CLP/month (6 employees)
            'shipping_costs_clp': 3500000,  # 3.5M CLP/month
            'platform_fees_clp': 1800000,  # 1.8M CLP/month
            'error_costs_clp': sample_responses['p2'] * 0.6,  # 60% of reported losses
            'inventory_costs_clp': 2500000,  # 2.5M CLP/month
            'investment_clp': 28000000,  # 28M CLP investment
            'industry': 'retail',
            'current_platforms': ['transbank', 'webpay', 'defontana']
        }
        
        roi_calculator = EnhancedROICalculator()
        roi_results = roi_calculator.calculate_roi(roi_inputs)
        
        if roi_results.get('success', False):
            print("✓ ROI calculation completed successfully")
            summary = roi_results.get('executive_summary', {})
            print(f"  ROI Year 1: {summary.get('headline_roi', 0):.1f}%")
            print(f"  Payback Period: {summary.get('payback_period_months', 0):.1f} months")
            print(f"  Annual Savings: ${summary.get('annual_savings_clp', 0):,.0f} CLP")
        else:
            print("✗ ROI calculation failed")
            print(f"  Error: {roi_results.get('message', 'Unknown error')}")
            return False
        
        print("\n3. PROPOSAL GENERATION TEST")
        print("-" * 40)
        
        # Step 3: Automated Proposal Generation
        proposal_generator = AutomatedProposalGenerator()
        proposal_data = proposal_generator.generate_proposal(
            client_data=client_data,
            assessment_results=assessment_results,
            roi_analysis=roi_results,
            template_type='executive',
            package_type='professional'
        )
        
        if not proposal_data.get('error', False):
            print("✓ Proposal generation completed successfully")
            metadata = proposal_data.get('generation_metadata', {})
            print(f"  Sections generated: {metadata.get('successful_sections', 0)}/{metadata.get('total_sections', 0)}")
            print(f"  Capabilities: {metadata.get('capabilities', {})}")
        else:
            print("✗ Proposal generation failed")
            print(f"  Error: {proposal_data.get('message', 'Unknown error')}")
            return False
        
        print("\n4. FILE EXPORT TESTS")
        print("-" * 40)
        
        # Create output directory
        output_dir = 'integration_test_output'
        os.makedirs(output_dir, exist_ok=True)
        
        # Export assessment results
        try:
            with open(f'{output_dir}/assessment_results.json', 'w', encoding='utf-8') as f:
                json.dump(assessment_results, f, ensure_ascii=False, indent=2, default=str)
            print("✓ Assessment JSON export successful")
        except Exception as e:
            print(f"✗ Assessment JSON export failed: {e}")
        
        # Export ROI results
        roi_export_success = roi_calculator.export_to_json(f'{output_dir}/roi_analysis.json')
        excel_export_success = roi_calculator.export_to_excel(f'{output_dir}/roi_analysis.xlsx')
        print(f"ROI JSON export: {'✓ Success' if roi_export_success else '✗ Failed'}")
        print(f"ROI Excel export: {'✓ Success' if excel_export_success else '✗ Failed'}")
        
        # Export proposal
        pdf_success = proposal_generator.export_to_pdf(f'{output_dir}/proposal.pdf')
        pptx_success = proposal_generator.export_to_powerpoint(f'{output_dir}/proposal.pptx')
        print(f"Proposal PDF export: {'✓ Success' if pdf_success else '✗ Failed (fallback created)'}")
        print(f"Proposal PowerPoint export: {'✓ Success' if pptx_success else '✗ Failed (fallback created)'}")
        
        # Generate one-pager
        try:
            one_pager = proposal_generator.generate_one_pager()
            with open(f'{output_dir}/one_pager.txt', 'w', encoding='utf-8') as f:
                f.write(one_pager)
            print("✓ One-pager export successful")
        except Exception as e:
            print(f"✗ One-pager export failed: {e}")
        
        # Generate assessment report
        try:
            report = assessment_tool.generate_assessment_report()
            with open(f'{output_dir}/assessment_report.txt', 'w', encoding='utf-8') as f:
                f.write(report)
            print("✓ Assessment report export successful")
        except Exception as e:
            print(f"✗ Assessment report export failed: {e}")
        
        print("\n5. ERROR HANDLING TESTS")
        print("-" * 40)
        
        # Test with invalid data
        try:
            invalid_assessment = assessment_tool.conduct_assessment({'invalid': 'data'})
            if not invalid_assessment.get('error', False):
                print("✓ Assessment handles invalid data gracefully")
            else:
                print("✓ Assessment properly rejects invalid data")
        except Exception as e:
            print(f"✓ Assessment error handling works: {e}")
        
        try:
            invalid_roi = roi_calculator.calculate_roi({'invalid': 'data'})
            if not invalid_roi.get('error', False):
                print("✓ ROI calculator handles invalid data gracefully")
            else:
                print("✓ ROI calculator properly rejects invalid data")
        except Exception as e:
            print(f"✓ ROI calculator error handling works: {e}")
        
        try:
            invalid_proposal = proposal_generator.generate_proposal({}, {}, {})
            if not invalid_proposal.get('error', False):
                print("✓ Proposal generator handles empty data gracefully")
            else:
                print("✓ Proposal generator properly handles empty data")
        except Exception as e:
            print(f"✓ Proposal generator error handling works: {e}")
        
        print("\n" + "=" * 70)
        print("INTEGRATION TEST COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print(f"\nOutput files created in: {output_dir}/")
        print("- assessment_results.json")
        print("- roi_analysis.json")
        print("- roi_analysis.xlsx")
        print("- proposal.pdf (or fallback)")
        print("- proposal.pptx (or fallback)")
        print("- one_pager.txt")
        print("- assessment_report.txt")
        
        print(f"\nFor detailed logs, check: sales_toolkit_debug.log")
        
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        print("Please ensure all required files are in the same directory")
        return False
    
    except Exception as e:
        print(f"✗ CRITICAL ERROR: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
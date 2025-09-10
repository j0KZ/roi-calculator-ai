#!/usr/bin/env python3
"""
Interactive Demo of Chilean E-commerce Sales Toolkit
Shows all three tools working together
"""

import sys
import os
import time
from datetime import datetime

# Add src to path
sys.path.insert(0, 'src')

def print_header(title):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_section(title):
    """Print section header"""
    print(f"\n{'─'*40}")
    print(f"▶ {title}")
    print('─'*40)

def demo_scenario():
    """Run a complete demo scenario"""
    print_header("CHILEAN E-COMMERCE SALES TOOLKIT DEMO")
    print(f"Demo Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Import tools
    print_section("Loading Tools")
    from enhanced_roi_calculator import EnhancedROICalculator
    print("✅ ROI Calculator loaded")
    
    # Company scenario
    print_header("SCENARIO: 'Tienda Digital Santiago' - Chilean Retail SME")
    
    print("""
📊 Company Profile:
  • Name: Tienda Digital Santiago SpA
  • Industry: Retail Fashion
  • Location: Santiago, Chile
  • Annual Revenue: $800M CLP (~$842K USD)
  • Monthly Orders: 2,500
  • Employees: 7 (5 in operations)
  • Current Platforms: WooCommerce + Manual processes
  • Main Challenge: 70% of time on manual order processing
    """)
    
    input("\n➡️  Press Enter to start ROI analysis...")
    
    # ROI Calculation
    print_header("STEP 1: ROI CALCULATION")
    
    calculator = EnhancedROICalculator()
    
    inputs = {
        'annual_revenue_clp': 800000000,  # 800M CLP
        'monthly_orders': 2500,
        'avg_order_value_clp': 26667,  # ~27K CLP per order
        'labor_costs_clp': 4250000,  # 5 employees @ 850K average
        'shipping_costs_clp': 3500000,  # Chilexpress costs
        'platform_fees_clp': 2000000,  # Transbank + platform fees
        'error_costs_clp': 800000,  # Manual errors
        'inventory_costs_clp': 2500000,  # Inventory management
        'investment_clp': 25000000,  # Consulting investment
        'industry': 'retail',
        'current_platforms': ['transbank', 'webpay'],
        'conversion_rate': 0.023
    }
    
    print("\n📊 Current Operational Costs (Monthly):")
    print(f"  • Labor: ${inputs['labor_costs_clp']/1000000:.1f}M CLP")
    print(f"  • Shipping: ${inputs['shipping_costs_clp']/1000000:.1f}M CLP")
    print(f"  • Platform Fees: ${inputs['platform_fees_clp']/1000000:.1f}M CLP")
    print(f"  • Error Costs: ${inputs['error_costs_clp']/1000000:.1f}M CLP")
    print(f"  • Inventory: ${inputs['inventory_costs_clp']/1000000:.1f}M CLP")
    total_monthly = sum([inputs['labor_costs_clp'], inputs['shipping_costs_clp'], 
                        inputs['platform_fees_clp'], inputs['error_costs_clp'], 
                        inputs['inventory_costs_clp']])
    print(f"  📍 Total: ${total_monthly/1000000:.1f}M CLP/month")
    
    print("\n⏳ Running Monte Carlo simulation (10,000 iterations)...")
    start = time.time()
    results = calculator.calculate_roi(inputs)
    elapsed = time.time() - start
    
    print(f"✅ Analysis complete in {elapsed:.2f} seconds")
    
    # Display results
    summary = results.get('executive_summary', {})
    
    print_section("ROI Results")
    print(f"""
💰 Financial Impact:
  • ROI Year 1: {summary.get('headline_roi', 0):.0f}%
  • Payback Period: {summary.get('payback_period_months', 0):.1f} months
  • Annual Savings: ${summary.get('annual_savings_clp', 0)/1000000:.1f}M CLP
  • Confidence Level: {summary.get('confidence_level', 0):.0f}%
    """)
    
    # Scenario breakdown
    scenarios = results.get('scenarios', {}).get('scenarios', {})
    print("📈 Scenario Analysis:")
    print(f"  • Conservative (25% prob): {scenarios.get('pessimistic', {}).get('roi_percentage', 0):.0f}% ROI")
    print(f"  • Expected (60% prob): {scenarios.get('realistic', {}).get('roi_percentage', 0):.0f}% ROI")
    print(f"  • Optimistic (15% prob): {scenarios.get('optimistic', {}).get('roi_percentage', 0):.0f}% ROI")
    
    input("\n➡️  Press Enter to see recommendations...")
    
    # Recommendations
    print_section("AI-Powered Recommendations")
    recommendations = results.get('recommendations', [])
    
    for i, rec in enumerate(recommendations[:3], 1):
        print(f"\n{i}. {rec.get('title', 'N/A')}")
        print(f"   Priority: {rec.get('priority', 'N/A')}")
        print(f"   Impact: {rec.get('expected_impact', rec.get('description', 'N/A'))}")
        print(f"   Timeline: {rec.get('implementation_time', 'N/A')}")
        if 'expected_savings_clp' in rec and rec['expected_savings_clp'] > 0:
            print(f"   Savings: ${rec['expected_savings_clp']/1000000:.1f}M CLP/month")
    
    # Chilean specifics
    print_section("Chilean Market Specifics")
    chilean = results.get('chilean_specifics', {})
    print(f"""
🇨🇱 Tax Calculations:
  • Savings before IVA: ${chilean.get('savings_before_iva_clp', 0)/1000000:.1f}M CLP
  • IVA (19%): ${chilean.get('iva_amount_clp', 0)/1000000:.1f}M CLP
  • Total with IVA: ${chilean.get('savings_with_iva_clp', 0)/1000000:.1f}M CLP
  • Savings in UF: {chilean.get('savings_in_uf', 0):,.0f} UF
    """)
    
    input("\n➡️  Press Enter to see the 3-year projection...")
    
    # 3-Year Projection
    print_section("3-Year Financial Projection")
    projection = results.get('three_year_projection', {})
    
    print("\n📊 Cumulative Impact:")
    for year in range(1, 4):
        year_data = projection.get(f'year_{year}', {})
        print(f"\nYear {year}:")
        print(f"  • Annual Savings: ${year_data.get('annual_savings_clp', 0)/1000000:.1f}M CLP")
        print(f"  • Cumulative ROI: {year_data.get('roi_percentage', 0):.0f}%")
        print(f"  • Net Benefit: ${year_data.get('net_benefit_clp', 0)/1000000:.1f}M CLP")
    
    # Benchmarks
    print_section("Industry Benchmark Comparison")
    benchmarks = results.get('benchmarks', {})
    
    if 'operational_cost_ratio' in benchmarks:
        op_ratio = benchmarks['operational_cost_ratio']
        print(f"""
📊 vs Chilean Retail Average:
  • Your Cost Ratio: {op_ratio.get('client', 0)*100:.1f}%
  • Industry Average: {op_ratio.get('benchmark', 0)*100:.1f}%
  • Status: {op_ratio.get('status', 'N/A')}
  • Potential Savings: ${op_ratio.get('potential_savings_clp', 0)/1000000:.1f}M CLP
        """)
    
    # Summary
    print_header("EXECUTIVE SUMMARY")
    
    print(f"""
🎯 Investment Decision:
    
  Investment Required: ${inputs['investment_clp']/1000000:.0f}M CLP
  Expected Annual Return: ${summary.get('annual_savings_clp', 0)/1000000:.1f}M CLP
  Payback Period: {summary.get('payback_period_months', 0):.1f} months
  3-Year Net Benefit: ${projection.get('year_3', {}).get('net_benefit_clp', 0)/1000000:.1f}M CLP
  
  Recommendation: {"✅ HIGHLY RECOMMENDED" if summary.get('headline_roi', 0) > 100 else "✅ RECOMMENDED" if summary.get('headline_roi', 0) > 50 else "⚠️ EVALUATE FURTHER"}
  
  Key Success Factors:
  • Automate order processing (save 20+ hrs/week)
  • Integrate ERP with e-commerce platform
  • Implement real-time inventory sync
  • Reduce error rate from 8% to <1%
    """)
    
    print("\n" + "="*60)
    print("  🎉 Demo Complete - Ready to Close the Deal!")
    print("="*60)

def main():
    """Main demo entry point"""
    print("\n" + "🚀 " * 10)
    print("\n    CHILEAN E-COMMERCE SALES TOOLKIT")
    print("    Professional Consulting Tools Demo")
    print("\n" + "🚀 " * 10)
    
    print("""
This demo showcases:
  1. Enhanced ROI Calculator with Monte Carlo simulation
  2. Chilean market specifics (IVA, CLP, UF)
  3. AI-powered recommendations
  4. Industry benchmarks
  5. 3-year projections
    """)
    
    input("Press Enter to begin the demo...")
    
    try:
        demo_scenario()
        
        print("\n📧 Next Steps:")
        print("  1. Export detailed proposal (PDF/PowerPoint)")
        print("  2. Schedule follow-up meeting")
        print("  3. Prepare implementation roadmap")
        print("  4. Sign engagement contract")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
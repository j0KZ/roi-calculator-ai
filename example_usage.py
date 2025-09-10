#!/usr/bin/env python3
"""
Example usage of the ROI Calculator
Demonstrates different ways to use the calculator with various business scenarios
"""

import sys
import os
from pathlib import Path

# Add src directory to path
current_dir = Path(__file__).parent
src_dir = current_dir / 'src'
sys.path.insert(0, str(src_dir))

from roi_calculator import ROICalculator
from pdf_generator import ROIPDFGenerator


def example_small_business():
    """Example calculation for a small e-commerce business"""
    print("="*60)
    print("SMALL E-COMMERCE BUSINESS EXAMPLE")
    print("="*60)
    
    calculator = ROICalculator()
    
    # Small business inputs
    inputs = {
        'company_name': 'Small E-commerce Startup',
        'annual_revenue': 500000,  # $500K annual revenue
        'monthly_orders': 1500,   # 1,500 orders per month
        'avg_order_value': 27.78, # ~$28 average order
        'labor_costs': 3000,      # $3K monthly labor
        'shipping_costs': 2000,   # $2K monthly shipping
        'error_costs': 500,       # $500 monthly errors
        'inventory_costs': 1000,  # $1K monthly inventory
        'service_investment': 25000  # $25K investment
    }
    
    # Calculate ROI
    results = calculator.calculate_roi(inputs)
    
    # Display summary
    print(calculator.get_summary_text())
    
    # Generate PDF report
    pdf_generator = ROIPDFGenerator(results)
    pdf_filename = pdf_generator.generate_pdf('reports/small_business_roi_report.pdf')
    print(f"\nPDF report generated: {pdf_filename}")
    
    return results


def example_medium_business():
    """Example calculation for a medium e-commerce business"""
    print("="*60)
    print("MEDIUM E-COMMERCE BUSINESS EXAMPLE")
    print("="*60)
    
    calculator = ROICalculator()
    
    # Medium business inputs
    inputs = {
        'company_name': 'Growing E-commerce Company',
        'annual_revenue': 2000000,  # $2M annual revenue
        'monthly_orders': 5000,     # 5,000 orders per month
        'avg_order_value': 33.33,   # ~$33 average order
        'labor_costs': 8000,        # $8K monthly labor
        'shipping_costs': 5000,     # $5K monthly shipping
        'error_costs': 2000,        # $2K monthly errors
        'inventory_costs': 3000,    # $3K monthly inventory
        'service_investment': 50000 # $50K investment
    }
    
    # Calculate ROI
    results = calculator.calculate_roi(inputs)
    
    # Display summary
    print(calculator.get_summary_text())
    
    # Generate PDF report
    pdf_generator = ROIPDFGenerator(results)
    pdf_filename = pdf_generator.generate_pdf('reports/medium_business_roi_report.pdf')
    print(f"\nPDF report generated: {pdf_filename}")
    
    return results


def example_large_business():
    """Example calculation for a large e-commerce enterprise"""
    print("="*60)
    print("LARGE E-COMMERCE ENTERPRISE EXAMPLE")
    print("="*60)
    
    calculator = ROICalculator()
    
    # Large business inputs
    inputs = {
        'company_name': 'Enterprise E-commerce Corp',
        'annual_revenue': 5000000,  # $5M annual revenue
        'monthly_orders': 12000,    # 12,000 orders per month
        'avg_order_value': 34.72,   # ~$35 average order
        'labor_costs': 20000,       # $20K monthly labor
        'shipping_costs': 12000,    # $12K monthly shipping
        'error_costs': 5000,        # $5K monthly errors
        'inventory_costs': 8000,    # $8K monthly inventory
        'service_investment': 100000 # $100K investment
    }
    
    # Calculate ROI
    results = calculator.calculate_roi(inputs)
    
    # Display summary
    print(calculator.get_summary_text())
    
    # Generate PDF report
    pdf_generator = ROIPDFGenerator(results)
    pdf_filename = pdf_generator.generate_pdf('reports/large_business_roi_report.pdf')
    print(f"\nPDF report generated: {pdf_filename}")
    
    return results


def example_comparison():
    """Compare ROI across different business sizes"""
    print("="*80)
    print("BUSINESS SIZE COMPARISON")
    print("="*80)
    
    calculator = ROICalculator()
    
    # Business scenarios
    scenarios = {
        'Small': {
            'annual_revenue': 500000,
            'monthly_orders': 1500,
            'avg_order_value': 27.78,
            'labor_costs': 3000,
            'shipping_costs': 2000,
            'error_costs': 500,
            'inventory_costs': 1000,
            'service_investment': 25000
        },
        'Medium': {
            'annual_revenue': 2000000,
            'monthly_orders': 5000,
            'avg_order_value': 33.33,
            'labor_costs': 8000,
            'shipping_costs': 5000,
            'error_costs': 2000,
            'inventory_costs': 3000,
            'service_investment': 50000
        },
        'Large': {
            'annual_revenue': 5000000,
            'monthly_orders': 12000,
            'avg_order_value': 34.72,
            'labor_costs': 20000,
            'shipping_costs': 12000,
            'error_costs': 5000,
            'inventory_costs': 8000,
            'service_investment': 100000
        }
    }
    
    print(f"{'Business Size':<15} {'Investment':<12} {'Annual Savings':<15} {'Payback':<12} {'3-Yr ROI':<10} {'NPV':<12}")
    print("-" * 80)
    
    for size, inputs in scenarios.items():
        results = calculator.calculate_roi(inputs)
        
        roi_metrics = results['roi_metrics']
        financial = results['financial_metrics']
        projections = results['projections']
        
        print(f"{size:<15} ${inputs['service_investment']:>10,} ${roi_metrics['annual_savings']:>13,.0f} {roi_metrics['payback_period_text']:<12} {projections['year_3']['roi_percentage']:>8.1f}% ${financial['npv']:>10,.0f}")


def example_sensitivity_analysis():
    """Demonstrate sensitivity to different investment levels"""
    print("="*80)
    print("INVESTMENT SENSITIVITY ANALYSIS")
    print("="*80)
    
    calculator = ROICalculator()
    
    # Base scenario (medium business)
    base_inputs = {
        'annual_revenue': 2000000,
        'monthly_orders': 5000,
        'avg_order_value': 33.33,
        'labor_costs': 8000,
        'shipping_costs': 5000,
        'error_costs': 2000,
        'inventory_costs': 3000,
        'service_investment': 50000  # This will vary
    }
    
    # Test different investment levels
    investment_levels = [25000, 40000, 50000, 60000, 75000, 100000]
    
    print(f"{'Investment':<12} {'Payback (Months)':<16} {'1st Year ROI':<13} {'3-Year ROI':<12} {'NPV':<12}")
    print("-" * 70)
    
    for investment in investment_levels:
        inputs = base_inputs.copy()
        inputs['service_investment'] = investment
        
        results = calculator.calculate_roi(inputs)
        roi_metrics = results['roi_metrics']
        financial = results['financial_metrics']
        projections = results['projections']
        
        print(f"${investment:>10,} {roi_metrics['payback_period_months']:>14.1f} {roi_metrics['first_year_roi']:>11.1f}% {projections['year_3']['roi_percentage']:>10.1f}% ${financial['npv']:>10,.0f}")


def example_export_json():
    """Demonstrate JSON export functionality"""
    print("="*60)
    print("JSON EXPORT EXAMPLE")
    print("="*60)
    
    calculator = ROICalculator()
    
    inputs = {
        'company_name': 'Example Export Company',
        'annual_revenue': 1500000,
        'monthly_orders': 4000,
        'avg_order_value': 31.25,
        'labor_costs': 6000,
        'shipping_costs': 4000,
        'error_costs': 1500,
        'inventory_costs': 2500,
        'service_investment': 40000
    }
    
    # Calculate ROI
    results = calculator.calculate_roi(inputs)
    
    # Export to JSON
    json_filename = calculator.export_to_json('reports/example_results.json')
    print(f"Results exported to: {json_filename}")
    
    # Display key metrics
    roi_metrics = results['roi_metrics']
    print(f"\nKey Metrics:")
    print(f"  Annual Savings: ${roi_metrics['annual_savings']:,.2f}")
    print(f"  Payback Period: {roi_metrics['payback_period_text']}")
    print(f"  3-Year ROI: {results['projections']['year_3']['roi_percentage']:.1f}%")
    print(f"  NPV: ${results['financial_metrics']['npv']:,.2f}")


def example_chilean_market_focus():
    """Demonstrate Chilean market-specific calculations"""
    print("="*60)
    print("CHILEAN MARKET FOCUS EXAMPLE")
    print("="*60)
    
    calculator = ROICalculator()
    
    # Chilean e-commerce business
    inputs = {
        'company_name': 'Chilean E-commerce Ltda.',
        'annual_revenue': 1800000,  # ~1.5B CLP at 850 CLP/USD
        'monthly_orders': 4500,
        'avg_order_value': 33.33,
        'labor_costs': 7000,   # Higher labor costs typical in Chile
        'shipping_costs': 4500, # Higher shipping costs due to geography
        'error_costs': 1800,
        'inventory_costs': 2700,
        'service_investment': 45000
    }
    
    results = calculator.calculate_roi(inputs)
    
    # Focus on Chilean specifics
    chilean = results['chilean_specifics']
    
    print(f"Chilean Market Analysis:")
    print(f"  IVA Rate: {chilean['iva_rate']*100:.0f}%")
    print(f"  Annual Savings (before IVA): ${chilean['savings_with_iva']['amount_before_iva']:,.2f}")
    print(f"  IVA on Savings: ${chilean['savings_with_iva']['iva_amount']:,.2f}")
    print(f"  Total Savings (with IVA): ${chilean['savings_with_iva']['amount_with_iva']:,.2f}")
    
    print(f"\nInflation-Adjusted Projections:")
    projections = results['projections']
    for year in range(1, 4):
        year_data = projections[f'year_{year}']
        print(f"  Year {year} Savings: ${year_data['savings']:,.2f}")
    
    print(calculator.get_summary_text())


def main():
    """Run all examples"""
    # Ensure reports directory exists
    os.makedirs('reports', exist_ok=True)
    
    try:
        print("ROI CALCULATOR - EXAMPLE SCENARIOS")
        print("="*80)
        
        # Run individual examples
        example_small_business()
        print("\n" + "="*80 + "\n")
        
        example_medium_business()
        print("\n" + "="*80 + "\n")
        
        example_large_business()
        print("\n" + "="*80 + "\n")
        
        # Comparative analyses
        example_comparison()
        print("\n" + "="*80 + "\n")
        
        example_sensitivity_analysis()
        print("\n" + "="*80 + "\n")
        
        # Feature demonstrations
        example_export_json()
        print("\n" + "="*80 + "\n")
        
        example_chilean_market_focus()
        
        print("\n" + "="*80)
        print("ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("Check the 'reports/' directory for generated PDF reports and JSON exports.")
        print("="*80)
        
    except Exception as e:
        print(f"Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
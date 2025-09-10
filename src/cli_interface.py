#!/usr/bin/env python3
"""
Command Line Interface for ROI Calculator
Provides interactive and batch calculation modes
"""

import argparse
import sys
import json
from typing import Dict
from roi_calculator import ROICalculator


def get_user_inputs() -> Dict:
    """Interactive input collection"""
    print("\n" + "="*60)
    print("E-COMMERCE OPERATIONS ROI CALCULATOR")
    print("="*60)
    print("\nPlease enter your business information:")
    print("(All monetary values should be in USD)")
    
    try:
        # Revenue information
        print("\n📊 REVENUE INFORMATION:")
        annual_revenue = float(input("Annual Revenue ($): "))
        monthly_orders = int(input("Average Monthly Orders: "))
        avg_order_value = float(input("Average Order Value ($): "))
        
        # Current operational costs (monthly)
        print("\n💰 CURRENT MONTHLY OPERATIONAL COSTS:")
        labor_costs = float(input("Labor Costs ($/month): "))
        shipping_costs = float(input("Shipping Costs ($/month): "))
        error_costs = float(input("Error-related Costs ($/month): "))
        inventory_costs = float(input("Inventory Management Costs ($/month): "))
        
        # Investment
        print("\n🏗️ INVESTMENT INFORMATION:")
        service_investment = float(input("Our Service Investment ($): "))
        
        return {
            'annual_revenue': annual_revenue,
            'monthly_orders': monthly_orders,
            'avg_order_value': avg_order_value,
            'labor_costs': labor_costs,
            'shipping_costs': shipping_costs,
            'error_costs': error_costs,
            'inventory_costs': inventory_costs,
            'service_investment': service_investment
        }
        
    except ValueError as e:
        print(f"Error: Please enter valid numeric values. {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nCalculation cancelled by user.")
        sys.exit(0)


def load_inputs_from_file(filename: str) -> Dict:
    """Load inputs from JSON file"""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format in '{filename}': {e}")
        sys.exit(1)


def save_template(filename: str = "roi_inputs_template.json") -> None:
    """Save input template file"""
    template = {
        "annual_revenue": 2000000,
        "monthly_orders": 5000,
        "avg_order_value": 33.33,
        "labor_costs": 8000,
        "shipping_costs": 5000,
        "error_costs": 2000,
        "inventory_costs": 3000,
        "service_investment": 50000
    }
    
    with open(filename, 'w') as f:
        json.dump(template, f, indent=2)
    
    print(f"Template saved to '{filename}'")
    print("Edit this file with your values and use --input flag to load it.")


def display_detailed_results(calculator: ROICalculator) -> None:
    """Display detailed calculation results"""
    results = calculator.results
    
    print("\n" + "="*80)
    print("DETAILED ROI ANALYSIS RESULTS")
    print("="*80)
    
    # Summary
    print(calculator.get_summary_text())
    
    # Detailed breakdown
    print("\n📈 YEAR-BY-YEAR PROJECTIONS:")
    print("-" * 60)
    for year in range(1, 4):
        year_data = results['projections'][f'year_{year}']
        print(f"Year {year}:")
        print(f"  Annual Savings: ${year_data['savings']:,.2f}")
        print(f"  Net Benefit: ${year_data['net_benefit']:,.2f}")
        print(f"  Cumulative ROI: {year_data['roi_percentage']:.1f}%")
        print()
    
    # Chilean market specifics
    print("\n🇨🇱 CHILEAN MARKET SPECIFICS:")
    print("-" * 40)
    chilean = results['chilean_specifics']
    iva_calc = chilean['savings_with_iva']
    print(f"IVA Rate: {chilean['iva_rate']*100:.0f}%")
    print(f"Savings before IVA: ${iva_calc['amount_before_iva']:,.2f}")
    print(f"IVA Amount: ${iva_calc['iva_amount']:,.2f}")
    print(f"Total with IVA: ${iva_calc['amount_with_iva']:,.2f}")
    
    # Cost breakdown
    print("\n💸 COST REDUCTION BREAKDOWN:")
    print("-" * 50)
    savings = results['savings']
    for category in ['labor', 'shipping', 'errors', 'inventory']:
        cat_data = savings[category]
        print(f"{category.title()} ({cat_data['percentage']*100:.0f}% reduction):")
        print(f"  Monthly Savings: ${cat_data['monthly']:,.2f}")
        print(f"  Annual Savings: ${cat_data['annual']:,.2f}")
    
    print("\n" + "="*80)


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="E-commerce Operations ROI Calculator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli_interface.py                    # Interactive mode
  python cli_interface.py -i data.json      # Load from file
  python cli_interface.py --template        # Create input template
  python cli_interface.py -i data.json -o results.json  # Save results
        """
    )
    
    parser.add_argument(
        '-i', '--input',
        type=str,
        help='Load inputs from JSON file'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        help='Save results to JSON file'
    )
    
    parser.add_argument(
        '--template',
        action='store_true',
        help='Create input template file'
    )
    
    parser.add_argument(
        '--summary',
        action='store_true',
        help='Show summary only (no detailed breakdown)'
    )
    
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Minimal output mode'
    )
    
    args = parser.parse_args()
    
    # Handle template creation
    if args.template:
        save_template()
        return
    
    # Get inputs
    if args.input:
        if not args.quiet:
            print(f"Loading inputs from '{args.input}'...")
        inputs = load_inputs_from_file(args.input)
    else:
        inputs = get_user_inputs()
    
    # Calculate ROI
    if not args.quiet:
        print("\n🔄 Calculating ROI...")
    
    try:
        calculator = ROICalculator()
        results = calculator.calculate_roi(inputs)
        
        # Display results
        if args.summary or args.quiet:
            print(calculator.get_summary_text())
        else:
            display_detailed_results(calculator)
        
        # Save results if requested
        if args.output:
            calculator.export_to_json(args.output)
            if not args.quiet:
                print(f"\n✅ Results saved to '{args.output}'")
        
    except Exception as e:
        print(f"Error during calculation: {e}")
        sys.exit(1)
    
    if not args.quiet:
        print("\n🎉 Calculation complete!")


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Test all backend functions to identify issues
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_all_modules():
    errors = []
    
    # Test 1: Enhanced ROI Calculator
    print("Testing Enhanced ROI Calculator...")
    try:
        from enhanced_roi_calculator import EnhancedROICalculator
        calc = EnhancedROICalculator()
        result = calc.calculate_roi(
            initial_investment=20000000,
            time_to_implement_months=3,
            monthly_revenue_increase=5000000,
            monthly_cost_savings=2000000
        )
        print(f"✅ ROI Calculator: ROI = {result['roi_percentage']:.1f}%")
    except Exception as e:
        errors.append(f"❌ ROI Calculator: {e}")
        print(f"❌ ROI Calculator failed: {e}")
    
    # Test 2: Tax Calculator
    print("\nTesting Tax Calculator...")
    try:
        from tax_calculator import TaxCalculator
        tax_calc = TaxCalculator()
        result = tax_calc.calculate_tax_impact(
            1000000,
            jurisdiction="Chile",
            tax_type="sales"
        )
        print(f"✅ Tax Calculator: Tax = ${result['tax_amount']:,.0f}")
    except Exception as e:
        errors.append(f"❌ Tax Calculator: {e}")
        print(f"❌ Tax Calculator failed: {e}")
    
    # Test 3: Currency Converter
    print("\nTesting Currency Converter...")
    try:
        from currency_converter import CurrencyConverter
        converter = CurrencyConverter()
        result = converter.convert(1000000, "CLP", "USD")
        print(f"✅ Currency Converter: 1M CLP = ${result['converted_amount']:,.2f} USD")
    except Exception as e:
        errors.append(f"❌ Currency Converter: {e}")
        print(f"❌ Currency Converter failed: {e}")
    
    # Test 4: Break-Even Analyzer
    print("\nTesting Break-Even Analyzer...")
    try:
        from breakeven_analyzer import BreakEvenAnalyzer
        analyzer = BreakEvenAnalyzer()
        roi_inputs = {
            'monthly_revenue': 50000000,
            'monthly_costs': 40000000,
            'initial_investment': 20000000
        }
        result = analyzer.analyze_breakeven_scenarios(roi_inputs)
        print(f"✅ Break-Even Analyzer: Analysis complete")
    except Exception as e:
        errors.append(f"❌ Break-Even Analyzer: {e}")
        print(f"❌ Break-Even Analyzer failed: {e}")
    
    # Test 5: Cost Optimizer
    print("\nTesting Cost Optimizer...")
    try:
        from cost_optimizer import CostOptimizer
        optimizer = CostOptimizer()
        roi_data = {
            'inputs': {
                'annual_revenue': 600000000,
                'labor_costs': 180000000,
                'shipping_costs': 42000000,
                'inventory_costs': 24000000
            },
            'current_costs': {
                'total_annual': 400000000
            }
        }
        report = optimizer.analyze_and_optimize(roi_data)
        summary = optimizer.get_optimization_summary(report)
        print(f"✅ Cost Optimizer: Savings = ${summary.get('total_savings', 0):,.0f}")
    except Exception as e:
        errors.append(f"❌ Cost Optimizer: {e}")
        print(f"❌ Cost Optimizer failed: {e}")
    
    # Test 6: Batch Processor
    print("\nTesting Batch Processor...")
    try:
        from batch_processor import BatchProcessor
        processor = BatchProcessor()
        scenarios = [
            {'name': 'Scenario 1', 'investment': 10000000},
            {'name': 'Scenario 2', 'investment': 20000000}
        ]
        results = processor.process_scenarios_parallel(scenarios)
        print(f"✅ Batch Processor: Processed {len(results)} scenarios")
    except Exception as e:
        errors.append(f"❌ Batch Processor: {e}")
        print(f"❌ Batch Processor failed: {e}")
    
    # Test 7: Rapid Assessment Tool
    print("\nTesting Rapid Assessment Tool...")
    try:
        from rapid_assessment_tool import RapidAssessmentTool
        tool = RapidAssessmentTool()
        assessment = tool.assess({
            'industry': 'retail',
            'company_size': 'medium',
            'current_revenue': 100000000,
            'current_conversion_rate': 2.5,
            'average_order_value': 75000,
            'monthly_traffic': 50000,
            'customer_service_tickets': 500,
            'inventory_turnover': 8,
            'current_tools': ['basic_ecommerce', 'email']
        })
        print(f"✅ Rapid Assessment: Score = {assessment['overall_score']}/100")
    except Exception as e:
        errors.append(f"❌ Rapid Assessment: {e}")
        print(f"❌ Rapid Assessment failed: {e}")
    
    # Test 8: Proposal Generator
    print("\nTesting Proposal Generator...")
    try:
        from proposal_generator import ProposalGenerator
        generator = ProposalGenerator()
        proposal = generator.generate_proposal({
            'company_name': 'Test Company',
            'industry': 'retail',
            'contact_name': 'John Doe',
            'current_revenue': 100000000
        })
        print(f"✅ Proposal Generator: Generated {len(proposal.get('sections', []))} sections")
    except Exception as e:
        errors.append(f"❌ Proposal Generator: {e}")
        print(f"❌ Proposal Generator failed: {e}")
    
    # Test 9: Template Manager
    print("\nTesting Template Manager...")
    try:
        from template_manager import TemplateManager
        manager = TemplateManager()
        templates = manager.list_templates()
        print(f"✅ Template Manager: Found {len(templates)} templates")
    except Exception as e:
        errors.append(f"❌ Template Manager: {e}")
        print(f"❌ Template Manager failed: {e}")
    
    # Test 10: History Manager
    print("\nTesting History Manager...")
    try:
        from history_manager import HistoryManager
        history = HistoryManager()
        # Just test initialization
        print(f"✅ History Manager: Initialized successfully")
    except Exception as e:
        errors.append(f"❌ History Manager: {e}")
        print(f"❌ History Manager failed: {e}")
    
    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    
    if errors:
        print(f"\n❌ {len(errors)} modules failed:")
        for error in errors:
            print(f"  {error}")
    else:
        print("\n✅ All modules working correctly!")
    
    return len(errors) == 0

if __name__ == "__main__":
    success = test_all_modules()
    sys.exit(0 if success else 1)
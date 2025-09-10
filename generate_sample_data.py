#!/usr/bin/env python3
"""
Generate sample data for testing real metrics display
"""

import sys
import os
import random
from datetime import datetime, timedelta

sys.path.insert(0, 'src')

from history_manager import HistoryManager

def generate_sample_calculations():
    """Generate sample ROI calculations for testing"""
    
    history = HistoryManager()
    
    # Sample company names
    companies = [
        "TechStore Chile", "Fashion Express", "ElectroMarket", 
        "HomeDecor Pro", "Sports Gear", "Beauty Shop CL",
        "Pet Supplies Plus", "Book Haven", "Toy Kingdom",
        "Office Supplies Co", "Garden Center", "Auto Parts Direct"
    ]
    
    # Sample industries
    industries = ["retail", "wholesale", "services", "manufacturing"]
    
    print("Generating sample ROI calculations...")
    
    for i in range(20):
        # Random values for realistic variation
        investment = random.randint(10000000, 50000000)
        annual_revenue = random.randint(100000000, 1000000000)
        roi_percentage = random.uniform(50, 300)
        payback_months = random.uniform(3, 18)
        annual_savings = random.randint(20000000, 200000000)
        
        # Random date within last 60 days
        days_ago = random.randint(0, 60)
        calc_date = datetime.now() - timedelta(days=days_ago)
        
        # Create calculation entry
        calc_id = history.add_calculation(
            calculation_type='roi',
            inputs={
                'investment_clp': investment,
                'annual_revenue_clp': annual_revenue,
                'industry': random.choice(industries),
                'monthly_orders': random.randint(500, 5000),
                'avg_order_value_clp': random.randint(25000, 150000),
                'labor_costs_clp': annual_revenue * 0.3,
                'shipping_costs_clp': annual_revenue * 0.1,
                'platform_fees_clp': annual_revenue * 0.03,
                'error_costs_clp': annual_revenue * 0.02,
                'inventory_costs_clp': annual_revenue * 0.05,
                'conversion_rate': random.uniform(1.5, 4.0)
            },
            results={
                'roi_percentage': roi_percentage,
                'payback_period_months': payback_months,
                'net_present_value': investment * (1 + roi_percentage/100),
                'internal_rate_of_return': roi_percentage / 100,
                'savings': {
                    'annual_savings': annual_savings,
                    'monthly_savings': annual_savings / 12,
                    'labor_savings': annual_savings * 0.4,
                    'shipping_savings': annual_savings * 0.3,
                    'error_reduction_savings': annual_savings * 0.2,
                    'inventory_savings': annual_savings * 0.1
                },
                'current_costs': {
                    'total_annual': annual_revenue * 0.6
                },
                'optimized_costs': {
                    'total_annual': annual_revenue * 0.45
                }
            },
            metadata={
                'company_name': random.choice(companies),
                'calculation_time': random.uniform(0.5, 2.0),
                'user': 'demo_user',
                'version': '1.0'
            }
        )
        
        # Override timestamp to spread across time
        history.history[-1]['timestamp'] = calc_date.isoformat()
    
    # Save history with updated timestamps
    history._save_history()
    
    print(f"✅ Generated {len(history.history)} sample calculations")
    
    # Display summary
    from metrics_aggregator import MetricsAggregator
    aggregator = MetricsAggregator(history)
    metrics = aggregator.get_dashboard_metrics()
    
    print("\n📊 Dashboard Metrics:")
    print(f"  - ROI Promedio: {metrics['avg_roi_display']}")
    print(f"  - Tiempo de Retorno: {metrics['avg_payback_display']}")
    print(f"  - Ahorro Mensual: {metrics['avg_monthly_savings_display']}")
    print(f"  - Clientes Analizados: {metrics['total_clients_display']}")
    print(f"  - Crecimiento: {metrics['monthly_growth_display']}")
    
    summary = aggregator.get_summary_statistics()
    print(f"\n📈 Estadísticas Totales:")
    print(f"  - Total de cálculos: {summary['total_calculations']}")
    print(f"  - Valor total analizado: {summary['total_value_analyzed_display']}")
    print(f"  - Ahorros identificados: {summary['total_savings_identified_display']}")
    print(f"  - Mejora promedio: {summary['avg_improvement_display']}")

if __name__ == "__main__":
    generate_sample_calculations()
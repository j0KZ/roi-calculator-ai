#!/usr/bin/env python3
"""
Create sample templates for the ROI Calculator
"""

import requests
import json

# API endpoint
BASE_URL = "http://localhost:8000"

# Sample templates to create
templates = [
    {
        "name": "Chilean Retail Chain",
        "description": "Template for Chilean retail businesses with multiple store locations",
        "category": "retail",
        "tags": ["chile", "retail", "multi-location", "physical-stores"],
        "template_data": {
            "annual_revenue": 3500000,
            "monthly_orders": 12000,
            "avg_order_value": 24.31,
            "labor_costs": 18000,
            "shipping_costs": 8500,
            "error_costs": 3200,
            "inventory_costs": 12000,
            "service_investment": 85000
        },
        "metadata": {
            "region": "Latin America",
            "currency": "CLP",
            "stores": 15,
            "employees": 120,
            "notes": "Typical Chilean retail chain with physical and online presence"
        }
    },
    {
        "name": "Tech Startup - SaaS",
        "description": "Software as a Service startup with recurring revenue model",
        "category": "technology",
        "tags": ["saas", "startup", "subscription", "b2b"],
        "template_data": {
            "annual_revenue": 1200000,
            "monthly_orders": 450,
            "avg_order_value": 222.22,
            "labor_costs": 25000,
            "shipping_costs": 500,
            "error_costs": 2000,
            "inventory_costs": 1500,
            "service_investment": 50000
        },
        "metadata": {
            "model": "Subscription",
            "mrr": 100000,
            "churn_rate": "5%",
            "cac": 500,
            "ltv": 10000,
            "notes": "B2B SaaS with monthly recurring revenue"
        }
    },
    {
        "name": "Fashion E-commerce",
        "description": "Online fashion retailer with high return rates",
        "category": "fashion",
        "tags": ["fashion", "apparel", "online", "high-returns"],
        "template_data": {
            "annual_revenue": 2800000,
            "monthly_orders": 6500,
            "avg_order_value": 35.90,
            "labor_costs": 12000,
            "shipping_costs": 15000,
            "error_costs": 8000,
            "inventory_costs": 20000,
            "service_investment": 75000
        },
        "metadata": {
            "return_rate": "30%",
            "peak_season": "November-December",
            "main_categories": ["Women's Apparel", "Accessories", "Shoes"],
            "notes": "Fashion retailer with seasonal variations and high returns"
        }
    },
    {
        "name": "Food Delivery Platform",
        "description": "Multi-restaurant food delivery marketplace",
        "category": "food_delivery",
        "tags": ["food", "delivery", "marketplace", "logistics"],
        "template_data": {
            "annual_revenue": 5500000,
            "monthly_orders": 35000,
            "avg_order_value": 13.10,
            "labor_costs": 28000,
            "shipping_costs": 45000,
            "error_costs": 12000,
            "inventory_costs": 3000,
            "service_investment": 150000
        },
        "metadata": {
            "restaurants": 250,
            "delivery_time_avg": "35 minutes",
            "commission_rate": "25%",
            "peak_hours": "12-2pm, 6-9pm",
            "notes": "Food delivery platform with high logistics costs"
        }
    },
    {
        "name": "Electronics B2B Wholesale",
        "description": "Business-to-business electronics wholesaler",
        "category": "b2b",
        "tags": ["b2b", "wholesale", "electronics", "bulk-orders"],
        "template_data": {
            "annual_revenue": 8000000,
            "monthly_orders": 850,
            "avg_order_value": 784.31,
            "labor_costs": 35000,
            "shipping_costs": 25000,
            "error_costs": 5000,
            "inventory_costs": 45000,
            "service_investment": 200000
        },
        "metadata": {
            "avg_order_size": "50 units",
            "payment_terms": "Net 30",
            "client_type": "Retailers and Distributors",
            "warehouse_locations": 3,
            "notes": "B2B wholesale with large order values and inventory requirements"
        }
    },
    {
        "name": "Subscription Box Service",
        "description": "Monthly subscription box for beauty products",
        "category": "subscription",
        "tags": ["subscription", "beauty", "monthly-box", "recurring"],
        "template_data": {
            "annual_revenue": 2000000,
            "monthly_orders": 8000,
            "avg_order_value": 20.83,
            "labor_costs": 10000,
            "shipping_costs": 18000,
            "error_costs": 3500,
            "inventory_costs": 15000,
            "service_investment": 60000
        },
        "metadata": {
            "subscription_tiers": ["Basic", "Premium", "Deluxe"],
            "retention_rate": "85%",
            "acquisition_channel": "Social Media",
            "box_curation": "Personalized",
            "notes": "Subscription box with personalized product selection"
        }
    }
]

def create_templates():
    """Create sample templates via API"""
    print("Creating sample templates...")
    print("-" * 50)
    
    for template in templates:
        try:
            response = requests.post(
                f"{BASE_URL}/api/templates/create",
                json=template,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✓ Created: {template['name']}")
                print(f"  ID: {result.get('id')}")
                print(f"  Category: {template['category']}")
                print(f"  Tags: {', '.join(template['tags'])}")
            else:
                print(f"✗ Failed to create: {template['name']}")
                print(f"  Error: {response.text}")
        
        except Exception as e:
            print(f"✗ Error creating {template['name']}: {str(e)}")
        
        print("-" * 50)
    
    # List all templates
    print("\nFetching all templates...")
    try:
        response = requests.get(f"{BASE_URL}/api/templates/list")
        if response.status_code == 200:
            all_templates = response.json()
            print(f"\nTotal templates available: {len(all_templates)}")
            print("\nTemplates by category:")
            
            categories = {}
            for tmpl in all_templates:
                cat = tmpl.get('category', 'uncategorized')
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(tmpl['name'])
            
            for cat, names in categories.items():
                print(f"  {cat}: {len(names)} templates")
                for name in names[:3]:  # Show first 3
                    print(f"    - {name}")
                if len(names) > 3:
                    print(f"    ... and {len(names) - 3} more")
    
    except Exception as e:
        print(f"Error fetching templates: {str(e)}")

if __name__ == "__main__":
    print("ROI Calculator - Sample Template Creator")
    print("=" * 50)
    create_templates()
    print("\n✅ Sample templates created successfully!")
    print("Visit http://localhost:8000/templates to view them")
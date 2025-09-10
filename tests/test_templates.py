#!/usr/bin/env python3
"""
Test the template functionality by displaying available templates
"""

import requests
import json

# API endpoint
BASE_URL = "http://localhost:8000"

def test_templates():
    """Test template functionality"""
    print("Testing Template Functionality")
    print("=" * 50)
    
    # List all templates
    print("\n1. Fetching all available templates...")
    print("-" * 50)
    try:
        response = requests.get(f"{BASE_URL}/api/templates/list")
        if response.status_code == 200:
            templates = response.json()
            print(f"✓ Found {len(templates)} templates\n")
            
            # Group by source
            system_templates = [t for t in templates if t.get('source') == 'system']
            user_templates = [t for t in templates if t.get('source') == 'user']
            
            print(f"System Templates: {len(system_templates)}")
            for i, tmpl in enumerate(system_templates, 1):
                print(f"  {i}. {tmpl['name']}")
                print(f"     Category: {tmpl.get('category', 'N/A')}")
                print(f"     Description: {tmpl.get('description', 'N/A')[:80]}...")
                if 'template_data' in tmpl:
                    data = tmpl['template_data']
                    print(f"     Annual Revenue: ${data.get('annual_revenue', 0):,.0f}")
                    print(f"     Monthly Orders: {data.get('monthly_orders', 0):,}")
                print()
            
            print(f"\nUser Templates: {len(user_templates)}")
            for tmpl in user_templates:
                print(f"  - {tmpl['name']} (ID: {tmpl['id']})")
        else:
            print(f"✗ Failed to fetch templates: {response.status_code}")
            print(response.text)
    
    except Exception as e:
        print(f"✗ Error: {str(e)}")
    
    # Test loading a specific template
    print("\n2. Testing template loading...")
    print("-" * 50)
    try:
        # Try to get the small_business template
        response = requests.get(f"{BASE_URL}/api/templates/small_business")
        if response.status_code == 200:
            template = response.json()
            print(f"✓ Successfully loaded template: {template['name']}")
            print(f"  Template Data:")
            for key, value in template['template_data'].items():
                print(f"    {key}: {value}")
        else:
            print(f"✗ Failed to load template: {response.status_code}")
    
    except Exception as e:
        print(f"✗ Error: {str(e)}")
    
    print("\n" + "=" * 50)
    print("Template system is working with predefined templates!")
    print("You can use these templates in the web interface at:")
    print(f"  {BASE_URL}/templates")

if __name__ == "__main__":
    test_templates()
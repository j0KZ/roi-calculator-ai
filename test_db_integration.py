#!/usr/bin/env python3
"""
Test Database Integration for Chilean E-commerce Sales Toolkit
"""

import sys
import os
import json
from datetime import datetime

# Add src to path
sys.path.insert(0, 'src')

# Import database modules
from database.connection import get_db, get_session, init_database
from database.models import Calculation, Template, Base

def test_connection():
    """Test database connection"""
    print("🔍 Testing Database Connection...")
    
    db = get_db()
    if db.test_connection():
        print("✅ Database connection successful")
        return True
    else:
        print("❌ Database connection failed")
        return False

def test_create_calculation():
    """Test creating a calculation"""
    print("\n📝 Testing Create Calculation...")
    
    try:
        session = get_session()
        
        # Create test calculation
        calc = Calculation(
            company_name="Test Company",
            annual_revenue=1000000000,
            monthly_orders=1000,
            avg_order_value=83333,
            labor_costs=5000000,
            shipping_costs=3000000,
            error_costs=1500000,
            inventory_costs=2000000,
            service_investment=50000000,
            results={
                'roi_percentage': 136.2,
                'payback_months': 8.8,
                'total_annual_savings': 68100000,
                'total_monthly_savings': 5675000
            },
            notes="Test calculation",
            tags="test,demo"
        )
        
        session.add(calc)
        session.commit()
        
        print(f"✅ Calculation created with ID: {calc.id}")
        
        # Store ID for later tests
        test_calc_id = calc.id
        
        session.close()
        return test_calc_id
        
    except Exception as e:
        print(f"❌ Error creating calculation: {e}")
        return None

def test_read_calculations():
    """Test reading calculations"""
    print("\n📖 Testing Read Calculations...")
    
    try:
        session = get_session()
        
        # Get all calculations
        calculations = session.query(Calculation).all()
        
        print(f"✅ Found {len(calculations)} calculations")
        
        for calc in calculations[:3]:  # Show first 3
            print(f"  - #{calc.id}: {calc.company_name} | ROI: {calc.get_roi():.0f}%")
        
        session.close()
        return True
        
    except Exception as e:
        print(f"❌ Error reading calculations: {e}")
        return False

def test_update_calculation(calc_id):
    """Test updating a calculation"""
    print(f"\n✏️ Testing Update Calculation #{calc_id}...")
    
    if not calc_id:
        print("⚠️ No calculation ID provided")
        return False
    
    try:
        session = get_session()
        
        # Get calculation
        calc = session.query(Calculation).filter_by(id=calc_id).first()
        
        if calc:
            # Update fields
            calc.company_name = "Updated Test Company"
            calc.notes = "Updated via test script"
            
            session.commit()
            print(f"✅ Calculation #{calc_id} updated")
            
            session.close()
            return True
        else:
            print(f"❌ Calculation #{calc_id} not found")
            return False
            
    except Exception as e:
        print(f"❌ Error updating calculation: {e}")
        return False

def test_create_template():
    """Test creating a template"""
    print("\n📋 Testing Create Template...")
    
    try:
        session = get_session()
        
        # Create test template
        template = Template(
            name="Test Template",
            description="Template created by test script",
            category="test",
            template_data={
                'annual_revenue': 2000000000,
                'monthly_orders': 2000,
                'avg_order_value': 83333,
                'labor_costs': 8000000,
                'shipping_costs': 5000000,
                'error_costs': 2000000,
                'inventory_costs': 3000000,
                'service_investment': 75000000,
                'industry': 'test',
                'business_size': 'medium'
            },
            industry="test",
            business_size="medium",
            is_public=1,
            created_by='test_script',
            tags="test,automation"
        )
        
        session.add(template)
        session.commit()
        
        print(f"✅ Template created with ID: {template.id}")
        
        session.close()
        return template.id
        
    except Exception as e:
        print(f"❌ Error creating template: {e}")
        return None

def test_read_templates():
    """Test reading templates"""
    print("\n📚 Testing Read Templates...")
    
    try:
        session = get_session()
        
        # Get all templates
        templates = session.query(Template).all()
        
        print(f"✅ Found {len(templates)} templates")
        
        for template in templates[:3]:  # Show first 3
            print(f"  - #{template.id}: {template.name} | Category: {template.category}")
        
        session.close()
        return True
        
    except Exception as e:
        print(f"❌ Error reading templates: {e}")
        return False

def test_delete_calculation(calc_id):
    """Test deleting a calculation"""
    print(f"\n🗑️ Testing Delete Calculation #{calc_id}...")
    
    if not calc_id:
        print("⚠️ No calculation ID provided")
        return False
    
    try:
        session = get_session()
        
        # Get calculation
        calc = session.query(Calculation).filter_by(id=calc_id).first()
        
        if calc:
            session.delete(calc)
            session.commit()
            print(f"✅ Calculation #{calc_id} deleted")
            
            session.close()
            return True
        else:
            print(f"❌ Calculation #{calc_id} not found")
            return False
            
    except Exception as e:
        print(f"❌ Error deleting calculation: {e}")
        return False

def test_database_stats():
    """Show database statistics"""
    print("\n📊 Database Statistics...")
    
    try:
        session = get_session()
        
        # Count records
        calc_count = session.query(Calculation).count()
        template_count = session.query(Template).count()
        
        print(f"✅ Database contains:")
        print(f"  - {calc_count} calculations")
        print(f"  - {template_count} templates")
        
        # Get latest calculation
        latest_calc = session.query(Calculation).order_by(Calculation.created_at.desc()).first()
        if latest_calc:
            print(f"  - Latest calculation: {latest_calc.company_name} ({latest_calc.created_at})")
        
        # Get most used template
        most_used = session.query(Template).order_by(Template.usage_count.desc()).first()
        if most_used:
            print(f"  - Most used template: {most_used.name} ({most_used.usage_count} uses)")
        
        session.close()
        return True
        
    except Exception as e:
        print(f"❌ Error getting statistics: {e}")
        return False

def main():
    """Run all database tests"""
    print("🚀 CHILEAN E-COMMERCE SALES TOOLKIT - DATABASE INTEGRATION TEST")
    print("=" * 70)
    
    # Track test results
    results = []
    
    # Test 1: Connection
    results.append(("Database Connection", test_connection()))
    
    # Test 2: Create Calculation
    calc_id = test_create_calculation()
    results.append(("Create Calculation", calc_id is not None))
    
    # Test 3: Read Calculations
    results.append(("Read Calculations", test_read_calculations()))
    
    # Test 4: Update Calculation
    results.append(("Update Calculation", test_update_calculation(calc_id)))
    
    # Test 5: Create Template
    template_id = test_create_template()
    results.append(("Create Template", template_id is not None))
    
    # Test 6: Read Templates
    results.append(("Read Templates", test_read_templates()))
    
    # Test 7: Database Statistics
    results.append(("Database Statistics", test_database_stats()))
    
    # Test 8: Delete Calculation (cleanup)
    results.append(("Delete Calculation", test_delete_calculation(calc_id)))
    
    # Print summary
    print("\n" + "=" * 70)
    print("📋 TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\n🎯 Results: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("\n🎉 All database integration tests passed!")
        print("✅ Database is fully functional and ready for production")
    else:
        print(f"\n⚠️ {total - passed} tests failed")
        print("Please review the errors above")
    
    # Show database location
    print("\n📁 Database Location:")
    print(f"  SQLite: data/roi_calculator.db")
    print("  To switch to PostgreSQL, set DATABASE_URL environment variable")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
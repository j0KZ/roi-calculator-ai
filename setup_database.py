#!/usr/bin/env python3
"""
Database setup script for ROI Calculator
Creates tables and adds sample templates
"""

import os
import sys
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from database.connection import init_database, get_session
from database.models import Calculation, Template, ComparisonScenario

def setup_database():
    """Setup database and create initial data"""
    
    print("ROI Calculator Database Setup")
    print("=" * 50)
    
    # Check for PostgreSQL URL
    pg_url = os.environ.get('DATABASE_URL')
    
    if pg_url:
        print(f"Using PostgreSQL: {pg_url}")
        db = init_database(pg_url)
    else:
        print("Using SQLite (default)")
        print("To use PostgreSQL, set DATABASE_URL environment variable:")
        print("  export DATABASE_URL='postgresql://username:password@localhost/roi_calculator'")
        db = init_database()
    
    # Test connection
    if db.test_connection():
        print("✓ Database connection successful")
    else:
        print("✗ Database connection failed")
        return False
    
    # Initialize database
    db.init_db()
    print("✓ Database tables created")
    
    # Create sample templates
    session = get_session()
    
    try:
        # Check if templates already exist
        existing_templates = session.query(Template).count()
        
        if existing_templates == 0:
            print("\nCreating sample templates...")
            
            # Small Business Template
            small_template = Template(
                name="Small Business",
                description="Template for small businesses with annual revenue around $500K",
                category="small_business",
                template_data=json.dumps({
                    "annual_revenue": 500000,
                    "monthly_orders": 200,
                    "avg_order_value": 208,
                    "labor_costs": 8000,
                    "shipping_costs": 3000,
                    "error_costs": 1500,
                    "inventory_costs": 2000,
                    "service_investment": 15000
                })
            )
            
            # Medium Business Template
            medium_template = Template(
                name="Medium Business",
                description="Template for medium businesses with annual revenue around $2M",
                category="medium_business",
                template_data=json.dumps({
                    "annual_revenue": 2000000,
                    "monthly_orders": 800,
                    "avg_order_value": 208,
                    "labor_costs": 25000,
                    "shipping_costs": 10000,
                    "error_costs": 4000,
                    "inventory_costs": 6000,
                    "service_investment": 35000
                })
            )
            
            # Large Business Template
            large_template = Template(
                name="Large Business",
                description="Template for large businesses with annual revenue around $5M",
                category="large_business",
                template_data=json.dumps({
                    "annual_revenue": 5000000,
                    "monthly_orders": 2000,
                    "avg_order_value": 208,
                    "labor_costs": 60000,
                    "shipping_costs": 25000,
                    "error_costs": 8000,
                    "inventory_costs": 15000,
                    "service_investment": 75000
                })
            )
            
            session.add(small_template)
            session.add(medium_template)
            session.add(large_template)
            session.commit()
            
            print("✓ Sample templates created")
        else:
            print(f"✓ Templates already exist ({existing_templates} found)")
        
        # Display database info
        print("\nDatabase Summary:")
        print(f"  Templates: {session.query(Template).count()}")
        print(f"  Calculations: {session.query(Calculation).count()}")
        print(f"  Scenarios: {session.query(ComparisonScenario).count()}")
        
    except Exception as e:
        print(f"Error setting up database: {e}")
        session.rollback()
        return False
    finally:
        session.close()
    
    print("\n✓ Database setup complete!")
    print("\nTo switch between databases:")
    print("  SQLite (default): Just run the application")
    print("  PostgreSQL: export DATABASE_URL='postgresql://user:pass@localhost/dbname'")
    
    return True

if __name__ == "__main__":
    setup_database()
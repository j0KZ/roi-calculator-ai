#!/usr/bin/env python3
"""
Initialize or reset the database for the ROI Calculator
"""

import os
import sys
from pathlib import Path

# Add the src directory to path
sys.path.insert(0, str(Path(__file__).parent))

from database.connection import DatabaseConnection
from database.models import Base

def init_database():
    """Initialize the database with all tables"""
    print("Initializing ROI Calculator database...")
    
    # Create data directory if it doesn't exist
    data_dir = Path(__file__).parent.parent / 'data'
    data_dir.mkdir(exist_ok=True)
    
    # Initialize database connection
    db = DatabaseConnection()
    
    # Test connection
    if db.test_connection():
        print("✓ Database connection successful")
    else:
        print("✗ Database connection failed")
        return False
    
    # Drop all existing tables (for clean slate)
    print("Dropping existing tables...")
    Base.metadata.drop_all(bind=db.engine)
    print("✓ Existing tables dropped")
    
    # Create all tables
    print("Creating new tables...")
    Base.metadata.create_all(bind=db.engine)
    print("✓ Database tables created")
    
    # List created tables
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print(f"\nCreated tables: {', '.join(tables)}")
    
    # Verify Template table has all required columns
    template_columns = [col['name'] for col in inspector.get_columns('templates')]
    print(f"\nTemplate table columns: {', '.join(template_columns)}")
    
    required_columns = ['id', 'name', 'description', 'category', 'template_data', 
                       'tags', 'meta_data', 'is_public', 'created_by', 'industry',
                       'business_size', 'usage_count', 'created_at', 'updated_at']
    
    missing_columns = set(required_columns) - set(template_columns)
    if missing_columns:
        print(f"⚠ Warning: Missing columns in Template table: {', '.join(missing_columns)}")
    else:
        print("✓ All required columns present in Template table")
    
    return True

if __name__ == "__main__":
    if init_database():
        print("\n✅ Database initialization complete!")
    else:
        print("\n❌ Database initialization failed!")
        sys.exit(1)
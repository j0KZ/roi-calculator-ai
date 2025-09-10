#!/usr/bin/env python3
"""
Database migration script for Market Data features
Creates new tables for market data and benchmarks
"""

import os
import sys
from datetime import datetime

# Add the src directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.connection import get_session, get_db
from database.models import Base, MarketData, MarketBenchmark
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_database():
    """Run database migration to add market data tables"""
    try:
        logger.info("Starting database migration for market data features...")
        
        # Create all tables (this will only create missing ones)
        db_conn = get_db()
        Base.metadata.create_all(db_conn.engine)
        
        logger.info("Migration completed successfully!")
        
        # Verify tables exist
        with get_session() as session:
            # Check MarketData table
            try:
                result = session.execute("SELECT COUNT(*) FROM market_data")
                count = result.scalar()
                logger.info(f"MarketData table exists with {count} records")
            except Exception as e:
                logger.error(f"Error checking MarketData table: {e}")
                
            # Check MarketBenchmark table  
            try:
                result = session.execute("SELECT COUNT(*) FROM market_benchmarks")
                count = result.scalar()
                logger.info(f"MarketBenchmark table exists with {count} records")
            except Exception as e:
                logger.error(f"Error checking MarketBenchmark table: {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return False

if __name__ == "__main__":
    success = migrate_database()
    sys.exit(0 if success else 1)
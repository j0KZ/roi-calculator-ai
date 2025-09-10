#!/usr/bin/env python3
"""
Migration script to move data from JSON files to PostgreSQL database
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
import logging

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.connection import get_session
from src.database.repository import (
    CompanyRepository, CalculationRepository,
    ExchangeRateRepository, MetricsRepository
)
from src.database.models import CalculationType, CompanySize, Industry
from contextlib import contextmanager

@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = get_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataMigrator:
    """Migrates data from JSON files to PostgreSQL"""
    
    def __init__(self):
        self.data_dir = Path('data/history')
        self.migrated_count = 0
        self.failed_count = 0
    
    def migrate_all(self):
        """Run complete migration"""
        logger.info("Starting data migration from JSON to PostgreSQL...")
        
        # Migrate calculation history
        self.migrate_calculations()
        
        # Migrate any cached exchange rates
        self.migrate_exchange_rates()
        
        # Summary
        logger.info(f"Migration complete!")
        logger.info(f"Migrated: {self.migrated_count} records")
        logger.info(f"Failed: {self.failed_count} records")
    
    def migrate_calculations(self):
        """Migrate calculation history files"""
        if not self.data_dir.exists():
            logger.warning(f"Data directory not found: {self.data_dir}")
            return
        
        json_files = list(self.data_dir.glob('*.json'))
        logger.info(f"Found {len(json_files)} history files to migrate")
        
        for json_file in json_files:
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                
                # Process each calculation in the file
                if isinstance(data, list):
                    for calc in data:
                        self.migrate_single_calculation(calc)
                else:
                    self.migrate_single_calculation(data)
                
                # Optionally rename processed file
                processed_file = json_file.with_suffix('.json.migrated')
                json_file.rename(processed_file)
                
            except Exception as e:
                logger.error(f"Failed to migrate {json_file}: {e}")
                self.failed_count += 1
    
    def migrate_single_calculation(self, calc_data: dict):
        """Migrate a single calculation record"""
        try:
            with session_scope() as session:
                # Get or create company
                company_repo = CompanyRepository(session)
                
                # Extract company info (or use defaults)
                company_name = calc_data.get('company_name', 'Unknown Company')
                company_email = calc_data.get('email', f"{company_name.lower().replace(' ', '_')}@example.com")
                
                company = company_repo.get_by_email(company_email)
                if not company:
                    company = company_repo.create(
                        name=company_name,
                        email=company_email,
                        industry=calc_data.get('industry', 'other'),
                        size=calc_data.get('size', 'medium')
                    )
                
                # Determine calculation type
                calc_type_str = calc_data.get('type', 'roi').upper()
                try:
                    calc_type = CalculationType[calc_type_str]
                except KeyError:
                    calc_type = CalculationType.ROI
                
                # Save calculation
                calc_repo = CalculationRepository(session)
                
                inputs = calc_data.get('inputs', {})
                results = calc_data.get('results', {})
                
                calculation = calc_repo.save_calculation(
                    company_id=company.id,
                    calc_type=calc_type,
                    inputs=inputs,
                    results=results,
                    metadata=calc_data.get('metadata', {}),
                    calculation_time_ms=calc_data.get('calculation_time_ms', 0)
                )
                
                # If it's an ROI calculation, save details
                if calc_type == CalculationType.ROI and 'roi_percentage' in results:
                    calc_repo.save_roi_details(
                        calculation_id=calculation.id,
                        investment=inputs.get('investment_amount_clp', 0),
                        revenue=inputs.get('annual_revenue_clp', 0),
                        months=inputs.get('implementation_months', 12),
                        roi=results.get('roi_percentage', 0),
                        payback=results.get('payback_months', 0),
                        projections=results.get('projections', {}),
                        scenarios=results.get('scenarios', {})
                    )
                
                self.migrated_count += 1
                
                if self.migrated_count % 10 == 0:
                    logger.info(f"Migrated {self.migrated_count} calculations...")
                
        except Exception as e:
            logger.error(f"Failed to migrate calculation: {e}")
            self.failed_count += 1
    
    def migrate_exchange_rates(self):
        """Migrate cached exchange rates if available"""
        exchange_file = Path('data/exchange_rates.json')
        
        if not exchange_file.exists():
            logger.info("No exchange rate cache found")
            return
        
        try:
            with open(exchange_file, 'r') as f:
                rates = json.load(f)
            
            with session_scope() as session:
                rate_repo = ExchangeRateRepository(session)
                
                for pair, rate_data in rates.items():
                    if '_' in pair:
                        from_curr, to_curr = pair.split('_')
                        rate_repo.save_rate(
                            from_currency=from_curr,
                            to_currency=to_curr,
                            rate=rate_data.get('rate', 0),
                            source=rate_data.get('source', 'cache')
                        )
                        self.migrated_count += 1
            
            logger.info(f"Migrated {len(rates)} exchange rates")
            
        except Exception as e:
            logger.error(f"Failed to migrate exchange rates: {e}")

def main():
    """Run migration"""
    migrator = DataMigrator()
    
    # Confirm before proceeding
    print("\n" + "="*50)
    print("JSON to PostgreSQL Data Migration")
    print("="*50)
    print("\nThis will migrate all data from JSON files to PostgreSQL.")
    print("Original files will be renamed with .migrated extension.")
    print("\nData directory: data/history/")
    
    response = input("\nProceed with migration? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        migrator.migrate_all()
        print("\n✅ Migration complete!")
    else:
        print("\n❌ Migration cancelled")

if __name__ == "__main__":
    main()
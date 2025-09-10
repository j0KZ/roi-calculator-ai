# Phase 2: Database Migration Guide

## Overview

This guide provides step-by-step instructions for migrating from JSON file storage to PostgreSQL database.

## Prerequisites

### 1. Install PostgreSQL

#### macOS
```bash
brew install postgresql
brew services start postgresql
```

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

#### Windows
Download and install from: https://www.postgresql.org/download/windows/

### 2. Create Database

```bash
# Access PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE roi_calculator;

# Create user (optional)
CREATE USER roi_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE roi_calculator TO roi_user;

# Exit
\q
```

### 3. Set Environment Variables

Update `.env` file:
```env
DATABASE_URL=postgresql://roi_user:secure_password@localhost:5432/roi_calculator
```

## Database Schema

### Tables Created

1. **companies** - Store company/organization information
   - UUID primary key
   - Email (unique)
   - Industry, size, country
   - Timestamps

2. **calculations** - General calculation history
   - Links to company
   - Type (ROI, Cost, Tax, etc.)
   - Input/output JSON
   - Performance metrics

3. **roi_calculations** - Detailed ROI results
   - Investment amounts
   - ROI percentages
   - Projections (5 years)
   - Scenarios

4. **cost_optimizations** - Cost optimization results
   - Current vs optimized costs
   - Savings calculations
   - ML model metrics

5. **exchange_rates** - Currency exchange rate cache
   - Currency pairs
   - Rates with timestamps
   - Source tracking

6. **user_sessions** - Session management
   - Session tokens
   - Preferences
   - Activity tracking

7. **performance_metrics** - Application performance
   - Operation timings
   - Resource usage
   - Error tracking

8. **audit_logs** - Audit trail
   - All actions logged
   - Changes tracked
   - IP addresses

## Migration Steps

### 1. Initialize Database

```bash
# Create tables
python3 -c "
from src.database.connection import db
db.init_database()
print('Database initialized!')
"
```

### 2. Create Initial Migration

```bash
# Initialize Alembic
alembic init src/database/migrations

# Create first migration
alembic revision --autogenerate -m "Initial schema"

# Apply migration
alembic upgrade head
```

### 3. Migrate Existing Data

```python
# Run migration script
python3 scripts/migrate_json_to_db.py
```

### 4. Verify Migration

```bash
# Check database
psql -U roi_user -d roi_calculator

# List tables
\dt

# Check data
SELECT COUNT(*) FROM companies;
SELECT COUNT(*) FROM calculations;
```

## Using the Database

### Repository Pattern

```python
from src.database import session_scope
from src.database.repository import CompanyRepository, CalculationRepository

# Create company
with session_scope() as session:
    company_repo = CompanyRepository(session)
    company = company_repo.create(
        name="Test Company",
        email="test@example.com",
        industry="ecommerce",
        size="medium"
    )

# Save calculation
with session_scope() as session:
    calc_repo = CalculationRepository(session)
    calculation = calc_repo.save_calculation(
        company_id=company.id,
        calc_type=CalculationType.ROI,
        inputs={"investment": 1000000},
        results={"roi": 186.5},
        calculation_time_ms=45.2
    )
```

### Direct Session Usage

```python
from src.database import get_session
from src.database.models import Company

session = get_session()
try:
    companies = session.query(Company).all()
    for company in companies:
        print(f"{company.name}: {company.email}")
finally:
    session.close()
```

## Performance Optimizations

### 1. Connection Pooling
- Pool size: 20 connections
- Max overflow: 40 connections
- Pre-ping enabled for connection verification

### 2. Indexes
- Email lookups
- Company ID foreign keys
- Calculation types
- Timestamps for time-based queries

### 3. Caching Integration
- Database results cached in Redis/memory
- TTL-based expiration
- Cache invalidation on updates

## Monitoring

### Database Statistics

```python
from src.database.connection import db

stats = db.get_db_stats()
print(f"Companies: {stats['companies']}")
print(f"Calculations: {stats['calculations']}")
print(f"Database: {stats['engine']}")
```

### Performance Metrics

```python
from src.database.repository import MetricsRepository

with session_scope() as session:
    metrics_repo = MetricsRepository(session)
    summary = metrics_repo.get_metrics_summary(hours=24)
    
    for operation, stats in summary.items():
        print(f"{operation}: {stats['avg_duration_ms']:.2f}ms")
```

## Backup & Recovery

### Backup Database

```bash
# Full backup
pg_dump -U roi_user -d roi_calculator > backup_$(date +%Y%m%d).sql

# Compressed backup
pg_dump -U roi_user -d roi_calculator | gzip > backup_$(date +%Y%m%d).sql.gz
```

### Restore Database

```bash
# From SQL file
psql -U roi_user -d roi_calculator < backup_20250910.sql

# From compressed file
gunzip -c backup_20250910.sql.gz | psql -U roi_user -d roi_calculator
```

## Troubleshooting

### Connection Issues

1. Check PostgreSQL is running:
```bash
pg_isready
```

2. Verify connection string:
```python
from src.database.connection import db
print(db.test_connection())
```

3. Check logs:
```bash
tail -f logs/process_manager.log
```

### Migration Issues

1. Reset migrations:
```bash
alembic downgrade base
alembic upgrade head
```

2. Manual table creation:
```python
from src.database.models import Base
from src.database.connection import db
Base.metadata.create_all(bind=db.engine)
```

## Security Considerations

1. **Never commit credentials** - Use environment variables
2. **Use SSL in production** - Add `?sslmode=require` to connection string
3. **Implement row-level security** - For multi-tenant access
4. **Regular backups** - Automate daily backups
5. **Monitor access** - Check audit_logs table

## Next Steps

After completing database migration:

1. ✅ Test all calculator functions with database
2. ✅ Verify data persistence
3. ✅ Check performance metrics
4. ✅ Implement automated backups
5. ⏭️ Move to Phase 3: AI/ML Enhancement
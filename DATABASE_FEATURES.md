# Database Features Documentation 

## Overview
The ROI Calculator includes comprehensive database integration for persistent storage of calculations, templates, and analytics data. The system supports both SQLite (default) and PostgreSQL databases with automatic migration handling.

## New Features

### 1. Database Storage
- **SQLite by default**: Works out of the box, no installation required
- **PostgreSQL ready**: Can switch to PostgreSQL by setting `DATABASE_URL` environment variable
- **Automatic setup**: Database tables created automatically on first run

### 2. Save Calculations
- Click "Save Calculation" button after any calculation
- Add optional notes to document the calculation
- All inputs and results stored securely in database
- Company name, dates, and all financial metrics preserved

### 3. Calculation History Page
- Access via "View History" button or `/history` URL
- View all saved calculations in elegant card layout
- Search by company name with real-time filtering
- Pagination for large datasets
- View detailed calculation results
- Delete unwanted calculations
- Regenerate PDFs from saved data
- **Compare Mode**: Select 2-3 calculations for side-by-side analysis
- **Export to Analytics**: Send calculations to What-If or Sensitivity tools

### 4. Templates System
- Pre-loaded templates for Small, Medium, and Large businesses
- Templates stored in database for consistency
- Accessible via API for all analytics tools
- Used as baseline scenarios in What-If Analysis
- Quick-start options for new users

## Database Schema

### Calculations Table
- `id`: Unique identifier
- `company_name`: Optional company name
- `created_at`, `updated_at`: Timestamps
- `annual_revenue`, `monthly_orders`, `avg_order_value`: Business metrics
- `labor_costs`, `shipping_costs`, `error_costs`, `inventory_costs`: Current costs
- `service_investment`: Investment amount
- `results`: JSON field with complete calculation results
- `notes`: Optional text notes
- `tags`: Comma-separated tags for categorization

### Templates Table
- Pre-configured calculation templates
- Category-based organization
- Usage tracking

### Comparison Scenarios Table
- Store multiple calculations for comparison
- Advanced analytics capabilities
- Tracks scenario variations and what-if results
- Links calculations for comparative analysis

## Setup Instructions

### Using SQLite (Default)
```bash
# Just run the setup script
python setup_database.py

# Start the application
cd src && python web_interface.py
```

### Using PostgreSQL

#### Option 1: Install via Homebrew
```bash
# Fix permissions if needed
sudo chown -R $(whoami) /usr/local/share/zsh /usr/local/share/zsh/site-functions

# Install PostgreSQL
brew install postgresql@16

# Start PostgreSQL service
brew services start postgresql@16

# Create database
createdb roi_calculator

# Set environment variable
export DATABASE_URL='postgresql://username:password@localhost/roi_calculator'

# Run setup
python setup_database.py
```

#### Option 2: Install via Postgres.app
1. Download from https://postgresapp.com/downloads.html
2. Move to Applications folder
3. Launch and initialize
4. Create database: `createdb roi_calculator`
5. Set environment variable and run setup

## API Endpoints

### Core Database Operations

#### Save Calculation
`POST /save`
```json
{
  "company_name": "Example Corp",
  "annual_revenue": 1000000,
  "monthly_orders": 500,
  ...
  "results": {...},
  "notes": "Optional notes",
  "tags": "tag1,tag2"
}
```

#### Get Calculations
`GET /api/calculations?limit=10&offset=0&search=company`

#### Get Single Calculation
`GET /api/calculations/{id}`

#### Delete Calculation
`DELETE /api/calculations/{id}`

#### Update Calculation
`PUT /api/calculations/{id}`

### Analytics Endpoints

#### Compare Calculations
`POST /api/compare`
```json
{
  "ids": [1, 2, 3]
}
```

#### What-If Analysis
`POST /api/whatif/calculate`
```json
{
  "baseline": {...},
  "adjustments": {
    "annual_revenue": 1.2,
    "labor_costs": 0.8
  }
}
```

#### Sensitivity Analysis
`POST /api/sensitivity/analyze`
```json
{
  "calculation_data": {...},
  "variables": ["annual_revenue", "labor_costs"],
  "range": 0.5
}
```

#### Get Templates
`GET /api/templates`

## Features in Action

### Saving a Calculation
1. Complete an ROI calculation on the main page
2. Click "Save Calculation" button in results section
3. Enter company name, notes, and tags in modal
4. Calculation is saved to database with all metadata

### Viewing History
1. Click "View History" button or navigate to `/history`
2. Browse all saved calculations in card format
3. Use search to find specific companies
4. Click "View" to see full details
5. Click trash icon to delete
6. Enable "Compare Mode" to select multiple calculations
7. Send to analytics tools for deeper analysis

### Database Migration
The system automatically handles database migrations:
- Creates tables if they don't exist
- Preserves existing data
- Compatible with both SQLite and PostgreSQL

## Security Notes
- Database credentials should be stored in environment variables
- Never commit `.env` files to version control
- Use strong passwords for PostgreSQL in production
- Regular backups recommended for production use

## Performance
- SQLite: Perfect for single-user or small team use
- PostgreSQL: Recommended for multi-user or production environments
- Indexed searches for fast query performance
- Pagination prevents loading too much data at once

## Advanced Features (v2.0)

### Implemented
- ✅ Calculation comparison with visual indicators
- ✅ What-if scenario modeling with database persistence
- ✅ Sensitivity analysis results storage
- ✅ Advanced search and filtering
- ✅ Tags and notes for organization
- ✅ Bulk operations (delete multiple)

### Planned Enhancements
- Export calculations to CSV/Excel
- Import bulk calculations from spreadsheets
- Automated report scheduling
- Team collaboration with sharing
- Calculation versioning and history
- Audit trail for changes

## Troubleshooting

### Database Connection Issues
```bash
# Test SQLite connection
python -c "from src.database.connection import get_db; print(get_db().test_connection())"

# For PostgreSQL, verify connection string
echo $DATABASE_URL
```

### Reset Database
```bash
# Delete SQLite database
rm data/roi_calculator.db

# Recreate tables
python setup_database.py
```

## Support
For issues or questions about database features, check the logs in `app.log` or run with debug mode enabled.
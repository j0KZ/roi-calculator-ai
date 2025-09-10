# ROI Calculator API Documentation Summary - Version 3.0

## Overview

The ROI Calculator provides a comprehensive RESTful API for all business analytics features. This document provides a quick reference for all available endpoints.

## Base URL
```
http://localhost:8000
```

## Authentication
Currently, the API operates without authentication. Authentication will be added in v3.1.

## Core Calculation Endpoints

### Calculate ROI
- **POST** `/calculate`
- Calculate ROI with multi-currency and tax support
- **Body**: Calculation parameters including currency and tax settings
- **Response**: Complete ROI analysis with tax impact

### Save Calculation
- **POST** `/save`
- Save calculation results to database
- **Body**: ROI results and metadata
- **Response**: Saved calculation with ID

## Multi-Currency Endpoints

### Convert Currency
- **POST** `/convert-currency`
- Convert ROI calculation to different currency
- **Body**: `{"roi_results": {}, "target_currency": "EUR"}`
- **Response**: Converted calculation results

### Supported Currencies
- **GET** `/api/supported-currencies`
- List all supported currencies and current rates
- **Response**: Currency list with symbols and exchange rates

## Tax Calculation Endpoints

### Calculate Tax Impact
- **POST** `/calculate-tax-impact`
- Analyze tax implications on ROI
- **Body**: `{"roi_results": {}, "tax_config": {}}`
- **Response**: Tax-adjusted ROI analysis

### Tax Jurisdictions
- **GET** `/api/tax-jurisdictions`
- List available tax jurisdictions and regions
- **Response**: Hierarchical list of supported tax regions

## AI Optimization Endpoints

### Cost Optimization Analysis
- **POST** `/optimize-costs`
- AI-powered cost optimization recommendations
- **Body**: `{"roi_results": {}}`
- **Response**: Optimization report with recommendations

### Industry Benchmarks
- **GET** `/api/benchmarks/{industry}`
- Get industry benchmark data
- **Response**: Benchmark metrics by company size

## Document Generation Endpoints

### Generate PDF Report
- **POST** `/generate-pdf`
- Generate traditional PDF report
- **Body**: ROI results
- **Response**: PDF file path

### Generate Business Proposal
- **POST** `/generate-proposal`
- Generate professional business proposal
- **Body**: `{"roi_results": {}, "format": "all", "template": "professional"}`
- **Response**: Generated proposal files (PDF/Word/HTML)

### Generate PowerPoint
- **POST** `/generate-powerpoint`
- Create PowerPoint presentation
- **Body**: ROI results and presentation config
- **Response**: PowerPoint file path

## Break-Even Analysis Endpoints

### Calculate Break-Even
- **POST** `/calculate-breakeven`
- Comprehensive break-even analysis
- **Body**: ROI results and scenarios
- **Response**: Break-even analysis with multiple scenarios

### Break-Even Scenarios
- **GET** `/api/breakeven-scenarios`
- List available break-even scenarios
- **Response**: Predefined scenario configurations

## Template Management Endpoints

### List Templates
- **GET** `/api/templates`
- List all available templates
- **Query Parameters**: 
  - `category`: Filter by category
  - `tags`: Filter by tags
  - `include_predefined`: Include system templates
- **Response**: Template list with metadata

### Create Template
- **POST** `/api/templates`
- Create new custom template
- **Body**: Template data and metadata
- **Response**: Created template with ID

### Get Template
- **GET** `/api/templates/{id}`
- Retrieve specific template
- **Response**: Template data and metadata

### Update Template
- **PUT** `/api/templates/{id}`
- Update existing template
- **Body**: Updated template data
- **Response**: Updated template

### Delete Template
- **DELETE** `/api/templates/{id}`
- Delete template
- **Response**: Success confirmation

### Clone Template
- **POST** `/api/templates/{id}/clone`
- Clone existing template
- **Body**: `{"new_name": "Template Name"}`
- **Response**: Cloned template with new ID

## Batch Processing Endpoints

### Batch Calculate
- **POST** `/api/batch-process`
- Process multiple calculations
- **Body**: Array of calculation parameters
- **Response**: Batch processing results

### Batch Status
- **GET** `/api/batch-status/{batch_id}`
- Check batch processing status
- **Response**: Progress and results

## Calculation Management Endpoints

### List Calculations
- **GET** `/api/calculations`
- List saved calculations
- **Query Parameters**:
  - `limit`: Number of results
  - `offset`: Pagination offset
  - `sort`: Sort order
- **Response**: Paginated calculation list

### Get Calculation
- **GET** `/api/calculations/{id}`
- Retrieve specific calculation
- **Response**: Complete calculation data

### Delete Calculation
- **DELETE** `/api/calculations/{id}`
- Delete saved calculation
- **Response**: Success confirmation

### Compare Calculations
- **POST** `/api/compare`
- Compare multiple calculations
- **Body**: Array of calculation IDs
- **Response**: Comparison analysis

## Analysis Endpoints

### What-If Analysis
- **POST** `/api/whatif/calculate`
- Scenario modeling with variable adjustments
- **Body**: Base calculation and variable modifications
- **Response**: What-if analysis results

### Sensitivity Analysis
- **POST** `/api/sensitivity/analyze`
- Monte Carlo sensitivity analysis
- **Body**: Calculation parameters and analysis config
- **Response**: Sensitivity analysis with tornado diagrams

## Version Control Endpoints

### Calculation History
- **GET** `/api/calculations/{id}/history`
- Get calculation version history
- **Response**: List of calculation versions

### Compare Versions
- **POST** `/api/calculations/{id}/compare-versions`
- Compare different versions of a calculation
- **Body**: `{"version_ids": [1, 2]}`
- **Response**: Version comparison analysis

## Market Data Endpoints

### Market Insights
- **GET** `/api/market-insights`
- Get market data and trends
- **Query Parameters**:
  - `industry`: Industry filter
  - `region`: Geographic region
- **Response**: Market analysis data

### Exchange Rates
- **GET** `/api/exchange-rates`
- Current exchange rates
- **Response**: Real-time currency conversion rates

## File Download Endpoints

### Download File
- **GET** `/download/{filename}`
- Download generated files (PDFs, proposals, presentations)
- **Response**: File download

### List Downloads
- **GET** `/api/downloads`
- List available download files
- **Response**: File list with metadata

## Web Interface Endpoints

### Main Calculator
- **GET** `/`
- Main calculator interface

### Analysis Tools
- **GET** `/compare` - Comparison analysis
- **GET** `/whatif` - What-if scenarios
- **GET** `/sensitivity` - Sensitivity analysis
- **GET** `/optimization` - Cost optimization dashboard
- **GET** `/templates` - Template management
- **GET** `/history` - Calculation history

### Configuration
- **GET** `/currency-tax-config` - Currency and tax configuration
- **GET** `/batch` - Batch processing interface
- **GET** `/versions` - Version control interface

## Error Responses

All endpoints return standardized error responses:

```json
{
  "error": true,
  "message": "Error description",
  "details": "Additional error details",
  "error_code": "ERROR_CODE",
  "timestamp": "2024-12-05T10:30:00Z"
}
```

### Common Error Codes
- `INVALID_INPUT` - Invalid request parameters
- `CALCULATION_ERROR` - Error in ROI calculation
- `CURRENCY_ERROR` - Currency conversion failed
- `TAX_ERROR` - Tax calculation failed
- `TEMPLATE_ERROR` - Template operation failed
- `FILE_ERROR` - File generation failed
- `DATABASE_ERROR` - Database operation failed

## Request/Response Examples

### Calculate ROI with Multi-Currency
```bash
curl -X POST http://localhost:8000/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Example Corp",
    "annual_revenue": 2000000,
    "monthly_orders": 5000,
    "avg_order_value": 33.33,
    "labor_costs": 8000,
    "shipping_costs": 5000,
    "error_costs": 2000,
    "inventory_costs": 3000,
    "service_investment": 50000,
    "currency": "USD",
    "target_currency": "EUR",
    "tax_jurisdiction": "US",
    "tax_region": "CA"
  }'
```

### Generate Business Proposal
```bash
curl -X POST http://localhost:8000/generate-proposal \
  -H "Content-Type: application/json" \
  -d '{
    "roi_results": {...},
    "format": "pdf",
    "template": "professional",
    "company_branding": {
      "name": "Example Corp",
      "primary_color": "#2E5BBA"
    }
  }'
```

### Cost Optimization Analysis
```bash
curl -X POST http://localhost:8000/optimize-costs \
  -H "Content-Type: application/json" \
  -d '{
    "roi_results": {...},
    "industry": "ecommerce",
    "include_benchmarks": true
  }'
```

## Rate Limiting

- **Standard Endpoints**: 1000 requests per hour per IP
- **Heavy Operations** (document generation): 100 requests per hour per IP
- **Batch Processing**: 10 requests per hour per IP

## Data Formats

### Dates
All dates are in ISO 8601 format: `YYYY-MM-DDTHH:MM:SSZ`

### Currency
All monetary values are returned as numbers with 2 decimal places.

### Percentages
Percentages are returned as decimals (0.15 = 15%).

## Changelog

### v3.0.0
- Added 20+ new endpoints for v3.0 features
- Multi-currency support across all endpoints
- Tax calculation integration
- AI optimization endpoints
- Enhanced document generation
- Batch processing capabilities

### v2.0.0
- Added comparison and analysis endpoints
- Database integration
- Enhanced error handling

### v1.0.0
- Initial API release
- Basic calculation endpoints

---

For detailed API documentation with full request/response schemas, see the complete API documentation at `/api/docs` when the application is running.

*Last updated: December 2024*
# Project Structure

## 📁 Directory Organization

```
roi-calculator-ai/
│
├── 📱 app.py                    # Main Streamlit application entry point
├── 📖 README.md                 # Project documentation (AI-focused)
├── 📋 requirements.txt          # Python dependencies
├── 🔧 setup.py                 # Package setup configuration
├── 🐳 Dockerfile               # Docker configuration
├── 🔒 .gitignore              # Git ignore rules
├── 🎨 .streamlit/             # Streamlit configuration
│   └── config.toml           # Theme and settings
│
├── 📂 src/                    # Source code
│   ├── roi_calculator.py     # Core ROI calculation engine
│   ├── cost_optimizer.py     # AI-powered cost optimization
│   ├── currency_converter.py # Real-time currency conversion
│   ├── tax_calculator.py     # Tax calculations
│   ├── market_data_service.py # Market data integration
│   ├── pdf_generator.py      # PDF report generation
│   ├── powerpoint_generator.py # PowerPoint export
│   └── database/             # Database layer
│       ├── models.py         # SQLAlchemy models
│       ├── connection.py     # Database connection
│       ├── repository.py     # Data access layer
│       └── migrations/       # Alembic migrations
│
├── 📂 pages/                  # Streamlit pages
│   ├── roi_calculator.py     # ROI calculation page
│   ├── cost_optimizer.py     # Cost optimization page
│   ├── assessment_tool.py    # Business assessment
│   ├── currency_converter.py # Currency conversion
│   ├── tax_calculator.py     # Tax calculations
│   ├── templates.py          # Template management
│   ├── history.py           # Calculation history
│   └── proposal_generator.py # Proposal generation
│
├── 📂 tests/                  # Test suite
│   ├── test_calculator.py    # Calculator tests
│   ├── test_all_features.py  # Integration tests
│   ├── test_business_tools.py # Business logic tests
│   ├── test_web_application.py # Web app tests
│   ├── test_db_integration.py # Database tests
│   ├── test_web_performance.py # Performance tests
│   └── edge_cases/           # Edge case tests
│       ├── test_chilean_edge_cases.py
│       ├── test_unicode_pdf_edge_cases.py
│       └── test_performance_edge_cases.py
│
├── 📂 docs/                   # Documentation
│   ├── CHANGELOG.md          # Version history
│   ├── guides/               # User guides
│   │   ├── QUICKSTART.md    # Getting started
│   │   ├── CLIENT_DEMO.md   # Demo instructions
│   │   └── ANALYTICS_GUIDE.md # Analytics guide
│   ├── technical/            # Technical docs
│   │   ├── DATABASE_FEATURES.md # Database design
│   │   ├── FEATURES.md      # Feature list
│   │   ├── PERFORMANCE_README.md # Performance guide
│   │   └── ERROR_HANDLING_DOCUMENTATION.md
│   └── archive/              # Historical docs
│       └── phase1-completion-report.md
│
├── 📂 static/                 # Static assets
│   ├── css/                  # Stylesheets
│   └── js/                   # JavaScript files
│
├── 📂 templates/              # HTML templates
│   ├── base.html            # Base template
│   ├── index.html           # Home page
│   └── roi_calculator.html  # Calculator page
│
├── 📂 config/                 # Configuration files
│   ├── currencies.json      # Currency data
│   └── tax_rates.json       # Tax rate data
│
├── 📂 scripts/                # Utility scripts
│   ├── migrate_json_to_db.py # Data migration
│   ├── process_manager.py    # Process management
│   └── health_check.py       # Health monitoring
│
└── 📂 utils/                  # Utility modules
    └── chart_theme.py        # Chart theming
```

## 🎯 Key Files

### Entry Points
- `app.py` - Main Streamlit application
- `run.py` - Alternative runner
- `setup.py` - Package installation

### Core Modules
- `src/roi_calculator.py` - ROI calculation engine with ML predictions
- `src/cost_optimizer.py` - AI-powered optimization algorithms
- `src/database/` - PostgreSQL integration with SQLAlchemy

### Configuration
- `.env` - Environment variables (not in Git)
- `.env.example` - Environment template
- `requirements.txt` - Python dependencies
- `alembic.ini` - Database migration config

### Testing
- `tests/` - Comprehensive test suite
- `tests/edge_cases/` - Edge case testing

### Documentation
- `README.md` - Main project documentation
- `docs/guides/` - User guides
- `docs/technical/` - Technical documentation

## 🚀 Quick Navigation

- **Start here**: `README.md` → `app.py`
- **Core logic**: `src/roi_calculator.py`
- **AI/ML features**: `src/cost_optimizer.py`
- **Database**: `src/database/models.py`
- **Tests**: `tests/test_calculator.py`
- **UI Pages**: `pages/roi_calculator.py`
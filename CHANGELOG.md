# Changelog

All notable changes to the ROI Calculator project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.1.0] - 2024-12-06

### Added
- **Three-Scenario What-If Analysis**: Worst Case / Most Likely / Best Case comparison view
- **PowerPoint Export**: Generate professional presentations with 3 templates (Executive, Sales, Technical)
- **Universal Loader Protection**: 30-second timeout on all API calls with user feedback
- **Scenario Quick Apply**: One-click buttons to apply predefined scenario multipliers
- **Color-Coded Results**: Visual indicators (red/yellow/green) for scenario comparison
- **Speaker Notes**: Automatically generated speaker notes in PowerPoint exports
- **Session Management**: Improved data persistence across pages using sessionStorage

### Changed
- **What-If Layout**: Redesigned to use full width with 3-column grid for variables
- **Template Cards**: Changed from small squares to wide cards for better readability
- **Preset Scenarios**: Now display horizontally for better space utilization
- **Variable Sliders**: Organized in responsive grid layout (3 columns on desktop, 2 on tablet, 1 on mobile)
- **Chart Heights**: Optimized for better visibility (300px default)
- **Navigation Buttons**: Moved to header bars for better accessibility

### Fixed
- **Loading Stuck Issue**: Fixed infinite loading states in What-If analysis
- **PowerPoint Template Selection**: Fixed template selection not working
- **jQuery Dependency**: Removed unnecessary jQuery requirement from PowerPoint export
- **Error Handling**: Added proper error messages and timeout handling
- **Scroll Issues**: Fixed excessive scrolling requirements in What-If analysis
- **API Timeouts**: Implemented 30-second timeout protection on all API calls

### Improved
- **Error Messages**: More user-friendly and actionable error feedback
- **Loading States**: Clear loading indicators with timeout protection
- **Code Organization**: Better separation of concerns in JavaScript modules
- **UI Consistency**: Unified corporate black theme across all pages
- **Performance**: Reduced unnecessary API calls and optimized rendering

## [3.0.0] - 2024-11-15

### Added
- Multi-Currency Support (8+ currencies)
- Tax Calculator with multi-jurisdiction support
- AI-Powered Cost Optimization
- Professional Proposal Generator
- Advanced Template Management System
- Batch Processing Capabilities
- Version Control for Calculations

### Changed
- Enhanced PDF report generation (8 pages)
- Improved database schema with PostgreSQL support
- Updated UI with dark theme

## [2.0.0] - 2024-10-01

### Added
- Advanced Analytics Suite
- Comparison View for multiple calculations
- Sensitivity Analysis with tornado diagrams
- Monte Carlo Simulation (1000 iterations)
- Break-Even Analysis
- What-If Scenario Modeling

### Changed
- Improved calculation engine
- Enhanced visualization capabilities
- Better error handling

## [1.0.0] - 2024-09-01

### Added
- Initial release
- Basic ROI calculations
- PDF report generation
- SQLite database support
- Cost breakdown analysis
- 3-year financial projections

---

## Upcoming Features (Roadmap)

### Version 3.2.0 (Planned)
- Excel export functionality
- API endpoints for third-party integration
- Mobile-responsive improvements
- Real-time collaboration features

### Version 4.0.0 (Future)
- Machine Learning predictions
- Industry-specific templates
- Multi-language support
- Cloud deployment options
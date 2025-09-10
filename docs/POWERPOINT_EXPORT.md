# PowerPoint Export Feature

The ROI Calculator now includes a comprehensive PowerPoint export feature that generates professional presentations from your ROI analysis results.

## Features

### 🎨 Professional Templates
- **Executive**: Clean, minimal design for C-level presentations
- **Sales**: Dynamic, persuasive design for sales presentations  
- **Technical**: Professional design for detailed technical analysis

### 📊 Auto-Generated Content
The PowerPoint presentations automatically include:

1. **Title Slide** - Company branding and presentation details
2. **Executive Summary** - Key ROI metrics and business impact
3. **Current State Analysis** - Cost breakdown and operational challenges
4. **ROI Projections** - 3-year timeline with visualizations
5. **Cost Breakdown** - Detailed savings by category with charts
6. **Savings Timeline** - 36-month projection with growth curves
7. **Implementation Timeline** - Gantt chart with milestones
8. **Risk Assessment** - Risk analysis with mitigation strategies
9. **Next Steps** - Action items and recommendations

### 📈 Data Visualizations
Automatically embedded charts include:
- ROI timeline with cumulative savings
- Cost breakdown donut charts
- 36-month savings projections
- Investment vs returns waterfall chart
- Risk assessment radar chart
- Implementation Gantt chart

### 🎯 Customization Options
- **Company Branding**: Logo, contact info, tagline
- **Color Schemes**: 5 professional color themes
- **Speaker Notes**: Detailed talking points for each slide
- **Content Options**: Toggle charts, timelines, and sections

## Usage

### Via Web Interface
1. Navigate to `/powerpoint` in the web interface
2. Select your ROI calculation data
3. Choose a presentation template
4. Customize company information and colors
5. Generate and download your PowerPoint

### Via API
```python
from powerpoint_generator import PowerPointGenerator

# Your ROI calculation results
results = {
    'inputs': {...},
    'roi_metrics': {...},
    'financial_metrics': {...},
    'projections': {...}
}

# Create generator
generator = PowerPointGenerator(results, company_config)

# Generate presentation
filepath = generator.generate_presentation('executive')
```

### API Endpoints
- `GET /powerpoint` - PowerPoint export page
- `POST /api/generate-powerpoint` - Generate PowerPoint presentation
- `GET /api/powerpoint-templates` - Available templates
- `GET /api/powerpoint-color-schemes` - Available color schemes

## Template Specifications

### Executive Template
- **Target Audience**: C-level executives, board members
- **Design**: Clean, minimal, professional
- **Colors**: Corporate blue theme
- **Font**: Calibri, conservative sizing
- **Focus**: High-level metrics, strategic impact

### Sales Template  
- **Target Audience**: Sales prospects, decision makers
- **Design**: Dynamic, engaging, persuasive
- **Colors**: Modern red/teal theme
- **Font**: Segoe UI, larger text
- **Focus**: Benefits, ROI, competitive advantage

### Technical Template
- **Target Audience**: IT teams, technical stakeholders
- **Design**: Professional, detailed, data-focused
- **Colors**: Purple/tech theme
- **Font**: Arial, compact layout
- **Focus**: Implementation details, technical metrics

## Color Schemes

### Corporate Blue
- Primary: `#1B365D` (Dark Blue)
- Secondary: `#5D737E` (Gray Blue)  
- Accent: `#00B894` (Teal)

### Modern Red
- Primary: `#FF6B6B` (Coral Red)
- Secondary: `#4ECDC4` (Turquoise)
- Accent: `#FFE66D` (Yellow)

### Tech Purple
- Primary: `#6C5CE7` (Purple)
- Secondary: `#A29BFE` (Light Purple)
- Accent: `#00B894` (Teal)

### Finance Green
- Primary: `#2D3436` (Dark Gray)
- Secondary: `#636E72` (Gray)
- Accent: `#00B894` (Green)

### Creative Orange
- Primary: `#E17055` (Orange)
- Secondary: `#FDCB6E` (Yellow)
- Accent: `#6C5CE7` (Purple)

## Integration

### With ROI Calculator
- Automatically uses current calculation results
- Seamless handoff from calculator to PowerPoint
- Session storage maintains data consistency

### With Proposal Generator
- Shares data models and calculations
- Consistent metrics and formatting
- Complementary output formats (PDF/Word/PowerPoint)

## Technical Implementation

### Dependencies
- `python-pptx==0.6.23` - PowerPoint generation
- `matplotlib==3.8.2` - Chart creation
- `seaborn==0.13.0` - Chart styling
- `Pillow>=10.0.0` - Image processing

### Key Classes
- `PowerPointGenerator` - Main generation class
- Template configurations with colors/fonts
- Chart generation methods
- Slide builder functions

### File Structure
```
src/
  powerpoint_generator.py     # Main generator class
templates/
  powerpoint_export.html      # Web interface
static/js/
  powerpoint.js              # Frontend functionality
```

## Best Practices

### For Presentations
- Use Executive template for board meetings
- Use Sales template for client presentations
- Use Technical template for implementation reviews
- Include speaker notes for key talking points

### For Customization
- Update company branding information
- Select appropriate color scheme for audience
- Include charts for visual impact
- Test presentation before important meetings

### For Integration
- Run calculations first to populate data
- Save calculations for reuse across formats
- Coordinate with proposal generation for consistency

## Troubleshooting

### Common Issues
1. **No data available**: Run ROI calculation first
2. **Missing charts**: Ensure matplotlib dependencies installed  
3. **Color issues**: Verify color scheme selection
4. **Font problems**: Check system font availability

### Error Messages
- `ROI calculation results required` - Select data first
- `Failed to generate charts` - Check matplotlib setup
- `Template not found` - Verify template selection

## Future Enhancements

### Planned Features
- Custom template creation
- Advanced chart customization
- Multi-language support
- Presentation analytics
- Integration with PowerPoint Online

### API Extensions
- Batch generation
- Template management
- Custom color schemes
- Presentation scheduling

---

The PowerPoint export feature transforms your ROI calculations into professional, compelling presentations ready for any business audience.
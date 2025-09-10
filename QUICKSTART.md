# ROI Calculator - Quick Start Guide 🚀

## Access the Calculator

### Local Access
Open your browser and navigate to: **http://localhost:8000**

### Public Demo URL
For remote demonstrations: Use localtunnel or ngrok to create a public URL

## Step-by-Step Usage

### 1️⃣ Load an Example (Optional)
Click one of the example buttons to pre-fill the form:
- **Small Business**: $500K revenue scenario
- **Medium Business**: $2M revenue scenario  
- **Large Business**: $5M revenue scenario

### 2️⃣ Enter Your Business Data

#### Company Information
- **Company Name**: Optional, for personalized reports

#### Revenue Information
- **Annual Revenue**: Your total yearly revenue in USD
- **Monthly Orders**: Average number of orders per month
- **Average Order Value**: Will auto-calculate based on revenue/orders

#### Current Monthly Costs
- **Labor Costs**: Staff salaries, contractors, benefits
- **Shipping Costs**: Carrier fees, packaging, handling
- **Error Costs**: Returns, refunds, customer service
- **Inventory Costs**: Storage, management, holding costs

#### Investment
- **Service Investment**: One-time cost for optimization services

### 3️⃣ Calculate ROI
Click the green **"Calculate ROI"** button

### 4️⃣ Review Results

#### Main Metrics (Right Panel)
- Annual Savings
- Payback Period  
- First Year ROI
- 3-Year ROI

#### Detailed Analysis (Bottom Section)
- Cost Savings Breakdown by Category
- 3-Year Financial Projections
- NPV and IRR Calculations
- Chilean Market Analysis (with IVA)

### 5️⃣ Generate PDF Report
Click the red **"Generate PDF Report"** button to download a professional 8-page report

## Validation Features

### Real-Time Validation
- ✅ Green border = Valid input
- ❌ Red border = Invalid input
- Helpful error messages appear below fields

### Smart Calculations
- Average Order Value auto-calculates from revenue and orders
- Monthly/annual conversions happen automatically
- Chilean IVA (19%) calculations included

### Input Ranges
- Annual Revenue: $10K - $100M
- Monthly Orders: 1 - 1,000,000
- Service Investment: $1K - $10M

## Error Handling

### Common Issues & Solutions

**"This field is required"**
- Fill in all required fields marked with red asterisks

**"Please enter a valid number"**
- Remove any text or special characters
- Use only numbers and decimal points

**"Annual revenue should be between..."**
- Ensure your values are within reasonable business ranges

**PDF Generation Failed**
- Check that you've calculated ROI first
- Ensure all data is valid
- Try refreshing the page

## Tips for Best Results

### Accurate Data Entry
1. Use your actual monthly averages
2. Include all operational costs
3. Be conservative with estimates

### Understanding Results
- **Payback Period**: How long to recover investment
- **NPV > 0**: Investment is profitable
- **IRR > 12%**: Exceeds typical cost of capital

### Client Presentations
1. Start with an example scenario
2. Modify with client's actual data
3. Show real-time calculations
4. Generate PDF for takeaway

## Keyboard Shortcuts

- **Tab**: Navigate between fields
- **Enter**: Submit calculation (when form is valid)
- **Esc**: Close modals/alerts

## API Testing

### Quick API Test
```bash
curl -X POST http://localhost:8000/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "annual_revenue": 2000000,
    "monthly_orders": 5000,
    "avg_order_value": 33.33,
    "labor_costs": 8000,
    "shipping_costs": 5000,
    "error_costs": 2000,
    "inventory_costs": 3000,
    "service_investment": 50000
  }'
```

## Support

### Need Help?
- Check validation messages for field-specific guidance
- Review example scenarios for typical values
- Contact support@yourcompany.com for assistance

### Report Issues
- GitHub Issues: [Create an issue](https://github.com/yourusername/roi-calculator/issues)
- Email: support@yourcompany.com

---

**Ready to demonstrate ROI to your clients!** 🎯
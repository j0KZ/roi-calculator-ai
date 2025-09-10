# ROI Calculator - Client Demo Guide

## Quick Demo Script for Chilean SME Clients

### 1. Opening Statement
"Let me show you how our operations optimization can transform your e-commerce business with a guaranteed ROI in under 6 months."

### 2. Live Calculation Demo

Open browser to: **http://localhost:8000**

#### Sample Scenarios to Use:

**Small Business ($500K revenue)**
```json
{
  "annual_revenue": 500000,
  "monthly_orders": 1500,
  "avg_order_value": 27.78,
  "labor_costs": 3000,
  "shipping_costs": 2000,
  "error_costs": 500,
  "inventory_costs": 1000,
  "service_investment": 25000
}
```
Expected: ~4 month payback, 150% first-year ROI

**Medium Business ($2M revenue)**
```json
{
  "annual_revenue": 2000000,
  "monthly_orders": 5000,
  "avg_order_value": 33.33,
  "labor_costs": 8000,
  "shipping_costs": 5000,
  "error_costs": 2000,
  "inventory_costs": 3000,
  "service_investment": 50000
}
```
Expected: ~6 month payback, 105% first-year ROI

**Large Business ($5M revenue)**
```json
{
  "annual_revenue": 5000000,
  "monthly_orders": 12000,
  "avg_order_value": 34.72,
  "labor_costs": 20000,
  "shipping_costs": 12000,
  "error_costs": 5000,
  "inventory_costs": 8000,
  "service_investment": 100000
}
```
Expected: ~4 month payback, 180% first-year ROI

### 3. Key Talking Points

#### Labor Savings (60% reduction)
"We automate repetitive tasks like order processing, inventory updates, and customer communications. Your team focuses on growth, not manual data entry."

#### Shipping Optimization (25% reduction)
"Our multi-carrier integration with Chilexpress, Starken, and Correos de Chile automatically selects the cheapest option for each shipment."

#### Error Elimination (80% reduction)
"Automated validation and synchronization eliminate costly mistakes in pricing, inventory, and order fulfillment."

#### Inventory Optimization (30% reduction)
"Real-time stock synchronization across all channels prevents overselling and reduces dead stock."

### 4. Chilean Market Advantages

- **IVA Compliant**: All calculations include 19% IVA
- **Local Integrations**: Defontana, Bsale, Transbank, WebPay
- **Chilean Logistics**: Chilexpress, Starken, Correos de Chile
- **Local Support**: Santiago-based team, CLT timezone

### 5. Implementation Timeline

**Week 1-2**: Discovery & Assessment
**Week 3-4**: System Design & Planning  
**Week 5-8**: Core Implementation
**Week 9-12**: Advanced Features & Optimization
**Week 13-14**: Testing & Training
**Week 15-16**: Go-Live & Support

### 6. Investment & Guarantees

- **Starter Package**: $25,000 (businesses <$1M revenue)
- **Growth Package**: $50,000 (businesses $1-3M revenue)
- **Enterprise Package**: $100,000+ (businesses >$3M revenue)

**Guarantees:**
- ROI within 12 months or money back
- 60% minimum cost reduction in manual processes
- 99.9% uptime SLA

### 7. Common Objections & Responses

**"It's too expensive"**
→ "With a 5.8 month payback period, it pays for itself twice in the first year alone."

**"We're too small"**
→ "Our starter package is designed for businesses your size, with proportional savings."

**"Implementation seems complex"**
→ "We handle everything. Your team just needs 2 hours of training per week."

**"What if it doesn't work?"**
→ "We guarantee ROI within 12 months or full refund. Plus, you keep all the improvements."

### 8. Next Steps

1. **Custom Analysis**: "Let's input your actual numbers for a precise calculation"
2. **Proposal**: "I'll prepare a detailed proposal with your specific ROI"
3. **Pilot Program**: "Start with one area (e.g., shipping) to prove the value"
4. **References**: "Speak with similar businesses already saving 40-60%"

### 9. Closing Statement

"Every day you wait costs you approximately $[daily_savings] in operational inefficiencies. When would you like to start saving?"

---

## Technical Demo Features

### API Testing
```bash
# Show real-time calculation
curl -X POST http://localhost:8000/calculate \
  -H "Content-Type: application/json" \
  -d '{ [client's actual data] }' | jq '.'
```

### Integration Examples
- Defontana API connection
- Transbank payment processing
- Chilexpress shipping rates
- MercadoLibre synchronization

### Dashboard Preview
- Real-time savings tracker
- Monthly performance metrics
- ROI progress visualization
- Alert system for issues

---

## Contact Information

**Sales Team**: ventas@suempresa.cl
**Technical Support**: soporte@suempresa.cl
**WhatsApp Business**: +56 9 XXXX XXXX

*Document prepared for client demonstrations - Internal use only*
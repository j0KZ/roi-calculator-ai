"""
PDF Report Generator for ROI Calculator
Creates professional PDF reports with charts and visualizations
"""

import io
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from typing import Dict, List
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from PIL import Image as PILImage


class ROIPDFGenerator:
    """Generate professional PDF reports for ROI calculations"""
    
    # Constants from ROICalculator
    INFLATION_RATE = 0.035  # Approximate Chilean inflation rate
    IVA_RATE = 0.19  # 19% IVA in Chile
    LABOR_REDUCTION_RATE = 0.60  # 60% labor cost reduction
    SHIPPING_OPTIMIZATION_RATE = 0.25  # 25% shipping cost reduction
    ERROR_ELIMINATION_RATE = 0.80  # 80% error cost reduction
    INVENTORY_OPTIMIZATION_RATE = 0.30  # 30% inventory cost reduction
    
    def __init__(self, roi_results: Dict):
        self.results = roi_results
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
        
    def _create_custom_styles(self):
        """Create custom styles for the PDF"""
        # Title style
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2C3E50'),
            alignment=TA_CENTER,
            spaceAfter=30
        )
        
        # Subtitle style
        self.subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=18,
            textColor=colors.HexColor('#34495E'),
            alignment=TA_LEFT,
            spaceBefore=20,
            spaceAfter=12
        )
        
        # Summary box style
        self.summary_style = ParagraphStyle(
            'SummaryStyle',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#2C3E50'),
            alignment=TA_LEFT,
            backColor=colors.HexColor('#ECF0F1'),
            borderColor=colors.HexColor('#BDC3C7'),
            borderWidth=1,
            borderPadding=10
        )
        
        # Metric value style
        self.metric_value_style = ParagraphStyle(
            'MetricValue',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=colors.HexColor('#E74C3C'),
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        # Chilean flag colors
        self.chilean_blue = colors.HexColor('#0039A6')
        self.chilean_red = colors.HexColor('#D52B1E')
    
    def generate_pdf(self, filename: str = None) -> str:
        """Generate the complete PDF report"""
        if not filename:
            filename = f"roi_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        # Create document
        doc = SimpleDocTemplate(
            filename,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Build story (content)
        story = []
        
        # Title page
        story.extend(self._create_title_page())
        story.append(PageBreak())
        
        # Executive summary
        story.extend(self._create_executive_summary())
        story.append(PageBreak())
        
        # Financial analysis
        story.extend(self._create_financial_analysis())
        story.append(PageBreak())
        
        # Cost breakdown
        story.extend(self._create_cost_breakdown())
        story.append(PageBreak())
        
        # Charts and visualizations
        story.extend(self._create_charts())
        story.append(PageBreak())
        
        # Chilean market specifics
        story.extend(self._create_chilean_analysis())
        story.append(PageBreak())
        
        # Appendix
        story.extend(self._create_appendix())
        
        # Build PDF
        doc.build(story)
        
        return filename
    
    def _create_title_page(self) -> List:
        """Create the title page"""
        story = []
        
        # Company logo placeholder (you can add actual logo)
        story.append(Spacer(1, 1*inch))
        
        # Main title
        title = Paragraph("E-COMMERCE OPERATIONS<br/>ROI ANALYSIS REPORT", self.title_style)
        story.append(title)
        story.append(Spacer(1, 0.5*inch))
        
        # Client information
        client_info = f"""
        <b>Client:</b> {self.results['inputs'].get('company_name', 'Confidential Client')}<br/>
        <b>Analysis Date:</b> {datetime.now().strftime('%B %d, %Y')}<br/>
        <b>Report Type:</b> 3-Year ROI Projection<br/>
        <b>Market Focus:</b> Chilean E-commerce Operations
        """
        
        client_para = Paragraph(client_info, self.styles['Normal'])
        story.append(client_para)
        story.append(Spacer(1, 1*inch))
        
        # Executive summary box
        roi_metrics = self.results['roi_metrics']
        summary_text = f"""
        <b>EXECUTIVE SUMMARY</b><br/><br/>
        <b>Investment:</b> ${self.results['inputs']['service_investment']:,.2f}<br/>
        <b>Annual Savings:</b> ${roi_metrics['annual_savings']:,.2f}<br/>
        <b>Payback Period:</b> {roi_metrics['payback_period_text']}<br/>
        <b>3-Year ROI:</b> {self.results['projections']['year_3']['roi_percentage']:.1f}%<br/>
        <b>NPV:</b> ${self.results['financial_metrics']['npv']:,.2f}
        """
        
        summary_para = Paragraph(summary_text, self.summary_style)
        story.append(summary_para)
        
        return story
    
    def _create_executive_summary(self) -> List:
        """Create executive summary section"""
        story = []
        
        story.append(Paragraph("EXECUTIVE SUMMARY", self.title_style))
        story.append(HRFlowable(width="100%", thickness=2, color=self.chilean_blue))
        story.append(Spacer(1, 20))
        
        # Key metrics table
        roi_metrics = self.results['roi_metrics']
        financial_metrics = self.results['financial_metrics']
        
        metrics_data = [
            ['Metric', 'Value'],
            ['Initial Investment', f"${self.results['inputs']['service_investment']:,.2f}"],
            ['Annual Savings', f"${roi_metrics['annual_savings']:,.2f}"],
            ['Monthly Savings', f"${roi_metrics['monthly_savings']:,.2f}"],
            ['Payback Period', roi_metrics['payback_period_text']],
            ['First Year ROI', f"{roi_metrics['first_year_roi']:.1f}%"],
            ['3-Year ROI', f"{self.results['projections']['year_3']['roi_percentage']:.1f}%"],
            ['Net Present Value', f"${financial_metrics['npv']:,.2f}"],
            ['Internal Rate of Return', f"{financial_metrics['irr']*100:.1f}%"],
        ]
        
        metrics_table = Table(metrics_data, colWidths=[3*inch, 2*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.chilean_blue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        
        story.append(metrics_table)
        story.append(Spacer(1, 30))
        
        # Analysis text
        analysis_text = f"""
        This comprehensive ROI analysis demonstrates the significant financial benefits of implementing 
        our e-commerce operations optimization services for your business. 
        
        <b>Key Findings:</b><br/>
        • Your investment of ${self.results['inputs']['service_investment']:,.2f} will be recovered in {roi_metrics['payback_period_text']}<br/>
        • Annual operational savings of ${roi_metrics['annual_savings']:,.2f} represent {roi_metrics['savings_vs_revenue_percentage']:.1f}% of your current revenue<br/>
        • Over 3 years, you can expect cumulative savings of ${self.results['projections']['year_3']['cumulative_savings']:,.2f}<br/>
        • The positive NPV of ${financial_metrics['npv']:,.2f} confirms this is a financially sound investment<br/>
        
        <b>Risk Assessment:</b><br/>
        With an IRR of {financial_metrics['irr']*100:.1f}%, this investment significantly exceeds typical market returns, 
        making it an attractive opportunity for operational improvement and cost reduction.
        """
        
        story.append(Paragraph(analysis_text, self.styles['Normal']))
        
        return story
    
    def _create_financial_analysis(self) -> List:
        """Create detailed financial analysis section"""
        story = []
        
        story.append(Paragraph("FINANCIAL ANALYSIS", self.title_style))
        story.append(HRFlowable(width="100%", thickness=2, color=self.chilean_blue))
        story.append(Spacer(1, 20))
        
        # 3-year projections table
        story.append(Paragraph("3-Year Financial Projections", self.subtitle_style))
        
        projections_data = [['Year', 'Annual Savings', 'Net Benefit', 'Cumulative ROI']]
        
        # Add investment row
        projections_data.append([
            'Initial Investment',
            f"-${self.results['inputs']['service_investment']:,.2f}",
            f"-${self.results['inputs']['service_investment']:,.2f}",
            "-"
        ])
        
        for year in range(1, 4):
            year_data = self.results['projections'][f'year_{year}']
            projections_data.append([
                f'Year {year}',
                f"${year_data['savings']:,.2f}",
                f"${year_data['net_benefit']:,.2f}",
                f"{year_data['roi_percentage']:.1f}%"
            ])
        
        projections_table = Table(projections_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        projections_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.chilean_blue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (0, 1), colors.lightcoral),  # Investment row
            ('TEXTCOLOR', (0, 1), (-1, 1), colors.white),
            ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 2), (-1, -1), colors.lightgreen),  # Positive years
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
        ]))
        
        story.append(projections_table)
        story.append(Spacer(1, 30))
        
        # Cash flow analysis
        story.append(Paragraph("Cash Flow Analysis", self.subtitle_style))
        
        cash_flows = self.results['financial_metrics']['cash_flows']
        cash_flow_text = f"""
        <b>Net Present Value (NPV) Analysis:</b><br/>
        Using a discount rate of {self.results['financial_metrics']['discount_rate']*100:.0f}% (typical cost of capital), 
        the NPV of ${self.results['financial_metrics']['npv']:,.2f} indicates this investment will create significant value.
        
        <b>Cash Flow Summary:</b><br/>
        • Year 0: ${cash_flows[0]:,.2f} (Initial Investment)<br/>
        • Year 1: ${cash_flows[1]:,.2f} (Net Cash Inflow)<br/>
        • Year 2: ${cash_flows[2]:,.2f} (Net Cash Inflow)<br/>
        • Year 3: ${cash_flows[3]:,.2f} (Net Cash Inflow)<br/>
        
        <b>Internal Rate of Return (IRR):</b><br/>
        The IRR of {self.results['financial_metrics']['irr']*100:.1f}% significantly exceeds the discount rate, 
        confirming this is an excellent investment opportunity.
        """
        
        story.append(Paragraph(cash_flow_text, self.styles['Normal']))
        
        return story
    
    def _create_cost_breakdown(self) -> List:
        """Create cost breakdown analysis"""
        story = []
        
        story.append(Paragraph("COST REDUCTION BREAKDOWN", self.title_style))
        story.append(HRFlowable(width="100%", thickness=2, color=self.chilean_blue))
        story.append(Spacer(1, 20))
        
        savings = self.results['savings']
        current_costs = self.results['current_costs']
        
        # Create breakdown table
        breakdown_data = [
            ['Category', 'Current Monthly Cost', 'Reduction %', 'Monthly Savings', 'Annual Savings']
        ]
        
        categories = [
            ('Labor Optimization', 'labor', '60%'),
            ('Shipping Optimization', 'shipping', '25%'),
            ('Error Elimination', 'errors', '80%'),
            ('Inventory Management', 'inventory', '30%')
        ]
        
        for name, key, rate in categories:
            breakdown_data.append([
                name,
                f"${current_costs[key]['monthly']:,.2f}",
                rate,
                f"${savings[key]['monthly']:,.2f}",
                f"${savings[key]['annual']:,.2f}"
            ])
        
        # Add total row
        breakdown_data.append([
            'TOTAL',
            f"${current_costs['total']['monthly']:,.2f}",
            f"{(savings['annual_total']/current_costs['total']['annual']*100):.1f}%",
            f"${savings['monthly_total']:,.2f}",
            f"${savings['annual_total']:,.2f}"
        ])
        
        breakdown_table = Table(breakdown_data, colWidths=[2*inch, 1.2*inch, 0.8*inch, 1.2*inch, 1.2*inch])
        breakdown_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.chilean_blue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightblue),  # Total row
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.lightgrey])
        ]))
        
        story.append(breakdown_table)
        story.append(Spacer(1, 30))
        
        # Detailed explanations
        explanations = f"""
        <b>Cost Reduction Strategies:</b><br/><br/>
        
        <b>1. Labor Optimization (60% reduction):</b><br/>
        Through process automation, workflow optimization, and staff productivity improvements, 
        we can reduce labor costs by ${savings['labor']['annual']:,.2f} annually.<br/><br/>
        
        <b>2. Shipping Optimization (25% reduction):</b><br/>
        Carrier optimization, route planning, and packaging improvements will save 
        ${savings['shipping']['annual']:,.2f} per year in shipping costs.<br/><br/>
        
        <b>3. Error Elimination (80% reduction):</b><br/>
        Quality control systems and automated validation processes will dramatically reduce 
        error-related costs by ${savings['errors']['annual']:,.2f} annually.<br/><br/>
        
        <b>4. Inventory Management (30% reduction):</b><br/>
        Demand forecasting and inventory optimization will reduce carrying costs by 
        ${savings['inventory']['annual']:,.2f} per year.
        """
        
        story.append(Paragraph(explanations, self.styles['Normal']))
        
        return story
    
    def _create_charts(self) -> List:
        """Create charts and visualizations"""
        story = []
        
        story.append(Paragraph("VISUAL ANALYSIS", self.title_style))
        story.append(HRFlowable(width="100%", thickness=2, color=self.chilean_blue))
        story.append(Spacer(1, 20))
        
        # Create savings breakdown pie chart
        savings_chart_path = self._create_savings_pie_chart()
        if savings_chart_path:
            story.append(Paragraph("Cost Savings Breakdown", self.subtitle_style))
            story.append(Image(savings_chart_path, width=5*inch, height=4*inch))
            story.append(Spacer(1, 20))
        
        # Create ROI progression chart
        roi_chart_path = self._create_roi_progression_chart()
        if roi_chart_path:
            story.append(Paragraph("3-Year ROI Progression", self.subtitle_style))
            story.append(Image(roi_chart_path, width=6*inch, height=4*inch))
            story.append(Spacer(1, 20))
        
        # Create cash flow chart
        cashflow_chart_path = self._create_cashflow_chart()
        if cashflow_chart_path:
            story.append(Paragraph("Cash Flow Analysis", self.subtitle_style))
            story.append(Image(cashflow_chart_path, width=6*inch, height=4*inch))
        
        return story
    
    def _create_savings_pie_chart(self) -> str:
        """Create pie chart for savings breakdown"""
        try:
            savings = self.results['savings']
            
            labels = ['Labor\nOptimization', 'Shipping\nOptimization', 'Error\nElimination', 'Inventory\nManagement']
            sizes = [
                savings['labor']['annual'],
                savings['shipping']['annual'],
                savings['errors']['annual'],
                savings['inventory']['annual']
            ]
            colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12']
            
            plt.figure(figsize=(8, 6))
            wedges, texts, autotexts = plt.pie(sizes, labels=labels, colors=colors, 
                                             autopct='%1.1f%%', startangle=90)
            
            plt.title('Annual Cost Savings Breakdown\n(${:,.0f} Total)'.format(sum(sizes)), 
                     fontsize=14, fontweight='bold')
            
            # Make percentage text bold
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(10)
            
            plt.axis('equal')
            
            chart_path = '/tmp/savings_pie_chart.png'
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return chart_path
            
        except Exception as e:
            print(f"Error creating savings pie chart: {e}")
            return None
    
    def _create_roi_progression_chart(self) -> str:
        """Create ROI progression line chart"""
        try:
            years = [0, 1, 2, 3]
            roi_values = [
                -100,  # Initial investment
                self.results['projections']['year_1']['roi_percentage'],
                self.results['projections']['year_2']['roi_percentage'],
                self.results['projections']['year_3']['roi_percentage']
            ]
            
            plt.figure(figsize=(10, 6))
            plt.plot(years, roi_values, marker='o', linewidth=3, markersize=8, color='#2c3e50')
            plt.axhline(y=0, color='red', linestyle='--', alpha=0.7, label='Break-even')
            
            plt.title('ROI Progression Over 3 Years', fontsize=14, fontweight='bold')
            plt.xlabel('Year', fontsize=12)
            plt.ylabel('ROI (%)', fontsize=12)
            plt.grid(True, alpha=0.3)
            
            # Add value annotations
            for i, (year, roi) in enumerate(zip(years, roi_values)):
                plt.annotate(f'{roi:.1f}%', 
                           xy=(year, roi), 
                           xytext=(10, 10), 
                           textcoords='offset points',
                           fontweight='bold',
                           bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))
            
            plt.legend()
            plt.tight_layout()
            
            chart_path = '/tmp/roi_progression_chart.png'
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return chart_path
            
        except Exception as e:
            print(f"Error creating ROI progression chart: {e}")
            return None
    
    def _create_cashflow_chart(self) -> str:
        """Create cash flow bar chart"""
        try:
            cash_flows = self.results['financial_metrics']['cash_flows']
            years = ['Initial\nInvestment', 'Year 1', 'Year 2', 'Year 3']
            
            plt.figure(figsize=(10, 6))
            bars = plt.bar(years, cash_flows, 
                          color=['red' if cf < 0 else 'green' for cf in cash_flows])
            
            plt.title('Cash Flow Analysis', fontsize=14, fontweight='bold')
            plt.ylabel('Cash Flow ($)', fontsize=12)
            plt.axhline(y=0, color='black', linestyle='-', alpha=0.5)
            
            # Add value annotations on bars
            for bar, value in zip(bars, cash_flows):
                height = bar.get_height()
                plt.annotate(f'${value:,.0f}',
                           xy=(bar.get_x() + bar.get_width()/2, height),
                           xytext=(0, 5 if height >= 0 else -15),
                           textcoords="offset points",
                           ha='center', va='bottom' if height >= 0 else 'top',
                           fontweight='bold')
            
            plt.grid(True, alpha=0.3, axis='y')
            plt.tight_layout()
            
            chart_path = '/tmp/cashflow_chart.png'
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return chart_path
            
        except Exception as e:
            print(f"Error creating cash flow chart: {e}")
            return None
    
    def _create_chilean_analysis(self) -> List:
        """Create Chilean market-specific analysis"""
        story = []
        
        story.append(Paragraph("CHILEAN MARKET ANALYSIS", self.title_style))
        story.append(HRFlowable(width="100%", thickness=2, color=self.chilean_red))
        story.append(Spacer(1, 20))
        
        chilean_data = self.results['chilean_specifics']
        
        # IVA analysis
        story.append(Paragraph("Tax Considerations (IVA)", self.subtitle_style))
        
        iva_text = f"""
        <b>Chilean IVA Impact Analysis:</b><br/><br/>
        
        In Chile, the Value Added Tax (IVA) rate is {chilean_data['iva_rate']*100:.0f}%. 
        This affects the total cost-benefit calculation as follows:<br/><br/>
        
        <b>Annual Savings before IVA:</b> ${chilean_data['savings_with_iva']['amount_before_iva']:,.2f}<br/>
        <b>IVA on Savings:</b> ${chilean_data['savings_with_iva']['iva_amount']:,.2f}<br/>
        <b>Total Savings with IVA:</b> ${chilean_data['savings_with_iva']['amount_with_iva']:,.2f}<br/><br/>
        
        <b>Important Note:</b> The savings calculations include the benefit of reduced IVA payments 
        on operational costs, making the actual benefit even more significant for Chilean businesses.
        """
        
        story.append(Paragraph(iva_text, self.styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Market context
        story.append(Paragraph("Chilean E-commerce Market Context", self.subtitle_style))
        
        market_text = f"""
        <b>Market Opportunity:</b><br/>
        Chile's e-commerce market has grown significantly, with increasing demand for operational efficiency. 
        Key factors supporting this investment include:<br/><br/>
        
        • <b>Digital Transformation:</b> Chilean businesses are rapidly adopting digital solutions<br/>
        • <b>Labor Cost Inflation:</b> Current inflation rate of {self.INFLATION_RATE*100:.1f}% makes automation more attractive<br/>
        • <b>Competitive Pressure:</b> Need for operational efficiency to compete effectively<br/>
        • <b>Consumer Expectations:</b> Higher expectations for delivery speed and accuracy<br/><br/>
        
        <b>Risk Mitigation:</b><br/>
        • Currency stability supports long-term planning<br/>
        • Government support for digital transformation<br/>
        • Strong e-commerce growth trajectory<br/>
        • Established logistics infrastructure
        """
        
        story.append(Paragraph(market_text, self.styles['Normal']))
        
        return story
    
    def _create_appendix(self) -> List:
        """Create appendix with technical details"""
        story = []
        
        story.append(Paragraph("APPENDIX", self.title_style))
        story.append(HRFlowable(width="100%", thickness=2, color=colors.gray))
        story.append(Spacer(1, 20))
        
        # Assumptions
        story.append(Paragraph("Key Assumptions", self.subtitle_style))
        
        assumptions_text = f"""
        <b>Financial Assumptions:</b><br/>
        • Discount Rate: {self.results['financial_metrics']['discount_rate']*100:.0f}%<br/>
        • Inflation Rate: {self.INFLATION_RATE*100:.1f}%<br/>
        • Chilean IVA Rate: {self.IVA_RATE*100:.0f}%<br/><br/>
        
        <b>Operational Improvement Rates:</b><br/>
        • Labor Reduction: {self.LABOR_REDUCTION_RATE*100:.0f}%<br/>
        • Shipping Optimization: {self.SHIPPING_OPTIMIZATION_RATE*100:.0f}%<br/>
        • Error Elimination: {self.ERROR_ELIMINATION_RATE*100:.0f}%<br/>
        • Inventory Optimization: {self.INVENTORY_OPTIMIZATION_RATE*100:.0f}%<br/><br/>
        
        <b>Implementation Timeline:</b><br/>
        • Phase 1 (Months 1-3): Process analysis and system setup<br/>
        • Phase 2 (Months 4-6): Implementation and staff training<br/>
        • Phase 3 (Months 7-12): Full optimization and monitoring<br/>
        • Years 2-3: Continuous improvement and scaling
        """
        
        story.append(Paragraph(assumptions_text, self.styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Methodology
        story.append(Paragraph("Calculation Methodology", self.subtitle_style))
        
        methodology_text = """
        <b>ROI Calculation Formula:</b><br/>
        ROI = ((Total Benefits - Total Costs) / Total Costs) × 100<br/><br/>
        
        <b>NPV Calculation:</b><br/>
        NPV = Σ (Cash Flow / (1 + Discount Rate)^t) for t = 0 to 3<br/><br/>
        
        <b>IRR Calculation:</b><br/>
        IRR is the discount rate that makes NPV = 0, calculated using Newton-Raphson method<br/><br/>
        
        <b>Risk Assessment:</b><br/>
        • Conservative estimates used for all improvement rates<br/>
        • Inflation adjustments applied to multi-year projections<br/>
        • Sensitivity analysis available upon request
        """
        
        story.append(Paragraph(methodology_text, self.styles['Normal']))
        
        # Footer
        story.append(Spacer(1, 1*inch))
        footer_text = f"""
        <i>This report was generated on {datetime.now().strftime('%B %d, %Y')} using our proprietary 
        ROI Calculator v1.0. For questions or additional analysis, please contact our team.</i>
        """
        story.append(Paragraph(footer_text, self.styles['Normal']))
        
        return story


# Example usage
if __name__ == "__main__":
    # This would typically be called with actual ROI results
    pass
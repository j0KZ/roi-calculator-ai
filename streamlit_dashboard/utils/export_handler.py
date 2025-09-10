"""
Export Handler for Streamlit Dashboard
=====================================
Handles export functionality for reports, data, and visualizations.
"""

import streamlit as st
import pandas as pd
import json
import io
import base64
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
import plotly.graph_objects as go
import plotly.io as pio
from pathlib import Path

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    st.warning("ReportLab not available. PDF export functionality will be limited.")


class ExportHandler:
    """Handles various export formats for dashboard data and reports"""
    
    def __init__(self):
        """Initialize export handler"""
        self.supported_formats = ['json', 'csv', 'excel', 'pdf', 'html']
        if REPORTLAB_AVAILABLE:
            self.styles = getSampleStyleSheet()
    
    def export_roi_data(self, roi_data: Dict[str, Any], format: str = 'json') -> Optional[bytes]:
        """
        Export ROI calculation data
        
        Args:
            roi_data: Dictionary containing ROI data
            format: Export format ('json', 'csv', 'excel', 'pdf')
            
        Returns:
            Exported data as bytes or None if error
        """
        try:
            if format.lower() == 'json':
                return self._export_json(roi_data)
            elif format.lower() == 'csv':
                return self._export_roi_csv(roi_data)
            elif format.lower() == 'excel':
                return self._export_roi_excel(roi_data)
            elif format.lower() == 'pdf':
                return self._export_roi_pdf(roi_data)
            else:
                st.error(f"Unsupported format: {format}")
                return None
                
        except Exception as e:
            st.error(f"Error exporting ROI data: {str(e)}")
            return None
    
    def export_assessment_data(self, assessment_data: Dict[str, Any], format: str = 'json') -> Optional[bytes]:
        """
        Export assessment data
        
        Args:
            assessment_data: Dictionary containing assessment data
            format: Export format
            
        Returns:
            Exported data as bytes or None if error
        """
        try:
            if format.lower() == 'json':
                return self._export_json(assessment_data)
            elif format.lower() == 'pdf':
                return self._export_assessment_pdf(assessment_data)
            elif format.lower() == 'excel':
                return self._export_assessment_excel(assessment_data)
            else:
                st.error(f"Unsupported format: {format}")
                return None
                
        except Exception as e:
            st.error(f"Error exporting assessment data: {str(e)}")
            return None
    
    def export_proposal(self, proposal_data: Dict[str, Any], format: str = 'pdf') -> Optional[bytes]:
        """
        Export proposal document
        
        Args:
            proposal_data: Dictionary containing proposal data
            format: Export format
            
        Returns:
            Exported data as bytes or None if error
        """
        try:
            if format.lower() == 'pdf':
                return self._export_proposal_pdf(proposal_data)
            elif format.lower() == 'html':
                return self._export_proposal_html(proposal_data)
            elif format.lower() == 'json':
                return self._export_json(proposal_data)
            else:
                st.error(f"Unsupported format: {format}")
                return None
                
        except Exception as e:
            st.error(f"Error exporting proposal: {str(e)}")
            return None
    
    def export_chart(self, fig: go.Figure, format: str = 'png', width: int = 1200, height: int = 600) -> Optional[bytes]:
        """
        Export Plotly chart
        
        Args:
            fig: Plotly figure object
            format: Export format ('png', 'svg', 'html', 'pdf')
            width: Image width
            height: Image height
            
        Returns:
            Exported chart as bytes or None if error
        """
        try:
            if format.lower() == 'png':
                img_bytes = pio.to_image(fig, format='png', width=width, height=height)
                return img_bytes
            elif format.lower() == 'svg':
                svg_string = pio.to_image(fig, format='svg', width=width, height=height)
                return svg_string
            elif format.lower() == 'html':
                html_string = pio.to_html(fig, include_plotlyjs=True)
                return html_string.encode('utf-8')
            elif format.lower() == 'pdf':
                pdf_bytes = pio.to_image(fig, format='pdf', width=width, height=height)
                return pdf_bytes
            else:
                st.error(f"Unsupported chart format: {format}")
                return None
                
        except Exception as e:
            st.error(f"Error exporting chart: {str(e)}")
            return None
    
    def _export_json(self, data: Dict[str, Any]) -> bytes:
        """Export data as JSON"""
        # Add metadata
        export_data = {
            'exported_at': datetime.now().isoformat(),
            'source': 'Chilean E-commerce Sales Toolkit',
            'version': '1.0.0',
            'data': data
        }
        
        json_string = json.dumps(export_data, indent=2, ensure_ascii=False)
        return json_string.encode('utf-8')
    
    def _export_roi_csv(self, roi_data: Dict[str, Any]) -> bytes:
        """Export ROI data as CSV"""
        # Create DataFrame with ROI metrics
        data_rows = []
        
        # Basic metrics
        basic_metrics = {
            'Ingresos Mensuales': roi_data.get('monthly_revenue', 0),
            'Costos Mensuales': roi_data.get('monthly_costs', 0),
            'Ganancia Mensual': roi_data.get('monthly_revenue', 0) - roi_data.get('monthly_costs', 0),
            'Costo Implementación': roi_data.get('implementation_cost', 0),
            'ROI Esperado (%)': roi_data.get('expected_roi', 0),
            'Tiempo Recuperación (meses)': roi_data.get('payback_months', 0),
            'Tasa Crecimiento (%)': roi_data.get('growth_rate', 0) * 100
        }
        
        for metric, value in basic_metrics.items():
            data_rows.append({
                'Métrica': metric,
                'Valor': value,
                'Unidad': 'CLP' if 'Costo' in metric or 'Ingreso' in metric or 'Ganancia' in metric else 
                         '%' if '%' in metric else 'Meses' if 'meses' in metric else ''
            })
        
        df = pd.DataFrame(data_rows)
        
        # Convert to CSV
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False, encoding='utf-8')
        return csv_buffer.getvalue().encode('utf-8')
    
    def _export_roi_excel(self, roi_data: Dict[str, Any]) -> bytes:
        """Export ROI data as Excel"""
        with pd.ExcelWriter(io.BytesIO(), engine='openpyxl') as writer:
            # Basic metrics sheet
            basic_data = self._prepare_roi_basic_data(roi_data)
            basic_df = pd.DataFrame(basic_data)
            basic_df.to_excel(writer, sheet_name='Métricas Básicas', index=False)
            
            # Projections sheet
            projections = self._generate_roi_projections(roi_data)
            projections_df = pd.DataFrame(projections)
            projections_df.to_excel(writer, sheet_name='Proyecciones', index=False)
            
            # Cost breakdown sheet
            cost_breakdown = self._prepare_cost_breakdown(roi_data)
            if cost_breakdown:
                cost_df = pd.DataFrame(cost_breakdown)
                cost_df.to_excel(writer, sheet_name='Desglose Costos', index=False)
        
        writer.close()
        return writer.book
    
    def _export_roi_pdf(self, roi_data: Dict[str, Any]) -> Optional[bytes]:
        """Export ROI data as PDF report"""
        if not REPORTLAB_AVAILABLE:
            st.error("PDF export requires reportlab library")
            return None
        
        try:
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            story = []
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=self.styles['Heading1'],
                fontSize=20,
                textColor=colors.darkblue,
                alignment=1  # Center
            )
            
            story.append(Paragraph("Reporte de Análisis ROI", title_style))
            story.append(Spacer(1, 20))
            
            # Subtitle with date
            subtitle = f"Generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}"
            story.append(Paragraph(subtitle, self.styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Executive summary
            story.append(Paragraph("Resumen Ejecutivo", self.styles['Heading2']))
            
            summary_data = [
                ['Métrica', 'Valor'],
                ['ROI Esperado', f"{roi_data.get('expected_roi', 0):.1f}%"],
                ['Inversión Inicial', f"${roi_data.get('implementation_cost', 0):,.0f} CLP"],
                ['Ganancia Mensual', f"${roi_data.get('monthly_revenue', 0) - roi_data.get('monthly_costs', 0):,.0f} CLP"],
                ['Tiempo de Recuperación', f"{roi_data.get('payback_months', 0):.1f} meses"]
            ]
            
            summary_table = Table(summary_data)
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(summary_table)
            story.append(Spacer(1, 20))
            
            # Detailed analysis
            story.append(Paragraph("Análisis Detallado", self.styles['Heading2']))
            
            detailed_data = [
                ['Concepto', 'Valor (CLP)', 'Observaciones'],
                ['Ingresos Mensuales', f"${roi_data.get('monthly_revenue', 0):,.0f}", 'Proyectado'],
                ['Costos Mensuales', f"${roi_data.get('monthly_costs', 0):,.0f}", 'Estimado'],
                ['Ganancia Mensual', f"${roi_data.get('monthly_revenue', 0) - roi_data.get('monthly_costs', 0):,.0f}", 'Neto'],
                ['Inversión Inicial', f"${roi_data.get('implementation_cost', 0):,.0f}", 'Una vez'],
                ['ROI 24 meses', f"{roi_data.get('expected_roi', 0):.1f}%", 'Calculado']
            ]
            
            detailed_table = Table(detailed_data, colWidths=[2*inch, 1.5*inch, 2*inch])
            detailed_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ALIGN', (1, 1), (1, -1), 'RIGHT')  # Right align currency
            ]))
            
            story.append(detailed_table)
            story.append(Spacer(1, 20))
            
            # Recommendations
            story.append(Paragraph("Recomendaciones", self.styles['Heading2']))
            
            roi_value = roi_data.get('expected_roi', 0)
            if roi_value > 50:
                recommendation = "Proyecto altamente recomendado con excelente retorno de inversión."
            elif roi_value > 20:
                recommendation = "Proyecto recomendado con buen retorno de inversión."
            elif roi_value > 0:
                recommendation = "Proyecto viable pero requiere análisis adicional de riesgos."
            else:
                recommendation = "Proyecto no recomendado en condiciones actuales."
            
            story.append(Paragraph(recommendation, self.styles['Normal']))
            
            # Build PDF
            doc.build(story)
            buffer.seek(0)
            return buffer.getvalue()
            
        except Exception as e:
            st.error(f"Error creating PDF: {str(e)}")
            return None
    
    def _export_assessment_pdf(self, assessment_data: Dict[str, Any]) -> Optional[bytes]:
        """Export assessment data as PDF"""
        if not REPORTLAB_AVAILABLE:
            return None
        
        try:
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            story = []
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=self.styles['Heading1'],
                fontSize=18,
                textColor=colors.darkgreen,
                alignment=1
            )
            
            story.append(Paragraph("Reporte de Evaluación Rápida", title_style))
            story.append(Spacer(1, 20))
            
            # Assessment results
            story.append(Paragraph("Resultados de Evaluación", self.styles['Heading2']))
            
            # Overall score
            total_score = assessment_data.get('total_score', 0)
            max_score = assessment_data.get('max_score', 100)
            percentage = (total_score / max_score * 100) if max_score > 0 else 0
            
            score_data = [
                ['Puntuación Total', f"{total_score}/{max_score}"],
                ['Porcentaje', f"{percentage:.1f}%"],
                ['Categoría', self._get_score_category(percentage)]
            ]
            
            score_table = Table(score_data)
            score_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.green),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(score_table)
            story.append(Spacer(1, 20))
            
            # Category breakdown
            if assessment_data.get('category_scores'):
                story.append(Paragraph("Desglose por Categorías", self.styles['Heading3']))
                
                category_data = [['Categoría', 'Puntuación']]
                for category, score in assessment_data['category_scores'].items():
                    category_data.append([category, f"{score}/100"])
                
                category_table = Table(category_data)
                category_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(category_table)
                story.append(Spacer(1, 20))
            
            # Recommendations
            story.append(Paragraph("Recomendaciones", self.styles['Heading2']))
            recommendations = assessment_data.get('recommendations', [])
            
            if recommendations:
                for i, rec in enumerate(recommendations, 1):
                    story.append(Paragraph(f"{i}. {rec}", self.styles['Normal']))
                    story.append(Spacer(1, 10))
            else:
                story.append(Paragraph("No se generaron recomendaciones específicas.", self.styles['Normal']))
            
            doc.build(story)
            buffer.seek(0)
            return buffer.getvalue()
            
        except Exception as e:
            st.error(f"Error creating assessment PDF: {str(e)}")
            return None
    
    def _export_proposal_pdf(self, proposal_data: Dict[str, Any]) -> Optional[bytes]:
        """Export proposal as PDF"""
        if not REPORTLAB_AVAILABLE:
            return None
        
        try:
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            story = []
            
            # Title page
            title_style = ParagraphStyle(
                'ProposalTitle',
                parent=self.styles['Title'],
                fontSize=24,
                textColor=colors.darkblue,
                alignment=1,
                spaceAfter=30
            )
            
            story.append(Paragraph("Propuesta Comercial", title_style))
            story.append(Paragraph("Solución E-commerce", self.styles['Heading2']))
            story.append(Spacer(1, 40))
            
            # Client information
            client_info = proposal_data.get('client_info', {})
            if client_info:
                story.append(Paragraph("Información del Cliente", self.styles['Heading2']))
                
                client_data = [
                    ['Campo', 'Valor'],
                    ['Empresa', client_info.get('company_name', 'N/A')],
                    ['Contacto', client_info.get('contact_person', 'N/A')],
                    ['Email', client_info.get('email', 'N/A')],
                    ['Teléfono', client_info.get('phone', 'N/A')]
                ]
                
                client_table = Table(client_data)
                client_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.navy),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(client_table)
                story.append(Spacer(1, 20))
            
            # Proposal content
            story.append(Paragraph("Propuesta de Solución", self.styles['Heading2']))
            
            proposal_content = proposal_data.get('content', 'Contenido de propuesta no disponible.')
            story.append(Paragraph(proposal_content, self.styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Investment summary
            if proposal_data.get('investment_summary'):
                story.append(Paragraph("Resumen de Inversión", self.styles['Heading2']))
                
                investment = proposal_data['investment_summary']
                investment_data = [
                    ['Concepto', 'Valor (CLP)'],
                    ['Inversión Total', f"${investment.get('total_cost', 0):,.0f}"],
                    ['ROI Esperado', f"{investment.get('expected_roi', 0):.1f}%"],
                    ['Tiempo de Recuperación', f"{investment.get('payback_months', 0)} meses"]
                ]
                
                investment_table = Table(investment_data)
                investment_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(investment_table)
            
            doc.build(story)
            buffer.seek(0)
            return buffer.getvalue()
            
        except Exception as e:
            st.error(f"Error creating proposal PDF: {str(e)}")
            return None
    
    def _export_proposal_html(self, proposal_data: Dict[str, Any]) -> bytes:
        """Export proposal as HTML"""
        client_info = proposal_data.get('client_info', {})
        proposal_content = proposal_data.get('content', '')
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Propuesta Comercial - {client_info.get('company_name', 'Cliente')}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                .header {{ text-align: center; margin-bottom: 40px; }}
                .section {{ margin-bottom: 30px; }}
                .client-info {{ background: #f8f9fa; padding: 20px; border-radius: 8px; }}
                .investment-summary {{ background: #e8f5e8; padding: 20px; border-radius: 8px; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
                th {{ background-color: #667eea; color: white; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Propuesta Comercial</h1>
                <h2>Solución E-commerce</h2>
                <p>Generado el {datetime.now().strftime('%d/%m/%Y')}</p>
            </div>
            
            <div class="section client-info">
                <h3>Información del Cliente</h3>
                <p><strong>Empresa:</strong> {client_info.get('company_name', 'N/A')}</p>
                <p><strong>Contacto:</strong> {client_info.get('contact_person', 'N/A')}</p>
                <p><strong>Email:</strong> {client_info.get('email', 'N/A')}</p>
                <p><strong>Teléfono:</strong> {client_info.get('phone', 'N/A')}</p>
            </div>
            
            <div class="section">
                <h3>Propuesta de Solución</h3>
                <p>{proposal_content}</p>
            </div>
            
            <div class="section investment-summary">
                <h3>Resumen de Inversión</h3>
                <!-- Investment details would go here -->
            </div>
        </body>
        </html>
        """
        
        return html_content.encode('utf-8')
    
    def _prepare_roi_basic_data(self, roi_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Prepare basic ROI data for export"""
        return [
            {'Métrica': 'Ingresos Mensuales', 'Valor': roi_data.get('monthly_revenue', 0), 'Unidad': 'CLP'},
            {'Métrica': 'Costos Mensuales', 'Valor': roi_data.get('monthly_costs', 0), 'Unidad': 'CLP'},
            {'Métrica': 'Ganancia Mensual', 'Valor': roi_data.get('monthly_revenue', 0) - roi_data.get('monthly_costs', 0), 'Unidad': 'CLP'},
            {'Métrica': 'Inversión Inicial', 'Valor': roi_data.get('implementation_cost', 0), 'Unidad': 'CLP'},
            {'Métrica': 'ROI Esperado', 'Valor': roi_data.get('expected_roi', 0), 'Unidad': '%'},
            {'Métrica': 'Tiempo Recuperación', 'Valor': roi_data.get('payback_months', 0), 'Unidad': 'Meses'}
        ]
    
    def _generate_roi_projections(self, roi_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate ROI projections for export"""
        monthly_revenue = roi_data.get('monthly_revenue', 1000000)
        monthly_costs = roi_data.get('monthly_costs', 800000)
        growth_rate = roi_data.get('growth_rate', 0.05)
        
        projections = []
        for month in range(1, 25):  # 24 months
            revenue = monthly_revenue * ((1 + growth_rate) ** (month - 1))
            costs = monthly_costs * ((1 + growth_rate * 0.7) ** (month - 1))
            profit = revenue - costs
            
            projections.append({
                'Mes': month,
                'Ingresos': revenue,
                'Costos': costs,
                'Ganancia': profit
            })
        
        return projections
    
    def _prepare_cost_breakdown(self, roi_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Prepare cost breakdown for export"""
        cost_items = [
            {'Categoría': 'Desarrollo', 'Costo': roi_data.get('development_cost', 2000000)},
            {'Categoría': 'Licencias', 'Costo': roi_data.get('license_cost', 500000)},
            {'Categoría': 'Hosting', 'Costo': roi_data.get('hosting_cost', 300000)},
            {'Categoría': 'Marketing', 'Costo': roi_data.get('marketing_cost', 800000)},
            {'Categoría': 'Capacitación', 'Costo': roi_data.get('training_cost', 200000)},
            {'Categoría': 'Contingencia', 'Costo': roi_data.get('contingency_cost', 400000)}
        ]
        
        # Filter out zero costs
        return [item for item in cost_items if item['Costo'] > 0]
    
    def _export_assessment_excel(self, assessment_data: Dict[str, Any]) -> bytes:
        """Export assessment data to Excel"""
        with pd.ExcelWriter(io.BytesIO(), engine='openpyxl') as writer:
            # Summary sheet
            summary_data = {
                'Métrica': ['Puntuación Total', 'Puntuación Máxima', 'Porcentaje'],
                'Valor': [
                    assessment_data.get('total_score', 0),
                    assessment_data.get('max_score', 100),
                    assessment_data.get('total_score', 0) / assessment_data.get('max_score', 100) * 100
                ]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Resumen', index=False)
            
            # Responses sheet
            if assessment_data.get('responses'):
                responses_data = []
                for question, answer in assessment_data['responses'].items():
                    responses_data.append({'Pregunta': question, 'Respuesta': answer})
                
                responses_df = pd.DataFrame(responses_data)
                responses_df.to_excel(writer, sheet_name='Respuestas', index=False)
        
        writer.close()
        return writer.book
    
    def _get_score_category(self, percentage: float) -> str:
        """Get score category based on percentage"""
        if percentage >= 80:
            return "Excelente"
        elif percentage >= 60:
            return "Bueno"
        elif percentage >= 40:
            return "Regular"
        else:
            return "Necesita Mejora"
    
    def create_download_link(self, data: bytes, filename: str, mime_type: str = 'application/octet-stream') -> str:
        """
        Create a download link for exported data
        
        Args:
            data: Data to download
            filename: Filename for download
            mime_type: MIME type for the file
            
        Returns:
            Base64 encoded download link
        """
        b64_data = base64.b64encode(data).decode()
        return f'data:{mime_type};base64,{b64_data}'
    
    def get_filename(self, export_type: str, format: str, timestamp: bool = True) -> str:
        """
        Generate appropriate filename for export
        
        Args:
            export_type: Type of export (roi, assessment, proposal)
            format: File format
            timestamp: Whether to include timestamp
            
        Returns:
            Generated filename
        """
        base_names = {
            'roi': 'analisis_roi',
            'assessment': 'evaluacion_rapida',
            'proposal': 'propuesta_comercial'
        }
        
        base_name = base_names.get(export_type, 'export')
        
        if timestamp:
            timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
            return f"{base_name}_{timestamp_str}.{format}"
        else:
            return f"{base_name}.{format}"
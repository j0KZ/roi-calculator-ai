"""
Visualization Generator for Streamlit Dashboard
==============================================
Creates interactive Plotly charts for ROI analysis, assessments, and reports.
"""

import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional
import streamlit as st
from datetime import datetime, timedelta


class ChartGenerator:
    """Generates various types of charts for the dashboard"""
    
    def __init__(self):
        """Initialize chart generator with default styling"""
        self.default_colors = {
            'primary': '#667eea',
            'secondary': '#764ba2',
            'success': '#00d4aa',
            'warning': '#f39c12',
            'danger': '#e74c3c',
            'info': '#3498db'
        }
        
        self.template = 'plotly_white'
        self.font_family = 'Arial, sans-serif'
    
    def format_currency(self, value: float, currency: str = 'CLP') -> str:
        """Format currency values for display"""
        if currency == 'CLP':
            return f"${value:,.0f} CLP"
        else:
            return f"${value:,.2f} {currency}"
    
    def create_roi_projection_chart(self, roi_data: Dict[str, Any]) -> go.Figure:
        """
        Create ROI projection chart over time
        
        Args:
            roi_data: Dictionary containing ROI calculation data
            
        Returns:
            Plotly figure object
        """
        try:
            # Extract data
            monthly_revenue = roi_data.get('monthly_revenue', 1000000)
            monthly_costs = roi_data.get('monthly_costs', 800000)
            growth_rate = roi_data.get('growth_rate', 0.05)  # 5% monthly growth
            months = roi_data.get('projection_months', 24)
            
            # Generate projections
            time_periods = list(range(1, months + 1))
            revenues = []
            costs = []
            profits = []
            cumulative_roi = []
            
            implementation_cost = roi_data.get('implementation_cost', 5000000)
            cumulative_profit = -implementation_cost  # Start negative due to initial investment
            
            for month in time_periods:
                # Calculate revenue with growth
                current_revenue = monthly_revenue * ((1 + growth_rate) ** (month - 1))
                current_costs = monthly_costs * ((1 + growth_rate * 0.7) ** (month - 1))  # Costs grow slower
                current_profit = current_revenue - current_costs
                
                revenues.append(current_revenue)
                costs.append(current_costs)
                profits.append(current_profit)
                
                # Calculate cumulative ROI
                cumulative_profit += current_profit
                roi_percentage = (cumulative_profit / implementation_cost) * 100 if implementation_cost > 0 else 0
                cumulative_roi.append(roi_percentage)
            
            # Create figure with subplots
            fig = go.Figure()
            
            # Add revenue line
            fig.add_trace(go.Scatter(
                x=time_periods,
                y=revenues,
                mode='lines+markers',
                name='Ingresos Mensuales',
                line=dict(color=self.default_colors['success'], width=3),
                marker=dict(size=6),
                hovertemplate='<b>Mes %{x}</b><br>Ingresos: %{y:,.0f} CLP<extra></extra>'
            ))
            
            # Add costs line
            fig.add_trace(go.Scatter(
                x=time_periods,
                y=costs,
                mode='lines+markers',
                name='Costos Mensuales',
                line=dict(color=self.default_colors['danger'], width=3),
                marker=dict(size=6),
                hovertemplate='<b>Mes %{x}</b><br>Costos: %{y:,.0f} CLP<extra></extra>'
            ))
            
            # Add profit line
            fig.add_trace(go.Scatter(
                x=time_periods,
                y=profits,
                mode='lines+markers',
                name='Ganancia Mensual',
                line=dict(color=self.default_colors['primary'], width=3),
                marker=dict(size=6),
                hovertemplate='<b>Mes %{x}</b><br>Ganancia: %{y:,.0f} CLP<extra></extra>'
            ))
            
            # Update layout
            fig.update_layout(
                title="Proyección Financiera E-commerce (24 meses)",
                xaxis_title="Meses",
                yaxis_title="Valor (CLP)",
                template=self.template,
                height=500,
                hovermode='x unified',
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            # Format y-axis
            fig.update_layout(
                yaxis=dict(
                    tickformat='.0s',
                    ticksuffix='',
                    showgrid=True,
                    gridcolor='lightgray'
                )
            )
            
            return fig
            
        except Exception as e:
            st.error(f"Error creating ROI projection chart: {str(e)}")
            return self.create_error_chart("Error en proyección ROI")
    
    def create_monte_carlo_chart(self, roi_data: Dict[str, Any], simulations: int = 10000) -> go.Figure:
        """
        Create Monte Carlo simulation chart for ROI analysis
        
        Args:
            roi_data: Dictionary containing ROI calculation data
            simulations: Number of Monte Carlo simulations
            
        Returns:
            Plotly figure object
        """
        try:
            # Extract parameters
            monthly_revenue = roi_data.get('monthly_revenue', 1000000)
            monthly_costs = roi_data.get('monthly_costs', 800000)
            implementation_cost = roi_data.get('implementation_cost', 5000000)
            
            # Define uncertainty ranges (percentage variations)
            revenue_uncertainty = roi_data.get('revenue_uncertainty', 0.2)  # ±20%
            cost_uncertainty = roi_data.get('cost_uncertainty', 0.15)      # ±15%
            
            # Run Monte Carlo simulation
            np.random.seed(42)  # For reproducible results
            
            simulated_rois = []
            
            for _ in range(simulations):
                # Sample from normal distributions
                sim_revenue = np.random.normal(monthly_revenue, monthly_revenue * revenue_uncertainty)
                sim_costs = np.random.normal(monthly_costs, monthly_costs * cost_uncertainty)
                
                # Ensure positive values
                sim_revenue = max(sim_revenue, monthly_revenue * 0.3)
                sim_costs = max(sim_costs, monthly_costs * 0.3)
                
                # Calculate 24-month ROI
                monthly_profit = sim_revenue - sim_costs
                total_profit_24m = monthly_profit * 24
                roi_percentage = ((total_profit_24m - implementation_cost) / implementation_cost) * 100
                
                simulated_rois.append(roi_percentage)
            
            # Create histogram
            fig = go.Figure()
            
            fig.add_trace(go.Histogram(
                x=simulated_rois,
                nbinsx=50,
                name='Distribución ROI',
                marker_color=self.default_colors['primary'],
                opacity=0.7,
                hovertemplate='<b>ROI Range</b>: %{x}%<br><b>Frequency</b>: %{y}<extra></extra>'
            ))
            
            # Add vertical lines for percentiles
            percentiles = [10, 25, 50, 75, 90]
            percentile_values = np.percentile(simulated_rois, percentiles)
            
            colors = ['red', 'orange', 'green', 'orange', 'red']
            for i, (perc, value) in enumerate(zip(percentiles, percentile_values)):
                fig.add_vline(
                    x=value,
                    line_dash="dash",
                    line_color=colors[i],
                    annotation_text=f"P{perc}: {value:.1f}%",
                    annotation_position="top"
                )
            
            # Update layout
            fig.update_layout(
                title=f"Análisis Monte Carlo - ROI 24 meses ({simulations:,} simulaciones)",
                xaxis_title="ROI (%)",
                yaxis_title="Frecuencia",
                template=self.template,
                height=500,
                showlegend=False
            )
            
            # Add statistics annotation
            mean_roi = np.mean(simulated_rois)
            std_roi = np.std(simulated_rois)
            prob_positive = (np.array(simulated_rois) > 0).mean() * 100
            
            stats_text = f"""
            <b>Estadísticas:</b><br>
            Media: {mean_roi:.1f}%<br>
            Desviación: {std_roi:.1f}%<br>
            Prob. ROI > 0%: {prob_positive:.1f}%
            """
            
            fig.add_annotation(
                x=0.02, y=0.98,
                xref="paper", yref="paper",
                text=stats_text,
                showarrow=False,
                align="left",
                bgcolor="white",
                bordercolor="gray",
                borderwidth=1
            )
            
            return fig
            
        except Exception as e:
            st.error(f"Error creating Monte Carlo chart: {str(e)}")
            return self.create_error_chart("Error en simulación Monte Carlo")
    
    def create_risk_assessment_chart(self, assessment_data: Dict[str, Any]) -> go.Figure:
        """
        Create radar chart for risk assessment
        
        Args:
            assessment_data: Dictionary containing assessment responses
            
        Returns:
            Plotly figure object
        """
        try:
            # Define assessment categories
            categories = [
                'Madurez Tecnológica',
                'Capacidad Financiera',
                'Experiencia Digital',
                'Recursos Humanos',
                'Infraestructura',
                'Competencia'
            ]
            
            # Extract scores (mock data if not available)
            if assessment_data.get('category_scores'):
                scores = list(assessment_data['category_scores'].values())[:6]
            else:
                # Generate mock scores based on responses
                responses = assessment_data.get('responses', {})
                scores = [
                    responses.get('tech_maturity', 3) * 20,
                    responses.get('financial_capacity', 3) * 20,
                    responses.get('digital_experience', 3) * 20,
                    responses.get('human_resources', 3) * 20,
                    responses.get('infrastructure', 3) * 20,
                    responses.get('competition', 3) * 20
                ]
            
            # Ensure we have 6 scores
            while len(scores) < 6:
                scores.append(60)  # Default score
            scores = scores[:6]  # Take only first 6
            
            # Create radar chart
            fig = go.Figure()
            
            fig.add_trace(go.Scatterpolar(
                r=scores + [scores[0]],  # Close the shape
                theta=categories + [categories[0]],
                fill='toself',
                fillcolor='rgba(102, 126, 234, 0.3)',
                line=dict(color=self.default_colors['primary'], width=2),
                marker=dict(size=8),
                name='Puntuación Actual',
                hovertemplate='<b>%{theta}</b><br>Puntuación: %{r}/100<extra></extra>'
            ))
            
            # Add benchmark line (industry average)
            benchmark_scores = [70] * 6  # Industry benchmark
            fig.add_trace(go.Scatterpolar(
                r=benchmark_scores + [benchmark_scores[0]],
                theta=categories + [categories[0]],
                line=dict(color=self.default_colors['warning'], width=2, dash='dash'),
                marker=dict(size=6),
                name='Promedio Industria',
                hovertemplate='<b>%{theta}</b><br>Promedio: %{r}/100<extra></extra>'
            ))
            
            # Update layout
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100],
                        tickfont=dict(size=10)
                    ),
                    angularaxis=dict(
                        tickfont=dict(size=12)
                    )
                ),
                showlegend=True,
                title="Evaluación de Madurez Digital",
                template=self.template,
                height=500,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.1,
                    xanchor="center",
                    x=0.5
                )
            )
            
            return fig
            
        except Exception as e:
            st.error(f"Error creating risk assessment chart: {str(e)}")
            return self.create_error_chart("Error en evaluación de riesgo")
    
    def create_implementation_timeline(self, proposal_data: Dict[str, Any]) -> go.Figure:
        """
        Create Gantt chart for implementation timeline
        
        Args:
            proposal_data: Dictionary containing proposal information
            
        Returns:
            Plotly figure object
        """
        try:
            # Define standard implementation phases
            phases = [
                {'Task': 'Análisis y Planificación', 'Start': '2024-01-01', 'Finish': '2024-01-15', 'Resource': 'Consultoría'},
                {'Task': 'Diseño de Arquitectura', 'Start': '2024-01-10', 'Finish': '2024-01-30', 'Resource': 'Arquitecto'},
                {'Task': 'Desarrollo Frontend', 'Start': '2024-01-25', 'Finish': '2024-03-15', 'Resource': 'Desarrollo'},
                {'Task': 'Desarrollo Backend', 'Start': '2024-01-25', 'Finish': '2024-03-01', 'Resource': 'Desarrollo'},
                {'Task': 'Integración Pagos', 'Start': '2024-02-15', 'Finish': '2024-03-01', 'Resource': 'Desarrollo'},
                {'Task': 'Testing y QA', 'Start': '2024-03-01', 'Finish': '2024-03-20', 'Resource': 'QA'},
                {'Task': 'Despliegue Producción', 'Start': '2024-03-15', 'Finish': '2024-03-25', 'Resource': 'DevOps'},
                {'Task': 'Capacitación', 'Start': '2024-03-20', 'Finish': '2024-04-05', 'Resource': 'Consultoría'},
                {'Task': 'Soporte Post-Lanzamiento', 'Start': '2024-03-25', 'Finish': '2024-04-25', 'Resource': 'Soporte'}
            ]
            
            # Override with custom phases if provided
            if proposal_data.get('implementation_phases'):
                phases = proposal_data['implementation_phases']
            
            # Convert to DataFrame for easier handling
            df = pd.DataFrame(phases)
            
            # Create Gantt chart
            fig = px.timeline(
                df, 
                x_start="Start", 
                x_end="Finish", 
                y="Task", 
                color="Resource",
                title="Cronograma de Implementación",
                color_discrete_map={
                    'Consultoría': self.default_colors['primary'],
                    'Arquitecto': self.default_colors['info'],
                    'Desarrollo': self.default_colors['success'],
                    'QA': self.default_colors['warning'],
                    'DevOps': self.default_colors['secondary'],
                    'Soporte': self.default_colors['danger']
                }
            )
            
            # Update layout
            fig.update_layout(
                height=500,
                template=self.template,
                xaxis_title="Fecha",
                yaxis_title="Fase",
                legend_title="Recurso",
                hovermode='y unified'
            )
            
            # Reverse y-axis to show tasks in chronological order
            fig.update_yaxes(categoryorder="total ascending")
            
            return fig
            
        except Exception as e:
            st.error(f"Error creating timeline chart: {str(e)}")
            return self.create_error_chart("Error en cronograma")
    
    def create_cost_breakdown_chart(self, roi_data: Dict[str, Any]) -> go.Figure:
        """
        Create cost breakdown pie chart
        
        Args:
            roi_data: Dictionary containing cost information
            
        Returns:
            Plotly figure object
        """
        try:
            # Define cost categories
            cost_categories = {
                'Desarrollo': roi_data.get('development_cost', 2000000),
                'Licencias': roi_data.get('license_cost', 500000),
                'Hardware/Hosting': roi_data.get('hosting_cost', 300000),
                'Marketing': roi_data.get('marketing_cost', 800000),
                'Capacitación': roi_data.get('training_cost', 200000),
                'Contingencia': roi_data.get('contingency_cost', 400000)
            }
            
            # Remove zero values
            cost_categories = {k: v for k, v in cost_categories.items() if v > 0}
            
            labels = list(cost_categories.keys())
            values = list(cost_categories.values())
            
            # Create pie chart
            fig = go.Figure(data=[go.Pie(
                labels=labels,
                values=values,
                hole=0.3,
                marker_colors=[
                    self.default_colors['primary'],
                    self.default_colors['success'],
                    self.default_colors['info'],
                    self.default_colors['warning'],
                    self.default_colors['secondary'],
                    self.default_colors['danger']
                ],
                textinfo='label+percent+value',
                texttemplate='<b>%{label}</b><br>%{percent}<br>$%{value:,.0f} CLP',
                hovertemplate='<b>%{label}</b><br>Costo: $%{value:,.0f} CLP<br>Porcentaje: %{percent}<extra></extra>'
            )])
            
            # Add center text with total
            total_cost = sum(values)
            fig.add_annotation(
                text=f"<b>Total</b><br>${total_cost:,.0f}<br>CLP",
                x=0.5, y=0.5,
                font_size=16,
                showarrow=False
            )
            
            # Update layout
            fig.update_layout(
                title="Desglose de Costos de Implementación",
                template=self.template,
                height=500,
                showlegend=True,
                legend=dict(
                    orientation="v",
                    yanchor="middle",
                    y=0.5,
                    xanchor="left",
                    x=1.01
                )
            )
            
            return fig
            
        except Exception as e:
            st.error(f"Error creating cost breakdown chart: {str(e)}")
            return self.create_error_chart("Error en desglose de costos")
    
    def create_sensitivity_analysis_chart(self, roi_data: Dict[str, Any]) -> go.Figure:
        """
        Create sensitivity analysis chart showing ROI sensitivity to key parameters
        
        Args:
            roi_data: Dictionary containing ROI calculation data
            
        Returns:
            Plotly figure object
        """
        try:
            # Base values
            base_revenue = roi_data.get('monthly_revenue', 1000000)
            base_costs = roi_data.get('monthly_costs', 800000)
            implementation_cost = roi_data.get('implementation_cost', 5000000)
            
            # Variation range (-50% to +50%)
            variation_range = np.linspace(-0.5, 0.5, 21)
            
            # Calculate ROI sensitivity for different parameters
            revenue_rois = []
            cost_rois = []
            impl_cost_rois = []
            
            for var in variation_range:
                # Revenue sensitivity
                varied_revenue = base_revenue * (1 + var)
                monthly_profit = varied_revenue - base_costs
                total_profit_24m = monthly_profit * 24
                roi = ((total_profit_24m - implementation_cost) / implementation_cost) * 100
                revenue_rois.append(roi)
                
                # Cost sensitivity (inverse relationship)
                varied_costs = base_costs * (1 + var)
                monthly_profit = base_revenue - varied_costs
                total_profit_24m = monthly_profit * 24
                roi = ((total_profit_24m - implementation_cost) / implementation_cost) * 100
                cost_rois.append(roi)
                
                # Implementation cost sensitivity (inverse relationship)
                varied_impl_cost = implementation_cost * (1 + var)
                monthly_profit = base_revenue - base_costs
                total_profit_24m = monthly_profit * 24
                roi = ((total_profit_24m - varied_impl_cost) / varied_impl_cost) * 100
                impl_cost_rois.append(roi)
            
            # Create figure
            fig = go.Figure()
            
            # Add traces
            fig.add_trace(go.Scatter(
                x=variation_range * 100,
                y=revenue_rois,
                mode='lines+markers',
                name='Sensibilidad Ingresos',
                line=dict(color=self.default_colors['success'], width=3),
                marker=dict(size=6)
            ))
            
            fig.add_trace(go.Scatter(
                x=variation_range * 100,
                y=cost_rois,
                mode='lines+markers',
                name='Sensibilidad Costos',
                line=dict(color=self.default_colors['danger'], width=3),
                marker=dict(size=6)
            ))
            
            fig.add_trace(go.Scatter(
                x=variation_range * 100,
                y=impl_cost_rois,
                mode='lines+markers',
                name='Sensibilidad Inversión Inicial',
                line=dict(color=self.default_colors['warning'], width=3),
                marker=dict(size=6)
            ))
            
            # Add zero lines
            fig.add_hline(y=0, line_dash="dash", line_color="gray", 
                         annotation_text="ROI = 0%", annotation_position="right")
            fig.add_vline(x=0, line_dash="dash", line_color="gray")
            
            # Update layout
            fig.update_layout(
                title="Análisis de Sensibilidad ROI",
                xaxis_title="Variación del Parámetro (%)",
                yaxis_title="ROI (%)",
                template=self.template,
                height=500,
                hovermode='x unified',
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            return fig
            
        except Exception as e:
            st.error(f"Error creating sensitivity analysis: {str(e)}")
            return self.create_error_chart("Error en análisis de sensibilidad")
    
    def create_error_chart(self, error_message: str) -> go.Figure:
        """Create a simple error chart when data is unavailable"""
        fig = go.Figure()
        
        fig.add_annotation(
            x=0.5, y=0.5,
            xref="paper", yref="paper",
            text=f"⚠️ {error_message}",
            showarrow=False,
            font=dict(size=16, color="red"),
            align="center"
        )
        
        fig.update_layout(
            template=self.template,
            height=400,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            title="Error en Visualización"
        )
        
        return fig
    
    def create_comparison_chart(self, scenarios: Dict[str, Dict[str, Any]]) -> go.Figure:
        """
        Create comparison chart for different scenarios
        
        Args:
            scenarios: Dictionary of scenario names and their data
            
        Returns:
            Plotly figure object
        """
        try:
            scenario_names = list(scenarios.keys())
            metrics = ['ROI (%)', 'Ganancia Mensual (CLP)', 'Tiempo Recuperación (meses)', 'Riesgo (%)']
            
            # Extract data for each scenario
            data = []
            for scenario_name, scenario_data in scenarios.items():
                roi = scenario_data.get('roi', 0)
                monthly_profit = scenario_data.get('monthly_profit', 0)
                payback_time = scenario_data.get('payback_months', 12)
                risk = scenario_data.get('risk_score', 50)
                
                data.append([roi, monthly_profit / 1000, payback_time, risk])  # Scale profit to thousands
            
            # Create grouped bar chart
            fig = go.Figure()
            
            colors = [self.default_colors['primary'], self.default_colors['success'], 
                     self.default_colors['warning'], self.default_colors['info']]
            
            for i, metric in enumerate(metrics):
                values = [scenario_data[i] for scenario_data in data]
                fig.add_trace(go.Bar(
                    name=metric,
                    x=scenario_names,
                    y=values,
                    marker_color=colors[i % len(colors)],
                    yaxis=f'y{i+1}' if i > 0 else 'y'
                ))
            
            # Update layout with multiple y-axes
            fig.update_layout(
                title="Comparación de Escenarios",
                template=self.template,
                height=500,
                barmode='group',
                xaxis_title="Escenarios"
            )
            
            return fig
            
        except Exception as e:
            st.error(f"Error creating comparison chart: {str(e)}")
            return self.create_error_chart("Error en comparación de escenarios")
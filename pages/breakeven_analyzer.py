#!/usr/bin/env python3
"""
Breakeven Analyzer Page - Calculate breakeven point for e-commerce businesses
"""

import streamlit as st
from pages.shared_navigation import show_navigation
import sys
import os
from datetime import datetime, timedelta
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from breakeven_analyzer import BreakEvenAnalyzer

def show_breakeven_analyzer():
    """Display breakeven analyzer page"""

    # Show navigation sidebar
    show_navigation()
    
    st.title("📈 Análisis de Punto de Equilibrio")
    st.markdown("Determine cuándo su negocio alcanzará el punto de equilibrio")
    
    # Initialize analyzer
    analyzer = BreakEvenAnalyzer()
    
    # Input section
    st.markdown("## 📊 Datos del Negocio")
    
    # Revenue inputs
    st.markdown("### 💰 Ingresos")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        price_per_unit = st.number_input(
            "Precio por Unidad (CLP)",
            min_value=0,
            value=50000,
            step=1000,
            format="%d",
            help="Precio promedio de venta por producto"
        )
    
    with col2:
        units_per_month = st.number_input(
            "Unidades Vendidas/Mes",
            min_value=0,
            value=100,
            step=10,
            format="%d",
            help="Promedio de unidades vendidas mensualmente"
        )
    
    with col3:
        growth_rate = st.number_input(
            "Crecimiento Mensual (%)",
            min_value=0.0,
            max_value=100.0,
            value=5.0,
            step=0.5,
            format="%.1f",
            help="Tasa de crecimiento esperada"
        )
    
    # Cost inputs
    st.markdown("### 💸 Costos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Costos Variables")
        
        cost_per_unit = st.number_input(
            "Costo por Unidad (CLP)",
            min_value=0,
            value=20000,
            step=1000,
            format="%d",
            help="Costo directo por producto"
        )
        
        shipping_cost = st.number_input(
            "Costo de Envío/Unidad",
            min_value=0,
            value=3000,
            step=500,
            format="%d"
        )
        
        commission_rate = st.number_input(
            "Comisión Marketplace (%)",
            min_value=0.0,
            max_value=50.0,
            value=10.0,
            step=0.5,
            format="%.1f"
        )
    
    with col2:
        st.markdown("#### Costos Fijos Mensuales")
        
        rent = st.number_input(
            "Arriendo/Oficina",
            min_value=0,
            value=2000000,
            step=100000,
            format="%d"
        )
        
        salaries = st.number_input(
            "Salarios",
            min_value=0,
            value=8000000,
            step=500000,
            format="%d"
        )
        
        marketing = st.number_input(
            "Marketing",
            min_value=0,
            value=3000000,
            step=100000,
            format="%d"
        )
        
        other_fixed = st.number_input(
            "Otros Costos Fijos",
            min_value=0,
            value=2000000,
            step=100000,
            format="%d"
        )
    
    # Investment input
    st.markdown("---")
    initial_investment = st.number_input(
        "Inversión Inicial (CLP)",
        min_value=0,
        value=50000000,
        step=1000000,
        format="%d",
        help="Capital inicial invertido en el negocio"
    )
    
    # Calculate button
    if st.button("📊 Calcular Punto de Equilibrio", type="primary", use_container_width=True):
        
        # Prepare data
        revenue_data = {
            'price_per_unit': price_per_unit,
            'units_per_month': units_per_month,
            'growth_rate': growth_rate / 100
        }
        
        variable_costs = {
            'cost_per_unit': cost_per_unit,
            'shipping': shipping_cost,
            'commission_rate': commission_rate / 100
        }
        
        fixed_costs = {
            'rent': rent,
            'salaries': salaries,
            'marketing': marketing,
            'other': other_fixed
        }
        
        # Run analysis
        results = analyzer.calculate_breakeven(
            revenue_data,
            variable_costs,
            fixed_costs,
            initial_investment
        )
        
        # Display results
        st.markdown("---")
        st.markdown("## 🎯 Resultados del Análisis")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Punto de Equilibrio",
                f"{results['breakeven_units']:.0f} unidades",
                delta="por mes"
            )
        
        with col2:
            st.metric(
                "Tiempo hasta Equilibrio",
                f"{results['months_to_breakeven']:.0f} meses",
                delta=f"Fecha: {results['breakeven_date'].strftime('%b %Y')}"
            )
        
        with col3:
            st.metric(
                "Margen de Contribución",
                f"{results['contribution_margin']:.1f}%",
                delta=f"${results['contribution_per_unit']:,.0f}/unidad"
            )
        
        with col4:
            st.metric(
                "ROI Proyectado",
                f"{results['projected_roi']:.1f}%",
                delta="A 12 meses"
            )
        
        # Breakeven chart
        st.markdown("---")
        st.markdown("## 📊 Análisis Gráfico")
        
        # Generate projection data
        months = np.arange(0, 25)
        revenues = []
        costs = []
        profits = []
        cumulative_profits = []
        cumulative = -initial_investment
        
        for month in months:
            units = units_per_month * ((1 + growth_rate/100) ** month)
            revenue = units * price_per_unit
            variable_cost = units * (cost_per_unit + shipping_cost + price_per_unit * commission_rate/100)
            fixed_cost = sum(fixed_costs.values())
            total_cost = variable_cost + fixed_cost
            profit = revenue - total_cost
            cumulative += profit
            
            revenues.append(revenue)
            costs.append(total_cost)
            profits.append(profit)
            cumulative_profits.append(cumulative)
        
        # Create breakeven chart
        fig = go.Figure()
        
        # Revenue line
        fig.add_trace(go.Scatter(
            x=months,
            y=revenues,
            mode='lines',
            name='Ingresos',
            line=dict(color='#4ecdc4', width=3)
        ))
        
        # Cost line
        fig.add_trace(go.Scatter(
            x=months,
            y=costs,
            mode='lines',
            name='Costos Totales',
            line=dict(color='#ff6b6b', width=3)
        ))
        
        # Breakeven point
        fig.add_trace(go.Scatter(
            x=[results['months_to_breakeven']],
            y=[revenues[int(results['months_to_breakeven'])]],
            mode='markers',
            name='Punto de Equilibrio',
            marker=dict(color='#f5b800', size=15, symbol='star')
        ))
        
        fig.update_layout(
            title="Análisis de Punto de Equilibrio",
            xaxis_title="Mes",
            yaxis_title="CLP",
            template='plotly_dark',
            paper_bgcolor='#0a0a0a',
            plot_bgcolor='#1a1a1a',
            height=400,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Profit projection chart
        col1, col2 = st.columns(2)
        
        with col1:
            # Monthly profit chart
            fig_profit = go.Figure()
            
            colors = ['#ff6b6b' if p < 0 else '#4ecdc4' for p in profits]
            
            fig_profit.add_trace(go.Bar(
                x=months,
                y=profits,
                name='Utilidad Mensual',
                marker_color=colors
            ))
            
            fig_profit.update_layout(
                title="Utilidad Mensual Proyectada",
                xaxis_title="Mes",
                yaxis_title="Utilidad (CLP)",
                template='plotly_dark',
                paper_bgcolor='#0a0a0a',
                plot_bgcolor='#1a1a1a',
                height=350
            )
            
            st.plotly_chart(fig_profit, use_container_width=True)
        
        with col2:
            # Cumulative profit chart
            fig_cumulative = go.Figure()
            
            fig_cumulative.add_trace(go.Scatter(
                x=months,
                y=cumulative_profits,
                mode='lines',
                fill='tozeroy',
                name='Utilidad Acumulada',
                line=dict(color='#f5b800', width=3),
                fillcolor='rgba(245, 184, 0, 0.2)'
            ))
            
            # Add zero line
            fig_cumulative.add_hline(
                y=0,
                line_dash="dash",
                line_color="white",
                opacity=0.5
            )
            
            fig_cumulative.update_layout(
                title="Utilidad Acumulada (Recuperación de Inversión)",
                xaxis_title="Mes",
                yaxis_title="CLP Acumulado",
                template='plotly_dark',
                paper_bgcolor='#0a0a0a',
                plot_bgcolor='#1a1a1a',
                height=350
            )
            
            st.plotly_chart(fig_cumulative, use_container_width=True)
        
        # Sensitivity analysis
        st.markdown("---")
        st.markdown("## 🔬 Análisis de Sensibilidad")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Variación en Precio")
            price_variations = [-20, -10, 0, 10, 20]
            breakeven_by_price = []
            
            for var in price_variations:
                new_price = price_per_unit * (1 + var/100)
                new_contribution = new_price - cost_per_unit - shipping_cost - new_price * commission_rate/100
                new_breakeven = sum(fixed_costs.values()) / new_contribution if new_contribution > 0 else float('inf')
                breakeven_by_price.append(new_breakeven)
            
            df_sensitivity_price = pd.DataFrame({
                'Variación (%)': price_variations,
                'Precio': [price_per_unit * (1 + v/100) for v in price_variations],
                'Punto Equilibrio': breakeven_by_price
            })
            
            st.dataframe(df_sensitivity_price, use_container_width=True, hide_index=True)
        
        with col2:
            st.markdown("### Variación en Costos")
            cost_variations = [-20, -10, 0, 10, 20]
            breakeven_by_cost = []
            
            for var in cost_variations:
                new_cost = cost_per_unit * (1 + var/100)
                new_contribution = price_per_unit - new_cost - shipping_cost - price_per_unit * commission_rate/100
                new_breakeven = sum(fixed_costs.values()) / new_contribution if new_contribution > 0 else float('inf')
                breakeven_by_cost.append(new_breakeven)
            
            df_sensitivity_cost = pd.DataFrame({
                'Variación (%)': cost_variations,
                'Costo/Unidad': [cost_per_unit * (1 + v/100) for v in cost_variations],
                'Punto Equilibrio': breakeven_by_cost
            })
            
            st.dataframe(df_sensitivity_cost, use_container_width=True, hide_index=True)
        
        # Scenarios
        st.markdown("---")
        st.markdown("## 🎭 Escenarios")
        
        scenarios = results['scenarios']
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.error("### 😟 Escenario Pesimista")
            st.metric("Punto de Equilibrio", f"{scenarios['pessimistic']['breakeven_units']:.0f} unidades")
            st.metric("Meses hasta Equilibrio", f"{scenarios['pessimistic']['months']:.0f}")
            st.metric("ROI a 12 meses", f"{scenarios['pessimistic']['roi']:.1f}%")
        
        with col2:
            st.warning("### 😐 Escenario Realista")
            st.metric("Punto de Equilibrio", f"{scenarios['realistic']['breakeven_units']:.0f} unidades")
            st.metric("Meses hasta Equilibrio", f"{scenarios['realistic']['months']:.0f}")
            st.metric("ROI a 12 meses", f"{scenarios['realistic']['roi']:.1f}%")
        
        with col3:
            st.success("### 😊 Escenario Optimista")
            st.metric("Punto de Equilibrio", f"{scenarios['optimistic']['breakeven_units']:.0f} unidades")
            st.metric("Meses hasta Equilibrio", f"{scenarios['optimistic']['months']:.0f}")
            st.metric("ROI a 12 meses", f"{scenarios['optimistic']['roi']:.1f}%")
        
        # Recommendations
        st.markdown("---")
        st.markdown("## 💡 Recomendaciones")
        
        recommendations = results['recommendations']
        
        for idx, rec in enumerate(recommendations, 1):
            with st.expander(f"{idx}. {rec['title']}"):
                st.markdown(f"**Descripción:** {rec['description']}")
                st.markdown(f"**Impacto:** {rec['impact']}")
                st.markdown(f"**Prioridad:** {rec['priority']}")
        
        # Export section
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📥 Exportar Análisis", use_container_width=True):
                # Prepare export data
                export_df = pd.DataFrame({
                    'Métrica': [
                        'Punto de Equilibrio (unidades)',
                        'Meses hasta Equilibrio',
                        'Margen de Contribución (%)',
                        'ROI Proyectado 12 meses (%)',
                        'Inversión Inicial',
                        'Costos Fijos Mensuales',
                        'Costo Variable por Unidad'
                    ],
                    'Valor': [
                        f"{results['breakeven_units']:.0f}",
                        f"{results['months_to_breakeven']:.0f}",
                        f"{results['contribution_margin']:.1f}",
                        f"{results['projected_roi']:.1f}",
                        f"${initial_investment:,.0f}",
                        f"${sum(fixed_costs.values()):,.0f}",
                        f"${cost_per_unit + shipping_cost:,.0f}"
                    ]
                })
                
                csv = export_df.to_csv(index=False)
                st.download_button(
                    label="Descargar CSV",
                    data=csv,
                    file_name=f"analisis_breakeven_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        
        with col2:
            if st.button("💾 Guardar Análisis", use_container_width=True):
                st.session_state['breakeven_analysis'] = {
                    'date': datetime.now(),
                    'results': results,
                    'inputs': {
                        'revenue': revenue_data,
                        'variable_costs': variable_costs,
                        'fixed_costs': fixed_costs,
                        'investment': initial_investment
                    }
                }
                st.success("Análisis guardado en la sesión")

if __name__ == "__main__":
    show_breakeven_analyzer()
"""
ROI Calculator Page for Streamlit Dashboard
"""

import streamlit as st
from pages.shared_navigation import show_navigation
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime
import time
import json

# Import the ROI calculator
import sys
import os
sys.path.insert(0, 'src')
from enhanced_roi_calculator import EnhancedROICalculator
from history_manager import HistoryManager
from roi_result_adapter import adapt_roi_results

# Import database connection
try:
    from database.connection import get_session
    from database.models import Calculation, Template
    db_available = True
except ImportError:
    db_available = False
    print("Database not available. Running in session-only mode.")

# Import chart theme utilities
sys.path.insert(0, 'utils')
try:
    from chart_theme import apply_dark_theme, get_dark_color_sequence, get_gauge_theme
except ImportError:
    # Fallback functions if chart_theme not available
    def apply_dark_theme(fig):
        fig.update_layout(
            paper_bgcolor='#0a0a0a',
            plot_bgcolor='#1a1a1a',
            font_color='#ffffff'
        )
        return fig
    
    def get_dark_color_sequence():
        return ['#f5b800', '#ffd700', '#ff9500', '#ff6b35', '#c9302c']
    
    def get_gauge_theme():
        return {'bar_color': '#f5b800', 'bgcolor': '#1a1a1a'}

def format_clp(amount):
    """Format amount as Chilean Pesos"""
    return f"${amount:,.0f} CLP"

def format_millions(amount):
    """Format amount in millions"""
    return f"${amount/1000000:.1f}M"

def create_roi_gauge(roi_value):
    """Create a gauge chart for ROI"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = roi_value,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "ROI Año 1 (%)"},
        delta = {'reference': 100, 'increasing': {'color': "green"}},
        gauge = {
            'axis': {'range': [None, 300], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "#f5b800"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 50], 'color': '#ffcccc'},
                {'range': [50, 100], 'color': '#ffffcc'},
                {'range': [100, 200], 'color': '#ccffcc'},
                {'range': [200, 300], 'color': '#00ff00'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 100
            }
        }
    ))
    fig.update_layout(height=300, margin=dict(l=0, r=0, t=30, b=0))
    return fig

def create_scenario_chart(scenarios):
    """Create scenario analysis chart"""
    scenario_data = []
    max_roi = 0
    for name, data in scenarios.items():
        roi = data.get('roi_percentage', 0)
        max_roi = max(max_roi, roi)
        scenario_data.append({
            'Scenario': data.get('name', name),
            'ROI (%)': roi,
            'Probability (%)': data.get('probability', 0)
        })
    
    df = pd.DataFrame(scenario_data)
    
    fig = px.bar(df, x='Scenario', y='ROI (%)', 
                 text='ROI (%)',
                 color='Probability (%)',
                 color_continuous_scale=['#ff6b6b', '#ffd93d', '#6bcf7f'],
                 title='Análisis de Escenarios')
    
    fig.update_traces(texttemplate='%{text:.0f}%', textposition='outside')
    
    # Adjust y-axis range to accommodate the highest value with some padding
    y_max = max(max_roi * 1.15, 100)  # Add 15% padding or at least 100%
    fig.update_layout(
        height=400,
        yaxis=dict(range=[0, y_max])
    )
    return fig

def create_savings_breakdown_chart(improvements):
    """Create savings breakdown pie chart"""
    savings = improvements.get('monthly_savings_clp', {})
    
    if savings:
        df = pd.DataFrame([
            {'Category': 'Labor', 'Savings': savings.get('labor', 0)},
            {'Category': 'Shipping', 'Savings': savings.get('shipping', 0)},
            {'Category': 'Platform Fees', 'Savings': savings.get('platform_fees', 0)},
            {'Category': 'Errors', 'Savings': savings.get('errors', 0)},
            {'Category': 'Inventory', 'Savings': savings.get('inventory', 0)}
        ])
        
        fig = px.pie(df, values='Savings', names='Category',
                     title='Distribución de Ahorros Mensuales',
                     color_discrete_sequence=get_dark_color_sequence())
        fig.update_layout(height=400)
        return apply_dark_theme(fig)
    return None

def create_payback_timeline(payback_months, investment, monthly_savings):
    """Create payback period timeline"""
    months = list(range(0, int(payback_months) + 3))
    cumulative_savings = [monthly_savings * m for m in months]
    investment_line = [investment] * len(months)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=months, y=cumulative_savings,
        mode='lines+markers',
        name='Ahorro Acumulado',
        line=dict(color='#6bcf7f', width=3),
        marker=dict(size=8)
    ))
    
    fig.add_trace(go.Scatter(
        x=months, y=investment_line,
        mode='lines',
        name='Inversión',
        line=dict(color='#ff6b6b', width=2, dash='dash')
    ))
    
    # Add breakeven point
    fig.add_vline(x=payback_months, line_dash="dot", line_color="orange",
                  annotation_text=f"Payback: {payback_months:.1f} meses")
    
    fig.update_layout(
        title='Período de Recuperación',
        xaxis_title='Meses',
        yaxis_title='CLP',
        height=400,
        hovermode='x unified'
    )
    return fig

# Initialize session state if not present
if 'client_data' not in st.session_state:
    st.session_state.client_data = {
        'company_name': '',
        'contact_name': '',
        'email': '',
        'phone': '',
        'industry': 'retail',
        'investment_clp': 20000000
    }
if 'assessment_results' not in st.session_state:
    st.session_state.assessment_results = {}
if 'roi_results' not in st.session_state:
    st.session_state.roi_results = {}
if 'proposal_data' not in st.session_state:
    st.session_state.proposal_data = {}
if 'calc_time' not in st.session_state:
    st.session_state.calc_time = 0
if 'last_saved_id' not in st.session_state:
    st.session_state.last_saved_id = None

def show_roi_calculator():
    """Display the ROI Calculator page"""

    # Show navigation sidebar
    show_navigation()
    
    st.title("📊 Calculadora ROI Avanzada")
    st.markdown("Analice el retorno de inversión con simulación Monte Carlo y proyecciones a 3 años")
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Datos de Entrada", "📊 Resultados", "📈 Visualizaciones", "📋 Recomendaciones"])
    
    with tab1:
        st.markdown("### Información de la Empresa")
        
        col1, col2 = st.columns(2)
        
        with col1:
            company_name = st.text_input("Nombre de la Empresa", 
                                        value=st.session_state.client_data.get('company_name', ''),
                                        placeholder="Tienda Digital Santiago SpA")
            
            annual_revenue = st.number_input("Ingresos Anuales (CLP)", 
                                            min_value=0,
                                            value=600000000,
                                            step=10000000,
                                            format="%d",
                                            help="Ingresos anuales totales en pesos chilenos")
            
            monthly_orders = st.number_input("Órdenes Mensuales", 
                                            min_value=0,
                                            value=2000,
                                            step=100,
                                            help="Cantidad promedio de órdenes por mes")
            
            avg_order_value = st.number_input("Valor Promedio por Orden (CLP)", 
                                             min_value=0,
                                             value=25000,
                                             step=1000,
                                             format="%d",
                                             help="Ticket promedio por transacción")
        
        with col2:
            industry = st.selectbox("Industria", 
                                   options=['retail', 'wholesale', 'services', 'manufacturing'],
                                   format_func=lambda x: {
                                       'retail': 'Retail',
                                       'wholesale': 'Mayorista',
                                       'services': 'Servicios',
                                       'manufacturing': 'Manufactura'
                                   }[x])
            
            employees = st.number_input("Empleados en Operaciones", 
                                       min_value=1,
                                       value=5,
                                       help="Empleados dedicados a operaciones e-commerce")
            
            conversion_rate = st.slider("Tasa de Conversión (%)", 
                                      min_value=0.5,
                                      max_value=10.0,
                                      value=2.3,
                                      step=0.1,
                                      format="%.1f%%") / 100
            
            current_platforms = st.multiselect("Plataformas Actuales",
                                              options=['transbank', 'webpay', 'mercadopago', 
                                                      'paypal', 'flow', 'khipu', 'mach', 'fpay'],
                                              default=['transbank', 'webpay'])
        
        st.markdown("### Costos Operacionales Mensuales")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            labor_costs = st.number_input("Costos Laborales (CLP/mes)", 
                                         min_value=0,
                                         value=3500000,
                                         step=100000,
                                         format="%d")
            
            shipping_costs = st.number_input("Costos de Envío (CLP/mes)", 
                                            min_value=0,
                                            value=2500000,
                                            step=100000,
                                            format="%d")
        
        with col2:
            platform_fees = st.number_input("Comisiones Plataforma (CLP/mes)", 
                                           min_value=0,
                                           value=1200000,
                                           step=100000,
                                           format="%d")
            
            error_costs = st.number_input("Costos por Errores (CLP/mes)", 
                                        min_value=0,
                                        value=600000,
                                        step=50000,
                                        format="%d")
        
        with col3:
            inventory_costs = st.number_input("Costos de Inventario (CLP/mes)", 
                                             min_value=0,
                                             value=1800000,
                                             step=100000,
                                             format="%d")
            
            investment = st.number_input("Inversión en Consultoría (CLP)", 
                                        min_value=0,
                                        value=20000000,
                                        step=1000000,
                                        format="%d",
                                        help="Inversión total en servicios de consultoría")
        
        # Advanced options
        with st.expander("⚙️ Opciones Avanzadas"):
            col1, col2 = st.columns(2)
            
            with col1:
                simulations = st.number_input("Iteraciones Monte Carlo", 
                                             min_value=1000,
                                             max_value=50000,
                                             value=10000,
                                             step=1000,
                                             help="Más iteraciones = Mayor precisión")
                
                confidence_level = st.slider("Nivel de Confianza", 
                                           min_value=80,
                                           max_value=99,
                                           value=95,
                                           help="Nivel de confianza estadística")
            
            with col2:
                include_inflation = st.checkbox("Incluir Inflación", value=True)
                inflation_rate = 0.035
                if include_inflation:
                    inflation_rate = st.slider("Tasa de Inflación Anual", 
                                              min_value=0.0,
                                              max_value=10.0,
                                              value=3.5,
                                              step=0.1,
                                              format="%.1f%%") / 100
                
                include_growth = st.checkbox("Incluir Crecimiento", value=True)
                growth_rate = 0.20
                if include_growth:
                    growth_rate = st.slider("Crecimiento Esperado", 
                                           min_value=0.0,
                                           max_value=100.0,
                                           value=20.0,
                                           step=5.0,
                                           format="%.0f%%") / 100
        
        # Calculate button
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if st.button("🚀 Calcular ROI", type="primary", use_container_width=True):
                with st.spinner("Ejecutando simulación Monte Carlo..."):
                    # Prepare inputs
                    inputs = {
                        'annual_revenue_clp': annual_revenue,
                        'monthly_orders': monthly_orders,
                        'avg_order_value_clp': avg_order_value,
                        'labor_costs_clp': labor_costs,
                        'shipping_costs_clp': shipping_costs,
                        'platform_fees_clp': platform_fees,
                        'error_costs_clp': error_costs,
                        'inventory_costs_clp': inventory_costs,
                        'investment_clp': investment,
                        'industry': industry,
                        'current_platforms': current_platforms,
                        'conversion_rate': conversion_rate
                    }
                    
                    # Save to session
                    st.session_state.client_data['company_name'] = company_name
                    
                    # Calculate ROI
                    calculator = EnhancedROICalculator()
                    start_time = time.time()
                    raw_results = calculator.calculate_roi(inputs)
                    results = adapt_roi_results(raw_results)
                    calc_time = time.time() - start_time
                    
                    # Save results
                    st.session_state.roi_results = results
                    st.session_state.calc_time = calc_time
                    
                    # Save to history
                    try:
                        history = HistoryManager()
                        history.add_calculation(
                            calculation_type='roi',
                            inputs=inputs,
                            results=results,
                            metadata={
                                'company_name': company_name,
                                'calculation_time': calc_time,
                                'timestamp': datetime.now().isoformat()
                            }
                        )
                    except Exception as e:
                        # Silently fail if history save fails
                        pass
                    
                    st.success(f"✅ Cálculo completado en {calc_time:.2f} segundos")
    
    with tab2:
        if st.session_state.roi_results:
            results = st.session_state.roi_results
            summary = results.get('executive_summary', {})
            
            st.markdown("### 📊 Resumen Ejecutivo")
            
            # Key metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                roi_value = summary.get('headline_roi', 0)
                delta_color = "normal" if roi_value > 100 else "inverse"
                st.metric("ROI Año 1", 
                         f"{roi_value:.0f}%",
                         f"{roi_value - 100:.0f}% sobre break-even",
                         delta_color=delta_color)
            
            with col2:
                payback = summary.get('payback_period_months', 0)
                st.metric("Período de Retorno", 
                         f"{payback:.1f} meses",
                         f"{12 - payback:.1f} meses antes del año" if payback < 12 else None)
            
            with col3:
                annual_savings = summary.get('annual_savings_clp', 0)
                st.metric("Ahorro Anual", 
                         format_millions(annual_savings),
                         f"{(annual_savings/annual_revenue)*100:.1f}% de ingresos")
            
            with col4:
                confidence = summary.get('confidence_level', 0)
                st.metric("Nivel de Confianza", 
                         f"{confidence:.0f}%",
                         "Alta precisión" if confidence > 90 else "Precisión moderada")
            
            # Scenario analysis
            st.markdown("### 📈 Análisis de Escenarios")
            
            scenarios = results.get('scenarios', {}).get('scenarios', {})
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                pessimistic = scenarios.get('pessimistic', {})
                st.info(f"""
                **Escenario Pesimista (25% prob)**
                - ROI: {pessimistic.get('roi_percentage', 0):.0f}%
                - Payback: {pessimistic.get('payback_months', 0):.1f} meses
                - Ahorro: {format_millions(pessimistic.get('annual_savings_clp', 0))}
                """)
            
            with col2:
                realistic = scenarios.get('realistic', {})
                st.success(f"""
                **Escenario Realista (60% prob)**
                - ROI: {realistic.get('roi_percentage', 0):.0f}%
                - Payback: {realistic.get('payback_months', 0):.1f} meses
                - Ahorro: {format_millions(realistic.get('annual_savings_clp', 0))}
                """)
            
            with col3:
                optimistic = scenarios.get('optimistic', {})
                st.success(f"""
                **Escenario Optimista (15% prob)**
                - ROI: {optimistic.get('roi_percentage', 0):.0f}%
                - Payback: {optimistic.get('payback_months', 0):.1f} meses
                - Ahorro: {format_millions(optimistic.get('annual_savings_clp', 0))}
                """)
            
            # Chilean specifics
            st.markdown("### 🇨🇱 Cálculos Mercado Chileno")
            
            chilean = results.get('chilean_specifics', {})
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Ahorro sin IVA", 
                         format_millions(chilean.get('savings_before_iva_clp', 0)))
            
            with col2:
                st.metric("IVA (19%)", 
                         format_millions(chilean.get('iva_amount_clp', 0)))
            
            with col3:
                st.metric("Total con IVA", 
                         format_millions(chilean.get('savings_with_iva_clp', 0)))
            
            with col4:
                st.metric("Ahorro en UF", 
                         f"{chilean.get('savings_in_uf', 0):,.0f} UF")
            
            # 3-year projection
            st.markdown("### 📅 Proyección a 3 Años")
            
            projection = results.get('three_year_projection', {})
            
            proj_data = []
            for year in range(1, 4):
                year_data = projection.get(f'year_{year}', {})
                proj_data.append({
                    'Año': year,
                    'Ahorro Anual (M CLP)': year_data.get('annual_savings_clp', 0) / 1000000,
                    'ROI Acumulado (%)': year_data.get('roi_percentage', 0),
                    'Beneficio Neto (M CLP)': year_data.get('net_benefit_clp', 0) / 1000000
                })
            
            df_proj = pd.DataFrame(proj_data)
            st.dataframe(df_proj.style.format({
                'Ahorro Anual (M CLP)': '{:.1f}',
                'ROI Acumulado (%)': '{:.0f}',
                'Beneficio Neto (M CLP)': '{:.1f}'
            }), use_container_width=True)
            
        else:
            st.info("👈 Configure los parámetros en la pestaña 'Datos de Entrada' y presione 'Calcular ROI'")
    
    with tab3:
        if st.session_state.roi_results:
            results = st.session_state.roi_results
            summary = results.get('executive_summary', {})
            
            # ROI Gauge
            col1, col2 = st.columns(2)
            
            with col1:
                st.plotly_chart(create_roi_gauge(summary.get('headline_roi', 0)), 
                              use_container_width=True)
            
            with col2:
                # Scenario chart
                scenarios = results.get('scenarios', {}).get('scenarios', {})
                if scenarios:
                    st.plotly_chart(create_scenario_chart(scenarios), 
                                  use_container_width=True)
            
            # Savings breakdown
            col1, col2 = st.columns(2)
            
            with col1:
                improvements = results.get('improvements', {})
                savings_chart = create_savings_breakdown_chart(improvements)
                if savings_chart:
                    st.plotly_chart(savings_chart, use_container_width=True)
            
            with col2:
                # Payback timeline
                payback_months = summary.get('payback_period_months', 0)
                monthly_savings = improvements.get('total_monthly_savings_clp', 0)
                investment_amount = st.session_state.client_data.get('investment_clp', 20000000)
                
                if payback_months and monthly_savings:
                    st.plotly_chart(
                        create_payback_timeline(payback_months, investment_amount, monthly_savings),
                        use_container_width=True
                    )
            
            # Monte Carlo distribution
            st.markdown("### 📊 Distribución Monte Carlo")
            
            monte_carlo = results.get('monte_carlo', {})
            if monte_carlo.get('roi_distribution'):
                roi_dist = monte_carlo['roi_distribution']
                
                fig = px.histogram(x=roi_dist, nbins=50,
                                  title='Distribución de ROI (10,000 simulaciones)',
                                  labels={'x': 'ROI (%)', 'y': 'Frecuencia'},
                                  color_discrete_sequence=['#f5b800'])
                
                # Add confidence interval lines
                percentiles = monte_carlo.get('percentiles', {})
                if percentiles:
                    fig.add_vline(x=percentiles.get('p5', 0), line_dash="dash", 
                                line_color="red", annotation_text="5%")
                    fig.add_vline(x=percentiles.get('p50', 0), line_dash="solid", 
                                line_color="green", annotation_text="Mediana")
                    fig.add_vline(x=percentiles.get('p95', 0), line_dash="dash", 
                                line_color="red", annotation_text="95%")
                
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
        else:
            st.info("👈 Primero debe calcular el ROI para ver las visualizaciones")
    
    with tab4:
        if st.session_state.roi_results:
            results = st.session_state.roi_results
            recommendations = results.get('recommendations', [])
            
            st.markdown("### 🎯 Recomendaciones Personalizadas")
            
            if recommendations:
                for i, rec in enumerate(recommendations, 1):
                    priority_color = {
                        'CRÍTICA': '🔴',
                        'ALTA': '🟠',
                        'MEDIA': '🟡',
                        'BAJA': '🟢'
                    }.get(rec.get('priority', 'MEDIA'), '⚪')
                    
                    with st.expander(f"{priority_color} {i}. {rec.get('title', 'Recomendación')}"):
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.markdown(f"**Descripción:**")
                            st.write(rec.get('description', rec.get('expected_impact', 'N/A')))
                            
                            st.markdown(f"**Tiempo de Implementación:** {rec.get('implementation_time', 'N/A')}")
                            
                            if rec.get('expected_savings_clp', 0) > 0:
                                st.markdown(f"**Ahorro Esperado:** {format_millions(rec['expected_savings_clp'])}/mes")
                        
                        with col2:
                            st.markdown(f"**Prioridad:** {rec.get('priority', 'N/A')}")
                            st.markdown(f"**Complejidad:** {rec.get('complexity', 'Media')}")
                            st.markdown(f"**ROI Impacto:** {rec.get('roi_impact', '+20')}%")
                
                # Action plan
                st.markdown("### 📋 Plan de Acción Sugerido")
                
                st.markdown("""
                **Fase 1: Quick Wins (Semanas 1-2)**
                - Implementar validación de datos automática
                - Configurar alertas de inventario
                - Optimizar proceso de checkout
                
                **Fase 2: Integraciones (Semanas 3-4)**
                - Integrar ERP con plataforma e-commerce
                - Conectar con marketplaces
                - Automatizar fulfillment
                
                **Fase 3: Optimización (Semanas 5-8)**
                - Implementar machine learning para precios
                - Optimizar rutas de envío
                - Personalización de experiencia cliente
                """)
                
                # Export options
                st.markdown("### 💾 Exportar Recomendaciones")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("📄 Exportar PDF", use_container_width=True):
                        st.info("Generando PDF con recomendaciones...")
                
                with col2:
                    if st.button("📊 Exportar Excel", use_container_width=True):
                        st.info("Exportando a Excel...")
                
                with col3:
                    if st.button("📧 Enviar por Email", use_container_width=True):
                        st.info("Preparando email...")
            
            else:
                st.warning("No hay recomendaciones disponibles para estos parámetros")
        
        else:
            st.info("👈 Calcule el ROI para obtener recomendaciones personalizadas")
    
    # Add Save/Load section if database is available
    if 'roi_results' in st.session_state and st.session_state.roi_results and db_available:
        st.divider()
        st.subheader("💾 Gestión de Cálculos")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💾 Guardar Cálculo", type="primary", use_container_width=True):
                save_calculation_to_db(st.session_state.client_data, st.session_state.roi_results)
        
        with col2:
            if st.button("📚 Ver Historial", use_container_width=True):
                st.switch_page("pages/history.py")
        
        with col3:
            # Export as JSON
            json_str = json.dumps(st.session_state.roi_results, indent=2, ensure_ascii=False)
            st.download_button(
                label="📥 Descargar JSON",
                data=json_str,
                file_name=f"roi_calc_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )

def save_calculation_to_db(client_data, results):
    """Save calculation to database"""
    try:
        session = get_session()
        
        # Create new calculation record
        calc = Calculation(
            company_name=client_data.get('company_name', 'Sin nombre'),
            annual_revenue=client_data.get('annual_revenue_clp', 0),
            monthly_orders=client_data.get('monthly_orders', 0),
            avg_order_value=client_data.get('avg_order_value_clp', 0),
            labor_costs=client_data.get('labor_costs_clp', 0),
            shipping_costs=client_data.get('shipping_costs_clp', 0),
            error_costs=client_data.get('error_costs_clp', 0),
            inventory_costs=client_data.get('inventory_costs_clp', 0),
            service_investment=client_data.get('investment_clp', 0),
            results=results,
            notes=client_data.get('notes', ''),
            tags='roi_calculator,chilean_market'
        )
        
        session.add(calc)
        session.commit()
        
        st.success(f"✅ Cálculo guardado exitosamente (ID: {calc.id})")
        
        # Store the ID in session state for reference
        st.session_state.last_saved_id = calc.id
        
        session.close()
        
    except Exception as e:
        st.error(f"❌ Error al guardar: {str(e)}")
        if db_available:
            print(f"Database save error: {e}")

# Run the page only if this file is run directly
if __name__ == "__main__":
    show_roi_calculator()
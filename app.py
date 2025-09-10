#!/usr/bin/env python3
"""
Chilean E-commerce Sales Toolkit - Web Dashboard
Professional consulting tools for Chilean SMEs
"""

import streamlit as st
import sys
import os
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# Add src to path
sys.path.insert(0, 'src')

# Import metrics aggregator for real data
try:
    from metrics_aggregator import MetricsAggregator
except ImportError:
    MetricsAggregator = None

# Page configuration
st.set_page_config(
    page_title="Chilean E-commerce Sales Toolkit",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for black and gold theme
st.markdown("""
<style>
    /* Black and Gold Theme */
    .stApp {
        background-color: #0a0a0a;
    }
    
    .main {
        background-color: #0a0a0a;
        color: #ffffff;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #f5b800 !important;
        font-weight: 700;
    }
    
    h1 {
        border-bottom: 3px solid #f5b800;
        padding-bottom: 10px;
        margin-bottom: 30px;
    }
    
    /* Metric cards */
    [data-testid="metric-container"] {
        background-color: #1a1a1a;
        border: 1px solid #f5b800;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(245, 184, 0, 0.3);
    }
    
    [data-testid="metric-container"] [data-testid="metric-label"] {
        color: #f5b800 !important;
    }
    
    [data-testid="metric-container"] [data-testid="metric-value"] {
        color: #ffffff !important;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #f5b800;
        color: #0a0a0a;
        border: 2px solid #f5b800;
        padding: 0.75rem 1.5rem;
        font-weight: 700;
        border-radius: 5px;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        background-color: transparent;
        color: #f5b800;
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(245, 184, 0, 0.4);
    }
    
    /* Alert boxes */
    .stAlert {
        background-color: #1a1a1a;
        border: 1px solid #f5b800;
        color: #ffffff;
    }
    
    /* Info boxes */
    .info-box {
        background-color: #1a1a1a;
        border: 2px solid #f5b800;
        padding: 20px;
        margin: 20px 0;
        border-radius: 10px;
        color: #ffffff;
    }
    
    .info-box h3 {
        color: #f5b800 !important;
        margin-top: 0;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #1a1a1a;
        border-right: 2px solid #f5b800;
    }
    
    section[data-testid="stSidebar"] .stButton > button {
        width: 100%;
        background-color: transparent;
        border: 1px solid #f5b800;
        color: #f5b800;
    }
    
    section[data-testid="stSidebar"] .stButton > button:hover {
        background-color: #f5b800;
        color: #0a0a0a;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        background-color: #1a1a1a;
        padding: 10px;
        border-radius: 10px;
        border: 1px solid #f5b800;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
        background-color: #0a0a0a;
        border: 1px solid #333;
        border-radius: 5px;
        color: #ffffff;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #f5b800;
        color: #0a0a0a;
        border: 1px solid #f5b800;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #1a1a1a;
        border: 1px solid #f5b800;
        border-radius: 5px;
        color: #f5b800;
        font-weight: 600;
    }
    
    .streamlit-expanderContent {
        background-color: #1a1a1a;
        border: 1px solid #333;
        border-top: none;
    }
    
    /* Progress bar */
    .stProgress > div > div > div > div {
        background-color: #f5b800;
    }
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select {
        background-color: #1a1a1a;
        color: #ffffff;
        border: 1px solid #f5b800;
    }
    
    /* Labels */
    .stTextInput > label,
    .stNumberInput > label,
    .stSelectbox > label,
    .stMultiSelect > label,
    .stSlider > label,
    .stRadio > label {
        color: #f5b800 !important;
    }
    
    /* Dataframes */
    .dataframe {
        background-color: #1a1a1a;
        color: #ffffff;
    }
    
    /* Markdown text */
    .stMarkdown {
        color: #ffffff;
    }
    
    /* Gold accent class */
    .gold-text { color: #f5b800 !important; }
    .gold-border { border-color: #f5b800 !important; }
    
    /* Fix text visibility */
    p, span, div, li {
        color: #ffffff;
    }
    
    /* Fix multiselect */
    [data-baseweb="select"] {
        background-color: #1a1a1a;
    }
    
    /* Success/Info/Warning boxes */
    .stSuccess, .stInfo, .stWarning, .stError {
        background-color: #1a1a1a;
        color: #ffffff;
    }
    
    /* Code blocks */
    .stCodeBlock {
        background-color: #1a1a1a;
        border: 1px solid #333;
    }
    
    /* File uploader */
    .stFileUploader {
        background-color: #1a1a1a;
        border: 1px dashed #f5b800;
    }
    
    /* Plotly charts dark theme */
    .js-plotly-plot {
        background-color: #0a0a0a;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'home'
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

def format_clp(amount):
    """Format amount as Chilean Pesos"""
    return f"${amount:,.0f} CLP"

def show_home_page():
    """Display the home landing page"""
    
    # Hero section
    st.markdown("""
    <div style='text-align: center; padding: 50px 0; background-color: #1a1a1a; border-radius: 10px; border: 2px solid #f5b800; margin-bottom: 30px;'>
        <h1 style='font-size: 3.5em; color: #f5b800; margin-bottom: 20px; border: none;'>
            🚀 Chilean E-commerce Sales Toolkit
        </h1>
        <p style='font-size: 1.3em; color: #ffffff; margin-bottom: 40px;'>
            Herramientas profesionales de consultoría para acelerar el crecimiento de su e-commerce
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Key metrics
    # Get real metrics from aggregator
    metrics = {
        'avg_roi_display': "Sin datos",
        'avg_payback_display': "Sin datos",
        'avg_monthly_savings_display': "Sin datos",
        'total_clients_display': "0",
        'monthly_growth_display': "Sin datos",
        'has_data': False
    }
    
    if MetricsAggregator:
        try:
            aggregator = MetricsAggregator()
            metrics = aggregator.get_dashboard_metrics()
        except Exception as e:
            pass  # Use default empty metrics
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="ROI Promedio",
            value=metrics['avg_roi_display'],
            delta="Calculado real" if metrics['has_data'] else "Sin cálculos",
            help="ROI promedio real de todos los cálculos"
        )
    
    with col2:
        st.metric(
            label="Tiempo de Retorno",
            value=metrics['avg_payback_display'],
            delta="Mediana real" if metrics['has_data'] else "Sin datos",
            help="Tiempo medio real de recuperación"
        )
    
    with col3:
        st.metric(
            label="Ahorro Mensual",
            value=metrics['avg_monthly_savings_display'],
            delta="Promedio real" if metrics['has_data'] else "Sin datos",
            help="Ahorro mensual promedio calculado"
        )
    
    with col4:
        st.metric(
            label="Clientes Analizados",
            value=metrics['total_clients_display'],
            delta=metrics['monthly_growth_display'] if metrics['has_data'] else "Sin cambios",
            help="Total de empresas analizadas"
        )
    
    # Show notice if no data
    if not metrics.get('has_data', False):
        st.info("💡 Las métricas se actualizarán automáticamente cuando realices cálculos de ROI")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Three main tools
    st.markdown("## 🎯 Nuestras Herramientas Principales")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class='info-box'>
            <h3>📊 Calculadora ROI Avanzada</h3>
            <p>Análisis detallado con simulación Monte Carlo para proyectar el retorno de inversión con 95% de confianza.</p>
            <ul style='color: #ffffff;'>
                <li>10,000 iteraciones Monte Carlo</li>
                <li>Escenarios múltiples</li>
                <li>Proyección a 3 años</li>
                <li>Benchmarks de industria</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🚀 Calcular ROI", key="btn_roi", use_container_width=True):
            st.switch_page("pages/roi_calculator.py")
    
    with col2:
        st.markdown("""
        <div class='info-box'>
            <h3>📋 Evaluación Rápida</h3>
            <p>Califique prospectos en 15 minutos con nuestro sistema de evaluación inteligente.</p>
            <ul style='color: #ffffff;'>
                <li>65+ preguntas diagnósticas</li>
                <li>Scoring A/B/C/D</li>
                <li>Análisis de madurez digital</li>
                <li>Recomendaciones personalizadas</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        if st.button("📋 Evaluar Prospecto", key="btn_assess", use_container_width=True):
            st.switch_page("pages/assessment_tool.py")
    
    with col3:
        st.markdown("""
        <div class='info-box'>
            <h3>📄 Generador de Propuestas</h3>
            <p>Cree propuestas profesionales en minutos con exportación a PDF y PowerPoint.</p>
            <ul style='color: #ffffff;'>
                <li>Plantillas ejecutivas</li>
                <li>Paquetes de servicios</li>
                <li>Exportación PDF/PPT</li>
                <li>One-pagers automáticos</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        if st.button("📄 Generar Propuesta", key="btn_proposal", use_container_width=True):
            st.switch_page("pages/proposal_generator.py")
    
    # Success stories - from real data
    st.markdown("## 🏆 Casos de Éxito")
    
    # Get top performers from real data
    top_performers = aggregator.get_top_performers(limit=2)
    
    if len(top_performers) >= 2:
        col1, col2 = st.columns(2)
        
        with col1:
            perf = top_performers[0]
            monthly_savings = perf['savings'] / 12
            
            # Format currency
            if monthly_savings >= 1_000_000:
                savings_display = f"${monthly_savings/1_000_000:.1f}M CLP/mes"
            else:
                savings_display = f"${monthly_savings/1_000:.0f}K CLP/mes"
            
            st.markdown(f"""
            <div style='background-color: #1a1a1a; padding: 20px; border-radius: 10px; border: 1px solid #f5b800;'>
                <h4 style='color: #f5b800;'>📈 {perf['company']}</h4>
                <p style='color: #ffffff;'><strong style='color: #f5b800;'>Resultado:</strong> {perf['roi']:.0f}% ROI</p>
                <p style='color: #ffffff;'><strong style='color: #f5b800;'>Ahorro:</strong> {savings_display}</p>
                <p style='color: #ffffff;'><strong style='color: #f5b800;'>Retorno:</strong> {perf['payback']:.1f} meses</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            perf = top_performers[1]
            monthly_savings = perf['savings'] / 12
            
            # Format currency
            if monthly_savings >= 1_000_000:
                savings_display = f"${monthly_savings/1_000_000:.1f}M CLP/mes"
            else:
                savings_display = f"${monthly_savings/1_000:.0f}K CLP/mes"
            
            st.markdown(f"""
            <div style='background-color: #1a1a1a; padding: 20px; border-radius: 10px; border: 1px solid #f5b800;'>
                <h4 style='color: #f5b800;'>📦 {perf['company']}</h4>
                <p style='color: #ffffff;'><strong style='color: #f5b800;'>Resultado:</strong> {perf['roi']:.0f}% ROI</p>
                <p style='color: #ffffff;'><strong style='color: #f5b800;'>Ahorro:</strong> {savings_display}</p>
                <p style='color: #ffffff;'><strong style='color: #f5b800;'>Retorno:</strong> {perf['payback']:.1f} meses</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        # If no real data available, show placeholder
        st.info("📊 Los casos de éxito se mostrarán cuando haya cálculos realizados.")
    
    # Features
    st.markdown("## ✨ Características Principales")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div style='color: #ffffff;'>
        <strong style='color: #f5b800;'>🇨🇱 100% Chileno</strong><br>
        • Cálculos en CLP<br>
        • IVA incluido<br>
        • Conversión UF
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='color: #ffffff;'>
        <strong style='color: #f5b800;'>⚡ Ultra Rápido</strong><br>
        • Resultados en segundos<br>
        • Interfaz intuitiva<br>
        • Sin instalación
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style='color: #ffffff;'>
        <strong style='color: #f5b800;'>📊 Data-Driven</strong><br>
        • IA y Machine Learning<br>
        • Benchmarks reales<br>
        • Análisis predictivo
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div style='color: #ffffff;'>
        <strong style='color: #f5b800;'>🎯 Resultados</strong><br>
        • ROI garantizado<br>
        • Soporte incluido<br>
        • Actualizaciones gratis
        </div>
        """, unsafe_allow_html=True)
    
    # Footer CTA
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align: center; background-color: #1a1a1a; color: white; padding: 30px; border-radius: 10px; border: 2px solid #f5b800;'>
        <h2 style='color: #f5b800;'>¿Listo para transformar su negocio?</h2>
        <p style='font-size: 1.2em; color: #ffffff;'>Comience ahora con nuestras herramientas profesionales</p>
    </div>
    """, unsafe_allow_html=True)

def main():
    """Main application"""
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("""
        <div style='text-align: center; padding: 20px; background-color: #1a1a1a; border-radius: 10px; border: 1px solid #f5b800;'>
            <h2 style='color: #f5b800; margin: 0;'>E-Commerce Toolkit</h2>
            <p style='color: #ffffff; margin: 5px 0;'>Professional Edition</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.markdown("### 🧭 Herramientas Principales")
        
        if st.button("🏠 Inicio", use_container_width=True):
            st.session_state.current_page = 'home'
            st.rerun()
            
        if st.button("📊 Calculadora ROI", use_container_width=True):
            st.switch_page("pages/roi_calculator.py")
            
        if st.button("📋 Evaluación Rápida", use_container_width=True):
            st.switch_page("pages/assessment_tool.py")
            
        if st.button("📄 Generar Propuesta", use_container_width=True):
            st.switch_page("pages/proposal_generator.py")
        
        st.markdown("---")
        st.markdown("### 🛠️ Herramientas Avanzadas")
        
        if st.button("💱 Conversor de Moneda", use_container_width=True):
            st.switch_page("pages/currency_converter.py")
            
        if st.button("🧮 Calculadora de Impuestos", use_container_width=True):
            st.switch_page("pages/tax_calculator.py")
            
        if st.button("💰 Optimizador de Costos", use_container_width=True):
            st.switch_page("pages/cost_optimizer.py")
            
        if st.button("📈 Análisis Punto de Equilibrio", use_container_width=True):
            st.switch_page("pages/breakeven_analyzer.py")
            
        if st.button("⚡ Procesador por Lotes", use_container_width=True):
            st.switch_page("pages/batch_processor.py")
        
        st.markdown("---")
        st.markdown("### 💾 Gestión de Datos")
        
        if st.button("📚 Historial", use_container_width=True):
            st.switch_page("pages/history.py")
            
        if st.button("📋 Plantillas", use_container_width=True):
            st.switch_page("pages/templates.py")
        
        st.markdown("---")
        
        # Session info
        st.markdown("### 📊 Sesión Actual")
        
        if st.session_state.client_data:
            st.success(f"Cliente: {st.session_state.client_data.get('company_name', 'N/A')}")
        
        if st.session_state.roi_results:
            roi = st.session_state.roi_results.get('executive_summary', {}).get('headline_roi', 0)
            st.info(f"ROI Calculado: {roi:.0f}%")
        
        if st.session_state.assessment_results:
            score = st.session_state.assessment_results.get('qualification', {}).get('score', 0)
            st.info(f"Score: {score}/100")
        
        st.markdown("---")
        
        # Export options
        st.markdown("### 💾 Exportar Datos")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📥 Excel", use_container_width=True):
                st.info("Exportando a Excel...")
        
        with col2:
            if st.button("📄 PDF", use_container_width=True):
                st.info("Generando PDF...")
        
        st.markdown("---")
        
        # Help section
        with st.expander("❓ Ayuda"):
            st.markdown("""
            <div style='color: #ffffff;'>
            <strong style='color: #f5b800;'>Flujo recomendado:</strong><br>
            1. Evaluación Rápida (15 min)<br>
            2. Calculadora ROI (5 min)<br>
            3. Generar Propuesta (2 min)<br>
            <br>
            <strong style='color: #f5b800;'>Soporte:</strong><br>
            📧 soporte@toolkit.cl<br>
            📱 +56 9 1234 5678<br>
            💬 Chat en vivo
            </div>
            """, unsafe_allow_html=True)
        
        # Footer
        st.markdown("---")
        st.caption(f"v2.0.0 | {datetime.now().strftime('%Y')} © E-Commerce Toolkit")
    
    # Main content area - only show home page
    # All other pages use st.switch_page() for navigation
    if st.session_state.current_page == 'home':
        show_home_page()
    else:
        # Reset to home if somehow we get an unknown page
        st.session_state.current_page = 'home'
        show_home_page()

if __name__ == "__main__":
    main()
"""
Chilean E-commerce Sales Toolkit Dashboard
==========================================
A comprehensive Streamlit web application for ROI analysis, assessments, and proposal generation.
Author: Sales Toolkit Team
Version: 1.0.0
"""

import streamlit as st
import sys
import os
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go

# Add the parent directory to Python path to import our modules
sys.path.append(str(Path(__file__).parent.parent / "src"))

from utils.session_manager import SessionManager
from utils.visualizations import ChartGenerator
from utils.export_handler import ExportHandler

# Page configuration
st.set_page_config(
    page_title="Chilean E-commerce Sales Toolkit",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/your-repo/help',
        'Report a bug': 'https://github.com/your-repo/issues',
        'About': "Chilean E-commerce Sales Toolkit v1.0.0"
    }
)

# Load custom CSS
def load_css():
    """Load custom CSS styling"""
    css_file = Path(__file__).parent / "styles" / "main.css"
    if css_file.exists():
        with open(css_file) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    else:
        # Fallback inline CSS if file doesn't exist
        st.markdown("""
        <style>
        .main {
            padding-top: 2rem;
        }
        .stApp > header {
            background-color: transparent;
        }
        .stMetric > div > div > div > div {
            font-size: 1.2rem;
        }
        .metric-card {
            background: white;
            padding: 1rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin: 0.5rem 0;
        }
        .hero-section {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            text-align: center;
        }
        .feature-card {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin: 1rem 0;
            border-left: 4px solid #667eea;
        }
        .sidebar .sidebar-content {
            background: linear-gradient(180deg, #f8f9ff 0%, #e8f0fe 100%);
        }
        .success-banner {
            background: linear-gradient(90deg, #00d4aa, #00b894);
            color: white;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
        }
        </style>
        """, unsafe_allow_html=True)

def initialize_session():
    """Initialize session state and managers"""
    if 'session_manager' not in st.session_state:
        st.session_state.session_manager = SessionManager()
    
    if 'chart_generator' not in st.session_state:
        st.session_state.chart_generator = ChartGenerator()
    
    if 'export_handler' not in st.session_state:
        st.session_state.export_handler = ExportHandler()
    
    # Initialize page state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'home'

def create_sidebar():
    """Create the sidebar navigation"""
    with st.sidebar:
        st.image("https://via.placeholder.com/200x80/667eea/white?text=E-commerce+Toolkit", 
                caption="Chilean E-commerce Sales Toolkit")
        
        st.markdown("---")
        
        # Navigation menu
        page = st.selectbox(
            "🧭 Navegación",
            ["🏠 Inicio", "📊 Calculadora ROI", "📋 Evaluación Rápida", "📄 Generador Propuestas"],
            key="page_selector"
        )
        
        # Update current page
        page_mapping = {
            "🏠 Inicio": "home",
            "📊 Calculadora ROI": "roi_calculator",
            "📋 Evaluación Rápida": "assessment_tool",
            "📄 Generador Propuestas": "proposal_generator"
        }
        st.session_state.current_page = page_mapping.get(page, "home")
        
        st.markdown("---")
        
        # Session info
        if st.session_state.session_manager.get_session_data():
            st.success(f"✅ Sesión activa")
            session_data = st.session_state.session_manager.get_session_data()
            st.caption(f"Datos guardados: {len(session_data)} elementos")
            
            if st.button("🗑️ Limpiar Sesión", type="secondary", use_container_width=True):
                st.session_state.session_manager.clear_session()
                st.rerun()
        else:
            st.info("Nueva sesión iniciada")
        
        st.markdown("---")
        
        # Quick stats if available
        session_data = st.session_state.session_manager.get_session_data()
        if session_data.get('roi_data'):
            roi_data = session_data['roi_data']
            st.markdown("### 📈 Resumen ROI")
            if roi_data.get('expected_roi'):
                st.metric("ROI Esperado", f"{roi_data['expected_roi']:.1f}%")
            if roi_data.get('monthly_revenue'):
                st.metric("Ingresos Mensuales", f"${roi_data['monthly_revenue']:,.0f} CLP")

def render_home_page():
    """Render the home page"""
    # Hero section
    st.markdown("""
    <div class="hero-section">
        <h1>🛍️ Chilean E-commerce Sales Toolkit</h1>
        <h3>Herramientas profesionales para análisis de ROI y generación de propuestas</h3>
        <p>Optimiza tus ventas de e-commerce con análisis avanzados, evaluaciones rápidas y propuestas personalizadas</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Key metrics overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #667eea;">📊</h3>
            <h4>ROI Calculator</h4>
            <p>Análisis Monte Carlo avanzado</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #667eea;">⚡</h3>
            <h4>Evaluación Rápida</h4>
            <p>Cuestionario inteligente</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #667eea;">📄</h3>
            <h4>Generador Propuestas</h4>
            <p>Documentos profesionales</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #667eea;">📈</h3>
            <h4>Visualizaciones</h4>
            <p>Gráficos interactivos</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Features overview
    st.markdown("## 🚀 Características Principales")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h4>📊 Calculadora ROI Avanzada</h4>
            <ul>
                <li>Simulación Monte Carlo con 10,000 iteraciones</li>
                <li>Análisis de riesgo probabilístico</li>
                <li>Gráficos interactivos en tiempo real</li>
                <li>Exportación de reportes PDF</li>
                <li>Análisis de sensibilidad</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <h4>📋 Evaluación Rápida</h4>
            <ul>
                <li>Cuestionario paso a paso</li>
                <li>Puntuación automática</li>
                <li>Recomendaciones personalizadas</li>
                <li>Análisis de madurez digital</li>
                <li>Identificación de oportunidades</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h4>📄 Generador de Propuestas</h4>
            <ul>
                <li>Templates profesionales</li>
                <li>Vista previa en tiempo real</li>
                <li>Exportación PDF y Word</li>
                <li>Personalización completa</li>
                <li>Integración con cálculos ROI</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <h4>🎯 Características Técnicas</h4>
            <ul>
                <li>Persistencia de sesión</li>
                <li>Validación de entrada robusta</li>
                <li>Diseño responsivo</li>
                <li>Contexto del mercado chileno</li>
                <li>Moneda CLP nativa</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Getting started section
    st.markdown("## 🎯 Comenzar Ahora")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Ir a Calculadora ROI", type="primary", use_container_width=True):
            st.session_state.current_page = "roi_calculator"
            st.rerun()
    
    with col2:
        if st.button("📋 Evaluación Rápida", type="primary", use_container_width=True):
            st.session_state.current_page = "assessment_tool"
            st.rerun()
    
    with col3:
        if st.button("📄 Generar Propuesta", type="primary", use_container_width=True):
            st.session_state.current_page = "proposal_generator"
            st.rerun()
    
    # Sample visualization
    st.markdown("## 📈 Ejemplo de Visualización")
    
    # Create sample ROI projection chart
    try:
        import numpy as np
        
        months = list(range(1, 25))  # 24 months
        base_revenue = 500000  # 500k CLP
        growth_rate = 0.15  # 15% monthly growth
        revenues = [base_revenue * (1 + growth_rate) ** (month - 1) for month in months]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=months,
            y=revenues,
            mode='lines+markers',
            name='Proyección de Ingresos',
            line=dict(color='#667eea', width=3),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title="Ejemplo: Proyección de Ingresos E-commerce (24 meses)",
            xaxis_title="Meses",
            yaxis_title="Ingresos (CLP)",
            template="plotly_white",
            height=400
        )
        
        # Format y-axis as Chilean pesos
        fig.update_layout(
            yaxis=dict(
                tickformat='.0f',
                tickprefix='$',
                ticksuffix=' CLP'
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    except ImportError:
        st.info("Visualización no disponible. Por favor instala las dependencias completas.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 2rem; background: #f8f9fa; border-radius: 10px; margin-top: 2rem;">
        <h5>Chilean E-commerce Sales Toolkit</h5>
        <p>Desarrollado específicamente para el mercado chileno • Versión 1.0.0</p>
        <p>💡 <strong>Tip:</strong> Utiliza la barra lateral para navegar entre herramientas y mantener tu sesión activa</p>
    </div>
    """, unsafe_allow_html=True)

def main():
    """Main application function"""
    # Load CSS
    load_css()
    
    # Initialize session
    initialize_session()
    
    # Create sidebar
    create_sidebar()
    
    # Route to appropriate page
    if st.session_state.current_page == "home":
        render_home_page()
    elif st.session_state.current_page == "roi_calculator":
        # Import and render ROI calculator
        try:
            from pages.roi_calculator import render_roi_calculator
            render_roi_calculator()
        except ImportError as e:
            st.error(f"Error loading ROI Calculator: {e}")
            st.info("Please ensure all required files are in the pages directory.")
    elif st.session_state.current_page == "assessment_tool":
        # Import and render assessment tool
        try:
            from pages.assessment_tool import render_assessment_tool
            render_assessment_tool()
        except ImportError as e:
            st.error(f"Error loading Assessment Tool: {e}")
            st.info("Please ensure all required files are in the pages directory.")
    elif st.session_state.current_page == "proposal_generator":
        # Import and render proposal generator
        try:
            from pages.proposal_generator import render_proposal_generator
            render_proposal_generator()
        except ImportError as e:
            st.error(f"Error loading Proposal Generator: {e}")
            st.info("Please ensure all required files are in the pages directory.")

if __name__ == "__main__":
    main()
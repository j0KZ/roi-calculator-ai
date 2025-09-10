#!/usr/bin/env python3
"""
Shared navigation component for all pages
"""

import streamlit as st
from datetime import datetime

def show_navigation():
    """Display consistent navigation sidebar across all pages"""
    
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
            st.switch_page("app.py")
            
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
        
        if st.session_state.get('client_data'):
            company = st.session_state.client_data.get('company_name', 'N/A')
            if company:
                st.success(f"Cliente: {company}")
        
        if st.session_state.get('roi_results'):
            roi = st.session_state.roi_results.get('executive_summary', {}).get('headline_roi', 0)
            if roi > 0:
                st.info(f"ROI Calculado: {roi:.0f}%")
        
        if st.session_state.get('assessment_results'):
            score = st.session_state.assessment_results.get('qualification', {}).get('score', 0)
            if score > 0:
                st.info(f"Score: {score}/100")
        
        st.markdown("---")
        
        # Export options
        st.markdown("### 💾 Exportar Datos")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📥 Excel", use_container_width=True, key="export_excel"):
                st.info("Exportando a Excel...")
        
        with col2:
            if st.button("📄 PDF", use_container_width=True, key="export_pdf"):
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
        st.caption(f"v2.1.0 | {datetime.now().strftime('%Y')} © E-Commerce Toolkit")
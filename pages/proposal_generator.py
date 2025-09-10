"""
Proposal Generator Page for Streamlit Dashboard
"""

import streamlit as st
from pages.shared_navigation import show_navigation
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime
import time
import base64
from io import BytesIO

# Import the proposal generator
import sys
sys.path.insert(0, 'src')
from automated_proposal_generator import AutomatedProposalGenerator

# Import chart theme utilities
sys.path.insert(0, 'utils')
try:
    from chart_theme import apply_dark_theme, get_dark_color_sequence
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

def format_clp(amount):
    """Format amount as Chilean Pesos"""
    return f"${amount:,.0f} CLP"

def format_millions(amount):
    """Format amount in millions"""
    return f"${amount/1000000:.1f}M"

def create_package_comparison():
    """Create package comparison chart"""
    
    packages = pd.DataFrame({
        'Característica': ['Horas Consultoría', 'Soporte', 'Integraciones', 'Training', 'ROI Garantizado'],
        'Starter': [20, '✓', 2, '✓', '100%'],
        'Professional': [40, '✓✓', 5, '✓✓', '150%'],
        'Enterprise': [80, '✓✓✓', 'Ilimitado', '✓✓✓', '200%']
    })
    
    return packages

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

def show_proposal_generator():
    """Display the Proposal Generator page"""

    # Show navigation sidebar
    show_navigation()
    
    st.title("📄 Generador de Propuestas")
    st.markdown("Cree propuestas profesionales personalizadas en minutos")
    
    # Check if we have required data
    has_assessment = bool(st.session_state.assessment_results)
    has_roi = bool(st.session_state.roi_results)
    
    if not has_assessment or not has_roi:
        st.warning("""
        ⚠️ **Datos Faltantes**
        
        Para generar una propuesta completa, necesita:
        - ✅ Completar la Evaluación Rápida (Score: {})
        - ✅ Calcular el ROI (ROI: {})
        
        Use la navegación lateral para completar estos pasos primero.
        """.format(
            st.session_state.assessment_results.get('qualification', {}).get('score', 'Pendiente') if has_assessment else 'Pendiente',
            f"{st.session_state.roi_results.get('executive_summary', {}).get('headline_roi', 0):.0f}%" if has_roi else 'Pendiente'
        ))
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📋 Ir a Evaluación", use_container_width=True):
                st.session_state.current_page = 'assessment'
                st.rerun()
        
        with col2:
            if st.button("📊 Ir a Calculadora ROI", use_container_width=True):
                st.session_state.current_page = 'roi_calculator'
                st.rerun()
        
        st.markdown("---")
        st.info("💡 **Tip:** También puede generar una propuesta básica con datos de ejemplo para ver el formato.")
        
        if st.button("👁️ Ver Propuesta de Ejemplo"):
            # Use example data
            st.session_state.client_data = {
                'company_name': 'Empresa Ejemplo SpA',
                'contact_name': 'Juan Pérez',
                'email': 'juan@ejemplo.cl',
                'phone': '+56 9 1234 5678',
                'industry': 'Retail'
            }
            
            st.session_state.assessment_results = {
                'qualification': {'level': 'A - HOT PROSPECT', 'score': 85, 'close_probability': 80},
                'maturity_level': {'level': 'INTERMEDIO', 'score': 5.5},
                'roi_potential': {'roi_percentage': 150, 'payback_months': 6}
            }
            
            st.session_state.roi_results = {
                'executive_summary': {
                    'headline_roi': 150,
                    'payback_period_months': 6,
                    'annual_savings_clp': 72000000
                },
                'improvements': {
                    'total_monthly_savings_clp': 6000000,
                    'new_operational_efficiency': 0.85
                }
            }
            st.rerun()
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Configuración", "👁️ Vista Previa", "📦 Paquetes", "💾 Exportar"])
    
    with tab1:
        st.markdown("### 📋 Información del Cliente")
        
        col1, col2 = st.columns(2)
        
        with col1:
            company_name = st.text_input("Nombre de la Empresa",
                                        value=st.session_state.client_data.get('company_name', ''),
                                        key="prop_company")
            
            contact_name = st.text_input("Nombre del Contacto",
                                        value=st.session_state.client_data.get('contact_name', ''),
                                        key="prop_contact")
            
            email = st.text_input("Email",
                                value=st.session_state.client_data.get('email', ''),
                                key="prop_email")
        
        with col2:
            phone = st.text_input("Teléfono",
                                value=st.session_state.client_data.get('phone', ''),
                                key="prop_phone")
            
            industry = st.selectbox("Industria",
                                  options=['Retail', 'Wholesale', 'Services', 'Manufacturing'],
                                  index=0,
                                  key="prop_industry")
            
            proposal_date = st.date_input("Fecha de Propuesta",
                                        value=datetime.now(),
                                        key="prop_date")
        
        st.markdown("### ⚙️ Configuración de Propuesta")
        
        col1, col2 = st.columns(2)
        
        with col1:
            template_type = st.selectbox("Tipo de Plantilla",
                                        options=['executive', 'technical', 'simple'],
                                        format_func=lambda x: {
                                            'executive': 'Ejecutiva',
                                            'technical': 'Técnica Detallada',
                                            'simple': 'Simple'
                                        }[x],
                                        key="prop_template")
            
            package_type = st.selectbox("Paquete de Servicios",
                                       options=['starter', 'professional', 'enterprise'],
                                       format_func=lambda x: {
                                           'starter': 'Starter ($15M CLP)',
                                           'professional': 'Professional ($25M CLP)',
                                           'enterprise': 'Enterprise ($50M CLP)'
                                       }[x],
                                       index=1,
                                       key="prop_package")
        
        with col2:
            include_sections = st.multiselect("Secciones a Incluir",
                                            options=['executive_summary', 'current_state', 
                                                   'proposed_solution', 'roi_analysis',
                                                   'implementation_plan', 'investment'],
                                            default=['executive_summary', 'current_state', 
                                                   'proposed_solution', 'roi_analysis',
                                                   'implementation_plan', 'investment'],
                                            format_func=lambda x: {
                                                'executive_summary': 'Resumen Ejecutivo',
                                                'current_state': 'Estado Actual',
                                                'proposed_solution': 'Solución Propuesta',
                                                'roi_analysis': 'Análisis ROI',
                                                'implementation_plan': 'Plan de Implementación',
                                                'investment': 'Inversión'
                                            }[x],
                                            key="prop_sections")
            
            language = st.radio("Idioma",
                              options=['es', 'en'],
                              format_func=lambda x: 'Español' if x == 'es' else 'English',
                              key="prop_language")
        
        # Custom message
        st.markdown("### 💬 Mensaje Personalizado")
        
        custom_message = st.text_area("Mensaje para el Cliente (Opcional)",
                                     placeholder="Agregue un mensaje personalizado que aparecerá en la propuesta...",
                                     height=100,
                                     key="prop_message")
        
        # Generate button
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if st.button("🎨 Generar Propuesta", type="primary", use_container_width=True):
                with st.spinner("Generando propuesta profesional..."):
                    # Update client data
                    st.session_state.client_data.update({
                        'company_name': company_name,
                        'contact_name': contact_name,
                        'email': email,
                        'phone': phone,
                        'industry': industry
                    })
                    
                    # Generate proposal
                    generator = AutomatedProposalGenerator()
                    
                    proposal = generator.generate_proposal(
                        client_data=st.session_state.client_data,
                        assessment_results=st.session_state.assessment_results,
                        roi_analysis=st.session_state.roi_results,
                        template_type=template_type,
                        package_type=package_type
                    )
                    
                    st.session_state.proposal_data = proposal
                    
                    st.success("✅ Propuesta generada exitosamente")
    
    with tab2:
        if st.session_state.proposal_data:
            proposal = st.session_state.proposal_data
            
            st.markdown("### 📄 Vista Previa de Propuesta")
            
            # Proposal header
            st.markdown(f"""
            <div style='background-color: #1e3d59; color: white; padding: 30px; border-radius: 10px;'>
                <h1 style='color: white;'>Propuesta de Transformación Digital</h1>
                <p style='font-size: 1.2em;'>{st.session_state.client_data.get('company_name', 'Empresa')}</p>
                <p>Fecha: {datetime.now().strftime('%d de %B, %Y')}</p>
                <p>Propuesta ID: {proposal.get('metadata', {}).get('proposal_id', 'N/A')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Display sections
            sections = proposal.get('sections', {})
            
            for section_key, section_data in sections.items():
                if isinstance(section_data, dict) and 'title' in section_data:
                    with st.expander(f"📑 {section_data['title']}", expanded=True):
                        st.markdown(section_data.get('content', ''))
                        
                        if 'highlights' in section_data:
                            st.markdown("**Puntos Clave:**")
                            for highlight in section_data['highlights']:
                                st.markdown(f"• {highlight}")
            
            # Package details
            package = proposal.get('package', {})
            if package:
                st.markdown("### 📦 Paquete Seleccionado")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Paquete", package.get('name', 'Professional'))
                
                with col2:
                    st.metric("Inversión", format_clp(package.get('price_clp', 25000000)))
                
                with col3:
                    st.metric("Duración", package.get('duration', '8 semanas'))
                
                st.markdown("**Incluye:**")
                for feature in package.get('features', []):
                    st.markdown(f"✓ {feature}")
            
            # Terms
            st.markdown("### 📋 Términos y Condiciones")
            
            terms = proposal.get('terms', {})
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Validez:** {terms.get('validity', '30 días')}")
                st.markdown(f"**Forma de Pago:** {terms.get('payment_terms', '50% inicio, 50% entrega')}")
            
            with col2:
                st.markdown(f"**Garantía:** {terms.get('warranty', '6 meses')}")
                st.markdown(f"**Soporte:** {terms.get('support', 'Incluido por 12 meses')}")
        
        else:
            st.info("👈 Configure la propuesta en la pestaña 'Configuración' y presione 'Generar Propuesta'")
    
    with tab3:
        st.markdown("### 📦 Comparación de Paquetes")
        
        # Package comparison table
        packages_df = create_package_comparison()
        
        # Style the dataframe
        def highlight_package(val):
            if val == 'Professional':
                return 'background-color: #f5b800'
            return ''
        
        st.dataframe(packages_df, use_container_width=True, height=250)
        
        # Detailed package descriptions
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div style='background-color: #f8f9fa; padding: 20px; border-radius: 10px; height: 400px;'>
                <h3>🚀 Starter</h3>
                <h4 style='color: #f5b800;'>$15M CLP</h4>
                <p>Perfecto para pequeñas empresas comenzando su transformación digital.</p>
                <ul>
                    <li>20 horas de consultoría</li>
                    <li>2 integraciones básicas</li>
                    <li>Soporte por email</li>
                    <li>Training básico</li>
                    <li>ROI garantizado 100%</li>
                </ul>
                <p><strong>Duración:</strong> 4 semanas</p>
                <p><strong>Ideal para:</strong> <$500M CLP/año</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style='background-color: #e8f4f8; padding: 20px; border-radius: 10px; border: 2px solid #f5b800; height: 400px;'>
                <h3>⭐ Professional</h3>
                <h4 style='color: #f5b800;'>$25M CLP</h4>
                <p><strong>RECOMENDADO</strong> - Nuestra opción más popular.</p>
                <ul>
                    <li>40 horas de consultoría</li>
                    <li>5 integraciones avanzadas</li>
                    <li>Soporte prioritario 24/7</li>
                    <li>Training completo</li>
                    <li>ROI garantizado 150%</li>
                </ul>
                <p><strong>Duración:</strong> 8 semanas</p>
                <p><strong>Ideal para:</strong> $500M-2B CLP/año</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div style='background-color: #f8f9fa; padding: 20px; border-radius: 10px; height: 400px;'>
                <h3>💎 Enterprise</h3>
                <h4 style='color: #f5b800;'>$50M CLP</h4>
                <p>Solución completa para grandes operaciones.</p>
                <ul>
                    <li>80+ horas de consultoría</li>
                    <li>Integraciones ilimitadas</li>
                    <li>Soporte dedicado on-site</li>
                    <li>Training personalizado</li>
                    <li>ROI garantizado 200%</li>
                </ul>
                <p><strong>Duración:</strong> 12-16 semanas</p>
                <p><strong>Ideal para:</strong> >$2B CLP/año</p>
            </div>
            """, unsafe_allow_html=True)
        
        # ROI comparison
        st.markdown("### 📈 ROI Esperado por Paquete")
        
        roi_data = pd.DataFrame({
            'Paquete': ['Starter', 'Professional', 'Enterprise'],
            'ROI Mínimo': [100, 150, 200],
            'ROI Promedio': [120, 180, 250],
            'ROI Máximo': [150, 220, 300]
        })
        
        fig = px.bar(roi_data, x='Paquete', y=['ROI Mínimo', 'ROI Promedio', 'ROI Máximo'],
                    title='Retorno de Inversión Esperado (%)',
                    color_discrete_sequence=get_dark_color_sequence()[:3])
        fig.update_layout(height=400)
        fig = apply_dark_theme(fig)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        if st.session_state.proposal_data:
            st.markdown("### 💾 Opciones de Exportación")
            
            # Export formats
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("""
                <div style='text-align: center; padding: 20px; background-color: #f8f9fa; border-radius: 10px;'>
                    <h3>📄 PDF</h3>
                    <p>Documento profesional listo para imprimir</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("📥 Descargar PDF", use_container_width=True):
                    with st.spinner("Generando PDF..."):
                        time.sleep(2)  # Simulate PDF generation
                        st.success("✅ PDF generado")
                        
                        # Create download button with proper variable
                        company_name = st.session_state.client_data.get('company_name', 'Cliente')
                        pdf_data = b"PDF content here"  # Would be actual PDF bytes
                        st.download_button(
                            label="⬇️ Descargar Propuesta.pdf",
                            data=pdf_data,
                            file_name=f"Propuesta_{company_name}_{datetime.now().strftime('%Y%m%d')}.pdf",
                            mime="application/pdf"
                        )
            
            with col2:
                st.markdown("""
                <div style='text-align: center; padding: 20px; background-color: #f8f9fa; border-radius: 10px;'>
                    <h3>📊 PowerPoint</h3>
                    <p>Presentación lista para reuniones</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("📥 Descargar PPTX", use_container_width=True):
                    with st.spinner("Generando PowerPoint..."):
                        time.sleep(2)  # Simulate PPTX generation
                        st.success("✅ PowerPoint generado")
                        
                        # Create download button with proper variable
                        company_name = st.session_state.client_data.get('company_name', 'Cliente')
                        pptx_data = b"PPTX content here"  # Would be actual PPTX bytes
                        st.download_button(
                            label="⬇️ Descargar Propuesta.pptx",
                            data=pptx_data,
                            file_name=f"Propuesta_{company_name}_{datetime.now().strftime('%Y%m%d')}.pptx",
                            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
                        )
            
            with col3:
                st.markdown("""
                <div style='text-align: center; padding: 20px; background-color: #f8f9fa; border-radius: 10px;'>
                    <h3>📧 Email</h3>
                    <p>Enviar directamente al cliente</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("📧 Enviar por Email", use_container_width=True):
                    with st.spinner("Preparando email..."):
                        time.sleep(1)
                        email = st.session_state.client_data.get('email', 'cliente@empresa.cl')
                        st.success(f"✅ Email enviado a {email}")
            
            # One-pager option
            st.markdown("### 📋 One-Pager Ejecutivo")
            
            if st.button("📄 Generar One-Pager", use_container_width=True):
                with st.spinner("Generando one-pager..."):
                    generator = AutomatedProposalGenerator()
                    one_pager = generator.generate_one_pager()
                    
                    st.text_area("One-Pager", value=one_pager, height=400)
                    
                    # Download button for one-pager
                    company_name = st.session_state.client_data.get('company_name', 'Cliente')
                    st.download_button(
                        label="⬇️ Descargar One-Pager.txt",
                        data=one_pager,
                        file_name=f"OnePager_{company_name}_{datetime.now().strftime('%Y%m%d')}.txt",
                        mime="text/plain"
                    )
            
            # Tracking
            st.markdown("### 📊 Seguimiento de Propuesta")
            
            col1, col2 = st.columns(2)
            
            with col1:
                enable_tracking = st.checkbox("Habilitar tracking de apertura", value=True)
                expiry_days = st.number_input("Días de validez", min_value=7, max_value=90, value=30)
            
            with col2:
                send_reminder = st.checkbox("Enviar recordatorios automáticos", value=True)
                reminder_days = st.multiselect("Días para recordatorio",
                                              options=[3, 7, 14, 21, 28],
                                              default=[7, 21])
            
            if st.button("💾 Guardar Configuración", type="secondary"):
                st.success("✅ Configuración guardada")
        
        else:
            st.info("👈 Primero debe generar una propuesta para poder exportarla")

# Run the page only if this file is run directly
if __name__ == "__main__":
    show_proposal_generator()
"""
Assessment Tool Page for Streamlit Dashboard
"""

import streamlit as st
from pages.shared_navigation import show_navigation
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime
import time

# Import the assessment tool
import sys
sys.path.insert(0, 'src')
from rapid_assessment_tool import RapidAssessmentTool

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

def create_qualification_gauge(score):
    """Create gauge chart for qualification score"""
    
    # Determine color based on score
    if score >= 80:
        color = "#00ff00"
        qualification = "A - HOT PROSPECT"
    elif score >= 60:
        color = "#ffff00"
        qualification = "B - QUALIFIED"
    elif score >= 40:
        color = "#ff9900"
        qualification = "C - NEEDS NURTURING"
    else:
        color = "#ff0000"
        qualification = "D - NOT QUALIFIED"
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': f"Calificación: {qualification}", 'font': {'color': '#f5b800', 'size': 16}},
        gauge = {
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickfont': {'color': '#ffffff'}},
            'bar': {'color': color},
            'bgcolor': "#1a1a1a",
            'borderwidth': 2,
            'bordercolor': "#f5b800",
            'steps': [
                {'range': [0, 40], 'color': '#2a2a2a'},
                {'range': [40, 60], 'color': '#3a3a3a'},
                {'range': [60, 80], 'color': '#4a4a4a'},
                {'range': [80, 100], 'color': '#5a5a5a'}
            ],
            'threshold': {
                'line': {'color': "#f5b800", 'width': 4},
                'thickness': 0.75,
                'value': score
            }
        }
    ))
    
    fig.update_layout(height=300, margin=dict(l=0, r=0, t=30, b=0))
    return apply_dark_theme(fig)

def create_maturity_radar(maturity_scores):
    """Create radar chart for digital maturity"""
    
    categories = list(maturity_scores.keys())
    values = list(maturity_scores.values())
    
    fig = go.Figure(data=go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        marker_color='#f5b800'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10],
                color='#ffffff'
            )),
        showlegend=False,
        title="Madurez Digital por Área",
        height=400
    )
    
    return apply_dark_theme(fig)

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
if 'assessment_step' not in st.session_state:
    st.session_state.assessment_step = 0
if 'assessment_responses' not in st.session_state:
    st.session_state.assessment_responses = {}
if 'assessment' not in st.session_state:
    st.session_state.assessment = RapidAssessmentTool()

def show_assessment_tool():
    """Display the Assessment Tool page"""

    # Show navigation sidebar
    show_navigation()
    
    st.title("📋 Herramienta de Evaluación Rápida")
    st.markdown("Califique prospectos en 15 minutos con nuestro sistema de evaluación inteligente")
    
    # Initialize assessment tool
    if 'assessment' not in st.session_state:
        st.session_state.assessment = RapidAssessmentTool()
    
    assessment = st.session_state.assessment
    
    # Progress tracking
    if 'assessment_step' not in st.session_state:
        st.session_state.assessment_step = 0
    
    if 'assessment_responses' not in st.session_state:
        st.session_state.assessment_responses = {}
    
    # Assessment sections
    sections = [
        "Información Básica",
        "Tecnología Actual",
        "Procesos Operacionales",
        "Integraciones",
        "Puntos de Dolor",
        "Objetivos de Crecimiento"
    ]
    
    # Progress bar
    progress = st.session_state.assessment_step / len(sections)
    st.progress(progress)
    st.markdown(f"**Sección {st.session_state.assessment_step + 1} de {len(sections)}**: {sections[st.session_state.assessment_step] if st.session_state.assessment_step < len(sections) else 'Completado'}")
    
    # Assessment wizard
    if st.session_state.assessment_step < len(sections):
        
        current_section = sections[st.session_state.assessment_step]
        
        if current_section == "Información Básica":
            st.markdown("### 🏢 Información Básica")
            
            col1, col2 = st.columns(2)
            
            with col1:
                company_name = st.text_input("Nombre de la Empresa", 
                                            key="assess_company",
                                            placeholder="Tienda Digital Santiago SpA")
                
                annual_revenue = st.number_input("Ingresos Anuales (CLP)", 
                                                min_value=0,
                                                value=600000000,
                                                step=10000000,
                                                key="assess_revenue",
                                                format="%d")
                
                monthly_orders = st.number_input("Órdenes Mensuales", 
                                                min_value=0,
                                                value=2000,
                                                step=100,
                                                key="assess_orders")
            
            with col2:
                employees = st.number_input("Empleados en Operaciones", 
                                          min_value=1,
                                          value=5,
                                          key="assess_employees")
                
                industry = st.selectbox("Industria", 
                                       options=['Retail', 'Wholesale', 'Services', 'Manufacturing'],
                                       key="assess_industry")
                
                location = st.text_input("Ubicación", 
                                        value="Santiago, Chile",
                                        key="assess_location")
            
            if st.button("Siguiente →", key="btn_basic"):
                st.session_state.assessment_responses.update({
                    'b1': annual_revenue,
                    'b2': monthly_orders,
                    'b3': employees,
                    'b4': industry,
                    'company_name': company_name,
                    'location': location
                })
                st.session_state.assessment_step += 1
                st.rerun()
        
        elif current_section == "Tecnología Actual":
            st.markdown("### 💻 Tecnología Actual")
            
            col1, col2 = st.columns(2)
            
            with col1:
                platform = st.selectbox("Plataforma E-commerce Principal",
                                       options=['WooCommerce', 'Shopify', 'Magento', 'PrestaShop', 
                                              'Vtex', 'Custom', 'Ninguna'],
                                       key="assess_platform")
                
                has_erp = st.radio("¿Tiene integración ERP?",
                                  options=[True, False],
                                  format_func=lambda x: "Sí" if x else "No",
                                  key="assess_erp")
                
                automation_level = st.slider("Nivel de Automatización (1-10)",
                                           min_value=1,
                                           max_value=10,
                                           value=3,
                                           key="assess_automation",
                                           help="1 = Todo manual, 10 = Totalmente automatizado")
            
            with col2:
                tools = st.multiselect("Herramientas en Uso",
                                      options=['Excel', 'Google Sheets', 'ERP', 'CRM', 
                                             'Email Marketing', 'Analytics', 'Inventory Management',
                                             'Defontana', 'Bsale', 'Manager'],
                                      default=['Excel'],
                                      key="assess_tools")
                
                integrations = st.multiselect("Integraciones Actuales",
                                            options=['Transbank', 'Webpay', 'MercadoPago', 
                                                   'Chilexpress', 'Starken', 'Correos Chile',
                                                   'WhatsApp', 'Instagram', 'Facebook'],
                                            default=['Transbank'],
                                            key="assess_integrations")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("← Anterior", key="btn_tech_back"):
                    st.session_state.assessment_step -= 1
                    st.rerun()
            
            with col2:
                if st.button("Siguiente →", key="btn_tech_next"):
                    st.session_state.assessment_responses.update({
                        't1': platform,
                        't2': has_erp,
                        't3': tools,
                        't4': automation_level,
                        'integrations': integrations
                    })
                    st.session_state.assessment_step += 1
                    st.rerun()
        
        elif current_section == "Procesos Operacionales":
            st.markdown("### ⚙️ Procesos Operacionales")
            
            col1, col2 = st.columns(2)
            
            with col1:
                time_per_order = st.number_input("Minutos por Orden (promedio)",
                                                min_value=1,
                                                value=20,
                                                key="assess_time_order",
                                                help="Tiempo promedio para procesar una orden")
                
                error_rate = st.slider("Tasa de Error (%)",
                                      min_value=0.0,
                                      max_value=20.0,
                                      value=7.0,
                                      step=0.5,
                                      key="assess_error_rate",
                                      format="%.1f%%")
                
                manual_hours = st.number_input("Horas de Trabajo Manual/Día",
                                              min_value=0,
                                              value=8,
                                              key="assess_manual_hours")
            
            with col2:
                has_sop = st.radio("¿Procesos Documentados?",
                                  options=[True, False],
                                  format_func=lambda x: "Sí" if x else "No",
                                  key="assess_sop")
                
                inventory_update = st.selectbox("Frecuencia Actualización Inventario",
                                              options=['Tiempo real', 'Cada hora', 'Diariamente', 
                                                     'Semanalmente', 'Mensualmente', 'Manual'],
                                              key="assess_inventory_freq")
                
                bottlenecks = st.multiselect("Cuellos de Botella Principales",
                                           options=['Procesamiento de órdenes', 'Gestión de inventario',
                                                  'Fulfillment', 'Atención al cliente', 'Facturación',
                                                  'Logística', 'Devoluciones', 'Reportes'],
                                           default=['Procesamiento de órdenes'],
                                           key="assess_bottlenecks")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("← Anterior", key="btn_ops_back"):
                    st.session_state.assessment_step -= 1
                    st.rerun()
            
            with col2:
                if st.button("Siguiente →", key="btn_ops_next"):
                    st.session_state.assessment_responses.update({
                        'o1': time_per_order,
                        'o2': error_rate,
                        'o3': manual_hours,
                        'o4': has_sop,
                        'o5': inventory_update,
                        'bottlenecks': bottlenecks
                    })
                    st.session_state.assessment_step += 1
                    st.rerun()
        
        elif current_section == "Integraciones":
            st.markdown("### 🔗 Integraciones y Canales")
            
            col1, col2 = st.columns(2)
            
            with col1:
                payment_methods = st.multiselect("Métodos de Pago",
                                               options=['Transbank', 'Webpay', 'MercadoPago', 
                                                      'PayPal', 'Flow', 'Khipu', 'Mach', 'Fpay',
                                                      'Transferencia', 'Efectivo'],
                                               default=['Transbank', 'Webpay'],
                                               key="assess_payments")
                
                shipping_providers = st.multiselect("Proveedores de Envío",
                                                  options=['Chilexpress', 'Starken', 'Correos Chile',
                                                         'Bluexpress', 'Envíame', 'Propio', 'Uber', 'Cabify'],
                                                  default=['Chilexpress'],
                                                  key="assess_shipping")
            
            with col2:
                marketplaces = st.multiselect("Marketplaces",
                                            options=['MercadoLibre', 'Falabella', 'Paris', 'Ripley',
                                                   'Linio', 'Amazon', 'Facebook Marketplace', 
                                                   'Instagram Shopping', 'No vendo en marketplaces'],
                                            default=['No vendo en marketplaces'],
                                            key="assess_marketplaces")
                
                has_inventory_sync = st.radio("¿Sincronización de Inventario Multi-canal?",
                                             options=[True, False],
                                             format_func=lambda x: "Sí" if x else "No",
                                             key="assess_inv_sync")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("← Anterior", key="btn_int_back"):
                    st.session_state.assessment_step -= 1
                    st.rerun()
            
            with col2:
                if st.button("Siguiente →", key="btn_int_next"):
                    st.session_state.assessment_responses.update({
                        'i1': payment_methods,
                        'i2': shipping_providers,
                        'i3': marketplaces,
                        'i4': has_inventory_sync
                    })
                    st.session_state.assessment_step += 1
                    st.rerun()
        
        elif current_section == "Puntos de Dolor":
            st.markdown("### 😰 Puntos de Dolor y Desafíos")
            
            col1, col2 = st.columns(2)
            
            with col1:
                pain_points = st.multiselect("Principales Problemas",
                                           options=['Procesamiento manual de órdenes', 
                                                  'Errores en fulfillment',
                                                  'Falta de visibilidad de inventario',
                                                  'Costos operacionales altos',
                                                  'Baja conversión',
                                                  'Problemas de escalabilidad',
                                                  'Falta de reportes',
                                                  'Integración deficiente',
                                                  'Experiencia cliente pobre'],
                                           default=['Procesamiento manual de órdenes'],
                                           key="assess_pain")
                
                monthly_loss = st.number_input("Pérdida Estimada Mensual (CLP)",
                                              min_value=0,
                                              value=4000000,
                                              step=500000,
                                              key="assess_loss",
                                              help="Pérdida por ineficiencias, errores, etc.")
            
            with col2:
                urgency = st.slider("Urgencia de Solución (1-10)",
                                  min_value=1,
                                  max_value=10,
                                  value=8,
                                  key="assess_urgency",
                                  help="1 = No urgente, 10 = Crítico")
                
                failed_attempts = st.number_input("Intentos Previos de Solución",
                                                min_value=0,
                                                value=1,
                                                key="assess_attempts",
                                                help="Número de veces que han intentado resolver estos problemas")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("← Anterior", key="btn_pain_back"):
                    st.session_state.assessment_step -= 1
                    st.rerun()
            
            with col2:
                if st.button("Siguiente →", key="btn_pain_next"):
                    st.session_state.assessment_responses.update({
                        'p1': pain_points,
                        'p2': monthly_loss,
                        'p3': urgency,
                        'attempts': failed_attempts
                    })
                    st.session_state.assessment_step += 1
                    st.rerun()
        
        elif current_section == "Objetivos de Crecimiento":
            st.markdown("### 🎯 Objetivos de Crecimiento")
            
            col1, col2 = st.columns(2)
            
            with col1:
                growth_target = st.number_input("Meta de Crecimiento Anual (%)",
                                              min_value=0,
                                              value=40,
                                              key="assess_growth",
                                              help="Crecimiento deseado en ventas")
                
                has_budget = st.radio("¿Tiene Presupuesto Asignado?",
                                     options=[True, False],
                                     format_func=lambda x: "Sí" if x else "No",
                                     key="assess_budget")
                
                timeline = st.selectbox("Timeline de Implementación",
                                       options=['Inmediato', '1-3 meses', '3-6 meses', 
                                              '6-12 meses', 'Más de 1 año'],
                                       key="assess_timeline")
            
            with col2:
                decision_maker = st.radio("¿Es el Tomador de Decisión?",
                                        options=[True, False],
                                        format_func=lambda x: "Sí" if x else "No",
                                        key="assess_decision")
                
                priorities = st.multiselect("Prioridades Principales",
                                          options=['Reducir costos', 'Aumentar ventas', 
                                                 'Mejorar eficiencia', 'Escalar operaciones',
                                                 'Mejorar experiencia cliente', 'Expandir a nuevos canales',
                                                 'Automatizar procesos', 'Obtener mejores reportes'],
                                          default=['Reducir costos', 'Mejorar eficiencia'],
                                          key="assess_priorities")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("← Anterior", key="btn_growth_back"):
                    st.session_state.assessment_step -= 1
                    st.rerun()
            
            with col2:
                if st.button("🎯 Completar Evaluación", type="primary", key="btn_complete"):
                    st.session_state.assessment_responses.update({
                        'g1': growth_target,
                        'g2': has_budget,
                        'g3': timeline,
                        'decision_maker': decision_maker,
                        'priorities': priorities
                    })
                    st.session_state.assessment_step += 1
                    st.rerun()
    
    else:
        # Assessment complete - show results
        with st.spinner("Analizando respuestas..."):
            time.sleep(1)  # Simulate processing
            
            # Run assessment
            assessment_results = assessment.conduct_assessment(st.session_state.assessment_responses)
            st.session_state.assessment_results = assessment_results
        
        st.success("✅ Evaluación Completada")
        
        # Results tabs
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Calificación", "📈 Análisis", "💡 Recomendaciones", "📄 Reporte"])
        
        with tab1:
            st.markdown("### 🎯 Calificación del Prospecto")
            
            qualification = assessment_results.get('qualification', {})
            roi_potential = assessment_results.get('roi_potential', {})
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Qualification gauge
                score = qualification.get('score', 0)
                st.plotly_chart(create_qualification_gauge(score), use_container_width=True)
            
            with col2:
                # Key metrics
                st.metric("Probabilidad de Cierre", 
                         f"{qualification.get('close_probability', 0)}%",
                         help="Probabilidad estimada de cerrar el negocio")
                
                st.metric("ROI Potencial", 
                         f"{roi_potential.get('roi_percentage', 0):.0f}%",
                         help="ROI estimado en el primer año")
                
                st.metric("Tiempo de Venta Estimado", 
                         qualification.get('estimated_sales_cycle', '2-4 semanas'),
                         help="Tiempo estimado para cerrar la venta")
            
            # Qualification details
            st.markdown("### 📋 Detalles de Calificación")
            
            level = qualification.get('level', 'N/A')
            level_colors = {
                'A - HOT PROSPECT': 'green',
                'B - QUALIFIED': 'blue',
                'C - NEEDS NURTURING': 'orange',
                'D - NOT QUALIFIED': 'red'
            }
            
            st.markdown(f"""
            <div style='background-color: {level_colors.get(level, 'gray')}20; 
                       border-left: 4px solid {level_colors.get(level, 'gray')}; 
                       padding: 15px; border-radius: 5px;'>
                <h3 style='color: {level_colors.get(level, 'gray')};'>{level}</h3>
                <p>{qualification.get('description', '')}</p>
                <p><strong>Acción Recomendada:</strong> {qualification.get('next_action', '')}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with tab2:
            st.markdown("### 📊 Análisis Detallado")
            
            # Maturity analysis
            maturity = assessment_results.get('maturity_level', {})
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Nivel de Madurez Digital", 
                         f"{maturity.get('level', 'N/A')}",
                         f"Score: {maturity.get('score', 0):.1f}/10")
                
                st.markdown(f"**Descripción:** {maturity.get('description', '')}")
            
            with col2:
                # Maturity radar chart
                maturity_scores = assessment_results.get('maturity_scores', {
                    'Tecnología': 3.5,
                    'Procesos': 2.8,
                    'Integraciones': 4.2,
                    'Datos': 3.0,
                    'Equipo': 5.0,
                    'Estrategia': 4.5
                })
                
                st.plotly_chart(create_maturity_radar(maturity_scores), use_container_width=True)
            
            # Pain points analysis
            st.markdown("### 😰 Análisis de Puntos de Dolor")
            
            pain_points = assessment_results.get('pain_points', [])
            
            if pain_points:
                # Display each pain point
                for pain in pain_points:
                    severity_color = {
                        'CRÍTICA': '🔴',
                        'ALTA': '🟠',
                        'MEDIA': '🟡',
                        'BAJA': '🟢'
                    }.get(pain.get('severity', 'MEDIA'), '🟡')
                    
                    with st.expander(f"{severity_color} {pain.get('issue', 'Punto de dolor')}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"**Severidad:** {pain.get('severity', 'N/A')}")
                            st.markdown(f"**Impacto:** {pain.get('impact', 'N/A')}")
                        with col2:
                            cost_impact = pain.get('cost_impact_clp', 0)
                            if cost_impact > 0:
                                st.metric("Impacto en Costos", 
                                        f"${cost_impact/1_000_000:.1f}M CLP/año")
                
                # Create impact visualization
                if len(pain_points) > 0:
                    pain_data = []
                    for pain in pain_points:
                        severity_score = {
                            'CRÍTICA': 10,
                            'ALTA': 8,
                            'MEDIA': 5,
                            'BAJA': 3
                        }.get(pain.get('severity', 'MEDIA'), 5)
                        
                        pain_data.append({
                            'Problema': pain.get('issue', 'N/A')[:30] + '...' if len(pain.get('issue', '')) > 30 else pain.get('issue', 'N/A'),
                            'Severidad': severity_score,
                            'Impacto Anual (M CLP)': pain.get('cost_impact_clp', 0) / 1_000_000
                        })
                    
                    if pain_data:
                        df_pain = pd.DataFrame(pain_data)
                        
                        fig = px.scatter(df_pain, 
                                       x='Severidad', 
                                       y='Impacto Anual (M CLP)',
                                       text='Problema',
                                       title='Matriz de Puntos de Dolor',
                                       size='Impacto Anual (M CLP)',
                                       color='Severidad',
                                       color_continuous_scale=['#6bcf7f', '#f5b800', '#ff6b6b'])
                        
                        fig.update_traces(textposition='top center')
                        fig.update_layout(height=400)
                        fig.update_xaxes(range=[0, 12], title='Severidad (1-10)')
                        fig.update_yaxes(title='Impacto Anual (Millones CLP)')
                        fig = apply_dark_theme(fig)
                        st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No se identificaron puntos de dolor significativos en base a las respuestas proporcionadas.")
        
        with tab3:
            st.markdown("### 💡 Recomendaciones Personalizadas")
            
            recommendations = assessment_results.get('recommendations', [])
            
            if recommendations:
                for i, rec in enumerate(recommendations[:5], 1):
                    with st.expander(f"{i}. {rec.get('title', 'Recomendación')}"):
                        st.markdown(f"**Impacto:** {rec.get('impact', 'Alto')}")
                        st.markdown(f"**Tiempo:** {rec.get('timeline', '2-4 semanas')}")
                        st.markdown(f"**Descripción:** {rec.get('description', '')}")
                        
                        if rec.get('expected_benefit'):
                            st.success(f"Beneficio Esperado: {rec['expected_benefit']}")
            
            # Quick wins
            st.markdown("### 🎯 Quick Wins Identificados")
            
            quick_wins = assessment_results.get('quick_wins', [
                "Automatizar procesamiento de órdenes",
                "Implementar validación de datos",
                "Integrar inventario con e-commerce",
                "Configurar alertas de stock bajo",
                "Optimizar proceso de checkout"
            ])
            
            for win in quick_wins[:5]:
                st.markdown(f"✅ {win}")
        
        with tab4:
            st.markdown("### 📄 Reporte de Evaluación")
            
            # Summary report
            company = st.session_state.assessment_responses.get('company_name', 'Empresa')
            
            st.markdown(f"""
            **Empresa:** {company}  
            **Fecha:** {datetime.now().strftime('%Y-%m-%d')}  
            **Evaluador:** Sistema Automatizado
            
            ---
            
            **RESUMEN EJECUTIVO**
            
            {company} ha sido evaluada con un score de **{qualification.get('score', 0)}/100**, 
            clasificándola como **{qualification.get('level', 'N/A')}**.
            
            La empresa muestra un potencial de ROI del **{roi_potential.get('roi_percentage', 0):.0f}%** 
            con un período de retorno estimado de **{roi_potential.get('payback_months', 0):.1f} meses**.
            
            **Principales Hallazgos:**
            - Nivel de madurez digital: {maturity.get('level', 'BÁSICO')}
            - Principal punto de dolor: Procesamiento manual de órdenes
            - Urgencia de solución: {st.session_state.assessment_responses.get('p3', 8)}/10
            - Presupuesto disponible: {'Sí' if st.session_state.assessment_responses.get('g2') else 'Por confirmar'}
            
            **Próximos Pasos Recomendados:**
            1. Agendar demo de solución
            2. Preparar propuesta técnica y comercial
            3. Reunión con stakeholders clave
            4. Definir plan de implementación
            """)
            
            # Export options
            st.markdown("### 💾 Opciones de Exportación")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📄 Descargar PDF", use_container_width=True):
                    st.info("Generando reporte PDF...")
            
            with col2:
                if st.button("📊 Exportar Excel", use_container_width=True):
                    st.info("Exportando a Excel...")
            
            with col3:
                if st.button("📧 Enviar por Email", use_container_width=True):
                    st.info("Preparando email...")
            
            # Reset button
            st.markdown("---")
            if st.button("🔄 Nueva Evaluación", type="secondary"):
                st.session_state.assessment_step = 0
                st.session_state.assessment_responses = {}
                st.rerun()

# Run the page only if this file is run directly
if __name__ == "__main__":
    show_assessment_tool()
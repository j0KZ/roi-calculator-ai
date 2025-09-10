"""
Assessment Tool Page for Streamlit Dashboard
===========================================
Wizard-style questionnaire for rapid e-commerce readiness assessment.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from typing import Dict, Any, List, Tuple
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Assessment questions and scoring
ASSESSMENT_CATEGORIES = {
    'tech_maturity': {
        'name': 'Madurez Tecnológica',
        'weight': 20,
        'icon': '💻'
    },
    'digital_experience': {
        'name': 'Experiencia Digital',
        'weight': 18,
        'icon': '🌐'
    },
    'financial_capacity': {
        'name': 'Capacidad Financiera',
        'weight': 16,
        'icon': '💰'
    },
    'team_readiness': {
        'name': 'Preparación del Equipo',
        'weight': 15,
        'icon': '👥'
    },
    'market_understanding': {
        'name': 'Conocimiento del Mercado',
        'weight': 14,
        'icon': '📊'
    },
    'infrastructure': {
        'name': 'Infraestructura',
        'weight': 12,
        'icon': '🏗️'
    },
    'compliance': {
        'name': 'Cumplimiento Legal',
        'weight': 5,
        'icon': '⚖️'
    }
}

ASSESSMENT_QUESTIONS = {
    'tech_maturity': [
        {
            'question': '¿Qué tan familiarizado está su equipo con tecnologías web?',
            'options': [
                ('Muy básico - solo uso de email y navegadores', 1),
                ('Básico - uso de redes sociales y herramientas simples', 2),
                ('Intermedio - manejo de CRM y herramientas digitales', 3),
                ('Avanzado - experiencia con plataformas e-commerce', 4),
                ('Experto - desarrollo y personalización técnica', 5)
            ]
        },
        {
            'question': '¿Su empresa actualmente usa herramientas de gestión digital?',
            'options': [
                ('No usamos herramientas digitales', 1),
                ('Solo herramientas básicas (email, calendario)', 2),
                ('CRM básico y herramientas de oficina', 3),
                ('Sistema integrado de gestión empresarial', 4),
                ('Múltiples sistemas integrados y automatizados', 5)
            ]
        },
        {
            'question': '¿Cómo manejan actualmente los datos de clientes?',
            'options': [
                ('En papel o sin sistema organizado', 1),
                ('Hojas de cálculo básicas', 2),
                ('Base de datos simple', 3),
                ('CRM estructurado', 4),
                ('Sistema CRM avanzado con analytics', 5)
            ]
        }
    ],
    'digital_experience': [
        {
            'question': '¿Su empresa tiene presencia digital actual?',
            'options': [
                ('No tenemos presencia digital', 1),
                ('Solo redes sociales básicas', 2),
                ('Página web informativa', 3),
                ('Website con formularios y contacto', 4),
                ('Plataforma digital completa con ventas', 5)
            ]
        },
        {
            'question': '¿Han realizado ventas online anteriormente?',
            'options': [
                ('Nunca hemos vendido online', 1),
                ('Solo por redes sociales ocasionalmente', 2),
                ('Ventas básicas por WhatsApp/Instagram', 3),
                ('Tienda online simple funcionando', 4),
                ('E-commerce completo con múltiples canales', 5)
            ]
        },
        {
            'question': '¿Qué tan cómodos están con el marketing digital?',
            'options': [
                ('No tenemos experiencia', 1),
                ('Publicaciones básicas en redes sociales', 2),
                ('Campañas simples en redes sociales', 3),
                ('Marketing digital con métricas básicas', 4),
                ('Marketing digital avanzado con ROI medible', 5)
            ]
        }
    ],
    'financial_capacity': [
        {
            'question': '¿Cuál es su presupuesto estimado para implementar e-commerce?',
            'options': [
                ('Menos de $2,000,000 CLP', 1),
                ('$2,000,000 - $5,000,000 CLP', 2),
                ('$5,000,000 - $10,000,000 CLP', 3),
                ('$10,000,000 - $20,000,000 CLP', 4),
                ('Más de $20,000,000 CLP', 5)
            ]
        },
        {
            'question': '¿Pueden invertir en marketing digital mensualmente?',
            'options': [
                ('No tenemos presupuesto para marketing', 1),
                ('Menos de $200,000 CLP/mes', 2),
                ('$200,000 - $500,000 CLP/mes', 3),
                ('$500,000 - $1,000,000 CLP/mes', 4),
                ('Más de $1,000,000 CLP/mes', 5)
            ]
        },
        {
            'question': '¿Cómo es la situación financiera actual de la empresa?',
            'options': [
                ('Ajustada, necesitamos ROI inmediato', 1),
                ('Estable pero conservadores', 2),
                ('Buena, podemos invertir moderadamente', 3),
                ('Sólida, podemos hacer inversiones significativas', 4),
                ('Excelente, presupuesto amplio para crecimiento', 5)
            ]
        }
    ],
    'team_readiness': [
        {
            'question': '¿Tienen personas dedicadas a ventas/marketing?',
            'options': [
                ('No tenemos equipo especializado', 1),
                ('Una persona hace todo', 2),
                ('2-3 personas en ventas/marketing', 3),
                ('Equipo pequeño pero dedicado (4-6 personas)', 4),
                ('Equipo grande y especializado (7+ personas)', 5)
            ]
        },
        {
            'question': '¿Qué tan dispuesto está el equipo a aprender nuevas tecnologías?',
            'options': [
                ('Resistente a cambios tecnológicos', 1),
                ('Cauteloso pero abierto', 2),
                ('Interesado en aprender gradualmente', 3),
                ('Entusiasta con nuevas herramientas', 4),
                ('Muy proactivo adoptando tecnología', 5)
            ]
        },
        {
            'question': '¿Pueden dedicar tiempo a capacitación inicial?',
            'options': [
                ('Muy poco tiempo disponible', 1),
                ('Algunas horas por semana', 2),
                ('Medio día por semana', 3),
                ('Uno o dos días completos', 4),
                ('Tiempo completo para capacitación inicial', 5)
            ]
        }
    ],
    'market_understanding': [
        {
            'question': '¿Conocen bien a su audiencia objetivo?',
            'options': [
                ('No tenemos definida nuestra audiencia', 1),
                ('Idea general de nuestros clientes', 2),
                ('Conocemos demografía básica', 3),
                ('Perfiles de cliente bien definidos', 4),
                ('Segmentación avanzada con datos', 5)
            ]
        },
        {
            'question': '¿Entienden la competencia en línea?',
            'options': [
                ('No sabemos quién vende online en nuestro sector', 1),
                ('Conocemos algunos competidores principales', 2),
                ('Análisis básico de competencia', 3),
                ('Monitoreo regular de competidores', 4),
                ('Análisis competitivo detallado y actualizado', 5)
            ]
        },
        {
            'question': '¿Tienen estrategia de precios para el canal digital?',
            'options': [
                ('Usamos los mismos precios que offline', 1),
                ('Precios similares con pequeños ajustes', 2),
                ('Estrategia básica de precios digitales', 3),
                ('Precios optimizados para e-commerce', 4),
                ('Estrategia dinámica de precios', 5)
            ]
        }
    ],
    'infrastructure': [
        {
            'question': '¿Cómo manejan actualmente su inventario?',
            'options': [
                ('Papel o control mental', 1),
                ('Hojas de cálculo simples', 2),
                ('Sistema básico de inventario', 3),
                ('Sistema integrado de inventario', 4),
                ('ERP completo con control en tiempo real', 5)
            ]
        },
        {
            'question': '¿Qué tan eficiente es su proceso de despacho?',
            'options': [
                ('Proceso manual sin organización', 1),
                ('Proceso básico con algunos controles', 2),
                ('Sistema organizado pero manual', 3),
                ('Proceso semi-automatizado', 4),
                ('Sistema automatizado de fulfillment', 5)
            ]
        },
        {
            'question': '¿Tienen proveedores de logística confiables?',
            'options': [
                ('No tenemos proveedores establecidos', 1),
                ('Un proveedor básico', 2),
                ('2-3 proveedores locales', 3),
                ('Múltiples proveedores con buenas tarifas', 4),
                ('Red de proveedores optimizada con tecnología', 5)
            ]
        }
    ],
    'compliance': [
        {
            'question': '¿Están al día con regulaciones de e-commerce en Chile?',
            'options': [
                ('No conocemos las regulaciones', 1),
                ('Conocimiento básico', 2),
                ('Entendemos los principales requisitos', 3),
                ('Cumplimos con la mayoría de regulaciones', 4),
                ('Completamente actualizados y conformes', 5)
            ]
        },
        {
            'question': '¿Tienen políticas de privacidad y términos de servicio?',
            'options': [
                ('No tenemos políticas definidas', 1),
                ('Políticas básicas informales', 2),
                ('Documentos básicos pero no actualizados', 3),
                ('Políticas actualizadas y publicadas', 4),
                ('Políticas completas revisadas legalmente', 5)
            ]
        }
    ]
}

def calculate_category_score(category_responses: Dict[str, int]) -> float:
    """Calculate score for a category"""
    if not category_responses:
        return 0.0
    
    total_score = sum(category_responses.values())
    max_possible = len(category_responses) * 5  # Max score per question is 5
    return (total_score / max_possible) * 100

def calculate_total_score(all_responses: Dict[str, Dict[str, int]]) -> Tuple[float, Dict[str, float]]:
    """Calculate total weighted score and category scores"""
    category_scores = {}
    weighted_total = 0.0
    total_weight = 0.0
    
    for category, responses in all_responses.items():
        if category in ASSESSMENT_CATEGORIES and responses:
            category_score = calculate_category_score(responses)
            category_scores[ASSESSMENT_CATEGORIES[category]['name']] = category_score
            
            weight = ASSESSMENT_CATEGORIES[category]['weight']
            weighted_total += category_score * weight
            total_weight += weight
    
    final_score = weighted_total / total_weight if total_weight > 0 else 0
    return final_score, category_scores

def get_recommendations(total_score: float, category_scores: Dict[str, float]) -> List[str]:
    """Generate recommendations based on scores"""
    recommendations = []
    
    # Overall recommendations based on total score
    if total_score >= 80:
        recommendations.append("🎉 Su empresa está muy bien preparada para e-commerce. Puede implementar una solución completa.")
    elif total_score >= 60:
        recommendations.append("✅ Buena base para e-commerce. Enfóquese en fortalecer las áreas más débiles antes de implementar.")
    elif total_score >= 40:
        recommendations.append("⚠️ Base moderada. Necesita preparación adicional en varias áreas antes de lanzar e-commerce.")
    else:
        recommendations.append("🚨 Necesita preparación significativa. Considere empezar con soluciones más simples y construir gradualmente.")
    
    # Category-specific recommendations
    for category_name, score in category_scores.items():
        if score < 50:  # Low score categories
            if 'Tecnológica' in category_name:
                recommendations.append("💻 Capacite al equipo en herramientas digitales básicas antes de implementar e-commerce.")
            elif 'Digital' in category_name:
                recommendations.append("🌐 Comience con presencia digital básica (website, redes sociales) antes del e-commerce.")
            elif 'Financiera' in category_name:
                recommendations.append("💰 Evalúe opciones de financiamiento o comience con solución de menor costo inicial.")
            elif 'Equipo' in category_name:
                recommendations.append("👥 Planifique capacitación intensiva del equipo o considere contratar especialistas.")
            elif 'Mercado' in category_name:
                recommendations.append("📊 Realice investigación de mercado detallada antes de lanzar.")
            elif 'Infraestructura' in category_name:
                recommendations.append("🏗️ Mejore procesos internos y sistemas de gestión antes del e-commerce.")
            elif 'Legal' in category_name:
                recommendations.append("⚖️ Consulte con abogado especializado en e-commerce para cumplimiento.")
    
    return recommendations

def create_radar_chart(category_scores: Dict[str, float]) -> go.Figure:
    """Create radar chart for category scores"""
    categories = list(category_scores.keys())
    scores = list(category_scores.values())
    
    # Ensure we close the radar chart
    categories_closed = categories + [categories[0]]
    scores_closed = scores + [scores[0]]
    
    fig = go.Figure()
    
    # Add current scores
    fig.add_trace(go.Scatterpolar(
        r=scores_closed,
        theta=categories_closed,
        fill='toself',
        fillcolor='rgba(102, 126, 234, 0.3)',
        line=dict(color='#667eea', width=2),
        marker=dict(size=8),
        name='Puntuación Actual'
    ))
    
    # Add industry benchmark
    benchmark_scores = [70] * len(categories) + [70]  # Industry average
    fig.add_trace(go.Scatterpolar(
        r=benchmark_scores,
        theta=categories_closed,
        line=dict(color='#f39c12', width=2, dash='dash'),
        marker=dict(size=6),
        name='Promedio Industria'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(size=10)
            ),
            angularaxis=dict(
                tickfont=dict(size=11)
            )
        ),
        showlegend=True,
        title="Evaluación de Madurez E-commerce",
        template="plotly_white",
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

def create_progress_bars(category_scores: Dict[str, float]) -> go.Figure:
    """Create horizontal bar chart for category scores"""
    categories = list(category_scores.keys())
    scores = list(category_scores.values())
    
    # Color scale based on score
    colors = []
    for score in scores:
        if score >= 80:
            colors.append('#00d4aa')  # Green
        elif score >= 60:
            colors.append('#f39c12')  # Orange
        elif score >= 40:
            colors.append('#e74c3c')  # Red
        else:
            colors.append('#95a5a6')  # Gray
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=categories,
        x=scores,
        orientation='h',
        marker_color=colors,
        text=[f'{score:.1f}%' for score in scores],
        textposition='inside',
        hovertemplate='<b>%{y}</b><br>Puntuación: %{x:.1f}%<extra></extra>'
    ))
    
    fig.update_layout(
        title="Puntuación por Categoría",
        xaxis_title="Puntuación (%)",
        yaxis_title="Categorías",
        template="plotly_white",
        height=400,
        xaxis=dict(range=[0, 100])
    )
    
    return fig

def render_assessment_tool():
    """Render the assessment tool page"""
    
    # Page header
    st.markdown("""
    <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #00d4aa 0%, #00b894 100%); color: white; border-radius: 15px; margin-bottom: 2rem;">
        <h1>📋 Evaluación Rápida E-commerce</h1>
        <h3>Evalúa la preparación de tu empresa para el comercio electrónico</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Get session manager
    session_manager = st.session_state.session_manager
    assessment_data = session_manager.get_assessment_data()
    
    # Initialize progress tracking
    if 'current_category' not in st.session_state:
        st.session_state.current_category = 'tech_maturity'
    
    if 'assessment_responses' not in st.session_state:
        st.session_state.assessment_responses = {}
    
    # Progress indicator
    categories = list(ASSESSMENT_CATEGORIES.keys())
    current_index = categories.index(st.session_state.current_category)
    progress = (current_index + 1) / len(categories)
    
    st.progress(progress, text=f"Progreso: {current_index + 1}/{len(categories)} categorías")
    
    # Navigation buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if current_index > 0 and st.button("⬅️ Anterior", use_container_width=True):
            st.session_state.current_category = categories[current_index - 1]
            st.rerun()
    
    with col3:
        if current_index < len(categories) - 1:
            if st.button("Siguiente ➡️", use_container_width=True):
                st.session_state.current_category = categories[current_index + 1]
                st.rerun()
        else:
            if st.button("Finalizar ✅", type="primary", use_container_width=True):
                # Calculate final results
                if st.session_state.assessment_responses:
                    total_score, category_scores = calculate_total_score(st.session_state.assessment_responses)
                    recommendations = get_recommendations(total_score, category_scores)
                    
                    # Save to session
                    final_assessment = {
                        'responses': st.session_state.assessment_responses,
                        'total_score': total_score,
                        'category_scores': category_scores,
                        'recommendations': recommendations,
                        'max_score': 100,
                        'completed': True
                    }
                    session_manager.update_assessment_data(final_assessment)
                    
                    st.success("¡Evaluación completada!")
                    st.rerun()
    
    # Current category section
    current_category = st.session_state.current_category
    category_info = ASSESSMENT_CATEGORIES[current_category]
    
    st.markdown(f"""
    <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 10px; margin: 1rem 0;">
        <h2>{category_info['icon']} {category_info['name']}</h2>
        <p><strong>Peso en evaluación:</strong> {category_info['weight']}%</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Questions for current category
    questions = ASSESSMENT_QUESTIONS[current_category]
    
    if current_category not in st.session_state.assessment_responses:
        st.session_state.assessment_responses[current_category] = {}
    
    for i, question_data in enumerate(questions):
        st.markdown(f"### Pregunta {i + 1}")
        
        # Question text
        st.write(question_data['question'])
        
        # Options
        question_key = f"{current_category}_q{i}"
        current_value = st.session_state.assessment_responses[current_category].get(question_key, 0)
        
        # Find current selection index
        selected_index = 0
        if current_value > 0:
            for idx, (text, value) in enumerate(question_data['options']):
                if value == current_value:
                    selected_index = idx
                    break
        
        selected = st.radio(
            "Seleccione la opción que mejor describe su situación:",
            options=range(len(question_data['options'])),
            format_func=lambda x: question_data['options'][x][0],
            index=selected_index,
            key=f"radio_{question_key}_{current_index}"
        )
        
        # Save response
        st.session_state.assessment_responses[current_category][question_key] = question_data['options'][selected]['value']
        
        st.markdown("---")
    
    # Show category progress
    if st.session_state.assessment_responses.get(current_category):
        category_score = calculate_category_score(st.session_state.assessment_responses[current_category])
        
        # Score indicator
        if category_score >= 80:
            score_color = "#00d4aa"
            score_text = "Excelente"
        elif category_score >= 60:
            score_color = "#f39c12"
            score_text = "Bueno"
        elif category_score >= 40:
            score_color = "#e74c3c"
            score_text = "Regular"
        else:
            score_color = "#95a5a6"
            score_text = "Necesita Mejora"
        
        st.markdown(f"""
        <div style="background: linear-gradient(90deg, {score_color}, {score_color}33); color: white; padding: 1rem; border-radius: 8px; text-align: center; margin: 1rem 0;">
            <h3>Puntuación de {category_info['name']}: {category_score:.1f}/100</h3>
            <p><strong>{score_text}</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    # Show results if assessment is completed
    if assessment_data.get('completed'):
        st.markdown("---")
        st.markdown("## 📈 Resultados de la Evaluación")
        
        # Overall score
        total_score = assessment_data.get('total_score', 0)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Puntuación Total",
                f"{total_score:.1f}/100",
                delta=f"{total_score - 70:.1f} vs promedio industria"
            )
        
        with col2:
            # Get score category
            if total_score >= 80:
                category = "Excelente"
                color = "normal"
            elif total_score >= 60:
                category = "Bueno"  
                color = "normal"
            elif total_score >= 40:
                category = "Regular"
                color = "normal"
            else:
                category = "Necesita Mejora"
                color = "inverse"
            
            st.metric("Categoría", category)
        
        with col3:
            # Calculate readiness percentage
            readiness = min(100, max(0, (total_score - 20) * 1.25))  # Scale 20-100 to 0-100
            st.metric("Preparación E-commerce", f"{readiness:.0f}%")
        
        # Visualizations
        tab1, tab2 = st.tabs(["🎯 Análisis Radar", "📊 Detalle por Categoría"])
        
        with tab1:
            category_scores = assessment_data.get('category_scores', {})
            if category_scores:
                radar_chart = create_radar_chart(category_scores)
                st.plotly_chart(radar_chart, use_container_width=True)
                
                # Interpretation
                st.markdown("### 🔍 Interpretación del Análisis")
                st.markdown("""
                - **Verde (>80%)**: Excelente preparación, listo para implementar
                - **Naranja (60-80%)**: Buena base, pequeñas mejoras necesarias  
                - **Rojo (40-60%)**: Preparación moderada, necesita trabajo
                - **Gris (<40%)**: Requiere mejoras significativas
                """)
        
        with tab2:
            if category_scores:
                progress_chart = create_progress_bars(category_scores)
                st.plotly_chart(progress_chart, use_container_width=True)
                
                # Detailed breakdown
                st.markdown("### 📋 Desglose Detallado")
                
                for category, score in category_scores.items():
                    with st.expander(f"{category}: {score:.1f}/100"):
                        if score >= 80:
                            st.success(f"✅ **Excelente** - {category} está muy bien preparado para e-commerce")
                        elif score >= 60:
                            st.info(f"ℹ️ **Bueno** - {category} tiene una base sólida con oportunidades de mejora")
                        elif score >= 40:
                            st.warning(f"⚠️ **Regular** - {category} necesita atención antes de implementar e-commerce")
                        else:
                            st.error(f"❌ **Crítico** - {category} requiere mejoras significativas")
        
        # Recommendations
        st.markdown("### 💡 Recomendaciones Personalizadas")
        
        recommendations = assessment_data.get('recommendations', [])
        for i, recommendation in enumerate(recommendations, 1):
            st.markdown(f"{i}. {recommendation}")
        
        # Next steps based on score
        st.markdown("### 🚀 Próximos Pasos Recomendados")
        
        if total_score >= 80:
            st.success("""
            **Su empresa está lista para e-commerce:**
            1. Proceda con la calculadora ROI para planificar la inversión
            2. Considere una plataforma e-commerce completa
            3. Planifique el lanzamiento en 2-4 meses
            """)
        elif total_score >= 60:
            st.info("""
            **Preparación adicional recomendada:**
            1. Fortalezca las áreas con menor puntuación
            2. Considere comenzar con una solución básica
            3. Planifique capacitación del equipo
            4. Evalúe ROI con escenarios conservadores
            """)
        elif total_score >= 40:
            st.warning("""
            **Preparación significativa necesaria:**
            1. Priorice mejoras en las 3 categorías más débiles
            2. Considere asesoría especializada
            3. Comience con presencia digital básica
            4. Planifique implementación en fases
            """)
        else:
            st.error("""
            **Preparación integral requerida:**
            1. Desarrolle plan de preparación de 6-12 meses
            2. Obtenga asesoría externa especializada
            3. Comience con herramientas básicas
            4. Considere asociarse con expertos
            """)
        
        # Export options
        st.markdown("---")
        st.markdown("### 📥 Exportar Resultados")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 Exportar PDF", use_container_width=True):
                try:
                    export_data = st.session_state.export_handler.export_assessment_data(assessment_data, 'pdf')
                    if export_data:
                        filename = st.session_state.export_handler.get_filename('assessment', 'pdf')
                        st.download_button(
                            "⬇️ Descargar PDF",
                            export_data,
                            filename,
                            'application/pdf'
                        )
                        session_manager.log_export('assessment', filename, True)
                except Exception as e:
                    st.error(f"Error exportando PDF: {str(e)}")
        
        with col2:
            if st.button("📋 Exportar Excel", use_container_width=True):
                try:
                    export_data = st.session_state.export_handler.export_assessment_data(assessment_data, 'excel')
                    if export_data:
                        filename = st.session_state.export_handler.get_filename('assessment', 'xlsx')
                        st.download_button(
                            "⬇️ Descargar Excel",
                            export_data,
                            filename,
                            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                        )
                        session_manager.log_export('assessment', filename, True)
                except Exception as e:
                    st.error(f"Error exportando Excel: {str(e)}")
        
        with col3:
            if st.button("🔗 Continuar con ROI", type="primary", use_container_width=True):
                st.session_state.current_page = "roi_calculator"
                st.rerun()
    
    # Help section
    with st.expander("❓ Ayuda y Consejos"):
        st.markdown("""
        **Cómo usar esta evaluación:**
        
        1. **Sea honesto**: Las respuestas precisas generan mejores recomendaciones
        2. **Tome su tiempo**: Reflexione sobre cada pregunta
        3. **Involucre al equipo**: Consulte con colegas relevantes
        4. **Documentos de apoyo**: Tenga a mano información financiera y técnica
        
        **Interpretación de resultados:**
        - **80-100%**: Listo para e-commerce completo
        - **60-79%**: Necesita preparación menor
        - **40-59%**: Requiere mejoras moderadas  
        - **0-39%**: Necesita preparación significativa
        
        **¿Necesita ayuda?**
        Esta evaluación es una guía inicial. Para análisis más detallados, 
        considere consultar con especialistas en e-commerce.
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 1rem; background: #f8f9fa; border-radius: 10px;">
        <small>
        💡 <strong>Consejo:</strong> Complete todas las categorías para obtener recomendaciones precisas. 
        Sus respuestas se guardan automáticamente en la sesión.
        </small>
    </div>
    """, unsafe_allow_html=True)
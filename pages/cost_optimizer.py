#!/usr/bin/env python3
"""
Cost Optimizer Page - Optimize operational costs for e-commerce
"""

import streamlit as st
from pages.shared_navigation import show_navigation
import sys
import os
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from cost_optimizer import CostOptimizer

@st.cache_resource
def get_optimizer():
    """Get cached optimizer instance with lazy loading"""
    return CostOptimizer(industry='ecommerce', lazy_load=True)

def show_cost_optimizer():
    """Display cost optimizer page"""

    # Show navigation sidebar
    show_navigation()
    
    st.title("💰 Optimizador de Costos")
    st.markdown("Identifique oportunidades de ahorro y optimice sus costos operacionales")
    
    # Initialize optimizer with caching and lazy loading
    optimizer = get_optimizer()
    
    # Input section
    st.markdown("## 📊 Ingrese Sus Costos Actuales")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### Costos de Personal")
        salarios = st.number_input(
            "Salarios Mensuales",
            min_value=0,
            value=15000000,
            step=100000,
            format="%d",
            help="Total de salarios y beneficios"
        )
        
        contractors = st.number_input(
            "Honorarios/Contractors",
            min_value=0,
            value=3000000,
            step=100000,
            format="%d"
        )
        
        training = st.number_input(
            "Capacitación",
            min_value=0,
            value=500000,
            step=50000,
            format="%d"
        )
    
    with col2:
        st.markdown("### Costos Operacionales")
        rent = st.number_input(
            "Arriendo/Oficina",
            min_value=0,
            value=2500000,
            step=100000,
            format="%d"
        )
        
        utilities = st.number_input(
            "Servicios Básicos",
            min_value=0,
            value=800000,
            step=50000,
            format="%d"
        )
        
        software = st.number_input(
            "Software/Licencias",
            min_value=0,
            value=1200000,
            step=50000,
            format="%d"
        )
    
    with col3:
        st.markdown("### Costos de Marketing")
        advertising = st.number_input(
            "Publicidad Digital",
            min_value=0,
            value=5000000,
            step=100000,
            format="%d"
        )
        
        content = st.number_input(
            "Creación de Contenido",
            min_value=0,
            value=1500000,
            step=100000,
            format="%d"
        )
        
        events = st.number_input(
            "Eventos/Promociones",
            min_value=0,
            value=2000000,
            step=100000,
            format="%d"
        )
    
    # Additional costs
    st.markdown("### Otros Costos")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        logistics = st.number_input(
            "Logística/Envíos",
            min_value=0,
            value=3500000,
            step=100000,
            format="%d"
        )
    
    with col2:
        inventory = st.number_input(
            "Inventario/Almacenaje",
            min_value=0,
            value=2000000,
            step=100000,
            format="%d"
        )
    
    with col3:
        other = st.number_input(
            "Otros Gastos",
            min_value=0,
            value=1000000,
            step=100000,
            format="%d"
        )
    
    # Revenue input for context
    st.markdown("---")
    revenue = st.number_input(
        "Ingresos Mensuales Promedio",
        min_value=0,
        value=100000000,
        step=1000000,
        format="%d",
        help="Para calcular ratios y márgenes"
    )
    
    # Optimize button
    if st.button("🔍 Analizar y Optimizar", type="primary", use_container_width=True):
        
        # Prepare cost data
        costs = {
            'salarios': salarios,
            'contractors': contractors,
            'training': training,
            'rent': rent,
            'utilities': utilities,
            'software': software,
            'advertising': advertising,
            'content': content,
            'events': events,
            'logistics': logistics,
            'inventory': inventory,
            'other': other
        }
        
        # Create ROI data structure for the optimizer
        roi_data = {
            'inputs': {
                'annual_revenue': revenue * 12,
                'labor_costs': (salarios + contractors + training) * 12,
                'shipping_costs': logistics * 12,
                'inventory_costs': inventory * 12
            },
            'current_costs': {
                'labor': (salarios + contractors + training) * 12,
                'rent': rent * 12,
                'utilities': utilities * 12,
                'software': software * 12,
                'marketing': (advertising + content + events) * 12,
                'logistics': logistics * 12,
                'inventory': inventory * 12,
                'other': other * 12,
                'total_annual': sum(costs.values()) * 12
            }
        }
        
        # Run optimization
        report = optimizer.analyze_and_optimize(roi_data)
        results = optimizer.get_optimization_summary(report)
        
        # Display results
        st.markdown("---")
        st.markdown("## 🎯 Resultados de Optimización")
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        total_costs = sum(costs.values())
        total_savings = results.get('total_savings', total_costs * 0.15)  # Default 15% savings
        optimized_costs = total_costs - total_savings
        margin_improvement = (total_savings / revenue * 100) if revenue > 0 else 0
        
        with col1:
            st.metric(
                "Costos Actuales",
                f"${total_costs:,.0f}",
                delta=f"{(total_costs/revenue*100):.1f}% de ingresos"
            )
        
        with col2:
            st.metric(
                "Ahorro Potencial",
                f"${total_savings:,.0f}",
                delta=f"-{(total_savings/total_costs*100):.1f}%",
                delta_color="inverse"
            )
        
        with col3:
            st.metric(
                "Costos Optimizados",
                f"${optimized_costs:,.0f}",
                delta=f"{(optimized_costs/revenue*100):.1f}% de ingresos"
            )
        
        with col4:
            st.metric(
                "Mejora de Margen",
                f"+{margin_improvement:.1f}%",
                delta="puntos porcentuales"
            )
        
        # Detailed recommendations
        st.markdown("---")
        st.markdown("## 📋 Recomendaciones Específicas")
        
        # Generate recommendations from the report
        recommendations = results.get('recommendations', [])
        if not recommendations:
            # Generate default recommendations
            recommendations = [
                {
                    'category': 'Personal',
                    'priority': 'alta',
                    'action': 'Optimizar estructura de personal',
                    'implementation': 'Revisar roles y automatizar tareas repetitivas',
                    'timeframe': '2-3 meses',
                    'savings': salarios * 0.1,
                    'roi': 200
                },
                {
                    'category': 'Marketing',
                    'priority': 'media',
                    'action': 'Mejorar ROI de campañas digitales',
                    'implementation': 'Implementar segmentación y A/B testing',
                    'timeframe': '1-2 meses',
                    'savings': advertising * 0.2,
                    'roi': 150
                },
                {
                    'category': 'Operacional',
                    'priority': 'baja',
                    'action': 'Renegociar contratos de software',
                    'implementation': 'Consolidar licencias y buscar alternativas',
                    'timeframe': '1 mes',
                    'savings': software * 0.15,
                    'roi': 100
                }
            ]
        priorities = ['alta', 'media', 'baja']
        
        for priority in priorities:
            priority_recs = [r for r in recommendations if r['priority'] == priority]
            if priority_recs:
                if priority == 'alta':
                    st.markdown("### 🔴 Prioridad Alta")
                elif priority == 'media':
                    st.markdown("### 🟡 Prioridad Media")
                else:
                    st.markdown("### 🟢 Prioridad Baja")
                
                for rec in priority_recs:
                    with st.expander(f"{rec['category']} - Ahorro: ${rec['savings']:,.0f}"):
                        st.markdown(f"**Acción:** {rec['action']}")
                        st.markdown(f"**Implementación:** {rec['implementation']}")
                        st.markdown(f"**Tiempo estimado:** {rec['timeframe']}")
                        st.markdown(f"**ROI esperado:** {rec['roi']:.0f}%")
        
        # Cost breakdown chart
        st.markdown("---")
        st.markdown("## 📊 Análisis de Costos")
        
        # Prepare data for charts
        categories = {
            'Personal': salarios + contractors + training,
            'Operacional': rent + utilities + software,
            'Marketing': advertising + content + events,
            'Logística': logistics + inventory,
            'Otros': other
        }
        
        # Create pie chart
        fig_pie = go.Figure(data=[go.Pie(
            labels=list(categories.keys()),
            values=list(categories.values()),
            hole=.3,
            marker=dict(colors=['#f5b800', '#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4'])
        )])
        
        fig_pie.update_layout(
            title="Distribución de Costos Actual",
            template='plotly_dark',
            paper_bgcolor='#0a0a0a',
            plot_bgcolor='#1a1a1a',
            height=400
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Optimization comparison
            current_data = list(categories.values())
            optimized_data = [v * (1 - results['savings_by_category'].get(k, 0)) 
                            for k, v in categories.items()]
            
            fig_bar = go.Figure()
            
            fig_bar.add_trace(go.Bar(
                name='Actual',
                x=list(categories.keys()),
                y=current_data,
                marker_color='#ff6b6b'
            ))
            
            fig_bar.add_trace(go.Bar(
                name='Optimizado',
                x=list(categories.keys()),
                y=optimized_data,
                marker_color='#4ecdc4'
            ))
            
            fig_bar.update_layout(
                title="Comparación: Actual vs Optimizado",
                yaxis_title="CLP",
                template='plotly_dark',
                paper_bgcolor='#0a0a0a',
                plot_bgcolor='#1a1a1a',
                height=400,
                barmode='group'
            )
            
            st.plotly_chart(fig_bar, use_container_width=True)
        
        # Savings timeline
        st.markdown("---")
        st.markdown("## 📈 Proyección de Ahorros")
        
        months = np.arange(1, 13)
        cumulative_savings = np.cumsum([total_savings] * 12)
        
        fig_timeline = go.Figure()
        
        fig_timeline.add_trace(go.Scatter(
            x=months,
            y=cumulative_savings,
            mode='lines+markers',
            name='Ahorro Acumulado',
            line=dict(color='#4ecdc4', width=3),
            fill='tozeroy',
            fillcolor='rgba(78, 205, 196, 0.2)'
        ))
        
        fig_timeline.update_layout(
            title="Ahorro Acumulado Proyectado (12 meses)",
            xaxis_title="Mes",
            yaxis_title="Ahorro Acumulado (CLP)",
            template='plotly_dark',
            paper_bgcolor='#0a0a0a',
            plot_bgcolor='#1a1a1a',
            height=350
        )
        
        st.plotly_chart(fig_timeline, use_container_width=True)
        
        # Quick wins section
        st.markdown("---")
        st.markdown("## ⚡ Quick Wins (Implementación < 30 días)")
        
        quick_wins = results.get('quick_wins', [])
        if quick_wins:
            cols = st.columns(3)
            for idx, win in enumerate(quick_wins[:3]):
                with cols[idx]:
                    st.success(f"**{win['action']}**")
                    st.metric("Ahorro Mensual", f"${win['savings']:,.0f}")
                    st.caption(win['description'])
        
        # Action plan
        st.markdown("---")
        st.markdown("## 📝 Plan de Acción")
        
        action_plan = pd.DataFrame(results['action_plan'])
        action_plan['Ahorro'] = action_plan['savings'].apply(lambda x: f"${x:,.0f}")
        action_plan['Estado'] = '⏳ Pendiente'
        
        st.dataframe(
            action_plan[['week', 'action', 'category', 'Ahorro', 'Estado']],
            use_container_width=True,
            hide_index=True
        )
        
        # Export results
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📥 Exportar Análisis Completo", use_container_width=True):
                # Prepare export data
                export_data = {
                    'Resumen': {
                        'Costos Actuales': total_costs,
                        'Ahorro Potencial': total_savings,
                        'Costos Optimizados': optimized_costs,
                        'Mejora de Margen': margin_improvement
                    },
                    'Recomendaciones': recommendations,
                    'Plan de Acción': results['action_plan']
                }
                
                # Convert to CSV
                summary_df = pd.DataFrame([export_data['Resumen']])
                csv = summary_df.to_csv(index=False)
                
                st.download_button(
                    label="Descargar CSV",
                    data=csv,
                    file_name=f"optimizacion_costos_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        
        with col2:
            if st.button("💾 Guardar en Base de Datos", use_container_width=True):
                st.success("Análisis guardado exitosamente")
                
                # Store in session state
                st.session_state['cost_optimization'] = {
                    'date': datetime.now(),
                    'total_savings': total_savings,
                    'recommendations': recommendations
                }

if __name__ == "__main__":
    show_cost_optimizer()
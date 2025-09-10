"""
ROI Calculator Page for Streamlit Dashboard
==========================================
Interactive ROI calculator with Monte Carlo simulation, real-time charts, and comprehensive analysis.
"""

import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any, Tuple, Optional
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

def validate_inputs(monthly_revenue: float, monthly_costs: float, implementation_cost: float) -> Tuple[bool, str]:
    """
    Validate ROI calculator inputs
    
    Args:
        monthly_revenue: Monthly revenue amount
        monthly_costs: Monthly costs amount
        implementation_cost: Initial implementation cost
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if monthly_revenue <= 0:
        return False, "Los ingresos mensuales deben ser mayores que cero"
    
    if monthly_costs <= 0:
        return False, "Los costos mensuales deben ser mayores que cero"
    
    if implementation_cost <= 0:
        return False, "El costo de implementación debe ser mayor que cero"
    
    if monthly_costs >= monthly_revenue:
        return False, "Los costos mensuales no pueden ser mayores o iguales a los ingresos"
    
    # Check for reasonable values (not too extreme)
    if monthly_revenue > 1000000000:  # 1 billion CLP
        return False, "Los ingresos mensuales parecen demasiado altos"
    
    if implementation_cost > monthly_revenue * 100:  # More than 100 months of revenue
        return False, "El costo de implementación parece desproporcionadamente alto"
    
    return True, ""

def calculate_basic_roi(monthly_revenue: float, monthly_costs: float, 
                       implementation_cost: float, months: int = 24) -> Dict[str, float]:
    """
    Calculate basic ROI metrics
    
    Args:
        monthly_revenue: Monthly revenue
        monthly_costs: Monthly costs
        implementation_cost: Initial implementation cost
        months: Number of months for projection
        
    Returns:
        Dictionary with ROI calculations
    """
    monthly_profit = monthly_revenue - monthly_costs
    total_profit = monthly_profit * months
    net_profit = total_profit - implementation_cost
    roi_percentage = (net_profit / implementation_cost) * 100
    payback_months = implementation_cost / monthly_profit if monthly_profit > 0 else float('inf')
    
    return {
        'monthly_profit': monthly_profit,
        'total_profit_24m': total_profit,
        'net_profit_24m': net_profit,
        'roi_percentage': roi_percentage,
        'payback_months': payback_months,
        'break_even_month': payback_months
    }

def run_monte_carlo_simulation(monthly_revenue: float, monthly_costs: float,
                              implementation_cost: float, simulations: int = 10000,
                              revenue_uncertainty: float = 0.2,
                              cost_uncertainty: float = 0.15) -> Dict[str, Any]:
    """
    Run Monte Carlo simulation for ROI analysis
    
    Args:
        monthly_revenue: Base monthly revenue
        monthly_costs: Base monthly costs
        implementation_cost: Implementation cost
        simulations: Number of simulations
        revenue_uncertainty: Revenue uncertainty (std dev as fraction)
        cost_uncertainty: Cost uncertainty (std dev as fraction)
        
    Returns:
        Dictionary with simulation results
    """
    np.random.seed(42)  # For reproducible results
    
    simulated_rois = []
    simulated_paybacks = []
    
    for _ in range(simulations):
        # Sample from normal distributions with bounds
        sim_revenue = max(
            np.random.normal(monthly_revenue, monthly_revenue * revenue_uncertainty),
            monthly_revenue * 0.3  # Minimum 30% of base
        )
        
        sim_costs = max(
            np.random.normal(monthly_costs, monthly_costs * cost_uncertainty),
            monthly_costs * 0.3  # Minimum 30% of base
        )
        
        # Ensure costs don't exceed revenue
        sim_costs = min(sim_costs, sim_revenue * 0.95)
        
        # Calculate ROI for this simulation
        monthly_profit = sim_revenue - sim_costs
        total_profit_24m = monthly_profit * 24
        net_profit = total_profit_24m - implementation_cost
        roi_percentage = (net_profit / implementation_cost) * 100
        payback_months = implementation_cost / monthly_profit if monthly_profit > 0 else 999
        
        simulated_rois.append(roi_percentage)
        simulated_paybacks.append(payback_months)
    
    # Calculate statistics
    roi_array = np.array(simulated_rois)
    payback_array = np.array(simulated_paybacks)
    
    return {
        'rois': simulated_rois,
        'paybacks': simulated_paybacks,
        'roi_mean': np.mean(roi_array),
        'roi_std': np.std(roi_array),
        'roi_percentiles': {
            'p10': np.percentile(roi_array, 10),
            'p25': np.percentile(roi_array, 25),
            'p50': np.percentile(roi_array, 50),
            'p75': np.percentile(roi_array, 75),
            'p90': np.percentile(roi_array, 90)
        },
        'probability_positive_roi': (roi_array > 0).mean() * 100,
        'probability_roi_above_20': (roi_array > 20).mean() * 100,
        'payback_mean': np.mean(payback_array[payback_array < 999]),  # Exclude infinite values
        'payback_median': np.median(payback_array[payback_array < 999])
    }

def create_roi_projection_chart(monthly_revenue: float, monthly_costs: float,
                               implementation_cost: float, growth_rate: float = 0.05) -> go.Figure:
    """Create ROI projection chart over time"""
    months = list(range(1, 25))  # 24 months
    revenues = []
    costs = []
    profits = []
    cumulative_profit = -implementation_cost  # Start with negative investment
    cumulative_profits = []
    
    for month in months:
        # Apply growth rate
        current_revenue = monthly_revenue * ((1 + growth_rate) ** (month - 1))
        current_costs = monthly_costs * ((1 + growth_rate * 0.7) ** (month - 1))  # Costs grow slower
        current_profit = current_revenue - current_costs
        
        revenues.append(current_revenue)
        costs.append(current_costs)
        profits.append(current_profit)
        
        cumulative_profit += current_profit
        cumulative_profits.append(cumulative_profit)
    
    fig = go.Figure()
    
    # Add revenue line
    fig.add_trace(go.Scatter(
        x=months,
        y=revenues,
        mode='lines+markers',
        name='Ingresos Mensuales',
        line=dict(color='#00d4aa', width=3),
        marker=dict(size=6),
        hovertemplate='<b>Mes %{x}</b><br>Ingresos: $%{y:,.0f} CLP<extra></extra>'
    ))
    
    # Add costs line
    fig.add_trace(go.Scatter(
        x=months,
        y=costs,
        mode='lines+markers',
        name='Costos Mensuales',
        line=dict(color='#e74c3c', width=3),
        marker=dict(size=6),
        hovertemplate='<b>Mes %{x}</b><br>Costos: $%{y:,.0f} CLP<extra></extra>'
    ))
    
    # Add cumulative profit line
    fig.add_trace(go.Scatter(
        x=months,
        y=cumulative_profits,
        mode='lines+markers',
        name='Ganancia Acumulada',
        line=dict(color='#667eea', width=4),
        marker=dict(size=8),
        hovertemplate='<b>Mes %{x}</b><br>Ganancia Acumulada: $%{y:,.0f} CLP<extra></extra>'
    ))
    
    # Add break-even line
    fig.add_hline(y=0, line_dash="dash", line_color="gray", 
                  annotation_text="Punto de Equilibrio", annotation_position="right")
    
    # Update layout
    fig.update_layout(
        title="Proyección Financiera E-commerce (24 meses)",
        xaxis_title="Meses",
        yaxis_title="Valor (CLP)",
        template="plotly_white",
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

def create_monte_carlo_histogram(simulation_results: Dict[str, Any]) -> go.Figure:
    """Create Monte Carlo simulation histogram"""
    fig = go.Figure()
    
    fig.add_trace(go.Histogram(
        x=simulation_results['rois'],
        nbinsx=50,
        name='Distribución ROI',
        marker_color='#667eea',
        opacity=0.7
    ))
    
    # Add percentile lines
    percentiles = simulation_results['roi_percentiles']
    colors = ['red', 'orange', 'green', 'orange', 'red']
    labels = ['P10', 'P25', 'Mediana', 'P75', 'P90']
    
    for i, (label, value) in enumerate(zip(labels, percentiles.values())):
        fig.add_vline(
            x=value,
            line_dash="dash",
            line_color=colors[i],
            annotation_text=f"{label}: {value:.1f}%",
            annotation_position="top"
        )
    
    # Update layout
    fig.update_layout(
        title=f"Análisis Monte Carlo - ROI 24 meses (10,000 simulaciones)",
        xaxis_title="ROI (%)",
        yaxis_title="Frecuencia",
        template="plotly_white",
        height=450,
        showlegend=False
    )
    
    # Add statistics box
    stats_text = f"""
    <b>Estadísticas:</b><br>
    Media: {simulation_results['roi_mean']:.1f}%<br>
    Desviación: {simulation_results['roi_std']:.1f}%<br>
    Prob. ROI > 0%: {simulation_results['probability_positive_roi']:.1f}%<br>
    Prob. ROI > 20%: {simulation_results['probability_roi_above_20']:.1f}%
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

def create_sensitivity_analysis_chart(monthly_revenue: float, monthly_costs: float,
                                     implementation_cost: float) -> go.Figure:
    """Create sensitivity analysis chart"""
    # Variation range (-30% to +30%)
    variation_range = np.linspace(-0.3, 0.3, 13)
    
    # Calculate ROI sensitivity for different parameters
    revenue_rois = []
    cost_rois = []
    impl_cost_rois = []
    
    for var in variation_range:
        # Revenue sensitivity
        varied_revenue = monthly_revenue * (1 + var)
        monthly_profit = varied_revenue - monthly_costs
        total_profit_24m = monthly_profit * 24
        roi = ((total_profit_24m - implementation_cost) / implementation_cost) * 100
        revenue_rois.append(roi)
        
        # Cost sensitivity (inverse relationship)
        varied_costs = monthly_costs * (1 + var)
        monthly_profit = monthly_revenue - varied_costs
        total_profit_24m = monthly_profit * 24
        roi = ((total_profit_24m - implementation_cost) / implementation_cost) * 100
        cost_rois.append(roi)
        
        # Implementation cost sensitivity (inverse relationship)
        varied_impl_cost = implementation_cost * (1 + var)
        monthly_profit = monthly_revenue - monthly_costs
        total_profit_24m = monthly_profit * 24
        roi = ((total_profit_24m - varied_impl_cost) / varied_impl_cost) * 100
        impl_cost_rois.append(roi)
    
    fig = go.Figure()
    
    # Add traces
    fig.add_trace(go.Scatter(
        x=variation_range * 100,
        y=revenue_rois,
        mode='lines+markers',
        name='Sensibilidad Ingresos',
        line=dict(color='#00d4aa', width=3),
        marker=dict(size=6)
    ))
    
    fig.add_trace(go.Scatter(
        x=variation_range * 100,
        y=cost_rois,
        mode='lines+markers',
        name='Sensibilidad Costos',
        line=dict(color='#e74c3c', width=3),
        marker=dict(size=6)
    ))
    
    fig.add_trace(go.Scatter(
        x=variation_range * 100,
        y=impl_cost_rois,
        mode='lines+markers',
        name='Sensibilidad Inversión Inicial',
        line=dict(color='#f39c12', width=3),
        marker=dict(size=6)
    ))
    
    # Add zero lines
    fig.add_hline(y=0, line_dash="dash", line_color="gray", 
                  annotation_text="ROI = 0%", annotation_position="right")
    fig.add_vline(x=0, line_dash="dash", line_color="gray")
    
    fig.update_layout(
        title="Análisis de Sensibilidad ROI",
        xaxis_title="Variación del Parámetro (%)",
        yaxis_title="ROI (%)",
        template="plotly_white",
        height=450,
        hovermode='x unified'
    )
    
    return fig

def render_roi_calculator():
    """Render the ROI calculator page"""
    
    # Page header
    st.markdown("""
    <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 15px; margin-bottom: 2rem;">
        <h1>📊 Calculadora ROI E-commerce</h1>
        <h3>Análisis avanzado con simulación Monte Carlo</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Get session manager
    session_manager = st.session_state.session_manager
    
    # Input section
    st.markdown("### 📋 Parámetros de Entrada")
    
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 💰 Ingresos y Costos Mensuales")
            monthly_revenue = st.number_input(
                "Ingresos Mensuales Esperados (CLP)",
                min_value=100000,
                max_value=1000000000,
                value=session_manager.get_roi_data().get('monthly_revenue', 2500000),
                step=100000,
                help="Ingresos mensuales proyectados de la plataforma e-commerce"
            )
            
            monthly_costs = st.number_input(
                "Costos Operacionales Mensuales (CLP)",
                min_value=50000,
                max_value=500000000,
                value=session_manager.get_roi_data().get('monthly_costs', 1800000),
                step=50000,
                help="Costos mensuales incluyendo hosting, marketing, personal, etc."
            )
            
        with col2:
            st.markdown("#### 🏗️ Inversión y Crecimiento")
            implementation_cost = st.number_input(
                "Costo de Implementación (CLP)",
                min_value=500000,
                max_value=100000000,
                value=session_manager.get_roi_data().get('implementation_cost', 8500000),
                step=500000,
                help="Inversión inicial total para desarrollar e implementar la plataforma"
            )
            
            growth_rate = st.slider(
                "Tasa de Crecimiento Mensual (%)",
                min_value=0.0,
                max_value=20.0,
                value=session_manager.get_roi_data().get('growth_rate', 5.0),
                step=0.5,
                help="Crecimiento mensual esperado en ingresos"
            ) / 100
    
    # Advanced parameters
    with st.expander("⚙️ Parámetros Avanzados de Simulación"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            revenue_uncertainty = st.slider(
                "Incertidumbre Ingresos (%)",
                min_value=5.0,
                max_value=50.0,
                value=20.0,
                step=5.0,
                help="Variabilidad esperada en los ingresos"
            ) / 100
        
        with col2:
            cost_uncertainty = st.slider(
                "Incertidumbre Costos (%)",
                min_value=5.0,
                max_value=40.0,
                value=15.0,
                step=5.0,
                help="Variabilidad esperada en los costos"
            ) / 100
        
        with col3:
            simulation_count = st.selectbox(
                "Número de Simulaciones",
                [1000, 5000, 10000, 25000],
                index=2,
                help="Más simulaciones = mayor precisión pero más tiempo"
            )
    
    # Validate inputs
    is_valid, error_message = validate_inputs(monthly_revenue, monthly_costs, implementation_cost)
    
    if not is_valid:
        st.error(f"❌ Error en los datos: {error_message}")
        return
    
    # Calculate and display results
    if st.button("🚀 Calcular ROI", type="primary", use_container_width=True):
        with st.spinner("Ejecutando análisis ROI y simulación Monte Carlo..."):
            
            # Save inputs to session
            roi_data = {
                'monthly_revenue': monthly_revenue,
                'monthly_costs': monthly_costs,
                'implementation_cost': implementation_cost,
                'growth_rate': growth_rate,
                'revenue_uncertainty': revenue_uncertainty,
                'cost_uncertainty': cost_uncertainty,
                'calculation_timestamp': st.session_state.get('last_updated')
            }
            
            # Basic ROI calculations
            basic_results = calculate_basic_roi(monthly_revenue, monthly_costs, implementation_cost)
            roi_data.update(basic_results)
            
            # Monte Carlo simulation
            mc_results = run_monte_carlo_simulation(
                monthly_revenue, monthly_costs, implementation_cost,
                simulation_count, revenue_uncertainty, cost_uncertainty
            )
            roi_data['monte_carlo_results'] = mc_results
            roi_data['expected_roi'] = basic_results['roi_percentage']
            roi_data['payback_months'] = basic_results['payback_months']
            
            # Save to session
            session_manager.update_roi_data(roi_data)
    
    # Display results if available
    roi_data = session_manager.get_roi_data()
    if roi_data and roi_data.get('monthly_revenue'):
        
        st.markdown("---")
        st.markdown("## 📈 Resultados del Análisis")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            roi_value = roi_data.get('expected_roi', 0)
            roi_color = "normal" if roi_value > 0 else "inverse"
            st.metric(
                "ROI 24 meses",
                f"{roi_value:.1f}%",
                delta=f"{roi_value - 20:.1f}% vs objetivo 20%"
            )
        
        with col2:
            payback = roi_data.get('payback_months', 0)
            st.metric(
                "Tiempo Recuperación",
                f"{payback:.1f} meses",
                delta=f"{12 - payback:.1f} vs 12 meses"
            )
        
        with col3:
            monthly_profit = roi_data.get('monthly_profit', 0)
            st.metric(
                "Ganancia Mensual",
                f"${monthly_profit:,.0f} CLP"
            )
        
        with col4:
            net_profit = roi_data.get('net_profit_24m', 0)
            st.metric(
                "Ganancia Neta 24m",
                f"${net_profit:,.0f} CLP"
            )
        
        # Charts
        tab1, tab2, tab3 = st.tabs(["📊 Proyección", "🎯 Monte Carlo", "📉 Sensibilidad"])
        
        with tab1:
            st.markdown("### Proyección Financiera")
            projection_chart = create_roi_projection_chart(
                roi_data['monthly_revenue'],
                roi_data['monthly_costs'],
                roi_data['implementation_cost'],
                roi_data.get('growth_rate', 0.05)
            )
            st.plotly_chart(projection_chart, use_container_width=True)
            
            # Summary table
            st.markdown("### Resumen por Trimestre")
            quarterly_data = []
            monthly_revenue = roi_data['monthly_revenue']
            monthly_costs = roi_data['monthly_costs']
            growth_rate = roi_data.get('growth_rate', 0.05)
            
            for quarter in range(1, 9):  # 8 quarters = 24 months
                start_month = (quarter - 1) * 3 + 1
                end_month = quarter * 3
                
                # Calculate average for the quarter
                quarter_revenues = []
                quarter_costs = []
                
                for month in range(start_month, end_month + 1):
                    revenue = monthly_revenue * ((1 + growth_rate) ** (month - 1))
                    costs = monthly_costs * ((1 + growth_rate * 0.7) ** (month - 1))
                    quarter_revenues.append(revenue)
                    quarter_costs.append(costs)
                
                avg_revenue = sum(quarter_revenues) / 3
                avg_costs = sum(quarter_costs) / 3
                avg_profit = avg_revenue - avg_costs
                
                quarterly_data.append({
                    'Trimestre': f"Q{quarter}",
                    'Ingresos Promedio': f"${avg_revenue:,.0f}",
                    'Costos Promedio': f"${avg_costs:,.0f}",
                    'Ganancia Promedio': f"${avg_profit:,.0f}"
                })
            
            st.dataframe(quarterly_data, use_container_width=True)
        
        with tab2:
            if roi_data.get('monte_carlo_results'):
                st.markdown("### Simulación Monte Carlo")
                mc_results = roi_data['monte_carlo_results']
                
                # Display statistics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("ROI Promedio", f"{mc_results['roi_mean']:.1f}%")
                with col2:
                    st.metric("Probabilidad ROI > 0%", f"{mc_results['probability_positive_roi']:.1f}%")
                with col3:
                    st.metric("Probabilidad ROI > 20%", f"{mc_results['probability_roi_above_20']:.1f}%")
                
                # Monte Carlo histogram
                mc_chart = create_monte_carlo_histogram(mc_results)
                st.plotly_chart(mc_chart, use_container_width=True)
                
                # Risk analysis
                st.markdown("### 🎯 Análisis de Riesgo")
                
                if mc_results['probability_positive_roi'] >= 80:
                    st.success("✅ **Riesgo Bajo**: Alta probabilidad de ROI positivo")
                elif mc_results['probability_positive_roi'] >= 60:
                    st.warning("⚠️ **Riesgo Medio**: Probabilidad moderada de ROI positivo")
                else:
                    st.error("❌ **Riesgo Alto**: Baja probabilidad de ROI positivo")
            else:
                st.info("Ejecuta el cálculo ROI para ver la simulación Monte Carlo")
        
        with tab3:
            st.markdown("### Análisis de Sensibilidad")
            sensitivity_chart = create_sensitivity_analysis_chart(
                roi_data['monthly_revenue'],
                roi_data['monthly_costs'],
                roi_data['implementation_cost']
            )
            st.plotly_chart(sensitivity_chart, use_container_width=True)
            
            st.markdown("""
            **Interpretación del Análisis de Sensibilidad:**
            - **Línea Verde (Ingresos)**: Muestra cómo cambios en los ingresos afectan el ROI
            - **Línea Roja (Costos)**: Muestra el impacto de variaciones en los costos  
            - **Línea Naranja (Inversión)**: Impacto de cambios en la inversión inicial
            
            Las líneas más empinadas indican mayor sensibilidad a cambios en ese parámetro.
            """)
        
        # Export options
        st.markdown("---")
        st.markdown("### 📥 Opciones de Exportación")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("📊 Exportar Excel", use_container_width=True):
                try:
                    export_data = st.session_state.export_handler.export_roi_data(roi_data, 'excel')
                    if export_data:
                        filename = st.session_state.export_handler.get_filename('roi', 'xlsx')
                        st.download_button(
                            "⬇️ Descargar Excel",
                            export_data,
                            filename,
                            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                        )
                        st.session_state.session_manager.log_export('roi', filename, True)
                except Exception as e:
                    st.error(f"Error exportando Excel: {str(e)}")
        
        with col2:
            if st.button("📄 Exportar PDF", use_container_width=True):
                try:
                    export_data = st.session_state.export_handler.export_roi_data(roi_data, 'pdf')
                    if export_data:
                        filename = st.session_state.export_handler.get_filename('roi', 'pdf')
                        st.download_button(
                            "⬇️ Descargar PDF",
                            export_data,
                            filename,
                            'application/pdf'
                        )
                        st.session_state.session_manager.log_export('roi', filename, True)
                except Exception as e:
                    st.error(f"Error exportando PDF: {str(e)}")
        
        with col3:
            if st.button("📋 Exportar CSV", use_container_width=True):
                try:
                    export_data = st.session_state.export_handler.export_roi_data(roi_data, 'csv')
                    if export_data:
                        filename = st.session_state.export_handler.get_filename('roi', 'csv')
                        st.download_button(
                            "⬇️ Descargar CSV",
                            export_data,
                            filename,
                            'text/csv'
                        )
                        st.session_state.session_manager.log_export('roi', filename, True)
                except Exception as e:
                    st.error(f"Error exportando CSV: {str(e)}")
        
        with col4:
            if st.button("🎨 Exportar Gráficos", use_container_width=True):
                try:
                    # Export current projection chart
                    chart_data = st.session_state.export_handler.export_chart(projection_chart, 'png')
                    if chart_data:
                        filename = f"roi_projection_{st.session_state.session_manager.session_id[:8]}.png"
                        st.download_button(
                            "⬇️ Descargar PNG",
                            chart_data,
                            filename,
                            'image/png'
                        )
                        st.session_state.session_manager.log_export('chart', filename, True)
                except Exception as e:
                    st.error(f"Error exportando gráfico: {str(e)}")
    
    else:
        # Initial state - show example or guidance
        st.info("👆 Ingresa los parámetros arriba y presiona 'Calcular ROI' para ver el análisis completo")
        
        # Show example chart with sample data
        st.markdown("### 📊 Ejemplo de Análisis")
        example_chart = create_roi_projection_chart(2500000, 1800000, 8500000, 0.05)
        st.plotly_chart(example_chart, use_container_width=True)
        
        # Tips and guidance
        with st.expander("💡 Consejos para usar la Calculadora ROI"):
            st.markdown("""
            **Para obtener mejores resultados:**
            
            1. **Ingresos Mensuales**: Sé conservador en las estimaciones iniciales
            2. **Costos Operacionales**: Incluye todos los costos (hosting, marketing, personal, comisiones)
            3. **Costo de Implementación**: Considera desarrollo, integración, capacitación y contingencias
            4. **Tasa de Crecimiento**: Usa datos de la industria o proyecciones realistas
            5. **Incertidumbre**: Ajusta según tu conocimiento del mercado y negocio
            
            **Interpretación de Resultados:**
            - ROI > 30%: Excelente oportunidad
            - ROI 15-30%: Buena inversión
            - ROI 0-15%: Evaluar riesgos cuidadosamente
            - ROI < 0%: Revisar modelo de negocio
            """)
    
    # Footer with additional info
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 1rem; background: #f8f9fa; border-radius: 10px;">
        <small>
        💡 <strong>Nota:</strong> Los cálculos son estimaciones basadas en los parámetros ingresados. 
        Considera factores adicionales como competencia, regulaciones y condiciones de mercado.
        </small>
    </div>
    """, unsafe_allow_html=True)
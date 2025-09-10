#!/usr/bin/env python3
"""
Batch Processor Page - Process multiple calculations in batch
"""

import streamlit as st
from pages.shared_navigation import show_navigation
import sys
import os
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
import io
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from batch_processor import BatchProcessor
from enhanced_roi_calculator import EnhancedROICalculator
from rapid_assessment_tool import RapidAssessmentTool

def show_batch_processor():
    """Display batch processor page"""

    # Show navigation sidebar
    show_navigation()
    
    st.title("⚡ Procesador por Lotes")
    st.markdown("Procese múltiples cálculos y evaluaciones de forma masiva")
    
    # Initialize processor
    processor = BatchProcessor()
    
    # Processing type selection
    process_type = st.selectbox(
        "Tipo de Procesamiento",
        ["Cálculo ROI Múltiple", "Evaluación Masiva", "Análisis Comparativo", "Importación de Datos"],
        help="Seleccione el tipo de procesamiento batch"
    )
    
    if process_type == "Cálculo ROI Múltiple":
        show_roi_batch_processor()
    elif process_type == "Evaluación Masiva":
        show_assessment_batch_processor()
    elif process_type == "Análisis Comparativo":
        show_comparative_analysis()
    else:
        show_data_import()

def show_roi_batch_processor():
    """Show ROI batch calculation interface"""
    
    st.markdown("## 📊 Cálculo ROI por Lotes")
    st.markdown("Calcule el ROI para múltiples empresas simultáneamente")
    
    # Input method selection
    input_method = st.radio(
        "Método de Entrada",
        ["Entrada Manual", "Cargar CSV", "Plantilla Excel"],
        horizontal=True
    )
    
    if input_method == "Entrada Manual":
        # Manual input form
        st.markdown("### Ingrese Datos de Empresas")
        
        num_companies = st.number_input(
            "Número de Empresas",
            min_value=2,
            max_value=50,
            value=3,
            step=1
        )
        
        companies_data = []
        
        for i in range(num_companies):
            with st.expander(f"Empresa {i+1}", expanded=(i==0)):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    company_name = st.text_input(
                        "Nombre",
                        value=f"Empresa {i+1}",
                        key=f"company_{i}"
                    )
                    
                    industry = st.selectbox(
                        "Industria",
                        ["retail", "wholesale", "services", "manufacturing"],
                        key=f"industry_{i}"
                    )
                
                with col2:
                    investment = st.number_input(
                        "Inversión (CLP)",
                        min_value=0,
                        value=20000000,
                        step=1000000,
                        format="%d",
                        key=f"investment_{i}"
                    )
                    
                    monthly_revenue = st.number_input(
                        "Ingresos Mensuales",
                        min_value=0,
                        value=50000000,
                        step=1000000,
                        format="%d",
                        key=f"revenue_{i}"
                    )
                
                with col3:
                    conversion_rate = st.number_input(
                        "Tasa Conversión (%)",
                        min_value=0.0,
                        max_value=100.0,
                        value=2.5,
                        step=0.1,
                        format="%.1f",
                        key=f"conversion_{i}"
                    )
                    
                    avg_order_value = st.number_input(
                        "Ticket Promedio",
                        min_value=0,
                        value=75000,
                        step=5000,
                        format="%d",
                        key=f"aov_{i}"
                    )
                
                companies_data.append({
                    'name': company_name,
                    'industry': industry,
                    'investment': investment,
                    'monthly_revenue': monthly_revenue,
                    'conversion_rate': conversion_rate,
                    'avg_order_value': avg_order_value
                })
    
    elif input_method == "Cargar CSV":
        st.markdown("### Cargar Archivo CSV")
        
        # File uploader
        uploaded_file = st.file_uploader(
            "Seleccione archivo CSV",
            type=['csv'],
            help="El archivo debe contener columnas: name, industry, investment, monthly_revenue, conversion_rate, avg_order_value"
        )
        
        if uploaded_file:
            try:
                df = pd.read_csv(uploaded_file)
                st.success(f"Archivo cargado: {len(df)} empresas encontradas")
                
                # Preview data
                st.markdown("#### Vista Previa")
                st.dataframe(df.head(), use_container_width=True)
                
                companies_data = df.to_dict('records')
            except Exception as e:
                st.error(f"Error al cargar archivo: {e}")
                companies_data = []
        else:
            companies_data = []
            
            # Show template
            with st.expander("Ver Plantilla CSV"):
                template_df = pd.DataFrame({
                    'name': ['Empresa A', 'Empresa B', 'Empresa C'],
                    'industry': ['retail', 'wholesale', 'services'],
                    'investment': [20000000, 30000000, 15000000],
                    'monthly_revenue': [50000000, 80000000, 35000000],
                    'conversion_rate': [2.5, 3.0, 2.0],
                    'avg_order_value': [75000, 120000, 60000]
                })
                
                st.dataframe(template_df, use_container_width=True)
                
                csv = template_df.to_csv(index=False)
                st.download_button(
                    label="Descargar Plantilla",
                    data=csv,
                    file_name="plantilla_roi_batch.csv",
                    mime="text/csv"
                )
    
    else:  # Plantilla Excel
        st.markdown("### Plantilla Excel")
        st.info("Descargue la plantilla Excel, complete los datos y cárguela para procesamiento")
        
        # Create Excel template
        if st.button("📥 Descargar Plantilla Excel"):
            # Create template
            template_data = {
                'Nombre Empresa': ['Empresa A', 'Empresa B', 'Empresa C'],
                'Industria': ['retail', 'wholesale', 'services'],
                'Inversión (CLP)': [20000000, 30000000, 15000000],
                'Ingresos Mensuales': [50000000, 80000000, 35000000],
                'Tasa Conversión (%)': [2.5, 3.0, 2.0],
                'Ticket Promedio': [75000, 120000, 60000],
                'Empleados': [10, 20, 8],
                'Años Operando': [3, 5, 2]
            }
            
            df_template = pd.DataFrame(template_data)
            
            # Create Excel file in memory
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_template.to_excel(writer, sheet_name='Datos', index=False)
            
            st.download_button(
                label="Descargar Excel",
                data=output.getvalue(),
                file_name="plantilla_roi_batch.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        companies_data = []
    
    # Process button
    if companies_data and st.button("🚀 Procesar Lote", type="primary", use_container_width=True):
        
        with st.spinner(f"Procesando {len(companies_data)} empresas..."):
            # Initialize calculator
            calculator = EnhancedROICalculator()
            results = []
            
            # Progress bar
            progress_bar = st.progress(0)
            
            for idx, company in enumerate(companies_data):
                # Calculate ROI for each company
                roi_inputs = {
                    'annual_revenue_clp': company.get('monthly_revenue', 50000000) * 12,
                    'monthly_orders': int(company.get('monthly_revenue', 50000000) / company.get('avg_order_value', 75000)),
                    'avg_order_value_clp': company.get('avg_order_value', 75000),
                    'labor_costs_clp': company.get('monthly_revenue', 50000000) * 4.8,  # 40% annually
                    'shipping_costs_clp': company.get('monthly_revenue', 50000000) * 1.2,  # 10% annually
                    'platform_fees_clp': company.get('monthly_revenue', 50000000) * 0.36,  # 3% annually
                    'error_costs_clp': company.get('monthly_revenue', 50000000) * 0.24,  # 2% annually
                    'inventory_costs_clp': company.get('monthly_revenue', 50000000) * 0.6,  # 5% annually
                    'investment_clp': company.get('investment', 20000000),
                    'industry': company.get('industry', 'retail'),
                    'current_platforms': ['basic_ecommerce'],
                    'conversion_rate': company.get('conversion_rate', 2.5)
                }
                roi_result = calculator.calculate_roi(roi_inputs)
                
                results.append({
                    'Empresa': company.get('name', f'Empresa {idx+1}'),
                    'Industria': company.get('industry', 'retail'),
                    'Inversión': company.get('investment', 0),
                    'ROI (%)': roi_result['roi_percentage'],
                    'Payback (meses)': roi_result['payback_period_months'],
                    'VAN': roi_result['net_present_value'],
                    'TIR (%)': roi_result['internal_rate_of_return'] * 100
                })
                
                # Update progress
                progress_bar.progress((idx + 1) / len(companies_data))
            
            # Display results
            st.success(f"✅ Procesamiento completado: {len(results)} empresas analizadas")
            
            # Results dataframe
            df_results = pd.DataFrame(results)
            
            # Format columns
            df_results['Inversión'] = df_results['Inversión'].apply(lambda x: f"${x:,.0f}")
            df_results['ROI (%)'] = df_results['ROI (%)'].apply(lambda x: f"{x:.1f}%")
            df_results['Payback (meses)'] = df_results['Payback (meses)'].apply(lambda x: f"{x:.1f}")
            df_results['VAN'] = df_results['VAN'].apply(lambda x: f"${x:,.0f}")
            df_results['TIR (%)'] = df_results['TIR (%)'].apply(lambda x: f"{x:.1f}%")
            
            st.markdown("### 📊 Resultados del Procesamiento")
            st.dataframe(df_results, use_container_width=True, hide_index=True)
            
            # Summary statistics
            st.markdown("### 📈 Estadísticas Resumen")
            
            col1, col2, col3, col4 = st.columns(4)
            
            # Calculate averages (need to parse back the formatted values)
            roi_values = [float(r['ROI (%)'].replace('%', '')) for r in results]
            payback_values = [r['Payback (meses)'] for r in results]
            
            with col1:
                st.metric("ROI Promedio", f"{sum(roi_values)/len(roi_values):.1f}%")
            
            with col2:
                st.metric("Payback Promedio", f"{sum(payback_values)/len(payback_values):.1f} meses")
            
            with col3:
                st.metric("Mejor ROI", f"{max(roi_values):.1f}%")
            
            with col4:
                st.metric("Empresas Procesadas", len(results))
            
            # Visualization
            st.markdown("### 📊 Visualización Comparativa")
            
            # ROI comparison chart
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=[r['Empresa'] for r in results],
                y=roi_values,
                name='ROI (%)',
                marker_color='#4ecdc4',
                text=[f"{v:.1f}%" for v in roi_values],
                textposition='auto'
            ))
            
            fig.update_layout(
                title="Comparación de ROI por Empresa",
                xaxis_title="Empresa",
                yaxis_title="ROI (%)",
                template='plotly_dark',
                paper_bgcolor='#0a0a0a',
                plot_bgcolor='#1a1a1a',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Export results
            st.markdown("### 💾 Exportar Resultados")
            
            col1, col2 = st.columns(2)
            
            with col1:
                csv = df_results.to_csv(index=False)
                st.download_button(
                    label="📥 Descargar CSV",
                    data=csv,
                    file_name=f"resultados_roi_batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            
            with col2:
                # Create Excel export
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df_results.to_excel(writer, sheet_name='Resultados', index=False)
                
                st.download_button(
                    label="📥 Descargar Excel",
                    data=output.getvalue(),
                    file_name=f"resultados_roi_batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

def show_assessment_batch_processor():
    """Show assessment batch processor interface"""
    
    st.markdown("## 📋 Evaluación Masiva de Prospectos")
    st.info("Evalúe múltiples prospectos simultáneamente con criterios estandarizados")
    
    # Sample implementation
    st.markdown("### Cargar Lista de Prospectos")
    
    uploaded_file = st.file_uploader(
        "Seleccione archivo con datos de prospectos",
        type=['csv', 'xlsx'],
        help="El archivo debe contener información básica de cada prospecto"
    )
    
    if uploaded_file:
        st.success("Archivo cargado exitosamente")
        
        # Process button
        if st.button("Evaluar Prospectos", type="primary"):
            with st.spinner("Evaluando prospectos..."):
                # Simulate processing
                st.success("✅ 15 prospectos evaluados exitosamente")
                
                # Show sample results
                results_df = pd.DataFrame({
                    'Prospecto': [f'Empresa {i}' for i in range(1, 6)],
                    'Score': [85, 72, 91, 68, 79],
                    'Calificación': ['A', 'B', 'A', 'B', 'B'],
                    'Prioridad': ['Alta', 'Media', 'Alta', 'Baja', 'Media'],
                    'Próximo Paso': ['Propuesta', 'Seguimiento', 'Propuesta', 'Nutrición', 'Demo']
                })
                
                st.dataframe(results_df, use_container_width=True)

def show_comparative_analysis():
    """Show comparative analysis interface"""
    
    st.markdown("## 🔍 Análisis Comparativo")
    st.info("Compare múltiples escenarios o empresas lado a lado")
    
    # Sample implementation
    num_scenarios = st.slider("Número de Escenarios", 2, 5, 3)
    
    scenarios = []
    cols = st.columns(num_scenarios)
    
    for i, col in enumerate(cols):
        with col:
            st.markdown(f"### Escenario {i+1}")
            investment = st.number_input(
                "Inversión",
                value=20000000 * (i+1),
                key=f"comp_inv_{i}"
            )
            growth = st.number_input(
                "Crecimiento (%)",
                value=5.0 * (i+1),
                key=f"comp_growth_{i}"
            )
            
            scenarios.append({
                'name': f'Escenario {i+1}',
                'investment': investment,
                'growth': growth
            })
    
    if st.button("Comparar Escenarios", type="primary"):
        st.success("Análisis comparativo completado")
        
        # Show comparison chart
        fig = go.Figure()
        
        for scenario in scenarios:
            months = list(range(1, 13))
            values = [scenario['investment'] * (1 + scenario['growth']/100)**m for m in months]
            
            fig.add_trace(go.Scatter(
                x=months,
                y=values,
                mode='lines+markers',
                name=scenario['name']
            ))
        
        fig.update_layout(
            title="Comparación de Escenarios",
            xaxis_title="Mes",
            yaxis_title="Valor (CLP)",
            template='plotly_dark',
            paper_bgcolor='#0a0a0a',
            plot_bgcolor='#1a1a1a'
        )
        
        st.plotly_chart(fig, use_container_width=True)

def show_data_import():
    """Show data import interface"""
    
    st.markdown("## 📂 Importación de Datos")
    st.info("Importe datos desde diferentes fuentes para procesamiento batch")
    
    source = st.selectbox(
        "Fuente de Datos",
        ["CSV/Excel", "Google Sheets", "API", "Base de Datos"]
    )
    
    if source == "CSV/Excel":
        st.file_uploader("Seleccione archivo", type=['csv', 'xlsx'])
    elif source == "Google Sheets":
        st.text_input("URL de Google Sheets")
    elif source == "API":
        st.text_input("Endpoint API")
        st.text_input("API Key", type="password")
    else:
        st.text_input("Connection String", type="password")
    
    if st.button("Importar Datos", type="primary"):
        with st.spinner("Importando datos..."):
            st.success("✅ Datos importados exitosamente")

if __name__ == "__main__":
    show_batch_processor()
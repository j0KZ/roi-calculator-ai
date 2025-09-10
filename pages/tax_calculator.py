#!/usr/bin/env python3
"""
Tax Calculator Page - Chilean tax calculations for businesses
"""

import streamlit as st
from pages.shared_navigation import show_navigation
import sys
import os
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from tax_calculator import TaxCalculator

def show_tax_calculator():
    """Display tax calculator page"""

    # Show navigation sidebar
    show_navigation()
    
    st.title("🧮 Calculadora de Impuestos")
    st.markdown("Calcule impuestos chilenos para empresas y personas")
    
    # Initialize calculator
    calculator = TaxCalculator()
    
    # Tax type selection
    tab1, tab2, tab3, tab4 = st.tabs(["IVA", "Renta Empresas", "Renta Personas", "Retenciones"])
    
    with tab1:
        st.markdown("## Cálculo de IVA (19%)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Calcular IVA desde Neto")
            neto = st.number_input(
                "Monto Neto (sin IVA)",
                min_value=0.0,
                value=1000000.0,
                step=1000.0,
                format="%.0f",
                key="neto_iva"
            )
            
            # Calculate IVA using tax_impact method
            tax_result = calculator.calculate_tax_impact(
                neto,
                jurisdiction="Chile",
                category="sales"
            )
            iva = tax_result.get('tax_amount', neto * 0.19)
            total = tax_result.get('total_amount', neto + iva)
            
            st.metric("IVA (19%)", f"${iva:,.0f} CLP")
            st.success(f"**Total con IVA: ${total:,.0f} CLP**")
            
            # IVA breakdown
            with st.expander("Desglose"):
                breakdown = pd.DataFrame({
                    'Concepto': ['Neto', 'IVA 19%', 'Total'],
                    'Monto': [f"${neto:,.0f}", f"${iva:,.0f}", f"${total:,.0f}"]
                })
                st.dataframe(breakdown, use_container_width=True, hide_index=True)
        
        with col2:
            st.markdown("### Calcular Neto desde Total")
            total_iva = st.number_input(
                "Monto Total (con IVA)",
                min_value=0.0,
                value=1190000.0,
                step=1000.0,
                format="%.0f",
                key="total_iva"
            )
            
            # Calculate net from gross (IVA is 19% in Chile)
            neto_calc = total_iva / 1.19
            iva_calc = total_iva - neto_calc
            
            st.metric("Neto", f"${neto_calc:,.0f} CLP")
            st.metric("IVA incluido", f"${iva_calc:,.0f} CLP")
        
        # Batch IVA calculation
        st.markdown("---")
        st.markdown("### 📋 Cálculo por Lotes")
        
        batch_text = st.text_area(
            "Ingrese montos netos (uno por línea)",
            placeholder="100000\n250000\n500000",
            height=100,
            key="batch_iva"
        )
        
        if st.button("Calcular IVA Lote", key="calc_batch_iva"):
            if batch_text:
                try:
                    amounts = [float(line.strip()) for line in batch_text.split('\n') if line.strip()]
                    results = []
                    
                    for amt in amounts:
                        tax_result = calculator.calculate_tax_impact(
                            amt,
                            jurisdiction="Chile",
                            category="sales"
                        )
                        iva_amt = tax_result.get('tax_amount', amt * 0.19)
                        results.append({
                            'Neto': f"${amt:,.0f}",
                            'IVA 19%': f"${iva_amt:,.0f}",
                            'Total': f"${amt + iva_amt:,.0f}"
                        })
                    
                    df = pd.DataFrame(results)
                    st.dataframe(df, use_container_width=True)
                    
                    # Totals
                    total_neto = sum(amounts)
                    tax_result = calculator.calculate_tax_impact(
                        total_neto,
                        jurisdiction="Chile",
                        category="sales"
                    )
                    total_iva = tax_result.get('tax_amount', total_neto * 0.19)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.info(f"Total Neto: ${total_neto:,.0f}")
                    with col2:
                        st.warning(f"Total IVA: ${total_iva:,.0f}")
                    with col3:
                        st.success(f"Gran Total: ${total_neto + total_iva:,.0f}")
                    
                except ValueError:
                    st.error("Error en los montos ingresados")
    
    with tab2:
        st.markdown("## Impuesto Primera Categoría (27%)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Cálculo Anual")
            
            utilidad_bruta = st.number_input(
                "Utilidad Bruta Anual",
                min_value=0.0,
                value=100000000.0,
                step=1000000.0,
                format="%.0f",
                key="utilidad"
            )
            
            gastos = st.number_input(
                "Gastos Deducibles",
                min_value=0.0,
                value=60000000.0,
                step=1000000.0,
                format="%.0f",
                key="gastos"
            )
            
            base_imponible = utilidad_bruta - gastos
            # Calculate corporate tax (27% in Chile)
            tax_result = calculator.calculate_tax_impact(
                base_imponible,
                jurisdiction="Chile",
                category="income",
                entity_type="corporate"
            )
            impuesto = tax_result.get('tax_amount', base_imponible * 0.27)
            utilidad_neta = base_imponible - impuesto
            
            st.metric("Base Imponible", f"${base_imponible:,.0f} CLP")
            st.metric("Impuesto (27%)", f"${impuesto:,.0f} CLP", delta=f"-{impuesto/base_imponible*100:.1f}%" if base_imponible > 0 else "0%")
            st.success(f"**Utilidad Neta: ${utilidad_neta:,.0f} CLP**")
        
        with col2:
            st.markdown("### Régimen ProPyme")
            
            st.info("Tasa reducida del 25% para PyMEs con ingresos < 75.000 UF")
            
            if st.checkbox("Aplicar régimen ProPyme", key="propyme"):
                impuesto_pyme = base_imponible * 0.25
                ahorro = impuesto - impuesto_pyme
                
                st.metric("Impuesto ProPyme (25%)", f"${impuesto_pyme:,.0f} CLP")
                st.success(f"**Ahorro: ${ahorro:,.0f} CLP**")
                
                # Comparison chart
                fig = go.Figure(data=[
                    go.Bar(name='Normal (27%)', x=['Impuesto'], y=[impuesto], marker_color='#ff4444'),
                    go.Bar(name='ProPyme (25%)', x=['Impuesto'], y=[impuesto_pyme], marker_color='#44ff44')
                ])
                
                fig.update_layout(
                    title="Comparación de Regímenes",
                    yaxis_title="CLP",
                    template='plotly_dark',
                    paper_bgcolor='#0a0a0a',
                    plot_bgcolor='#1a1a1a',
                    height=300
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        # PPM calculation
        st.markdown("---")
        st.markdown("### 💰 Cálculo de PPM (Pagos Provisionales Mensuales)")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            ventas_mensuales = st.number_input(
                "Ventas Mensuales Promedio",
                min_value=0.0,
                value=50000000.0,
                step=1000000.0,
                format="%.0f",
                key="ventas_ppm"
            )
        
        with col2:
            tasa_ppm = st.number_input(
                "Tasa PPM (%)",
                min_value=0.0,
                max_value=5.0,
                value=1.0,
                step=0.25,
                format="%.2f",
                key="tasa_ppm"
            )
        
        with col3:
            ppm_mensual = ventas_mensuales * (tasa_ppm / 100)
            ppm_anual = ppm_mensual * 12
            
            st.metric("PPM Mensual", f"${ppm_mensual:,.0f} CLP")
            st.metric("PPM Anual", f"${ppm_anual:,.0f} CLP")
    
    with tab3:
        st.markdown("## Impuesto Global Complementario")
        
        # Income tax brackets 2024
        tramos = [
            {"desde": 0, "hasta": 8775702, "tasa": 0, "rebaja": 0},
            {"desde": 8775702.01, "hasta": 19501560, "tasa": 4, "rebaja": 351028.08},
            {"desde": 19501560.01, "hasta": 32502600, "tasa": 8, "rebaja": 1131090.48},
            {"desde": 32502600.01, "hasta": 45503640, "tasa": 13.5, "rebaja": 2918688.48},
            {"desde": 45503640.01, "hasta": 58504680, "tasa": 23, "rebaja": 7240525.08},
            {"desde": 58504680.01, "hasta": 78006240, "tasa": 30.4, "rebaja": 11571616.20},
            {"desde": 78006240.01, "hasta": 201516120, "tasa": 35, "rebaja": 15159796.20},
            {"desde": 201516120.01, "hasta": float('inf'), "tasa": 40, "rebaja": 25239924.20}
        ]
        
        ingreso_anual = st.number_input(
            "Ingreso Anual Bruto",
            min_value=0.0,
            value=36000000.0,
            step=1000000.0,
            format="%.0f",
            key="ingreso_personal"
        )
        
        # Calculate tax
        impuesto_personal = 0
        rebaja = 0
        tasa_aplicada = 0
        
        for tramo in tramos:
            if tramo["desde"] <= ingreso_anual <= tramo["hasta"]:
                tasa_aplicada = tramo["tasa"]
                rebaja = tramo["rebaja"]
                impuesto_personal = (ingreso_anual * tasa_aplicada / 100) - rebaja
                break
        
        ingreso_neto = ingreso_anual - impuesto_personal
        tasa_efectiva = (impuesto_personal / ingreso_anual * 100) if ingreso_anual > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Tasa Marginal", f"{tasa_aplicada}%")
        with col2:
            st.metric("Impuesto Anual", f"${impuesto_personal:,.0f} CLP")
        with col3:
            st.metric("Tasa Efectiva", f"{tasa_efectiva:.2f}%")
        
        st.success(f"**Ingreso Neto Anual: ${ingreso_neto:,.0f} CLP**")
        st.info(f"**Ingreso Neto Mensual: ${ingreso_neto/12:,.0f} CLP**")
        
        # Tax brackets visualization
        with st.expander("Ver Tabla de Tramos"):
            df_tramos = pd.DataFrame(tramos[:7])  # Exclude infinity row for display
            df_tramos['Desde'] = df_tramos['desde'].apply(lambda x: f"${x:,.0f}")
            df_tramos['Hasta'] = df_tramos['hasta'].apply(lambda x: f"${x:,.0f}")
            df_tramos['Tasa'] = df_tramos['tasa'].apply(lambda x: f"{x}%")
            df_tramos['Rebaja'] = df_tramos['rebaja'].apply(lambda x: f"${x:,.0f}")
            
            st.dataframe(
                df_tramos[['Desde', 'Hasta', 'Tasa', 'Rebaja']], 
                use_container_width=True,
                hide_index=True
            )
    
    with tab4:
        st.markdown("## Retenciones y Otros Impuestos")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Retención Honorarios (11.5%)")
            
            honorarios = st.number_input(
                "Monto Honorarios",
                min_value=0.0,
                value=1000000.0,
                step=10000.0,
                format="%.0f",
                key="honorarios"
            )
            
            # Calculate retention (11.5% in Chile)
            retencion = honorarios * 0.115
            liquido = honorarios - retencion
            
            st.metric("Retención", f"${retencion:,.0f} CLP")
            st.success(f"**Líquido a Pagar: ${liquido:,.0f} CLP**")
        
        with col2:
            st.markdown("### Impuesto de Timbres (0.8%)")
            
            credito = st.number_input(
                "Monto del Crédito",
                min_value=0.0,
                value=50000000.0,
                step=1000000.0,
                format="%.0f",
                key="credito"
            )
            
            meses = st.number_input(
                "Plazo (meses)",
                min_value=1,
                value=12,
                step=1,
                key="plazo"
            )
            
            # Calculate stamp tax (0.8% annual, max 1.6%)
            tasa_mensual = 0.0066667  # 0.8% annual / 12 months
            tasa_total = min(tasa_mensual * meses, 0.016)  # Max 1.6%
            timbres = credito * tasa_total
            timbres_mensual = timbres / meses if meses > 0 else 0
            
            st.metric("Impuesto Total", f"${timbres:,.0f} CLP")
            st.info(f"**Por mes: ${timbres_mensual:,.0f} CLP**")
    
    # Summary section
    st.markdown("---")
    st.markdown("## 📊 Resumen de Cálculos")
    
    if 'neto_iva' in st.session_state and st.session_state.neto_iva > 0:
        summary_data = []
        
        # Add IVA calculation if exists
        if st.session_state.get('neto_iva', 0) > 0:
            summary_data.append({
                'Tipo': 'IVA',
                'Base': f"${st.session_state.neto_iva:,.0f}",
                'Tasa': '19%',
                'Impuesto': f"${st.session_state.neto_iva * 0.19:,.0f}"
            })
        
        # Add corporate tax if exists
        if st.session_state.get('utilidad', 0) > 0:
            base = st.session_state.utilidad - st.session_state.get('gastos', 0)
            summary_data.append({
                'Tipo': 'Primera Categoría',
                'Base': f"${base:,.0f}",
                'Tasa': '27%',
                'Impuesto': f"${base * 0.27:,.0f}"
            })
        
        if summary_data:
            df_summary = pd.DataFrame(summary_data)
            st.dataframe(df_summary, use_container_width=True, hide_index=True)
            
            # Export button
            csv = df_summary.to_csv(index=False)
            st.download_button(
                label="📥 Exportar Resumen CSV",
                data=csv,
                file_name=f"resumen_impuestos_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

if __name__ == "__main__":
    show_tax_calculator()
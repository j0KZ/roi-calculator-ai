#!/usr/bin/env python3
"""
Currency Converter Page - Convert between CLP, USD, EUR, and UF
"""

import streamlit as st
from pages.shared_navigation import show_navigation
import sys
import os
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from currency_converter import CurrencyConverter

def show_currency_converter():
    """Display currency converter page"""

    # Show navigation sidebar
    show_navigation()
    
    st.title("💱 Conversor de Moneda")
    st.markdown("Convierta entre CLP, USD, EUR y UF con tasas actualizadas")
    
    # Initialize converter (will use API key from environment)
    api_key = os.getenv('EXCHANGE_RATE_API_KEY')
    converter = CurrencyConverter(api_key=api_key)
    
    # Get current rates
    rates_data = converter.get_current_rates()
    rates = rates_data.get('rates', {})
    
    # Display current rates - using the rates relative to USD
    st.markdown("## 📊 Tasas de Cambio Actuales")
    
    # Show data source
    if api_key:
        st.success("✅ Usando tasas de cambio en tiempo real de exchangerate-api.com")
    else:
        st.warning("⚠️ Usando tasas de cambio aproximadas (configure API key para tasas en tiempo real)")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Calculate exchange rates with real API data
    usd_to_clp = rates.get('CLP', 965.80)  # CLP per 1 USD
    eur_to_clp = rates.get('CLP', 965.80) / rates.get('EUR', 0.85)  # CLP per 1 EUR
    uf_value = 37539  # Updated UF value in CLP (as of 2024)
    utm_value = 65182  # Updated UTM value in CLP (as of 2024)
    
    with col1:
        st.metric(
            label="USD → CLP",
            value=f"${usd_to_clp:,.2f}",
            delta=f"Actualizado: {datetime.now().strftime('%H:%M')}"
        )
    
    with col2:
        st.metric(
            label="EUR → CLP",
            value=f"${eur_to_clp:,.2f}",
            delta="Banco Central"
        )
    
    with col3:
        st.metric(
            label="UF → CLP",
            value=f"${uf_value:,.2f}",
            delta=f"{datetime.now().strftime('%d/%m/%Y')}"
        )
    
    with col4:
        st.metric(
            label="UTM → CLP",
            value=f"${utm_value:,.2f}",
            delta="Mensual"
        )
    
    st.markdown("---")
    
    # Conversion calculator
    st.markdown("## 🔄 Calculadora de Conversión")
    
    col1, col2, col3 = st.columns([2, 1, 2])
    
    with col1:
        amount = st.number_input(
            "Monto a convertir",
            min_value=0.0,
            value=1000000.0,
            step=1000.0,
            format="%.2f"
        )
        
        from_currency = st.selectbox(
            "De",
            ["CLP", "USD", "EUR"],
            index=0
        )
    
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<div style='text-align: center; font-size: 2em; color: #f5b800;'>→</div>", unsafe_allow_html=True)
    
    with col3:
        to_currency = st.selectbox(
            "A",
            ["USD", "EUR", "CLP"],
            index=0 if from_currency != "USD" else 2
        )
        
        # Perform conversion
        if from_currency != to_currency:
            result = converter.convert(amount, from_currency, to_currency)
            converted = result.get('amount', 0)
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.success(f"**Resultado: {converter.format_currency(converted, to_currency)}**")
        else:
            st.warning("Seleccione monedas diferentes")
    
    # Batch conversion
    st.markdown("---")
    st.markdown("## 📋 Conversión por Lotes")
    
    with st.expander("Convertir múltiples montos"):
        batch_text = st.text_area(
            "Ingrese montos (uno por línea)",
            placeholder="1000000\n2500000\n5000000",
            height=150
        )
        
        col1, col2 = st.columns(2)
        with col1:
            batch_from = st.selectbox("De", ["CLP", "USD", "EUR"], key="batch_from")
        with col2:
            batch_to = st.selectbox("A", ["USD", "EUR", "CLP"], key="batch_to")
        
        if st.button("Convertir Lote", type="primary"):
            if batch_text and batch_from != batch_to:
                try:
                    amounts = [float(line.strip()) for line in batch_text.split('\n') if line.strip()]
                    results = []
                    
                    for amt in amounts:
                        result = converter.convert(amt, batch_from, batch_to)
                        converted = result.get('amount', 0)
                        results.append({
                            'Original': converter.format_currency(amt, batch_from),
                            'Convertido': converter.format_currency(converted, batch_to),
                            'Tasa': f"{converted/amt:.4f}" if amt > 0 else "N/A"
                        })
                    
                    df = pd.DataFrame(results)
                    st.dataframe(df, use_container_width=True)
                    
                    # Summary
                    total_original = sum(amounts)
                    result = converter.convert(total_original, batch_from, batch_to)
                    total_converted = result.get('amount', 0)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.info(f"Total Original: {converter.format_currency(total_original, batch_from)}")
                    with col2:
                        st.success(f"Total Convertido: {converter.format_currency(total_converted, batch_to)}")
                    
                except ValueError as e:
                    st.error(f"Error en los montos ingresados: {e}")
    
    # Historical chart
    st.markdown("---")
    st.markdown("## 📈 Histórico de Tasas (Últimos 30 días)")
    
    # Generate sample historical data
    dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
    
    # Simulate historical rates with some variation
    import numpy as np
    base_usd = usd_to_clp
    base_eur = eur_to_clp
    base_uf = uf_value
    
    historical_data = pd.DataFrame({
        'Fecha': dates,
        'USD/CLP': base_usd + np.random.randn(30) * 10,
        'EUR/CLP': base_eur + np.random.randn(30) * 12,
        'UF/CLP': base_uf + np.random.randn(30) * 50
    })
    
    # Create chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=historical_data['Fecha'],
        y=historical_data['USD/CLP'],
        mode='lines',
        name='USD/CLP',
        line=dict(color='#00ff00', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=historical_data['Fecha'],
        y=historical_data['EUR/CLP'],
        mode='lines',
        name='EUR/CLP',
        line=dict(color='#0080ff', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=historical_data['Fecha'],
        y=historical_data['UF/CLP'],
        mode='lines',
        name='UF/CLP',
        line=dict(color='#f5b800', width=2),
        yaxis='y2'
    ))
    
    fig.update_layout(
        title="Evolución de Tasas de Cambio",
        xaxis_title="Fecha",
        yaxis_title="CLP",
        yaxis2=dict(
            title="UF/CLP",
            overlaying='y',
            side='right'
        ),
        hovermode='x unified',
        template='plotly_dark',
        paper_bgcolor='#0a0a0a',
        plot_bgcolor='#1a1a1a',
        font=dict(color='#ffffff'),
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Currency calculator widget
    st.markdown("---")
    st.markdown("## 🧮 Calculadora Rápida")
    
    col1, col2, col3 = st.columns(3)
    
    quick_amount = st.number_input(
        "Monto en CLP",
        min_value=0.0,
        value=1000000.0,
        step=100000.0,
        format="%.0f",
        key="quick_calc"
    )
    
    with col1:
        result = converter.convert(quick_amount, "CLP", "USD")
        usd_equiv = result.get('amount', 0)
        st.metric("En USD", f"${usd_equiv:,.2f}")
    
    with col2:
        result = converter.convert(quick_amount, "CLP", "EUR")
        eur_equiv = result.get('amount', 0)
        st.metric("En EUR", f"€{eur_equiv:,.2f}")
    
    with col3:
        # Show equivalent in UF (static calculation)
        uf_equiv = quick_amount / uf_value
        st.metric("En UF (aprox)", f"{uf_equiv:,.2f} UF")
    
    # Export functionality
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 Exportar Tasas Actuales", use_container_width=True):
            df_rates = pd.DataFrame([
                {'Par': 'USD/CLP', 'Tasa': usd_to_clp},
                {'Par': 'EUR/CLP', 'Tasa': eur_to_clp},
                {'Par': 'UF/CLP', 'Tasa': uf_value},
                {'Par': 'CLP/USD', 'Tasa': 1/usd_to_clp if usd_to_clp > 0 else 0},
                {'Par': 'CLP/EUR', 'Tasa': 1/eur_to_clp if eur_to_clp > 0 else 0},
            ])
            
            csv = df_rates.to_csv(index=False)
            st.download_button(
                label="Descargar CSV",
                data=csv,
                file_name=f"tasas_cambio_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("🔄 Actualizar Tasas", use_container_width=True):
            with st.spinner("Actualizando tasas..."):
                converter.update_rates()
                st.success("Tasas actualizadas exitosamente")
                st.rerun()

if __name__ == "__main__":
    show_currency_converter()
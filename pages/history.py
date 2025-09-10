"""
History Page - View and manage saved ROI calculations
"""

import streamlit as st
from pages.shared_navigation import show_navigation
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import json
import sys

# Add parent directory to path
sys.path.insert(0, 'src')
sys.path.insert(0, 'utils')

# Import database connection
try:
    from database.connection import get_session
    from database.models import Calculation
    db_available = True
except ImportError:
    db_available = False
    st.error("❌ Database not available")

# Import chart theme
try:
    from chart_theme import apply_dark_theme, get_dark_color_sequence
except ImportError:
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

def format_date(date_obj):
    """Format datetime for display"""
    if date_obj:
        return date_obj.strftime("%d/%m/%Y %H:%M")
    return ""

def load_calculations():
    """Load all saved calculations from database"""
    if not db_available:
        return []
    
    try:
        session = get_session()
        calculations = session.query(Calculation).order_by(Calculation.created_at.desc()).all()
        
        # Extract data while session is open
        calc_data = []
        for calc in calculations:
            calc_data.append({
                'id': calc.id,
                'company_name': calc.company_name,
                'annual_revenue': calc.annual_revenue,
                'monthly_orders': calc.monthly_orders,
                'avg_order_value': calc.avg_order_value,
                'labor_costs': calc.labor_costs,
                'shipping_costs': calc.shipping_costs,
                'error_costs': calc.error_costs,
                'inventory_costs': calc.inventory_costs,
                'service_investment': calc.service_investment,
                'results': calc.results,
                'created_at': calc.created_at,
                'updated_at': calc.updated_at,
                'notes': calc.notes,
                'tags': calc.tags,
                'get_roi': calc.get_roi() if hasattr(calc, 'get_roi') else (calc.results.get('roi_percentage', 0) if calc.results else 0),
                'get_payback': calc.get_payback() if hasattr(calc, 'get_payback') else (calc.results.get('payback_months', 0) if calc.results else 0)
            })
        
        session.close()
        return calc_data
    except Exception as e:
        st.error(f"Error loading calculations: {e}")
        return []

def delete_calculation(calc_id):
    """Delete a calculation from database"""
    try:
        session = get_session()
        calc = session.query(Calculation).filter_by(id=calc_id).first()
        if calc:
            session.delete(calc)
            session.commit()
            st.success(f"✅ Cálculo #{calc_id} eliminado")
            st.rerun()
        session.close()
    except Exception as e:
        st.error(f"Error deleting calculation: {e}")

def load_calculation_to_session(calc_id):
    """Load a calculation into session state"""
    try:
        session = get_session()
        calc = session.query(Calculation).filter_by(id=calc_id).first()
        
        if calc:
            # Extract data while session is open
            calc_data = {
                'company_name': calc.company_name or '',
                'annual_revenue': calc.annual_revenue,
                'monthly_orders': calc.monthly_orders,
                'avg_order_value': calc.avg_order_value,
                'labor_costs': calc.labor_costs,
                'shipping_costs': calc.shipping_costs,
                'error_costs': calc.error_costs,
                'inventory_costs': calc.inventory_costs,
                'service_investment': calc.service_investment,
                'results': calc.results
            }
            
            session.close()
            
            # Update session state with loaded data
            st.session_state.client_data = {
                'company_name': calc_data['company_name'],
                'annual_revenue_clp': calc_data['annual_revenue'],
                'monthly_orders': calc_data['monthly_orders'],
                'avg_order_value_clp': calc_data['avg_order_value'],
                'labor_costs_clp': calc_data['labor_costs'],
                'shipping_costs_clp': calc_data['shipping_costs'],
                'error_costs_clp': calc_data['error_costs'],
                'inventory_costs_clp': calc_data['inventory_costs'],
                'investment_clp': calc_data['service_investment']
            }
            
            # Store results
            if calc_data['results']:
                st.session_state.roi_results = calc_data['results']
            
            st.success(f"✅ Cálculo #{calc_id} cargado exitosamente")
            
            # Switch to ROI calculator page
            st.switch_page("pages/roi_calculator.py")
        else:
            session.close()
            st.error(f"Cálculo #{calc_id} no encontrado")
            
    except Exception as e:
        st.error(f"Error loading calculation: {e}")

def create_comparison_chart(calculations):
    """Create comparison chart for multiple calculations"""
    if not calculations:
        return None
    
    # Prepare data
    data = []
    for calc in calculations[:10]:  # Limit to last 10
        # Handle both dict and object
        if isinstance(calc, dict):
            roi = calc.get('get_roi', 0)
            company = calc.get('company_name') or f"Calc #{calc.get('id', 0)}"
            investment = calc.get('service_investment', 0)
            date = calc.get('created_at')
        else:
            roi = calc.get_roi() if hasattr(calc, 'get_roi') else 0
            company = calc.company_name or f"Calc #{calc.id}"
            investment = calc.service_investment
            date = calc.created_at
        
        data.append({
            'Company': company,
            'ROI': roi,
            'Investment': investment,
            'Date': date
        })
    
    df = pd.DataFrame(data)
    
    # Create bar chart
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df['Company'],
        y=df['ROI'],
        marker_color=get_dark_color_sequence()[0],
        text=[f"{roi:.0f}%" for roi in df['ROI']],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>ROI: %{y:.1f}%<extra></extra>'
    ))
    
    fig.update_layout(
        title="Comparación de ROI - Últimos 10 Cálculos",
        xaxis_title="Empresa",
        yaxis_title="ROI (%)",
        height=400
    )
    
    return apply_dark_theme(fig)

def display_calculation_card(calc):
    """Display a calculation as a card"""
    with st.container():
        col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 1, 1])
        
        # Handle both dict and object
        if isinstance(calc, dict):
            calc_id = calc['id']
            company_name = calc.get('company_name', 'Sin nombre')
            created_at = calc.get('created_at')
            roi = calc.get('get_roi', 0)
            investment = calc.get('service_investment', 0)
        else:
            calc_id = calc.id
            company_name = calc.company_name or 'Sin nombre'
            created_at = calc.created_at
            roi = calc.get_roi() if hasattr(calc, 'get_roi') else 0
            investment = calc.service_investment
        
        with col1:
            st.markdown(f"**{company_name}**")
            st.caption(f"ID: #{calc_id} | {format_date(created_at)}")
        
        with col2:
            color = "green" if roi > 100 else "orange" if roi > 50 else "red"
            st.metric("ROI", f"{roi:.0f}%", delta=None, delta_color="normal")
        
        with col3:
            st.metric("Inversión", format_clp(investment))
        
        with col4:
            if st.button("📂 Cargar", key=f"load_{calc_id}", use_container_width=True):
                load_calculation_to_session(calc_id)
        
        with col5:
            if st.button("🗑️", key=f"del_{calc_id}", help="Eliminar"):
                if st.session_state.get(f'confirm_delete_{calc_id}', False):
                    delete_calculation(calc_id)
                else:
                    st.session_state[f'confirm_delete_{calc_id}'] = True
                    st.warning("Presione nuevamente para confirmar")
                    st.rerun()
        
        st.divider()

def show_calculation_details(calc):
    """Show detailed view of a calculation"""

    # Show navigation sidebar
    show_navigation()
    # Handle both dict and object
    if isinstance(calc, dict):
        company_name = calc.get('company_name', 'Sin nombre')
        annual_revenue = calc.get('annual_revenue', 0)
        monthly_orders = calc.get('monthly_orders', 0)
        avg_order_value = calc.get('avg_order_value', 0)
        labor_costs = calc.get('labor_costs', 0)
        shipping_costs = calc.get('shipping_costs', 0)
        error_costs = calc.get('error_costs', 0)
        inventory_costs = calc.get('inventory_costs', 0)
        results = calc.get('results')
    else:
        company_name = calc.company_name or 'Sin nombre'
        annual_revenue = calc.annual_revenue
        monthly_orders = calc.monthly_orders
        avg_order_value = calc.avg_order_value
        labor_costs = calc.labor_costs
        shipping_costs = calc.shipping_costs
        error_costs = calc.error_costs
        inventory_costs = calc.inventory_costs
        results = calc.results
    
    st.subheader(f"📊 Detalles - {company_name}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Información de la Empresa**")
        st.write(f"• Ingresos Anuales: {format_clp(annual_revenue)}")
        st.write(f"• Órdenes Mensuales: {monthly_orders:,}")
        st.write(f"• Valor Promedio: {format_clp(avg_order_value)}")
    
    with col2:
        st.markdown("**Costos Operacionales**")
        st.write(f"• Costos Laborales: {format_clp(labor_costs)}")
        st.write(f"• Costos de Envío: {format_clp(shipping_costs)}")
        st.write(f"• Costos de Errores: {format_clp(error_costs)}")
        st.write(f"• Costos de Inventario: {format_clp(inventory_costs)}")
    
    if results:
        st.markdown("**Resultados del Cálculo**")
        results_dict = results if isinstance(results, dict) else json.loads(results)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("ROI", f"{results_dict.get('roi_percentage', 0):.0f}%")
        with col2:
            st.metric("Periodo de Recuperación", f"{results_dict.get('payback_months', 0):.1f} meses")
        with col3:
            st.metric("Ahorros Anuales", format_clp(results_dict.get('total_annual_savings', 0)))

def main():
    # Show navigation sidebar
    show_navigation()
    
    st.title("📚 Historial de Cálculos ROI")
    st.markdown("Gestione todos sus cálculos guardados")
    
    # Add refresh button
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        if st.button("🔄 Actualizar", use_container_width=True):
            st.rerun()
    
    with col2:
        if st.button("🏠 Volver", use_container_width=True):
            st.switch_page("pages/roi_calculator.py")
    
    # Load calculations
    calculations = load_calculations()
    
    if not calculations:
        st.info("📭 No hay cálculos guardados todavía")
        st.markdown("Vaya a la [Calculadora ROI](roi_calculator) para crear su primer cálculo")
        return
    
    # Display summary stats
    st.markdown("### 📊 Resumen")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Cálculos", len(calculations))
    
    with col2:
        # Handle both dict and object for ROI calculation
        roi_values = []
        for c in calculations:
            if isinstance(c, dict):
                roi_values.append(c.get('get_roi', 0))
            else:
                roi_values.append(c.get_roi() if hasattr(c, 'get_roi') else 0)
        avg_roi = sum(roi_values) / len(roi_values) if roi_values else 0
        st.metric("ROI Promedio", f"{avg_roi:.0f}%")
    
    with col3:
        # Handle both dict and object for investment
        total_investment = 0
        for c in calculations:
            if isinstance(c, dict):
                total_investment += c.get('service_investment', 0)
            else:
                total_investment += c.service_investment
        st.metric("Inversión Total", format_clp(total_investment))
    
    with col4:
        latest = calculations[0] if calculations else None
        if latest:
            if isinstance(latest, dict):
                st.metric("Último Cálculo", format_date(latest.get('created_at')))
            else:
                st.metric("Último Cálculo", format_date(latest.created_at))
    
    # Display comparison chart
    if len(calculations) > 1:
        st.markdown("### 📈 Comparación de ROI")
        chart = create_comparison_chart(calculations)
        if chart:
            st.plotly_chart(chart, use_container_width=True)
    
    # Display calculations list
    st.markdown("### 📋 Lista de Cálculos")
    
    # Add search/filter
    search_term = st.text_input("🔍 Buscar por nombre de empresa", "")
    
    # Filter calculations
    filtered_calcs = calculations
    if search_term:
        filtered_calcs = []
        for c in calculations:
            if isinstance(c, dict):
                company_name = c.get('company_name', '')
            else:
                company_name = c.company_name or ''
            if search_term.lower() in company_name.lower():
                filtered_calcs.append(c)
    
    # Display mode selector
    view_mode = st.radio("Vista", ["Lista", "Detallada"], horizontal=True)
    
    if view_mode == "Lista":
        # Display as cards
        for calc in filtered_calcs:
            display_calculation_card(calc)
    else:
        # Display detailed view
        # Get IDs from filtered calcs
        calc_ids = []
        for c in filtered_calcs:
            if isinstance(c, dict):
                calc_ids.append(c['id'])
            else:
                calc_ids.append(c.id)
        
        # Format function for selectbox
        def format_calc_option(calc_id):
            for c in filtered_calcs:
                if isinstance(c, dict):
                    if c['id'] == calc_id:
                        return f"#{calc_id} - {c.get('company_name', 'Sin nombre')}"
                else:
                    if c.id == calc_id:
                        return f"#{calc_id} - {c.company_name or 'Sin nombre'}"
            return f"#{calc_id}"
        
        selected_id = st.selectbox(
            "Seleccione un cálculo",
            options=calc_ids,
            format_func=format_calc_option
        )
        
        if selected_id:
            selected_calc = None
            for c in filtered_calcs:
                if isinstance(c, dict):
                    if c['id'] == selected_id:
                        selected_calc = c
                        break
                else:
                    if c.id == selected_id:
                        selected_calc = c
                        break
            
            if selected_calc:
                show_calculation_details(selected_calc)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("📂 Cargar este cálculo", type="primary", use_container_width=True):
                        load_calculation_to_session(selected_id)
                with col2:
                    if st.button("🗑️ Eliminar este cálculo", type="secondary", use_container_width=True):
                        delete_calculation(selected_id)
    
    # Export options
    if calculations:
        st.divider()
        st.markdown("### 📤 Exportar Datos")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Export as CSV
            export_data = []
            for c in calculations:
                if isinstance(c, dict):
                    export_data.append({
                        'ID': c.get('id', 0),
                        'Empresa': c.get('company_name', 'Sin nombre'),
                        'ROI (%)': c.get('get_roi', 0),
                        'Inversión': c.get('service_investment', 0),
                        'Fecha': c.get('created_at', '')
                    })
                else:
                    export_data.append({
                        'ID': c.id,
                        'Empresa': c.company_name or 'Sin nombre',
                        'ROI (%)': c.get_roi() if hasattr(c, 'get_roi') else 0,
                        'Inversión': c.service_investment,
                        'Fecha': c.created_at
                    })
            
            df_export = pd.DataFrame(export_data)
            
            csv = df_export.to_csv(index=False)
            st.download_button(
                label="📥 Descargar CSV",
                data=csv,
                file_name=f"roi_history_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            # Export as JSON
            json_data = []
            for c in calculations:
                if isinstance(c, dict):
                    created_at = c.get('created_at')
                    json_data.append({
                        'id': c.get('id', 0),
                        'company': c.get('company_name', 'Sin nombre'),
                        'roi': c.get('get_roi', 0),
                        'investment': c.get('service_investment', 0),
                        'date': created_at.isoformat() if created_at else None,
                        'results': c.get('results', {})
                    })
                else:
                    json_data.append({
                        'id': c.id,
                        'company': c.company_name or 'Sin nombre',
                        'roi': c.get_roi() if hasattr(c, 'get_roi') else 0,
                        'investment': c.service_investment,
                        'date': c.created_at.isoformat() if c.created_at else None,
                        'results': c.results
                    })
            
            json_str = json.dumps(json_data, indent=2, ensure_ascii=False)
            st.download_button(
                label="📥 Descargar JSON",
                data=json_str,
                file_name=f"roi_history_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json",
                use_container_width=True
            )

if __name__ == "__main__":
    main()
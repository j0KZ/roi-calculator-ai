"""
Template Management Page - Create and manage calculation templates
"""

import streamlit as st
from pages.shared_navigation import show_navigation
import pandas as pd
import json
import sys
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, 'src')

# Import database connection
try:
    from database.connection import get_session
    from database.models import Template, Calculation
    db_available = True
except ImportError:
    db_available = False
    st.error("❌ Database not available")

def format_clp(amount):
    """Format amount as Chilean Pesos"""
    return f"${amount:,.0f} CLP"

def load_templates():
    """Load all templates from database"""
    if not db_available:
        return []
    
    try:
        session = get_session()
        templates = session.query(Template).order_by(Template.usage_count.desc()).all()
        
        # Extract data from templates while session is still open
        template_data = []
        for template in templates:
            template_data.append({
                'id': template.id,
                'name': template.name,
                'description': template.description,
                'category': template.category,
                'template_data': template.template_data,
                'industry': template.industry,
                'business_size': template.business_size,
                'usage_count': template.usage_count,
                'created_by': template.created_by,
                'tags': template.tags,
                'is_public': template.is_public
            })
        
        session.close()
        return template_data
    except Exception as e:
        st.error(f"Error loading templates: {e}")
        return []

def create_template(name, description, category, template_data):
    """Create a new template"""
    try:
        session = get_session()
        
        template = Template(
            name=name,
            description=description,
            category=category,
            template_data=template_data,
            industry=template_data.get('industry', 'general'),
            business_size=template_data.get('business_size', 'medium'),
            is_public=1,
            created_by='user',
            tags=f"{category},{template_data.get('industry', 'general')}"
        )
        
        session.add(template)
        session.commit()
        
        st.success(f"✅ Plantilla '{name}' creada exitosamente")
        
        session.close()
        return True
        
    except Exception as e:
        st.error(f"Error creating template: {e}")
        return False

def update_template_usage(template_id):
    """Increment template usage count"""
    try:
        session = get_session()
        template = session.query(Template).filter_by(id=template_id).first()
        if template:
            template.usage_count += 1
            session.commit()
        session.close()
    except Exception as e:
        print(f"Error updating usage count: {e}")

def apply_template(template_id):
    """Apply a template to the ROI calculator"""
    try:
        session = get_session()
        template = session.query(Template).filter_by(id=template_id).first()
        
        if template:
            # Extract data while session is open
            template_name = template.name
            template_data = template.template_data if isinstance(template.template_data, dict) else json.loads(template.template_data)
            
            # Close session before updating state
            session.close()
            
            # Update session state with template data
            st.session_state.client_data = {
                'company_name': template_data.get('company_name', ''),
                'annual_revenue_clp': template_data.get('annual_revenue', 0),
                'monthly_orders': template_data.get('monthly_orders', 0),
                'avg_order_value_clp': template_data.get('avg_order_value', 0),
                'labor_costs_clp': template_data.get('labor_costs', 0),
                'shipping_costs_clp': template_data.get('shipping_costs', 0),
                'error_costs_clp': template_data.get('error_costs', 0),
                'inventory_costs_clp': template_data.get('inventory_costs', 0),
                'investment_clp': template_data.get('service_investment', 0),
                'industry': template_data.get('industry', 'general')
            }
            
            # Update usage count
            update_template_usage(template_id)
            
            st.success(f"✅ Plantilla '{template_name}' aplicada")
            
            # Switch to ROI calculator
            st.switch_page("pages/roi_calculator.py")
        else:
            session.close()
            st.error("Template not found")
        
    except Exception as e:
        st.error(f"Error applying template: {e}")

def delete_template(template_id):
    """Delete a template"""
    try:
        session = get_session()
        template = session.query(Template).filter_by(id=template_id).first()
        if template:
            session.delete(template)
            session.commit()
            st.success(f"✅ Plantilla eliminada")
            st.rerun()
        session.close()
    except Exception as e:
        st.error(f"Error deleting template: {e}")

def display_template_card(template):
    """Display a template as a card"""
    with st.container():
        col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
        
        # Handle both dict and object templates
        if isinstance(template, dict):
            template_id = template['id']
            template_name = template['name']
            template_desc = template.get('description', '')
            template_category = template.get('category', '')
            template_industry = template.get('industry', '')
            template_size = template.get('business_size', '')
            template_usage = template.get('usage_count', 0)
            template_creator = template.get('created_by', '')
        else:
            template_id = template.id
            template_name = template.name
            template_desc = template.description
            template_category = template.category
            template_industry = template.industry
            template_size = template.business_size
            template_usage = template.usage_count
            template_creator = template.created_by
        
        with col1:
            st.markdown(f"**{template_name}**")
            st.caption(template_desc or "Sin descripción")
            
            # Show tags
            tags = []
            if template_category:
                tags.append(f"📁 {template_category}")
            if template_industry:
                tags.append(f"🏢 {template_industry}")
            if template_size:
                tags.append(f"📏 {template_size}")
            
            if tags:
                st.caption(" | ".join(tags))
        
        with col2:
            st.metric("Usos", template_usage)
        
        with col3:
            if st.button("📂 Usar", key=f"use_{template_id}", use_container_width=True):
                apply_template(template_id)
        
        with col4:
            if template_creator == 'user':
                if st.button("🗑️", key=f"del_{template_id}", help="Eliminar"):
                    delete_template(template_id)
        
        st.divider()

def create_default_templates():
    """Create default templates if none exist"""
    templates = [
        {
            "name": "Pequeña Empresa - Retail",
            "description": "Empresa retail con $500M CLP de ingresos anuales",
            "category": "small_business",
            "data": {
                "company_name": "Pequeña Empresa Retail",
                "annual_revenue": 500000000,
                "monthly_orders": 1000,
                "avg_order_value": 41667,
                "labor_costs": 4000000,
                "shipping_costs": 2500000,
                "error_costs": 1000000,
                "inventory_costs": 1500000,
                "service_investment": 25000000,
                "industry": "retail",
                "business_size": "small"
            }
        },
        {
            "name": "Mediana Empresa - E-commerce",
            "description": "E-commerce con $2.000M CLP de ingresos anuales",
            "category": "medium_business",
            "data": {
                "company_name": "Mediana Empresa E-commerce",
                "annual_revenue": 2000000000,
                "monthly_orders": 5000,
                "avg_order_value": 33333,
                "labor_costs": 8000000,
                "shipping_costs": 5000000,
                "error_costs": 2000000,
                "inventory_costs": 3000000,
                "service_investment": 50000000,
                "industry": "ecommerce",
                "business_size": "medium"
            }
        },
        {
            "name": "Gran Empresa - Distribución",
            "description": "Empresa de distribución con $5.000M CLP de ingresos",
            "category": "large_business",
            "data": {
                "company_name": "Gran Empresa Distribución",
                "annual_revenue": 5000000000,
                "monthly_orders": 10000,
                "avg_order_value": 41667,
                "labor_costs": 15000000,
                "shipping_costs": 10000000,
                "error_costs": 5000000,
                "inventory_costs": 7500000,
                "service_investment": 100000000,
                "industry": "distribution",
                "business_size": "large"
            }
        },
        {
            "name": "Startup - Tecnología",
            "description": "Startup tecnológica con $100M CLP de ingresos",
            "category": "startup",
            "data": {
                "company_name": "Startup Tech",
                "annual_revenue": 100000000,
                "monthly_orders": 200,
                "avg_order_value": 41667,
                "labor_costs": 1500000,
                "shipping_costs": 500000,
                "error_costs": 300000,
                "inventory_costs": 200000,
                "service_investment": 10000000,
                "industry": "technology",
                "business_size": "startup"
            }
        }
    ]
    
    for template_info in templates:
        create_template(
            template_info["name"],
            template_info["description"],
            template_info["category"],
            template_info["data"]
        )

def main():
    # Show navigation sidebar
    show_navigation()
    
    st.title("📋 Gestión de Plantillas")
    st.markdown("Cree y gestione plantillas para cálculos rápidos")
    
    # Navigation
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        if st.button("🔄 Actualizar", use_container_width=True):
            st.rerun()
    
    with col2:
        if st.button("🏠 Volver", use_container_width=True):
            st.switch_page("pages/roi_calculator.py")
    
    # Load templates
    templates = load_templates()
    
    # Create default templates if none exist
    if not templates:
        if st.button("🎯 Crear Plantillas Predeterminadas", type="primary"):
            create_default_templates()
            st.rerun()
    
    # Tabs for different sections
    tab1, tab2, tab3 = st.tabs(["📚 Plantillas Disponibles", "➕ Nueva Plantilla", "📊 Estadísticas"])
    
    with tab1:
        if not templates:
            st.info("📭 No hay plantillas disponibles")
            st.markdown("Cree su primera plantilla en la pestaña **Nueva Plantilla**")
        else:
            # Filter options
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Get categories from dict templates
                categories = set()
                for t in templates:
                    cat = t.get('category') if isinstance(t, dict) else t.category
                    if cat:
                        categories.add(cat)
                category_filter = st.selectbox(
                    "Categoría",
                    ["Todas"] + sorted(list(categories))
                )
            
            with col2:
                # Get industries from dict templates
                industries = set()
                for t in templates:
                    ind = t.get('industry') if isinstance(t, dict) else t.industry
                    if ind:
                        industries.add(ind)
                industry_filter = st.selectbox(
                    "Industria",
                    ["Todas"] + sorted(list(industries))
                )
            
            with col3:
                # Get sizes from dict templates
                sizes = set()
                for t in templates:
                    size = t.get('business_size') if isinstance(t, dict) else t.business_size
                    if size:
                        sizes.add(size)
                size_filter = st.selectbox(
                    "Tamaño",
                    ["Todos"] + sorted(list(sizes))
                )
            
            # Filter templates
            filtered_templates = templates
            if category_filter != "Todas":
                filtered_templates = []
                for t in templates:
                    cat = t.get('category') if isinstance(t, dict) else t.category
                    if cat == category_filter:
                        filtered_templates.append(t)
            if industry_filter != "Todas":
                temp_filtered = []
                for t in filtered_templates:
                    ind = t.get('industry') if isinstance(t, dict) else t.industry
                    if ind == industry_filter:
                        temp_filtered.append(t)
                filtered_templates = temp_filtered
            if size_filter != "Todos":
                temp_filtered = []
                for t in filtered_templates:
                    size = t.get('business_size') if isinstance(t, dict) else t.business_size
                    if size == size_filter:
                        temp_filtered.append(t)
                filtered_templates = temp_filtered
            
            # Display templates
            st.markdown(f"### {len(filtered_templates)} plantillas encontradas")
            
            for template in filtered_templates:
                display_template_card(template)
    
    with tab2:
        st.markdown("### Crear Nueva Plantilla")
        
        # Template from existing calculation
        st.markdown("#### Desde Cálculo Existente")
        
        if db_available:
            session = get_session()
            calculations = session.query(Calculation).order_by(Calculation.created_at.desc()).limit(10).all()
            
            # Extract calculation data while session is open
            calc_options = []
            for c in calculations:
                calc_options.append((c.id, c.company_name or f"Cálculo #{c.id}"))
            
            session.close()
            
            if calc_options:
                selected_calc = st.selectbox(
                    "Seleccionar cálculo",
                    options=calc_options,
                    format_func=lambda x: x[1]
                )
                
                if selected_calc and st.button("📋 Crear Plantilla desde Cálculo", type="primary"):
                    # Get the calculation
                    session = get_session()
                    calc = session.query(Calculation).filter_by(id=selected_calc[0]).first()
                    
                    if calc:
                        template_data = {
                            'company_name': '',  # Clear company name for template
                            'annual_revenue': calc.annual_revenue,
                            'monthly_orders': calc.monthly_orders,
                            'avg_order_value': calc.avg_order_value,
                            'labor_costs': calc.labor_costs,
                            'shipping_costs': calc.shipping_costs,
                            'error_costs': calc.error_costs,
                            'inventory_costs': calc.inventory_costs,
                            'service_investment': calc.service_investment,
                            'industry': 'general',
                            'business_size': 'medium'
                        }
                        
                        with st.form("template_from_calc"):
                            name = st.text_input("Nombre de la plantilla", f"Plantilla desde {calc.company_name or 'cálculo'}")
                            description = st.text_area("Descripción")
                            category = st.selectbox("Categoría", ["general", "small_business", "medium_business", "large_business", "startup"])
                            
                            if st.form_submit_button("Crear Plantilla"):
                                if name:
                                    create_template(name, description, category, template_data)
                                    st.rerun()
                    
                    session.close()
        
        st.divider()
        
        # Manual template creation
        st.markdown("#### Crear Manualmente")
        
        with st.form("new_template"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Nombre de la plantilla*")
                description = st.text_area("Descripción")
                category = st.selectbox("Categoría", ["general", "small_business", "medium_business", "large_business", "startup"])
            
            with col2:
                industry = st.selectbox("Industria", ["general", "retail", "ecommerce", "wholesale", "services", "manufacturing", "technology", "distribution"])
                business_size = st.selectbox("Tamaño de empresa", ["startup", "small", "medium", "large", "enterprise"])
            
            st.markdown("#### Datos del Template")
            
            col1, col2 = st.columns(2)
            
            with col1:
                annual_revenue = st.number_input("Ingresos Anuales (CLP)", min_value=0, value=1000000000, step=100000000)
                monthly_orders = st.number_input("Órdenes Mensuales", min_value=0, value=1000, step=100)
                avg_order_value = st.number_input("Valor Promedio Orden (CLP)", min_value=0, value=35000, step=1000)
                service_investment = st.number_input("Inversión Servicio (CLP)", min_value=0, value=50000000, step=1000000)
            
            with col2:
                labor_costs = st.number_input("Costos Laborales (CLP)", min_value=0, value=5000000, step=100000)
                shipping_costs = st.number_input("Costos de Envío (CLP)", min_value=0, value=3000000, step=100000)
                error_costs = st.number_input("Costos de Errores (CLP)", min_value=0, value=1500000, step=100000)
                inventory_costs = st.number_input("Costos de Inventario (CLP)", min_value=0, value=2000000, step=100000)
            
            submitted = st.form_submit_button("Crear Plantilla", type="primary")
            
            if submitted:
                if name:
                    template_data = {
                        'annual_revenue': annual_revenue,
                        'monthly_orders': monthly_orders,
                        'avg_order_value': avg_order_value,
                        'labor_costs': labor_costs,
                        'shipping_costs': shipping_costs,
                        'error_costs': error_costs,
                        'inventory_costs': inventory_costs,
                        'service_investment': service_investment,
                        'industry': industry,
                        'business_size': business_size
                    }
                    
                    if create_template(name, description, category, template_data):
                        st.rerun()
                else:
                    st.error("Por favor ingrese un nombre para la plantilla")
    
    with tab3:
        st.markdown("### 📊 Estadísticas de Uso")
        
        if templates:
            # Usage statistics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Plantillas", len(templates))
            
            with col2:
                # Calculate total usage from dict templates
                total_usage = 0
                for t in templates:
                    usage = t.get('usage_count', 0) if isinstance(t, dict) else t.usage_count
                    total_usage += usage
                st.metric("Uso Total", total_usage)
            
            with col3:
                # Find most used template
                if templates:
                    most_used = None
                    max_usage = -1
                    for t in templates:
                        usage = t.get('usage_count', 0) if isinstance(t, dict) else t.usage_count
                        if usage > max_usage:
                            max_usage = usage
                            most_used = t
                    
                    if most_used:
                        name = most_used.get('name', '') if isinstance(most_used, dict) else most_used.name
                        st.metric("Más Usada", name)
                else:
                    st.metric("Más Usada", "N/A")
            
            # Usage chart
            st.markdown("#### Top 10 Plantillas Más Usadas")
            
            # Sort templates by usage
            sorted_templates = sorted(templates, 
                key=lambda t: t.get('usage_count', 0) if isinstance(t, dict) else t.usage_count, 
                reverse=True)[:10]
            
            # Create dataframe
            df_data = []
            for t in sorted_templates:
                if isinstance(t, dict):
                    df_data.append({
                        'Plantilla': t.get('name', ''),
                        'Usos': t.get('usage_count', 0),
                        'Categoría': t.get('category', 'general')
                    })
                else:
                    df_data.append({
                        'Plantilla': t.name,
                        'Usos': t.usage_count,
                        'Categoría': t.category or 'general'
                    })
            
            df = pd.DataFrame(df_data)
            
            if not df.empty:
                st.bar_chart(df.set_index('Plantilla')['Usos'])
            
            # Category distribution
            st.markdown("#### Distribución por Categoría")
            
            category_counts = {}
            for t in templates:
                cat = t.category or 'general'
                category_counts[cat] = category_counts.get(cat, 0) + 1
            
            if category_counts:
                df_cat = pd.DataFrame(list(category_counts.items()), columns=['Categoría', 'Cantidad'])
                st.bar_chart(df_cat.set_index('Categoría'))
        else:
            st.info("No hay estadísticas disponibles todavía")

if __name__ == "__main__":
    main()
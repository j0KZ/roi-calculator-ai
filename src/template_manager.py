"""
Template Manager for ROI Calculator
Handles creation, storage, and management of calculation templates
"""

import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from database.connection import get_session
from database.models import Template


class TemplateManager:
    """Manages calculation templates for easy scenario creation"""
    
    def __init__(self):
        self.predefined_templates = self._load_predefined_templates()
    
    def _load_predefined_templates(self) -> Dict[str, Dict]:
        """Load predefined business templates"""
        return {
            'small_business': {
                'name': 'Small E-commerce Business',
                'description': 'Perfect for startups and small businesses with basic operations',
                'category': 'business_size',
                'tags': ['startup', 'small', 'basic'],
                'industry': 'ecommerce',
                'business_size': 'small',
                'template_data': {
                    'annual_revenue': 500000,
                    'monthly_orders': 1500,
                    'avg_order_value': 27.78,
                    'labor_costs': 3000,
                    'shipping_costs': 2000,
                    'error_costs': 500,
                    'inventory_costs': 1000,
                    'service_investment': 25000
                },
                'metadata': {
                    'created_by': 'system',
                    'version': '1.0',
                    'use_cases': ['New e-commerce business', 'Testing ROI scenarios']
                }
            },
            
            'enterprise': {
                'name': 'Enterprise E-commerce',
                'description': 'Large-scale enterprise operations with complex logistics',
                'category': 'business_size',
                'tags': ['enterprise', 'large', 'complex'],
                'industry': 'ecommerce',
                'business_size': 'enterprise',
                'template_data': {
                    'annual_revenue': 10000000,
                    'monthly_orders': 25000,
                    'avg_order_value': 33.33,
                    'labor_costs': 50000,
                    'shipping_costs': 30000,
                    'error_costs': 15000,
                    'inventory_costs': 25000,
                    'service_investment': 250000
                },
                'metadata': {
                    'created_by': 'system',
                    'version': '1.0',
                    'use_cases': ['Enterprise transformation', 'Large-scale optimization']
                }
            },
            
            'ecommerce_marketplace': {
                'name': 'E-commerce Marketplace',
                'description': 'Multi-vendor marketplace with high transaction volume',
                'category': 'industry',
                'tags': ['marketplace', 'multi-vendor', 'high-volume'],
                'industry': 'ecommerce',
                'business_size': 'medium',
                'template_data': {
                    'annual_revenue': 3000000,
                    'monthly_orders': 8000,
                    'avg_order_value': 31.25,
                    'labor_costs': 12000,
                    'shipping_costs': 8000,
                    'error_costs': 4000,
                    'inventory_costs': 6000,
                    'service_investment': 75000
                },
                'metadata': {
                    'created_by': 'system',
                    'version': '1.0',
                    'use_cases': ['Marketplace optimization', 'Vendor management efficiency']
                }
            },
            
            'manufacturing': {
                'name': 'Manufacturing Operations',
                'description': 'Direct-to-consumer manufacturing with inventory challenges',
                'category': 'industry',
                'tags': ['manufacturing', 'inventory-heavy', 'b2c'],
                'industry': 'manufacturing',
                'business_size': 'medium',
                'template_data': {
                    'annual_revenue': 4000000,
                    'monthly_orders': 3500,
                    'avg_order_value': 95.24,
                    'labor_costs': 18000,
                    'shipping_costs': 12000,
                    'error_costs': 6000,
                    'inventory_costs': 15000,
                    'service_investment': 100000
                },
                'metadata': {
                    'created_by': 'system',
                    'version': '1.0',
                    'use_cases': ['Manufacturing efficiency', 'Supply chain optimization']
                }
            }
        }
    
    def create_template(self, name: str, description: str, template_data: Dict, 
                       category: str = 'custom', tags: List[str] = None,
                       metadata: Dict = None) -> Dict:
        """Create a new custom template"""
        try:
            session = get_session()
            
            # Create template record
            template = Template(
                name=name,
                description=description,
                category=category,
                tags=','.join(tags) if tags else '',
                template_data=template_data,
                meta_data=metadata or {},
                is_public=False,
                created_by='user'
            )
            
            session.add(template)
            session.commit()
            
            result = {
                'id': template.id,
                'name': template.name,
                'description': template.description,
                'category': template.category,
                'template_data': template.template_data,
                'created_at': template.created_at.isoformat(),
                'success': True
            }
            
            session.close()
            return result
            
        except Exception as e:
            if 'session' in locals():
                session.rollback()
                session.close()
            raise Exception(f"Error creating template: {str(e)}")
    
    def get_template(self, template_id: Optional[str] = None, 
                    name: Optional[str] = None) -> Optional[Dict]:
        """Get a specific template by ID or name"""
        try:
            if template_id:
                # Check if it's a predefined template
                if template_id in self.predefined_templates:
                    return self.predefined_templates[template_id]
                
                # Check database
                session = get_session()
                template = session.query(Template).get(template_id)
                
                if template:
                    result = template.to_dict()
                    session.close()
                    return result
                
                session.close()
            
            elif name:
                # Search predefined templates first
                for key, template in self.predefined_templates.items():
                    if template['name'].lower() == name.lower():
                        return template
                
                # Search database
                session = get_session()
                template = session.query(Template).filter(Template.name == name).first()
                
                if template:
                    result = template.to_dict()
                    session.close()
                    return result
                
                session.close()
            
            return None
            
        except Exception as e:
            if 'session' in locals():
                session.close()
            raise Exception(f"Error retrieving template: {str(e)}")
    
    def list_templates(self, category: Optional[str] = None, 
                      include_predefined: bool = True,
                      include_user: bool = True,
                      tags: List[str] = None) -> List[Dict]:
        """List all available templates with filtering"""
        try:
            templates = []
            
            # Add predefined templates
            if include_predefined:
                for key, template in self.predefined_templates.items():
                    # Apply filters
                    if category and template.get('category') != category:
                        continue
                    if tags:
                        template_tags = template.get('tags', [])
                        if not any(tag in template_tags for tag in tags):
                            continue
                    
                    # Add system identifier
                    template_copy = template.copy()
                    template_copy['id'] = key
                    template_copy['source'] = 'system'
                    templates.append(template_copy)
            
            # Add user templates from database
            if include_user:
                session = get_session()
                query = session.query(Template)
                
                if category:
                    query = query.filter(Template.category == category)
                
                db_templates = query.all()
                
                for template in db_templates:
                    template_dict = template.to_dict()
                    
                    # Apply tag filter
                    if tags:
                        template_tags = template_dict.get('tags', '').split(',')
                        if not any(tag in template_tags for tag in tags):
                            continue
                    
                    template_dict['source'] = 'user'
                    templates.append(template_dict)
                
                session.close()
            
            # Sort by creation date (newest first)
            templates.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            
            return templates
            
        except Exception as e:
            if 'session' in locals():
                session.close()
            raise Exception(f"Error listing templates: {str(e)}")
    
    def update_template(self, template_id: str, updates: Dict) -> Dict:
        """Update an existing template"""
        try:
            # Cannot update predefined templates
            if template_id in self.predefined_templates:
                raise Exception("Cannot update predefined system templates")
            
            session = get_session()
            template = session.query(Template).get(template_id)
            
            if not template:
                session.close()
                raise Exception("Template not found")
            
            # Update allowed fields (map metadata to meta_data for database)
            allowed_fields = ['name', 'description', 'category', 'tags', 'template_data']
            for field, value in updates.items():
                if field in allowed_fields:
                    setattr(template, field, value)
                elif field == 'metadata':
                    setattr(template, 'meta_data', value)
            
            template.updated_at = datetime.utcnow()
            session.commit()
            
            result = template.to_dict()
            session.close()
            
            return result
            
        except Exception as e:
            if 'session' in locals():
                session.rollback()
                session.close()
            raise Exception(f"Error updating template: {str(e)}")
    
    def delete_template(self, template_id: str) -> bool:
        """Delete a template"""
        try:
            # Cannot delete predefined templates
            if template_id in self.predefined_templates:
                raise Exception("Cannot delete predefined system templates")
            
            session = get_session()
            template = session.query(Template).get(template_id)
            
            if not template:
                session.close()
                raise Exception("Template not found")
            
            session.delete(template)
            session.commit()
            session.close()
            
            return True
            
        except Exception as e:
            if 'session' in locals():
                session.rollback()
                session.close()
            raise Exception(f"Error deleting template: {str(e)}")
    
    def export_template(self, template_id: str, format: str = 'json') -> Dict:
        """Export a template to various formats"""
        try:
            template = self.get_template(template_id)
            
            if not template:
                raise Exception("Template not found")
            
            if format.lower() == 'json':
                return {
                    'format': 'json',
                    'data': json.dumps(template, indent=2),
                    'filename': f"{template['name'].replace(' ', '_').lower()}_template.json"
                }
            
            else:
                raise Exception(f"Unsupported export format: {format}")
                
        except Exception as e:
            raise Exception(f"Error exporting template: {str(e)}")
    
    def import_template(self, template_data: Dict, source: str = 'import') -> Dict:
        """Import a template from external data"""
        try:
            # Validate required fields
            required_fields = ['name', 'template_data']
            for field in required_fields:
                if field not in template_data:
                    raise Exception(f"Missing required field: {field}")
            
            # Validate template_data structure
            template_inputs = template_data['template_data']
            required_inputs = [
                'annual_revenue', 'monthly_orders', 'avg_order_value',
                'labor_costs', 'shipping_costs', 'error_costs',
                'inventory_costs', 'service_investment'
            ]
            
            for field in required_inputs:
                if field not in template_inputs:
                    raise Exception(f"Missing required input field: {field}")
            
            # Create the template
            result = self.create_template(
                name=template_data['name'],
                description=template_data.get('description', 'Imported template'),
                template_data=template_inputs,
                category=template_data.get('category', 'imported'),
                tags=template_data.get('tags', ['imported']),
                metadata=template_data.get('metadata', {'source': source})
            )
            
            return result
            
        except Exception as e:
            raise Exception(f"Error importing template: {str(e)}")
    
    def clone_template(self, template_id: str, new_name: str) -> Dict:
        """Clone an existing template with a new name"""
        try:
            original = self.get_template(template_id)
            
            if not original:
                raise Exception("Template not found")
            
            # Create new template with cloned data
            result = self.create_template(
                name=new_name,
                description=f"Copy of {original['name']}",
                template_data=original['template_data'].copy(),
                category=original.get('category', 'custom'),
                tags=original.get('tags', []) + ['cloned'],
                metadata=original.get('metadata', {})
            )
            
            return result
            
        except Exception as e:
            raise Exception(f"Error cloning template: {str(e)}")
    
    def get_template_analytics(self, template_id: str) -> Dict:
        """Get usage analytics for a template"""
        try:
            # This would integrate with calculation history to show usage stats
            # For now, return basic information
            template = self.get_template(template_id)
            
            if not template:
                raise Exception("Template not found")
            
            # Basic analytics (would be enhanced with actual usage data)
            analytics = {
                'template_id': template_id,
                'template_name': template['name'],
                'usage_count': 0,  # Would query calculation history
                'last_used': None,  # Would query calculation history
                'avg_roi': None,  # Would calculate from usage history
                'popularity_rank': None,  # Would calculate from all templates
                'created_at': template.get('created_at'),
                'category': template.get('category'),
                'tags': template.get('tags', [])
            }
            
            return analytics
            
        except Exception as e:
            raise Exception(f"Error getting template analytics: {str(e)}")
    
    def validate_template_data(self, template_data: Dict) -> List[str]:
        """Validate template data structure and values"""
        errors = []
        
        # Check required fields
        required_fields = {
            'annual_revenue': 'Annual Revenue',
            'monthly_orders': 'Monthly Orders',
            'avg_order_value': 'Average Order Value',
            'labor_costs': 'Labor Costs',
            'shipping_costs': 'Shipping Costs',
            'error_costs': 'Error Costs',
            'inventory_costs': 'Inventory Costs',
            'service_investment': 'Service Investment'
        }
        
        for field, label in required_fields.items():
            if field not in template_data:
                errors.append(f"Missing required field: {label}")
                continue
            
            try:
                value = float(template_data[field])
                if value < 0:
                    errors.append(f"{label} must be positive")
                elif field == 'annual_revenue' and value < 1000:
                    errors.append(f"{label} seems too low (minimum $1,000)")
                elif field == 'service_investment' and value < 100:
                    errors.append(f"{label} seems too low (minimum $100)")
            except (ValueError, TypeError):
                errors.append(f"{label} must be a valid number")
        
        # Business logic validation
        if not errors:
            try:
                revenue = float(template_data['annual_revenue'])
                orders = float(template_data['monthly_orders'])
                aov = float(template_data['avg_order_value'])
                
                # Check if monthly revenue matches orders * AOV
                expected_monthly_revenue = orders * aov
                actual_monthly_revenue = revenue / 12
                
                if abs(expected_monthly_revenue - actual_monthly_revenue) / actual_monthly_revenue > 0.15:
                    errors.append('Monthly orders × Average order value should approximately equal monthly revenue')
                
            except (ValueError, KeyError):
                pass  # Individual field errors already caught
        
        return errors
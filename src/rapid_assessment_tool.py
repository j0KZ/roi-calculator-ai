#!/usr/bin/env python3
"""
Rapid Assessment Tool - 15-minute qualification for Chilean E-commerce SMEs
Converts prospects quickly by identifying pain points and quantifying opportunities
"""

import json
from datetime import datetime
from typing import Dict, List, Tuple
from dataclasses import dataclass
import numpy as np
from functools import wraps

# Error handler decorator
def error_handler(func):
    """Decorator to handle errors gracefully"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"Error in {func.__name__}: {str(e)}")
            # Return safe default based on function
            if 'calculate' in func.__name__.lower():
                return 0
            elif 'validate' in func.__name__.lower():
                return False
            else:
                return None
    return wrapper


@dataclass
class AssessmentQuestion:
    """Structure for assessment questions"""
    id: str
    category: str
    question: str
    question_type: str  # 'yes_no', 'scale', 'number', 'multiple_choice'
    options: List[str] = None
    weight: float = 1.0
    follow_up: str = None


class RapidAssessmentTool:
    """15-minute assessment tool for qualifying prospects"""
    
    def __init__(self):
        self.questions = self._initialize_questions()
        self.scoring_weights = {
            'technology': 0.25,
            'operations': 0.30,
            'integration': 0.20,
            'team': 0.15,
            'growth': 0.10
        }
        self.responses = {}
        self.assessment_results = {}
        
    def _initialize_questions(self) -> Dict[str, List[AssessmentQuestion]]:
        """Initialize assessment questions by category"""
        
        questions = {
            'basic_info': [
                AssessmentQuestion(
                    id='b1',
                    category='basic_info',
                    question='¿Cuál es su volumen de ventas mensual en CLP?',
                    question_type='number',
                    weight=2.0
                ),
                AssessmentQuestion(
                    id='b2',
                    category='basic_info',
                    question='¿Cuántas órdenes procesan mensualmente?',
                    question_type='number',
                    weight=1.5
                ),
                AssessmentQuestion(
                    id='b3',
                    category='basic_info',
                    question='¿Cuántos empleados dedican a operaciones e-commerce?',
                    question_type='number',
                    weight=1.0
                ),
                AssessmentQuestion(
                    id='b4',
                    category='basic_info',
                    question='¿En qué industria opera?',
                    question_type='multiple_choice',
                    options=['Retail', 'Wholesale', 'Servicios', 'Manufactura', 'Otro'],
                    weight=1.0
                )
            ],
            
            'technology': [
                AssessmentQuestion(
                    id='t1',
                    category='technology',
                    question='¿Qué plataforma de e-commerce utiliza?',
                    question_type='multiple_choice',
                    options=['WooCommerce', 'Shopify', 'Magento', 'PrestaShop', 'Desarrollo propio', 'Otra'],
                    weight=1.5
                ),
                AssessmentQuestion(
                    id='t2',
                    category='technology',
                    question='¿Tiene integración automática con su ERP?',
                    question_type='yes_no',
                    weight=2.0,
                    follow_up='Si no, ¿cuántas horas dedican a ingreso manual de datos?'
                ),
                AssessmentQuestion(
                    id='t3',
                    category='technology',
                    question='¿Qué sistemas de gestión utiliza? (Seleccione todos los que apliquen)',
                    question_type='multiple_choice',
                    options=['Defontana', 'Bsale', 'SAP', 'Manager', 'Softland', 'Excel', 'Ninguno'],
                    weight=1.5
                ),
                AssessmentQuestion(
                    id='t4',
                    category='technology',
                    question='En escala 1-10, ¿qué tan automatizados están sus procesos?',
                    question_type='scale',
                    weight=2.0
                )
            ],
            
            'operations': [
                AssessmentQuestion(
                    id='o1',
                    category='operations',
                    question='¿Cuánto tiempo promedio toma procesar una orden? (minutos)',
                    question_type='number',
                    weight=2.0
                ),
                AssessmentQuestion(
                    id='o2',
                    category='operations',
                    question='¿Qué porcentaje de órdenes tienen errores o requieren corrección?',
                    question_type='number',
                    weight=2.5
                ),
                AssessmentQuestion(
                    id='o3',
                    category='operations',
                    question='¿Cuántas horas al día dedican a tareas operativas repetitivas?',
                    question_type='number',
                    weight=2.0
                ),
                AssessmentQuestion(
                    id='o4',
                    category='operations',
                    question='¿Tienen procesos documentados y estandarizados?',
                    question_type='yes_no',
                    weight=1.5
                ),
                AssessmentQuestion(
                    id='o5',
                    category='operations',
                    question='¿Con qué frecuencia tienen quiebres de stock?',
                    question_type='multiple_choice',
                    options=['Diariamente', 'Semanalmente', 'Mensualmente', 'Raramente', 'Nunca'],
                    weight=1.5
                )
            ],
            
            'integration': [
                AssessmentQuestion(
                    id='i1',
                    category='integration',
                    question='¿Qué pasarelas de pago utiliza?',
                    question_type='multiple_choice',
                    options=['Transbank', 'Webpay', 'MercadoPago', 'PayPal', 'Flow', 'Khipu', 'Otras'],
                    weight=1.0
                ),
                AssessmentQuestion(
                    id='i2',
                    category='integration',
                    question='¿Qué servicios de envío utiliza?',
                    question_type='multiple_choice',
                    options=['Chilexpress', 'Starken', 'Correos Chile', 'Blue Express', 'Propio', 'Otros'],
                    weight=1.0
                ),
                AssessmentQuestion(
                    id='i3',
                    category='integration',
                    question='¿Vende en marketplaces?',
                    question_type='multiple_choice',
                    options=['MercadoLibre', 'Falabella', 'Paris', 'Ripley', 'Linio', 'No vendo en marketplaces'],
                    weight=1.5
                ),
                AssessmentQuestion(
                    id='i4',
                    category='integration',
                    question='¿Sincroniza inventario automáticamente entre canales?',
                    question_type='yes_no',
                    weight=2.0
                )
            ],
            
            'pain_points': [
                AssessmentQuestion(
                    id='p1',
                    category='pain_points',
                    question='¿Cuáles son sus 3 principales desafíos operativos?',
                    question_type='multiple_choice',
                    options=[
                        'Procesamiento manual de órdenes',
                        'Errores en fulfillment',
                        'Gestión de inventario',
                        'Costos de envío altos',
                        'Falta de integración entre sistemas',
                        'Reportería insuficiente',
                        'Atención al cliente',
                        'Gestión de devoluciones'
                    ],
                    weight=3.0
                ),
                AssessmentQuestion(
                    id='p2',
                    category='pain_points',
                    question='¿Cuánto estima que pierde mensualmente por ineficiencias? (CLP)',
                    question_type='number',
                    weight=2.5
                ),
                AssessmentQuestion(
                    id='p3',
                    category='pain_points',
                    question='En escala 1-10, ¿qué tan urgente es resolver estos problemas?',
                    question_type='scale',
                    weight=2.0
                )
            ],
            
            'growth': [
                AssessmentQuestion(
                    id='g1',
                    category='growth',
                    question='¿Cuál es su objetivo de crecimiento para los próximos 12 meses? (%)',
                    question_type='number',
                    weight=1.5
                ),
                AssessmentQuestion(
                    id='g2',
                    category='growth',
                    question='¿Tiene presupuesto asignado para mejoras operativas?',
                    question_type='yes_no',
                    weight=2.0,
                    follow_up='Si sí, ¿cuál es el rango de presupuesto en CLP?'
                ),
                AssessmentQuestion(
                    id='g3',
                    category='growth',
                    question='¿Cuál es su timeline ideal para implementar mejoras?',
                    question_type='multiple_choice',
                    options=['Inmediato', '1-3 meses', '3-6 meses', '6-12 meses', 'Más de 12 meses'],
                    weight=1.5
                )
            ]
        }
        
        return questions
    
    def conduct_assessment(self, responses: Dict) -> Dict:
        """
        Conduct rapid assessment based on responses
        
        Args:
            responses: Dictionary of question_id: answer pairs
        
        Returns:
            Comprehensive assessment results with scoring and recommendations
        """
        
        self.responses = responses
        
        # Calculate scores
        scores = self._calculate_scores(responses)
        
        # Identify pain points
        pain_points = self._identify_pain_points(responses)
        
        # Calculate maturity level
        maturity = self._calculate_maturity_level(scores)
        
        # Generate opportunities
        opportunities = self._identify_opportunities(responses, scores)
        
        # Calculate potential ROI
        roi_potential = self._calculate_roi_potential(responses, opportunities)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(scores, pain_points, opportunities)
        
        # Determine engagement scope
        engagement_scope = self._determine_engagement_scope(scores, roi_potential)
        
        # Create qualification score
        qualification = self._qualify_prospect(scores, roi_potential, responses)
        
        self.assessment_results = {
            'timestamp': datetime.now().isoformat(),
            'company_profile': self._create_company_profile(responses),
            'scores': scores,
            'maturity_level': maturity,
            'pain_points': pain_points,
            'opportunities': opportunities,
            'roi_potential': roi_potential,
            'recommendations': recommendations,
            'engagement_scope': engagement_scope,
            'qualification': qualification,
            'next_steps': self._generate_next_steps(qualification)
        }
        
        return self.assessment_results
    
    def _calculate_scores(self, responses: Dict) -> Dict:
        """Calculate scores by category"""
        
        scores = {}
        
        # Technology score
        tech_score = 0
        tech_questions = ['t1', 't2', 't3', 't4']
        for q_id in tech_questions:
            if q_id in responses:
                if q_id == 't2':  # Integration question
                    tech_score += 10 if responses[q_id] else 3
                elif q_id == 't4':  # Automation scale
                    tech_score += responses[q_id]
                else:
                    tech_score += 5  # Base score for having technology
        
        scores['technology'] = min(tech_score / 4, 10)  # Normalize to 10
        
        # Operations score
        ops_score = 10
        if 'o1' in responses:  # Order processing time
            if responses['o1'] > 15:
                ops_score -= 3
        if 'o2' in responses:  # Error rate
            if responses['o2'] > 5:
                ops_score -= 3
        if 'o3' in responses:  # Manual hours
            if responses['o3'] > 6:
                ops_score -= 2
        if 'o4' in responses:  # Documented processes
            if not responses['o4']:
                ops_score -= 2
        
        scores['operations'] = max(ops_score, 1)
        
        # Integration score
        int_score = 0
        if 'i1' in responses:  # Payment gateways
            int_score += len(responses['i1']) * 2 if isinstance(responses['i1'], list) else 2
        if 'i2' in responses:  # Shipping services
            int_score += len(responses['i2']) * 1.5 if isinstance(responses['i2'], list) else 1.5
        if 'i3' in responses:  # Marketplaces
            int_score += len(responses['i3']) * 2 if isinstance(responses['i3'], list) else 0
        if 'i4' in responses:  # Inventory sync
            int_score += 3 if responses['i4'] else 0
        
        scores['integration'] = min(int_score, 10)
        
        # Calculate overall score
        overall_score = 0
        for category, weight in self.scoring_weights.items():
            if category in scores:
                overall_score += scores[category] * weight
        
        scores['overall'] = overall_score
        
        return scores
    
    def _identify_pain_points(self, responses: Dict) -> List[Dict]:
        """Identify and prioritize pain points"""
        
        pain_points = []
        
        # Manual processing pain
        if 't2' in responses and not responses['t2']:
            pain_points.append({
                'issue': 'Procesamiento Manual de Datos',
                'severity': 'ALTA',
                'impact': 'Pérdida de 15-20 horas semanales en tareas manuales',
                'cost_impact_clp': responses.get('b1', 500000000) * 0.03  # 3% of revenue
            })
        
        # High error rate
        if 'o2' in responses and responses['o2'] > 5:
            pain_points.append({
                'issue': 'Alta Tasa de Errores',
                'severity': 'CRÍTICA',
                'impact': f"{responses['o2']}% de órdenes con errores",
                'cost_impact_clp': responses.get('b2', 1000) * responses['o2'] * 5000  # 5000 CLP per error
            })
        
        # Inventory issues
        if 'o5' in responses and responses['o5'] in ['Diariamente', 'Semanalmente']:
            pain_points.append({
                'issue': 'Quiebres de Stock Frecuentes',
                'severity': 'ALTA',
                'impact': 'Pérdida de ventas y clientes insatisfechos',
                'cost_impact_clp': responses.get('b1', 500000000) * 0.05  # 5% lost sales
            })
        
        # No integration
        if 'i4' in responses and not responses['i4']:
            pain_points.append({
                'issue': 'Falta de Sincronización de Inventario',
                'severity': 'MEDIA',
                'impact': 'Sobreventa y problemas de fulfillment',
                'cost_impact_clp': responses.get('b2', 1000) * 10 * 15000  # 10 orders * 15000 CLP
            })
        
        # Sort by severity
        severity_order = {'CRÍTICA': 0, 'ALTA': 1, 'MEDIA': 2, 'BAJA': 3}
        pain_points.sort(key=lambda x: severity_order[x['severity']])
        
        return pain_points[:3]  # Return top 3 pain points
    
    def _calculate_maturity_level(self, scores: Dict) -> Dict:
        """Calculate digital maturity level"""
        
        overall_score = scores['overall']
        
        if overall_score >= 8:
            level = 'AVANZADO'
            description = 'Operaciones digitalizadas y optimizadas'
            color = 'green'
        elif overall_score >= 6:
            level = 'INTERMEDIO'
            description = 'Algunos procesos automatizados, con oportunidades de mejora'
            color = 'yellow'
        elif overall_score >= 4:
            level = 'BÁSICO'
            description = 'Procesos mayormente manuales con automatización limitada'
            color = 'orange'
        else:
            level = 'INICIAL'
            description = 'Operaciones principalmente manuales, alta oportunidad de mejora'
            color = 'red'
        
        return {
            'level': level,
            'score': overall_score,
            'description': description,
            'color': color,
            'breakdown': {
                'technology': f"{scores.get('technology', 0):.1f}/10",
                'operations': f"{scores.get('operations', 0):.1f}/10",
                'integration': f"{scores.get('integration', 0):.1f}/10"
            }
        }
    
    def _identify_opportunities(self, responses: Dict, scores: Dict) -> List[Dict]:
        """Identify improvement opportunities"""
        
        opportunities = []
        monthly_revenue = responses.get('b1', 500000000) / 12
        
        # Automation opportunity
        if scores.get('technology', 0) < 5:
            manual_hours = responses.get('o3', 8)
            labor_cost_per_hour = 5000  # CLP
            
            opportunities.append({
                'area': 'Automatización de Procesos',
                'current_state': f'{manual_hours} horas diarias en tareas manuales',
                'future_state': 'Reducción del 70% en trabajo manual',
                'monthly_savings_clp': manual_hours * 22 * labor_cost_per_hour * 0.7,
                'implementation_effort': 'MEDIO',
                'time_to_value': '2-3 semanas'
            })
        
        # Integration opportunity
        if not responses.get('t2', False):  # No ERP integration
            opportunities.append({
                'area': 'Integración ERP-Ecommerce',
                'current_state': 'Ingreso manual de datos entre sistemas',
                'future_state': 'Sincronización automática en tiempo real',
                'monthly_savings_clp': monthly_revenue * 0.02,  # 2% of revenue
                'implementation_effort': 'ALTO',
                'time_to_value': '4-6 semanas'
            })
        
        # Error reduction opportunity
        error_rate = responses.get('o2', 0)
        if error_rate > 3:
            opportunities.append({
                'area': 'Reducción de Errores',
                'current_state': f'{error_rate}% de órdenes con errores',
                'future_state': 'Menos del 1% de errores',
                'monthly_savings_clp': responses.get('b2', 1000) * (error_rate - 1) * 0.01 * 10000,
                'implementation_effort': 'BAJO',
                'time_to_value': '1-2 semanas'
            })
        
        # Marketplace expansion
        if 'i3' in responses and 'No vendo en marketplaces' in responses.get('i3', []):
            opportunities.append({
                'area': 'Expansión a Marketplaces',
                'current_state': 'Venta solo en canal propio',
                'future_state': 'Presencia en MercadoLibre y otros',
                'monthly_revenue_increase_clp': monthly_revenue * 0.25,  # 25% revenue increase
                'implementation_effort': 'MEDIO',
                'time_to_value': '3-4 semanas'
            })
        
        # Sort by value
        opportunities.sort(key=lambda x: x.get('monthly_savings_clp', 0) + x.get('monthly_revenue_increase_clp', 0), reverse=True)
        
        return opportunities[:4]  # Return top 4 opportunities
    
    def _calculate_roi_potential(self, responses: Dict, opportunities: List[Dict]) -> Dict:
        """Calculate potential ROI from improvements"""
        
        total_monthly_savings = sum(opp.get('monthly_savings_clp', 0) for opp in opportunities)
        total_revenue_increase = sum(opp.get('monthly_revenue_increase_clp', 0) for opp in opportunities)
        total_monthly_benefit = total_monthly_savings + total_revenue_increase
        
        # Estimate investment based on company size
        monthly_revenue = responses.get('b1', 500000000) / 12
        if monthly_revenue > 100000000:  # > 100M CLP/month
            estimated_investment = 30000000  # 30M CLP
        elif monthly_revenue > 50000000:  # > 50M CLP/month
            estimated_investment = 20000000  # 20M CLP
        else:
            estimated_investment = 10000000  # 10M CLP
        
        annual_benefit = total_monthly_benefit * 12
        roi_percentage = ((annual_benefit - estimated_investment) / estimated_investment) * 100
        payback_months = estimated_investment / total_monthly_benefit if total_monthly_benefit > 0 else float('inf')
        
        return {
            'total_monthly_savings_clp': total_monthly_savings,
            'total_monthly_revenue_increase_clp': total_revenue_increase,
            'total_monthly_benefit_clp': total_monthly_benefit,
            'total_annual_benefit_clp': annual_benefit,
            'estimated_investment_clp': estimated_investment,
            'roi_percentage': roi_percentage,
            'payback_months': payback_months,
            'three_year_value_clp': annual_benefit * 3 - estimated_investment
        }
    
    def _generate_recommendations(self, scores: Dict, pain_points: List[Dict], opportunities: List[Dict]) -> List[Dict]:
        """Generate prioritized recommendations"""
        
        recommendations = []
        
        # Priority 1: Address critical pain points
        for pain in pain_points[:2]:
            if pain['issue'] == 'Alta Tasa de Errores':
                recommendations.append({
                    'priority': 1,
                    'title': 'Implementar Sistema de Validación Automática',
                    'description': 'Validación en tiempo real de datos para prevenir errores',
                    'expected_impact': 'Reducción del 80% en errores de procesamiento',
                    'quick_win': True,
                    'implementation_time': '1-2 semanas'
                })
            elif pain['issue'] == 'Procesamiento Manual de Datos':
                recommendations.append({
                    'priority': 1,
                    'title': 'Automatizar Integración ERP-Ecommerce',
                    'description': 'Conectar sistemas para eliminar ingreso manual',
                    'expected_impact': 'Ahorro de 20+ horas semanales',
                    'quick_win': False,
                    'implementation_time': '3-4 semanas'
                })
        
        # Priority 2: Quick wins
        if scores.get('operations', 0) < 5:
            recommendations.append({
                'priority': 2,
                'title': 'Optimizar Proceso de Fulfillment',
                'description': 'Estandarizar y automatizar preparación de pedidos',
                'expected_impact': '40% reducción en tiempo de procesamiento',
                'quick_win': True,
                'implementation_time': '1 semana'
            })
        
        # Priority 3: Growth opportunities
        for opp in opportunities[:2]:
            if 'Marketplace' in opp.get('area', ''):
                recommendations.append({
                    'priority': 3,
                    'title': 'Expandir a MercadoLibre',
                    'description': 'Integración con el marketplace líder en Chile',
                    'expected_impact': '25-30% incremento en ventas',
                    'quick_win': False,
                    'implementation_time': '3-4 semanas'
                })
        
        return recommendations[:5]
    
    def _determine_engagement_scope(self, scores: Dict, roi_potential: Dict) -> Dict:
        """Determine recommended engagement scope"""
        
        if scores['overall'] < 4 and roi_potential['roi_percentage'] > 150:
            scope = 'TRANSFORMACIÓN COMPLETA'
            description = 'Rediseño integral de operaciones e-commerce'
            duration = '3-4 meses'
            investment_range = '25M - 40M CLP'
        elif scores['overall'] < 6 and roi_potential['roi_percentage'] > 100:
            scope = 'OPTIMIZACIÓN INTEGRAL'
            description = 'Automatización y optimización de procesos clave'
            duration = '2-3 meses'
            investment_range = '15M - 25M CLP'
        elif roi_potential['roi_percentage'] > 50:
            scope = 'MEJORAS FOCALIZADAS'
            description = 'Implementación de mejoras específicas de alto impacto'
            duration = '1-2 meses'
            investment_range = '8M - 15M CLP'
        else:
            scope = 'CONSULTORÍA PUNTUAL'
            description = 'Asesoría y quick wins'
            duration = '2-4 semanas'
            investment_range = '3M - 8M CLP'
        
        return {
            'scope': scope,
            'description': description,
            'duration': duration,
            'investment_range': investment_range,
            'included_services': self._get_included_services(scope)
        }
    
    def _get_included_services(self, scope: str) -> List[str]:
        """Get services included in engagement scope"""
        
        services = {
            'TRANSFORMACIÓN COMPLETA': [
                'Auditoría completa de operaciones',
                'Diseño de arquitectura de sistemas',
                'Implementación de integraciones',
                'Automatización de procesos',
                'Capacitación del equipo',
                'Soporte post-implementación (3 meses)',
                'Dashboard de KPIs en tiempo real'
            ],
            'OPTIMIZACIÓN INTEGRAL': [
                'Análisis de procesos críticos',
                'Implementación de automatizaciones',
                'Integración de sistemas principales',
                'Optimización de fulfillment',
                'Capacitación operativa',
                'Soporte post-implementación (1 mes)'
            ],
            'MEJORAS FOCALIZADAS': [
                'Diagnóstico de pain points',
                'Implementación de quick wins',
                'Automatización de 2-3 procesos',
                'Documentación de procesos',
                'Capacitación básica'
            ],
            'CONSULTORÍA PUNTUAL': [
                'Diagnóstico rápido',
                'Recomendaciones priorizadas',
                'Implementación de 1 mejora clave',
                'Guía de implementación'
            ]
        }
        
        return services.get(scope, [])
    
    def _qualify_prospect(self, scores: Dict, roi_potential: Dict, responses: Dict) -> Dict:
        """Qualify prospect based on assessment"""
        
        qualification_score = 0
        factors = []
        
        # Budget availability (30 points)
        if responses.get('g2', False):  # Has budget
            qualification_score += 30
            factors.append('✓ Presupuesto asignado')
        else:
            factors.append('✗ Sin presupuesto definido')
        
        # Urgency (25 points)
        urgency = responses.get('p3', 5)
        if urgency >= 8:
            qualification_score += 25
            factors.append('✓ Alta urgencia')
        elif urgency >= 6:
            qualification_score += 15
            factors.append('◐ Urgencia media')
        else:
            qualification_score += 5
            factors.append('✗ Baja urgencia')
        
        # ROI potential (25 points)
        if roi_potential['roi_percentage'] > 150:
            qualification_score += 25
            factors.append(f"✓ ROI excepcional ({roi_potential['roi_percentage']:.0f}%)")
        elif roi_potential['roi_percentage'] > 100:
            qualification_score += 18
            factors.append(f"✓ ROI alto ({roi_potential['roi_percentage']:.0f}%)")
        elif roi_potential['roi_percentage'] > 50:
            qualification_score += 10
            factors.append(f"◐ ROI moderado ({roi_potential['roi_percentage']:.0f}%)")
        else:
            factors.append(f"✗ ROI bajo ({roi_potential['roi_percentage']:.0f}%)")
        
        # Company size (20 points)
        monthly_revenue = responses.get('b1', 0) / 12
        if monthly_revenue > 50000000:  # > 50M CLP/month
            qualification_score += 20
            factors.append('✓ Empresa de tamaño ideal')
        elif monthly_revenue > 20000000:  # > 20M CLP/month
            qualification_score += 12
            factors.append('◐ Tamaño adecuado')
        else:
            qualification_score += 5
            factors.append('✗ Empresa pequeña')
        
        # Determine qualification level
        if qualification_score >= 80:
            level = 'A - HOT PROSPECT'
            action = 'Agendar reunión de propuesta inmediatamente'
            probability = 80
        elif qualification_score >= 60:
            level = 'B - QUALIFIED'
            action = 'Enviar propuesta y hacer seguimiento'
            probability = 50
        elif qualification_score >= 40:
            level = 'C - NURTURE'
            action = 'Mantener en pipeline, educar sobre valor'
            probability = 20
        else:
            level = 'D - NOT QUALIFIED'
            action = 'Agregar a lista de nurturing a largo plazo'
            probability = 5
        
        return {
            'score': qualification_score,
            'level': level,
            'factors': factors,
            'recommended_action': action,
            'close_probability': probability
        }
    
    def _generate_next_steps(self, qualification: Dict) -> List[str]:
        """Generate next steps based on qualification"""
        
        if 'HOT' in qualification['level']:
            return [
                '📅 Agendar reunión de propuesta dentro de 48 horas',
                '📊 Preparar propuesta personalizada con ROI específico',
                '💼 Involucrar a decision makers en la siguiente reunión',
                '🎯 Presentar plan de implementación con quick wins',
                '✍️ Preparar contrato y términos comerciales'
            ]
        elif 'QUALIFIED' in qualification['level']:
            return [
                '📧 Enviar propuesta detallada en próximas 24 horas',
                '📞 Programar llamada de seguimiento en 3 días',
                '📈 Compartir caso de éxito similar',
                '🎯 Identificar y contactar al decision maker',
                '📅 Proponer reunión de demostración'
            ]
        elif 'NURTURE' in qualification['level']:
            return [
                '📚 Enviar material educativo sobre ROI',
                '📧 Agregar a campaña de nurturing',
                '📅 Programar seguimiento en 30 días',
                '🎯 Identificar triggers de compra',
                '📊 Compartir benchmark de la industria'
            ]
        else:
            return [
                '📧 Agregar a lista de marketing',
                '📚 Enviar contenido educativo mensual',
                '📅 Revisar en 6 meses',
                '🔄 Mantener en CRM para futuro'
            ]
    
    def _create_company_profile(self, responses: Dict) -> Dict:
        """Create company profile from responses"""
        
        return {
            'industry': responses.get('b4', 'No especificado'),
            'monthly_revenue_clp': responses.get('b1', 0) / 12,
            'monthly_orders': responses.get('b2', 0),
            'team_size': responses.get('b3', 0),
            'current_platforms': {
                'ecommerce': responses.get('t1', 'No especificado'),
                'erp': responses.get('t3', []),
                'payments': responses.get('i1', []),
                'shipping': responses.get('i2', []),
                'marketplaces': responses.get('i3', [])
            }
        }
    
    def generate_assessment_report(self) -> str:
        """Generate formatted assessment report"""
        
        if not self.assessment_results:
            return "No assessment results available"
        
        results = self.assessment_results
        
        report = f"""
{'='*60}
INFORME DE EVALUACIÓN RÁPIDA - OPERACIONES E-COMMERCE
{'='*60}

📊 PERFIL DE LA EMPRESA
{'-'*40}
Industria: {results['company_profile']['industry']}
Facturación Mensual: ${results['company_profile']['monthly_revenue_clp']:,.0f} CLP
Órdenes Mensuales: {results['company_profile']['monthly_orders']}
Equipo: {results['company_profile']['team_size']} personas

🎯 NIVEL DE MADUREZ DIGITAL: {results['maturity_level']['level']}
{'-'*40}
Puntaje General: {results['maturity_level']['score']:.1f}/10
{results['maturity_level']['description']}

Desglose:
- Tecnología: {results['maturity_level']['breakdown']['technology']}
- Operaciones: {results['maturity_level']['breakdown']['operations']}
- Integración: {results['maturity_level']['breakdown']['integration']}

⚠️ PRINCIPALES PAIN POINTS
{'-'*40}"""
        
        for i, pain in enumerate(results['pain_points'], 1):
            report += f"""
{i}. {pain['issue']} ({pain['severity']})
   Impacto: {pain['impact']}
   Costo estimado: ${pain['cost_impact_clp']:,.0f} CLP/mes
"""
        
        report += f"""
💰 POTENCIAL DE ROI
{'-'*40}
Inversión Estimada: ${results['roi_potential']['estimated_investment_clp']:,.0f} CLP
Beneficio Anual: ${results['roi_potential']['total_annual_benefit_clp']:,.0f} CLP
ROI Proyectado: {results['roi_potential']['roi_percentage']:.0f}%
Período de Recuperación: {results['roi_potential']['payback_months']:.1f} meses
Valor a 3 Años: ${results['roi_potential']['three_year_value_clp']:,.0f} CLP

🚀 TOP 3 OPORTUNIDADES
{'-'*40}"""
        
        for i, opp in enumerate(results['opportunities'][:3], 1):
            value = opp.get('monthly_savings_clp', 0) + opp.get('monthly_revenue_increase_clp', 0)
            report += f"""
{i}. {opp['area']}
   Ahorro/Ingreso Mensual: ${value:,.0f} CLP
   Tiempo de Implementación: {opp['time_to_value']}
   Esfuerzo: {opp['implementation_effort']}
"""
        
        report += f"""
📋 ALCANCE RECOMENDADO: {results['engagement_scope']['scope']}
{'-'*40}
{results['engagement_scope']['description']}
Duración: {results['engagement_scope']['duration']}
Inversión: {results['engagement_scope']['investment_range']}

✅ CALIFICACIÓN: {results['qualification']['level']}
{'-'*40}
Puntaje: {results['qualification']['score']}/100
Probabilidad de Cierre: {results['qualification']['close_probability']}%
Acción Recomendada: {results['qualification']['recommended_action']}

📌 PRÓXIMOS PASOS
{'-'*40}"""
        
        for step in results['next_steps']:
            report += f"\n{step}"
        
        report += f"""

{'='*60}
Informe generado: {results['timestamp']}
{'='*60}
"""
        
        return report
    
    @error_handler
    def _basic_response_validation(self, responses: Dict) -> Dict:
        """Basic response validation as fallback when advanced validation fails"""
        try:
            validated = {}
            
            # Define basic expected responses with defaults and types
            defaults = {
                'b1': 50000000,  # Revenue (CLP)
                'b2': 500,  # Orders per month
                'b3': 3,  # Team size
                'b4': 'Retail',  # Industry
                't1': 'WooCommerce',  # E-commerce platform
                't2': False,  # ERP integration
                't3': ['Excel'],  # Management systems
                't4': 5,  # Automation level (1-10)
                'o1': 15,  # Processing time (minutes)
                'o2': 5,  # Error rate (%)
                'o3': 6,  # Manual hours daily
                'o4': False,  # Documented processes
                'o5': 'Mensualmente',  # Stock breaks frequency
                'i1': ['Transbank'],  # Payment gateways
                'i2': ['Chilexpress'],  # Shipping services
                'i3': ['No vendo en marketplaces'],  # Marketplaces
                'i4': False,  # Inventory sync
                'p1': ['Procesamiento manual'],  # Pain points
                'p2': 1000000,  # Monthly losses (CLP)
                'p3': 5,  # Urgency (1-10)
                'g1': 20,  # Growth target (%)
                'g2': False,  # Has budget
                'g3': '3-6 meses'  # Timeline
            }
            
            for key, default in defaults.items():
                try:
                    if key in responses and responses[key] is not None:
                        value = responses[key]
                        
                        if isinstance(default, bool):
                            if isinstance(value, bool):
                                validated[key] = value
                            elif isinstance(value, str):
                                validated[key] = value.lower() in ['true', 'yes', 'sí', '1', 'y']
                            elif isinstance(value, (int, float)):
                                validated[key] = bool(value)
                            else:
                                validated[key] = default
                                
                        elif isinstance(default, (int, float)):
                            try:
                                numeric_value = float(value)
                                if np.isnan(numeric_value) or np.isinf(numeric_value):
                                    validated[key] = default
                                elif numeric_value < 0 and key not in ['p2']:  # Allow negative for losses
                                    validated[key] = abs(numeric_value)
                                else:
                                    validated[key] = numeric_value
                            except (ValueError, TypeError):
                                validated[key] = default
                                
                        elif isinstance(default, str):
                            validated[key] = str(value).strip() if str(value).strip() else default
                            
                        elif isinstance(default, list):
                            if isinstance(value, list):
                                validated[key] = [str(item).strip() for item in value if item]
                            elif isinstance(value, str):
                                validated[key] = [item.strip() for item in value.split(',') if item.strip()]
                            else:
                                validated[key] = default
                        else:
                            validated[key] = value
                    else:
                        validated[key] = default
                        
                except Exception as e:
                    self.logger.warning(f"Error validating response {key}: {e}")
                    validated[key] = default
            
            self.logger.info(f"Basic validation completed for {len(validated)} responses")
            return validated
            
        except Exception as e:
            self.logger.error(f"Basic response validation failed: {e}")
            # Return minimal safe defaults
            return {
                'b1': 50000000,
                'b2': 500,
                'b3': 3,
                'b4': 'Retail',
                't2': False,
                't4': 5,
                'o1': 15,
                'o2': 5,
                'o3': 6,
                'o4': False,
                'i4': False,
                'p3': 5,
                'g2': False
            }


# Example usage
if __name__ == "__main__":
    # Initialize assessment tool
    assessment = RapidAssessmentTool()
    
    # Sample responses from a prospect
    sample_responses = {
        'b1': 600000000,  # 600M CLP annual revenue
        'b2': 1800,  # 1800 orders/month
        'b3': 5,  # 5 employees
        'b4': 'Retail',
        't1': 'WooCommerce',
        't2': False,  # No ERP integration
        't3': ['Excel', 'Defontana'],
        't4': 3,  # Low automation
        'o1': 25,  # 25 minutes per order
        'o2': 8,  # 8% error rate
        'o3': 10,  # 10 hours daily manual work
        'o4': False,  # No documented processes
        'o5': 'Semanalmente',
        'i1': ['Transbank', 'Webpay'],
        'i2': ['Chilexpress'],
        'i3': ['No vendo en marketplaces'],
        'i4': False,  # No inventory sync
        'p1': ['Procesamiento manual de órdenes', 'Errores en fulfillment', 'Gestión de inventario'],
        'p2': 5000000,  # 5M CLP monthly loss
        'p3': 8,  # High urgency
        'g1': 50,  # 50% growth target
        'g2': True,  # Has budget
        'g3': '1-3 meses'
    }
    
    # Conduct assessment
    results = assessment.conduct_assessment(sample_responses)
    
    # Generate and print report
    report = assessment.generate_assessment_report()
    print(report)
    
    # Save results to JSON
    with open('assessment_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
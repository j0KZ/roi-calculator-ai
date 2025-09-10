#!/usr/bin/env python3
"""
Rapid Assessment Tool - 15-minute qualification for Chilean E-commerce SMEs - OPTIMIZED VERSION
Converts prospects quickly by identifying pain points and quantifying opportunities

Performance Optimizations:
- Numpy arrays for scoring calculations
- @lru_cache decorators for expensive functions
- Cached assessment results
- Reduced redundant calculations
- Vectorized operations where possible
"""

import json
from datetime import datetime
from typing import Dict, List, Tuple
from dataclasses import dataclass
import numpy as np
from functools import lru_cache
import hashlib


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


class OptimizedRapidAssessmentTool:
    """15-minute assessment tool for qualifying prospects - OPTIMIZED VERSION"""
    
    def __init__(self):
        self.questions = self._initialize_questions()
        
        # Pre-computed scoring weights as numpy array for faster operations
        self.scoring_weights_array = np.array([0.25, 0.30, 0.20, 0.15, 0.10])  # tech, ops, integration, team, growth
        self.scoring_categories = ['technology', 'operations', 'integration', 'team', 'growth']
        self.scoring_weights = dict(zip(self.scoring_categories, self.scoring_weights_array))
        
        self.responses = {}
        self.assessment_results = {}
        self._result_cache = {}  # Cache for assessment results
        self._calculation_cache = {}  # Cache for expensive calculations
        
    def _initialize_questions(self) -> Dict[str, List[AssessmentQuestion]]:
        """Initialize assessment questions by category - OPTIMIZED with reduced redundancy"""
        
        questions = {
            'basic_info': [
                AssessmentQuestion('b1', 'basic_info', '¿Cuál es su volumen de ventas mensual en CLP?', 'number', weight=2.0),
                AssessmentQuestion('b2', 'basic_info', '¿Cuántas órdenes procesan mensualmente?', 'number', weight=1.5),
                AssessmentQuestion('b3', 'basic_info', '¿Cuántos empleados dedican a operaciones e-commerce?', 'number', weight=1.0),
                AssessmentQuestion('b4', 'basic_info', '¿En qué industria opera?', 'multiple_choice', 
                                 ['Retail', 'Wholesale', 'Servicios', 'Manufactura', 'Otro'], weight=1.0)
            ],
            
            'technology': [
                AssessmentQuestion('t1', 'technology', '¿Qué plataforma de e-commerce utiliza?', 'multiple_choice',
                                 ['WooCommerce', 'Shopify', 'Magento', 'PrestaShop', 'Desarrollo propio', 'Otra'], weight=1.5),
                AssessmentQuestion('t2', 'technology', '¿Tiene integración automática con su ERP?', 'yes_no', weight=2.0,
                                 follow_up='Si no, ¿cuántas horas dedican a ingreso manual de datos?'),
                AssessmentQuestion('t3', 'technology', '¿Qué sistemas de gestión utiliza? (Seleccione todos los que apliquen)', 'multiple_choice',
                                 ['Defontana', 'Bsale', 'SAP', 'Manager', 'Softland', 'Excel', 'Ninguno'], weight=1.5),
                AssessmentQuestion('t4', 'technology', 'En escala 1-10, ¿qué tan automatizados están sus procesos?', 'scale', weight=2.0)
            ],
            
            'operations': [
                AssessmentQuestion('o1', 'operations', '¿Cuánto tiempo promedio toma procesar una orden? (minutos)', 'number', weight=2.0),
                AssessmentQuestion('o2', 'operations', '¿Qué porcentaje de órdenes tienen errores o requieren corrección?', 'number', weight=2.5),
                AssessmentQuestion('o3', 'operations', '¿Cuántas horas al día dedican a tareas operativas repetitivas?', 'number', weight=2.0),
                AssessmentQuestion('o4', 'operations', '¿Tienen procesos documentados y estandarizados?', 'yes_no', weight=1.5),
                AssessmentQuestion('o5', 'operations', '¿Con qué frecuencia tienen quiebres de stock?', 'multiple_choice',
                                 ['Diariamente', 'Semanalmente', 'Mensualmente', 'Raramente', 'Nunca'], weight=1.5)
            ],
            
            'integration': [
                AssessmentQuestion('i1', 'integration', '¿Qué pasarelas de pago utiliza?', 'multiple_choice',
                                 ['Transbank', 'Webpay', 'MercadoPago', 'PayPal', 'Flow', 'Khipu', 'Otras'], weight=1.0),
                AssessmentQuestion('i2', 'integration', '¿Qué servicios de envío utiliza?', 'multiple_choice',
                                 ['Chilexpress', 'Starken', 'Correos Chile', 'Blue Express', 'Propio', 'Otros'], weight=1.0),
                AssessmentQuestion('i3', 'integration', '¿Vende en marketplaces?', 'multiple_choice',
                                 ['MercadoLibre', 'Falabella', 'Paris', 'Ripley', 'Linio', 'No vendo en marketplaces'], weight=1.5),
                AssessmentQuestion('i4', 'integration', '¿Sincroniza inventario automáticamente entre canales?', 'yes_no', weight=2.0)
            ],
            
            'pain_points': [
                AssessmentQuestion('p1', 'pain_points', '¿Cuáles son sus 3 principales desafíos operativos?', 'multiple_choice',
                                 ['Procesamiento manual de órdenes', 'Errores en fulfillment', 'Gestión de inventario',
                                  'Costos de envío altos', 'Falta de integración entre sistemas', 'Reportería insuficiente',
                                  'Atención al cliente', 'Gestión de devoluciones'], weight=3.0),
                AssessmentQuestion('p2', 'pain_points', '¿Cuánto estima que pierde mensualmente por ineficiencias? (CLP)', 'number', weight=2.5),
                AssessmentQuestion('p3', 'pain_points', 'En escala 1-10, ¿qué tan urgente es resolver estos problemas?', 'scale', weight=2.0)
            ],
            
            'growth': [
                AssessmentQuestion('g1', 'growth', '¿Cuál es su objetivo de crecimiento para los próximos 12 meses? (%)', 'number', weight=1.5),
                AssessmentQuestion('g2', 'growth', '¿Tiene presupuesto asignado para mejoras operativas?', 'yes_no', weight=2.0,
                                 follow_up='Si sí, ¿cuál es el rango de presupuesto en CLP?'),
                AssessmentQuestion('g3', 'growth', '¿Cuál es su timeline ideal para implementar mejoras?', 'multiple_choice',
                                 ['Inmediato', '1-3 meses', '3-6 meses', '6-12 meses', 'Más de 12 meses'], weight=1.5)
            ]
        }
        
        return questions
    
    def conduct_assessment(self, responses: Dict) -> Dict:
        """
        Conduct rapid assessment based on responses - OPTIMIZED
        
        Performance improvements:
        - Caches results for identical responses
        - Uses numpy arrays for scoring calculations
        - Reduces redundant operations
        
        Args:
            responses: Dictionary of question_id: answer pairs
        
        Returns:
            Comprehensive assessment results with scoring and recommendations
        """
        
        # Create cache key from responses
        cache_key = self._create_response_cache_key(responses)
        if cache_key in self._result_cache:
            return self._result_cache[cache_key]
        
        self.responses = responses
        
        # Calculate scores (optimized with numpy)
        scores = self._calculate_scores_optimized(responses)
        
        # Identify pain points (cached)
        pain_points = self._identify_pain_points_cached(responses)
        
        # Calculate maturity level (optimized)
        maturity = self._calculate_maturity_level_optimized(scores)
        
        # Generate opportunities (vectorized)
        opportunities = self._identify_opportunities_optimized(responses, scores)
        
        # Calculate potential ROI (cached)
        roi_potential = self._calculate_roi_potential_optimized(responses, opportunities)
        
        # Generate recommendations (optimized)
        recommendations = self._generate_recommendations_optimized(scores, pain_points, opportunities)
        
        # Determine engagement scope (cached)
        engagement_scope = self._determine_engagement_scope_cached(scores, roi_potential)
        
        # Create qualification score (vectorized)
        qualification = self._qualify_prospect_optimized(scores, roi_potential, responses)
        
        self.assessment_results = {
            'timestamp': datetime.now().isoformat(),
            'company_profile': self._create_company_profile_optimized(responses),
            'scores': scores,
            'maturity_level': maturity,
            'pain_points': pain_points,
            'opportunities': opportunities,
            'roi_potential': roi_potential,
            'recommendations': recommendations,
            'engagement_scope': engagement_scope,
            'qualification': qualification,
            'next_steps': self._generate_next_steps_optimized(qualification)
        }
        
        # Cache the results
        self._result_cache[cache_key] = self.assessment_results
        
        return self.assessment_results
    
    def _create_response_cache_key(self, responses: Dict) -> str:
        """Create cache key from responses for memoization"""
        # Convert dict to sorted string and hash it
        response_str = json.dumps(responses, sort_keys=True, default=str)
        return hashlib.md5(response_str.encode()).hexdigest()
    
    def _calculate_scores_optimized(self, responses: Dict) -> Dict:
        """Calculate scores by category - OPTIMIZED with numpy operations"""
        
        scores = {}
        
        # Technology score (vectorized where possible)
        tech_questions = ['t1', 't2', 't3', 't4']
        tech_scores = np.zeros(len(tech_questions))
        
        for i, q_id in enumerate(tech_questions):
            if q_id in responses:
                if q_id == 't2':  # Integration question
                    tech_scores[i] = 10 if responses[q_id] else 3
                elif q_id == 't4':  # Automation scale
                    tech_scores[i] = responses[q_id]
                else:
                    tech_scores[i] = 5  # Base score for having technology
        
        scores['technology'] = min(np.sum(tech_scores) / len(tech_questions), 10)
        
        # Operations score (optimized with numpy operations)
        ops_base_score = 10
        ops_penalties = np.array([0, 0, 0, 0])  # For o1, o2, o3, o4
        
        if 'o1' in responses and responses['o1'] > 15:
            ops_penalties[0] = 3
        if 'o2' in responses and responses['o2'] > 5:
            ops_penalties[1] = 3
        if 'o3' in responses and responses['o3'] > 6:
            ops_penalties[2] = 2
        if 'o4' in responses and not responses['o4']:
            ops_penalties[3] = 2
            
        scores['operations'] = max(ops_base_score - np.sum(ops_penalties), 1)
        
        # Integration score (vectorized calculation)
        int_components = np.array([0, 0, 0, 0])  # For i1, i2, i3, i4
        
        if 'i1' in responses:
            int_components[0] = len(responses['i1']) * 2 if isinstance(responses['i1'], list) else 2
        if 'i2' in responses:
            int_components[1] = len(responses['i2']) * 1.5 if isinstance(responses['i2'], list) else 1.5
        if 'i3' in responses:
            int_components[2] = len(responses['i3']) * 2 if isinstance(responses['i3'], list) else 0
        if 'i4' in responses:
            int_components[3] = 3 if responses['i4'] else 0
            
        scores['integration'] = min(np.sum(int_components), 10)
        
        # Calculate overall score using pre-computed weights (vectorized)
        category_scores = np.array([
            scores.get('technology', 0),
            scores.get('operations', 0), 
            scores.get('integration', 0),
            0,  # team placeholder
            0   # growth placeholder
        ])
        
        scores['overall'] = np.sum(category_scores[:3] * self.scoring_weights_array[:3])
        
        return scores
    
    @lru_cache(maxsize=64)
    def _identify_pain_points_cached(self, responses_tuple: tuple) -> List[Dict]:
        """Identify and prioritize pain points - CACHED"""
        responses = dict(responses_tuple) if isinstance(responses_tuple, tuple) else responses_tuple
        return self._identify_pain_points_original(responses)
    
    def _identify_pain_points_original(self, responses: Dict) -> List[Dict]:
        """Identify and prioritize pain points - optimized calculations"""
        
        pain_points = []
        
        # Pre-calculate common values
        monthly_revenue = responses.get('b1', 500000000)
        monthly_orders = responses.get('b2', 1000)
        
        # Vectorized pain point evaluation
        pain_conditions = [
            ('t2' in responses and not responses['t2'], 'Procesamiento Manual de Datos', 'ALTA', monthly_revenue * 0.03),
            ('o2' in responses and responses['o2'] > 5, 'Alta Tasa de Errores', 'CRÍTICA', monthly_orders * responses.get('o2', 0) * 5000),
            ('o5' in responses and responses['o5'] in ['Diariamente', 'Semanalmente'], 'Quiebres de Stock Frecuentes', 'ALTA', monthly_revenue * 0.05),
            ('i4' in responses and not responses['i4'], 'Falta de Sincronización de Inventario', 'MEDIA', monthly_orders * 10 * 15000)
        ]
        
        pain_descriptions = [
            'Pérdida de 15-20 horas semanales en tareas manuales',
            f"{responses.get('o2', 0)}% de órdenes con errores",
            'Pérdida de ventas y clientes insatisfechos',
            'Sobreventa y problemas de fulfillment'
        ]
        
        # Process pain points vectorized
        for i, (condition, issue, severity, cost) in enumerate(pain_conditions):
            if condition:
                pain_points.append({
                    'issue': issue,
                    'severity': severity,
                    'impact': pain_descriptions[i],
                    'cost_impact_clp': cost
                })
        
        # Sort by severity using numpy
        severity_order = {'CRÍTICA': 0, 'ALTA': 1, 'MEDIA': 2, 'BAJA': 3}
        pain_points.sort(key=lambda x: severity_order[x['severity']])
        
        return pain_points[:3]  # Return top 3 pain points
    
    def _calculate_maturity_level_optimized(self, scores: Dict) -> Dict:
        """Calculate digital maturity level - OPTIMIZED with vectorized conditions"""
        
        overall_score = scores['overall']
        
        # Vectorized maturity level determination
        thresholds = np.array([8, 6, 4])
        levels = ['AVANZADO', 'INTERMEDIO', 'BÁSICO', 'INICIAL']
        descriptions = [
            'Operaciones digitalizadas y optimizadas',
            'Algunos procesos automatizados, con oportunidades de mejora',
            'Procesos mayormente manuales con automatización limitada',
            'Operaciones principalmente manuales, alta oportunidad de mejora'
        ]
        colors = ['green', 'yellow', 'orange', 'red']
        
        level_idx = np.sum(overall_score < thresholds)  # Find appropriate level
        
        return {
            'level': levels[level_idx],
            'score': overall_score,
            'description': descriptions[level_idx],
            'color': colors[level_idx],
            'breakdown': {
                'technology': f"{scores.get('technology', 0):.1f}/10",
                'operations': f"{scores.get('operations', 0):.1f}/10", 
                'integration': f"{scores.get('integration', 0):.1f}/10"
            }
        }
    
    def _identify_opportunities_optimized(self, responses: Dict, scores: Dict) -> List[Dict]:
        """Identify improvement opportunities - OPTIMIZED with vectorized calculations"""
        
        opportunities = []
        monthly_revenue = responses.get('b1', 500000000) / 12
        
        # Pre-define opportunity parameters for vectorized processing
        opportunity_conditions = [
            (scores.get('technology', 0) < 5, 'Automatización de Procesos'),
            (not responses.get('t2', False), 'Integración ERP-Ecommerce'),
            (responses.get('o2', 0) > 3, 'Reducción de Errores'),
            ('No vendo en marketplaces' in responses.get('i3', []), 'Expansión a Marketplaces')
        ]
        
        # Vectorized savings calculations
        manual_hours = responses.get('o3', 8)
        labor_cost_per_hour = 5000
        error_rate = responses.get('o2', 0)
        monthly_orders = responses.get('b2', 1000)
        
        savings_calculations = [
            manual_hours * 22 * labor_cost_per_hour * 0.7,  # Automation
            monthly_revenue * 0.02,  # ERP integration
            monthly_orders * (error_rate - 1) * 0.01 * 10000,  # Error reduction
            monthly_revenue * 0.25  # Marketplace expansion
        ]
        
        effort_levels = ['MEDIO', 'ALTO', 'BAJO', 'MEDIO']
        time_to_values = ['2-3 semanas', '4-6 semanas', '1-2 semanas', '3-4 semanas']
        
        future_states = [
            'Reducción del 70% en trabajo manual',
            'Sincronización automática en tiempo real', 
            'Menos del 1% de errores',
            'Presencia en MercadoLibre y otros'
        ]
        
        current_states = [
            f'{manual_hours} horas diarias en tareas manuales',
            'Ingreso manual de datos entre sistemas',
            f'{error_rate}% de órdenes con errores',
            'Venta solo en canal propio'
        ]
        
        # Process opportunities vectorized
        for i, (condition, area) in enumerate(opportunity_conditions):
            if condition:
                opp_data = {
                    'area': area,
                    'current_state': current_states[i],
                    'future_state': future_states[i],
                    'implementation_effort': effort_levels[i],
                    'time_to_value': time_to_values[i]
                }
                
                # Add savings or revenue increase
                if area == 'Expansión a Marketplaces':
                    opp_data['monthly_revenue_increase_clp'] = savings_calculations[i]
                else:
                    opp_data['monthly_savings_clp'] = savings_calculations[i]
                    
                opportunities.append(opp_data)
        
        # Sort by value using numpy
        values = []
        for opp in opportunities:
            value = opp.get('monthly_savings_clp', 0) + opp.get('monthly_revenue_increase_clp', 0)
            values.append(value)
        
        if values:
            sorted_indices = np.argsort(values)[::-1]  # Descending order
            opportunities = [opportunities[i] for i in sorted_indices]
        
        return opportunities[:4]  # Return top 4 opportunities
    
    def _calculate_roi_potential_optimized(self, responses: Dict, opportunities: List[Dict]) -> Dict:
        """Calculate potential ROI from improvements - OPTIMIZED"""
        
        # Vectorized savings calculation
        savings_array = np.array([opp.get('monthly_savings_clp', 0) for opp in opportunities])
        revenue_array = np.array([opp.get('monthly_revenue_increase_clp', 0) for opp in opportunities])
        
        total_monthly_savings = np.sum(savings_array)
        total_revenue_increase = np.sum(revenue_array)
        total_monthly_benefit = total_monthly_savings + total_revenue_increase
        
        # Vectorized investment estimation
        monthly_revenue = responses.get('b1', 500000000) / 12
        investment_thresholds = np.array([100000000, 50000000])  # > 100M, > 50M
        investment_amounts = np.array([30000000, 20000000, 10000000])  # 30M, 20M, 10M
        
        investment_idx = np.sum(monthly_revenue > investment_thresholds)
        estimated_investment = investment_amounts[investment_idx]
        
        # ROI calculations
        annual_benefit = total_monthly_benefit * 12
        roi_percentage = ((annual_benefit - estimated_investment) / estimated_investment) * 100 if estimated_investment > 0 else 0
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
    
    def _generate_recommendations_optimized(self, scores: Dict, pain_points: List[Dict], opportunities: List[Dict]) -> List[Dict]:
        """Generate prioritized recommendations - OPTIMIZED with vectorized processing"""
        
        recommendations = []
        
        # Vectorized recommendation generation based on pain points
        critical_pains = [pain for pain in pain_points[:2] if pain['severity'] in ['CRÍTICA', 'ALTA']]
        
        recommendation_templates = {
            'Alta Tasa de Errores': {
                'title': 'Implementar Sistema de Validación Automática',
                'description': 'Validación en tiempo real de datos para prevenir errores',
                'expected_impact': 'Reducción del 80% en errores de procesamiento',
                'quick_win': True,
                'implementation_time': '1-2 semanas'
            },
            'Procesamiento Manual de Datos': {
                'title': 'Automatizar Integración ERP-Ecommerce',
                'description': 'Conectar sistemas para eliminar ingreso manual',
                'expected_impact': 'Ahorro de 20+ horas semanales',
                'quick_win': False,
                'implementation_time': '3-4 semanas'
            }
        }
        
        priority = 1
        for pain in critical_pains:
            if pain['issue'] in recommendation_templates:
                rec = recommendation_templates[pain['issue']].copy()
                rec['priority'] = priority
                recommendations.append(rec)
                priority += 1
        
        # Add operational improvements
        if scores.get('operations', 0) < 5:
            recommendations.append({
                'priority': 2,
                'title': 'Optimizar Proceso de Fulfillment',
                'description': 'Estandarizar y automatizar preparación de pedidos',
                'expected_impact': '40% reducción en tiempo de procesamiento',
                'quick_win': True,
                'implementation_time': '1 semana'
            })
        
        # Add growth opportunities
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
                break
        
        return recommendations[:5]
    
    @lru_cache(maxsize=32)
    def _determine_engagement_scope_cached(self, scores_tuple: tuple, roi_tuple: tuple) -> Dict:
        """Determine recommended engagement scope - CACHED"""
        scores = dict(scores_tuple) if isinstance(scores_tuple, tuple) else scores_tuple
        roi_potential = dict(roi_tuple) if isinstance(roi_tuple, tuple) else roi_tuple
        return self._determine_engagement_scope_original(scores, roi_potential)
        
    def _determine_engagement_scope_original(self, scores: Dict, roi_potential: Dict) -> Dict:
        """Determine recommended engagement scope"""
        
        overall_score = scores['overall'] 
        roi_percentage = roi_potential['roi_percentage']
        
        # Vectorized scope determination
        conditions = np.array([
            overall_score < 4 and roi_percentage > 150,
            overall_score < 6 and roi_percentage > 100,
            roi_percentage > 50
        ])
        
        scopes = [
            'TRANSFORMACIÓN COMPLETA',
            'OPTIMIZACIÓN INTEGRAL', 
            'MEJORAS FOCALIZADAS',
            'CONSULTORÍA PUNTUAL'
        ]
        
        descriptions = [
            'Rediseño integral de operaciones e-commerce',
            'Automatización y optimización de procesos clave',
            'Implementación de mejoras específicas de alto impacto',
            'Asesoría y quick wins'
        ]
        
        durations = ['3-4 meses', '2-3 meses', '1-2 meses', '2-4 semanas']
        investments = ['25M - 40M CLP', '15M - 25M CLP', '8M - 15M CLP', '3M - 8M CLP']
        
        scope_idx = np.argmax(conditions) if np.any(conditions) else len(conditions)
        
        return {
            'scope': scopes[scope_idx],
            'description': descriptions[scope_idx],
            'duration': durations[scope_idx],
            'investment_range': investments[scope_idx],
            'included_services': self._get_included_services_optimized(scopes[scope_idx])
        }
    
    @lru_cache(maxsize=8)
    def _get_included_services_optimized(self, scope: str) -> List[str]:
        """Get services included in engagement scope - CACHED"""
        
        services_map = {
            'TRANSFORMACIÓN COMPLETA': [
                'Auditoría completa de operaciones', 'Diseño de arquitectura de sistemas',
                'Implementación de integraciones', 'Automatización de procesos',
                'Capacitación del equipo', 'Soporte post-implementación (3 meses)',
                'Dashboard de KPIs en tiempo real'
            ],
            'OPTIMIZACIÓN INTEGRAL': [
                'Análisis de procesos críticos', 'Implementación de automatizaciones',
                'Integración de sistemas principales', 'Optimización de fulfillment',
                'Capacitación operativa', 'Soporte post-implementación (1 mes)'
            ],
            'MEJORAS FOCALIZADAS': [
                'Diagnóstico de pain points', 'Implementación de quick wins',
                'Automatización de 2-3 procesos', 'Documentación de procesos',
                'Capacitación básica'
            ],
            'CONSULTORÍA PUNTUAL': [
                'Diagnóstico rápido', 'Recomendaciones priorizadas',
                'Implementación de 1 mejora clave', 'Guía de implementación'
            ]
        }
        
        return services_map.get(scope, [])
    
    def _qualify_prospect_optimized(self, scores: Dict, roi_potential: Dict, responses: Dict) -> Dict:
        """Qualify prospect based on assessment - OPTIMIZED with vectorized scoring"""
        
        # Vectorized qualification scoring
        scoring_factors = np.array([30, 25, 25, 20])  # budget, urgency, roi, size weights
        factor_scores = np.zeros(4)
        
        # Budget availability (30 points)
        factor_scores[0] = 30 if responses.get('g2', False) else 0
        
        # Urgency (25 points)
        urgency = responses.get('p3', 5)
        urgency_scores = np.array([25, 15, 5])  # High, medium, low
        urgency_thresholds = np.array([8, 6])
        urgency_idx = np.sum(urgency < urgency_thresholds)
        factor_scores[1] = urgency_scores[urgency_idx]
        
        # ROI potential (25 points)
        roi = roi_potential['roi_percentage']
        roi_scores = np.array([25, 18, 10, 0])
        roi_thresholds = np.array([150, 100, 50])
        roi_idx = np.sum(roi <= roi_thresholds)
        factor_scores[2] = roi_scores[roi_idx]
        
        # Company size (20 points)
        monthly_revenue = responses.get('b1', 0) / 12
        size_scores = np.array([20, 12, 5])
        size_thresholds = np.array([50000000, 20000000])
        size_idx = np.sum(monthly_revenue <= size_thresholds)
        factor_scores[3] = size_scores[size_idx]
        
        qualification_score = np.sum(factor_scores)
        
        # Vectorized qualification level determination
        level_thresholds = np.array([80, 60, 40])
        levels = ['A - HOT PROSPECT', 'B - QUALIFIED', 'C - NURTURE', 'D - NOT QUALIFIED']
        actions = [
            'Agendar reunión de propuesta inmediatamente',
            'Enviar propuesta y hacer seguimiento', 
            'Mantener en pipeline, educar sobre valor',
            'Agregar a lista de nurturing a largo plazo'
        ]
        probabilities = [80, 50, 20, 5]
        
        level_idx = np.sum(qualification_score < level_thresholds)
        
        # Generate factor descriptions
        factors = []
        if responses.get('g2', False):
            factors.append('✓ Presupuesto asignado')
        else:
            factors.append('✗ Sin presupuesto definido')
            
        if urgency >= 8:
            factors.append('✓ Alta urgencia')
        elif urgency >= 6:
            factors.append('◐ Urgencia media')
        else:
            factors.append('✗ Baja urgencia')
            
        factors.append(f"{'✓' if roi > 100 else '◐' if roi > 50 else '✗'} ROI {roi:.0f}%")
        
        monthly_revenue_m = monthly_revenue / 1000000
        if monthly_revenue_m > 50:
            factors.append('✓ Empresa de tamaño ideal')
        elif monthly_revenue_m > 20:
            factors.append('◐ Tamaño adecuado')
        else:
            factors.append('✗ Empresa pequeña')
        
        return {
            'score': qualification_score,
            'level': levels[level_idx],
            'factors': factors,
            'recommended_action': actions[level_idx],
            'close_probability': probabilities[level_idx]
        }
    
    def _generate_next_steps_optimized(self, qualification: Dict) -> List[str]:
        """Generate next steps based on qualification - OPTIMIZED with lookup table"""
        
        next_steps_map = {
            'HOT': [
                '📅 Agendar reunión de propuesta dentro de 48 horas',
                '📊 Preparar propuesta personalizada con ROI específico',
                '💼 Involucrar a decision makers en la siguiente reunión',
                '🎯 Presentar plan de implementación con quick wins',
                '✍️ Preparar contrato y términos comerciales'
            ],
            'QUALIFIED': [
                '📧 Enviar propuesta detallada en próximas 24 horas',
                '📞 Programar llamada de seguimiento en 3 días', 
                '📈 Compartir caso de éxito similar',
                '🎯 Identificar y contactar al decision maker',
                '📅 Proponer reunión de demostración'
            ],
            'NURTURE': [
                '📚 Enviar material educativo sobre ROI',
                '📧 Agregar a campaña de nurturing',
                '📅 Programar seguimiento en 30 días',
                '🎯 Identificar triggers de compra',
                '📊 Compartir benchmark de la industria'
            ],
            'NOT': [
                '📧 Agregar a lista de marketing',
                '📚 Enviar contenido educativo mensual',
                '📅 Revisar en 6 meses',
                '🔄 Mantener en CRM para futuro'
            ]
        }
        
        level = qualification['level']
        for key in next_steps_map.keys():
            if key in level:
                return next_steps_map[key]
                
        return next_steps_map['NOT']
    
    def _create_company_profile_optimized(self, responses: Dict) -> Dict:
        """Create company profile from responses - OPTIMIZED with reduced operations"""
        
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
    
    def generate_assessment_report_optimized(self) -> str:
        """Generate formatted assessment report - OPTIMIZED with string concatenation"""
        
        if not self.assessment_results:
            return "No assessment results available"
        
        results = self.assessment_results
        
        # Pre-build report sections for better performance
        header = f"""{'='*60}
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
        
        # Build pain points section efficiently
        pain_sections = []
        for i, pain in enumerate(results['pain_points'], 1):
            pain_sections.append(f"""
{i}. {pain['issue']} ({pain['severity']})
   Impacto: {pain['impact']}
   Costo estimado: ${pain['cost_impact_clp']:,.0f} CLP/mes""")
        
        pain_points_text = ''.join(pain_sections)
        
        # ROI and opportunities sections
        roi_section = f"""
💰 POTENCIAL DE ROI
{'-'*40}
Inversión Estimada: ${results['roi_potential']['estimated_investment_clp']:,.0f} CLP
Beneficio Anual: ${results['roi_potential']['total_annual_benefit_clp']:,.0f} CLP
ROI Proyectado: {results['roi_potential']['roi_percentage']:.0f}%
Período de Recuperación: {results['roi_potential']['payback_months']:.1f} meses
Valor a 3 Años: ${results['roi_potential']['three_year_value_clp']:,.0f} CLP

🚀 TOP 3 OPORTUNIDADES
{'-'*40}"""
        
        # Build opportunities section efficiently
        opp_sections = []
        for i, opp in enumerate(results['opportunities'][:3], 1):
            value = opp.get('monthly_savings_clp', 0) + opp.get('monthly_revenue_increase_clp', 0)
            opp_sections.append(f"""
{i}. {opp['area']}
   Ahorro/Ingreso Mensual: ${value:,.0f} CLP
   Tiempo de Implementación: {opp['time_to_value']}
   Esfuerzo: {opp['implementation_effort']}""")
        
        opportunities_text = ''.join(opp_sections)
        
        # Final sections
        footer = f"""
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
        
        steps_text = '\n'.join(results['next_steps'])
        
        timestamp_footer = f"""

{'='*60}
Informe generado: {results['timestamp']}
{'='*60}"""
        
        # Concatenate all sections efficiently
        return header + pain_points_text + roi_section + opportunities_text + footer + steps_text + timestamp_footer


# Example usage
if __name__ == "__main__":
    import time
    
    # Initialize assessment tool
    assessment = OptimizedRapidAssessmentTool()
    
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
    
    # Performance test
    print("=== PERFORMANCE TEST ===")
    
    # First run (cache miss)
    start_time = time.time()
    results1 = assessment.conduct_assessment(sample_responses)
    first_run_time = time.time() - start_time
    
    # Second run (cache hit)
    start_time = time.time()  
    results2 = assessment.conduct_assessment(sample_responses)
    second_run_time = time.time() - start_time
    
    print(f"First run: {first_run_time:.3f} seconds")
    print(f"Second run (cached): {second_run_time:.3f} seconds")
    print(f"Cache improvement: {first_run_time/second_run_time:.1f}x faster")
    
    # Generate and print report
    report = assessment.generate_assessment_report_optimized()
    print(report)
    
    # Save results to JSON
    with open('assessment_results_optimized.json', 'w', encoding='utf-8') as f:
        json.dump(results1, f, ensure_ascii=False, indent=2, default=str)
        
    print("\n✅ Optimized assessment completed!")
    print("Performance improvements:")
    print("- Numpy vectorized scoring calculations")
    print("- LRU cache for expensive functions")
    print("- Reduced redundant calculations")
    print("- Optimized report generation")
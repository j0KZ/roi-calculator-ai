"""
AI-Powered Cost Optimizer for ROI Calculator
Analyzes cost patterns and provides optimization recommendations using ML and heuristics
"""

import os
import json
import logging
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

@dataclass
class OptimizationRecommendation:
    """Data class for optimization recommendations"""
    category: str
    current_value: float
    optimized_value: float
    potential_savings: float
    confidence_score: float
    priority: str  # 'high', 'medium', 'low'
    description: str
    implementation_difficulty: str  # 'easy', 'moderate', 'difficult'
    timeframe: str  # 'immediate', 'short-term', 'long-term'
    risk_level: str  # 'low', 'medium', 'high'
    supporting_data: Dict[str, Any]

@dataclass
class BenchmarkData:
    """Industry benchmark data"""
    industry: str
    company_size: str  # 'small', 'medium', 'large'
    metric: str
    p25: float  # 25th percentile
    p50: float  # 50th percentile (median)
    p75: float  # 75th percentile
    p90: float  # 90th percentile
    source: str

@dataclass
class OptimizationReport:
    """Complete optimization report"""
    company_name: str
    analysis_date: datetime
    current_metrics: Dict[str, float]
    recommendations: List[OptimizationRecommendation]
    total_potential_savings: float
    implementation_timeline: Dict[str, List[str]]
    risk_assessment: Dict[str, Any]
    benchmark_comparison: Dict[str, Any]
    priority_matrix: Dict[str, List[str]]

class CostOptimizer:
    """AI-powered cost optimization engine"""
    
    # Class-level cache for models (shared across instances)
    _ml_models_cache = None
    _models_trained = False
    
    def __init__(self, industry: str = 'ecommerce', lazy_load: bool = True):
        """
        Initialize cost optimizer
        
        Args:
            industry: Industry type for benchmarking
            lazy_load: If True, defer ML model training until needed
        """
        self.industry = industry
        self.benchmark_data = self._load_benchmark_data()
        self.optimization_rules = self._load_optimization_rules()
        self.lazy_load = lazy_load
        self.ml_models = None  # Initialize as None first
        
        if not lazy_load:
            self._ensure_models_loaded()
        
    def _load_benchmark_data(self) -> Dict[str, BenchmarkData]:
        """Load industry benchmark data"""
        benchmarks = {}
        
        # E-commerce benchmarks (these would typically be loaded from a database)
        ecommerce_benchmarks = [
            BenchmarkData('ecommerce', 'small', 'labor_cost_ratio', 0.12, 0.18, 0.25, 0.35, 'Industry Survey 2024'),
            BenchmarkData('ecommerce', 'medium', 'labor_cost_ratio', 0.10, 0.15, 0.22, 0.30, 'Industry Survey 2024'),
            BenchmarkData('ecommerce', 'large', 'labor_cost_ratio', 0.08, 0.12, 0.18, 0.25, 'Industry Survey 2024'),
            
            BenchmarkData('ecommerce', 'small', 'shipping_cost_ratio', 0.08, 0.12, 0.18, 0.25, 'Logistics Report 2024'),
            BenchmarkData('ecommerce', 'medium', 'shipping_cost_ratio', 0.06, 0.10, 0.15, 0.20, 'Logistics Report 2024'),
            BenchmarkData('ecommerce', 'large', 'shipping_cost_ratio', 0.04, 0.07, 0.12, 0.16, 'Logistics Report 2024'),
            
            BenchmarkData('ecommerce', 'small', 'error_rate', 0.02, 0.04, 0.07, 0.12, 'Quality Metrics 2024'),
            BenchmarkData('ecommerce', 'medium', 'error_rate', 0.015, 0.03, 0.05, 0.08, 'Quality Metrics 2024'),
            BenchmarkData('ecommerce', 'large', 'error_rate', 0.01, 0.02, 0.035, 0.05, 'Quality Metrics 2024'),
            
            BenchmarkData('ecommerce', 'small', 'inventory_turnover', 4, 6, 9, 12, 'Inventory Management 2024'),
            BenchmarkData('ecommerce', 'medium', 'inventory_turnover', 6, 8, 12, 16, 'Inventory Management 2024'),
            BenchmarkData('ecommerce', 'large', 'inventory_turnover', 8, 12, 18, 24, 'Inventory Management 2024'),
        ]
        
        for benchmark in ecommerce_benchmarks:
            key = f"{benchmark.industry}_{benchmark.company_size}_{benchmark.metric}"
            benchmarks[key] = benchmark
            
        return benchmarks
    
    def _load_optimization_rules(self) -> Dict[str, Dict]:
        """Load optimization rules and heuristics"""
        return {
            'labor_optimization': {
                'automation_threshold': 0.3,  # If labor > 30% of revenue, consider automation
                'max_reduction': 0.4,  # Maximum 40% reduction possible
                'implementation_cost_factor': 0.15,  # 15% of current labor cost
                'payback_threshold_months': 18
            },
            'shipping_optimization': {
                'bulk_shipping_threshold': 1000,  # Monthly orders for bulk rates
                'carrier_optimization_savings': 0.15,  # 15% average savings from carrier optimization
                'zone_skipping_savings': 0.12,  # 12% savings from zone skipping
                'packaging_optimization': 0.08  # 8% savings from packaging optimization
            },
            'error_reduction': {
                'automation_impact': 0.7,  # 70% error reduction from automation
                'training_impact': 0.3,  # 30% error reduction from training
                'system_integration_impact': 0.5,  # 50% error reduction from better integration
                'quality_control_impact': 0.4  # 40% error reduction from QC processes
            },
            'inventory_optimization': {
                'demand_forecasting_improvement': 0.25,  # 25% inventory reduction from better forecasting
                'abc_analysis_impact': 0.15,  # 15% reduction from ABC analysis
                'supplier_optimization': 0.12,  # 12% reduction from supplier optimization
                'safety_stock_optimization': 0.18  # 18% reduction from safety stock optimization
            }
        }
    
    def _ensure_models_loaded(self) -> None:
        """Ensure ML models are loaded (lazy loading)"""
        if self.ml_models is None:
            if CostOptimizer._ml_models_cache is None:
                self._setup_ml_models()
            else:
                self.ml_models = CostOptimizer._ml_models_cache
    
    def _setup_ml_models(self) -> None:
        """Setup machine learning models for optimization"""
        # Check if models are already trained at class level
        if CostOptimizer._models_trained and CostOptimizer._ml_models_cache is not None:
            self.ml_models = CostOptimizer._ml_models_cache
            return
        
        # Initialize models (in production, these would be pre-trained)
        self.ml_models = {
            'cost_predictor': RandomForestRegressor(n_estimators=50, random_state=42, n_jobs=-1),  # Reduced estimators, parallel
            'savings_estimator': RandomForestRegressor(n_estimators=50, random_state=42, n_jobs=-1),
            'risk_classifier': KMeans(n_clusters=3, random_state=42, n_init=5)  # Reduced iterations
        }
        
        # Train with synthetic data (in production, use historical data)
        self._train_models_with_synthetic_data()
        
        # Cache models at class level
        CostOptimizer._ml_models_cache = self.ml_models
        CostOptimizer._models_trained = True
    
    def _train_models_with_synthetic_data(self) -> None:
        """Train ML models with synthetic data"""
        # Generate synthetic training data (reduced sample size for speed)
        np.random.seed(42)
        n_samples = 500  # Reduced from 1000 for faster training
        
        # Features: [annual_revenue, monthly_orders, avg_order_value, current_labor_ratio, 
        #           current_shipping_ratio, current_error_rate, inventory_turnover]
        features = np.random.rand(n_samples, 7)
        features[:, 0] *= 5000000  # annual_revenue: 0-5M
        features[:, 1] *= 10000    # monthly_orders: 0-10K
        features[:, 2] *= 100      # avg_order_value: 0-100
        features[:, 3] *= 0.5      # labor_ratio: 0-50%
        features[:, 4] *= 0.3      # shipping_ratio: 0-30%
        features[:, 5] *= 0.15     # error_rate: 0-15%
        features[:, 6] *= 20       # inventory_turnover: 0-20
        
        # Target: potential_savings_percentage
        targets = (0.1 + 0.3 * features[:, 3] + 0.2 * features[:, 4] + 
                  0.25 * features[:, 5] + 0.1 * (12 / (features[:, 6] + 1)))
        
        # Add some noise
        targets += np.random.normal(0, 0.05, n_samples)
        targets = np.clip(targets, 0, 0.6)  # Clip to realistic range
        
        # Split and train
        X_train, X_test, y_train, y_test = train_test_split(features, targets, test_size=0.2, random_state=42)
        
        # Train cost predictor
        self.ml_models['cost_predictor'].fit(X_train, y_train)
        
        # Train savings estimator (slightly different target)
        savings_targets = targets * features[:, 0] / 12  # Monthly savings amount
        y_savings_train = savings_targets[:len(y_train)]
        self.ml_models['savings_estimator'].fit(X_train, y_savings_train)
        
        # Train risk classifier
        risk_features = np.column_stack([features[:, 0], targets])  # Revenue and potential savings
        self.ml_models['risk_classifier'].fit(risk_features)
    
    def analyze_and_optimize(self, roi_data: Dict[str, Any]) -> OptimizationReport:
        """
        Analyze costs and generate optimization recommendations
        
        Args:
            roi_data: ROI calculation results
            
        Returns:
            Complete optimization report
        """
        try:
            # Ensure models are loaded (lazy loading)
            if self.lazy_load:
                self._ensure_models_loaded()
            
            # Extract current metrics
            current_metrics = self._extract_metrics(roi_data)
            
            # Generate recommendations using multiple approaches
            ml_recommendations = self._generate_ml_recommendations(current_metrics)
            heuristic_recommendations = self._generate_heuristic_recommendations(current_metrics)
            benchmark_recommendations = self._generate_benchmark_recommendations(current_metrics)
            
            # Combine and rank recommendations
            all_recommendations = ml_recommendations + heuristic_recommendations + benchmark_recommendations
            ranked_recommendations = self._rank_recommendations(all_recommendations)
            
            # Create optimization report
            report = OptimizationReport(
                company_name=roi_data.get('inputs', {}).get('company_name', 'Client'),
                analysis_date=datetime.now(),
                current_metrics=current_metrics,
                recommendations=ranked_recommendations,
                total_potential_savings=sum(rec.potential_savings for rec in ranked_recommendations),
                implementation_timeline=self._generate_implementation_timeline(ranked_recommendations),
                risk_assessment=self._assess_risks(ranked_recommendations, current_metrics),
                benchmark_comparison=self._compare_to_benchmarks(current_metrics),
                priority_matrix=self._create_priority_matrix(ranked_recommendations)
            )
            
            return report
            
        except Exception as e:
            logger.error(f"Error in cost optimization analysis: {str(e)}")
            raise
    
    def _extract_metrics(self, roi_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract key metrics from ROI data"""
        inputs = roi_data.get('inputs', {})
        
        annual_revenue = inputs.get('annual_revenue', 0)
        monthly_orders = inputs.get('monthly_orders', 0)
        avg_order_value = inputs.get('avg_order_value', 0)
        
        # Convert monthly costs to ratios
        labor_monthly = inputs.get('labor_costs', 0)
        shipping_monthly = inputs.get('shipping_costs', 0)
        error_monthly = inputs.get('error_costs', 0)
        inventory_monthly = inputs.get('inventory_costs', 0)
        
        monthly_revenue = annual_revenue / 12 if annual_revenue > 0 else 1
        
        return {
            'annual_revenue': annual_revenue,
            'monthly_revenue': monthly_revenue,
            'monthly_orders': monthly_orders,
            'avg_order_value': avg_order_value,
            'labor_costs_monthly': labor_monthly,
            'shipping_costs_monthly': shipping_monthly,
            'error_costs_monthly': error_monthly,
            'inventory_costs_monthly': inventory_monthly,
            'labor_cost_ratio': labor_monthly / monthly_revenue,
            'shipping_cost_ratio': shipping_monthly / monthly_revenue,
            'error_cost_ratio': error_monthly / monthly_revenue,
            'inventory_cost_ratio': inventory_monthly / monthly_revenue,
            'total_cost_ratio': (labor_monthly + shipping_monthly + error_monthly + inventory_monthly) / monthly_revenue,
            'estimated_inventory_turnover': monthly_orders * avg_order_value / (inventory_monthly * 12) if inventory_monthly > 0 else 6,
            'estimated_error_rate': error_monthly / monthly_revenue,
            'company_size': self._determine_company_size(annual_revenue)
        }
    
    def _determine_company_size(self, annual_revenue: float) -> str:
        """Determine company size category"""
        if annual_revenue < 1000000:
            return 'small'
        elif annual_revenue < 10000000:
            return 'medium'
        else:
            return 'large'
    
    def _generate_ml_recommendations(self, metrics: Dict[str, float]) -> List[OptimizationRecommendation]:
        """Generate recommendations using ML models"""
        recommendations = []
        
        try:
            # Prepare features for ML models
            features = np.array([[
                metrics['annual_revenue'],
                metrics['monthly_orders'],
                metrics['avg_order_value'],
                metrics['labor_cost_ratio'],
                metrics['shipping_cost_ratio'],
                metrics['estimated_error_rate'],
                metrics['estimated_inventory_turnover']
            ]])
            
            # Predict potential savings
            predicted_savings_ratio = self.ml_models['cost_predictor'].predict(features)[0]
            predicted_monthly_savings = self.ml_models['savings_estimator'].predict(features)[0]
            
            # Determine risk level
            risk_features = np.array([[metrics['annual_revenue'], predicted_savings_ratio]])
            risk_cluster = self.ml_models['risk_classifier'].predict(risk_features)[0]
            risk_levels = ['low', 'medium', 'high']
            risk_level = risk_levels[risk_cluster]
            
            # Generate ML-based recommendation
            if predicted_savings_ratio > 0.1:  # If potential savings > 10%
                recommendations.append(OptimizationRecommendation(
                    category='ml_optimization',
                    current_value=metrics['total_cost_ratio'] * metrics['monthly_revenue'] * 12,
                    optimized_value=(metrics['total_cost_ratio'] - predicted_savings_ratio) * metrics['monthly_revenue'] * 12,
                    potential_savings=predicted_monthly_savings * 12,
                    confidence_score=0.75,  # ML model confidence
                    priority='high' if predicted_savings_ratio > 0.2 else 'medium',
                    description=f"Machine learning analysis identified {predicted_savings_ratio*100:.1f}% potential cost reduction through integrated optimization approaches.",
                    implementation_difficulty='moderate',
                    timeframe='short-term',
                    risk_level=risk_level,
                    supporting_data={
                        'ml_model_confidence': 0.75,
                        'predicted_savings_ratio': predicted_savings_ratio,
                        'feature_importance': 'labor_costs, error_reduction, shipping_optimization'
                    }
                ))
                
        except Exception as e:
            logger.warning(f"ML recommendation generation failed: {str(e)}")
            
        return recommendations
    
    def _generate_heuristic_recommendations(self, metrics: Dict[str, float]) -> List[OptimizationRecommendation]:
        """Generate recommendations using business heuristics"""
        recommendations = []
        rules = self.optimization_rules
        
        # Labor cost optimization
        if metrics['labor_cost_ratio'] > rules['labor_optimization']['automation_threshold']:
            max_reduction = rules['labor_optimization']['max_reduction']
            potential_reduction = min(max_reduction, metrics['labor_cost_ratio'] * 0.6)  # Be conservative
            annual_savings = potential_reduction * metrics['annual_revenue']
            
            recommendations.append(OptimizationRecommendation(
                category='labor_optimization',
                current_value=metrics['labor_costs_monthly'] * 12,
                optimized_value=metrics['labor_costs_monthly'] * 12 * (1 - potential_reduction),
                potential_savings=annual_savings,
                confidence_score=0.8,
                priority='high' if potential_reduction > 0.2 else 'medium',
                description=f"Automation and process optimization can reduce labor costs by {potential_reduction*100:.1f}% through workflow streamlining, task automation, and improved efficiency.",
                implementation_difficulty='moderate',
                timeframe='short-term',
                risk_level='medium',
                supporting_data={
                    'current_labor_ratio': metrics['labor_cost_ratio'],
                    'industry_threshold': rules['labor_optimization']['automation_threshold'],
                    'automation_technologies': ['workflow_automation', 'rpa', 'ai_assistants']
                }
            ))
        
        # Shipping cost optimization
        if metrics['monthly_orders'] > rules['shipping_optimization']['bulk_shipping_threshold']:
            carrier_savings = rules['shipping_optimization']['carrier_optimization_savings']
            annual_shipping = metrics['shipping_costs_monthly'] * 12
            potential_savings = annual_shipping * carrier_savings
            
            recommendations.append(OptimizationRecommendation(
                category='shipping_optimization',
                current_value=annual_shipping,
                optimized_value=annual_shipping * (1 - carrier_savings),
                potential_savings=potential_savings,
                confidence_score=0.85,
                priority='high',
                description=f"Shipping optimization through carrier negotiation, zone skipping, and bulk rates can reduce shipping costs by {carrier_savings*100:.1f}%.",
                implementation_difficulty='easy',
                timeframe='immediate',
                risk_level='low',
                supporting_data={
                    'monthly_orders': metrics['monthly_orders'],
                    'bulk_threshold': rules['shipping_optimization']['bulk_shipping_threshold'],
                    'optimization_methods': ['carrier_negotiation', 'zone_skipping', 'packaging_optimization']
                }
            ))
        
        # Error reduction
        if metrics['estimated_error_rate'] > 0.03:  # If error rate > 3%
            error_reduction = rules['error_reduction']['automation_impact']
            current_error_costs = metrics['error_costs_monthly'] * 12
            potential_savings = current_error_costs * error_reduction
            
            recommendations.append(OptimizationRecommendation(
                category='error_reduction',
                current_value=current_error_costs,
                optimized_value=current_error_costs * (1 - error_reduction),
                potential_savings=potential_savings,
                confidence_score=0.9,
                priority='high',
                description=f"Quality control improvements and automation can reduce error costs by {error_reduction*100:.1f}% through better processes and validation.",
                implementation_difficulty='moderate',
                timeframe='short-term',
                risk_level='low',
                supporting_data={
                    'current_error_rate': metrics['estimated_error_rate'],
                    'target_error_rate': metrics['estimated_error_rate'] * (1 - error_reduction),
                    'improvement_methods': ['automation', 'quality_control', 'training']
                }
            ))
        
        # Inventory optimization
        if metrics['estimated_inventory_turnover'] < 6:  # Below average turnover
            improvement = rules['inventory_optimization']['demand_forecasting_improvement']
            current_inventory_costs = metrics['inventory_costs_monthly'] * 12
            potential_savings = current_inventory_costs * improvement
            
            recommendations.append(OptimizationRecommendation(
                category='inventory_optimization',
                current_value=current_inventory_costs,
                optimized_value=current_inventory_costs * (1 - improvement),
                potential_savings=potential_savings,
                confidence_score=0.7,
                priority='medium',
                description=f"Inventory optimization through better demand forecasting and ABC analysis can reduce inventory costs by {improvement*100:.1f}%.",
                implementation_difficulty='moderate',
                timeframe='long-term',
                risk_level='medium',
                supporting_data={
                    'current_turnover': metrics['estimated_inventory_turnover'],
                    'target_turnover': metrics['estimated_inventory_turnover'] * 1.5,
                    'optimization_methods': ['demand_forecasting', 'abc_analysis', 'safety_stock_optimization']
                }
            ))
        
        return recommendations
    
    def _generate_benchmark_recommendations(self, metrics: Dict[str, float]) -> List[OptimizationRecommendation]:
        """Generate recommendations based on industry benchmarks"""
        recommendations = []
        company_size = metrics['company_size']
        
        # Compare against benchmarks
        for metric_name in ['labor_cost_ratio', 'shipping_cost_ratio', 'error_rate']:
            benchmark_key = f"{self.industry}_{company_size}_{metric_name}"
            
            if benchmark_key in self.benchmark_data:
                benchmark = self.benchmark_data[benchmark_key]
                current_value = metrics.get(metric_name, 0)
                
                if metric_name == 'error_rate':
                    current_value = metrics['estimated_error_rate']
                
                # If current performance is worse than 75th percentile, recommend improvement
                if current_value > benchmark.p75:
                    target_value = benchmark.p50  # Target median performance
                    improvement_ratio = (current_value - target_value) / current_value
                    
                    if metric_name == 'labor_cost_ratio':
                        annual_savings = improvement_ratio * metrics['labor_costs_monthly'] * 12
                        category = 'benchmark_labor'
                    elif metric_name == 'shipping_cost_ratio':
                        annual_savings = improvement_ratio * metrics['shipping_costs_monthly'] * 12
                        category = 'benchmark_shipping'
                    else:  # error_rate
                        annual_savings = improvement_ratio * metrics['error_costs_monthly'] * 12
                        category = 'benchmark_quality'
                    
                    recommendations.append(OptimizationRecommendation(
                        category=category,
                        current_value=current_value,
                        optimized_value=target_value,
                        potential_savings=annual_savings,
                        confidence_score=0.85,
                        priority='high' if current_value > benchmark.p90 else 'medium',
                        description=f"Industry benchmarking shows {improvement_ratio*100:.1f}% improvement opportunity to reach median industry performance in {metric_name.replace('_', ' ')}.",
                        implementation_difficulty='moderate',
                        timeframe='short-term',
                        risk_level='low',
                        supporting_data={
                            'current_percentile': self._calculate_percentile(current_value, benchmark),
                            'industry_median': benchmark.p50,
                            'top_quartile': benchmark.p25,
                            'benchmark_source': benchmark.source
                        }
                    ))
        
        return recommendations
    
    def _calculate_percentile(self, value: float, benchmark: BenchmarkData) -> str:
        """Calculate which percentile the current value falls into"""
        if value <= benchmark.p25:
            return '< 25th percentile (Top Quartile)'
        elif value <= benchmark.p50:
            return '25th-50th percentile (Above Average)'
        elif value <= benchmark.p75:
            return '50th-75th percentile (Below Average)'
        else:
            return '> 75th percentile (Bottom Quartile)'
    
    def _rank_recommendations(self, recommendations: List[OptimizationRecommendation]) -> List[OptimizationRecommendation]:
        """Rank recommendations by impact and feasibility"""
        def recommendation_score(rec: OptimizationRecommendation) -> float:
            # Weight factors
            savings_weight = 0.4
            confidence_weight = 0.2
            difficulty_weight = 0.2  # Lower difficulty = higher score
            risk_weight = 0.2  # Lower risk = higher score
            
            # Normalize savings (0-1 scale)
            max_savings = max(r.potential_savings for r in recommendations) if recommendations else 1
            savings_score = rec.potential_savings / max_savings if max_savings > 0 else 0
            
            # Difficulty score (easy=1, moderate=0.7, difficult=0.3)
            difficulty_scores = {'easy': 1.0, 'moderate': 0.7, 'difficult': 0.3}
            difficulty_score = difficulty_scores.get(rec.implementation_difficulty, 0.5)
            
            # Risk score (low=1, medium=0.7, high=0.3)
            risk_scores = {'low': 1.0, 'medium': 0.7, 'high': 0.3}
            risk_score = risk_scores.get(rec.risk_level, 0.5)
            
            return (savings_score * savings_weight + 
                   rec.confidence_score * confidence_weight +
                   difficulty_score * difficulty_weight +
                   risk_score * risk_weight)
        
        return sorted(recommendations, key=recommendation_score, reverse=True)
    
    def _generate_implementation_timeline(self, recommendations: List[OptimizationRecommendation]) -> Dict[str, List[str]]:
        """Generate implementation timeline"""
        timeline = {
            'immediate': [],
            'short-term': [],
            'long-term': []
        }
        
        for rec in recommendations:
            timeline[rec.timeframe].append(f"{rec.category}: {rec.description[:100]}...")
        
        return timeline
    
    def _assess_risks(self, recommendations: List[OptimizationRecommendation], metrics: Dict[str, float]) -> Dict[str, Any]:
        """Assess implementation risks"""
        risk_counts = {'low': 0, 'medium': 0, 'high': 0}
        for rec in recommendations:
            risk_counts[rec.risk_level] += 1
        
        total_savings = sum(rec.potential_savings for rec in recommendations)
        revenue_impact_ratio = total_savings / metrics['annual_revenue'] if metrics['annual_revenue'] > 0 else 0
        
        overall_risk = 'low'
        if revenue_impact_ratio > 0.15 or risk_counts['high'] > 2:
            overall_risk = 'high'
        elif revenue_impact_ratio > 0.08 or risk_counts['medium'] > 3:
            overall_risk = 'medium'
        
        return {
            'overall_risk_level': overall_risk,
            'risk_distribution': risk_counts,
            'revenue_impact_ratio': revenue_impact_ratio,
            'mitigation_required': overall_risk in ['medium', 'high'],
            'recommended_pilot_approach': overall_risk == 'high'
        }
    
    def _compare_to_benchmarks(self, metrics: Dict[str, float]) -> Dict[str, Any]:
        """Compare current performance to industry benchmarks"""
        company_size = metrics['company_size']
        comparisons = {}
        
        metrics_to_compare = [
            ('labor_cost_ratio', 'Labor Cost Ratio'),
            ('shipping_cost_ratio', 'Shipping Cost Ratio'),
            ('error_rate', 'Error Rate')
        ]
        
        for metric_key, metric_name in metrics_to_compare:
            benchmark_key = f"{self.industry}_{company_size}_{metric_key}"
            
            if benchmark_key in self.benchmark_data:
                benchmark = self.benchmark_data[benchmark_key]
                current_value = metrics.get(metric_key, 0)
                
                if metric_key == 'error_rate':
                    current_value = metrics['estimated_error_rate']
                
                comparisons[metric_name] = {
                    'current_value': current_value,
                    'industry_median': benchmark.p50,
                    'top_quartile': benchmark.p25,
                    'bottom_quartile': benchmark.p75,
                    'percentile_position': self._calculate_percentile(current_value, benchmark),
                    'improvement_to_median': max(0, current_value - benchmark.p50),
                    'improvement_to_top_quartile': max(0, current_value - benchmark.p25)
                }
        
        return comparisons
    
    def _create_priority_matrix(self, recommendations: List[OptimizationRecommendation]) -> Dict[str, List[str]]:
        """Create priority matrix for recommendations"""
        matrix = {
            'quick_wins': [],      # High impact, easy implementation
            'major_projects': [],  # High impact, difficult implementation
            'fill_ins': [],        # Low impact, easy implementation
            'questionable': []     # Low impact, difficult implementation
        }
        
        for rec in recommendations:
            is_high_impact = rec.potential_savings > (sum(r.potential_savings for r in recommendations) / len(recommendations))
            is_easy_implementation = rec.implementation_difficulty == 'easy'
            
            if is_high_impact and is_easy_implementation:
                matrix['quick_wins'].append(rec.category)
            elif is_high_impact and not is_easy_implementation:
                matrix['major_projects'].append(rec.category)
            elif not is_high_impact and is_easy_implementation:
                matrix['fill_ins'].append(rec.category)
            else:
                matrix['questionable'].append(rec.category)
        
        return matrix
    
    def generate_optimization_report_text(self, report: OptimizationReport) -> str:
        """Generate human-readable optimization report"""
        text = f"""
COST OPTIMIZATION ANALYSIS REPORT
==================================

Company: {report.company_name}
Analysis Date: {report.analysis_date.strftime('%B %d, %Y')}
Industry: {self.industry.title()}

EXECUTIVE SUMMARY
-----------------
Total Potential Annual Savings: ${report.total_potential_savings:,.2f}
Number of Optimization Opportunities: {len(report.recommendations)}
Overall Risk Level: {report.risk_assessment['overall_risk_level'].title()}

TOP RECOMMENDATIONS
------------------
"""
        
        # Top 5 recommendations
        for i, rec in enumerate(report.recommendations[:5], 1):
            text += f"""
{i}. {rec.category.replace('_', ' ').title()} ({rec.priority.title()} Priority)
   Potential Savings: ${rec.potential_savings:,.2f} annually
   Confidence: {rec.confidence_score*100:.0f}%
   Implementation: {rec.implementation_difficulty.title()} | Risk: {rec.risk_level.title()}
   {rec.description}
"""
        
        text += f"""

IMPLEMENTATION ROADMAP
----------------------
Immediate Actions ({len(report.implementation_timeline['immediate'])} items):
"""
        for item in report.implementation_timeline['immediate'][:3]:
            text += f"• {item}\n"
        
        text += f"""
Short-term Projects ({len(report.implementation_timeline['short-term'])} items):
"""
        for item in report.implementation_timeline['short-term'][:3]:
            text += f"• {item}\n"
        
        text += f"""
Long-term Initiatives ({len(report.implementation_timeline['long-term'])} items):
"""
        for item in report.implementation_timeline['long-term'][:3]:
            text += f"• {item}\n"
        
        text += f"""

BENCHMARK COMPARISON
--------------------
"""
        for metric, data in report.benchmark_comparison.items():
            text += f"{metric}: Currently {data['percentile_position']}\n"
            text += f"  Improvement to median: {data['improvement_to_median']:.3f}\n"
        
        text += f"""

RISK ASSESSMENT
---------------
Overall Risk: {report.risk_assessment['overall_risk_level'].title()}
Revenue Impact: {report.risk_assessment['revenue_impact_ratio']*100:.1f}% of annual revenue
Risk Distribution: {report.risk_assessment['risk_distribution']}
"""
        
        if report.risk_assessment['mitigation_required']:
            text += "⚠️  Risk mitigation strategies recommended before implementation.\n"
        
        if report.risk_assessment['recommended_pilot_approach']:
            text += "🧪 Pilot program approach recommended for high-risk initiatives.\n"
        
        return text
    
    def get_optimization_summary(self, report: OptimizationReport) -> Dict[str, Any]:
        """Get condensed optimization summary for API responses"""
        return {
            'total_potential_savings': report.total_potential_savings,
            'savings_percentage': (report.total_potential_savings / (report.current_metrics['annual_revenue'] or 1)) * 100,
            'top_recommendations': [
                {
                    'category': rec.category,
                    'savings': rec.potential_savings,
                    'priority': rec.priority,
                    'description': rec.description[:100] + '...' if len(rec.description) > 100 else rec.description
                }
                for rec in report.recommendations[:3]
            ],
            'risk_level': report.risk_assessment['overall_risk_level'],
            'implementation_complexity': self._assess_complexity(report.recommendations),
            'quick_wins_count': len(report.priority_matrix['quick_wins']),
            'benchmark_position': self._get_benchmark_summary(report.benchmark_comparison)
        }
    
    def _assess_complexity(self, recommendations: List[OptimizationRecommendation]) -> str:
        """Assess overall implementation complexity"""
        difficulty_scores = {'easy': 1, 'moderate': 2, 'difficult': 3}
        avg_difficulty = sum(difficulty_scores.get(rec.implementation_difficulty, 2) for rec in recommendations) / len(recommendations)
        
        if avg_difficulty < 1.5:
            return 'low'
        elif avg_difficulty < 2.5:
            return 'moderate'
        else:
            return 'high'
    
    def _get_benchmark_summary(self, benchmark_comparison: Dict[str, Any]) -> str:
        """Get summary of benchmark position"""
        positions = [data['percentile_position'] for data in benchmark_comparison.values()]
        
        if any('Top Quartile' in pos for pos in positions):
            return 'above_average'
        elif any('Bottom Quartile' in pos for pos in positions):
            return 'below_average'
        else:
            return 'average'


# Example usage
if __name__ == '__main__':
    # Sample ROI data for testing
    sample_roi_data = {
        'inputs': {
            'company_name': 'Acme E-commerce Ltd.',
            'annual_revenue': 2000000,
            'monthly_orders': 5000,
            'avg_order_value': 33.33,
            'labor_costs': 8000,
            'shipping_costs': 5000,
            'error_costs': 2000,
            'inventory_costs': 3000,
            'service_investment': 50000
        },
        'roi_metrics': {
            'first_year_roi': 0.35,
            'annual_savings': 75000,
            'monthly_savings': 6250,
            'payback_period_months': 8.0
        }
    }
    
    # Create optimizer and analyze
    optimizer = CostOptimizer(industry='ecommerce')
    report = optimizer.analyze_and_optimize(sample_roi_data)
    
    # Generate report
    report_text = optimizer.generate_optimization_report_text(report)
    print(report_text)
    
    # Get summary
    summary = optimizer.get_optimization_summary(report)
    print("\nOptimization Summary:")
    print(json.dumps(summary, indent=2))
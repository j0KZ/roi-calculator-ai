#!/usr/bin/env python3
"""
Metrics Aggregator - Calculates real metrics from historical data
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
import statistics

logger = logging.getLogger(__name__)


class MetricsAggregator:
    """Aggregates and calculates real metrics from calculation history"""
    
    def __init__(self, history_manager=None):
        """
        Initialize metrics aggregator
        
        Args:
            history_manager: Optional HistoryManager instance
        """
        if history_manager is None:
            from history_manager import HistoryManager
            self.history = HistoryManager()
        else:
            self.history = history_manager
    
    def get_dashboard_metrics(self) -> Dict:
        """
        Get real metrics for dashboard display
        
        Returns:
            Dictionary with calculated metrics
        """
        # Get all ROI calculations from history
        roi_calculations = self.history.get_recent_calculations(
            limit=1000, 
            calculation_type='roi'
        )
        
        # If no data, return zeros with indicators
        if not roi_calculations:
            return {
                'avg_roi': 0,
                'avg_roi_display': "Sin datos",
                'avg_payback': 0,
                'avg_payback_display': "Sin datos",
                'avg_monthly_savings': 0,
                'avg_monthly_savings_display': "Sin datos",
                'total_clients': 0,
                'total_clients_display': "0",
                'monthly_growth': 0,
                'monthly_growth_display': "Sin datos",
                'has_data': False
            }
        
        # Calculate average ROI
        roi_values = []
        payback_values = []
        savings_values = []
        
        for calc in roi_calculations:
            results = calc.get('results', {})
            
            # Extract ROI percentage
            roi_pct = results.get('roi_percentage', 0)
            if roi_pct > 0:
                roi_values.append(roi_pct)
            
            # Extract payback period
            payback = results.get('payback_period_months', 0)
            if payback > 0:
                payback_values.append(payback)
            
            # Extract monthly savings
            savings = results.get('savings', {})
            annual_savings = savings.get('annual_savings', 0)
            if annual_savings > 0:
                monthly_savings = annual_savings / 12
                savings_values.append(monthly_savings)
        
        # Calculate averages
        avg_roi = statistics.mean(roi_values) if roi_values else 0
        avg_payback = statistics.median(payback_values) if payback_values else 0
        avg_monthly_savings = statistics.mean(savings_values) if savings_values else 0
        
        # Count unique clients (based on metadata)
        unique_clients = set()
        for calc in roi_calculations:
            metadata = calc.get('metadata', {})
            client = metadata.get('company_name') or metadata.get('client_id')
            if client:
                unique_clients.add(client)
        
        total_clients = len(unique_clients)
        
        # Calculate monthly growth
        now = datetime.now()
        last_month = now - timedelta(days=30)
        this_month_count = 0
        last_month_count = 0
        
        for calc in roi_calculations:
            calc_date = datetime.fromisoformat(calc['timestamp'])
            if calc_date >= last_month:
                this_month_count += 1
            elif calc_date >= last_month - timedelta(days=30):
                last_month_count += 1
        
        monthly_growth = 0
        if last_month_count > 0:
            monthly_growth = ((this_month_count - last_month_count) / last_month_count) * 100
        elif this_month_count > 0:
            monthly_growth = 100  # New this month
        
        # Format values for display
        return {
            'avg_roi': avg_roi,
            'avg_roi_display': f"{avg_roi:.0f}%" if avg_roi > 0 else "Sin datos",
            'avg_payback': avg_payback,
            'avg_payback_display': f"{avg_payback:.1f} meses" if avg_payback > 0 else "Sin datos",
            'avg_monthly_savings': avg_monthly_savings,
            'avg_monthly_savings_display': self._format_currency(avg_monthly_savings) if avg_monthly_savings > 0 else "Sin datos",
            'total_clients': total_clients,
            'total_clients_display': str(total_clients) if total_clients > 0 else "0",
            'monthly_growth': monthly_growth,
            'monthly_growth_display': f"+{monthly_growth:.0f}% este mes" if monthly_growth > 0 else f"{monthly_growth:.0f}% este mes" if monthly_growth < 0 else "Sin cambios",
            'has_data': len(roi_calculations) > 0
        }
    
    def get_historical_trends(self, days: int = 30) -> Dict:
        """
        Get historical trend data for charts
        
        Args:
            days: Number of days to look back
            
        Returns:
            Dictionary with trend data
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get all calculations in date range
        all_calcs = self.history.get_recent_calculations(limit=10000)
        
        # Filter by date
        filtered = []
        for calc in all_calcs:
            calc_date = datetime.fromisoformat(calc['timestamp'])
            if start_date <= calc_date <= end_date:
                filtered.append(calc)
        
        # Group by day
        daily_metrics = {}
        for calc in filtered:
            calc_date = datetime.fromisoformat(calc['timestamp']).date()
            date_str = calc_date.isoformat()
            
            if date_str not in daily_metrics:
                daily_metrics[date_str] = {
                    'roi_values': [],
                    'savings_values': [],
                    'count': 0
                }
            
            results = calc.get('results', {})
            roi = results.get('roi_percentage', 0)
            savings = results.get('savings', {}).get('annual_savings', 0)
            
            if roi > 0:
                daily_metrics[date_str]['roi_values'].append(roi)
            if savings > 0:
                daily_metrics[date_str]['savings_values'].append(savings)
            daily_metrics[date_str]['count'] += 1
        
        # Calculate daily averages
        trend_data = {
            'dates': [],
            'avg_roi': [],
            'total_savings': [],
            'calculation_count': []
        }
        
        for date_str in sorted(daily_metrics.keys()):
            metrics = daily_metrics[date_str]
            trend_data['dates'].append(date_str)
            
            avg_roi = statistics.mean(metrics['roi_values']) if metrics['roi_values'] else 0
            trend_data['avg_roi'].append(avg_roi)
            
            total_savings = sum(metrics['savings_values'])
            trend_data['total_savings'].append(total_savings)
            
            trend_data['calculation_count'].append(metrics['count'])
        
        return trend_data
    
    def get_top_performers(self, limit: int = 5) -> List[Dict]:
        """
        Get top performing calculations by ROI
        
        Args:
            limit: Number of top performers to return
            
        Returns:
            List of top performing calculations
        """
        all_calcs = self.history.get_recent_calculations(
            limit=1000,
            calculation_type='roi'
        )
        
        # Sort by ROI
        sorted_calcs = []
        for calc in all_calcs:
            roi = calc.get('results', {}).get('roi_percentage', 0)
            if roi > 0:
                sorted_calcs.append({
                    'id': calc['id'],
                    'timestamp': calc['timestamp'],
                    'roi': roi,
                    'company': calc.get('metadata', {}).get('company_name', 'Sin nombre'),
                    'savings': calc.get('results', {}).get('savings', {}).get('annual_savings', 0),
                    'payback': calc.get('results', {}).get('payback_period_months', 0)
                })
        
        sorted_calcs.sort(key=lambda x: x['roi'], reverse=True)
        
        return sorted_calcs[:limit]
    
    def get_industry_breakdown(self) -> Dict:
        """
        Get breakdown of calculations by industry
        
        Returns:
            Dictionary with industry statistics
        """
        all_calcs = self.history.get_recent_calculations(limit=1000)
        
        industry_stats = {}
        
        for calc in all_calcs:
            inputs = calc.get('inputs', {})
            industry = inputs.get('industry', 'Unknown')
            
            if industry not in industry_stats:
                industry_stats[industry] = {
                    'count': 0,
                    'roi_values': [],
                    'savings_values': []
                }
            
            industry_stats[industry]['count'] += 1
            
            results = calc.get('results', {})
            roi = results.get('roi_percentage', 0)
            if roi > 0:
                industry_stats[industry]['roi_values'].append(roi)
            
            savings = results.get('savings', {}).get('annual_savings', 0)
            if savings > 0:
                industry_stats[industry]['savings_values'].append(savings)
        
        # Calculate averages for each industry
        for industry in industry_stats:
            stats = industry_stats[industry]
            stats['avg_roi'] = statistics.mean(stats['roi_values']) if stats['roi_values'] else 0
            stats['avg_savings'] = statistics.mean(stats['savings_values']) if stats['savings_values'] else 0
            # Remove raw lists to clean up output
            del stats['roi_values']
            del stats['savings_values']
        
        return industry_stats
    
    def _format_currency(self, amount: float) -> str:
        """
        Format amount as Chilean Peso currency
        
        Args:
            amount: Amount to format
            
        Returns:
            Formatted currency string
        """
        if amount >= 1_000_000:
            return f"${amount/1_000_000:.1f}M CLP"
        elif amount >= 1_000:
            return f"${amount/1_000:.0f}K CLP"
        else:
            return f"${amount:.0f} CLP"
    
    def get_summary_statistics(self) -> Dict:
        """
        Get comprehensive summary statistics
        
        Returns:
            Dictionary with summary statistics
        """
        all_calcs = self.history.get_recent_calculations(limit=10000)
        
        if not all_calcs:
            return {
                'total_calculations': 0,
                'roi_calculations': 0,
                'tax_calculations': 0,
                'assessment_calculations': 0,
                'total_value_analyzed': 0,
                'total_savings_identified': 0,
                'avg_improvement': 0
            }
        
        # Count by type
        type_counts = {}
        total_investment = 0
        total_savings = 0
        improvement_percentages = []
        
        for calc in all_calcs:
            calc_type = calc.get('type', 'unknown')
            type_counts[calc_type] = type_counts.get(calc_type, 0) + 1
            
            # Sum investments and savings
            inputs = calc.get('inputs', {})
            results = calc.get('results', {})
            
            investment = inputs.get('investment_clp', 0) or inputs.get('service_investment', 0)
            if investment > 0:
                total_investment += investment
            
            annual_savings = results.get('savings', {}).get('annual_savings', 0)
            if annual_savings > 0:
                total_savings += annual_savings
            
            # Calculate improvement percentage
            roi = results.get('roi_percentage', 0)
            if roi > 0:
                improvement_percentages.append(roi)
        
        avg_improvement = statistics.mean(improvement_percentages) if improvement_percentages else 0
        
        return {
            'total_calculations': len(all_calcs),
            'roi_calculations': type_counts.get('roi', 0),
            'tax_calculations': type_counts.get('tax', 0),
            'assessment_calculations': type_counts.get('assessment', 0),
            'total_value_analyzed': total_investment,
            'total_value_analyzed_display': self._format_currency(total_investment),
            'total_savings_identified': total_savings,
            'total_savings_identified_display': self._format_currency(total_savings),
            'avg_improvement': avg_improvement,
            'avg_improvement_display': f"{avg_improvement:.1f}%"
        }


def main():
    """Test the metrics aggregator"""
    aggregator = MetricsAggregator()
    
    # Get dashboard metrics
    metrics = aggregator.get_dashboard_metrics()
    print("Dashboard Metrics:")
    print(json.dumps(metrics, indent=2))
    
    # Get summary statistics
    summary = aggregator.get_summary_statistics()
    print("\nSummary Statistics:")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
"""
ROI Result Adapter - Converts new result format to expected format
"""

def adapt_roi_results(results):
    """
    Convert new ROI calculator results to expected format for database and pages
    
    Args:
        results: Results from EnhancedROICalculator.calculate_roi()
    
    Returns:
        dict: Standardized results with expected keys
    """
    if not results or not results.get('success'):
        return {
            'roi_percentage': 0,
            'payback_months': 0,
            'total_annual_savings': 0,
            'total_monthly_savings': 0,
            'success': False
        }
    
    # Extract from executive summary
    exec_summary = results.get('executive_summary', {})
    
    # Extract from scenarios (use realistic scenario)
    scenarios = results.get('scenarios', {})
    realistic = scenarios.get('realistic', {})
    
    # Build standardized result
    adapted = {
        'roi_percentage': exec_summary.get('headline_roi', 0),
        'payback_months': exec_summary.get('payback_period_months', 0),
        'total_annual_savings': exec_summary.get('annual_savings_clp', 0),
        'total_monthly_savings': exec_summary.get('annual_savings_clp', 0) / 12 if exec_summary.get('annual_savings_clp', 0) > 0 else 0,
        
        # Keep original data for reference
        'executive_summary': exec_summary,
        'scenarios': scenarios,
        'recommendations': results.get('recommendations', []),
        'three_year_projection': results.get('three_year_projection', []),
        'chilean_specifics': results.get('chilean_specifics', {}),
        
        # Meta info
        'success': results.get('success', True),
        'timestamp': results.get('timestamp'),
        'confidence_level': exec_summary.get('confidence_level', 95),
        
        # Additional metrics from realistic scenario
        'monthly_savings_breakdown': realistic.get('monthly_savings_breakdown', {}),
        'annual_metrics': realistic.get('annual_metrics', {}),
        'implementation_costs': realistic.get('implementation_costs', {}),
        
        # For compatibility
        'roi_data': results  # Keep original data
    }
    
    return adapted

def extract_roi_value(results):
    """Extract just the ROI percentage value"""
    if isinstance(results, dict):
        # Try different possible locations
        if 'roi_percentage' in results:
            return results['roi_percentage']
        if 'executive_summary' in results:
            return results['executive_summary'].get('headline_roi', 0)
        if 'headline_roi' in results:
            return results['headline_roi']
    return 0

def extract_payback_months(results):
    """Extract payback period in months"""
    if isinstance(results, dict):
        if 'payback_months' in results:
            return results['payback_months']
        if 'executive_summary' in results:
            return results['executive_summary'].get('payback_period_months', 0)
        if 'payback_period_months' in results:
            return results['payback_period_months']
    return 0

def extract_annual_savings(results):
    """Extract annual savings"""
    if isinstance(results, dict):
        if 'total_annual_savings' in results:
            return results['total_annual_savings']
        if 'executive_summary' in results:
            return results['executive_summary'].get('annual_savings_clp', 0)
        if 'annual_savings_clp' in results:
            return results['annual_savings_clp']
    return 0
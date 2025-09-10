"""
Tax Calculator for ROI Analysis
Supports multiple jurisdictions and tax types (VAT, IVA, GST, Sales Tax)
"""

import json
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class TaxCalculator:
    """Tax calculator with multi-jurisdiction support"""
    
    # Tax configuration by country/region
    TAX_JURISDICTIONS = {
        # United States - State Sales Tax
        'US': {
            'name': 'United States',
            'tax_type': 'Sales Tax',
            'default_rate': 0.0875,  # Average combined state/local rate
            'states': {
                'AL': 0.0913, 'AK': 0.0176, 'AZ': 0.0837, 'AR': 0.0947, 'CA': 0.0857,
                'CO': 0.0769, 'CT': 0.0635, 'DE': 0.0000, 'FL': 0.0701, 'GA': 0.0732,
                'HI': 0.0444, 'ID': 0.0603, 'IL': 0.0882, 'IN': 0.0700, 'IA': 0.0694,
                'KS': 0.0865, 'KY': 0.0600, 'LA': 0.0907, 'ME': 0.0550, 'MD': 0.0600,
                'MA': 0.0625, 'MI': 0.0600, 'MN': 0.0738, 'MS': 0.0707, 'MO': 0.0823,
                'MT': 0.0000, 'NE': 0.0691, 'NV': 0.0827, 'NH': 0.0000, 'NJ': 0.0663,
                'NM': 0.0512, 'NY': 0.0804, 'NC': 0.0695, 'ND': 0.0695, 'OH': 0.0723,
                'OK': 0.0891, 'OR': 0.0000, 'PA': 0.0634, 'RI': 0.0700, 'SC': 0.0728,
                'SD': 0.0645, 'TN': 0.0947, 'TX': 0.0820, 'UT': 0.0719, 'VT': 0.0624,
                'VA': 0.0573, 'WA': 0.0929, 'WV': 0.0659, 'WI': 0.0543, 'WY': 0.0546
            }
        },
        
        # European Union - VAT
        'EU': {
            'name': 'European Union',
            'tax_type': 'VAT',
            'default_rate': 0.21,  # Average EU VAT rate
            'countries': {
                'AT': 0.20, 'BE': 0.21, 'BG': 0.20, 'CY': 0.19, 'CZ': 0.21,
                'DE': 0.19, 'DK': 0.25, 'EE': 0.20, 'ES': 0.21, 'FI': 0.24,
                'FR': 0.20, 'GR': 0.24, 'HU': 0.27, 'IE': 0.23, 'IT': 0.22,
                'LV': 0.21, 'LT': 0.21, 'LU': 0.17, 'MT': 0.18, 'NL': 0.21,
                'PL': 0.23, 'PT': 0.23, 'RO': 0.19, 'SK': 0.20, 'SI': 0.22,
                'SE': 0.25, 'HR': 0.25
            }
        },
        
        # Latin America - IVA and other taxes
        'CL': {
            'name': 'Chile',
            'tax_type': 'IVA',
            'default_rate': 0.19,
            'regions': {
                'national': 0.19,
                'zona_franca': 0.0  # Free trade zones
            }
        },
        
        'BR': {
            'name': 'Brazil',
            'tax_type': 'ICMS/IPI',
            'default_rate': 0.18,  # Average ICMS rate
            'states': {
                'SP': 0.18, 'RJ': 0.20, 'MG': 0.18, 'RS': 0.18, 'PR': 0.18,
                'SC': 0.17, 'BA': 0.18, 'GO': 0.17, 'PE': 0.18, 'CE': 0.18,
                'PA': 0.17, 'MA': 0.18, 'PB': 0.18, 'ES': 0.17, 'PI': 0.18,
                'AL': 0.17, 'RN': 0.18, 'MT': 0.17, 'MS': 0.17, 'DF': 0.18,
                'SE': 0.18, 'AM': 0.18, 'RO': 0.17, 'AC': 0.17, 'AP': 0.18,
                'RR': 0.17, 'TO': 0.18
            }
        },
        
        'MX': {
            'name': 'Mexico',
            'tax_type': 'IVA',
            'default_rate': 0.16,
            'regions': {
                'national': 0.16,
                'frontera': 0.08  # Border region
            }
        },
        
        'AR': {
            'name': 'Argentina',
            'tax_type': 'IVA',
            'default_rate': 0.21,
            'categories': {
                'general': 0.21,
                'basic_goods': 0.105,
                'medicines': 0.0
            }
        },
        
        # Other countries
        'CA': {
            'name': 'Canada',
            'tax_type': 'GST/HST',
            'default_rate': 0.13,  # Average combined rate
            'provinces': {
                'AB': 0.05, 'BC': 0.12, 'MB': 0.12, 'NB': 0.15, 'NL': 0.15,
                'NT': 0.05, 'NS': 0.15, 'NU': 0.05, 'ON': 0.13, 'PE': 0.15,
                'QC': 0.14975, 'SK': 0.11, 'YT': 0.05
            }
        },
        
        'GB': {
            'name': 'United Kingdom',
            'tax_type': 'VAT',
            'default_rate': 0.20,
            'rates': {
                'standard': 0.20,
                'reduced': 0.05,
                'zero': 0.0
            }
        },
        
        'AU': {
            'name': 'Australia',
            'tax_type': 'GST',
            'default_rate': 0.10,
            'rates': {
                'standard': 0.10,
                'gst_free': 0.0
            }
        },
        
        'JP': {
            'name': 'Japan',
            'tax_type': 'Consumption Tax',
            'default_rate': 0.10,
            'rates': {
                'standard': 0.10,
                'reduced': 0.08
            }
        },
        
        'CN': {
            'name': 'China',
            'tax_type': 'VAT',
            'default_rate': 0.13,
            'rates': {
                'standard': 0.13,
                'basic_goods': 0.09,
                'services': 0.06
            }
        }
    }
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize tax calculator
        
        Args:
            config_file: Path to custom tax configuration file
        """
        self.jurisdictions = self.TAX_JURISDICTIONS.copy()
        
        # Load custom configuration if provided
        if config_file and os.path.exists(config_file):
            self._load_custom_config(config_file)
    
    def _load_custom_config(self, config_file: str) -> None:
        """Load custom tax configuration from file"""
        try:
            with open(config_file, 'r') as f:
                custom_config = json.load(f)
            
            # Merge with default configuration
            self.jurisdictions.update(custom_config)
            logger.info(f"Loaded custom tax configuration from {config_file}")
            
        except Exception as e:
            logger.error(f"Error loading custom tax config: {e}")
    
    def get_tax_rate(self, jurisdiction: str, region: Optional[str] = None,
                     category: Optional[str] = None) -> float:
        """
        Get tax rate for specific jurisdiction and region
        
        Args:
            jurisdiction: Country/jurisdiction code (e.g., 'US', 'EU', 'CL')
            region: State/province/region code (optional)
            category: Tax category (optional)
            
        Returns:
            Tax rate as decimal (e.g., 0.19 for 19%)
        """
        if jurisdiction not in self.jurisdictions:
            logger.warning(f"Unknown jurisdiction: {jurisdiction}, using 0% tax rate")
            return 0.0
        
        jurisdiction_data = self.jurisdictions[jurisdiction]
        
        # Check for regional rates
        if region:
            # Try different possible keys for regional data
            for key in ['states', 'provinces', 'countries', 'regions']:
                if key in jurisdiction_data and region in jurisdiction_data[key]:
                    return jurisdiction_data[key][region]
        
        # Check for category-specific rates
        if category:
            for key in ['categories', 'rates']:
                if key in jurisdiction_data and category in jurisdiction_data[key]:
                    return jurisdiction_data[key][category]
        
        # Return default rate
        return jurisdiction_data.get('default_rate', 0.0)
    
    def calculate_tax_impact(self, amount: float, jurisdiction: str, 
                           region: Optional[str] = None,
                           category: Optional[str] = None,
                           include_tax: bool = True) -> Dict:
        """
        Calculate tax impact on given amount
        
        Args:
            amount: Base amount (pre-tax or post-tax depending on include_tax)
            jurisdiction: Tax jurisdiction
            region: Specific region within jurisdiction
            category: Tax category
            include_tax: If True, amount includes tax; if False, tax is added
            
        Returns:
            Dictionary with tax calculations
        """
        tax_rate = self.get_tax_rate(jurisdiction, region, category)
        
        if include_tax:
            # Amount includes tax - extract the tax portion
            tax_inclusive_amount = amount
            base_amount = amount / (1 + tax_rate)
            tax_amount = tax_inclusive_amount - base_amount
        else:
            # Amount is pre-tax - calculate tax to add
            base_amount = amount
            tax_amount = amount * tax_rate
            tax_inclusive_amount = base_amount + tax_amount
        
        return {
            'base_amount': round(base_amount, 2),
            'tax_amount': round(tax_amount, 2),
            'tax_inclusive_amount': round(tax_inclusive_amount, 2),
            'tax_rate': tax_rate,
            'tax_percentage': round(tax_rate * 100, 2),
            'jurisdiction': jurisdiction,
            'region': region,
            'category': category,
            'tax_type': self.jurisdictions.get(jurisdiction, {}).get('tax_type', 'Tax'),
            'calculation_date': datetime.now().isoformat()
        }
    
    def calculate_roi_tax_impact(self, roi_results: Dict, tax_config: Dict) -> Dict:
        """
        Calculate tax impact on ROI calculations
        
        Args:
            roi_results: ROI calculation results
            tax_config: Tax configuration dict with jurisdiction, region, etc.
            
        Returns:
            ROI results with tax impact analysis
        """
        jurisdiction = tax_config.get('jurisdiction')
        region = tax_config.get('region')
        category = tax_config.get('category')
        
        if not jurisdiction:
            logger.warning("No jurisdiction specified for tax calculation")
            return roi_results
        
        # Create a copy of results to avoid modifying original
        tax_adjusted_results = roi_results.copy()
        
        # Calculate tax impact on key monetary values
        tax_calculations = {}
        
        # Tax impact on savings (benefits may be subject to tax)
        if 'savings' in roi_results:
            annual_savings = roi_results['savings'].get('annual_total', 0)
            monthly_savings = roi_results['savings'].get('monthly_total', 0)
            
            annual_tax_impact = self.calculate_tax_impact(
                annual_savings, jurisdiction, region, category, include_tax=False
            )
            monthly_tax_impact = self.calculate_tax_impact(
                monthly_savings, jurisdiction, region, category, include_tax=False
            )
            
            tax_calculations['savings_tax_impact'] = {
                'annual': annual_tax_impact,
                'monthly': monthly_tax_impact
            }
            
            # Adjust savings for tax impact
            tax_adjusted_results['savings']['annual_after_tax'] = annual_tax_impact['base_amount']
            tax_adjusted_results['savings']['monthly_after_tax'] = monthly_tax_impact['base_amount']
            tax_adjusted_results['savings']['annual_tax_liability'] = annual_tax_impact['tax_amount']
            tax_adjusted_results['savings']['monthly_tax_liability'] = monthly_tax_impact['tax_amount']
        
        # Tax impact on investment (may be deductible)
        if 'inputs' in roi_results and 'service_investment' in roi_results['inputs']:
            investment = roi_results['inputs']['service_investment']
            investment_deduction = tax_config.get('investment_deductible', True)
            
            if investment_deduction:
                # Investment is tax deductible - calculate tax benefit
                investment_tax_benefit = self.calculate_tax_impact(
                    investment, jurisdiction, region, category, include_tax=False
                )
                
                tax_calculations['investment_tax_benefit'] = investment_tax_benefit
                
                # Effective investment cost after tax benefit
                tax_adjusted_results['inputs']['effective_investment'] = (
                    investment - investment_tax_benefit['tax_amount']
                )
            else:
                tax_adjusted_results['inputs']['effective_investment'] = investment
        
        # Recalculate ROI with tax considerations
        if 'savings' in tax_adjusted_results and 'inputs' in tax_adjusted_results:
            effective_investment = tax_adjusted_results['inputs'].get('effective_investment', 0)
            annual_savings_after_tax = tax_adjusted_results['savings'].get('annual_after_tax', 0)
            monthly_savings_after_tax = tax_adjusted_results['savings'].get('monthly_after_tax', 0)
            
            # Recalculate key metrics
            if effective_investment > 0:
                tax_adjusted_roi = ((annual_savings_after_tax - effective_investment) / effective_investment) * 100
                payback_period_months = effective_investment / monthly_savings_after_tax if monthly_savings_after_tax > 0 else float('inf')
                
                tax_calculations['tax_adjusted_metrics'] = {
                    'roi_percentage': round(tax_adjusted_roi, 2),
                    'payback_period_months': round(payback_period_months, 1),
                    'annual_savings_after_tax': round(annual_savings_after_tax, 2),
                    'monthly_savings_after_tax': round(monthly_savings_after_tax, 2),
                    'effective_investment': round(effective_investment, 2)
                }
        
        # Add tax configuration info
        tax_calculations['tax_config'] = {
            'jurisdiction': jurisdiction,
            'jurisdiction_name': self.jurisdictions.get(jurisdiction, {}).get('name', jurisdiction),
            'region': region,
            'category': category,
            'tax_type': self.jurisdictions.get(jurisdiction, {}).get('tax_type', 'Tax'),
            'tax_rate': self.get_tax_rate(jurisdiction, region, category),
            'investment_deductible': tax_config.get('investment_deductible', True)
        }
        
        # Add to results
        tax_adjusted_results['tax_analysis'] = tax_calculations
        
        return tax_adjusted_results
    
    def get_jurisdiction_info(self, jurisdiction: str) -> Optional[Dict]:
        """Get information about a specific jurisdiction"""
        return self.jurisdictions.get(jurisdiction)
    
    def get_available_jurisdictions(self) -> Dict:
        """Get list of available jurisdictions"""
        return {
            code: {
                'name': data.get('name', code),
                'tax_type': data.get('tax_type', 'Tax'),
                'default_rate': data.get('default_rate', 0.0)
            }
            for code, data in self.jurisdictions.items()
        }
    
    def get_regions_for_jurisdiction(self, jurisdiction: str) -> List[str]:
        """Get available regions for a jurisdiction"""
        if jurisdiction not in self.jurisdictions:
            return []
        
        jurisdiction_data = self.jurisdictions[jurisdiction]
        regions = []
        
        # Check different possible keys for regional data
        for key in ['states', 'provinces', 'countries', 'regions']:
            if key in jurisdiction_data:
                regions.extend(jurisdiction_data[key].keys())
        
        return sorted(regions)
    
    def export_tax_config(self, filename: str) -> None:
        """Export current tax configuration to file"""
        try:
            with open(filename, 'w') as f:
                json.dump(self.jurisdictions, f, indent=2)
            logger.info(f"Tax configuration exported to {filename}")
        except Exception as e:
            logger.error(f"Error exporting tax config: {e}")
    
    def validate_tax_config(self, config: Dict) -> List[str]:
        """Validate tax configuration and return any errors"""
        errors = []
        
        required_fields = ['jurisdiction']
        for field in required_fields:
            if field not in config:
                errors.append(f"Missing required field: {field}")
        
        jurisdiction = config.get('jurisdiction')
        if jurisdiction and jurisdiction not in self.jurisdictions:
            errors.append(f"Unknown jurisdiction: {jurisdiction}")
        
        region = config.get('region')
        if region and jurisdiction:
            available_regions = self.get_regions_for_jurisdiction(jurisdiction)
            if available_regions and region not in available_regions:
                errors.append(f"Unknown region '{region}' for jurisdiction '{jurisdiction}'")
        
        return errors


def main():
    """Test the tax calculator"""
    calculator = TaxCalculator()
    
    # Test basic tax calculation
    result = calculator.calculate_tax_impact(1000, 'US', 'CA')  # California sales tax
    print(f"$1000 + tax in California: ${result['tax_inclusive_amount']:.2f}")
    print(f"Tax amount: ${result['tax_amount']:.2f} ({result['tax_percentage']:.1f}%)")
    
    # Test different jurisdictions
    jurisdictions_to_test = [
        ('CL', None, None),  # Chile IVA
        ('EU', 'DE', None),  # Germany VAT
        ('AU', None, None),  # Australia GST
        ('BR', 'SP', None)   # São Paulo, Brazil
    ]
    
    print("\nTax rates across jurisdictions:")
    for jurisdiction, region, category in jurisdictions_to_test:
        rate = calculator.get_tax_rate(jurisdiction, region, category)
        info = calculator.get_jurisdiction_info(jurisdiction)
        name = info['name'] if info else jurisdiction
        tax_type = info['tax_type'] if info else 'Tax'
        print(f"{name} ({tax_type}): {rate*100:.1f}%")
    
    # Show available jurisdictions
    print("\nAvailable jurisdictions:")
    jurisdictions = calculator.get_available_jurisdictions()
    for code, info in jurisdictions.items():
        print(f"  {code}: {info['name']} - {info['tax_type']} ({info['default_rate']*100:.1f}%)")


if __name__ == "__main__":
    main()
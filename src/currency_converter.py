"""
Multi-Currency Support for ROI Calculator
Provides currency conversion with API integration and fallback rates
"""

import json
import time
import os
import requests
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import logging

logger = logging.getLogger(__name__)


class CurrencyConverter:
    """Currency converter with API integration and local caching"""
    
    # Supported currencies
    SUPPORTED_CURRENCIES = {
        'USD': {'name': 'US Dollar', 'symbol': '$'},
        'EUR': {'name': 'Euro', 'symbol': '€'},
        'CLP': {'name': 'Chilean Peso', 'symbol': '$'},
        'GBP': {'name': 'British Pound', 'symbol': '£'},
        'JPY': {'name': 'Japanese Yen', 'symbol': '¥'},
        'CNY': {'name': 'Chinese Yuan', 'symbol': '¥'},
        'BRL': {'name': 'Brazilian Real', 'symbol': 'R$'},
        'MXN': {'name': 'Mexican Peso', 'symbol': '$'}
    }
    
    # Fallback exchange rates (updated periodically)
    FALLBACK_RATES = {
        'USD': 1.0,
        'EUR': 0.85,
        'CLP': 890.0,
        'GBP': 0.73,
        'JPY': 150.0,
        'CNY': 7.3,
        'BRL': 5.1,
        'MXN': 17.2
    }
    
    def __init__(self, api_key: Optional[str] = None, cache_dir: str = None):
        """
        Initialize currency converter
        
        Args:
            api_key: API key for exchangerate-api.com
            cache_dir: Directory for caching exchange rates
        """
        self.api_key = api_key or os.environ.get('EXCHANGE_RATE_API_KEY')
        self.cache_dir = cache_dir or os.path.join(os.path.dirname(__file__), 'cache')
        self.cache_file = os.path.join(self.cache_dir, 'exchange_rates.json')
        self.cache_ttl = 3600  # 1 hour in seconds
        
        # Create cache directory if it doesn't exist
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Load cached rates
        self.rates = self._load_cached_rates()
        
        # Try to update rates on initialization if cache is old or missing
        if self.rates == self.FALLBACK_RATES:
            self.update_rates()
        
    def _load_cached_rates(self) -> Dict:
        """Load exchange rates from cache if available and not expired"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    cache_data = json.load(f)
                
                # Check if cache is still valid (within TTL)
                cache_time = datetime.fromisoformat(cache_data.get('timestamp', '1970-01-01'))
                if datetime.now() - cache_time < timedelta(seconds=self.cache_ttl):
                    logger.info("Using cached exchange rates")
                    return cache_data.get('rates', self.FALLBACK_RATES)
                else:
                    logger.info("Cache expired, will fetch fresh rates")
            
        except Exception as e:
            logger.warning(f"Error loading cached rates: {e}")
        
        return self.FALLBACK_RATES.copy()
    
    def _save_rates_to_cache(self, rates: Dict) -> None:
        """Save exchange rates to cache"""
        try:
            cache_data = {
                'rates': rates,
                'timestamp': datetime.now().isoformat(),
                'source': 'api' if self.api_key else 'fallback'
            }
            
            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
                
            logger.info("Exchange rates cached successfully")
            
        except Exception as e:
            logger.error(f"Error saving rates to cache: {e}")
    
    def _fetch_rates_from_api(self) -> Optional[Dict]:
        """Fetch exchange rates from exchangerate-api.com"""
        if not self.api_key:
            logger.info("No API key provided, using fallback rates")
            return None
            
        try:
            url = f"https://v6.exchangerate-api.com/v6/{self.api_key}/latest/USD"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('result') == 'success':
                rates = data.get('conversion_rates', {})
                
                # Filter to only supported currencies
                filtered_rates = {}
                for currency in self.SUPPORTED_CURRENCIES.keys():
                    if currency in rates:
                        filtered_rates[currency] = rates[currency]
                    else:
                        filtered_rates[currency] = self.FALLBACK_RATES[currency]
                
                logger.info("Successfully fetched exchange rates from API")
                return filtered_rates
            else:
                logger.error(f"API error: {data.get('error-type', 'Unknown error')}")
                return None
                
        except requests.RequestException as e:
            logger.error(f"API request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Error fetching rates from API: {e}")
            return None
    
    def update_rates(self) -> bool:
        """Update exchange rates from API or use fallbacks"""
        try:
            # Try to fetch from API first
            api_rates = self._fetch_rates_from_api()
            
            if api_rates:
                self.rates = api_rates
                self._save_rates_to_cache(self.rates)
                return True
            else:
                # Fall back to hardcoded rates
                logger.info("Using fallback exchange rates")
                self.rates = self.FALLBACK_RATES.copy()
                return False
                
        except Exception as e:
            logger.error(f"Error updating rates: {e}")
            self.rates = self.FALLBACK_RATES.copy()
            return False
    
    def convert(self, amount: float, from_currency: str, to_currency: str) -> Dict:
        """
        Convert amount from one currency to another
        
        Args:
            amount: Amount to convert
            from_currency: Source currency code
            to_currency: Target currency code
            
        Returns:
            Dict with conversion details
        """
        # Validate currencies
        if from_currency not in self.SUPPORTED_CURRENCIES:
            raise ValueError(f"Unsupported source currency: {from_currency}")
        if to_currency not in self.SUPPORTED_CURRENCIES:
            raise ValueError(f"Unsupported target currency: {to_currency}")
        
        # If same currency, no conversion needed
        if from_currency == to_currency:
            return {
                'original_amount': amount,
                'converted_amount': amount,
                'from_currency': from_currency,
                'to_currency': to_currency,
                'exchange_rate': 1.0,
                'conversion_date': datetime.now().isoformat()
            }
        
        # Get exchange rates (all rates are relative to USD)
        from_rate = self.rates.get(from_currency, self.FALLBACK_RATES[from_currency])
        to_rate = self.rates.get(to_currency, self.FALLBACK_RATES[to_currency])
        
        # Convert: amount in from_currency -> USD -> to_currency
        if from_currency == 'USD':
            usd_amount = amount
        else:
            usd_amount = amount / from_rate
        
        if to_currency == 'USD':
            converted_amount = usd_amount
        else:
            converted_amount = usd_amount * to_rate
        
        # Calculate direct exchange rate
        exchange_rate = to_rate / from_rate if from_currency != 'USD' else to_rate
        
        return {
            'original_amount': amount,
            'converted_amount': round(converted_amount, 2),
            'amount': round(converted_amount, 2),  # For backward compatibility
            'from_currency': from_currency,
            'to_currency': to_currency,
            'exchange_rate': round(exchange_rate, 4),
            'conversion_date': datetime.now().isoformat(),
            'from_currency_symbol': self.SUPPORTED_CURRENCIES[from_currency]['symbol'],
            'to_currency_symbol': self.SUPPORTED_CURRENCIES[to_currency]['symbol']
        }
    
    def convert_roi_calculation(self, roi_results: Dict, target_currency: str) -> Dict:
        """
        Convert entire ROI calculation results to target currency
        
        Args:
            roi_results: ROI calculation results
            target_currency: Target currency code
            
        Returns:
            ROI results converted to target currency
        """
        # Assume original calculation is in USD
        source_currency = roi_results.get('currency', 'USD')
        
        if source_currency == target_currency:
            return roi_results
        
        # Fields to convert (monetary values)
        monetary_fields = [
            'service_investment',
            'annual_revenue',
            'labor_costs',
            'shipping_costs',
            'error_costs',
            'inventory_costs'
        ]
        
        converted_results = roi_results.copy()
        converted_results['currency'] = target_currency
        converted_results['currency_symbol'] = self.SUPPORTED_CURRENCIES[target_currency]['symbol']
        converted_results['conversion_info'] = {
            'original_currency': source_currency,
            'target_currency': target_currency,
            'conversion_date': datetime.now().isoformat()
        }
        
        # Convert input values
        for field in monetary_fields:
            if field in converted_results.get('inputs', {}):
                original_value = converted_results['inputs'][field]
                conversion = self.convert(original_value, source_currency, target_currency)
                converted_results['inputs'][field] = conversion['converted_amount']
        
        # Convert calculated values
        sections_to_convert = ['current_costs', 'optimized_costs', 'savings', 'roi_metrics']
        
        for section in sections_to_convert:
            if section in converted_results:
                converted_results[section] = self._convert_section(
                    converted_results[section], source_currency, target_currency
                )
        
        # Convert projections
        if 'projections' in converted_results:
            for year_key, year_data in converted_results['projections'].items():
                converted_results['projections'][year_key] = self._convert_section(
                    year_data, source_currency, target_currency
                )
        
        # Convert financial metrics
        if 'financial_metrics' in converted_results:
            fm = converted_results['financial_metrics']
            if 'npv' in fm:
                conversion = self.convert(fm['npv'], source_currency, target_currency)
                fm['npv'] = conversion['converted_amount']
            if 'cash_flows' in fm:
                fm['cash_flows'] = [
                    self.convert(cf, source_currency, target_currency)['converted_amount']
                    for cf in fm['cash_flows']
                ]
        
        return converted_results
    
    def _convert_section(self, section_data: Dict, from_currency: str, to_currency: str) -> Dict:
        """Convert monetary values in a section"""
        if isinstance(section_data, dict):
            converted_section = {}
            for key, value in section_data.items():
                if isinstance(value, (int, float)) and key not in ['percentage', 'roi_percentage']:
                    # This is likely a monetary value
                    conversion = self.convert(value, from_currency, to_currency)
                    converted_section[key] = conversion['converted_amount']
                elif isinstance(value, dict):
                    converted_section[key] = self._convert_section(value, from_currency, to_currency)
                else:
                    converted_section[key] = value
            return converted_section
        else:
            return section_data
    
    def get_supported_currencies(self) -> Dict:
        """Get list of supported currencies"""
        return self.SUPPORTED_CURRENCIES.copy()
    
    def get_current_rates(self) -> Dict:
        """Get current exchange rates"""
        return {
            'rates': self.rates.copy(),
            'base_currency': 'USD',
            'last_updated': datetime.now().isoformat(),
            'supported_currencies': self.SUPPORTED_CURRENCIES
        }
    
    def format_currency(self, amount: float, currency: str) -> str:
        """Format amount with currency symbol"""
        if currency not in self.SUPPORTED_CURRENCIES:
            return f"{amount:,.2f} {currency}"
        
        symbol = self.SUPPORTED_CURRENCIES[currency]['symbol']
        
        # Special formatting for different currencies
        if currency == 'JPY':
            # Japanese Yen doesn't use decimals
            return f"{symbol}{amount:,.0f}"
        elif currency in ['CLP']:
            # Chilean Peso - no decimals in common usage
            return f"{symbol}{amount:,.0f}"
        else:
            return f"{symbol}{amount:,.2f}"


def main():
    """Test the currency converter"""
    converter = CurrencyConverter()
    
    # Update rates
    success = converter.update_rates()
    print(f"Rate update {'successful' if success else 'failed, using fallbacks'}")
    
    # Test conversion
    result = converter.convert(1000, 'USD', 'EUR')
    print(f"$1000 USD = €{result['converted_amount']} EUR")
    
    # Show all rates
    rates = converter.get_current_rates()
    print("\nCurrent exchange rates (base: USD):")
    for currency, rate in rates['rates'].items():
        formatted = converter.format_currency(rate, currency)
        print(f"1 USD = {formatted}")


if __name__ == "__main__":
    main()
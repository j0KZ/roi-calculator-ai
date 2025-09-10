"""
Market Data Service for ROI Calculator
Integrates with FRED API and other data sources to provide market insights
"""

import requests
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from dataclasses import dataclass
from enum import Enum

from database.connection import get_session
from database.models import MarketData, MarketBenchmark

logger = logging.getLogger(__name__)

class DataFrequency(Enum):
    DAILY = "d"
    WEEKLY = "w"
    MONTHLY = "m"
    QUARTERLY = "q"
    ANNUAL = "a"

@dataclass
class MarketSeries:
    series_id: str
    title: str
    description: str
    frequency: DataFrequency
    units: str
    seasonal_adjustment: str

class FREDAPIClient:
    """Client for Federal Reserve Economic Data API"""
    
    BASE_URL = "https://api.stlouisfed.org/fred"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()
        
    def get_series_observations(self, series_id: str, start_date: Optional[str] = None, 
                              end_date: Optional[str] = None, limit: int = 10000) -> Dict:
        """Fetch observations for a FRED series"""
        url = f"{self.BASE_URL}/series/observations"
        params = {
            'series_id': series_id,
            'api_key': self.api_key,
            'file_type': 'json',
            'limit': limit
        }
        
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
            
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching FRED data for {series_id}: {str(e)}")
            raise
    
    def get_series_info(self, series_id: str) -> Dict:
        """Get metadata for a FRED series"""
        url = f"{self.BASE_URL}/series"
        params = {
            'series_id': series_id,
            'api_key': self.api_key,
            'file_type': 'json'
        }
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching FRED series info for {series_id}: {str(e)}")
            raise

class MarketDataService:
    """Service for managing market data and benchmarks"""
    
    # E-commerce and retail data series
    ECOMMERCE_SERIES = {
        'ECOMSA': MarketSeries(
            'ECOMSA', 
            'E-Commerce Retail Sales',
            'E-commerce retail sales, seasonally adjusted',
            DataFrequency.QUARTERLY,
            'Millions of Dollars',
            'Seasonally Adjusted'
        ),
        'ECOMPCTSA': MarketSeries(
            'ECOMPCTSA',
            'E-Commerce Sales Percentage',
            'E-commerce sales as a percent of total retail sales',
            DataFrequency.QUARTERLY,
            'Percent',
            'Seasonally Adjusted'
        ),
        'RSXFS': MarketSeries(
            'RSXFS',
            'Retail Sales: Total',
            'Advance retail sales: retail and food services, total',
            DataFrequency.MONTHLY,
            'Millions of Dollars',
            'Seasonally Adjusted'
        ),
        'CES4200000001': MarketSeries(
            'CES4200000001',
            'Retail Trade Employment',
            'All employees: retail trade',
            DataFrequency.MONTHLY,
            'Thousands of Persons',
            'Seasonally Adjusted'
        )
    }
    
    def __init__(self, fred_api_key: str):
        self.fred_client = FREDAPIClient(fred_api_key)
        
    def update_market_data(self, series_ids: Optional[List[str]] = None) -> Dict[str, bool]:
        """Update market data for specified series or all series"""
        if series_ids is None:
            series_ids = list(self.ECOMMERCE_SERIES.keys())
            
        results = {}
        
        with get_session() as session:
            for series_id in series_ids:
                try:
                    success = self._update_series_data(session, series_id)
                    results[series_id] = success
                    logger.info(f"Updated {series_id}: {'Success' if success else 'Failed'}")
                except Exception as e:
                    logger.error(f"Failed to update {series_id}: {str(e)}")
                    results[series_id] = False
                    
            session.commit()
            
        return results
    
    def _update_series_data(self, session, series_id: str) -> bool:
        """Update data for a single series"""
        try:
            # Get series info
            series_info = self.fred_client.get_series_info(series_id)
            series_data = series_info['seriess'][0]
            
            # Get observations (last 5 years)
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=5*365)).strftime('%Y-%m-%d')
            
            observations = self.fred_client.get_series_observations(
                series_id, start_date=start_date, end_date=end_date
            )
            
            # Store each observation
            for obs in observations['observations']:
                if obs['value'] != '.':  # Skip missing values
                    try:
                        value = float(obs['value'])
                        date = datetime.strptime(obs['date'], '%Y-%m-%d').date()
                        
                        # Check if record exists
                        existing = session.query(MarketData).filter(
                            MarketData.series_id == series_id,
                            MarketData.date == date
                        ).first()
                        
                        if existing:
                            existing.value = value
                            existing.updated_at = datetime.utcnow()
                        else:
                            market_data = MarketData(
                                series_id=series_id,
                                series_title=series_data['title'],
                                date=date,
                                value=value,
                                frequency=series_data.get('frequency', ''),
                                units=series_data.get('units', ''),
                                seasonal_adjustment=series_data.get('seasonal_adjustment', ''),
                                created_at=datetime.utcnow(),
                                updated_at=datetime.utcnow()
                            )
                            session.add(market_data)
                    except (ValueError, TypeError) as e:
                        logger.warning(f"Invalid value in {series_id}: {obs['value']}")
                        continue
                        
            return True
            
        except Exception as e:
            logger.error(f"Error updating series {series_id}: {str(e)}")
            session.rollback()
            return False
    
    def get_latest_data(self, series_id: str, days: int = 365) -> List[Dict]:
        """Get latest data points for a series"""
        with get_session() as session:
            cutoff_date = datetime.now().date() - timedelta(days=days)
            
            data = session.query(MarketData).filter(
                MarketData.series_id == series_id,
                MarketData.date >= cutoff_date
            ).order_by(MarketData.date.desc()).all()
            
            return [{
                'date': d.date.isoformat(),
                'value': d.value,
                'series_title': d.series_title,
                'units': d.units
            } for d in data]
    
    def calculate_growth_rates(self, series_id: str, periods: List[int] = [30, 90, 365]) -> Dict:
        """Calculate growth rates over different periods"""
        data = self.get_latest_data(series_id, days=max(periods) + 30)
        
        if len(data) < 2:
            return {}
            
        # Sort by date
        sorted_data = sorted(data, key=lambda x: x['date'])
        current_value = sorted_data[-1]['value']
        
        growth_rates = {}
        
        for period in periods:
            # Find value from 'period' days ago
            target_date = datetime.now().date() - timedelta(days=period)
            
            # Find closest data point
            closest_data = min(
                sorted_data,
                key=lambda x: abs((datetime.fromisoformat(x['date']).date() - target_date).days)
            )
            
            if closest_data['value'] > 0:
                growth_rate = ((current_value - closest_data['value']) / closest_data['value']) * 100
                growth_rates[f'{period}d'] = {
                    'rate': round(growth_rate, 2),
                    'current_value': current_value,
                    'previous_value': closest_data['value'],
                    'previous_date': closest_data['date']
                }
                
        return growth_rates
    
    def generate_roi_benchmarks(self, roi_value: float, industry: str = 'ecommerce') -> Dict:
        """Generate ROI benchmarks and percentile rankings"""
        benchmarks = {}
        
        try:
            # Get e-commerce growth data
            ecom_growth = self.calculate_growth_rates('ECOMSA', [90, 365])
            retail_growth = self.calculate_growth_rates('RSXFS', [90, 365])
            
            # Industry benchmark ROI ranges (based on historical data and studies)
            industry_benchmarks = {
                'ecommerce': {
                    'excellent': 30.0,  # Top 10%
                    'good': 20.0,       # Top 25%
                    'average': 12.0,    # Median
                    'below_average': 5.0, # Bottom 25%
                    'poor': 0.0         # Bottom 10%
                },
                'retail': {
                    'excellent': 25.0,
                    'good': 15.0,
                    'average': 8.0,
                    'below_average': 3.0,
                    'poor': 0.0
                }
            }
            
            bench = industry_benchmarks.get(industry, industry_benchmarks['ecommerce'])
            
            # Determine percentile
            if roi_value >= bench['excellent']:
                percentile = 90 + (roi_value - bench['excellent']) / bench['excellent'] * 10
                rating = 'Excellent'
            elif roi_value >= bench['good']:
                percentile = 75 + (roi_value - bench['good']) / (bench['excellent'] - bench['good']) * 15
                rating = 'Good'
            elif roi_value >= bench['average']:
                percentile = 50 + (roi_value - bench['average']) / (bench['good'] - bench['average']) * 25
                rating = 'Above Average'
            elif roi_value >= bench['below_average']:
                percentile = 25 + (roi_value - bench['below_average']) / (bench['average'] - bench['below_average']) * 25
                rating = 'Below Average'
            else:
                percentile = max(0, (roi_value / bench['below_average']) * 25)
                rating = 'Poor'
                
            benchmarks = {
                'roi_value': roi_value,
                'percentile': min(100, max(0, percentile)),
                'rating': rating,
                'industry_averages': bench,
                'market_context': {
                    'ecommerce_growth_90d': ecom_growth.get('90d', {}).get('rate', 0),
                    'ecommerce_growth_365d': ecom_growth.get('365d', {}).get('rate', 0),
                    'retail_growth_90d': retail_growth.get('90d', {}).get('rate', 0),
                    'retail_growth_365d': retail_growth.get('365d', {}).get('rate', 0)
                }
            }
            
            # Store benchmark in database
            self._store_roi_benchmark(roi_value, industry, benchmarks)
            
        except Exception as e:
            logger.error(f"Error generating ROI benchmarks: {str(e)}")
            
        return benchmarks
    
    def _store_roi_benchmark(self, roi_value: float, industry: str, benchmarks: Dict):
        """Store ROI benchmark calculation in database"""
        try:
            with get_session() as session:
                benchmark = MarketBenchmark(
                    roi_value=roi_value,
                    industry=industry,
                    percentile=benchmarks['percentile'],
                    rating=benchmarks['rating'],
                    benchmark_data=json.dumps(benchmarks),
                    created_at=datetime.utcnow()
                )
                session.add(benchmark)
                session.commit()
        except Exception as e:
            logger.error(f"Error storing ROI benchmark: {str(e)}")
    
    def get_market_overview(self) -> Dict:
        """Get comprehensive market overview with latest data"""
        overview = {}
        
        try:
            with get_session() as session:
                # Get latest data for each series
                for series_id, series_info in self.ECOMMERCE_SERIES.items():
                    latest_data = session.query(MarketData).filter(
                        MarketData.series_id == series_id
                    ).order_by(MarketData.date.desc()).first()
                    
                    if latest_data:
                        growth_rates = self.calculate_growth_rates(series_id)
                        
                        overview[series_id] = {
                            'title': series_info.title,
                            'description': series_info.description,
                            'latest_value': latest_data.value,
                            'latest_date': latest_data.date.isoformat(),
                            'units': latest_data.units,
                            'growth_rates': growth_rates,
                            'frequency': latest_data.frequency
                        }
                        
        except Exception as e:
            logger.error(f"Error generating market overview: {str(e)}")
            
        return overview
    
    def get_trend_analysis(self, series_id: str, days: int = 365) -> Dict:
        """Perform trend analysis on a data series"""
        data_points = self.get_latest_data(series_id, days)
        
        if len(data_points) < 10:
            return {'error': 'Insufficient data for trend analysis'}
        
        try:
            # Convert to pandas for analysis
            df = pd.DataFrame(data_points)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            
            # Calculate moving averages
            df['ma_30'] = df['value'].rolling(window=min(30, len(df))).mean()
            df['ma_90'] = df['value'].rolling(window=min(90, len(df))).mean()
            
            # Calculate trend direction
            recent_values = df['value'].tail(30).values
            if len(recent_values) >= 2:
                trend_slope = np.polyfit(range(len(recent_values)), recent_values, 1)[0]
                if trend_slope > 0.1:
                    trend_direction = 'Upward'
                elif trend_slope < -0.1:
                    trend_direction = 'Downward'
                else:
                    trend_direction = 'Stable'
            else:
                trend_direction = 'Unknown'
            
            # Calculate volatility
            returns = df['value'].pct_change().dropna()
            volatility = returns.std() * 100  # As percentage
            
            return {
                'trend_direction': trend_direction,
                'volatility': round(volatility, 2),
                'current_vs_ma30': round(((df['value'].iloc[-1] / df['ma_30'].iloc[-1]) - 1) * 100, 2),
                'current_vs_ma90': round(((df['value'].iloc[-1] / df['ma_90'].iloc[-1]) - 1) * 100, 2),
                'data_points': len(data_points),
                'date_range': {
                    'start': df['date'].min().isoformat(),
                    'end': df['date'].max().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error in trend analysis for {series_id}: {str(e)}")
            return {'error': str(e)}

def test_fred_api_connection(api_key: str) -> Dict:
    """Test FRED API connection and data retrieval"""
    try:
        service = MarketDataService(api_key)
        
        # Test with a simple series
        test_series = 'ECOMSA'
        data = service.get_latest_data(test_series, days=30)
        
        if data:
            return {
                'status': 'success',
                'message': f'Successfully connected to FRED API and retrieved {len(data)} data points',
                'sample_data': data[:3] if len(data) >= 3 else data
            }
        else:
            # Try to update data
            results = service.update_market_data([test_series])
            return {
                'status': 'success' if results.get(test_series) else 'warning',
                'message': 'Connected to FRED API, updated data',
                'update_results': results
            }
            
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Failed to connect to FRED API: {str(e)}'
        }

if __name__ == "__main__":
    # Test the service
    import os
    api_key = os.getenv('FRED_API_KEY', 'c5ed99d76664a2191ccfd433edd9af6d')
    
    test_result = test_fred_api_connection(api_key)
    print(json.dumps(test_result, indent=2))
    
    if test_result['status'] == 'success':
        service = MarketDataService(api_key)
        
        # Update all series
        print("\nUpdating market data...")
        results = service.update_market_data()
        print(f"Update results: {results}")
        
        # Generate market overview
        print("\nGenerating market overview...")
        overview = service.get_market_overview()
        print(json.dumps(overview, indent=2, default=str))
        
        # Test ROI benchmarking
        print("\nTesting ROI benchmarking...")
        benchmark = service.generate_roi_benchmarks(15.5, 'ecommerce')
        print(json.dumps(benchmark, indent=2, default=str))
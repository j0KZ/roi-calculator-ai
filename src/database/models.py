"""
Database models for ROI Calculator
Supports both SQLite and PostgreSQL
"""

from datetime import datetime, date
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, JSON, Date, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import json

Base = declarative_base()

class Calculation(Base):
    """Model for storing ROI calculations"""
    __tablename__ = 'calculations'
    
    id = Column(Integer, primary_key=True)
    
    # Company Information
    company_name = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Revenue Information
    annual_revenue = Column(Float, nullable=False)
    monthly_orders = Column(Integer, nullable=False)
    avg_order_value = Column(Float, nullable=False)
    
    # Current Costs
    labor_costs = Column(Float, nullable=False)
    shipping_costs = Column(Float, nullable=False)
    error_costs = Column(Float, nullable=False)
    inventory_costs = Column(Float, nullable=False)
    
    # Investment
    service_investment = Column(Float, nullable=False)
    
    # Calculated Results (stored as JSON for flexibility)
    results = Column(JSON, nullable=True)
    
    # Metadata
    notes = Column(Text, nullable=True)
    tags = Column(String(500), nullable=True)  # Comma-separated tags
    
    def __repr__(self):
        return f"<Calculation(id={self.id}, company='{self.company_name}', roi={self.get_roi()})>"
    
    def get_roi(self):
        """Extract ROI percentage from results"""
        if self.results:
            results_dict = self.results if isinstance(self.results, dict) else json.loads(self.results)
            return results_dict.get('roi_percentage', 0)
        return 0
    
    def get_payback_months(self):
        """Extract payback period from results"""
        if self.results:
            results_dict = self.results if isinstance(self.results, dict) else json.loads(self.results)
            return results_dict.get('payback_months', 0)
        return 0
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'company_name': self.company_name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'annual_revenue': self.annual_revenue,
            'monthly_orders': self.monthly_orders,
            'avg_order_value': self.avg_order_value,
            'labor_costs': self.labor_costs,
            'shipping_costs': self.shipping_costs,
            'error_costs': self.error_costs,
            'inventory_costs': self.inventory_costs,
            'service_investment': self.service_investment,
            'results': self.results if isinstance(self.results, dict) else json.loads(self.results) if self.results else {},
            'notes': self.notes,
            'tags': self.tags.split(',') if self.tags else []
        }


class ComparisonScenario(Base):
    """Model for storing comparison scenarios"""
    __tablename__ = 'comparison_scenarios'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Store multiple calculation IDs
    calculation_ids = Column(JSON, nullable=False)  # List of calculation IDs
    
    # Comparison results
    comparison_results = Column(JSON, nullable=True)
    
    def __repr__(self):
        return f"<ComparisonScenario(id={self.id}, name='{self.name}')>"


class Template(Base):
    """Model for storing calculation templates"""
    __tablename__ = 'templates'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)  # e.g., 'small_business', 'medium_business', 'large_business'
    
    # Template values
    template_data = Column(JSON, nullable=False)
    
    # Additional fields for template manager compatibility
    tags = Column(String(500), nullable=True)  # Comma-separated tags
    meta_data = Column(JSON, nullable=True)  # Additional metadata (renamed from metadata to avoid SQLAlchemy conflict)
    is_public = Column(Integer, default=0)  # 0 = private, 1 = public
    created_by = Column(String(100), default='user')  # 'system' or 'user'
    industry = Column(String(100), nullable=True)  # Industry type
    business_size = Column(String(50), nullable=True)  # small, medium, large, enterprise
    
    # Usage tracking
    usage_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Template(id={self.id}, name='{self.name}', category='{self.category}')>"
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'template_data': self.template_data if isinstance(self.template_data, dict) else json.loads(self.template_data),
            'tags': self.tags.split(',') if self.tags else [],
            'metadata': self.meta_data if isinstance(self.meta_data, dict) else json.loads(self.meta_data) if self.meta_data else {},
            'is_public': bool(self.is_public),
            'created_by': self.created_by,
            'industry': self.industry,
            'business_size': self.business_size,
            'usage_count': self.usage_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class MarketData(Base):
    """Model for storing market data from FRED and other sources"""
    __tablename__ = 'market_data'
    
    id = Column(Integer, primary_key=True)
    series_id = Column(String(50), nullable=False)
    series_title = Column(String(500), nullable=False)
    date = Column(Date, nullable=False)
    value = Column(Float, nullable=False)
    
    # Series metadata
    frequency = Column(String(20), nullable=True)  # Daily, Monthly, Quarterly, etc.
    units = Column(String(100), nullable=True)
    seasonal_adjustment = Column(String(100), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Create composite index for efficient queries
    __table_args__ = (
        Index('idx_market_data_series_date', 'series_id', 'date'),
        Index('idx_market_data_date', 'date'),
    )
    
    def __repr__(self):
        return f"<MarketData(series_id='{self.series_id}', date='{self.date}', value={self.value})>"
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'series_id': self.series_id,
            'series_title': self.series_title,
            'date': self.date.isoformat() if self.date else None,
            'value': self.value,
            'frequency': self.frequency,
            'units': self.units,
            'seasonal_adjustment': self.seasonal_adjustment,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class MarketBenchmark(Base):
    """Model for storing ROI benchmarking calculations"""
    __tablename__ = 'market_benchmarks'
    
    id = Column(Integer, primary_key=True)
    roi_value = Column(Float, nullable=False)
    industry = Column(String(100), nullable=False)
    percentile = Column(Float, nullable=False)  # 0-100
    rating = Column(String(50), nullable=False)  # Excellent, Good, Average, etc.
    
    # Store detailed benchmark data as JSON
    benchmark_data = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Create index for efficient queries
    __table_args__ = (
        Index('idx_benchmark_roi_industry', 'roi_value', 'industry'),
        Index('idx_benchmark_created_at', 'created_at'),
    )
    
    def __repr__(self):
        return f"<MarketBenchmark(roi={self.roi_value}, industry='{self.industry}', percentile={self.percentile})>"
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'roi_value': self.roi_value,
            'industry': self.industry,
            'percentile': self.percentile,
            'rating': self.rating,
            'benchmark_data': self.benchmark_data if isinstance(self.benchmark_data, dict) else json.loads(self.benchmark_data) if self.benchmark_data else {},
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
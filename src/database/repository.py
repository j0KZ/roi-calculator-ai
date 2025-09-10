#!/usr/bin/env python3
"""
Data Repository Layer for ROI Calculator
Provides data access abstraction with caching
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_, func
import uuid
import logging

from .models import (
    Company, Calculation, ROICalculation, CostOptimization,
    ExchangeRate, UserSession, PerformanceMetric, AuditLog,
    CalculationType, CompanySize, Industry
)
from ..cache_manager import get_cache, CacheKeys

logger = logging.getLogger(__name__)

class CompanyRepository:
    """Repository for company operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.cache = get_cache()
    
    def create(self, name: str, email: str, industry: str, size: str) -> Company:
        """Create a new company"""
        company = Company(
            name=name,
            email=email,
            industry=Industry[industry.upper()],
            size=CompanySize[size.upper()]
        )
        self.db.add(company)
        self.db.commit()
        self.db.refresh(company)
        
        # Clear cache
        self.cache.delete(f"company:email:{email}")
        
        return company
    
    def get_by_email(self, email: str) -> Optional[Company]:
        """Get company by email with caching"""
        cache_key = f"company:email:{email}"
        
        # Try cache first
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        # Query database
        company = self.db.query(Company).filter(
            Company.email == email
        ).first()
        
        if company:
            # Cache for 1 hour
            self.cache.set(cache_key, company, ttl=3600)
        
        return company
    
    def get_by_id(self, company_id: uuid.UUID) -> Optional[Company]:
        """Get company by ID"""
        return self.db.query(Company).filter(
            Company.id == company_id
        ).first()
    
    def update(self, company_id: uuid.UUID, **kwargs) -> Optional[Company]:
        """Update company details"""
        company = self.get_by_id(company_id)
        if company:
            for key, value in kwargs.items():
                if hasattr(company, key):
                    setattr(company, key, value)
            
            company.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(company)
            
            # Clear cache
            self.cache.delete(f"company:email:{company.email}")
            
        return company

class CalculationRepository:
    """Repository for calculation operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.cache = get_cache()
    
    def save_calculation(
        self,
        company_id: uuid.UUID,
        calc_type: CalculationType,
        inputs: Dict[str, Any],
        results: Dict[str, Any],
        metadata: Optional[Dict] = None,
        calculation_time_ms: Optional[float] = None,
        cache_hit: bool = False
    ) -> Calculation:
        """Save a calculation to database"""
        
        calculation = Calculation(
            company_id=company_id,
            type=calc_type,
            inputs=inputs,
            results=results,
            metadata=metadata,
            calculation_time_ms=calculation_time_ms,
            cache_hit=cache_hit
        )
        
        self.db.add(calculation)
        self.db.commit()
        self.db.refresh(calculation)
        
        # Clear related caches
        self.cache.clear_pattern(f"calculations:{company_id}:*")
        
        return calculation
    
    def save_roi_details(
        self,
        calculation_id: uuid.UUID,
        investment: float,
        revenue: float,
        months: int,
        roi: float,
        payback: float,
        projections: Dict[str, float],
        scenarios: Dict[str, float]
    ) -> ROICalculation:
        """Save detailed ROI calculation"""
        
        roi_calc = ROICalculation(
            calculation_id=calculation_id,
            investment_amount_clp=investment,
            annual_revenue_clp=revenue,
            implementation_months=months,
            roi_percentage=roi,
            payback_months=payback,
            year1_revenue_clp=projections.get('year1'),
            year2_revenue_clp=projections.get('year2'),
            year3_revenue_clp=projections.get('year3'),
            year4_revenue_clp=projections.get('year4'),
            year5_revenue_clp=projections.get('year5'),
            best_case_roi=scenarios.get('best'),
            worst_case_roi=scenarios.get('worst'),
            most_likely_roi=scenarios.get('likely')
        )
        
        self.db.add(roi_calc)
        self.db.commit()
        self.db.refresh(roi_calc)
        
        return roi_calc
    
    def get_recent_calculations(
        self,
        company_id: uuid.UUID,
        calc_type: Optional[CalculationType] = None,
        limit: int = 10
    ) -> List[Calculation]:
        """Get recent calculations for a company"""
        
        cache_key = f"calculations:{company_id}:{calc_type}:{limit}"
        
        # Try cache
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        # Query
        query = self.db.query(Calculation).filter(
            Calculation.company_id == company_id
        )
        
        if calc_type:
            query = query.filter(Calculation.type == calc_type)
        
        calculations = query.order_by(
            desc(Calculation.created_at)
        ).limit(limit).all()
        
        # Cache for 5 minutes
        self.cache.set(cache_key, calculations, ttl=300)
        
        return calculations
    
    def get_calculation_stats(
        self,
        company_id: uuid.UUID,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get calculation statistics for a company"""
        
        since = datetime.utcnow() - timedelta(days=days)
        
        stats = self.db.query(
            Calculation.type,
            func.count(Calculation.id).label('count'),
            func.avg(Calculation.calculation_time_ms).label('avg_time'),
            func.sum(
                func.cast(Calculation.cache_hit, type_=Integer)
            ).label('cache_hits')
        ).filter(
            and_(
                Calculation.company_id == company_id,
                Calculation.created_at >= since
            )
        ).group_by(Calculation.type).all()
        
        return {
            str(stat.type): {
                'count': stat.count,
                'avg_time_ms': float(stat.avg_time) if stat.avg_time else 0,
                'cache_hit_rate': (stat.cache_hits / stat.count) if stat.count > 0 else 0
            }
            for stat in stats
        }

class ExchangeRateRepository:
    """Repository for exchange rates"""
    
    def __init__(self, db: Session):
        self.db = db
        self.cache = get_cache()
    
    def save_rate(
        self,
        from_currency: str,
        to_currency: str,
        rate: float,
        source: str = "API"
    ) -> ExchangeRate:
        """Save exchange rate to database"""
        
        exchange_rate = ExchangeRate(
            from_currency=from_currency,
            to_currency=to_currency,
            rate=rate,
            source=source
        )
        
        self.db.add(exchange_rate)
        self.db.commit()
        
        # Update cache
        cache_key = CacheKeys.exchange_rate(from_currency, to_currency)
        self.cache.set(cache_key, rate, ttl=3600)  # 1 hour
        
        return exchange_rate
    
    def get_latest_rate(
        self,
        from_currency: str,
        to_currency: str
    ) -> Optional[float]:
        """Get latest exchange rate"""
        
        # Try cache first
        cache_key = CacheKeys.exchange_rate(from_currency, to_currency)
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        # Query database
        rate_record = self.db.query(ExchangeRate).filter(
            and_(
                ExchangeRate.from_currency == from_currency,
                ExchangeRate.to_currency == to_currency
            )
        ).order_by(desc(ExchangeRate.fetched_at)).first()
        
        if rate_record:
            # Cache the rate
            self.cache.set(cache_key, rate_record.rate, ttl=3600)
            return rate_record.rate
        
        return None
    
    def get_rate_history(
        self,
        from_currency: str,
        to_currency: str,
        days: int = 30
    ) -> List[ExchangeRate]:
        """Get exchange rate history"""
        
        since = datetime.utcnow() - timedelta(days=days)
        
        return self.db.query(ExchangeRate).filter(
            and_(
                ExchangeRate.from_currency == from_currency,
                ExchangeRate.to_currency == to_currency,
                ExchangeRate.fetched_at >= since
            )
        ).order_by(ExchangeRate.fetched_at).all()

class SessionRepository:
    """Repository for user sessions"""
    
    def __init__(self, db: Session):
        self.db = db
        self.cache = get_cache()
    
    def create_session(
        self,
        company_id: Optional[uuid.UUID],
        token: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        expires_hours: int = 24
    ) -> UserSession:
        """Create a new user session"""
        
        session = UserSession(
            company_id=company_id,
            session_token=token,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=datetime.utcnow() + timedelta(hours=expires_hours)
        )
        
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        
        # Cache session
        cache_key = f"session:{token}"
        self.cache.set(cache_key, session, ttl=expires_hours * 3600)
        
        return session
    
    def get_session(self, token: str) -> Optional[UserSession]:
        """Get session by token"""
        
        # Try cache first
        cache_key = f"session:{token}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        # Query database
        session = self.db.query(UserSession).filter(
            and_(
                UserSession.session_token == token,
                UserSession.expires_at > datetime.utcnow()
            )
        ).first()
        
        if session:
            # Update last activity
            session.last_activity = datetime.utcnow()
            self.db.commit()
            
            # Cache session
            remaining_ttl = int((session.expires_at - datetime.utcnow()).total_seconds())
            self.cache.set(cache_key, session, ttl=remaining_ttl)
        
        return session
    
    def invalidate_session(self, token: str) -> bool:
        """Invalidate a session"""
        
        session = self.db.query(UserSession).filter(
            UserSession.session_token == token
        ).first()
        
        if session:
            self.db.delete(session)
            self.db.commit()
            
            # Clear cache
            self.cache.delete(f"session:{token}")
            
            return True
        
        return False

class MetricsRepository:
    """Repository for performance metrics"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def save_metric(
        self,
        operation: str,
        duration_ms: float,
        success: bool = True,
        memory_mb: Optional[float] = None,
        cpu_percent: Optional[float] = None,
        error_message: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> PerformanceMetric:
        """Save performance metric"""
        
        metric = PerformanceMetric(
            operation=operation,
            duration_ms=duration_ms,
            success=success,
            memory_mb=memory_mb,
            cpu_percent=cpu_percent,
            error_message=error_message,
            metadata=metadata
        )
        
        self.db.add(metric)
        self.db.commit()
        
        return metric
    
    def get_metrics_summary(
        self,
        hours: int = 24
    ) -> Dict[str, Any]:
        """Get metrics summary for the last N hours"""
        
        since = datetime.utcnow() - timedelta(hours=hours)
        
        metrics = self.db.query(
            PerformanceMetric.operation,
            func.count(PerformanceMetric.id).label('count'),
            func.avg(PerformanceMetric.duration_ms).label('avg_duration'),
            func.max(PerformanceMetric.duration_ms).label('max_duration'),
            func.min(PerformanceMetric.duration_ms).label('min_duration'),
            func.avg(PerformanceMetric.memory_mb).label('avg_memory'),
            func.sum(
                func.cast(~PerformanceMetric.success, type_=Integer)
            ).label('errors')
        ).filter(
            PerformanceMetric.created_at >= since
        ).group_by(PerformanceMetric.operation).all()
        
        return {
            metric.operation: {
                'count': metric.count,
                'avg_duration_ms': float(metric.avg_duration) if metric.avg_duration else 0,
                'max_duration_ms': float(metric.max_duration) if metric.max_duration else 0,
                'min_duration_ms': float(metric.min_duration) if metric.min_duration else 0,
                'avg_memory_mb': float(metric.avg_memory) if metric.avg_memory else 0,
                'error_rate': (metric.errors / metric.count) if metric.count > 0 else 0
            }
            for metric in metrics
        }

class AuditRepository:
    """Repository for audit logging"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def log_action(
        self,
        action: str,
        company_id: Optional[uuid.UUID] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        old_values: Optional[Dict] = None,
        new_values: Optional[Dict] = None,
        user_ip: Optional[str] = None
    ) -> AuditLog:
        """Log an audit action"""
        
        audit = AuditLog(
            company_id=company_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            old_values=old_values,
            new_values=new_values,
            user_ip=user_ip
        )
        
        self.db.add(audit)
        self.db.commit()
        
        return audit
    
    def get_audit_trail(
        self,
        company_id: Optional[uuid.UUID] = None,
        action: Optional[str] = None,
        days: int = 7,
        limit: int = 100
    ) -> List[AuditLog]:
        """Get audit trail"""
        
        since = datetime.utcnow() - timedelta(days=days)
        
        query = self.db.query(AuditLog).filter(
            AuditLog.created_at >= since
        )
        
        if company_id:
            query = query.filter(AuditLog.company_id == company_id)
        
        if action:
            query = query.filter(AuditLog.action == action)
        
        return query.order_by(
            desc(AuditLog.created_at)
        ).limit(limit).all()
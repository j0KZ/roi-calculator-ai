#!/usr/bin/env python3
"""
Performance Monitor for ROI Calculator
Tracks application performance metrics and bottlenecks
"""

import time
import psutil
import logging
from typing import Dict, Any, List, Optional, Callable
from functools import wraps
from collections import deque, defaultdict
from datetime import datetime, timedelta
import json
from pathlib import Path
import threading

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """Monitors and tracks application performance metrics"""
    
    def __init__(self, max_history: int = 1000):
        """
        Initialize performance monitor
        
        Args:
            max_history: Maximum number of metrics to keep in history
        """
        self.max_history = max_history
        self.metrics_history = deque(maxlen=max_history)
        self.operation_stats = defaultdict(lambda: {
            'count': 0,
            'total_time': 0,
            'min_time': float('inf'),
            'max_time': 0,
            'errors': 0
        })
        self.current_operations = {}
        self.start_time = time.time()
        self._lock = threading.Lock()
        
        # System resource baseline
        self.baseline_memory = psutil.Process().memory_info().rss / 1024 / 1024
        self.baseline_cpu = psutil.cpu_percent(interval=1)
    
    def track_operation(self, operation_name: str, metadata: Optional[Dict] = None):
        """
        Context manager for tracking operation performance
        
        Usage:
            with monitor.track_operation('database_query', {'query': 'SELECT ...'}):
                # Perform operation
        """
        class OperationTracker:
            def __init__(tracker_self, monitor, name, meta):
                tracker_self.monitor = monitor
                tracker_self.name = name
                tracker_self.metadata = meta or {}
                tracker_self.start_time = None
                tracker_self.operation_id = None
            
            def __enter__(tracker_self):
                tracker_self.start_time = time.time()
                tracker_self.operation_id = f"{tracker_self.name}_{tracker_self.start_time}"
                
                with self._lock:
                    self.current_operations[tracker_self.operation_id] = {
                        'name': tracker_self.name,
                        'start_time': tracker_self.start_time,
                        'metadata': tracker_self.metadata
                    }
                
                return tracker_self
            
            def __exit__(tracker_self, exc_type, exc_val, exc_tb):
                end_time = time.time()
                duration = end_time - tracker_self.start_time
                
                with self._lock:
                    # Remove from current operations
                    if tracker_self.operation_id in self.current_operations:
                        del self.current_operations[tracker_self.operation_id]
                    
                    # Update statistics
                    stats = self.operation_stats[tracker_self.name]
                    stats['count'] += 1
                    stats['total_time'] += duration
                    stats['min_time'] = min(stats['min_time'], duration)
                    stats['max_time'] = max(stats['max_time'], duration)
                    
                    if exc_type is not None:
                        stats['errors'] += 1
                    
                    # Add to history
                    self.metrics_history.append({
                        'timestamp': datetime.now().isoformat(),
                        'operation': tracker_self.name,
                        'duration': duration,
                        'success': exc_type is None,
                        'metadata': tracker_self.metadata,
                        'memory_mb': psutil.Process().memory_info().rss / 1024 / 1024,
                        'cpu_percent': psutil.cpu_percent()
                    })
                
                # Log slow operations
                if duration > 1.0:
                    logger.warning(
                        f"Slow operation: {tracker_self.name} took {duration:.2f}s"
                    )
        
        return OperationTracker(self, operation_name, metadata)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current performance statistics"""
        with self._lock:
            # Calculate averages
            stats_summary = {}
            for operation, stats in self.operation_stats.items():
                if stats['count'] > 0:
                    stats_summary[operation] = {
                        'count': stats['count'],
                        'avg_time': stats['total_time'] / stats['count'],
                        'min_time': stats['min_time'],
                        'max_time': stats['max_time'],
                        'error_rate': stats['errors'] / stats['count'],
                        'total_time': stats['total_time']
                    }
            
            # System resources
            process = psutil.Process()
            memory_info = process.memory_info()
            
            return {
                'uptime': time.time() - self.start_time,
                'operations': stats_summary,
                'current_operations': len(self.current_operations),
                'system': {
                    'memory_mb': memory_info.rss / 1024 / 1024,
                    'memory_percent': process.memory_percent(),
                    'cpu_percent': process.cpu_percent(),
                    'threads': process.num_threads(),
                    'open_files': len(process.open_files()) if hasattr(process, 'open_files') else 0
                },
                'history_size': len(self.metrics_history)
            }
    
    def get_bottlenecks(self, threshold: float = 0.5) -> List[Dict[str, Any]]:
        """
        Identify performance bottlenecks
        
        Args:
            threshold: Time threshold in seconds for considering an operation slow
        
        Returns:
            List of bottleneck operations
        """
        bottlenecks = []
        
        with self._lock:
            for operation, stats in self.operation_stats.items():
                if stats['count'] > 0:
                    avg_time = stats['total_time'] / stats['count']
                    if avg_time > threshold or stats['max_time'] > threshold * 2:
                        bottlenecks.append({
                            'operation': operation,
                            'avg_time': avg_time,
                            'max_time': stats['max_time'],
                            'frequency': stats['count'],
                            'total_impact': stats['total_time'],
                            'error_rate': stats['errors'] / stats['count']
                        })
        
        # Sort by total impact
        bottlenecks.sort(key=lambda x: x['total_impact'], reverse=True)
        return bottlenecks
    
    def get_recent_slow_operations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent slow operations"""
        slow_ops = [
            m for m in self.metrics_history
            if m['duration'] > 0.5  # Operations taking more than 500ms
        ]
        
        # Return most recent
        return list(reversed(slow_ops))[:limit]
    
    def export_metrics(self, filepath: str):
        """Export metrics to JSON file"""
        with self._lock:
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'stats': self.get_stats(),
                'bottlenecks': self.get_bottlenecks(),
                'recent_slow': self.get_recent_slow_operations(),
                'history': list(self.metrics_history)
            }
        
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w') as f:
            json.dump(metrics, f, indent=2, default=str)
        
        logger.info(f"Exported metrics to {filepath}")
    
    def reset(self):
        """Reset all metrics"""
        with self._lock:
            self.metrics_history.clear()
            self.operation_stats.clear()
            self.current_operations.clear()
            self.start_time = time.time()
        
        logger.info("Performance metrics reset")


def performance_tracked(operation_name: Optional[str] = None):
    """
    Decorator for tracking function performance
    
    Args:
        operation_name: Name for the operation (defaults to function name)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get or create monitor
            if not hasattr(wrapper, '_monitor'):
                wrapper._monitor = PerformanceMonitor()
            
            name = operation_name or f"{func.__module__}.{func.__name__}"
            
            with wrapper._monitor.track_operation(name):
                return func(*args, **kwargs)
        
        # Attach monitor methods
        wrapper.get_stats = lambda: wrapper._monitor.get_stats()
        wrapper.get_bottlenecks = lambda: wrapper._monitor.get_bottlenecks()
        
        return wrapper
    return decorator


# Global performance monitor
_global_monitor = None

def get_monitor() -> PerformanceMonitor:
    """Get global performance monitor instance"""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = PerformanceMonitor()
    return _global_monitor


# Streamlit-specific performance tracking
def track_streamlit_operation(operation: str):
    """Track Streamlit-specific operations"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            monitor = get_monitor()
            
            # Add Streamlit-specific metadata
            metadata = {
                'page': func.__module__,
                'function': func.__name__
            }
            
            with monitor.track_operation(f"streamlit.{operation}", metadata):
                return func(*args, **kwargs)
        
        return wrapper
    return decorator


# Example usage for monitoring specific operations
class PerformanceMetrics:
    """Helper class for common performance metrics"""
    
    @staticmethod
    def log_page_load(page_name: str, load_time: float):
        """Log page load time"""
        monitor = get_monitor()
        monitor.metrics_history.append({
            'timestamp': datetime.now().isoformat(),
            'operation': 'page_load',
            'page': page_name,
            'duration': load_time,
            'success': True,
            'memory_mb': psutil.Process().memory_info().rss / 1024 / 1024,
            'cpu_percent': psutil.cpu_percent()
        })
        
        if load_time > 2.0:
            logger.warning(f"Slow page load: {page_name} took {load_time:.2f}s")
    
    @staticmethod
    def log_calculation(calc_type: str, duration: float, success: bool = True):
        """Log calculation performance"""
        monitor = get_monitor()
        stats = monitor.operation_stats[f"calculation.{calc_type}"]
        stats['count'] += 1
        stats['total_time'] += duration
        stats['min_time'] = min(stats['min_time'], duration)
        stats['max_time'] = max(stats['max_time'], duration)
        
        if not success:
            stats['errors'] += 1
    
    @staticmethod
    def get_dashboard_metrics() -> Dict[str, Any]:
        """Get metrics formatted for dashboard display"""
        monitor = get_monitor()
        stats = monitor.get_stats()
        
        return {
            'uptime_hours': stats['uptime'] / 3600,
            'total_operations': sum(
                s['count'] for s in stats['operations'].values()
            ),
            'avg_response_time': sum(
                s['avg_time'] * s['count'] for s in stats['operations'].values()
            ) / max(1, sum(s['count'] for s in stats['operations'].values())),
            'memory_usage_mb': stats['system']['memory_mb'],
            'cpu_usage': stats['system']['cpu_percent'],
            'error_rate': sum(
                s.get('error_rate', 0) * s['count'] 
                for s in stats['operations'].values()
            ) / max(1, sum(s['count'] for s in stats['operations'].values())),
            'bottlenecks': monitor.get_bottlenecks(threshold=1.0)
        }
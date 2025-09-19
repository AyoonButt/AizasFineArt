"""
Cache Metrics Model and Monitoring System
Tracks cache performance, hit/miss rates, and warming effectiveness
"""
from django.db import models
from django.utils import timezone
from django.core.cache import cache
from django.contrib.auth.models import User
import json
import logging
from typing import Dict, Optional, Any, List

logger = logging.getLogger(__name__)


class CachePerformanceAnalyzer:
    """Analyzes cache performance and generates reports"""
    
    @staticmethod
    def record_metric(metric_type: str, artwork_id: Optional[int] = None, 
                     response_time_ms: Optional[float] = None, 
                     metadata: Optional[Dict] = None):
        """Record a cache performance metric"""
        try:
            from .models import CacheMetric
            CacheMetric.objects.create(
                metric_type=metric_type,
                artwork_id=artwork_id,
                response_time_ms=response_time_ms,
                metadata=metadata or {}
            )
        except Exception as e:
            logger.warning(f"Failed to record cache metric: {str(e)}")
    
    @classmethod
    def get_cache_hit_rate(cls, hours: int = 24) -> float:
        """Calculate cache hit rate for the last N hours"""
        from .models import CacheMetric
        since = timezone.now() - timezone.timedelta(hours=hours)
        
        hits = CacheMetric.objects.filter(
            metric_type='hit',
            timestamp__gte=since
        ).count()
        
        misses = CacheMetric.objects.filter(
            metric_type='miss',
            timestamp__gte=since
        ).count()
        
        total = hits + misses
        return (hits / total * 100) if total > 0 else 0.0
    
    @classmethod
    def get_warming_success_rate(cls, hours: int = 24) -> float:
        """Calculate cache warming success rate"""
        from .models import CacheMetric
        since = timezone.now() - timezone.timedelta(hours=hours)
        
        successes = CacheMetric.objects.filter(
            metric_type='warming_success',
            timestamp__gte=since
        ).count()
        
        failures = CacheMetric.objects.filter(
            metric_type='warming_failure',
            timestamp__gte=since
        ).count()
        
        total = successes + failures
        return (successes / total * 100) if total > 0 else 0.0
    
    @classmethod
    def get_average_response_time(cls, hours: int = 24) -> float:
        """Calculate average response time for cache hits"""
        from .models import CacheMetric
        since = timezone.now() - timezone.timedelta(hours=hours)
        
        result = CacheMetric.objects.filter(
            metric_type='hit',
            timestamp__gte=since,
            response_time_ms__isnull=False
        ).aggregate(avg_time=models.Avg('response_time_ms'))
        
        return result['avg_time'] or 0.0
    
    @classmethod
    def get_top_cached_artworks(cls, hours: int = 24, limit: int = 10) -> List[Dict]:
        """Get most frequently cached artworks"""
        from .models import CacheMetric
        since = timezone.now() - timezone.timedelta(hours=hours)
        
        from django.db.models import Count
        results = CacheMetric.objects.filter(
            metric_type__in=['hit', 'miss'],
            artwork_id__isnull=False,
            timestamp__gte=since
        ).values('artwork_id').annotate(
            total_requests=Count('id'),
            hits=Count('id', filter=models.Q(metric_type='hit')),
            misses=Count('id', filter=models.Q(metric_type='miss'))
        ).order_by('-total_requests')[:limit]
        
        # Enrich with artwork details
        artwork_stats = []
        for result in results:
            try:
                from .models import Artwork
                artwork = Artwork.objects.get(id=result['artwork_id'])
                hit_rate = (result['hits'] / result['total_requests'] * 100) if result['total_requests'] > 0 else 0
                
                artwork_stats.append({
                    'artwork_id': result['artwork_id'],
                    'title': artwork.title,
                    'total_requests': result['total_requests'],
                    'hit_rate': hit_rate,
                    'hits': result['hits'],
                    'misses': result['misses']
                })
            except Exception:
                continue
                
        return artwork_stats
    
    @classmethod
    def get_thread_pool_stats(cls, hours: int = 24) -> Dict[str, Any]:
        """Get thread pool performance statistics"""
        from .models import CacheMetric
        since = timezone.now() - timezone.timedelta(hours=hours)
        
        thread_metrics = CacheMetric.objects.filter(
            metric_type='thread_pool_task',
            timestamp__gte=since
        )
        
        total_tasks = thread_metrics.count()
        avg_time = thread_metrics.aggregate(
            avg_time=models.Avg('response_time_ms')
        )['avg_time'] or 0.0
        
        # Get current thread pool stats from cache
        from .thread_manager import thread_manager
        current_stats = thread_manager.get_stats()
        
        return {
            'total_tasks_completed': total_tasks,
            'average_task_time_ms': avg_time,
            'current_active_threads': current_stats.get('active_threads', 0),
            'current_queue_size': current_stats.get('queue_size', 0),
            'total_submitted': current_stats.get('total_submitted', 0),
            'total_failed': current_stats.get('total_failed', 0)
        }
    
    @classmethod
    def generate_performance_report(cls, hours: int = 24) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        return {
            'period_hours': hours,
            'timestamp': timezone.now().isoformat(),
            'cache_hit_rate': cls.get_cache_hit_rate(hours),
            'warming_success_rate': cls.get_warming_success_rate(hours),
            'average_response_time_ms': cls.get_average_response_time(hours),
            'top_cached_artworks': cls.get_top_cached_artworks(hours),
            'thread_pool_stats': cls.get_thread_pool_stats(hours),
            'api_call_reduction': cls._calculate_api_reduction(hours)
        }
    
    @classmethod
    def _calculate_api_reduction(cls, hours: int = 24) -> Dict[str, Any]:
        """Calculate estimated API call reduction from caching"""
        from .models import CacheMetric
        since = timezone.now() - timezone.timedelta(hours=hours)
        
        hits = CacheMetric.objects.filter(
            metric_type='hit',
            timestamp__gte=since
        ).count()
        
        api_calls = CacheMetric.objects.filter(
            metric_type='api_call',
            timestamp__gte=since
        ).count()
        
        # Estimate calls that would have been made without caching
        estimated_without_cache = hits + api_calls
        reduction_percentage = (hits / estimated_without_cache * 100) if estimated_without_cache > 0 else 0
        
        return {
            'actual_api_calls': api_calls,
            'cache_hits_avoided_calls': hits,
            'estimated_calls_without_cache': estimated_without_cache,
            'reduction_percentage': reduction_percentage
        }
    
    @classmethod
    def cleanup_old_metrics(cls, days: int = 30):
        """Clean up old metrics to prevent database bloat"""
        from .models import CacheMetric
        cutoff = timezone.now() - timezone.timedelta(days=days)
        deleted_count = CacheMetric.objects.filter(timestamp__lt=cutoff).delete()[0]
        logger.info(f"Cleaned up {deleted_count} cache metrics older than {days} days")
        return deleted_count


class CacheHealthMonitor:
    """Monitors cache health and sends alerts"""
    
    WARNING_THRESHOLDS = {
        'low_hit_rate': 70.0,  # Below 70% hit rate
        'high_warming_failure': 10.0,  # Above 10% warming failure rate
        'slow_response_time': 1000.0,  # Above 1 second average response
        'high_thread_usage': 80.0,  # Above 80% thread pool utilization
    }
    
    @classmethod
    def check_health(cls) -> Dict[str, Any]:
        """Perform health checks and return status"""
        analyzer = CachePerformanceAnalyzer()
        
        hit_rate = analyzer.get_cache_hit_rate(1)  # Last hour
        warming_success = analyzer.get_warming_success_rate(1)
        avg_response = analyzer.get_average_response_time(1)
        thread_stats = analyzer.get_thread_pool_stats(1)
        
        warnings = []
        errors = []
        
        # Check hit rate
        if hit_rate < cls.WARNING_THRESHOLDS['low_hit_rate']:
            warnings.append(f"Low cache hit rate: {hit_rate:.1f}% (threshold: {cls.WARNING_THRESHOLDS['low_hit_rate']}%)")
        
        # Check warming failure rate
        warming_failure_rate = 100 - warming_success
        if warming_failure_rate > cls.WARNING_THRESHOLDS['high_warming_failure']:
            warnings.append(f"High warming failure rate: {warming_failure_rate:.1f}%")
        
        # Check response time
        if avg_response > cls.WARNING_THRESHOLDS['slow_response_time']:
            warnings.append(f"Slow average response time: {avg_response:.1f}ms")
        
        # Check thread pool utilization
        from .thread_manager import thread_manager
        max_workers = thread_manager.max_workers
        active_threads = thread_stats.get('current_active_threads', 0)
        utilization = (active_threads / max_workers * 100) if max_workers > 0 else 0
        
        if utilization > cls.WARNING_THRESHOLDS['high_thread_usage']:
            warnings.append(f"High thread pool utilization: {utilization:.1f}%")
        
        status = 'healthy'
        if errors:
            status = 'error'
        elif warnings:
            status = 'warning'
        
        return {
            'status': status,
            'timestamp': timezone.now().isoformat(),
            'metrics': {
                'hit_rate': hit_rate,
                'warming_success_rate': warming_success,
                'avg_response_time_ms': avg_response,
                'thread_pool_utilization': utilization
            },
            'warnings': warnings,
            'errors': errors
        }
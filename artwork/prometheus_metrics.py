"""
Prometheus Metrics Integration for Cache Performance
Exposes cache metrics to Prometheus monitoring system
"""
from django.http import HttpResponse
from django.conf import settings
import json
import time
from typing import Dict, List
from .cache_metrics import CachePerformanceAnalyzer
from .thread_manager import thread_manager


class PrometheusMetricsExporter:
    """Export cache metrics in Prometheus format"""
    
    @staticmethod
    def get_metrics_response() -> HttpResponse:
        """Generate Prometheus metrics response"""
        metrics = PrometheusMetricsExporter._collect_metrics()
        content = PrometheusMetricsExporter._format_prometheus_metrics(metrics)
        
        return HttpResponse(
            content,
            content_type='text/plain; version=0.0.4; charset=utf-8'
        )
    
    @staticmethod
    def _collect_metrics() -> Dict:
        """Collect all cache-related metrics"""
        analyzer = CachePerformanceAnalyzer()
        
        # Get basic performance metrics
        metrics = {
            'cache_hit_rate': analyzer.get_cache_hit_rate(1),  # Last hour
            'cache_hit_rate_24h': analyzer.get_cache_hit_rate(24),  # Last 24 hours
            'warming_success_rate': analyzer.get_warming_success_rate(1),
            'avg_response_time_ms': analyzer.get_average_response_time(1),
            'thread_pool_stats': analyzer.get_thread_pool_stats(1)
        }
        
        # Get current thread pool state
        thread_stats = thread_manager.get_stats()
        metrics['current_thread_stats'] = thread_stats
        
        return metrics
    
    @staticmethod
    def _format_prometheus_metrics(metrics: Dict) -> str:
        """Format metrics in Prometheus exposition format"""
        timestamp = int(time.time() * 1000)  # Milliseconds
        
        lines = []
        
        # Cache hit rate
        lines.extend([
            "# HELP cache_hit_rate_percent Cache hit rate as percentage",
            "# TYPE cache_hit_rate_percent gauge",
            f'cache_hit_rate_percent{{period="1h"}} {metrics["cache_hit_rate"]:.2f} {timestamp}',
            f'cache_hit_rate_percent{{period="24h"}} {metrics["cache_hit_rate_24h"]:.2f} {timestamp}',
        ])
        
        # Cache warming success rate
        lines.extend([
            "# HELP cache_warming_success_rate_percent Cache warming success rate as percentage",
            "# TYPE cache_warming_success_rate_percent gauge",
            f'cache_warming_success_rate_percent {metrics["warming_success_rate"]:.2f} {timestamp}',
        ])
        
        # Response time
        lines.extend([
            "# HELP cache_response_time_ms Average cache response time in milliseconds",
            "# TYPE cache_response_time_ms gauge",
            f'cache_response_time_ms {metrics["avg_response_time_ms"]:.2f} {timestamp}',
        ])
        
        # Thread pool metrics
        thread_stats = metrics['current_thread_stats']
        lines.extend([
            "# HELP thread_pool_active_threads Number of currently active threads",
            "# TYPE thread_pool_active_threads gauge",
            f'thread_pool_active_threads {thread_stats.get("active_threads", 0)} {timestamp}',
            
            "# HELP thread_pool_queue_size Number of tasks in thread pool queue",
            "# TYPE thread_pool_queue_size gauge",
            f'thread_pool_queue_size {thread_stats.get("queue_size", 0)} {timestamp}',
            
            "# HELP thread_pool_total_submitted Total number of tasks submitted",
            "# TYPE thread_pool_total_submitted counter",
            f'thread_pool_total_submitted {thread_stats.get("total_submitted", 0)} {timestamp}',
            
            "# HELP thread_pool_total_completed Total number of tasks completed",
            "# TYPE thread_pool_total_completed counter",
            f'thread_pool_total_completed {thread_stats.get("total_completed", 0)} {timestamp}',
            
            "# HELP thread_pool_total_failed Total number of tasks failed",
            "# TYPE thread_pool_total_failed counter",
            f'thread_pool_total_failed {thread_stats.get("total_failed", 0)} {timestamp}',
        ])
        
        # Add application info
        lines.extend([
            "# HELP app_info Application information",
            "# TYPE app_info gauge",
            f'app_info{{version="1.0",component="cache_system"}} 1 {timestamp}',
        ])
        
        return '\n'.join(lines) + '\n'


def metrics_view(request):
    """Django view for Prometheus metrics endpoint"""
    # Optional: Add authentication/IP filtering for security
    if hasattr(settings, 'PROMETHEUS_ALLOWED_IPS'):
        client_ip = request.META.get('REMOTE_ADDR')
        if client_ip not in settings.PROMETHEUS_ALLOWED_IPS:
            return HttpResponse('Forbidden', status=403)
    
    return PrometheusMetricsExporter.get_metrics_response()


class MetricsCollector:
    """Simplified metrics collector for non-Prometheus setups"""
    
    @staticmethod
    def collect_json_metrics() -> Dict:
        """Collect metrics in JSON format"""
        analyzer = CachePerformanceAnalyzer()
        thread_stats = thread_manager.get_stats()
        
        return {
            'timestamp': int(time.time()),
            'cache': {
                'hit_rate_1h': analyzer.get_cache_hit_rate(1),
                'hit_rate_24h': analyzer.get_cache_hit_rate(24),
                'warming_success_rate': analyzer.get_warming_success_rate(1),
                'avg_response_time_ms': analyzer.get_average_response_time(1),
            },
            'thread_pool': {
                'active_threads': thread_stats.get('active_threads', 0),
                'queue_size': thread_stats.get('queue_size', 0),
                'total_submitted': thread_stats.get('total_submitted', 0),
                'total_completed': thread_stats.get('total_completed', 0),
                'total_failed': thread_stats.get('total_failed', 0),
            }
        }


def json_metrics_view(request):
    """Django view for JSON metrics endpoint"""
    metrics = MetricsCollector.collect_json_metrics()
    return HttpResponse(
        json.dumps(metrics, indent=2),
        content_type='application/json'
    )
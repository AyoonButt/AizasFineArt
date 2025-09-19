"""
URL Configuration for Cache Metrics and Monitoring Endpoints
"""
from django.urls import path
from .prometheus_metrics import metrics_view, json_metrics_view

urlpatterns = [
    # Prometheus metrics endpoint
    path('prometheus/', metrics_view, name='prometheus_metrics'),
    
    # JSON metrics endpoint
    path('json/', json_metrics_view, name='json_metrics'),
    
    # Health check endpoint
    path('health/', json_metrics_view, name='health_check'),  # Reuse JSON metrics for now
]
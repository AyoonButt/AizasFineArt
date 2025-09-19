"""
Django management command to display cache statistics and performance metrics
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
import json
from artwork.cache_metrics import CachePerformanceAnalyzer, CacheHealthMonitor


class Command(BaseCommand):
    help = 'Display cache statistics and performance metrics'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--hours',
            type=int,
            default=24,
            help='Number of hours to analyze (default: 24)'
        )
        parser.add_argument(
            '--format',
            type=str,
            choices=['table', 'json'],
            default='table',
            help='Output format (default: table)'
        )
        parser.add_argument(
            '--health-check',
            action='store_true',
            help='Perform cache health check'
        )
        parser.add_argument(
            '--cleanup-days',
            type=int,
            help='Clean up metrics older than N days'
        )
    
    def handle(self, *args, **options):
        hours = options['hours']
        output_format = options['format']
        
        if options['cleanup_days']:
            deleted = CachePerformanceAnalyzer.cleanup_old_metrics(options['cleanup_days'])
            self.stdout.write(
                self.style.SUCCESS(f'✓ Cleaned up {deleted} old cache metrics')
            )
            return
        
        if options['health_check']:
            self.display_health_check()
            return
        
        # Generate performance report
        analyzer = CachePerformanceAnalyzer()
        report = analyzer.generate_performance_report(hours)
        
        if output_format == 'json':
            self.stdout.write(json.dumps(report, indent=2, default=str))
        else:
            self.display_table_format(report)
    
    def display_health_check(self):
        """Display cache health check results"""
        health = CacheHealthMonitor.check_health()
        
        # Status indicator
        if health['status'] == 'healthy':
            status_style = self.style.SUCCESS
            status_icon = '✓'
        elif health['status'] == 'warning':
            status_style = self.style.WARNING
            status_icon = '⚠'
        else:
            status_style = self.style.ERROR
            status_icon = '✗'
        
        self.stdout.write(
            status_style(f'{status_icon} Cache Health Status: {health["status"].upper()}')
        )
        self.stdout.write('')
        
        # Current metrics
        metrics = health['metrics']
        self.stdout.write(self.style.HTTP_INFO('📊 Current Metrics:'))
        self.stdout.write(f'  Hit Rate: {metrics["hit_rate"]:.1f}%')
        self.stdout.write(f'  Warming Success Rate: {metrics["warming_success_rate"]:.1f}%')
        self.stdout.write(f'  Avg Response Time: {metrics["avg_response_time_ms"]:.1f}ms')
        self.stdout.write(f'  Thread Pool Utilization: {metrics["thread_pool_utilization"]:.1f}%')
        self.stdout.write('')
        
        # Warnings
        if health['warnings']:
            self.stdout.write(self.style.WARNING('⚠ Warnings:'))
            for warning in health['warnings']:
                self.stdout.write(f'  • {warning}')
            self.stdout.write('')
        
        # Errors
        if health['errors']:
            self.stdout.write(self.style.ERROR('✗ Errors:'))
            for error in health['errors']:
                self.stdout.write(f'  • {error}')
    
    def display_table_format(self, report):
        """Display report in table format"""
        self.stdout.write(
            self.style.HTTP_INFO(f'🔥 Cache Performance Report - Last {report["period_hours"]} Hours')
        )
        self.stdout.write('')
        
        # Overall metrics
        self.stdout.write(self.style.HTTP_INFO('📈 Overall Performance:'))
        self.stdout.write(f'  Cache Hit Rate: {report["cache_hit_rate"]:.1f}%')
        self.stdout.write(f'  Cache Warming Success Rate: {report["warming_success_rate"]:.1f}%')
        self.stdout.write(f'  Average Response Time: {report["average_response_time_ms"]:.1f}ms')
        self.stdout.write('')
        
        # API call reduction
        api_reduction = report['api_call_reduction']
        self.stdout.write(self.style.HTTP_INFO('🎯 API Call Efficiency:'))
        self.stdout.write(f'  Actual API Calls: {api_reduction["actual_api_calls"]}')
        self.stdout.write(f'  Cache Hits (Avoided Calls): {api_reduction["cache_hits_avoided_calls"]}')
        self.stdout.write(f'  Reduction: {api_reduction["reduction_percentage"]:.1f}%')
        self.stdout.write('')
        
        # Thread pool stats
        thread_stats = report['thread_pool_stats']
        self.stdout.write(self.style.HTTP_INFO('🔄 Thread Pool Performance:'))
        self.stdout.write(f'  Tasks Completed: {thread_stats["total_tasks_completed"]}')
        self.stdout.write(f'  Average Task Time: {thread_stats["average_task_time_ms"]:.1f}ms')
        self.stdout.write(f'  Current Active Threads: {thread_stats["current_active_threads"]}')
        self.stdout.write(f'  Current Queue Size: {thread_stats["current_queue_size"]}')
        self.stdout.write(f'  Total Failed: {thread_stats["total_failed"]}')
        self.stdout.write('')
        
        # Top cached artworks
        top_artworks = report['top_cached_artworks']
        if top_artworks:
            self.stdout.write(self.style.HTTP_INFO('🖼️  Top Cached Artworks:'))
            self.stdout.write(f'{"Title":<30} {"Requests":<10} {"Hit Rate":<10} {"Status"}')
            self.stdout.write('-' * 65)
            
            for artwork in top_artworks:
                title = artwork['title'][:29] if len(artwork['title']) > 29 else artwork['title']
                hit_rate = f"{artwork['hit_rate']:.1f}%"
                
                # Status based on hit rate
                if artwork['hit_rate'] >= 80:
                    status = self.style.SUCCESS('Excellent')
                elif artwork['hit_rate'] >= 60:
                    status = self.style.WARNING('Good')
                else:
                    status = self.style.ERROR('Poor')
                
                self.stdout.write(
                    f'{title:<30} {artwork["total_requests"]:<10} {hit_rate:<10} {status}'
                )
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('✓ Cache performance analysis complete'))
        
        # Recommendations
        self.show_recommendations(report)
    
    def show_recommendations(self, report):
        """Show performance recommendations"""
        recommendations = []
        
        if report['cache_hit_rate'] < 70:
            recommendations.append('Consider increasing cache warming frequency')
        
        if report['warming_success_rate'] < 90:
            recommendations.append('Check Supabase connection stability')
        
        if report['average_response_time_ms'] > 1000:
            recommendations.append('Investigate slow response times')
        
        thread_stats = report['thread_pool_stats']
        if thread_stats['total_failed'] > thread_stats['total_tasks_completed'] * 0.1:
            recommendations.append('High thread failure rate - check error logs')
        
        if recommendations:
            self.stdout.write(self.style.HTTP_INFO('💡 Recommendations:'))
            for rec in recommendations:
                self.stdout.write(f'  • {rec}')
            self.stdout.write('')
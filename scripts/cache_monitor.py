#!/usr/bin/env python3
"""
Cache Monitoring and Diagnostics Script for Aiza's Fine Art
Provides comprehensive cache warming system monitoring and health checks
"""

import os
import sys
import json
import datetime
import argparse
from pathlib import Path

# Add Django project to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aizasfineart.settings')
import django
django.setup()

from django.utils import timezone
from django.core.cache import cache
from artwork.models import Artwork
import logging

logger = logging.getLogger(__name__)


class CacheMonitor:
    """Monitor and analyze cache warming system performance"""
    
    def __init__(self):
        self.stats = {
            'timestamp': timezone.now().isoformat(),
            'cache_status': {},
            'warming_systems': {},
            'recommendations': []
        }
    
    def check_artwork_cache_health(self):
        """Check the health of artwork URL caches"""
        try:
            artworks = Artwork.objects.filter(is_active=True)
            total_count = artworks.count()
            
            cached_count = artworks.exclude(_cached_image_url__isnull=True).exclude(_cached_image_url='').count()
            
            # Check expiration status
            now = timezone.now()
            soon_expire = artworks.filter(
                _url_cache_expires__lt=now + timezone.timedelta(hours=2),
                _url_cache_expires__gt=now
            ).count()
            
            expired = artworks.filter(_url_cache_expires__lt=now).count()
            
            cache_hit_rate = (cached_count / total_count * 100) if total_count > 0 else 0
            
            self.stats['cache_status'] = {
                'total_artworks': total_count,
                'cached_artworks': cached_count,
                'cache_hit_rate': round(cache_hit_rate, 2),
                'expiring_soon': soon_expire,
                'expired': expired,
                'health_status': 'good' if cache_hit_rate > 80 else 'poor' if cache_hit_rate < 50 else 'fair'
            }
            
            # Add recommendations
            if cache_hit_rate < 80:
                self.stats['recommendations'].append(
                    f"Low cache hit rate ({cache_hit_rate:.1f}%) - consider running warm_all_cache"
                )
            
            if expired > 5:
                self.stats['recommendations'].append(
                    f"{expired} artworks have expired cache - run refresh_image_urls"
                )
                
        except Exception as e:
            self.stats['cache_status'] = {'error': str(e)}
            logger.error(f"Cache health check failed: {e}")
    
    def check_warming_systems(self):
        """Check status of all cache warming systems"""
        
        # Check background warming status
        try:
            last_warmed = cache.get('artwork_cache_last_warmed')
            if last_warmed:
                hours_since = (timezone.now() - last_warmed).total_seconds() / 3600
                background_status = 'recent' if hours_since < 2 else 'stale'
            else:
                background_status = 'unknown'
                
            self.stats['warming_systems']['background_auto'] = {
                'status': background_status,
                'last_run': last_warmed.isoformat() if last_warmed else None,
                'hours_since': round(hours_since, 1) if last_warmed else None
            }
        except Exception as e:
            self.stats['warming_systems']['background_auto'] = {'error': str(e)}
        
        # Check cron job status (if available)
        try:
            import subprocess
            result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
            if result.returncode == 0 and 'warm_featured_cache' in result.stdout:
                cron_status = 'configured'
            else:
                cron_status = 'not_configured'
                
            self.stats['warming_systems']['cron_jobs'] = {
                'status': cron_status,
                'details': 'Featured cache warming scheduled' if cron_status == 'configured' else 'No cron jobs found'
            }
        except Exception as e:
            self.stats['warming_systems']['cron_jobs'] = {'error': str(e)}
        
        # Check management commands
        try:
            from django.core.management import get_commands
            commands = get_commands()
            
            warming_commands = [cmd for cmd in commands if 'warm' in cmd or 'cache' in cmd]
            self.stats['warming_systems']['management_commands'] = {
                'available': warming_commands,
                'status': 'available' if warming_commands else 'missing'
            }
        except Exception as e:
            self.stats['warming_systems']['management_commands'] = {'error': str(e)}
    
    def check_featured_artworks(self):
        """Check specific status of featured artworks (highest priority)"""
        try:
            featured = Artwork.objects.filter(is_active=True, is_featured=True)
            total_featured = featured.count()
            
            if total_featured == 0:
                self.stats['featured_status'] = {'message': 'No featured artworks found'}
                return
            
            cached_featured = featured.exclude(_cached_image_url__isnull=True).exclude(_cached_image_url='').count()
            
            # Check cache freshness for featured artworks
            now = timezone.now()
            fresh_cache = featured.filter(
                _url_cache_expires__gt=now + timezone.timedelta(hours=2)
            ).count()
            
            self.stats['featured_status'] = {
                'total': total_featured,
                'cached': cached_featured,
                'fresh_cache': fresh_cache,
                'cache_rate': round((cached_featured / total_featured * 100), 2) if total_featured > 0 else 0,
                'freshness_rate': round((fresh_cache / total_featured * 100), 2) if total_featured > 0 else 0
            }
            
            if cached_featured < total_featured:
                self.stats['recommendations'].append(
                    f"Featured artworks cache incomplete ({cached_featured}/{total_featured}) - run warm_featured_cache"
                )
                
        except Exception as e:
            self.stats['featured_status'] = {'error': str(e)}
    
    def generate_report(self, format='text'):
        """Generate formatted monitoring report"""
        if format == 'json':
            return json.dumps(self.stats, indent=2, default=str)
        
        # Text format
        report = []
        report.append("🔥 CACHE WARMING SYSTEM MONITOR")
        report.append("=" * 40)
        report.append(f"Timestamp: {self.stats['timestamp']}")
        report.append("")
        
        # Cache status
        if 'cache_status' in self.stats:
            status = self.stats['cache_status']
            if 'error' not in status:
                report.append("📊 CACHE STATUS:")
                report.append(f"  Total Artworks: {status['total_artworks']}")
                report.append(f"  Cached: {status['cached_artworks']} ({status['cache_hit_rate']}%)")
                report.append(f"  Expiring Soon: {status['expiring_soon']}")
                report.append(f"  Expired: {status['expired']}")
                report.append(f"  Health: {status['health_status'].upper()}")
            else:
                report.append(f"❌ CACHE STATUS ERROR: {status['error']}")
            report.append("")
        
        # Featured artworks
        if 'featured_status' in self.stats:
            featured = self.stats['featured_status']
            if 'error' not in featured:
                report.append("⭐ FEATURED ARTWORKS:")
                if 'total' in featured:
                    report.append(f"  Total Featured: {featured['total']}")
                    report.append(f"  Cached: {featured['cached']} ({featured['cache_rate']}%)")
                    report.append(f"  Fresh Cache: {featured['fresh_cache']} ({featured['freshness_rate']}%)")
                else:
                    report.append(f"  {featured['message']}")
            else:
                report.append(f"❌ FEATURED STATUS ERROR: {featured['error']}")
            report.append("")
        
        # Warming systems
        if 'warming_systems' in self.stats:
            report.append("🔧 WARMING SYSTEMS:")
            systems = self.stats['warming_systems']
            
            for system, info in systems.items():
                if 'error' not in info:
                    report.append(f"  {system.replace('_', ' ').title()}: {info.get('status', 'unknown')}")
                    if 'details' in info:
                        report.append(f"    {info['details']}")
                    if 'last_run' in info and info['last_run']:
                        report.append(f"    Last run: {info['last_run']}")
                else:
                    report.append(f"  {system.replace('_', ' ').title()}: ERROR - {info['error']}")
            report.append("")
        
        # Recommendations
        if self.stats.get('recommendations'):
            report.append("💡 RECOMMENDATIONS:")
            for rec in self.stats['recommendations']:
                report.append(f"  • {rec}")
            report.append("")
        
        return "\n".join(report)
    
    def run_diagnostics(self):
        """Run all diagnostic checks"""
        print("Running cache warming diagnostics...")
        
        self.check_artwork_cache_health()
        self.check_warming_systems()
        self.check_featured_artworks()
        
        return self.stats


def main():
    parser = argparse.ArgumentParser(description='Monitor cache warming system health')
    parser.add_argument('--format', choices=['text', 'json'], default='text',
                       help='Output format (default: text)')
    parser.add_argument('--output', help='Output file path (default: stdout)')
    
    args = parser.parse_args()
    
    monitor = CacheMonitor()
    monitor.run_diagnostics()
    
    report = monitor.generate_report(args.format)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"Report saved to: {args.output}")
    else:
        print(report)


if __name__ == '__main__':
    main()
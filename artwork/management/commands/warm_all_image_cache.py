#!/usr/bin/env python3
"""
Comprehensive Image URL Cache Warming Command
Aggressively pre-caches ALL image URLs to eliminate runtime Supabase API calls
"""

import time
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from artwork.models import Artwork
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

class Command(BaseCommand):
    help = 'Aggressively warm all image URL caches for sub-3-second performance'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--batch-size',
            type=int,
            default=10,
            help='Number of artworks to process concurrently'
        )
        parser.add_argument(
            '--force-refresh',
            action='store_true',
            help='Force refresh all URLs even if cached'
        )
        parser.add_argument(
            '--featured-only',
            action='store_true',
            help='Only warm cache for featured artworks (fastest)'
        )
    
    def handle(self, *args, **options):
        start_time = time.time()
        self.stdout.write(self.style.SUCCESS('🚀 Starting Aggressive Image Cache Warming'))
        
        # Get artworks to process
        if options['featured_only']:
            artworks = Artwork.objects.filter(is_featured=True, is_active=True)
            self.stdout.write(f'📊 Processing {artworks.count()} featured artworks')
        else:
            artworks = Artwork.objects.filter(is_active=True)
            self.stdout.write(f'📊 Processing {artworks.count()} total artworks')
        
        # Warm main image URLs
        self.warm_main_images(artworks, options)
        
        # Warm frame image URLs
        self.warm_frame_images(artworks, options)
        
        total_time = time.time() - start_time
        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Cache warming completed in {total_time:.2f} seconds'
            )
        )
        
        # Verify cache effectiveness
        self.verify_cache_performance()
    
    def warm_main_images(self, artworks, options):
        """Warm main image URL cache with concurrent processing"""
        self.stdout.write('🔥 Warming main image URLs...')
        
        def warm_single_artwork(artwork):
            try:
                # Force refresh if requested or cache expired
                if (options['force_refresh'] or 
                    not artwork._cached_image_url or 
                    not artwork._url_cache_expires or
                    timezone.now() > (artwork._url_cache_expires - timedelta(hours=1))):
                    
                    # Generate fresh URL
                    url = artwork.get_simple_signed_url(expires_in=3600)
                    return {
                        'id': artwork.id,
                        'title': artwork.title,
                        'url': url,
                        'status': 'refreshed'
                    }
                else:
                    return {
                        'id': artwork.id,
                        'title': artwork.title,
                        'url': artwork._cached_image_url,
                        'status': 'cached'
                    }
            except Exception as e:
                return {
                    'id': artwork.id,
                    'title': artwork.title,
                    'error': str(e),
                    'status': 'failed'
                }
        
        # Process concurrently
        batch_size = options['batch_size']
        success_count = 0
        failed_count = 0
        
        with ThreadPoolExecutor(max_workers=batch_size) as executor:
            future_to_artwork = {
                executor.submit(warm_single_artwork, artwork): artwork 
                for artwork in artworks
            }
            
            for future in as_completed(future_to_artwork):
                result = future.result()
                
                if 'error' in result:
                    failed_count += 1
                    self.stdout.write(
                        self.style.ERROR(
                            f'❌ Failed {result["title"]}: {result["error"]}'
                        )
                    )
                else:
                    success_count += 1
                    if result['status'] == 'refreshed':
                        self.stdout.write(f'🔄 Refreshed: {result["title"]}')
                    else:
                        self.stdout.write(f'✅ Cached: {result["title"]}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'📊 Main images: {success_count} success, {failed_count} failed'
            )
        )
    
    def warm_frame_images(self, artworks, options):
        """Warm frame image URL cache"""
        self.stdout.write('🖼️  Warming frame image URLs...')
        
        frame_count = 0
        
        for artwork in artworks:
            for frame_num in range(1, 5):  # frames 1-4
                frame_url_field = f'frame{frame_num}_image_url'
                if hasattr(artwork, frame_url_field) and getattr(artwork, frame_url_field):
                    try:
                        # Pre-cache frame URL
                        frame_url = artwork.get_frame_simple_url(frame_num)
                        if frame_url:
                            frame_count += 1
                            self.stdout.write(f'🖼️  Cached frame {frame_num} for {artwork.title}')
                    except Exception as e:
                        self.stdout.write(
                            self.style.WARNING(
                                f'⚠️  Frame {frame_num} failed for {artwork.title}: {e}'
                            )
                        )
        
        self.stdout.write(
            self.style.SUCCESS(f'📊 Frame images cached: {frame_count}')
        )
    
    def verify_cache_performance(self):
        """Verify cache effectiveness with performance test"""
        self.stdout.write('🧪 Testing cache performance...')
        
        # Test featured artworks (most critical for homepage)
        featured_artworks = Artwork.objects.filter(is_featured=True, is_active=True)[:5]
        
        total_time = 0
        for artwork in featured_artworks:
            start = time.time()
            url = artwork.get_simple_signed_url()
            end = time.time()
            
            access_time = (end - start) * 1000  # Convert to milliseconds
            total_time += access_time
            
            if access_time < 10:  # Sub-10ms is excellent
                self.stdout.write(f'⚡ {artwork.title}: {access_time:.1f}ms (cached)')
            elif access_time < 50:  # Sub-50ms is good
                self.stdout.write(f'🟡 {artwork.title}: {access_time:.1f}ms (acceptable)')
            else:
                self.stdout.write(
                    self.style.WARNING(f'🔴 {artwork.title}: {access_time:.1f}ms (slow)')
                )
        
        avg_time = total_time / len(featured_artworks)
        self.stdout.write(
            self.style.SUCCESS(
                f'📊 Average URL access time: {avg_time:.1f}ms'
            )
        )
        
        if avg_time < 10:
            self.stdout.write(
                self.style.SUCCESS(
                    '🎯 EXCELLENT: Cache performance optimal for sub-3s page loads'
                )
            )
        elif avg_time < 50:
            self.stdout.write(
                self.style.WARNING(
                    '⚠️  GOOD: Cache performance acceptable but could be improved'
                )
            )
        else:
            self.stdout.write(
                self.style.ERROR(
                    '❌ POOR: Cache performance needs optimization'
                )
            )
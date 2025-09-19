from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import models
from artwork.models import Artwork
from artwork.async_cache import run_async_cache_warming
import time


class Command(BaseCommand):
    help = 'Pre-warm URL cache for featured artworks to improve API performance (with async optimization)'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--force', 
            action='store_true',
            help='Force refresh of all cached URLs, even if not expired'
        )
        parser.add_argument(
            '--async',
            action='store_true',
            help='Use async batch processing for better performance'
        )
    
    def handle(self, *args, **options):
        use_async = options.get('async', False)
        force = options.get('force', False)
        
        self.stdout.write('Warming URL cache for featured artworks...')
        start_time = time.time()
        
        # Get featured artworks that need warming
        if force:
            # If forcing, get all featured artworks
            featured_artworks = Artwork.objects.filter(
                is_active=True,
                is_featured=True
            ).order_by('-created_at')[:20]
            artwork_ids = list(featured_artworks.values_list('id', flat=True))
        else:
            # Only get artworks that need warming
            now = timezone.now()
            featured_artworks = Artwork.objects.filter(
                is_active=True,
                is_featured=True
            ).filter(
                # Cache expired or missing
                models.Q(_cached_image_url__isnull=True) |
                models.Q(_url_cache_expires__isnull=True) |
                models.Q(_url_cache_expires__lt=now + timezone.timedelta(minutes=10))
            ).order_by('-created_at')[:20]
            artwork_ids = list(featured_artworks.values_list('id', flat=True))
        
        total_count = len(artwork_ids)
        
        if not artwork_ids:
            self.stdout.write(self.style.SUCCESS('✓ All featured artworks already have warm cache'))
            return
        
        if use_async:
            # Use async batch processing
            self.stdout.write(f'Using async batch processing for {total_count} artworks...')
            
            try:
                results = run_async_cache_warming(artwork_ids, force=force)
                
                duration = time.time() - start_time
                
                self.stdout.write('')
                self.stdout.write(f'📊 Batch Results:')
                self.stdout.write(f'  Processed: {results["total_processed"]}')
                self.stdout.write(f'  Successful: {results["successful"]}')
                self.stdout.write(f'  Failed: {results["failed"]}')
                self.stdout.write(f'  Duration: {duration:.2f}s')
                
                if results['errors']:
                    self.stdout.write(self.style.WARNING('\n⚠ Errors:'))
                    for error in results['errors'][:5]:  # Show first 5 errors
                        self.stdout.write(f'  {error}')
                    
                    if len(results['errors']) > 5:
                        self.stdout.write(f'  ... and {len(results["errors"]) - 5} more errors')
                
                if results['successful'] > 0:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✓ Async cache warming complete: {results["successful"]}/{total_count} successful'
                        )
                    )
                else:
                    self.stdout.write(self.style.ERROR('✗ No artworks were successfully warmed'))
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Async warming failed: {str(e)}'))
                self.stdout.write('Falling back to synchronous processing...')
                use_async = False
        
        if not use_async:
            # Use original synchronous processing
            warmed_count = 0
            
            for i, artwork_id in enumerate(artwork_ids, 1):
                try:
                    artwork = Artwork.objects.get(id=artwork_id)
                    self.stdout.write(f'[{i}/{total_count}] Processing: {artwork.title}...', ending='')
                    
                    # Warm cache
                    full_url = artwork.get_simple_signed_url()
                    thumb_url = artwork.get_cached_thumbnail_url()
                    
                    if full_url and thumb_url:
                        warmed_count += 1
                        self.stdout.write(' ✓')
                    else:
                        self.stdout.write(' ✗ (no URLs generated)')
                        
                except Exception as e:
                    self.stdout.write(f' ✗ (error: {str(e)})')
            
            # Also warm frame URL caches for featured artworks
            self.stdout.write('\n--- Warming frame URL caches ---')
            frame_count = 0
            
            for artwork_id in artwork_ids:
                try:
                    artwork = Artwork.objects.get(id=artwork_id)
                    if any(getattr(artwork, f'frame{i}_image_url', '') for i in range(1, 5)):
                        # Check if frame cache needs warming
                        from django.utils import timezone
                        now = timezone.now()
                        needs_refresh = (
                            force or
                            not artwork._url_cache_expires or 
                            now >= (artwork._url_cache_expires - timezone.timedelta(minutes=20))
                        )
                        
                        if needs_refresh:
                            self.stdout.write(f'Warming frame cache for: {artwork.title}')
                            for i in range(1, 5):
                                frame_url = artwork.get_frame_simple_url(i)
                                if frame_url:
                                    frame_count += 1
                except Exception as e:
                    self.stdout.write(f'Frame warming error for artwork {artwork_id}: {e}')
            
            duration = time.time() - start_time
            self.stdout.write(f'\nDuration: {duration:.2f}s')
            self.stdout.write(
                self.style.SUCCESS(
                    f'Cache warming complete: {warmed_count}/{total_count} artworks and {frame_count} frame URLs processed'
                )
            )
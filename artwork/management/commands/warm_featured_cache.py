from django.core.management.base import BaseCommand
from django.utils import timezone
from artwork.models import Artwork


class Command(BaseCommand):
    help = 'Pre-warm URL cache for featured artworks to improve API performance'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--force', 
            action='store_true',
            help='Force refresh of all cached URLs, even if not expired'
        )
    
    def handle(self, *args, **options):
        self.stdout.write('Warming URL cache for featured artworks...')
        
        # Get all featured artworks
        featured_artworks = Artwork.objects.filter(
            is_active=True,
            is_featured=True
        ).order_by('-created_at')[:20]  # Limit to top 20 featured
        
        warmed_count = 0
        total_count = featured_artworks.count()
        
        for artwork in featured_artworks:
            self.stdout.write(f'Processing: {artwork.title}...', ending='')
            
            # Check if cache needs refreshing
            now = timezone.now()
            force_refresh = options.get('force', False)
            cache_expired = (force_refresh or 
                           not artwork._cached_image_url or 
                           not artwork._url_cache_expires or 
                           now > (artwork._url_cache_expires - timezone.timedelta(minutes=10)))
            
            if cache_expired:
                try:
                    # Warm both full-size and thumbnail caches
                    full_url = artwork.get_simple_signed_url()
                    thumb_url = artwork.get_cached_thumbnail_url()
                    if full_url and thumb_url:
                        warmed_count += 1
                        self.stdout.write(' ✓')
                    else:
                        self.stdout.write(' ✗ (no URLs generated)')
                except Exception as e:
                    self.stdout.write(f' ✗ (error: {str(e)})')
            else:
                self.stdout.write(' (cached)')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Cache warming complete: {warmed_count}/{total_count} artworks processed'
            )
        )
from django.core.management.base import BaseCommand
from artwork.models import Artwork
from django.utils import timezone

class Command(BaseCommand):
    help = 'Pre-warm the URL cache for all artworks to improve page load performance'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force refresh of all cached URLs even if they are not expired',
        )

    def handle(self, *args, **options):
        self.stdout.write('Starting URL cache warming...')
        
        artworks = Artwork.objects.filter(is_active=True)
        total = artworks.count()
        
        self.stdout.write(f'Found {total} active artworks to process')
        
        success_count = 0
        error_count = 0
        
        for i, artwork in enumerate(artworks, 1):
            try:
                # Check if cache needs refresh
                needs_refresh = (
                    options['force'] or 
                    not artwork._cached_image_url or 
                    not artwork._url_cache_expires or
                    timezone.now() >= artwork._url_cache_expires
                )
                
                if needs_refresh:
                    # Generate and cache the main URL
                    url = artwork.get_simple_signed_url(expires_in=86400)  # 24 hours
                    
                    # Also generate frame URLs to warm the cache
                    frame_urls = []
                    for frame_num in range(1, 5):
                        frame_url = artwork.get_frame_simple_url(frame_num)
                        if frame_url:
                            frame_urls.append(f'frame{frame_num}')
                    
                    if url:
                        frame_info = f" + {len(frame_urls)} frames" if frame_urls else ""
                        success_count += 1
                        self.stdout.write(f'[{i}/{total}] ✅ {artwork.title}{frame_info}')
                    else:
                        error_count += 1
                        self.stdout.write(f'[{i}/{total}] ❌ {artwork.title} - Failed to generate URL')
                else:
                    self.stdout.write(f'[{i}/{total}] ⏭️  {artwork.title} - Cache still valid')
                    
            except Exception as e:
                error_count += 1
                self.stdout.write(f'[{i}/{total}] ❌ {artwork.title} - Error: {e}')
        
        self.stdout.write(self.style.SUCCESS(
            f'URL cache warming complete: {success_count} success, {error_count} errors'
        ))
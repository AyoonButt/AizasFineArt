from django.core.management.base import BaseCommand
from django.utils import timezone
from artwork.models import Artwork


class Command(BaseCommand):
    help = 'Warm all artwork image URL caches proactively to ensure fast first-time user experience'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Warm all caches regardless of current state',
        )
        parser.add_argument(
            '--hours',
            type=int,
            default=2,
            help='Warm caches expiring within X hours (default: 2)',
        )

    def handle(self, *args, **options):
        now = timezone.now()
        warmed_count = 0
        total_count = 0
        
        self.stdout.write("Warming artwork image URL caches for optimal user experience...")
        
        artworks = Artwork.objects.filter(main_image_url__startswith='supabase://').order_by('-is_featured', '-created_at')
        total_count = artworks.count()
        
        for artwork in artworks:
            should_warm = False
            reason = ""
            
            if options['force']:
                should_warm = True
                reason = "forced warming"
            elif not artwork._cached_image_url:
                should_warm = True
                reason = "no main cache"
            elif not artwork._url_cache_expires:
                should_warm = True
                reason = "no expiry set"
            elif now > artwork._url_cache_expires:
                should_warm = True
                reason = "cache expired"
            elif artwork._url_cache_expires - now <= timezone.timedelta(hours=options['hours']):
                should_warm = True
                expires_in = artwork._url_cache_expires - now
                reason = f"expires soon ({expires_in})"
            
            if should_warm:
                try:
                    # Warm main image and gallery URLs
                    main_url = artwork.image_url
                    gallery_url = artwork.gallery_url
                    
                    # Warm frame caches for artworks that have frame images
                    frame_count = 0
                    for i in range(1, 5):
                        raw_frame = getattr(artwork, f'frame{i}_image_url', '')
                        if raw_frame:
                            frame_url = artwork.get_frame_simple_url(i)
                            if frame_url:
                                frame_count += 1
                    
                    warmed_count += 1
                    frame_info = f" + {frame_count} frames" if frame_count > 0 else ""
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Warmed cache for "{artwork.title}"{frame_info} ({reason})')
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'✗ Failed to warm cache for "{artwork.title}": {e}')
                    )
        
        if warmed_count == 0:
            self.stdout.write(self.style.SUCCESS('All artwork URL caches are already warm'))
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully warmed caches for {warmed_count}/{total_count} artworks')
            )
            
        # Summary of cache coverage
        cached_artworks = Artwork.objects.filter(
            main_image_url__startswith='supabase://',
            _cached_image_url__isnull=False
        ).exclude(_cached_image_url='').count()
        
        self.stdout.write(f"\nCache coverage: {cached_artworks}/{total_count} artworks have warm caches")
        self.stdout.write("Users will now experience fast image loading on first visit!")
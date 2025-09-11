from django.core.management.base import BaseCommand
from django.utils import timezone
from artwork.models import Artwork


class Command(BaseCommand):
    help = 'Refresh cached Supabase image URLs for artworks with expired or expiring caches'

    def add_arguments(self, parser):
        parser.add_argument(
            '--artwork-id',
            type=int,
            help='Refresh URLs for specific artwork ID only',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Refresh all caches regardless of expiration',
        )
        parser.add_argument(
            '--hours',
            type=int,
            default=1,
            help='Refresh caches expiring within X hours (default: 1)',
        )

    def handle(self, *args, **options):
        now = timezone.now()
        refreshed = 0
        total = 0
        
        if options['artwork_id']:
            artworks = Artwork.objects.filter(id=options['artwork_id'])
            if not artworks.exists():
                self.stdout.write(
                    self.style.ERROR(f'Artwork with ID {options["artwork_id"]} not found')
                )
                return
        else:
            artworks = Artwork.objects.filter(main_image_url__startswith='supabase://')

        self.stdout.write(f'Checking {artworks.count()} artwork(s) for URL cache expiration...')

        for artwork in artworks:
            total += 1
            should_refresh = False
            reason = ""
            
            if options['force']:
                should_refresh = True
                reason = "forced refresh"
            elif not artwork._url_cache_expires:
                should_refresh = True
                reason = "no expiration set"
            elif now > artwork._url_cache_expires:
                should_refresh = True
                reason = f"expired {now - artwork._url_cache_expires} ago"
            elif artwork._url_cache_expires - now <= timezone.timedelta(hours=options['hours']):
                should_refresh = True
                expires_in = artwork._url_cache_expires - now
                reason = f"expires in {expires_in}"
            
            if should_refresh:
                try:
                    artwork.refresh_url_cache()
                    refreshed += 1
                    self.stdout.write(f'✓ Refreshed URLs for: {artwork.title} ({reason})')
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'✗ Failed to refresh {artwork.title}: {str(e)}')
                    )
        
        if refreshed == 0:
            self.stdout.write(self.style.SUCCESS('All artwork URL caches are current'))
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully refreshed URLs for {refreshed}/{total} artworks')
            )
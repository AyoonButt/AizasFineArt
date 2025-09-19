"""
Management command to refresh frame image URL cache for all artworks
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from artwork.models import Artwork
import requests
import time


class Command(BaseCommand):
    help = 'Refresh frame image URL cache for all artworks'

    def add_arguments(self, parser):
        parser.add_argument(
            '--slug',
            type=str,
            help='Refresh cache for specific artwork slug only',
        )
        parser.add_argument(
            '--check-only',
            action='store_true',
            help='Only check current cache status without refreshing',
        )
        parser.add_argument(
            '--test-urls',
            action='store_true',
            help='Test that refreshed URLs are accessible',
        )

    def handle(self, *args, **options):
        if options['slug']:
            # Refresh specific artwork
            try:
                artwork = Artwork.objects.get(slug=options['slug'], is_active=True)
                artworks = [artwork]
                self.stdout.write(f"Processing artwork: {artwork.title}")
            except Artwork.DoesNotExist:
                raise CommandError(f'Artwork with slug "{options["slug"]}" not found')
        else:
            # Refresh all artworks with frame images
            artworks = Artwork.objects.filter(is_active=True).exclude(frame1_image_url='')
            self.stdout.write(f"Processing {artworks.count()} artworks with frame images")

        if options['check_only']:
            self._check_cache_status(artworks)
            return

        self._refresh_caches(artworks, test_urls=options['test_urls'])

    def _check_cache_status(self, artworks):
        """Check current cache status without refreshing"""
        self.stdout.write("\n=== CACHE STATUS REPORT ===")
        
        expired_count = 0
        missing_count = 0
        
        for artwork in artworks:
            self.stdout.write(f"\n{artwork.title} ({artwork.slug}):")
            
            if artwork._url_cache_expires:
                time_left = (artwork._url_cache_expires - timezone.now()).total_seconds() / 60
                if time_left < 5:
                    self.stdout.write(
                        self.style.WARNING(f"  ⚠️  Cache expires in {time_left:.1f} minutes")
                    )
                    expired_count += 1
                else:
                    self.stdout.write(f"  ✅ Cache valid for {time_left:.1f} minutes")
            else:
                self.stdout.write(self.style.ERROR("  ❌ No cache expiry set"))
                missing_count += 1

            if artwork._cached_frame_urls:
                frame_count = len(artwork._cached_frame_urls)
                self.stdout.write(f"  📦 {frame_count} cached frame URLs")
            else:
                self.stdout.write(self.style.ERROR("  ❌ No cached frame URLs"))
                missing_count += 1

        self.stdout.write(f"\n=== SUMMARY ===")
        self.stdout.write(f"Total artworks: {artworks.count()}")
        self.stdout.write(f"Expired/expiring soon: {expired_count}")
        self.stdout.write(f"Missing cache: {missing_count}")

    def _refresh_caches(self, artworks, test_urls=False):
        """Force refresh all frame URL caches"""
        self.stdout.write("\n=== REFRESHING FRAME CACHES ===")
        
        total_refreshed = 0
        total_frames = 0
        failed_artworks = []

        for artwork in artworks:
            self.stdout.write(f"\nRefreshing {artwork.title}...")

            try:
                # Clear existing cache
                artwork._cached_frame_urls = {}
                artwork._url_cache_expires = None
                artwork.save(update_fields=['_cached_frame_urls', '_url_cache_expires'])

                # Force regeneration of all frame URLs
                fresh_count = 0
                for i in range(1, 5):
                    frame_url = artwork.get_frame_simple_url(i)
                    if frame_url and 'supabase' in frame_url:
                        fresh_count += 1
                        
                        # Test URL if requested
                        if test_urls:
                            try:
                                response = requests.head(frame_url, timeout=5)
                                if response.status_code != 200:
                                    self.stdout.write(
                                        self.style.WARNING(f"  ⚠️  Frame {i} returned status {response.status_code}")
                                    )
                            except Exception as e:
                                self.stdout.write(
                                    self.style.ERROR(f"  ❌ Frame {i} test failed: {e}")
                                )

                self.stdout.write(
                    self.style.SUCCESS(f"  ✅ Generated {fresh_count} fresh frame URLs")
                )
                total_refreshed += 1
                total_frames += fresh_count

                # Small delay to avoid overwhelming Supabase
                time.sleep(0.1)

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"  ❌ Failed to refresh {artwork.title}: {e}")
                )
                failed_artworks.append(artwork.title)

        # Final summary
        self.stdout.write(f"\n=== REFRESH COMPLETE ===")
        self.stdout.write(self.style.SUCCESS(f"✅ Refreshed {total_refreshed} artworks"))
        self.stdout.write(self.style.SUCCESS(f"✅ Generated {total_frames} fresh frame URLs"))
        
        if failed_artworks:
            self.stdout.write(self.style.ERROR(f"❌ Failed: {len(failed_artworks)} artworks"))
            for title in failed_artworks:
                self.stdout.write(f"  - {title}")
        
        if test_urls:
            self.stdout.write("\n🔗 All frame URLs have been tested for accessibility")
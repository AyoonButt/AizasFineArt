from django.apps import AppConfig


class ArtworkConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'artwork'
    
    def ready(self):
        """Run when Django app is ready - warm critical caches automatically"""
        import os
        import sys
        
        # Only run cache warming in production or when explicitly enabled
        # Skip during migrations, tests, or development commands
        if (os.environ.get('DJANGO_SETTINGS_MODULE', '').endswith('settings') and
            not any(arg in sys.argv for arg in ['migrate', 'makemigrations', 'test', 'collectstatic', 'shell'])):
            
            # Import here to avoid circular imports
            try:
                from django.db import connection
                
                # Check if database is ready (skip during initial setup)
                try:
                    connection.ensure_connection()
                    if connection.is_usable():
                        self._schedule_cache_warming()
                except Exception:
                    pass  # Skip cache warming if database isn't ready
                    
            except ImportError:
                pass  # Skip if not available
    
    def _schedule_cache_warming(self):
        """Schedule background cache warming for critical artworks"""
        try:
            import threading
            import time
            
            def delayed_cache_warming():
                """Warm cache after app startup delay"""
                try:
                    time.sleep(10)  # Wait 10 seconds after app startup
                    
                    from django.utils import timezone
                    from .models import Artwork
                    
                    # Warm cache for featured artworks and first 5 artworks (most likely to be accessed)
                    critical_artworks = Artwork.objects.filter(
                        is_active=True,
                        main_image_url__startswith='supabase://'
                    ).order_by('-is_featured', '-created_at')[:8]  # Top 8 critical artworks
                    
                    warmed_count = 0
                    for artwork in critical_artworks:
                        # Only warm if cache is missing or expires soon
                        now = timezone.now()
                        needs_warming = (
                            not artwork._cached_image_url or
                            not artwork._url_cache_expires or
                            now >= (artwork._url_cache_expires - timezone.timedelta(hours=2))
                        )
                        
                        if needs_warming:
                            # Trigger cache warming by accessing the property
                            _ = artwork.image_url
                            warmed_count += 1
                    
                    if warmed_count > 0:
                        print(f"🔥 Auto-warmed cache for {warmed_count} critical artworks")
                            
                except Exception:
                    pass  # Silent failure - don't disrupt app
            
            # Start background warming thread
            thread = threading.Thread(target=delayed_cache_warming, daemon=True)
            thread.start()
            
        except Exception:
            pass  # Don't disrupt app startup if warming fails

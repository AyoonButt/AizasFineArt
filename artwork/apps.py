from django.apps import AppConfig
import os
import sys
import logging

logger = logging.getLogger(__name__)


class ArtworkConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'artwork'
    
    def ready(self):
        """Run when Django app is ready - warm critical caches automatically"""
        # Enhanced cache warming with improved safety checks and error handling
        
        # Skip cache warming in specific scenarios to prevent startup issues
        skip_conditions = [
            # Development/testing commands
            'migrate', 'makemigrations', 'test', 'collectstatic', 'shell',
            'check', 'showmigrations', 'sqlmigrate', 'dbshell',
            # Build/deployment commands
            'compilemessages', 'makemessages', 'diffsettings',
            # Custom management commands that don't need caching
            'warm_all_cache', 'warm_featured_cache', 'warm_url_cache',
            # Testing frameworks
            'pytest', 'coverage'
        ]
        
        # Check if we should skip cache warming
        should_skip = (
            # Skip during command execution
            any(arg in sys.argv for arg in skip_conditions) or
            # Skip if not in production-like environment
            not os.environ.get('DJANGO_SETTINGS_MODULE', '').endswith('settings') or
            # Skip during testing
            'test' in sys.argv[0].lower() or
            # Skip if explicitly disabled
            os.environ.get('DISABLE_CACHE_WARMING', '').lower() in ['true', '1', 'yes'] or
            # Skip during any management command (be more conservative)
            len(sys.argv) > 1 and sys.argv[1] in ['runserver', 'collectstatic', 'build', 'webpack'] or
            # Skip if we're in development mode (DEBUG=True)
            os.environ.get('DEBUG', '').lower() in ['true', '1'] or
            # Skip if Django is not fully initialized
            not hasattr(sys, 'argv') or len(sys.argv) == 0
        )
        
        # Only enable cache warming in very specific production scenarios
        # Be extremely conservative to prevent any build or command interference
        enable_cache_warming = (
            # Must be production settings
            os.environ.get('DJANGO_SETTINGS_MODULE', '').endswith('settings') and
            # Must not be during any command execution
            not any(arg in sys.argv for arg in skip_conditions) and
            # Must be actual server startup - be very explicit
            len(sys.argv) >= 2 and sys.argv[1] == 'runserver' and
            # Must not be explicitly disabled
            os.environ.get('DISABLE_CACHE_WARMING', '').lower() not in ['true', '1', 'yes'] and
            # Must not be in debug/development mode
            os.environ.get('DEBUG', '').lower() not in ['true', '1'] and
            # Must have ENABLE_CACHE_WARMING explicitly set to true
            os.environ.get('ENABLE_CACHE_WARMING', '').lower() in ['true', '1', 'yes']
        )
        
        if enable_cache_warming:
            self._schedule_enhanced_cache_warming()
            self._start_cache_refresh_service()
    
    def _schedule_enhanced_cache_warming(self):
        """Schedule background cache warming with enhanced safety checks"""
        try:
            from .thread_manager import thread_manager
            import time
            from django.db import connection
            
            def enhanced_cache_warming():
                """Enhanced cache warming with robust error handling"""
                max_retries = 3
                retry_delay = 5  # Start with 5 seconds
                
                for attempt in range(max_retries):
                    try:
                        # Longer initial delay to ensure app is fully loaded
                        time.sleep(30 + (attempt * 10))  # Exponential backoff for retries
                        
                        # Validate database readiness with multiple checks
                        if not self._validate_database_ready():
                            if attempt == max_retries - 1:
                                logger.info("Cache warming skipped: Database not ready after retries")
                            continue
                        
                        # Perform cache warming
                        warmed_count = self._perform_cache_warming()
                        
                        if warmed_count > 0:
                            logger.info(f"🔥 Auto-warmed cache for {warmed_count} critical artworks")
                        else:
                            logger.info("Cache warming completed: No artworks needed cache refresh")
                        
                        break  # Success - exit retry loop
                        
                    except Exception as e:
                        logger.warning(f"Cache warming attempt {attempt + 1} failed: {str(e)}")
                        if attempt == max_retries - 1:
                            logger.error("Cache warming failed after all retries")
                        else:
                            time.sleep(retry_delay)
                            retry_delay *= 2  # Exponential backoff
            
            # Submit to thread pool for non-blocking cache warming
            thread_manager.submit_task(
                enhanced_cache_warming,
                task_name="startup_cache_warming"
            )
            
        except Exception as e:
            logger.warning(f"Failed to schedule cache warming: {str(e)}")
    
    def _validate_database_ready(self):
        """Comprehensive database readiness validation"""
        try:
            from django.db import connection
            from django.core.exceptions import ImproperlyConfigured
            import time
            
            # Wait a bit more before even attempting database connection
            time.sleep(5)
            
            # Check 1: Basic connection test with timeout
            try:
                connection.ensure_connection()
                if not connection.is_usable():
                    return False
            except Exception:
                return False
            
            # Check 2: Test a simple query to verify database is accessible
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    result = cursor.fetchone()
                    if not result or result[0] != 1:
                        return False
            except Exception:
                return False
            
            # Check 3: Verify Django tables exist (more basic check)
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT COUNT(*) FROM django_migrations")
                    cursor.fetchone()
            except Exception:
                return False
            
            # Check 4: Verify artwork table exists and is accessible
            try:
                from .models import Artwork
                # Use a more gentle check that doesn't force query execution
                Artwork._meta.get_field('title')  # Just check model is loadable
                
                # Only if model loads, then try database
                count = Artwork.objects.count()  # This should work if table exists
                return True
            except Exception as e:
                logger.warning(f"Artwork model not ready: {e}")
                return False
                
        except (ImproperlyConfigured, Exception) as e:
            logger.warning(f"Database validation failed: {e}")
            return False
    
    def _perform_cache_warming(self):
        """Perform the actual cache warming with memory efficiency"""
        try:
            from django.utils import timezone
            from .models import Artwork
            
            # Get critical artworks with minimal memory footprint
            # Use only() to fetch minimal fields and defer expensive operations
            critical_artworks = Artwork.objects.filter(
                is_active=True,
                main_image_url__startswith='supabase://'
            ).only(
                'id', 'title', 'main_image_url', '_cached_image_url', '_url_cache_expires'
            ).order_by('-is_featured', '-created_at')[:8]  # Top 8 critical artworks
            
            warmed_count = 0
            now = timezone.now()
            
            for artwork in critical_artworks:
                try:
                    # Check if cache needs warming (expires within 2 hours)
                    needs_warming = (
                        not artwork._cached_image_url or
                        not artwork._url_cache_expires or
                        now >= (artwork._url_cache_expires - timezone.timedelta(hours=2))
                    )
                    
                    if needs_warming:
                        # Trigger cache warming by accessing the image_url property
                        # This will generate and cache the URL
                        _ = artwork.image_url
                        warmed_count += 1
                        
                        # Small delay to avoid overwhelming the database
                        import time
                        time.sleep(0.1)
                        
                except Exception as e:
                    logger.warning(f"Failed to warm cache for artwork {artwork.id}: {str(e)}")
                    continue
            
            return warmed_count
            
        except Exception as e:
            logger.error(f"Cache warming operation failed: {str(e)}")
            return 0
    
    def _start_cache_refresh_service(self):
        """Start the continuous cache refresh service"""
        try:
            from .cache_refresh_service import start_cache_refresh_service
            start_cache_refresh_service()
            logger.info("🔄 Continuous cache refresh service started")
        except Exception as e:
            logger.warning(f"Cache refresh service failed to start: {e}")

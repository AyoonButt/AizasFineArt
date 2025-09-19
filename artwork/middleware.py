"""
Cache Warming Middleware for Aiza's Fine Art
Provides request-triggered cache warming as fallback mechanism
"""
import logging
import threading
import time
from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from django.core.cache import cache

logger = logging.getLogger(__name__)


class CacheWarmingMiddleware(MiddlewareMixin):
    """
    Middleware that triggers cache warming on homepage visits when cache is cold.
    Acts as fallback mechanism if background cache warming fails.
    """
    
    # Cache key to track last warming time
    CACHE_WARMING_KEY = 'artwork_cache_last_warmed'
    WARMING_COOLDOWN = 30 * 60  # 30 minutes cooldown between warmings
    
    def process_request(self, request):
        """Check if cache warming is needed on homepage visits"""
        
        # Only trigger on homepage or gallery pages (high-traffic areas)
        homepage_paths = ['/', '/gallery/', '/shop/', '/art/']
        if not any(request.path.startswith(path) for path in homepage_paths):
            return None
        
        # Check if we recently warmed the cache
        last_warmed = cache.get(self.CACHE_WARMING_KEY)
        now = timezone.now()
        
        if last_warmed and (now - last_warmed).seconds < self.WARMING_COOLDOWN:
            return None  # Recently warmed, skip
        
        # Check if cache actually needs warming
        if not self._cache_needs_warming():
            return None
        
        # Trigger background cache warming
        self._trigger_background_warming()
        
        return None
    
    def _cache_needs_warming(self):
        """Check if cache actually needs warming by sampling a few artworks"""
        try:
            from .models import Artwork
            
            # Sample a few featured artworks to check cache status
            sample_artworks = Artwork.objects.filter(
                is_active=True,
                is_featured=True
            ).only('_cached_image_url', '_url_cache_expires')[:3]
            
            now = timezone.now()
            needs_warming = False
            
            for artwork in sample_artworks:
                if (not artwork._cached_image_url or 
                    not artwork._url_cache_expires or
                    now >= (artwork._url_cache_expires - timezone.timedelta(hours=1))):
                    needs_warming = True
                    break
            
            return needs_warming
            
        except Exception as e:
            logger.warning(f"Could not check cache status: {str(e)}")
            return False  # Conservative: don't warm if we can't check
    
    def _trigger_background_warming(self):
        """Trigger background cache warming in a separate thread"""
        try:
            from .thread_manager import thread_manager
            
            def background_warming():
                """Perform cache warming in background thread"""
                try:
                    # Small delay to not interfere with current request
                    time.sleep(2)
                    
                    from .models import Artwork
                    from django.utils import timezone
                    
                    # Warm cache for featured artworks (prioritize user-visible content)
                    featured_artworks = Artwork.objects.filter(
                        is_active=True,
                        is_featured=True,
                        main_image_url__startswith='supabase://'
                    ).only(
                        'id', 'title', 'main_image_url', '_cached_image_url', '_url_cache_expires'
                    )[:5]  # Limit to 5 to keep it fast
                    
                    warmed_count = 0
                    now = timezone.now()
                    
                    for artwork in featured_artworks:
                        try:
                            # Check if cache needs warming
                            needs_warming = (
                                not artwork._cached_image_url or
                                not artwork._url_cache_expires or
                                now >= (artwork._url_cache_expires - timezone.timedelta(hours=1))
                            )
                            
                            if needs_warming:
                                # Warm cache by accessing image_url property
                                _ = artwork.image_url
                                warmed_count += 1
                                time.sleep(0.1)  # Small delay between requests
                                
                        except Exception as e:
                            logger.warning(f"Failed to warm cache for artwork {artwork.id}: {str(e)}")
                            continue
                    
                    if warmed_count > 0:
                        logger.info(f"🔥 Request-triggered cache warming: {warmed_count} artworks")
                    
                    # Update last warmed timestamp
                    cache.set(self.CACHE_WARMING_KEY, timezone.now(), 3600)  # 1 hour cache
                    
                except Exception as e:
                    logger.error(f"Background cache warming failed: {str(e)}")
            
            # Submit to thread pool instead of raw thread
            thread_manager.submit_task(
                background_warming,
                task_name="request_triggered_warming"
            )
            
        except Exception as e:
            logger.warning(f"Could not trigger background cache warming: {str(e)}")


class PerformanceMonitoringMiddleware(MiddlewareMixin):
    """
    Optional middleware to monitor cache performance and warming effectiveness
    """
    
    def process_request(self, request):
        """Track cache hit/miss rates for monitoring"""
        if hasattr(request, 'cache_start_time'):
            return None
            
        request.cache_start_time = time.time()
        return None
    
    def process_response(self, request, response):
        """Log cache performance metrics"""
        if not hasattr(request, 'cache_start_time'):
            return response
        
        try:
            response_time = time.time() - request.cache_start_time
            
            # Only log for image-heavy pages
            if any(path in request.path for path in ['/gallery/', '/shop/', '/art/']):
                if response_time > 2.0:  # Slow responses
                    logger.info(f"Slow response: {request.path} took {response_time:.2f}s")
                elif response_time < 0.5:  # Fast responses (likely cached)
                    logger.debug(f"Fast response: {request.path} took {response_time:.2f}s")
            
        except Exception:
            pass  # Don't disrupt response
        
        return response
#!/usr/bin/env python3
"""
Automatic Image URL Cache Refresh Service
Continuously refreshes image URLs before expiry to maintain sub-3s performance
"""

import time
import threading
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import transaction
from django.core.management import call_command
from artwork.models import Artwork
import logging

logger = logging.getLogger(__name__)

class ImageCacheRefreshService:
    """Background service to refresh image URLs before expiry"""
    
    def __init__(self):
        self.running = False
        self.thread = None
        self.refresh_interval = 1800  # 30 minutes
        self.expiry_buffer = 3600     # Refresh 1 hour before expiry
    
    def start(self):
        """Start the background refresh service"""
        if self.running:
            logger.warning("Cache refresh service already running")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._refresh_loop, daemon=True)
        self.thread.start()
        logger.info("🚀 Image cache refresh service started")
    
    def stop(self):
        """Stop the background refresh service"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("🛑 Image cache refresh service stopped")
    
    def _refresh_loop(self):
        """Main refresh loop - runs continuously"""
        while self.running:
            try:
                self._refresh_expiring_urls()
                time.sleep(self.refresh_interval)
            except Exception as e:
                logger.error(f"Cache refresh error: {e}")
                time.sleep(60)  # Wait 1 minute before retrying on error
    
    def _refresh_expiring_urls(self):
        """Refresh URLs that are close to expiring"""
        now = timezone.now()
        expiry_threshold = now + timedelta(seconds=self.expiry_buffer)
        
        # Find artworks with URLs expiring soon
        expiring_artworks = Artwork.objects.filter(
            is_active=True,
            _url_cache_expires__lte=expiry_threshold,
            _url_cache_expires__isnull=False
        ).select_related('category')
        
        if not expiring_artworks.exists():
            logger.info("✅ All image URLs are fresh")
            return
        
        logger.info(f"🔄 Refreshing {expiring_artworks.count()} expiring URLs")
        
        # Refresh main image URLs
        self._refresh_main_urls(expiring_artworks)
        
        # Refresh frame URLs for featured artworks (priority)
        featured_expiring = expiring_artworks.filter(is_featured=True)
        self._refresh_frame_urls(featured_expiring)
        
        logger.info("✅ URL refresh cycle completed")
    
    def _refresh_main_urls(self, artworks):
        """Refresh main image URLs for artworks"""
        success_count = 0
        
        for artwork in artworks:
            try:
                # Generate fresh URL
                fresh_url = artwork.get_simple_signed_url(expires_in=3600)
                success_count += 1
                
                if success_count <= 5:  # Log first 5 for monitoring
                    logger.info(f"🔄 Refreshed: {artwork.title}")
                
            except Exception as e:
                logger.error(f"❌ Failed to refresh {artwork.title}: {e}")
        
        logger.info(f"📊 Main URLs refreshed: {success_count}/{artworks.count()}")
    
    def _refresh_frame_urls(self, artworks):
        """Refresh frame URLs for priority artworks"""
        frame_count = 0
        
        for artwork in artworks:
            for frame_num in range(1, 5):
                frame_url_field = f'frame{frame_num}_image_url'
                if hasattr(artwork, frame_url_field) and getattr(artwork, frame_url_field):
                    try:
                        artwork.get_frame_simple_url(frame_num)
                        frame_count += 1
                    except Exception as e:
                        logger.warning(f"Frame {frame_num} refresh failed for {artwork.title}")
        
        if frame_count > 0:
            logger.info(f"🖼️  Frame URLs refreshed: {frame_count}")
    
    def force_refresh_featured(self):
        """Force refresh all featured artwork URLs (for immediate performance boost)"""
        logger.info("🚀 Force refreshing featured artwork URLs")
        
        featured_artworks = Artwork.objects.filter(
            is_featured=True, 
            is_active=True
        ).select_related('category')
        
        for artwork in featured_artworks:
            try:
                # Force refresh main image
                artwork.get_simple_signed_url(expires_in=3600)
                
                # Force refresh frame images
                for frame_num in range(1, 5):
                    frame_url_field = f'frame{frame_num}_image_url'
                    if hasattr(artwork, frame_url_field) and getattr(artwork, frame_url_field):
                        artwork.get_frame_simple_url(frame_num)
                
                logger.info(f"✅ Force refreshed: {artwork.title}")
                
            except Exception as e:
                logger.error(f"❌ Force refresh failed for {artwork.title}: {e}")
        
        logger.info("🎯 Featured artwork URL refresh completed")

# Global service instance
cache_refresh_service = ImageCacheRefreshService()

def start_cache_refresh_service():
    """Start the global cache refresh service"""
    cache_refresh_service.start()

def stop_cache_refresh_service():
    """Stop the global cache refresh service"""
    cache_refresh_service.stop()

def force_refresh_featured():
    """Force refresh featured artworks for immediate performance"""
    cache_refresh_service.force_refresh_featured()
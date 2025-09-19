"""
Async Cache Warming Operations
Provides non-blocking database operations for cache warming
"""
import asyncio
import logging
from typing import List, Optional, Dict, Any
from django.utils import timezone
from django.db import transaction
from django.core.cache import cache
from asgiref.sync import sync_to_async, async_to_sync
import time

logger = logging.getLogger(__name__)


class AsyncCacheWarmer:
    """Asynchronous cache warming operations"""
    
    def __init__(self):
        self.semaphore = asyncio.Semaphore(5)  # Limit concurrent operations
    
    async def warm_artwork_batch(self, artwork_ids: List[int], force: bool = False) -> Dict[str, Any]:
        """Warm cache for a batch of artworks asynchronously"""
        start_time = time.time()
        results = {
            'total_processed': 0,
            'successful': 0,
            'failed': 0,
            'errors': []
        }
        
        # Create tasks for concurrent processing
        tasks = []
        for artwork_id in artwork_ids:
            task = asyncio.create_task(
                self._warm_single_artwork(artwork_id, force)
            )
            tasks.append(task)
        
        # Process tasks concurrently
        completed_tasks = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Analyze results
        for i, result in enumerate(completed_tasks):
            results['total_processed'] += 1
            
            if isinstance(result, Exception):
                results['failed'] += 1
                results['errors'].append(f"Artwork {artwork_ids[i]}: {str(result)}")
            elif result:
                results['successful'] += 1
            else:
                results['failed'] += 1
        
        results['duration_seconds'] = time.time() - start_time
        
        # Record batch metrics
        await self._record_batch_metrics(results)
        
        logger.info(
            f"Async batch warming: {results['successful']}/{results['total_processed']} "
            f"successful in {results['duration_seconds']:.2f}s"
        )
        
        return results
    
    async def _warm_single_artwork(self, artwork_id: int, force: bool = False) -> bool:
        """Warm cache for a single artwork"""
        async with self.semaphore:  # Limit concurrent operations
            try:
                # Get artwork data
                artwork = await self._get_artwork_async(artwork_id)
                if not artwork:
                    return False
                
                # Check if warming is needed
                if not force and not await self._needs_warming(artwork):
                    return True  # Already cached
                
                # Generate signed URL
                signed_url = await self._generate_signed_url_async(artwork['main_image_url'])
                if not signed_url:
                    return False
                
                # Update cache in database
                success = await self._update_cache_async(artwork_id, signed_url)
                
                if success:
                    # Record success metric
                    await self._record_metric_async('warming_success', artwork_id)
                    
                    # Warm frame images if they exist
                    await self._warm_frame_images_async(artwork)
                
                return success
                
            except Exception as e:
                logger.error(f"Failed to warm artwork {artwork_id}: {str(e)}")
                await self._record_metric_async('warming_failure', artwork_id, metadata={'error': str(e)})
                return False
    
    @sync_to_async
    def _get_artwork_async(self, artwork_id: int) -> Optional[Dict]:
        """Get artwork data asynchronously"""
        try:
            from .models import Artwork
            artwork = Artwork.objects.only(
                'id', 'main_image_url', '_cached_image_url', '_url_cache_expires',
                'frame1_image_url', 'frame2_image_url', 'frame3_image_url', 'frame4_image_url'
            ).get(id=artwork_id, is_active=True)
            
            return {
                'id': artwork.id,
                'main_image_url': artwork.main_image_url,
                '_cached_image_url': artwork._cached_image_url,
                '_url_cache_expires': artwork._url_cache_expires,
                'frame_urls': [
                    artwork.frame1_image_url,
                    artwork.frame2_image_url,
                    artwork.frame3_image_url,
                    artwork.frame4_image_url
                ]
            }
        except Exception:
            return None
    
    async def _needs_warming(self, artwork: Dict) -> bool:
        """Check if artwork cache needs warming"""
        if not artwork['_cached_image_url'] or not artwork['_url_cache_expires']:
            return True
        
        now = timezone.now()
        # Warm if expires within 1 hour
        return now >= (artwork['_url_cache_expires'] - timezone.timedelta(hours=1))
    
    async def _generate_signed_url_async(self, image_url: str) -> Optional[str]:
        """Generate signed URL asynchronously"""
        if not image_url or not image_url.startswith('supabase://'):
            return None
        
        try:
            # Run Supabase API call in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            signed_url = await loop.run_in_executor(
                None, 
                self._generate_signed_url_sync, 
                image_url
            )
            
            # Record API call metric
            await self._record_metric_async('api_call', metadata={'operation': 'create_signed_url'})
            
            return signed_url
            
        except Exception as e:
            logger.error(f"Failed to generate signed URL: {str(e)}")
            return None
    
    def _generate_signed_url_sync(self, image_url: str) -> Optional[str]:
        """Synchronous signed URL generation"""
        try:
            from utils.supabase_client import supabase_storage
            file_path = image_url.replace('supabase://', '')
            signed_url = supabase_storage.client.storage.from_(supabase_storage.bucket).create_signed_url(file_path, 3600)
            
            if signed_url and 'signedURL' in signed_url:
                return signed_url['signedURL']
            
        except Exception:
            pass
        
        return None
    
    @sync_to_async
    def _update_cache_async(self, artwork_id: int, signed_url: str) -> bool:
        """Update cache in database asynchronously"""
        try:
            from .models import Artwork
            from django.utils import timezone
            
            with transaction.atomic():
                artwork = Artwork.objects.select_for_update().get(id=artwork_id)
                artwork._cached_image_url = signed_url
                artwork._url_cache_expires = timezone.now() + timezone.timedelta(seconds=3300)  # 55 minutes
                artwork.save(update_fields=['_cached_image_url', '_url_cache_expires'])
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to update cache for artwork {artwork_id}: {str(e)}")
            return False
    
    async def _warm_frame_images_async(self, artwork: Dict):
        """Warm frame image caches asynchronously"""
        frame_tasks = []
        
        for i, frame_url in enumerate(artwork['frame_urls'], 1):
            if frame_url and frame_url.startswith('supabase://'):
                task = asyncio.create_task(
                    self._warm_frame_image(artwork['id'], i, frame_url)
                )
                frame_tasks.append(task)
        
        if frame_tasks:
            await asyncio.gather(*frame_tasks, return_exceptions=True)
    
    async def _warm_frame_image(self, artwork_id: int, frame_num: int, frame_url: str):
        """Warm a single frame image cache"""
        try:
            signed_url = await self._generate_signed_url_async(frame_url)
            if signed_url:
                await self._update_frame_cache_async(artwork_id, frame_num, signed_url)
        except Exception:
            pass  # Silent failure for frame images
    
    @sync_to_async
    def _update_frame_cache_async(self, artwork_id: int, frame_num: int, signed_url: str):
        """Update frame cache in database"""
        try:
            from .models import Artwork
            from django.utils import timezone
            
            with transaction.atomic():
                artwork = Artwork.objects.select_for_update().get(id=artwork_id)
                if not artwork._cached_frame_urls:
                    artwork._cached_frame_urls = {}
                artwork._cached_frame_urls[f'frame{frame_num}'] = signed_url
                artwork._url_cache_expires = timezone.now() + timezone.timedelta(seconds=3300)
                artwork.save(update_fields=['_cached_frame_urls', '_url_cache_expires'])
                
        except Exception:
            pass
    
    @sync_to_async
    def _record_metric_async(self, metric_type: str, artwork_id: Optional[int] = None, 
                           response_time_ms: Optional[float] = None, metadata: Optional[Dict] = None):
        """Record cache metric asynchronously"""
        try:
            from .cache_metrics import CachePerformanceAnalyzer
            CachePerformanceAnalyzer.record_metric(
                metric_type=metric_type,
                artwork_id=artwork_id,
                response_time_ms=response_time_ms,
                metadata=metadata
            )
        except Exception:
            pass
    
    async def _record_batch_metrics(self, results: Dict[str, Any]):
        """Record batch operation metrics"""
        await self._record_metric_async(
            'thread_pool_task',
            response_time_ms=results['duration_seconds'] * 1000,
            metadata={
                'operation': 'batch_warming',
                'total_processed': results['total_processed'],
                'successful': results['successful'],
                'failed': results['failed']
            }
        )
    
    async def get_artworks_needing_warming(self, limit: int = 20) -> List[int]:
        """Get list of artwork IDs that need cache warming"""
        return await self._get_artworks_needing_warming_async(limit)
    
    @sync_to_async
    def _get_artworks_needing_warming_async(self, limit: int) -> List[int]:
        """Database query to find artworks needing warming"""
        from .models import Artwork
        from django.utils import timezone
        
        now = timezone.now()
        cutoff = now + timezone.timedelta(hours=1)  # Warm if expires within 1 hour
        
        from django.db import models
        
        artworks = Artwork.objects.filter(
            is_active=True,
            main_image_url__startswith='supabase://'
        ).filter(
            # Either no cache or expires soon
            models.Q(_cached_image_url__isnull=True) |
            models.Q(_url_cache_expires__isnull=True) |
            models.Q(_url_cache_expires__lt=cutoff)
        ).values_list('id', flat=True)[:limit]
        
        return list(artworks)


# Global instance
async_cache_warmer = AsyncCacheWarmer()


def run_async_cache_warming(artwork_ids: List[int], force: bool = False) -> Dict[str, Any]:
    """Synchronous wrapper for async cache warming"""
    return async_to_sync(async_cache_warmer.warm_artwork_batch)(artwork_ids, force)
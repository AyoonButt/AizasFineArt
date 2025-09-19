"""
Thread Manager for Cache Pre-Warming Operations
Provides centralized thread pool management with monitoring
"""
import logging
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import contextmanager
from typing import Callable, Dict, List, Optional, Any
import time
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


class ThreadManager:
    """Centralized thread pool manager for cache operations"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
            
        self._initialized = True
        self.max_workers = getattr(settings, 'CACHE_THREAD_POOL_SIZE', 5)
        self.executor = ThreadPoolExecutor(
            max_workers=self.max_workers,
            thread_name_prefix='CacheWarming'
        )
        self.active_tasks: Dict[str, Any] = {}
        self.task_counter = 0
        self._stats = {
            'total_submitted': 0,
            'total_completed': 0,
            'total_failed': 0,
            'active_threads': 0,
            'queue_size': 0
        }
        self._stats_lock = threading.Lock()
        
        # Start monitoring thread
        self._start_monitoring()
    
    def submit_task(self, func: Callable, *args, task_name: Optional[str] = None, **kwargs) -> str:
        """Submit a task to the thread pool"""
        with self._stats_lock:
            self.task_counter += 1
            task_id = f"task_{self.task_counter}"
            if task_name:
                task_id = f"{task_name}_{task_id}"
            
            self._stats['total_submitted'] += 1
            
        future = self.executor.submit(self._wrapped_task, task_id, func, *args, **kwargs)
        self.active_tasks[task_id] = {
            'future': future,
            'start_time': time.time(),
            'name': task_name or func.__name__
        }
        
        return task_id
    
    def _wrapped_task(self, task_id: str, func: Callable, *args, **kwargs):
        """Wrapper to track task execution"""
        try:
            with self._stats_lock:
                self._stats['active_threads'] += 1
                
            result = func(*args, **kwargs)
            
            with self._stats_lock:
                self._stats['total_completed'] += 1
                
            return result
            
        except Exception as e:
            with self._stats_lock:
                self._stats['total_failed'] += 1
                
            logger.error(f"Task {task_id} failed: {str(e)}")
            raise
            
        finally:
            with self._stats_lock:
                self._stats['active_threads'] -= 1
                
            if task_id in self.active_tasks:
                del self.active_tasks[task_id]
    
    def wait_for_completion(self, task_ids: List[str], timeout: Optional[float] = None) -> Dict[str, Any]:
        """Wait for specific tasks to complete"""
        futures = {
            task_id: self.active_tasks[task_id]['future'] 
            for task_id in task_ids 
            if task_id in self.active_tasks
        }
        
        results = {}
        for future in as_completed(futures.values(), timeout=timeout):
            task_id = [k for k, v in futures.items() if v == future][0]
            try:
                results[task_id] = future.result()
            except Exception as e:
                results[task_id] = {'error': str(e)}
                
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current thread pool statistics"""
        with self._stats_lock:
            stats = self._stats.copy()
            
        stats['queue_size'] = self.executor._work_queue.qsize()
        stats['active_tasks'] = [
            {
                'id': task_id,
                'name': info['name'],
                'duration': time.time() - info['start_time']
            }
            for task_id, info in self.active_tasks.items()
        ]
        
        return stats
    
    def _start_monitoring(self):
        """Start background monitoring thread"""
        def monitor():
            while True:
                try:
                    stats = self.get_stats()
                    
                    # Store stats in cache for external monitoring
                    cache.set('thread_manager_stats', stats, 60)
                    
                    # Log warnings if thresholds exceeded
                    if stats['active_threads'] >= self.max_workers:
                        logger.warning(f"Thread pool at capacity: {stats['active_threads']}/{self.max_workers}")
                    
                    if stats['queue_size'] > 10:
                        logger.warning(f"Large task queue: {stats['queue_size']} tasks pending")
                    
                    # Check for stuck tasks (running > 5 minutes)
                    for task in stats['active_tasks']:
                        if task['duration'] > 300:  # 5 minutes
                            logger.warning(f"Long-running task detected: {task['name']} ({task['duration']:.1f}s)")
                    
                    time.sleep(30)  # Monitor every 30 seconds
                    
                except Exception as e:
                    logger.error(f"Monitoring thread error: {str(e)}")
                    time.sleep(60)
        
        monitor_thread = threading.Thread(target=monitor, daemon=True, name='ThreadPoolMonitor')
        monitor_thread.start()
    
    def shutdown(self, wait: bool = True):
        """Shutdown the thread pool"""
        logger.info(f"Shutting down thread pool. Stats: {self.get_stats()}")
        self.executor.shutdown(wait=wait)
    
    @contextmanager
    def batch_submit(self, task_name: str):
        """Context manager for batch task submission"""
        batch_ids = []
        
        def batch_submit_func(func, *args, **kwargs):
            task_id = self.submit_task(func, *args, task_name=task_name, **kwargs)
            batch_ids.append(task_id)
            return task_id
        
        yield batch_submit_func
        
        # Wait for all batch tasks to complete
        if batch_ids:
            logger.info(f"Waiting for {len(batch_ids)} {task_name} tasks to complete")
            results = self.wait_for_completion(batch_ids, timeout=300)  # 5 minute timeout
            
            successful = sum(1 for r in results.values() if 'error' not in r)
            logger.info(f"Batch {task_name} completed: {successful}/{len(batch_ids)} successful")


# Global instance
thread_manager = ThreadManager()
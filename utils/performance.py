"""
Performance optimization utilities for the anime video management application.
Includes caching, threading utilities, and UI responsiveness improvements.
"""

import threading
import time
from functools import wraps
from typing import Dict, Any, Callable, Optional
import weakref

class PerformanceManager:
    """Manages performance optimizations for the application"""
    
    def __init__(self):
        self.thumbnail_cache = {}
        self.max_cache_size = 100
        self.cache_cleanup_threshold = 150
        self.loading_states = weakref.WeakSet()
        
    def cache_thumbnail(self, url: str, image_data: Any) -> None:
        """Cache a thumbnail image"""
        # Clean cache if it gets too large
        if len(self.thumbnail_cache) > self.cache_cleanup_threshold:
            self._cleanup_cache()
        
        self.thumbnail_cache[url] = {
            'data': image_data,
            'timestamp': time.time()
        }
    
    def get_cached_thumbnail(self, url: str) -> Optional[Any]:
        """Get a cached thumbnail if available"""
        if url in self.thumbnail_cache:
            cache_entry = self.thumbnail_cache[url]
            # Check if cache entry is still fresh (1 hour)
            if time.time() - cache_entry['timestamp'] < 3600:
                return cache_entry['data']
            else:
                # Remove stale cache entry
                del self.thumbnail_cache[url]
        return None
    
    def _cleanup_cache(self):
        """Clean up old cache entries"""
        current_time = time.time()
        # Remove entries older than 1 hour
        expired_keys = [
            key for key, value in self.thumbnail_cache.items()
            if current_time - value['timestamp'] > 3600
        ]
        
        for key in expired_keys:
            del self.thumbnail_cache[key]
        
        # If still too many entries, remove oldest ones
        if len(self.thumbnail_cache) > self.max_cache_size:
            sorted_items = sorted(
                self.thumbnail_cache.items(),
                key=lambda x: x[1]['timestamp']
            )
            
            # Keep only the most recent entries
            keep_count = self.max_cache_size // 2
            keys_to_remove = [item[0] for item in sorted_items[:-keep_count]]
            
            for key in keys_to_remove:
                del self.thumbnail_cache[key]
    
    def clear_cache(self):
        """Clear all cached data"""
        self.thumbnail_cache.clear()

# Global performance manager instance
perf_manager = PerformanceManager()

def async_operation(func: Callable) -> Callable:
    """Decorator to run operations in background threads"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        def run_async():
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(f"Async operation error: {e}")
        
        thread = threading.Thread(target=run_async, daemon=True)
        thread.start()
        return thread
    
    return wrapper

def debounce(wait_time: float):
    """Decorator to debounce function calls"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get the instance from args if it's a method
            instance = args[0] if args and hasattr(args[0], '__dict__') else None
            attr_name = f"_debounce_timer_{func.__name__}"
            
            # Cancel previous timer if exists
            if instance and hasattr(instance, attr_name):
                timer = getattr(instance, attr_name)
                if timer and timer.is_alive():
                    timer.cancel()
            
            # Create new timer
            timer = threading.Timer(wait_time, func, args, kwargs)
            timer.start()
            
            # Store timer reference
            if instance:
                setattr(instance, attr_name, timer)
            
            return timer
        
        return wrapper
    return decorator

class LoadingState:
    """Manages loading states for UI components"""
    
    def __init__(self, widget, progress_callback=None):
        self.widget = widget
        self.progress_callback = progress_callback
        self.is_loading = False
        self.loading_animation_timer = None
        perf_manager.loading_states.add(self)
    
    def start_loading(self, message="Loading..."):
        """Start loading animation"""
        self.is_loading = True
        if self.progress_callback:
            self.progress_callback(message, 0)
        self._animate_loading()
    
    def stop_loading(self):
        """Stop loading animation"""
        self.is_loading = False
        if self.loading_animation_timer:
            self.widget.after_cancel(self.loading_animation_timer)
            self.loading_animation_timer = None
    
    def update_progress(self, message, progress):
        """Update loading progress"""
        if self.progress_callback:
            self.progress_callback(message, progress)
    
    def _animate_loading(self):
        """Internal loading animation"""
        if self.is_loading and self.widget.winfo_exists():
            # Simple animation logic here
            self.loading_animation_timer = self.widget.after(100, self._animate_loading)

def smooth_scroll_to(scrollable_frame, target_position, duration=300):
    """Smooth scroll animation for scrollable frames"""
    if not hasattr(scrollable_frame, '_scrollbar'):
        return
    
    start_position = scrollable_frame._parent_canvas.canvasy(0)
    distance = target_position - start_position
    steps = max(1, duration // 16)  # 60 FPS
    step_size = distance / steps
    
    def animate_step(step):
        if step < steps:
            current_pos = start_position + (step_size * step)
            scrollable_frame._parent_canvas.yview_moveto(current_pos)
            scrollable_frame.after(16, lambda: animate_step(step + 1))
    
    animate_step(0)

def optimize_image_loading(image_url: str, size: tuple = (240, 135)):
    """Optimize image loading with caching and resizing"""
    # Check cache first
    cache_key = f"{image_url}_{size[0]}x{size[1]}"
    cached_image = perf_manager.get_cached_thumbnail(cache_key)
    
    if cached_image:
        return cached_image
    
    # If not cached, this would typically load and process the image
    # For now, return None to indicate cache miss
    return None

def batch_operation(items, operation, batch_size=10, delay_between_batches=0.1):
    """Process items in batches to avoid blocking the UI"""
    def process_batch(start_index):
        end_index = min(start_index + batch_size, len(items))
        batch = items[start_index:end_index]
        
        for item in batch:
            operation(item)
        
        # Schedule next batch if there are more items
        if end_index < len(items):
            threading.Timer(
                delay_between_batches,
                lambda: process_batch(end_index)
            ).start()
    
    if items:
        process_batch(0)

# Memory management utilities
def cleanup_unused_resources():
    """Clean up unused resources to free memory"""
    perf_manager.clear_cache()
    
    # Clean up dead loading states
    try:
        # WeakSet automatically removes dead references
        pass
    except:
        pass

def get_performance_stats():
    """Get current performance statistics"""
    return {
        'thumbnail_cache_size': len(perf_manager.thumbnail_cache),
        'active_loading_states': len(perf_manager.loading_states),
        'cache_hit_ratio': getattr(perf_manager, '_cache_hits', 0) / max(getattr(perf_manager, '_cache_requests', 1), 1)
    }

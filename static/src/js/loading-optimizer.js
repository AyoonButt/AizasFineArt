// Advanced Loading Optimizer for Gallery, Shop & Artwork Details
// Optimizes perceived performance and user experience

class LoadingOptimizer {
    constructor(options = {}) {
        this.options = {
            skeletonDuration: 0,
            staggerDelay: 0,
            batchSize: 6,
            preloadCount: 12,
            virtualScrolling: true,
            prefetchNextPage: true,
            enableServiceWorker: true,
            ...options
        };
        
        this.loadedImages = new Set();
        this.imageCache = new Map();
        this.intersectionObserver = null;
        this.prefetchObserver = null;
        
        this.init();
    }
    
    init() {
        this.setupImageObserver();
        this.setupPrefetching();
        this.setupSkeletonLoading();
        this.setupProgressiveEnhancement();
        this.setupServiceWorker();
        
        // Performance timing
        this.markStart = performance.now();
    }
    
    setupImageObserver() {
        // High-performance intersection observer with different thresholds
        this.intersectionObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.loadImageWithPriority(entry.target);
                }
            });
        }, {
            rootMargin: '200px 0px', // Load images 200px before visible
            threshold: 0.01
        });
        
        // Only observe images that actually need lazy loading (have data-lazy attribute and no src)
        document.querySelectorAll('[data-lazy]').forEach(img => {
            // Skip images that already have a proper src URL
            if (!img.src || img.src.startsWith('data:') || img.src === window.location.href) {
                this.intersectionObserver.observe(img);
            }
        });
    }
    
    setupPrefetching() {
        // Prefetch observer for next page content
        this.prefetchObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.prefetchNextPageContent();
                }
            });
        }, {
            rootMargin: '400px 0px'
        });
        
        // Observe pagination/load more buttons
        const loadMoreBtn = document.querySelector('.load-more');
        if (loadMoreBtn) {
            this.prefetchObserver.observe(loadMoreBtn);
        }
    }
    
    setupSkeletonLoading() {
        // Skip skeleton creation for better performance
        return;
    }
    
    createSkeletonGrid(container) {
        // Removed for performance
        return;
    }
    
    calculateSkeletonCount() {
        const viewportWidth = window.innerWidth;
        const viewportHeight = window.innerHeight;
        const cardHeight = 400; // Approximate card height
        
        let columns;
        if (viewportWidth >= 1280) columns = 4;
        else if (viewportWidth >= 1024) columns = 3;
        else if (viewportWidth >= 640) columns = 2;
        else columns = 1;
        
        const rows = Math.ceil(viewportHeight / cardHeight) + 1;
        return Math.min(columns * rows, 12);
    }
    
    async loadImageWithPriority(img) {
        const imageSources = this.getImageSources(img);
        if (imageSources.length === 0) return;
        
        const primarySrc = imageSources[0];
        if (this.loadedImages.has(primarySrc)) {
            this.setImageSource(img, primarySrc);
            return;
        }
        
        const priority = img.dataset.priority || 'auto';
        
        try {
            // Skip loading shimmer for better performance
            
            // Try loading with fallback chain
            const successfulSrc = await this.loadImageWithFallbacks(imageSources, priority);
            
            // Set image immediately regardless of priority
            this.setImageSource(img, successfulSrc);
            
            this.loadedImages.add(primarySrc);
            // Cache successful source for future use
            this.imageCache.set(primarySrc + '_success', successfulSrc);
            
        } catch (error) {
            this.handleImageError(img);
        }
    }
    
    // Get multiple image sources from element
    getImageSources(img) {
        const sources = [];
        
        // Check for multiple source attributes in priority order
        const srcAttributes = [
            'data-lazy',           // Primary lazy source
            'data-src-gallery',    // High quality gallery image
            'data-src-thumbnail',  // Fast loading thumbnail
            'data-src',            // Alternative source
            'src'                  // Fallback to current src
        ];
        
        srcAttributes.forEach(attr => {
            const src = img.getAttribute(attr);
            if (src && src !== 'data:' && !sources.includes(src)) {
                sources.push(src);
            }
        });
        
        return sources.filter(Boolean);
    }
    
    // Enhanced image loading with multiple fallbacks
    async loadImageWithFallbacks(sources, priority = 'auto') {
        for (let i = 0; i < sources.length; i++) {
            const src = sources[i];
            
            // Check cache first
            const cacheKey = src + '_loaded';
            if (this.imageCache.has(cacheKey)) {
                return src; // Return cached successful source
            }
            
            try {
                await this.testImageLoad(src, priority);
                // Success - cache and return
                this.imageCache.set(cacheKey, true);
                return src;
            } catch (error) {
                console.warn(`Image source ${i + 1}/${sources.length} failed:`, src, error.message);
                // Continue to next source
            }
        }
        
        throw new Error('All image sources failed to load');
    }
    
    // Test individual image load with timeout and proper error handling
    testImageLoad(src, priority = 'auto') {
        return new Promise((resolve, reject) => {
            const img = new Image();
            
            // Set loading attributes
            img.crossOrigin = 'anonymous';
            if (priority === 'high') {
                img.fetchPriority = 'high';
                img.loading = 'eager';
            } else {
                img.fetchPriority = 'auto';
                img.loading = 'lazy';
            }
            
            // Set timeout based on priority
            const timeout = priority === 'high' ? 8000 : 12000;
            const timer = setTimeout(() => {
                img.onload = null;
                img.onerror = null;
                reject(new Error('Image load timeout'));
            }, timeout);
            
            img.onload = () => {
                clearTimeout(timer);
                resolve(img);
            };
            
            img.onerror = () => {
                clearTimeout(timer);
                reject(new Error('Image load error'));
            };
            
            img.src = src;
        });
    }
    
    // Legacy method for backwards compatibility
    preloadImage(src, priority = 'auto') {
        return this.testImageLoad(src, priority);
    }
    
    setImageSource(img, src = null) {
        const imageSrc = src || img.dataset.lazy;
        
        // Set image source immediately without transitions
        img.src = imageSrc;
        
        // Mark as loaded and stop observing
        img.dataset.lazyLoaded = 'true';
        if (this.intersectionObserver) {
            this.intersectionObserver.unobserve(img);
        }
    }
    
    handleImageError(img) {
        // Simple fallback - hide broken images
        img.style.display = 'none';
    }
    
    
    async prefetchNextPageContent() {
        if (!this.options.prefetchNextPage) return;
        
        const nextPageLink = document.querySelector('.load-more a, .pagination .next');
        if (!nextPageLink) return;
        
        const nextPageUrl = nextPageLink.href;
        
        try {
            // Prefetch next page HTML
            const response = await fetch(nextPageUrl, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'prefetch'
                }
            });
            
            if (response.ok) {
                const html = await response.text();
                // Parse and extract image URLs for preloading
                this.extractAndPreloadImages(html);
            }
        } catch (error) {
            console.warn('Prefetch failed:', error);
        }
    }
    
    extractAndPreloadImages(html) {
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        const images = doc.querySelectorAll('[data-lazy]');
        
        // Preload first few images from next page
        Array.from(images)
            .slice(0, this.options.preloadCount)
            .forEach(img => {
                this.preloadImage(img.dataset.lazy, 'low');
            });
    }
    
    setupProgressiveEnhancement() {
        // Enhanced progressive loading for artwork detail pages
        const artworkDetail = document.querySelector('.artwork-detail');
        if (artworkDetail) {
            this.optimizeArtworkDetailLoading();
        }
        
        // Enhanced masonry loading
        this.optimizeMasonryLoading();
    }
    
    optimizeArtworkDetailLoading() {
        // Prioritize main artwork image
        const mainImage = document.querySelector('#main-artwork-image, .main-artwork-image');
        if (mainImage && mainImage.dataset.lazy) {
            mainImage.dataset.priority = 'high';
            this.loadImageWithPriority(mainImage);
        }
        
        // Lazy load thumbnail images
        const thumbnails = document.querySelectorAll('.thumbnail-image[data-lazy]');
        thumbnails.forEach((thumb, index) => {
            thumb.dataset.priority = index < 4 ? 'high' : 'auto';
        });
    }
    
    optimizeMasonryLoading() {
        // Override masonry to load in batches for better performance
        const originalMasonry = window.initVariableMasonry;
        if (originalMasonry) {
            window.initVariableMasonry = () => {
                this.batchLoadMasonryItems(originalMasonry);
            };
        }
    }
    
    batchLoadMasonryItems(originalMasonry) {
        const items = document.querySelectorAll('.artwork-item');
        
        // Load all items immediately for better performance
        items.forEach(item => {
            const img = item.querySelector('[data-lazy]');
            if (img) {
                this.loadImageWithPriority(img);
            }
        });
        
        // Run masonry immediately
        originalMasonry();
    }
    
    setupServiceWorker() {
        if (!this.options.enableServiceWorker || !('serviceWorker' in navigator)) {
            return;
        }
        
        // Register service worker for caching
        navigator.serviceWorker.register('/static/sw.js')
            .then(registration => {
                console.log('SW registered:', registration);
            })
            .catch(error => {
                console.log('SW registration failed:', error);
            });
    }
    
    // Performance reporting
    reportPerformance() {
        const loadTime = performance.now() - this.markStart;
        
        // Send to performance monitor
        if (window.performanceMonitor) {
            window.performanceMonitor.metrics.optimizerLoadTime = loadTime;
            window.performanceMonitor.metrics.imagesPreloaded = this.imageCache.size;
            window.performanceMonitor.metrics.imagesLoaded = this.loadedImages.size;
        }
        
        return {
            loadTime,
            imagesPreloaded: this.imageCache.size,
            imagesLoaded: this.loadedImages.size
        };
    }
    
    // Cleanup
    destroy() {
        if (this.intersectionObserver) {
            this.intersectionObserver.disconnect();
        }
        if (this.prefetchObserver) {
            this.prefetchObserver.disconnect();
        }
        this.imageCache.clear();
        this.loadedImages.clear();
    }
}

// Minimal CSS for fast loading
const loadingCSS = `
/* Minimal image optimization */
img[data-lazy] {
    opacity: 1;
}

.artwork-image-container img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
}
`;

// Inject CSS
const style = document.createElement('style');
style.textContent = loadingCSS;
document.head.appendChild(style);

// Auto-initialize with safety checks
document.addEventListener('DOMContentLoaded', () => {
    // Only initialize if there are images that need lazy loading
    const lazyImages = document.querySelectorAll('[data-lazy]');
    if (lazyImages.length > 0) {
        window.loadingOptimizer = new LoadingOptimizer({
            skeletonDuration: 600,
            staggerDelay: 80,
            batchSize: 20,
            preloadCount: 6,
            prefetchNextPage: false,
            enableServiceWorker: false
        });
    }
});

// Re-initialize after dynamic content
if (typeof htmx !== 'undefined') {
    document.body.addEventListener('htmx:afterSettle', () => {
        if (window.loadingOptimizer) {
            window.loadingOptimizer.destroy();
            window.loadingOptimizer = new LoadingOptimizer();
        }
    });
}

// Export
window.LoadingOptimizer = LoadingOptimizer;
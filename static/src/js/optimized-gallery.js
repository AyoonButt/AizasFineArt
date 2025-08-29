/**
 * Optimized Gallery Performance System
 * Fixes loading issues with efficient lazy loading, masonry, and animations
 */

class OptimizedGallery {
    constructor() {
        this.images = [];
        this.masonryContainer = null;
        this.isLoading = false;
        this.intersectionObserver = null;
        this.resizeTimeout = null;
        
        this.init();
    }
    
    init() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setup());
        } else {
            this.setup();
        }
    }
    
    setup() {
        this.setupLazyLoading();
        this.setupMasonry();
        this.setupOptimizedAnimations();
        this.setupPerformanceMonitoring();
    }
    
    // Optimized Lazy Loading with Intersection Observer
    setupLazyLoading() {
        const imageObserverOptions = {
            root: null,
            rootMargin: '50px',
            threshold: 0.01
        };
        
        this.intersectionObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    this.loadImage(img);
                    observer.unobserve(img);
                }
            });
        }, imageObserverOptions);
        
        // Find all lazy images
        const lazyImages = document.querySelectorAll('img[data-src]');
        lazyImages.forEach(img => {
            this.intersectionObserver.observe(img);
        });
    }
    
    loadImage(img) {
        const dataSrc = img.getAttribute('data-src');
        if (!dataSrc) return;
        
        // Create new image to preload
        const imageLoader = new Image();
        
        imageLoader.onload = () => {
            // Fade in effect
            img.style.opacity = '0';
            img.src = dataSrc;
            img.removeAttribute('data-src');
            
            // Smooth fade in
            requestAnimationFrame(() => {
                img.style.transition = 'opacity 0.3s ease';
                img.style.opacity = '1';
            });
            
            // Trigger masonry recalculation if needed
            this.recalculateMasonry();
        };
        
        imageLoader.onerror = () => {
            // Handle error gracefully
            img.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 500"%3E%3Crect width="100%" height="100%" fill="%23f3f4f6"/%3E%3Ctext x="50%" y="50%" text-anchor="middle" fill="%23666"%3EImage Error%3C/text%3E%3C/svg%3E';
        };
        
        imageLoader.src = dataSrc;
    }
    
    // Efficient Masonry Layout
    setupMasonry() {
        this.masonryContainer = document.querySelector('.gallery-grid-large');
        if (!this.masonryContainer) return;
        
        // Use CSS Grid with auto-placement for better performance
        this.masonryContainer.style.cssText = `
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 1.5rem;
            grid-auto-rows: 10px;
        `;
        
        this.calculateMasonryLayout();
        
        // Throttled resize handler
        window.addEventListener('resize', () => {
            if (this.resizeTimeout) clearTimeout(this.resizeTimeout);
            this.resizeTimeout = setTimeout(() => this.calculateMasonryLayout(), 150);
        });
    }
    
    calculateMasonryLayout() {
        const items = this.masonryContainer?.querySelectorAll('.artwork-item');
        if (!items) return;
        
        // Use requestAnimationFrame for smooth updates
        requestAnimationFrame(() => {
            items.forEach(item => {
                const height = item.offsetHeight;
                const rowSpan = Math.ceil((height + 15) / 25); // 25px = 10px row + 15px gap
                item.style.gridRowEnd = `span ${rowSpan}`;
            });
        });
    }
    
    recalculateMasonry() {
        // Debounced recalculation
        if (this.recalculateTimeout) clearTimeout(this.recalculateTimeout);
        this.recalculateTimeout = setTimeout(() => this.calculateMasonryLayout(), 100);
    }
    
    // Optimized Animation System
    setupOptimizedAnimations() {
        // Single scroll listener with throttling
        let ticking = false;
        
        const handleScroll = () => {
            if (!ticking) {
                requestAnimationFrame(() => {
                    this.handleScrollAnimations();
                    ticking = false;
                });
                ticking = true;
            }
        };
        
        // Passive event listener for better performance
        window.addEventListener('scroll', handleScroll, { passive: true });
    }
    
    handleScrollAnimations() {
        const scrollTop = window.pageYOffset;
        const windowHeight = window.innerHeight;
        
        // Get all animation elements
        const animateElements = document.querySelectorAll('[data-scroll-item]:not(.scroll-item-revealed)');
        
        // Use DocumentFragment for batch DOM updates
        const elementsToAnimate = [];
        
        animateElements.forEach(element => {
            const elementTop = element.getBoundingClientRect().top + scrollTop;
            const elementBottom = elementTop + element.offsetHeight;
            
            // Check if element is in viewport
            if (elementTop < scrollTop + windowHeight && elementBottom > scrollTop) {
                elementsToAnimate.push(element);
            }
        });
        
        // Batch DOM updates
        if (elementsToAnimate.length > 0) {
            requestAnimationFrame(() => {
                elementsToAnimate.forEach(element => {
                    element.classList.add('scroll-item-revealed');
                });
            });
        }
    }
    
    // Performance Monitoring
    setupPerformanceMonitoring() {
        if ('performance' in window && 'PerformanceObserver' in window) {
            // Monitor Largest Contentful Paint
            const observer = new PerformanceObserver((list) => {
                const entries = list.getEntries();
                const lastEntry = entries[entries.length - 1];
                console.log('LCP:', lastEntry.startTime);
            });
            
            observer.observe({ entryTypes: ['largest-contentful-paint'] });
        }
    }
    
    // Public API
    refresh() {
        this.recalculateMasonry();
    }
    
    destroy() {
        if (this.intersectionObserver) {
            this.intersectionObserver.disconnect();
        }
        if (this.resizeTimeout) {
            clearTimeout(this.resizeTimeout);
        }
        if (this.recalculateTimeout) {
            clearTimeout(this.recalculateTimeout);
        }
    }
}

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.optimizedGallery = new OptimizedGallery();
    });
} else {
    window.optimizedGallery = new OptimizedGallery();
}

// Export for manual initialization
window.OptimizedGallery = OptimizedGallery;
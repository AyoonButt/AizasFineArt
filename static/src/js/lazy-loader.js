// Vanilla JS Lazy Loading System for Aiza's Fine Art
// Optimized for performance without external dependencies

class LazyLoader {
    constructor(options = {}) {
        this.options = {
            threshold: 0.1,
            rootMargin: '50px 0px',
            enableAnimations: true,
            loadingClass: 'lazy-loading',
            loadedClass: 'lazy-loaded',
            errorClass: 'lazy-error',
            ...options
        };
        
        this.observer = null;
        this.init();
    }
    
    init() {
        // Check if Intersection Observer is supported
        if (!('IntersectionObserver' in window)) {
            // Fallback for older browsers
            this.loadAllImages();
            return;
        }
        
        this.observer = new IntersectionObserver(
            this.handleIntersection.bind(this), 
            {
                threshold: this.options.threshold,
                rootMargin: this.options.rootMargin
            }
        );
        
        this.observeImages();
        this.setupPreloading();
    }
    
    observeImages() {
        const lazyImages = document.querySelectorAll('[data-lazy]:not([data-lazy-loaded])');
        lazyImages.forEach(img => {
            this.observer.observe(img);
            
            // Add loading class
            img.classList.add(this.options.loadingClass);
            
            // Create placeholder background
            this.createPlaceholder(img);
        });
    }
    
    createPlaceholder(img) {
        const aspectRatio = img.dataset.aspectRatio || '4/5';
        const placeholder = img.dataset.placeholder;
        
        if (placeholder) {
            img.style.backgroundImage = `url(${placeholder})`;
            img.style.backgroundSize = 'cover';
            img.style.backgroundPosition = 'center';
        } else {
            // Create a simple gradient placeholder
            img.style.background = 'linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%)';
        }
        
        img.style.aspectRatio = aspectRatio;
    }
    
    handleIntersection(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                this.loadImage(entry.target);
                this.observer.unobserve(entry.target);
            }
        });
    }
    
    loadImage(img) {
        const src = img.dataset.lazy;
        const priority = img.dataset.priority || 'auto';
        
        // Set loading priority
        if (priority === 'high') {
            img.loading = 'eager';
        } else {
            img.loading = 'lazy';
        }
        
        // Handle loading states
        img.onload = () => this.handleImageLoad(img);
        img.onerror = () => this.handleImageError(img);
        
        // Start loading
        img.src = src;
        img.dataset.lazyLoaded = 'true';
    }
    
    handleImageLoad(img) {
        img.classList.remove(this.options.loadingClass);
        img.classList.add(this.options.loadedClass);
        
        // Clear placeholder background
        img.style.background = '';
        
        // Trigger animation if enabled
        if (this.options.enableAnimations) {
            this.animateImageIn(img);
        }
        
        // Fire custom event
        img.dispatchEvent(new CustomEvent('lazyloaded', {
            detail: { element: img }
        }));
    }
    
    handleImageError(img) {
        img.classList.remove(this.options.loadingClass);
        img.classList.add(this.options.errorClass);
        
        // Set fallback image or placeholder
        const fallback = img.dataset.fallback || '/static/dist/images/placeholder.svg';
        img.src = fallback;
        
        console.warn('Failed to load image:', img.dataset.lazy);
    }
    
    animateImageIn(img) {
        img.style.transition = 'opacity 0.3s ease';
        img.style.opacity = '0';
        
        requestAnimationFrame(() => {
            img.style.opacity = '1';
        });
    }
    
    setupPreloading() {
        // Preload images marked as high priority
        const highPriorityImages = document.querySelectorAll('[data-lazy][data-priority="high"]');
        highPriorityImages.forEach(img => {
            const link = document.createElement('link');
            link.rel = 'preload';
            link.as = 'image';
            link.href = img.dataset.lazy;
            document.head.appendChild(link);
        });
    }
    
    loadAllImages() {
        // Fallback for browsers without IntersectionObserver
        const lazyImages = document.querySelectorAll('[data-lazy]:not([data-lazy-loaded])');
        lazyImages.forEach(img => this.loadImage(img));
    }
    
    refresh() {
        // Re-observe new images added to the DOM
        this.observeImages();
    }
    
    destroy() {
        if (this.observer) {
            this.observer.disconnect();
        }
    }
}

// Auto-initialize
document.addEventListener('DOMContentLoaded', () => {
    window.lazyLoader = new LazyLoader({
        threshold: 0.1,
        rootMargin: '100px 0px',
        enableAnimations: true
    });
});

// Re-initialize after HTMX swaps
if (typeof htmx !== 'undefined') {
    document.body.addEventListener('htmx:afterSettle', () => {
        if (window.lazyLoader) {
            window.lazyLoader.refresh();
        }
    });
}

// Export for manual use
window.LazyLoader = LazyLoader;
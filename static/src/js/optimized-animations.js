/**
 * Optimized Animation System
 * Addresses performance issues in animations.js
 */

class OptimizedAnimations {
    constructor() {
        this.isReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        this.observers = new Map();
        this.scrollTicking = false;
        this.activeAnimations = new Set();
        
        this.init();
    }
    
    init() {
        if (this.isReducedMotion) {
            this.showAllElements();
            return;
        }
        
        this.setupSingleIntersectionObserver();
        this.setupOptimizedScrollEffects();
    }
    
    showAllElements() {
        const elements = document.querySelectorAll('.animate-on-scroll, [data-animate]');
        elements.forEach(el => {
            el.style.opacity = '1';
            el.style.transform = 'none';
            el.classList.add('animate-in');
        });
    }
    
    setupSingleIntersectionObserver() {
        if (!window.IntersectionObserver) return;
        
        // Single observer for all animation elements
        const observer = new IntersectionObserver(
            (entries) => this.handleIntersections(entries),
            {
                root: null,
                rootMargin: '50px 0px -50px 0px',
                threshold: [0.1, 0.3, 0.5]
            }
        );
        
        // Collect all animation elements at once
        const elements = document.querySelectorAll(`
            .animate-on-scroll,
            [data-animate],
            .artwork-card,
            [data-counter]
        `);
        
        elements.forEach(element => {
            observer.observe(element);
        });
        
        this.observers.set('main', observer);
    }
    
    handleIntersections(entries) {
        // Batch process entries for better performance
        const toAnimate = [];
        
        entries.forEach(entry => {
            if (entry.isIntersecting && !entry.target.classList.contains('animate-in')) {
                toAnimate.push(entry.target);
            }
        });
        
        if (toAnimate.length > 0) {
            this.batchAnimate(toAnimate);
        }
    }
    
    batchAnimate(elements) {
        // Use single requestAnimationFrame for batch animations
        requestAnimationFrame(() => {
            elements.forEach((element, index) => {
                // Stagger animations for visual appeal
                setTimeout(() => {
                    this.animateElement(element);
                }, index * 50);
            });
        });
    }
    
    animateElement(element) {
        if (this.activeAnimations.has(element)) return;
        
        this.activeAnimations.add(element);
        element.classList.add('animate-in');
        
        // Handle special element types
        if (element.hasAttribute('data-counter')) {
            this.animateCounter(element);
        }
        
        // Cleanup after animation
        setTimeout(() => {
            this.activeAnimations.delete(element);
            // Unobserve to improve performance
            const observer = this.observers.get('main');
            if (observer) observer.unobserve(element);
        }, 500);
    }
    
    setupOptimizedScrollEffects() {
        // Single throttled scroll handler
        const handleScroll = () => {
            if (!this.scrollTicking) {
                requestAnimationFrame(() => {
                    this.updateScrollEffects();
                    this.scrollTicking = false;
                });
                this.scrollTicking = true;
            }
        };
        
        window.addEventListener('scroll', handleScroll, { 
            passive: true,
            capture: false
        });
    }
    
    updateScrollEffects() {
        const scrollY = window.scrollY;
        
        // Batch DOM reads and writes
        const elements = {
            navbar: document.querySelector('nav'),
            hero: document.querySelector('.hero-section')
        };
        
        // Read phase
        const measurements = {
            scrollThreshold: scrollY > 50
        };
        
        // Write phase
        if (elements.navbar) {
            elements.navbar.classList.toggle('scrolled', measurements.scrollThreshold);
        }
        
        if (elements.hero && scrollY < window.innerHeight) {
            // Only apply parallax when element is visible
            elements.hero.style.transform = `translateY(${scrollY * 0.3}px)`;
        }
    }
    
    animateCounter(element) {
        const target = parseInt(element.dataset.counter);
        const duration = 1500; // Fixed duration for consistency
        const startTime = performance.now();
        
        const updateCounter = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Use easing function for smooth animation
            const eased = this.easeOutQuart(progress);
            const current = Math.floor(target * eased);
            
            element.textContent = current;
            
            if (progress < 1) {
                requestAnimationFrame(updateCounter);
            } else {
                element.textContent = target;
            }
        };
        
        requestAnimationFrame(updateCounter);
    }
    
    easeOutQuart(t) {
        return 1 - Math.pow(1 - t, 4);
    }
    
    destroy() {
        this.observers.forEach(observer => observer.disconnect());
        this.observers.clear();
        this.activeAnimations.clear();
    }
}

// Initialize optimized animations
document.addEventListener('DOMContentLoaded', () => {
    if (window.scrollAnimations) {
        window.scrollAnimations.destroy();
    }
    window.scrollAnimations = new OptimizedAnimations();
});

// Cleanup
window.addEventListener('beforeunload', () => {
    if (window.scrollAnimations) {
        window.scrollAnimations.destroy();
    }
});
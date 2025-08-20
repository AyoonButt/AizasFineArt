/**
 * Scroll animations and interactive effects for Aiza's Fine Art
 * Using Intersection Observer API for smooth scroll animations
 */

class ScrollAnimations {
    constructor() {
        this.init();
    }

    init() {
        this.setupIntersectionObserver();
        this.setupScrollEffects();
        this.setupParallaxEffects();
        this.setupCounterAnimations();
    }

    /**
     * Setup Intersection Observer for fade-in animations
     */
    setupIntersectionObserver() {
        // Check if Intersection Observer is supported
        if (!window.IntersectionObserver) return;

        const observerOptions = {
            root: null,
            rootMargin: '0px 0px -100px 0px',
            threshold: 0.1
        };

        // Create observer for fade-in animations
        const fadeObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                    
                    // Add stagger delay for child elements
                    const children = entry.target.querySelectorAll('[data-stagger]');
                    children.forEach((child, index) => {
                        setTimeout(() => {
                            child.classList.add('animate-in');
                        }, index * 100);
                    });
                }
            });
        }, observerOptions);

        // Observe elements with animation attributes
        const animationElements = document.querySelectorAll('[data-animate]');
        animationElements.forEach(element => {
            element.classList.add('animate-ready');
            fadeObserver.observe(element);
        });

        // Observe gallery items
        const galleryItems = document.querySelectorAll('.artwork-card');
        galleryItems.forEach((item, index) => {
            item.classList.add('animate-ready');
            item.style.transitionDelay = `${index * 50}ms`;
            fadeObserver.observe(item);
        });
    }

    /**
     * Setup scroll-based effects
     */
    setupScrollEffects() {
        let ticking = false;

        const handleScroll = () => {
            if (!ticking) {
                requestAnimationFrame(() => {
                    this.updateScrollEffects();
                    ticking = false;
                });
                ticking = true;
            }
        };

        window.addEventListener('scroll', handleScroll, { passive: true });
        
        // Initial call
        this.updateScrollEffects();
    }

    /**
     * Update scroll-based effects
     */
    updateScrollEffects() {
        const scrollY = window.scrollY;
        const windowHeight = window.innerHeight;

        // Navbar background blur on scroll
        const navbar = document.querySelector('nav');
        if (navbar) {
            if (scrollY > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        }

        // Hero parallax effect
        const hero = document.querySelector('.hero-section');
        if (hero) {
            const speed = 0.5;
            hero.style.transform = `translateY(${scrollY * speed}px)`;
        }

        // Section reveal animations
        const sections = document.querySelectorAll('[data-scroll-section]');
        sections.forEach(section => {
            const rect = section.getBoundingClientRect();
            const isVisible = rect.top < windowHeight && rect.bottom > 0;
            
            if (isVisible && !section.classList.contains('section-revealed')) {
                section.classList.add('section-revealed');
                
                // Animate child elements with stagger
                const children = section.querySelectorAll('[data-scroll-item]');
                children.forEach((child, index) => {
                    setTimeout(() => {
                        child.classList.add('scroll-item-revealed');
                    }, index * 100);
                });
            }
        });
    }

    /**
     * Setup parallax effects for images
     */
    setupParallaxEffects() {
        const parallaxElements = document.querySelectorAll('[data-parallax]');
        
        if (parallaxElements.length === 0) return;

        const handleParallax = () => {
            if (!ticking) {
                requestAnimationFrame(() => {
                    this.updateParallax();
                    ticking = false;
                });
                ticking = true;
            }
        };

        let ticking = false;
        window.addEventListener('scroll', handleParallax, { passive: true });
    }

    /**
     * Update parallax effects
     */
    updateParallax() {
        const scrollY = window.scrollY;
        
        const parallaxElements = document.querySelectorAll('[data-parallax]');
        parallaxElements.forEach(element => {
            const speed = parseFloat(element.dataset.parallax) || 0.5;
            const yPos = -(scrollY * speed);
            element.style.transform = `translateY(${yPos}px)`;
        });
    }

    /**
     * Setup counter animations for statistics
     */
    setupCounterAnimations() {
        const counters = document.querySelectorAll('[data-counter]');
        
        if (counters.length === 0) return;

        const observerOptions = {
            root: null,
            rootMargin: '0px',
            threshold: 0.5
        };

        const counterObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.animateCounter(entry.target);
                    counterObserver.unobserve(entry.target);
                }
            });
        }, observerOptions);

        counters.forEach(counter => {
            counterObserver.observe(counter);
        });
    }

    /**
     * Animate a counter element
     */
    animateCounter(element) {
        const target = parseInt(element.dataset.counter);
        const duration = parseInt(element.dataset.duration) || 2000;
        const increment = target / (duration / 16); // 60fps
        
        let current = 0;
        
        const updateCounter = () => {
            current += increment;
            if (current < target) {
                element.textContent = Math.floor(current);
                requestAnimationFrame(updateCounter);
            } else {
                element.textContent = target;
            }
        };
        
        updateCounter();
    }

    /**
     * Add smooth scroll to anchor links
     */
    setupSmoothScroll() {
        const links = document.querySelectorAll('a[href^="#"]');
        
        links.forEach(link => {
            link.addEventListener('click', (e) => {
                const targetId = link.getAttribute('href');
                const targetElement = document.querySelector(targetId);
                
                if (targetElement) {
                    e.preventDefault();
                    
                    targetElement.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }
}

/**
 * HTMX-specific animations
 */
class HTMXAnimations {
    constructor() {
        this.init();
    }

    init() {
        this.setupHTMXAnimations();
    }

    setupHTMXAnimations() {
        // Animate HTMX content swaps
        document.body.addEventListener('htmx:beforeSwap', (e) => {
            // Add fade-out class to current content
            if (e.target.classList.contains('htmx-animate')) {
                e.target.classList.add('htmx-fade-out');
            }
        });

        document.body.addEventListener('htmx:afterSwap', (e) => {
            // Remove fade-out and add fade-in to new content
            if (e.target.classList.contains('htmx-animate')) {
                e.target.classList.remove('htmx-fade-out');
                e.target.classList.add('htmx-fade-in');
                
                // Re-initialize animations for new content
                this.reinitializeAnimations(e.target);
                
                // Remove fade-in class after animation
                setTimeout(() => {
                    e.target.classList.remove('htmx-fade-in');
                }, 300);
            }
        });

        // Loading states
        document.body.addEventListener('htmx:beforeRequest', (e) => {
            if (e.target.classList.contains('htmx-loading-animate')) {
                e.target.classList.add('htmx-loading');
            }
        });

        document.body.addEventListener('htmx:afterRequest', (e) => {
            if (e.target.classList.contains('htmx-loading-animate')) {
                e.target.classList.remove('htmx-loading');
            }
        });
    }

    reinitializeAnimations(container) {
        // Re-observe new elements for intersection
        if (window.scrollAnimations) {
            const animationElements = container.querySelectorAll('[data-animate]');
            animationElements.forEach(element => {
                element.classList.add('animate-ready');
                // Re-observe with intersection observer
            });
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.scrollAnimations = new ScrollAnimations();
    window.htmxAnimations = new HTMXAnimations();
});

// Re-initialize animations after HTMX swaps
document.body.addEventListener('htmx:afterSettle', () => {
    if (window.scrollAnimations) {
        window.scrollAnimations.setupIntersectionObserver();
    }
});
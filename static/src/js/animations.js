/**
 * Aiza's Fine Art - Enhanced Animation System
 * Sea Glass & Rosewood Design System Integration
 * Using Intersection Observer API for smooth scroll animations
 */

class ScrollAnimations {
    constructor() {
        this.isReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        this.observers = new Map();
        
        // Detect performance-critical pages and disable animations
        const currentPath = window.location.pathname;
        this.isPerformancePage = currentPath.includes('/shop') || 
                                 currentPath.includes('/gallery') ||
                                 currentPath.includes('/search');
        
        this.init();
    }

    init() {
        // Skip animations on performance-critical pages or if reduced motion is preferred
        if (this.isReducedMotion || this.isPerformancePage) {
            // Add performance class to body for CSS overrides
            if (this.isPerformancePage) {
                document.body.classList.add('performance-page');
            }
            this.showAllElements();
            return;
        }

        this.setupIntersectionObserver();
        this.setupScrollEffects();
        this.setupParallaxEffects();
        this.setupCounterAnimations();
        this.setupHoverEffects();
        this.setupPageTransitions();
    }

    showAllElements() {
        // Show all animated elements immediately for reduced motion
        const elements = document.querySelectorAll('.animate-on-scroll, [data-animate]');
        elements.forEach(el => {
            el.style.opacity = '1';
            el.style.transform = 'none';
            el.classList.add('animate-in');
        });
    }

    /**
     * Setup Intersection Observer for scroll-triggered animations
     */
    setupIntersectionObserver() {
        // Skip intersection observer on performance pages
        if (this.isPerformancePage || !window.IntersectionObserver) return;

        const observerOptions = {
            root: null,
            rootMargin: '0px 0px -50px 0px',
            threshold: 0.1
        };

        // Main scroll animation observer
        const scrollObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.animateElement(entry.target);
                }
            });
        }, observerOptions);

        // Observe elements with our design system animation classes
        const animationSelectors = [
            '.animate-on-scroll',
            '[data-animate]'
        ];

        animationSelectors.forEach(selector => {
            const elements = document.querySelectorAll(selector);
            elements.forEach(element => {
                scrollObserver.observe(element);
            });
        });

        // Special handling for artwork cards with stagger
        const artworkCards = document.querySelectorAll('.artwork-card');
        artworkCards.forEach((card, index) => {
            card.classList.add('animate-on-scroll', 'scale');
            card.style.transitionDelay = `${index * 100}ms`;
            scrollObserver.observe(card);
        });

        this.observers.set('scroll', scrollObserver);
    }

    animateElement(element) {
        // Apply appropriate animation based on element classes
        const delay = element.dataset.animationDelay || 0;
        
        setTimeout(() => {
            element.classList.add('animate-in');
            
            // Handle staggered child animations
            const staggerChildren = element.querySelectorAll('[data-stagger]');
            staggerChildren.forEach((child, index) => {
                setTimeout(() => {
                    child.classList.add('animate-in');
                }, index * 100);
            });
        }, parseInt(delay));

        // Unobserve after animation to improve performance
        const observer = this.observers.get('scroll');
        if (observer) {
            observer.unobserve(element);
        }
    }

    /**
     * Setup scroll-based effects
     */
    setupScrollEffects() {
        // Skip all scroll effects on performance pages
        if (this.isPerformancePage) {
            return;
        }
        
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
        // Skip all parallax effects on performance pages
        if (this.isPerformancePage) {
            return;
        }
        
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
     * Setup hover effects for interactive elements
     */
    setupHoverEffects() {
        if (this.isReducedMotion) return;

        // Enhanced card hover effects
        const cards = document.querySelectorAll('.card, .artwork-card');
        cards.forEach(card => {
            card.addEventListener('mouseenter', this.handleCardEnter.bind(this));
            card.addEventListener('mouseleave', this.handleCardLeave.bind(this));
            card.addEventListener('mousemove', this.handleCardMove.bind(this));
        });

        // Button hover effects
        const buttons = document.querySelectorAll('.btn');
        buttons.forEach(button => {
            button.addEventListener('mouseenter', this.handleButtonEnter.bind(this));
            button.addEventListener('mouseleave', this.handleButtonLeave.bind(this));
        });
    }

    handleCardEnter(event) {
        const card = event.currentTarget;
        card.style.transition = 'transform var(--transition-base), box-shadow var(--transition-base)';
        card.style.transform = 'translateY(-4px)';
        card.style.boxShadow = 'var(--shadow-lg)';
    }

    handleCardLeave(event) {
        const card = event.currentTarget;
        card.style.transform = 'translateY(0)';
        card.style.boxShadow = 'var(--shadow-sm)';
    }

    handleCardMove(event) {
        if (this.isReducedMotion) return;
        
        const card = event.currentTarget;
        const rect = card.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;
        
        const rotateX = (y - centerY) / 20;
        const rotateY = (centerX - x) / 20;
        
        card.style.transform = `translateY(-4px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
    }

    handleButtonEnter(event) {
        const button = event.currentTarget;
        button.style.transform = 'translateY(-1px) scale(1.02)';
    }

    handleButtonLeave(event) {
        const button = event.currentTarget;
        button.style.transform = 'translateY(0) scale(1)';
    }

    /**
     * Setup smooth page transitions
     */
    setupPageTransitions() {
        // Fade in page content on load
        document.body.style.opacity = '0';
        document.body.style.transition = 'opacity var(--transition-slow)';
        
        window.addEventListener('load', () => {
            document.body.style.opacity = '1';
        });

        // Handle internal navigation links
        const navLinks = document.querySelectorAll('nav a[href^="/"], nav a[href^="./"]');
        navLinks.forEach(link => {
            if (link.hostname === window.location.hostname) {
                link.addEventListener('click', this.handlePageTransition.bind(this));
            }
        });
    }

    handlePageTransition(event) {
        if (this.isReducedMotion) return;
        
        const link = event.currentTarget;
        const href = link.href;
        
        // Skip if it's an external link or has target="_blank"
        if (link.target === '_blank' || link.hostname !== window.location.hostname) {
            return;
        }

        event.preventDefault();
        
        // Fade out current page
        document.body.style.opacity = '0';
        
        // Navigate after fade completes
        setTimeout(() => {
            window.location.href = href;
        }, 200);
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

    /**
     * Cleanup observers on page unload
     */
    destroy() {
        this.observers.forEach(observer => observer.disconnect());
        this.observers.clear();
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
        window.scrollAnimations.setupHoverEffects();
    }
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (window.scrollAnimations) {
        window.scrollAnimations.destroy();
    }
});

// Handle browser back/forward navigation
window.addEventListener('pageshow', (event) => {
    // Re-initialize animations if page was loaded from cache
    if (event.persisted) {
        if (window.scrollAnimations) {
            window.scrollAnimations.destroy();
            window.scrollAnimations = new ScrollAnimations();
        }
    }
});
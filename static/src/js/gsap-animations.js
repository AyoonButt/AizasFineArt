/**
 * GSAP Animation System for Aiza's Fine Art
 * Professional animations for Django components with HTMX integration
 */

class GSAPAnimations {
    constructor() {
        this.tl = gsap.timeline();
        this.components = new Map();
        this.observerOptions = {
            root: null,
            rootMargin: '0px 0px -50px 0px',
            threshold: 0.1
        };
        
        this.init();
    }

    init() {
        // Wait for DOM and GSAP to be ready
        if (typeof gsap === 'undefined') {
            console.error('GSAP not loaded');
            return;
        }

        // Set GSAP defaults
        gsap.defaults({
            duration: 0.6,
            ease: "power2.out"
        });

        this.setupIntersectionObserver();
        this.setupHTMXAnimations();
        this.registerComponentAnimations();
    }

    /**
     * Setup Intersection Observer for scroll-triggered animations
     */
    setupIntersectionObserver() {
        if (!window.IntersectionObserver) return;

        this.observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.animateElement(entry.target);
                    this.observer.unobserve(entry.target);
                }
            });
        }, this.observerOptions);

        // Observe initial elements
        this.observeElements();
    }

    /**
     * Observe elements for scroll animations
     */
    observeElements() {
        const elements = document.querySelectorAll('[data-gsap], .artwork-card, .form-container, [data-component]');
        elements.forEach(el => {
            if (!el.hasAttribute('data-gsap-observed')) {
                el.setAttribute('data-gsap-observed', 'true');
                this.observer.observe(el);
            }
        });
    }

    /**
     * Animate element based on its type or data attributes
     */
    animateElement(element) {
        const animationType = element.dataset.gsap || this.getDefaultAnimation(element);
        
        switch (animationType) {
            case 'fadeInUp':
                this.fadeInUp(element);
                break;
            case 'fadeInLeft':
                this.fadeInLeft(element);
                break;
            case 'fadeInRight':
                this.fadeInRight(element);
                break;
            case 'staggerChildren':
                this.staggerChildren(element);
                break;
            case 'scaleIn':
                this.scaleIn(element);
                break;
            case 'slideInUp':
                this.slideInUp(element);
                break;
            default:
                this.fadeInUp(element);
        }
    }

    /**
     * Get default animation based on element type
     */
    getDefaultAnimation(element) {
        if (element.classList.contains('artwork-card')) return 'scaleIn';
        if (element.classList.contains('form-container')) return 'fadeInUp';
        if (element.dataset.component === 'gallery-grid') return 'staggerChildren';
        if (element.dataset.component === 'gallery-filters') return 'slideInUp';
        return 'fadeInUp';
    }

    // Animation Methods

    fadeInUp(element, duration = 0.8) {
        gsap.fromTo(element, 
            { 
                opacity: 0, 
                y: 30 
            },
            { 
                opacity: 1, 
                y: 0, 
                duration,
                ease: "power2.out"
            }
        );
    }

    fadeInLeft(element, duration = 0.8) {
        gsap.fromTo(element,
            {
                opacity: 0,
                x: -30
            },
            {
                opacity: 1,
                x: 0,
                duration,
                ease: "power2.out"
            }
        );
    }

    fadeInRight(element, duration = 0.8) {
        gsap.fromTo(element,
            {
                opacity: 0,
                x: 30
            },
            {
                opacity: 1,
                x: 0,
                duration,
                ease: "power2.out"
            }
        );
    }

    scaleIn(element, duration = 0.6) {
        gsap.fromTo(element,
            {
                opacity: 0,
                scale: 0.9,
                transformOrigin: "center center"
            },
            {
                opacity: 1,
                scale: 1,
                duration,
                ease: "back.out(1.2)"
            }
        );
    }

    slideInUp(element, duration = 0.7) {
        gsap.fromTo(element,
            {
                opacity: 0,
                y: 50
            },
            {
                opacity: 1,
                y: 0,
                duration,
                ease: "power3.out"
            }
        );
    }

    staggerChildren(element, stagger = 0.1) {
        const children = element.children;
        gsap.fromTo(children,
            {
                opacity: 0,
                y: 20
            },
            {
                opacity: 1,
                y: 0,
                duration: 0.6,
                stagger: stagger,
                ease: "power2.out"
            }
        );
    }

    /**
     * Setup HTMX-specific animations
     */
    setupHTMXAnimations() {
        document.body.addEventListener('htmx:beforeSwap', (e) => {
            this.beforeHTMXSwap(e.target);
        });

        document.body.addEventListener('htmx:afterSwap', (e) => {
            this.afterHTMXSwap(e.target);
        });

        document.body.addEventListener('htmx:beforeRequest', (e) => {
            this.showLoadingAnimation(e.target);
        });

        document.body.addEventListener('htmx:afterRequest', (e) => {
            this.hideLoadingAnimation(e.target);
        });
    }

    beforeHTMXSwap(element) {
        if (element.classList.contains('htmx-animate')) {
            gsap.to(element, {
                opacity: 0,
                y: -10,
                duration: 0.2,
                ease: "power2.in"
            });
        }
    }

    afterHTMXSwap(element) {
        if (element.classList.contains('htmx-animate')) {
            gsap.fromTo(element,
                {
                    opacity: 0,
                    y: 10
                },
                {
                    opacity: 1,
                    y: 0,
                    duration: 0.4,
                    ease: "power2.out"
                }
            );

            // Re-observe new elements
            this.observeElements();
        }
    }

    showLoadingAnimation(element) {
        if (element.classList.contains('htmx-loading-animate')) {
            const loadingSpinner = element.querySelector('.htmx-indicator');
            if (loadingSpinner) {
                gsap.to(loadingSpinner, {
                    rotation: 360,
                    duration: 1,
                    ease: "none",
                    repeat: -1
                });
            }
        }
    }

    hideLoadingAnimation(element) {
        if (element.classList.contains('htmx-loading-animate')) {
            const loadingSpinner = element.querySelector('.htmx-indicator');
            if (loadingSpinner) {
                gsap.killTweensOf(loadingSpinner);
                gsap.set(loadingSpinner, { rotation: 0 });
            }
        }
    }

    /**
     * Register component-specific animations
     */
    registerComponentAnimations() {
        // Gallery animations
        this.registerGalleryAnimations();
        
        // Form animations
        this.registerFormAnimations();
        
        // Navigation animations
        this.registerNavAnimations();
    }

    registerGalleryAnimations() {
        // Artwork card hover animations
        document.addEventListener('mouseenter', (e) => {
            if (e.target.closest('.artwork-card')) {
                const card = e.target.closest('.artwork-card');
                gsap.to(card, {
                    y: -8,
                    scale: 1.02,
                    duration: 0.3,
                    ease: "power2.out"
                });
            }
        }, true);

        document.addEventListener('mouseleave', (e) => {
            if (e.target.closest('.artwork-card')) {
                const card = e.target.closest('.artwork-card');
                gsap.to(card, {
                    y: 0,
                    scale: 1,
                    duration: 0.3,
                    ease: "power2.out"
                });
            }
        }, true);

        // Filter animations
        const filterButtons = document.querySelectorAll('[data-filter]');
        filterButtons.forEach(button => {
            button.addEventListener('click', () => {
                gsap.to(button, {
                    scale: 0.95,
                    duration: 0.1,
                    yoyo: true,
                    repeat: 1,
                    ease: "power2.inOut"
                });
            });
        });
    }

    registerFormAnimations() {
        // Form field focus animations
        document.addEventListener('focus', (e) => {
            if (e.target.matches('.form-input, .form-textarea, .form-select')) {
                gsap.to(e.target, {
                    scale: 1.01,
                    duration: 0.2,
                    ease: "power2.out"
                });
            }
        }, true);

        document.addEventListener('blur', (e) => {
            if (e.target.matches('.form-input, .form-textarea, .form-select')) {
                gsap.to(e.target, {
                    scale: 1,
                    duration: 0.2,
                    ease: "power2.out"
                });
            }
        }, true);

        // Button press animations
        document.addEventListener('click', (e) => {
            if (e.target.matches('.btn-primary, .btn-secondary, .btn-outline')) {
                gsap.to(e.target, {
                    scale: 0.97,
                    duration: 0.1,
                    yoyo: true,
                    repeat: 1,
                    ease: "power2.inOut"
                });
            }
        }, true);
    }

    registerNavAnimations() {
        // Navigation link hover effects
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('mouseenter', () => {
                gsap.to(link, {
                    y: -2,
                    duration: 0.2,
                    ease: "power2.out"
                });
            });

            link.addEventListener('mouseleave', () => {
                gsap.to(link, {
                    y: 0,
                    duration: 0.2,
                    ease: "power2.out"
                });
            });
        });
    }

    /**
     * Animate page transitions
     */
    pageTransition() {
        const tl = gsap.timeline();
        
        tl.to('.page-content', {
            opacity: 0,
            y: 20,
            duration: 0.3,
            ease: "power2.in"
        })
        .to('.page-content', {
            opacity: 1,
            y: 0,
            duration: 0.5,
            ease: "power2.out"
        });

        return tl;
    }

    /**
     * Animate modal/popup appearance
     */
    modalAnimation(modal, show = true) {
        if (show) {
            gsap.fromTo(modal,
                {
                    opacity: 0,
                    scale: 0.9,
                    y: 20
                },
                {
                    opacity: 1,
                    scale: 1,
                    y: 0,
                    duration: 0.4,
                    ease: "back.out(1.2)"
                }
            );
        } else {
            gsap.to(modal, {
                opacity: 0,
                scale: 0.9,
                y: -20,
                duration: 0.3,
                ease: "power2.in"
            });
        }
    }

    /**
     * Refresh animations for new content
     */
    refresh() {
        this.observeElements();
    }

    /**
     * Kill all animations
     */
    destroy() {
        if (this.observer) {
            this.observer.disconnect();
        }
        gsap.killTweensOf("*");
    }
}

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.gsapAnimations = new GSAPAnimations();
});

// Re-initialize after HTMX content swaps
document.body.addEventListener('htmx:afterSettle', () => {
    if (window.gsapAnimations) {
        window.gsapAnimations.refresh();
    }
});
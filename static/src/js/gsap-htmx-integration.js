/**
 * GSAP-HTMX Integration for Django Components
 * Enhanced animations specifically for HTMX interactions
 */

class GSAPHTMXIntegration {
    constructor() {
        this.init();
    }

    init() {
        // Enhanced HTMX animations
        this.setupHTMXEnhancedAnimations();
        this.setupComponentSpecificAnimations();
        this.setupLoadingAnimations();
    }

    /**
     * Enhanced HTMX animations with more sophisticated effects
     */
    setupHTMXEnhancedAnimations() {
        // Gallery filter animations
        document.body.addEventListener('htmx:beforeSwap', (e) => {
            if (e.target.closest('[data-component="gallery-grid"]')) {
                this.animateGallerySwap(e.target, 'out');
            }
        });

        document.body.addEventListener('htmx:afterSwap', (e) => {
            if (e.target.closest('[data-component="gallery-grid"]')) {
                this.animateGallerySwap(e.target, 'in');
            }
        });

        // Form submissions
        document.body.addEventListener('htmx:beforeSwap', (e) => {
            if (e.target.closest('.form-container')) {
                this.animateFormSwap(e.target, 'out');
            }
        });

        document.body.addEventListener('htmx:afterSwap', (e) => {
            if (e.target.closest('.form-container')) {
                this.animateFormSwap(e.target, 'in');
            }
        });
    }

    /**
     * Gallery-specific swap animations
     */
    animateGallerySwap(element, direction) {
        const gallery = element.closest('[data-component="gallery-grid"]');
        const cards = gallery.querySelectorAll('.artwork-card');

        if (direction === 'out') {
            gsap.to(cards, {
                scale: 0.9,
                opacity: 0,
                duration: 0.3,
                stagger: 0.05,
                ease: "power2.in"
            });
        } else {
            gsap.fromTo(cards,
                {
                    scale: 0.9,
                    opacity: 0,
                    y: 20
                },
                {
                    scale: 1,
                    opacity: 1,
                    y: 0,
                    duration: 0.6,
                    stagger: 0.1,
                    ease: "back.out(1.2)"
                }
            );
        }
    }

    /**
     * Form-specific swap animations
     */
    animateFormSwap(element, direction) {
        if (direction === 'out') {
            gsap.to(element, {
                x: -20,
                opacity: 0.7,
                duration: 0.25,
                ease: "power2.in"
            });
        } else {
            gsap.fromTo(element,
                {
                    x: 20,
                    opacity: 0
                },
                {
                    x: 0,
                    opacity: 1,
                    duration: 0.4,
                    ease: "power2.out"
                }
            );
        }
    }

    /**
     * Component-specific animations
     */
    setupComponentSpecificAnimations() {
        // Enhanced artwork card interactions
        this.setupArtworkCardAnimations();
        
        // Filter button animations
        this.setupFilterAnimations();
        
        // Form field animations
        this.setupFormFieldAnimations();
    }

    /**
     * Enhanced artwork card animations
     */
    setupArtworkCardAnimations() {
        document.addEventListener('mouseenter', (e) => {
            const card = e.target.closest('.artwork-card');
            if (card) {
                gsap.to(card, {
                    y: -12,
                    scale: 1.03,
                    rotationX: 2,
                    transformPerspective: 1000,
                    duration: 0.4,
                    ease: "power2.out"
                });

                const overlay = card.querySelector('.artwork-overlay');
                if (overlay) {
                    gsap.to(overlay, {
                        opacity: 1,
                        duration: 0.3,
                        ease: "power2.out"
                    });
                }
            }
        }, true);

        document.addEventListener('mouseleave', (e) => {
            const card = e.target.closest('.artwork-card');
            if (card) {
                gsap.to(card, {
                    y: 0,
                    scale: 1,
                    rotationX: 0,
                    duration: 0.4,
                    ease: "power2.out"
                });

                const overlay = card.querySelector('.artwork-overlay');
                if (overlay) {
                    gsap.to(overlay, {
                        opacity: 0,
                        duration: 0.3,
                        ease: "power2.out"
                    });
                }
            }
        }, true);
    }

    /**
     * Filter button animations
     */
    setupFilterAnimations() {
        const filterSelects = document.querySelectorAll('[data-component="gallery-filters"] select');
        filterSelects.forEach(select => {
            select.addEventListener('change', () => {
                gsap.to(select, {
                    scale: 1.05,
                    duration: 0.1,
                    yoyo: true,
                    repeat: 1,
                    ease: "power2.inOut"
                });
            });
        });

        const quickFilters = document.querySelectorAll('[data-component="gallery-filters"] button');
        quickFilters.forEach(button => {
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

    /**
     * Enhanced form field animations
     */
    setupFormFieldAnimations() {
        document.addEventListener('focus', (e) => {
            if (e.target.matches('.form-input, .form-textarea, .form-select')) {
                gsap.to(e.target, {
                    scale: 1.02,
                    boxShadow: "0 0 0 3px rgba(167, 139, 250, 0.1)",
                    duration: 0.3,
                    ease: "power2.out"
                });

                const label = e.target.previousElementSibling;
                if (label && label.tagName === 'LABEL') {
                    gsap.to(label, {
                        color: "#8B5CF6",
                        duration: 0.3,
                        ease: "power2.out"
                    });
                }
            }
        }, true);

        document.addEventListener('blur', (e) => {
            if (e.target.matches('.form-input, .form-textarea, .form-select')) {
                gsap.to(e.target, {
                    scale: 1,
                    boxShadow: "none",
                    duration: 0.3,
                    ease: "power2.out"
                });

                const label = e.target.previousElementSibling;
                if (label && label.tagName === 'LABEL') {
                    gsap.to(label, {
                        color: "#374151",
                        duration: 0.3,
                        ease: "power2.out"
                    });
                }
            }
        }, true);
    }

    /**
     * Enhanced loading animations
     */
    setupLoadingAnimations() {
        document.body.addEventListener('htmx:beforeRequest', (e) => {
            this.showEnhancedLoading(e.target);
        });

        document.body.addEventListener('htmx:afterRequest', (e) => {
            this.hideEnhancedLoading(e.target);
        });
    }

    showEnhancedLoading(element) {
        if (element.classList.contains('htmx-loading-animate')) {
            // Add loading overlay
            const overlay = document.createElement('div');
            overlay.className = 'htmx-loading-overlay';
            overlay.innerHTML = `
                <div class="htmx-loading-spinner">
                    <div class="spinner-dot"></div>
                    <div class="spinner-dot"></div>
                    <div class="spinner-dot"></div>
                </div>
            `;
            element.style.position = 'relative';
            element.appendChild(overlay);

            // Animate overlay
            gsap.fromTo(overlay,
                { opacity: 0 },
                { opacity: 1, duration: 0.3 }
            );

            // Animate spinner dots
            const dots = overlay.querySelectorAll('.spinner-dot');
            gsap.to(dots, {
                scale: 1.5,
                duration: 0.6,
                repeat: -1,
                yoyo: true,
                stagger: 0.2,
                ease: "power2.inOut"
            });
        }
    }

    hideEnhancedLoading(element) {
        const overlay = element.querySelector('.htmx-loading-overlay');
        if (overlay) {
            gsap.to(overlay, {
                opacity: 0,
                duration: 0.3,
                onComplete: () => overlay.remove()
            });
        }
    }

    /**
     * Page transition effects
     */
    pageEntranceAnimation() {
        const components = document.querySelectorAll('[data-component]');
        
        gsap.fromTo(components,
            {
                opacity: 0,
                y: 30
            },
            {
                opacity: 1,
                y: 0,
                duration: 0.8,
                stagger: 0.2,
                ease: "power3.out"
            }
        );
    }
}

// Initialize enhanced HTMX integration
document.addEventListener('DOMContentLoaded', () => {
    window.gsapHTMXIntegration = new GSAPHTMXIntegration();
    
    // Run entrance animation
    setTimeout(() => {
        window.gsapHTMXIntegration.pageEntranceAnimation();
    }, 100);
});

// Re-initialize after HTMX swaps
document.body.addEventListener('htmx:afterSettle', () => {
    if (window.gsapHTMXIntegration) {
        window.gsapHTMXIntegration.setupComponentSpecificAnimations();
    }
});
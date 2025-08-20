// Main JavaScript entry point for Aiza's Fine Art website
import '../css/input.css';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

// Register GSAP plugins
gsap.registerPlugin(ScrollTrigger);

// Main application class
class AizasFineArt {
  constructor() {
    this.init();
  }

  init() {
    this.setupGlobalAnimations();
    this.setupNavigation();
    this.setupScrollEffects();
    this.setupImageLazyLoading();
    this.setupFormEnhancements();
    this.setupMobileMenu();
  }

  // Global animations and transitions
  setupGlobalAnimations() {
    // Fade in animation for page load
    gsap.from('.animate-fade-in', {
      duration: 0.8,
      opacity: 0,
      y: 30,
      stagger: 0.1,
      ease: "power2.out"
    });

    // Hero text animation
    const heroTitle = document.querySelector('.hero-title');
    if (heroTitle) {
      gsap.from(heroTitle.children, {
        duration: 1,
        opacity: 0,
        y: 50,
        stagger: 0.2,
        ease: "power3.out",
        delay: 0.3
      });
    }

    // CTA button hover effects
    document.querySelectorAll('.btn-primary, .btn-secondary, .btn-accent').forEach(btn => {
      btn.addEventListener('mouseenter', () => {
        gsap.to(btn, { duration: 0.3, scale: 1.05, ease: "power2.out" });
      });
      
      btn.addEventListener('mouseleave', () => {
        gsap.to(btn, { duration: 0.3, scale: 1, ease: "power2.out" });
      });
    });
  }

  // Navigation functionality
  setupNavigation() {
    const navbar = document.querySelector('.navbar');
    let lastScrollY = window.scrollY;

    // Navbar hide/show on scroll
    window.addEventListener('scroll', () => {
      const currentScrollY = window.scrollY;
      
      if (navbar) {
        if (currentScrollY > lastScrollY && currentScrollY > 100) {
          // Scrolling down
          gsap.to(navbar, { duration: 0.3, y: -100, ease: "power2.out" });
        } else {
          // Scrolling up
          gsap.to(navbar, { duration: 0.3, y: 0, ease: "power2.out" });
        }
        
        // Add/remove background on scroll
        if (currentScrollY > 50) {
          navbar.classList.add('navbar-scrolled');
        } else {
          navbar.classList.remove('navbar-scrolled');
        }
      }
      
      lastScrollY = currentScrollY;
    });

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
      anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
          gsap.to(window, {
            duration: 1,
            scrollTo: { y: target, offsetY: 80 },
            ease: "power2.inOut"
          });
        }
      });
    });
  }

  // Scroll-triggered animations
  setupScrollEffects() {
    // Reveal animations for sections
    gsap.utils.toArray('.reveal-on-scroll').forEach(element => {
      gsap.from(element, {
        scrollTrigger: {
          trigger: element,
          start: "top 80%",
          end: "bottom 20%",
          toggleActions: "play none none reverse"
        },
        duration: 1,
        opacity: 0,
        y: 50,
        ease: "power2.out"
      });
    });

    // Parallax effect for hero background
    const heroBackground = document.querySelector('.hero-background');
    if (heroBackground) {
      gsap.to(heroBackground, {
        scrollTrigger: {
          trigger: heroBackground,
          start: "top top",
          end: "bottom top",
          scrub: true
        },
        y: -100,
        ease: "none"
      });
    }

    // Scale artwork images on scroll
    gsap.utils.toArray('.artwork-card').forEach(card => {
      const image = card.querySelector('.artwork-image');
      if (image) {
        gsap.from(image, {
          scrollTrigger: {
            trigger: card,
            start: "top 90%",
            end: "bottom 10%",
            toggleActions: "play none none reverse"
          },
          duration: 1.2,
          scale: 1.1,
          ease: "power2.out"
        });
      }
    });
  }

  // Lazy loading for images
  setupImageLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver((entries, observer) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const img = entry.target;
          img.src = img.dataset.src;
          img.classList.remove('opacity-0');
          img.classList.add('opacity-100');
          observer.unobserve(img);
        }
      });
    });

    images.forEach(img => {
      img.classList.add('opacity-0', 'transition-opacity', 'duration-500');
      imageObserver.observe(img);
    });
  }

  // Form enhancements
  setupFormEnhancements() {
    // Floating label effect
    document.querySelectorAll('.form-group').forEach(group => {
      const input = group.querySelector('input, textarea, select');
      const label = group.querySelector('label');
      
      if (input && label) {
        // Check if input has value on page load
        if (input.value) {
          label.classList.add('floating');
        }

        input.addEventListener('focus', () => {
          label.classList.add('floating');
        });

        input.addEventListener('blur', () => {
          if (!input.value) {
            label.classList.remove('floating');
          }
        });
      }
    });

    // Form validation feedback
    document.querySelectorAll('form').forEach(form => {
      form.addEventListener('submit', function(e) {
        const requiredFields = form.querySelectorAll('[required]');
        let isValid = true;

        requiredFields.forEach(field => {
          if (!field.value.trim()) {
            field.classList.add('border-red-500');
            isValid = false;
          } else {
            field.classList.remove('border-red-500');
          }
        });

        if (!isValid) {
          e.preventDefault();
          // Show error message
          this.showFormError('Please fill in all required fields');
        }
      });
    });
  }

  // Mobile menu functionality
  setupMobileMenu() {
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const mobileMenu = document.querySelector('.mobile-menu');
    const mobileMenuOverlay = document.querySelector('.mobile-menu-overlay');

    if (mobileMenuBtn && mobileMenu) {
      mobileMenuBtn.addEventListener('click', () => {
        const isOpen = mobileMenu.classList.contains('open');
        
        if (isOpen) {
          this.closeMobileMenu();
        } else {
          this.openMobileMenu();
        }
      });

      // Close menu when clicking overlay
      if (mobileMenuOverlay) {
        mobileMenuOverlay.addEventListener('click', () => {
          this.closeMobileMenu();
        });
      }

      // Close menu when clicking links
      mobileMenu.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', () => {
          this.closeMobileMenu();
        });
      });
    }
  }

  openMobileMenu() {
    const mobileMenu = document.querySelector('.mobile-menu');
    const mobileMenuOverlay = document.querySelector('.mobile-menu-overlay');
    
    mobileMenu.classList.add('open');
    document.body.classList.add('menu-open');
    
    gsap.to(mobileMenuOverlay, { duration: 0.3, opacity: 1, visibility: 'visible' });
    gsap.to(mobileMenu, { duration: 0.3, x: 0, ease: "power2.out" });
  }

  closeMobileMenu() {
    const mobileMenu = document.querySelector('.mobile-menu');
    const mobileMenuOverlay = document.querySelector('.mobile-menu-overlay');
    
    mobileMenu.classList.remove('open');
    document.body.classList.remove('menu-open');
    
    gsap.to(mobileMenuOverlay, { duration: 0.3, opacity: 0, visibility: 'hidden' });
    gsap.to(mobileMenu, { duration: 0.3, x: '100%', ease: "power2.out" });
  }

  // Utility methods
  showFormError(message) {
    // Create or update error message
    let errorDiv = document.querySelector('.form-error-message');
    if (!errorDiv) {
      errorDiv = document.createElement('div');
      errorDiv.className = 'form-error-message bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4';
      document.querySelector('form').prepend(errorDiv);
    }
    errorDiv.textContent = message;
    
    // Animate in
    gsap.from(errorDiv, { duration: 0.3, opacity: 0, y: -10 });
  }

  showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification fixed top-4 right-4 z-50 px-6 py-4 rounded-lg shadow-lg text-white max-w-sm ${
      type === 'success' ? 'bg-green-500' :
      type === 'error' ? 'bg-red-500' :
      type === 'warning' ? 'bg-yellow-500' :
      'bg-blue-500'
    }`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Animate in
    gsap.from(notification, { duration: 0.3, opacity: 0, x: 100 });
    
    // Auto remove after 5 seconds
    setTimeout(() => {
      gsap.to(notification, { 
        duration: 0.3, 
        opacity: 0, 
        x: 100,
        onComplete: () => notification.remove()
      });
    }, 5000);
  }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  new AizasFineArt();
});

// Export for use in other modules
window.AizasFineArt = AizasFineArt;
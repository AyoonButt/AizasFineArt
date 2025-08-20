/**
 * Global Wishlist Manager
 * Manages wishlist state across all pages and components
 */

class WishlistManager {
    constructor() {
        this.wishlistedItems = new Set();
        this.isInitialized = false;
        this.pendingRequests = new Map();
        
        this.init();
    }

    async init() {
        await this.loadWishlistState();
        this.setupEventListeners();
        this.updateAllButtons();
        this.isInitialized = true;
    }

    /**
     * Load current wishlist state from server
     */
    async loadWishlistState() {
        try {
            const response = await fetch('/api/wishlist/status/', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            if (response.ok) {
                const data = await response.json();
                this.wishlistedItems = new Set(data.wishlisted_artwork_ids || []);
            } else {
                // Fallback to localStorage for guests
                const stored = localStorage.getItem('wishlist_items');
                if (stored) {
                    this.wishlistedItems = new Set(JSON.parse(stored));
                }
            }
        } catch (error) {
            console.warn('Could not load wishlist state:', error);
            // Fallback to localStorage
            const stored = localStorage.getItem('wishlist_items');
            if (stored) {
                this.wishlistedItems = new Set(JSON.parse(stored));
            }
        }
    }

    /**
     * Set up global event listeners for wishlist buttons
     */
    setupEventListeners() {
        // Handle all wishlist button clicks globally
        document.addEventListener('click', async (e) => {
            const wishlistBtn = e.target.closest('.wishlist-btn, [data-wishlist-toggle]');
            if (wishlistBtn) {
                e.preventDefault();
                e.stopPropagation();
                
                const artworkId = wishlistBtn.dataset.artworkId || 
                                wishlistBtn.getAttribute('data-artwork-id');
                
                if (artworkId) {
                    await this.toggle(artworkId);
                }
            }
        });

        // Update buttons when page content changes (HTMX, infinite scroll, etc.)
        document.addEventListener('htmx:afterSwap', () => {
            this.updateAllButtons();
        });

        // Handle React component updates
        document.addEventListener('react:wishlist:update', () => {
            this.updateAllButtons();
        });
    }

    /**
     * Toggle wishlist status for an artwork
     */
    async toggle(artworkId) {
        const id = String(artworkId);
        
        // Prevent duplicate requests
        if (this.pendingRequests.has(id)) {
            return;
        }

        const wasWishlisted = this.wishlistedItems.has(id);
        const willBeWishlisted = !wasWishlisted;

        // Optimistic UI update
        this.updateButtonState(id, willBeWishlisted);
        if (willBeWishlisted) {
            this.wishlistedItems.add(id);
        } else {
            this.wishlistedItems.delete(id);
        }

        this.pendingRequests.set(id, true);

        try {
            const response = await fetch('/api/wishlist/toggle/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    artwork_id: id
                })
            });

            if (response.ok) {
                const data = await response.json();
                
                if (data.success) {
                    // Server confirmed the change
                    if (data.is_wishlisted) {
                        this.wishlistedItems.add(id);
                    } else {
                        this.wishlistedItems.delete(id);
                    }
                    
                    // Update localStorage for guests
                    if (!this.isUserAuthenticated()) {
                        localStorage.setItem('wishlist_items', JSON.stringify([...this.wishlistedItems]));
                    }
                    
                    // Update all buttons to match server state
                    this.updateButtonState(id, data.is_wishlisted);
                    
                    // Show feedback
                    this.showFeedback(data.is_wishlisted ? 'Added to wishlist' : 'Removed from wishlist');
                    
                    // Update wishlist count in header/nav
                    this.updateWishlistCount();
                    
                } else {
                    throw new Error(data.message || 'Toggle failed');
                }
            } else {
                throw new Error(`HTTP ${response.status}`);
            }
        } catch (error) {
            console.error('Wishlist toggle error:', error);
            
            // Revert optimistic update
            if (wasWishlisted) {
                this.wishlistedItems.add(id);
            } else {
                this.wishlistedItems.delete(id);
            }
            this.updateButtonState(id, wasWishlisted);
            
            this.showFeedback('Error updating wishlist', 'error');
        } finally {
            this.pendingRequests.delete(id);
        }
    }

    /**
     * Update all wishlist buttons on the page
     */
    updateAllButtons() {
        const buttons = document.querySelectorAll('.wishlist-btn, [data-wishlist-toggle]');
        buttons.forEach(button => {
            const artworkId = button.dataset.artworkId || 
                             button.getAttribute('data-artwork-id');
            if (artworkId) {
                const isWishlisted = this.wishlistedItems.has(String(artworkId));
                this.updateButtonState(artworkId, isWishlisted, button);
            }
        });
    }

    /**
     * Update specific button state
     */
    updateButtonState(artworkId, isWishlisted, specificButton = null) {
        const selector = specificButton ? [specificButton] : 
                        document.querySelectorAll(`[data-artwork-id="${artworkId}"]`);
        
        (selector.length ? selector : [specificButton]).forEach(button => {
            if (!button) return;
            
            // Update classes
            if (isWishlisted) {
                button.classList.add('active', 'wishlisted');
            } else {
                button.classList.remove('active', 'wishlisted');
            }
            
            // Update SVG fill
            const svg = button.querySelector('svg');
            if (svg) {
                svg.setAttribute('fill', isWishlisted ? 'currentColor' : 'none');
            }
            
            // Update title
            const newTitle = isWishlisted ? 'Remove from Wishlist' : 'Add to Wishlist';
            button.setAttribute('title', newTitle);
            
            // Update aria-label for accessibility
            button.setAttribute('aria-label', newTitle);
            button.setAttribute('aria-pressed', isWishlisted.toString());
        });
    }

    /**
     * Check if artwork is wishlisted
     */
    isWishlisted(artworkId) {
        return this.wishlistedItems.has(String(artworkId));
    }

    /**
     * Get all wishlisted artwork IDs
     */
    getWishlistedItems() {
        return [...this.wishlistedItems];
    }

    /**
     * Update wishlist count in navigation
     */
    updateWishlistCount() {
        const countElements = document.querySelectorAll('.wishlist-count');
        const count = this.wishlistedItems.size;
        
        countElements.forEach(el => {
            el.textContent = count;
            el.style.display = count > 0 ? 'inline' : 'none';
        });
    }

    /**
     * Show user feedback
     */
    showFeedback(message, type = 'success') {
        // Try to use existing toast system
        if (window.showToast) {
            window.showToast(message, type);
            return;
        }
        
        // Fallback: simple notification
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 z-50 px-4 py-2 rounded-lg text-white transition-all duration-300 ${
            type === 'error' ? 'bg-red-500' : 'bg-green-500'
        }`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => notification.classList.add('opacity-100'), 10);
        
        // Remove after 3 seconds
        setTimeout(() => {
            notification.classList.add('opacity-0', 'translate-x-full');
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    /**
     * Get CSRF token
     */
    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
               document.querySelector('meta[name="csrf-token"]')?.content || '';
    }

    /**
     * Check if user is authenticated
     */
    isUserAuthenticated() {
        return document.body.classList.contains('user-authenticated') ||
               document.querySelector('meta[name="user-authenticated"]')?.content === 'true';
    }

    /**
     * Force refresh wishlist state from server
     */
    async refresh() {
        await this.loadWishlistState();
        this.updateAllButtons();
        this.updateWishlistCount();
    }
}

// Initialize global wishlist manager
let wishlistManager;

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        wishlistManager = new WishlistManager();
        window.wishlistManager = wishlistManager;
    });
} else {
    wishlistManager = new WishlistManager();
    window.wishlistManager = wishlistManager;
}

// Export for modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = WishlistManager;
}
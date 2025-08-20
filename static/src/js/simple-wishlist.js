// Simple Wishlist Manager
console.log('Wishlist script loaded');

class SimpleWishlist {
    constructor() {
        this.wishlistedItems = new Set();
        console.log('SimpleWishlist constructor called');
        this.init();
    }

    init() {
        this.loadFromStorage();
        this.setupClickHandlers();
        this.updateAllButtons();
    }

    loadFromStorage() {
        const stored = localStorage.getItem('wishlist_items');
        if (stored) {
            this.wishlistedItems = new Set(JSON.parse(stored));
        }
    }

    saveToStorage() {
        localStorage.setItem('wishlist_items', JSON.stringify([...this.wishlistedItems]));
    }

    setupClickHandlers() {
        document.addEventListener('click', (e) => {
            const wishlistBtn = e.target.closest('.wishlist-btn, [data-wishlist-toggle]');
            if (wishlistBtn) {
                e.preventDefault();
                console.log('Wishlist button clicked:', wishlistBtn);
                const artworkId = wishlistBtn.dataset.artworkId || wishlistBtn.getAttribute('data-artwork-id');
                console.log('Artwork ID found:', artworkId);
                if (artworkId) {
                    this.toggle(artworkId);
                }
            }
        });
    }

    toggle(artworkId) {
        const id = String(artworkId);
        console.log('Toggling wishlist for artwork:', id);
        
        if (this.wishlistedItems.has(id)) {
            this.wishlistedItems.delete(id);
            console.log('Removed from wishlist:', id);
        } else {
            this.wishlistedItems.add(id);
            console.log('Added to wishlist:', id);
        }
        
        this.saveToStorage();
        this.updateButtonsForArtwork(id);
    }

    updateButtonsForArtwork(artworkId) {
        const buttons = document.querySelectorAll(`[data-artwork-id="${artworkId}"]`);
        const isWishlisted = this.wishlistedItems.has(String(artworkId));
        
        console.log(`Updating ${buttons.length} buttons for artwork ${artworkId}, wishlisted: ${isWishlisted}`);
        
        buttons.forEach(button => {
            if (isWishlisted) {
                button.classList.add('active');
                button.style.color = '#ef4444'; // red-500
                button.setAttribute('title', 'Remove from Wishlist');
            } else {
                button.classList.remove('active');
                button.style.color = ''; // reset to default
                button.setAttribute('title', 'Add to Wishlist');
            }
            
            // Update SVG fill
            const svg = button.querySelector('svg');
            if (svg) {
                svg.setAttribute('fill', isWishlisted ? 'currentColor' : 'none');
                console.log(`Updated SVG fill to: ${isWishlisted ? 'currentColor' : 'none'}`);
            }
        });
    }

    updateAllButtons() {
        document.querySelectorAll('.wishlist-btn, [data-wishlist-toggle]').forEach(button => {
            const artworkId = button.dataset.artworkId || button.getAttribute('data-artwork-id');
            if (artworkId) {
                this.updateButtonsForArtwork(artworkId);
            }
        });
    }

    isWishlisted(artworkId) {
        return this.wishlistedItems.has(String(artworkId));
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.simpleWishlist = new SimpleWishlist();
});
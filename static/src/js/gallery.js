// Gallery functionality for artwork display
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

class ArtworkGallery {
  constructor() {
    this.currentFilter = 'all';
    this.currentSort = 'newest';
    this.artworks = [];
    this.filteredArtworks = [];
    this.lightboxOpen = false;
    
    this.init();
  }

  init() {
    this.setupMasonryLayout();
    this.setupFiltering();
    this.setupSorting();
    this.setupLightbox();
    this.setupInfiniteScroll();
    this.setupSearch();
    this.loadArtworks();
  }

  // Masonry layout implementation
  setupMasonryLayout() {
    const grid = document.querySelector('.masonry-grid');
    if (!grid) return;

    this.resizeGridItems();
    
    // Recalculate on window resize
    window.addEventListener('resize', () => {
      this.resizeGridItems();
    });

    // Recalculate when images load
    grid.addEventListener('load', (e) => {
      if (e.target.tagName === 'IMG') {
        this.resizeGridItems();
      }
    }, true);
  }

  resizeGridItems() {
    const grid = document.querySelector('.masonry-grid');
    if (!grid) return;

    const items = grid.querySelectorAll('.masonry-item');
    const rowHeight = 10; // Base grid row height
    const rowGap = 24; // Gap between rows

    items.forEach(item => {
      const content = item.querySelector('.masonry-content');
      if (content) {
        const contentHeight = content.getBoundingClientRect().height;
        const rowSpan = Math.ceil((contentHeight + rowGap) / (rowHeight + rowGap));
        item.style.setProperty('--grid-rows', rowSpan);
      }
    });
  }

  // Filtering functionality
  setupFiltering() {
    const filterButtons = document.querySelectorAll('.filter-btn');
    
    filterButtons.forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        const filter = btn.dataset.filter;
        this.applyFilter(filter);
        
        // Update active state
        filterButtons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
      });
    });
  }

  applyFilter(filter) {
    this.currentFilter = filter;
    const items = document.querySelectorAll('.artwork-item');
    
    items.forEach(item => {
      const categories = item.dataset.categories ? item.dataset.categories.split(',') : [];
      const medium = item.dataset.medium || '';
      
      let shouldShow = filter === 'all';
      
      if (!shouldShow) {
        shouldShow = categories.includes(filter) || medium === filter;
      }
      
      if (shouldShow) {
        gsap.to(item, {
          duration: 0.5,
          opacity: 1,
          scale: 1,
          display: 'block',
          ease: "power2.out"
        });
      } else {
        gsap.to(item, {
          duration: 0.3,
          opacity: 0,
          scale: 0.8,
          ease: "power2.out",
          onComplete: () => {
            item.style.display = 'none';
          }
        });
      }
    });

    // Recalculate masonry after filtering
    setTimeout(() => {
      this.resizeGridItems();
    }, 500);
  }

  // Sorting functionality
  setupSorting() {
    const sortSelect = document.querySelector('.sort-select');
    if (!sortSelect) return;

    sortSelect.addEventListener('change', (e) => {
      this.applySorting(e.target.value);
    });
  }

  applySorting(sortBy) {
    this.currentSort = sortBy;
    const grid = document.querySelector('.masonry-grid');
    if (!grid) return;

    const items = Array.from(grid.querySelectorAll('.artwork-item'));
    
    items.sort((a, b) => {
      switch (sortBy) {
        case 'newest':
          return new Date(b.dataset.created) - new Date(a.dataset.created);
        case 'oldest':
          return new Date(a.dataset.created) - new Date(b.dataset.created);
        case 'price-low':
          return parseFloat(a.dataset.price || 0) - parseFloat(b.dataset.price || 0);
        case 'price-high':
          return parseFloat(b.dataset.price || 0) - parseFloat(a.dataset.price || 0);
        case 'title':
          return a.dataset.title.localeCompare(b.dataset.title);
        default:
          return 0;
      }
    });

    // Animate out and reorder
    gsap.to(items, {
      duration: 0.3,
      opacity: 0,
      y: 20,
      stagger: 0.02,
      onComplete: () => {
        // Reorder DOM elements
        items.forEach(item => grid.appendChild(item));
        
        // Animate back in
        gsap.to(items, {
          duration: 0.5,
          opacity: 1,
          y: 0,
          stagger: 0.03,
          ease: "power2.out",
          onComplete: () => {
            this.resizeGridItems();
          }
        });
      }
    });
  }

  // Lightbox functionality
  setupLightbox() {
    const artworkLinks = document.querySelectorAll('.artwork-link');
    
    artworkLinks.forEach(link => {
      link.addEventListener('click', (e) => {
        if (link.dataset.lightbox === 'true') {
          e.preventDefault();
          this.openLightbox(link);
        }
      });
    });

    // Close lightbox on escape key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && this.lightboxOpen) {
        this.closeLightbox();
      }
    });
  }

  openLightbox(trigger) {
    const imageUrl = trigger.dataset.image || trigger.querySelector('img')?.src;
    const title = trigger.dataset.title || '';
    const description = trigger.dataset.description || '';
    const price = trigger.dataset.price || '';
    
    if (!imageUrl) return;

    // Create lightbox element
    const lightbox = document.createElement('div');
    lightbox.className = 'lightbox fixed inset-0 z-50 flex items-center justify-center p-4';
    lightbox.innerHTML = `
      <div class="lightbox-overlay absolute inset-0 bg-black/80 backdrop-blur-sm"></div>
      <div class="lightbox-content relative max-w-6xl max-h-full bg-white rounded-lg overflow-hidden shadow-2xl">
        <button class="lightbox-close absolute top-4 right-4 z-10 w-8 h-8 bg-white/20 backdrop-blur-sm rounded-full flex items-center justify-center text-white hover:bg-white/30 transition-colors">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
        <div class="lightbox-image-container">
          <img src="${imageUrl}" alt="${title}" class="w-full h-auto max-h-[80vh] object-contain">
        </div>
        ${title || description || price ? `
          <div class="lightbox-info p-6 bg-white">
            ${title ? `<h3 class="text-2xl font-playfair font-semibold mb-2">${title}</h3>` : ''}
            ${description ? `<p class="text-neutral-600 mb-4">${description}</p>` : ''}
            ${price ? `<div class="price-display">${price}</div>` : ''}
          </div>
        ` : ''}
      </div>
    `;

    document.body.appendChild(lightbox);
    document.body.classList.add('overflow-hidden');
    this.lightboxOpen = true;

    // Animate in
    gsap.from(lightbox.querySelector('.lightbox-overlay'), {
      duration: 0.3,
      opacity: 0
    });
    
    gsap.from(lightbox.querySelector('.lightbox-content'), {
      duration: 0.4,
      opacity: 0,
      scale: 0.9,
      ease: "power2.out"
    });

    // Close handlers
    lightbox.querySelector('.lightbox-close').addEventListener('click', () => {
      this.closeLightbox();
    });
    
    lightbox.querySelector('.lightbox-overlay').addEventListener('click', () => {
      this.closeLightbox();
    });
  }

  closeLightbox() {
    const lightbox = document.querySelector('.lightbox');
    if (!lightbox) return;

    gsap.to(lightbox, {
      duration: 0.3,
      opacity: 0,
      onComplete: () => {
        lightbox.remove();
        document.body.classList.remove('overflow-hidden');
        this.lightboxOpen = false;
      }
    });
  }

  // Search functionality
  setupSearch() {
    const searchInput = document.querySelector('.artwork-search');
    if (!searchInput) return;

    let searchTimeout;
    
    searchInput.addEventListener('input', (e) => {
      clearTimeout(searchTimeout);
      searchTimeout = setTimeout(() => {
        this.performSearch(e.target.value);
      }, 300);
    });
  }

  performSearch(query) {
    const items = document.querySelectorAll('.artwork-item');
    const normalizedQuery = query.toLowerCase().trim();
    
    if (!normalizedQuery) {
      // Show all items if search is empty
      items.forEach(item => {
        item.style.display = 'block';
        gsap.to(item, { duration: 0.3, opacity: 1 });
      });
      return;
    }

    items.forEach(item => {
      const title = (item.dataset.title || '').toLowerCase();
      const description = (item.dataset.description || '').toLowerCase();
      const medium = (item.dataset.medium || '').toLowerCase();
      const categories = (item.dataset.categories || '').toLowerCase();
      
      const matches = title.includes(normalizedQuery) ||
                     description.includes(normalizedQuery) ||
                     medium.includes(normalizedQuery) ||
                     categories.includes(normalizedQuery);
      
      if (matches) {
        item.style.display = 'block';
        gsap.to(item, { duration: 0.3, opacity: 1 });
      } else {
        gsap.to(item, {
          duration: 0.3,
          opacity: 0,
          onComplete: () => {
            item.style.display = 'none';
          }
        });
      }
    });

    // Recalculate masonry after search
    setTimeout(() => {
      this.resizeGridItems();
    }, 300);
  }

  // Infinite scroll (for large galleries)
  setupInfiniteScroll() {
    const loadMore = document.querySelector('.load-more');
    if (!loadMore) return;

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          this.loadMoreArtworks();
        }
      });
    }, { threshold: 0.1 });

    observer.observe(loadMore);
  }

  async loadMoreArtworks() {
    const loadMore = document.querySelector('.load-more');
    if (!loadMore || loadMore.dataset.loading === 'true') return;

    loadMore.dataset.loading = 'true';
    loadMore.innerHTML = '<div class="loading-dots"><span style="--delay: 0"></span><span style="--delay: 1"></span><span style="--delay: 2"></span></div>';

    try {
      // Simulate API call (replace with actual endpoint)
      const response = await fetch(`/api/artworks/?page=${this.getNextPage()}&filter=${this.currentFilter}&sort=${this.currentSort}`);
      const data = await response.json();
      
      if (data.artworks && data.artworks.length > 0) {
        this.appendArtworks(data.artworks);
        
        if (!data.has_next) {
          loadMore.style.display = 'none';
        }
      } else {
        loadMore.style.display = 'none';
      }
    } catch (error) {
      console.error('Error loading more artworks:', error);
      loadMore.innerHTML = 'Error loading more artworks';
    } finally {
      loadMore.dataset.loading = 'false';
    }
  }

  appendArtworks(artworks) {
    const grid = document.querySelector('.masonry-grid');
    if (!grid) return;

    const fragment = document.createDocumentFragment();
    
    artworks.forEach((artwork, index) => {
      const item = this.createArtworkElement(artwork);
      fragment.appendChild(item);
      
      // Animate in with stagger
      gsap.from(item, {
        duration: 0.6,
        opacity: 0,
        y: 50,
        delay: index * 0.1,
        ease: "power2.out"
      });
    });

    grid.appendChild(fragment);
    
    // Recalculate masonry layout
    setTimeout(() => {
      this.resizeGridItems();
    }, 100);
  }

  createArtworkElement(artwork) {
    const item = document.createElement('div');
    item.className = 'masonry-item artwork-item';
    item.dataset.categories = artwork.categories?.join(',') || '';
    item.dataset.medium = artwork.medium || '';
    item.dataset.title = artwork.title || '';
    item.dataset.price = artwork.price || '';
    item.dataset.created = artwork.created_at || '';
    
    item.innerHTML = `
      <div class="masonry-content card artwork-card">
        <a href="${artwork.url}" class="artwork-link block" data-lightbox="true" data-image="${artwork.primary_image}" data-title="${artwork.title}" data-description="${artwork.description}" data-price="${artwork.price_display}">
          <div class="artwork-image-container relative overflow-hidden">
            <img src="${artwork.primary_image}" alt="${artwork.alt_text}" class="artwork-image w-full h-auto">
            <div class="artwork-overlay">
              <div class="absolute bottom-4 left-4 text-white">
                <h3 class="font-playfair font-semibold text-lg mb-1">${artwork.title}</h3>
                <p class="text-sm opacity-90">${artwork.medium} • ${artwork.dimensions_display}</p>
              </div>
              ${artwork.price ? `<div class="absolute top-4 right-4 bg-white/20 backdrop-blur-sm rounded-full px-3 py-1 text-white text-sm font-medium">${artwork.price_display}</div>` : ''}
            </div>
          </div>
        </a>
      </div>
    `;
    
    return item;
  }

  getNextPage() {
    // Implementation depends on your pagination system
    return parseInt(document.querySelector('.masonry-grid').dataset.currentPage || '1') + 1;
  }

  // Load initial artworks (if needed)
  async loadArtworks() {
    // This would typically load from an API
    // For now, just setup existing elements
    this.resizeGridItems();
  }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  if (document.querySelector('.masonry-grid')) {
    new ArtworkGallery();
  }
});

export default ArtworkGallery;
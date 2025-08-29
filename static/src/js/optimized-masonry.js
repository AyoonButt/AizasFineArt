/**
 * Optimized Masonry Layout System
 * Addresses performance issues in shop.html and gallery.html
 */

class OptimizedMasonry {
    constructor(container, options = {}) {
        this.container = typeof container === 'string' ? document.querySelector(container) : container;
        if (!this.container) return;
        
        this.options = {
            itemSelector: '.artwork-item',
            columnGap: 24,
            ...options
        };
        
        this.items = [];
        this.columns = [];
        this.resizeTimeout = null;
        this.isLayoutInProgress = false;
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.layout();
    }
    
    bindEvents() {
        // Debounced resize handler
        window.addEventListener('resize', this.debounce(() => {
            if (!this.isLayoutInProgress) {
                this.layout();
            }
        }, 250));
    }
    
    debounce(func, wait) {
        return (...args) => {
            clearTimeout(this.resizeTimeout);
            this.resizeTimeout = setTimeout(() => func.apply(this, args), wait);
        };
    }
    
    layout() {
        if (this.isLayoutInProgress) return;
        this.isLayoutInProgress = true;
        
        // Use requestAnimationFrame for smooth updates
        requestAnimationFrame(() => {
            this.calculateLayout();
            this.isLayoutInProgress = false;
        });
    }
    
    calculateLayout() {
        this.items = Array.from(this.container.querySelectorAll(`${this.options.itemSelector}:not(.filter-hidden)`));
        
        if (this.items.length === 0) return;
        
        // Calculate responsive columns
        const containerWidth = this.container.offsetWidth;
        const isSmallView = this.container.classList.contains('gallery-grid-small');
        
        let columnCount = this.getColumnCount(isSmallView);
        const itemWidth = (containerWidth - (this.options.columnGap * (columnCount - 1))) / columnCount;
        
        // Initialize column heights
        this.columns = new Array(columnCount).fill(0);
        
        // Use document fragment for batch DOM updates
        const fragment = document.createDocumentFragment();
        
        // Position items with virtual DOM approach
        this.items.forEach((item, index) => {
            this.positionItem(item, itemWidth, index);
        });
        
        // Set final container height
        const maxHeight = Math.max(...this.columns);
        this.container.style.height = `${maxHeight + this.options.columnGap}px`;
    }
    
    positionItem(item, itemWidth, index) {
        // Get or estimate item height
        const img = item.querySelector('.artwork-image');
        let itemHeight = itemWidth * 1.4; // Default aspect ratio
        
        if (img && img.naturalWidth && img.naturalHeight) {
            const aspectRatio = img.naturalWidth / img.naturalHeight;
            itemHeight = itemWidth / aspectRatio;
        }
        
        // Find shortest column
        const shortestColumnIndex = this.columns.indexOf(Math.min(...this.columns));
        const x = shortestColumnIndex * (itemWidth + this.options.columnGap);
        const y = this.columns[shortestColumnIndex];
        
        // Apply positioning with transform for better performance
        item.style.position = 'absolute';
        item.style.transform = `translate3d(${x}px, ${y}px, 0)`;
        item.style.width = `${itemWidth}px`;
        
        // Update image container
        const imageContainer = item.querySelector('.artwork-image-container');
        if (imageContainer) {
            imageContainer.style.height = `${itemHeight}px`;
        }
        
        // Update column height
        const cardHeight = item.offsetHeight || itemHeight + 120; // Estimated content height
        this.columns[shortestColumnIndex] = y + cardHeight + this.options.columnGap;
    }
    
    getColumnCount(isSmallView) {
        const width = window.innerWidth;
        
        if (isSmallView) {
            if (width >= 1280) return 6;
            if (width >= 1024) return 5;
            if (width >= 768) return 4;
            if (width >= 640) return 3;
            return 2;
        } else {
            if (width >= 1280) return 4;
            if (width >= 1024) return 3;
            if (width >= 640) return 2;
            return 1;
        }
    }
    
    refresh() {
        this.layout();
    }
    
    destroy() {
        window.removeEventListener('resize', this.layout);
        clearTimeout(this.resizeTimeout);
    }
}

// Export for use in templates
window.OptimizedMasonry = OptimizedMasonry;
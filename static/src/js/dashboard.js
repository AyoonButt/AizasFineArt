// User dashboard functionality
import { gsap } from 'gsap';
import axios from 'axios';

class UserDashboard {
  constructor() {
    this.currentTab = 'overview';
    this.wishlistItems = [];
    this.orders = [];
    this.notifications = [];
    
    this.init();
  }

  init() {
    this.setupTabNavigation();
    this.setupWishlistManagement();
    this.setupOrderTracking();
    this.setupNotifications();
    this.setupProfileManagement();
    this.loadDashboardData();
  }

  // Tab navigation
  setupTabNavigation() {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabPanels = document.querySelectorAll('.tab-panel');

    tabButtons.forEach(button => {
      button.addEventListener('click', (e) => {
        e.preventDefault();
        const tabName = button.dataset.tab;
        this.switchTab(tabName);
      });
    });
  }

  switchTab(tabName) {
    const currentPanel = document.querySelector(`.tab-panel[data-tab="${this.currentTab}"]`);
    const nextPanel = document.querySelector(`.tab-panel[data-tab="${tabName}"]`);
    const currentButton = document.querySelector(`.tab-button[data-tab="${this.currentTab}"]`);
    const nextButton = document.querySelector(`.tab-button[data-tab="${tabName}"]`);

    if (!currentPanel || !nextPanel) return;

    // Update button states
    currentButton?.classList.remove('active');
    nextButton?.classList.add('active');

    // Animate panel transition
    gsap.to(currentPanel, {
      duration: 0.3,
      opacity: 0,
      x: -20,
      onComplete: () => {
        currentPanel.classList.add('hidden');
        nextPanel.classList.remove('hidden');
        
        gsap.from(nextPanel, {
          duration: 0.4,
          opacity: 0,
          x: 20,
          ease: "power2.out"
        });
      }
    });

    this.currentTab = tabName;
    
    // Load tab-specific data
    this.loadTabData(tabName);
  }

  async loadTabData(tabName) {
    try {
      switch (tabName) {
        case 'wishlist':
          await this.loadWishlist();
          break;
        case 'orders':
          await this.loadOrders();
          break;
        case 'profile':
          await this.loadProfile();
          break;
      }
    } catch (error) {
      console.error(`Error loading ${tabName} data:`, error);
    }
  }

  // Wishlist management
  setupWishlistManagement() {
    document.addEventListener('click', (e) => {
      if (e.target.matches('.wishlist-toggle')) {
        e.preventDefault();
        const artworkId = e.target.dataset.artworkId;
        this.toggleWishlistItem(artworkId);
      }
      
      if (e.target.matches('.remove-from-wishlist')) {
        e.preventDefault();
        const artworkId = e.target.dataset.artworkId;
        this.removeFromWishlist(artworkId);
      }
    });
  }

  async toggleWishlistItem(artworkId) {
    try {
      const response = await axios.post('/api/wishlist/toggle/', {
        artwork_id: artworkId
      }, {
        headers: {
          'X-CSRFToken': this.getCSRFToken()
        }
      });

      if (response.data.success) {
        this.updateWishlistButton(artworkId, response.data.is_wishlisted);
        
        if (response.data.is_wishlisted) {
          this.showNotification('Added to wishlist', 'success');
        } else {
          this.showNotification('Removed from wishlist', 'info');
        }
      }
    } catch (error) {
      console.error('Error toggling wishlist:', error);
      this.showNotification('Error updating wishlist', 'error');
    }
  }

  updateWishlistButton(artworkId, isWishlisted) {
    const buttons = document.querySelectorAll(`[data-artwork-id="${artworkId}"]`);
    
    buttons.forEach(button => {
      const icon = button.querySelector('.wishlist-icon');
      if (isWishlisted) {
        button.classList.add('wishlisted');
        if (icon) icon.innerHTML = '❤️';
      } else {
        button.classList.remove('wishlisted');
        if (icon) icon.innerHTML = '🤍';
      }
    });
  }

  async removeFromWishlist(artworkId) {
    try {
      const response = await axios.delete(`/api/wishlist/${artworkId}/`, {
        headers: {
          'X-CSRFToken': this.getCSRFToken()
        }
      });

      if (response.data.success) {
        const item = document.querySelector(`[data-wishlist-item="${artworkId}"]`);
        if (item) {
          gsap.to(item, {
            duration: 0.3,
            opacity: 0,
            x: -50,
            onComplete: () => item.remove()
          });
        }
        this.showNotification('Removed from wishlist', 'success');
      }
    } catch (error) {
      console.error('Error removing from wishlist:', error);
      this.showNotification('Error removing from wishlist', 'error');
    }
  }

  async loadWishlist() {
    try {
      const response = await axios.get('/api/wishlist/');
      this.wishlistItems = response.data.items;
      this.renderWishlist();
    } catch (error) {
      console.error('Error loading wishlist:', error);
    }
  }

  renderWishlist() {
    const container = document.querySelector('.wishlist-container');
    if (!container) return;

    if (this.wishlistItems.length === 0) {
      container.innerHTML = `
        <div class="empty-state text-center py-12">
          <div class="text-6xl mb-4">🤍</div>
          <h3 class="text-xl font-playfair font-semibold mb-2">Your wishlist is empty</h3>
          <p class="text-neutral-600 mb-6">Save artworks you love for later</p>
          <a href="/art/" class="btn-primary">Browse Artwork</a>
        </div>
      `;
      return;
    }

    const html = this.wishlistItems.map(item => `
      <div class="wishlist-item card p-4" data-wishlist-item="${item.artwork.id}">
        <div class="flex gap-4">
          <div class="w-24 h-24 rounded-lg overflow-hidden flex-shrink-0">
            <img src="${item.artwork.primary_image}" alt="${item.artwork.alt_text}" class="w-full h-full object-cover">
          </div>
          <div class="flex-1">
            <h4 class="font-playfair font-semibold text-lg mb-1">
              <a href="${item.artwork.url}" class="hover:text-primary-600">${item.artwork.title}</a>
            </h4>
            <p class="text-neutral-600 text-sm mb-2">${item.artwork.medium} • ${item.artwork.dimensions_display}</p>
            <p class="price-display text-lg mb-3">${item.artwork.price_display}</p>
            ${item.notes ? `<p class="text-sm text-neutral-500 italic">${item.notes}</p>` : ''}
          </div>
          <div class="flex flex-col gap-2">
            <button class="btn-primary btn-sm" onclick="window.location.href='${item.artwork.url}'">View</button>
            <button class="remove-from-wishlist text-red-500 hover:text-red-700 text-sm" data-artwork-id="${item.artwork.id}">Remove</button>
          </div>
        </div>
      </div>
    `).join('');

    container.innerHTML = html;
    
    // Animate in
    gsap.from('.wishlist-item', {
      duration: 0.5,
      opacity: 0,
      y: 20,
      stagger: 0.1,
      ease: "power2.out"
    });
  }

  // Order tracking
  setupOrderTracking() {
    document.addEventListener('click', (e) => {
      if (e.target.matches('.track-order')) {
        e.preventDefault();
        const orderNumber = e.target.dataset.orderNumber;
        this.showOrderDetails(orderNumber);
      }
    });
  }

  async loadOrders() {
    try {
      const response = await axios.get('/api/orders/');
      this.orders = response.data.orders;
      this.renderOrders();
    } catch (error) {
      console.error('Error loading orders:', error);
    }
  }

  renderOrders() {
    const container = document.querySelector('.orders-container');
    if (!container) return;

    if (this.orders.length === 0) {
      container.innerHTML = `
        <div class="empty-state text-center py-12">
          <div class="text-6xl mb-4">📦</div>
          <h3 class="text-xl font-playfair font-semibold mb-2">No orders yet</h3>
          <p class="text-neutral-600 mb-6">Your order history will appear here</p>
          <a href="/art/" class="btn-primary">Start Shopping</a>
        </div>
      `;
      return;
    }

    const html = this.orders.map(order => `
      <div class="order-item card p-6 mb-4">
        <div class="flex justify-between items-start mb-4">
          <div>
            <h4 class="font-playfair font-semibold text-lg">Order ${order.order_number}</h4>
            <p class="text-neutral-600 text-sm">Placed on ${new Date(order.created_at).toLocaleDateString()}</p>
          </div>
          <div class="text-right">
            <div class="status-badge status-${order.status.replace('_', '-')}">${order.status_display}</div>
            <p class="text-lg font-semibold mt-1">${order.total_amount}</p>
          </div>
        </div>
        
        <div class="order-items mb-4">
          ${order.items.map(item => `
            <div class="flex items-center gap-3 py-2 border-b border-neutral-100 last:border-b-0">
              <div class="w-12 h-12 rounded overflow-hidden">
                <img src="${item.artwork?.primary_image || '/static/images/placeholder.jpg'}" alt="${item.title}" class="w-full h-full object-cover">
              </div>
              <div class="flex-1">
                <h5 class="font-medium">${item.title}</h5>
                <p class="text-sm text-neutral-600">${item.description}</p>
              </div>
              <div class="text-right">
                <p class="font-medium">${item.total_price}</p>
                ${item.quantity > 1 ? `<p class="text-sm text-neutral-600">Qty: ${item.quantity}</p>` : ''}
              </div>
            </div>
          `).join('')}
        </div>
        
        <div class="flex justify-between items-center">
          <div class="text-sm text-neutral-600">
            ${order.tracking_number ? `Tracking: ${order.tracking_number}` : ''}
          </div>
          <div class="flex gap-2">
            <button class="track-order btn-outline btn-sm" data-order-number="${order.order_number}">View Details</button>
            ${order.status === 'delivered' && order.can_be_refunded ? `<button class="request-refund btn-ghost btn-sm text-red-600" data-order-number="${order.order_number}">Request Refund</button>` : ''}
          </div>
        </div>
      </div>
    `).join('');

    container.innerHTML = html;
  }

  showOrderDetails(orderNumber) {
    const order = this.orders.find(o => o.order_number === orderNumber);
    if (!order) return;

    // Create modal with order details
    const modal = document.createElement('div');
    modal.className = 'modal-overlay fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50';
    modal.innerHTML = `
      <div class="modal-content bg-white rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div class="modal-header flex justify-between items-center p-6 border-b">
          <h3 class="text-xl font-playfair font-semibold">Order ${order.order_number}</h3>
          <button class="close-modal text-neutral-400 hover:text-neutral-600">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
        
        <div class="modal-body p-6">
          <div class="order-timeline mb-6">
            <h4 class="font-semibold mb-3">Order Status</h4>
            ${this.renderOrderTimeline(order)}
          </div>
          
          <div class="order-details grid md:grid-cols-2 gap-6">
            <div>
              <h4 class="font-semibold mb-3">Shipping Address</h4>
              <div class="bg-neutral-50 p-4 rounded-lg">
                <p>${order.shipping_name || order.billing_name}</p>
                <p>${order.shipping_address_1 || order.billing_address_1}</p>
                ${order.shipping_address_2 || order.billing_address_2 ? `<p>${order.shipping_address_2 || order.billing_address_2}</p>` : ''}
                <p>${order.shipping_city || order.billing_city}, ${order.shipping_state || order.billing_state} ${order.shipping_postal_code || order.billing_postal_code}</p>
              </div>
            </div>
            
            <div>
              <h4 class="font-semibold mb-3">Order Summary</h4>
              <div class="bg-neutral-50 p-4 rounded-lg">
                <div class="flex justify-between mb-2">
                  <span>Subtotal</span>
                  <span>${order.subtotal}</span>
                </div>
                <div class="flex justify-between mb-2">
                  <span>Shipping</span>
                  <span>${order.shipping_amount}</span>
                </div>
                <div class="flex justify-between mb-2">
                  <span>Tax</span>
                  <span>${order.tax_amount}</span>
                </div>
                <div class="flex justify-between font-semibold text-lg pt-2 border-t">
                  <span>Total</span>
                  <span>${order.total_amount}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;

    document.body.appendChild(modal);
    document.body.classList.add('overflow-hidden');

    // Animation
    gsap.from(modal.querySelector('.modal-content'), {
      duration: 0.3,
      opacity: 0,
      scale: 0.9,
      ease: "power2.out"
    });

    // Close handlers
    modal.querySelector('.close-modal').addEventListener('click', () => {
      this.closeModal(modal);
    });
    
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        this.closeModal(modal);
      }
    });
  }

  renderOrderTimeline(order) {
    const statuses = [
      { key: 'pending', label: 'Order Placed', icon: '📝' },
      { key: 'confirmed', label: 'Confirmed', icon: '✅' },
      { key: 'processing', label: 'Processing', icon: '⚙️' },
      { key: 'shipped', label: 'Shipped', icon: '🚚' },
      { key: 'delivered', label: 'Delivered', icon: '📦' }
    ];

    const currentIndex = statuses.findIndex(s => s.key === order.status);
    
    return statuses.map((status, index) => {
      const isCompleted = index <= currentIndex;
      const isCurrent = index === currentIndex;
      
      return `
        <div class="timeline-item flex items-center mb-4 ${isCompleted ? 'completed' : 'pending'}">
          <div class="timeline-icon w-8 h-8 rounded-full flex items-center justify-center ${isCompleted ? 'bg-green-500 text-white' : 'bg-neutral-200 text-neutral-500'} mr-4">
            ${isCompleted ? '✓' : status.icon}
          </div>
          <div class="flex-1">
            <h5 class="font-medium ${isCurrent ? 'text-primary-600' : ''}">${status.label}</h5>
            ${this.getStatusDate(order, status.key) ? `<p class="text-sm text-neutral-600">${this.getStatusDate(order, status.key)}</p>` : ''}
          </div>
        </div>
      `;
    }).join('');
  }

  getStatusDate(order, status) {
    const dateField = {
      'pending': order.created_at,
      'confirmed': order.confirmed_at,
      'shipped': order.shipped_at,
      'delivered': order.delivered_at
    }[status];
    
    return dateField ? new Date(dateField).toLocaleDateString() : null;
  }

  closeModal(modal) {
    gsap.to(modal, {
      duration: 0.3,
      opacity: 0,
      onComplete: () => {
        modal.remove();
        document.body.classList.remove('overflow-hidden');
      }
    });
  }

  // Notifications
  setupNotifications() {
    document.addEventListener('click', (e) => {
      if (e.target.matches('.mark-notification-read')) {
        e.preventDefault();
        const notificationId = e.target.dataset.notificationId;
        this.markNotificationRead(notificationId);
      }
    });
  }

  async markNotificationRead(notificationId) {
    try {
      await axios.patch(`/api/notifications/${notificationId}/read/`, {}, {
        headers: {
          'X-CSRFToken': this.getCSRFToken()
        }
      });
      
      const notification = document.querySelector(`[data-notification-id="${notificationId}"]`);
      if (notification) {
        notification.classList.remove('unread');
        notification.classList.add('read');
      }
    } catch (error) {
      console.error('Error marking notification as read:', error);
    }
  }

  // Profile management
  setupProfileManagement() {
    const profileForm = document.querySelector('.profile-form');
    if (profileForm) {
      profileForm.addEventListener('submit', (e) => {
        e.preventDefault();
        this.updateProfile();
      });
    }
  }

  async updateProfile() {
    const form = document.querySelector('.profile-form');
    const formData = new FormData(form);
    
    try {
      const response = await axios.post('/api/profile/update/', formData, {
        headers: {
          'X-CSRFToken': this.getCSRFToken()
        }
      });

      if (response.data.success) {
        this.showNotification('Profile updated successfully', 'success');
      }
    } catch (error) {
      console.error('Error updating profile:', error);
      this.showNotification('Error updating profile', 'error');
    }
  }

  // Utility methods
  async loadDashboardData() {
    try {
      const response = await axios.get('/api/dashboard/');
      const data = response.data;
      
      // Update dashboard statistics
      this.updateDashboardStats(data.stats);
      
      // Load recent activity
      this.renderRecentActivity(data.recent_activity);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    }
  }

  updateDashboardStats(stats) {
    const elements = {
      totalOrders: document.querySelector('.stat-total-orders'),
      totalSpent: document.querySelector('.stat-total-spent'),
      wishlistCount: document.querySelector('.stat-wishlist-count'),
      activeCommissions: document.querySelector('.stat-active-commissions')
    };

    Object.entries(elements).forEach(([key, el]) => {
      if (el && stats[key] !== undefined) {
        el.textContent = stats[key];
      }
    });
  }

  renderRecentActivity(activities) {
    const container = document.querySelector('.recent-activity');
    if (!container || !activities) return;

    const html = activities.map(activity => `
      <div class="activity-item flex items-center gap-3 py-3 border-b border-neutral-100 last:border-b-0">
        <div class="activity-icon w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center text-primary-600 text-sm">
          ${this.getActivityIcon(activity.type)}
        </div>
        <div class="flex-1">
          <p class="text-sm">${activity.description}</p>
          <p class="text-xs text-neutral-500">${new Date(activity.timestamp).toLocaleDateString()}</p>
        </div>
      </div>
    `).join('');

    container.innerHTML = html;
  }

  getActivityIcon(type) {
    const icons = {
      order: '📦',
      wishlist: '❤️',
      inquiry: '💬',
      commission: '🎨',
      profile: '👤'
    };
    return icons[type] || '•';
  }

  getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
  }

  showNotification(message, type = 'info') {
    if (window.AizasFineArt) {
      const app = new window.AizasFineArt();
      app.showNotification(message, type);
    }
  }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  if (document.querySelector('.dashboard-container')) {
    new UserDashboard();
  }
});

export default UserDashboard;
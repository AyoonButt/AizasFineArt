import React from 'react';
import { createRoot } from 'react-dom/client';
import { MotionConfig } from 'framer-motion';

// Import main components
import GalleryGrid from '@components/Gallery/GalleryGrid';
import { ShopGrid, ArtworkCardShop } from '@components/Gallery';
import ArtworkImageViewer from '@components/Gallery/ArtworkImageViewer';
import FeaturedSlider from './components/Gallery/FeaturedSlider.jsx';
import OrderTracking from './components/Orders/OrderTracking.jsx';
import ContactForm from '@components/Forms/ContactForm';
import NewsletterForm from '@components/Forms/NewsletterForm';
import CommissionForm from '@components/Forms/CommissionForm';
import Navbar from '@components/Navigation/Navbar';
import { ArtworkForm, ArtworkImageManager } from '@components/Artwork';

// Global motion configuration
const motionConfig = {
  transition: { type: "spring", stiffness: 260, damping: 20 },
  reducedMotion: "user"
};

// Component registry for dynamic mounting
const componentRegistry = {
  'gallery-grid': GalleryGrid,
  'shop-grid': ShopGrid,
  'artwork-image-viewer': ArtworkImageViewer,
  'featured-slider': FeaturedSlider,
  'order-tracking': OrderTracking,
  'contact-form': ContactForm,
  'newsletter-form': NewsletterForm,
  'commission-form': CommissionForm,
  'navbar': Navbar,
  'ArtworkForm': ArtworkForm,
  'ArtworkImageManager': ArtworkImageManager,
  'ArtworkCardShop': ArtworkCardShop,
};

// Django-React bridge for passing server data to components
window.ReactComponents = {
  // Direct component access
  ArtworkForm: ({ container, props }) => {
    // Check if root already exists
    if (!container._reactRoot) {
      container._reactRoot = createRoot(container);
    }
    container._reactRoot.render(
      <MotionConfig {...motionConfig}>
        <ArtworkForm {...props} />
      </MotionConfig>
    );
    return container._reactRoot;
  },
  
  ArtworkImageManager: ({ container, props }) => {
    // Check if root already exists
    if (!container._reactRoot) {
      container._reactRoot = createRoot(container);
    }
    container._reactRoot.render(
      <MotionConfig {...motionConfig}>
        <ArtworkImageManager {...props} />
      </MotionConfig>
    );
    return container._reactRoot;
  },

  mount: (componentName, elementId, props = {}) => {
    const Component = componentRegistry[componentName];
    const element = document.getElementById(elementId);
    
    if (Component && element) {
      // Check if root already exists
      if (!element._reactRoot) {
        element._reactRoot = createRoot(element);
      }
      element._reactRoot.render(
        <MotionConfig {...motionConfig}>
          <Component {...props} />
        </MotionConfig>
      );
      return element._reactRoot;
    }
    console.warn(`Component ${componentName} or element ${elementId} not found`);
  },

  mountAll: () => {
    // Auto-mount components based on data attributes
    document.querySelectorAll('[data-react-component]').forEach(element => {
      const componentName = element.dataset.reactComponent;
      const props = element.dataset.reactProps ? JSON.parse(element.dataset.reactProps) : {};
      
      if (componentRegistry[componentName]) {
        // Only create root if it doesn't exist
        if (!element._reactRoot) {
          element._reactRoot = createRoot(element);
        }
        element._reactRoot.render(
          <MotionConfig {...motionConfig}>
            {React.createElement(componentRegistry[componentName], props)}
          </MotionConfig>
        );
      }
    });
  },

  unmountAll: () => {
    document.querySelectorAll('[data-react-component]').forEach(element => {
      if (element._reactRoot) {
        element._reactRoot.unmount();
        delete element._reactRoot;
      }
    });
  }
};

// Auto-initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
  window.ReactComponents.mountAll();
});

// HTMX integration - remount React components after HTMX swaps
document.body.addEventListener('htmx:afterSettle', () => {
  window.ReactComponents.mountAll();
});

// Export for manual use
export default window.ReactComponents;
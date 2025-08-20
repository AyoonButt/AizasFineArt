import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import ArtworkCardShop from './ArtworkCardShop';
import GalleryFilters from './GalleryFilters';
import axios from 'axios';

const ShopGrid = ({ 
  initialArtworks = [],
  showFilters = true,
  endpoint = '/api/artworks/',
  medium = 'all',
  category = 'all'
}) => {
  const [artworks, setArtworks] = useState(initialArtworks);
  const [filters, setFilters] = useState({ medium, category }); // Show all artworks in shop
  const [loading, setLoading] = useState(false);
  const [totalCount, setTotalCount] = useState(initialArtworks.length);
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'list'

  // Container animation variants
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
        delayChildren: 0.2
      }
    }
  };

  // Grid animation variants
  const gridVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.08,
        delayChildren: 0.1
      }
    }
  };

  // Fetch artworks from API
  const fetchArtworks = async (newFilters = filters) => {
    setLoading(true);
    
    try {
      const params = new URLSearchParams();
      
      // No status filtering - show all artworks
      
      if (newFilters.medium && newFilters.medium !== 'all') {
        params.append('medium', newFilters.medium);
      }
      if (newFilters.category && newFilters.category !== 'all') {
        params.append('category', newFilters.category);
      }
      if (newFilters.featured) {
        params.append('featured', 'true');
      }
      if (newFilters.price_min) {
        params.append('price_min', newFilters.price_min);
      }
      if (newFilters.price_max) {
        params.append('price_max', newFilters.price_max);
      }

      const response = await axios.get(`${endpoint}?${params.toString()}`);
      
      setArtworks(response.data.results || response.data);
      setTotalCount(response.data.count || response.data.length);
      
    } catch (error) {
      console.error('Error fetching artworks:', error);
      setArtworks([]);
    } finally {
      setLoading(false);
    }
  };

  // Handle filter changes
  const handleFilterChange = (newFilters) => {
    const updatedFilters = { ...filters, ...newFilters };
    setFilters(updatedFilters);
    fetchArtworks(updatedFilters);
  };

  // Initial load
  useEffect(() => {
    if (initialArtworks.length === 0) {
      fetchArtworks();
    }
  }, []);

  // Empty state component
  const EmptyState = () => (
    <motion.div
      className="text-center py-16"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <div className="max-w-md mx-auto">
        <svg className="w-24 h-24 mx-auto text-gray-300 mb-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
        </svg>
        <h3 className="text-xl font-medium text-gray-900 mb-2">No artworks found</h3>
        <p className="text-gray-600">
          No artworks match your current filters. Try adjusting your search criteria.
        </p>
      </div>
    </motion.div>
  );

  return (
    <motion.div 
      className="shop-gallery-container"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      {/* Filters */}
      {showFilters && (
        <GalleryFilters
          filters={filters}
          onFilterChange={handleFilterChange}
          loading={loading}
        />
      )}

      {/* Results Header */}
      <motion.div 
        className="flex items-center justify-between mb-8 p-4 bg-white rounded-lg shadow-sm"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <div className="flex items-center gap-4">
          <p className="text-sm text-gray-600">
            {loading ? 'Loading...' : `${totalCount} artwork${totalCount !== 1 ? 's' : ''}`}
            {filters.medium !== 'all' && ` in ${filters.medium.charAt(0).toUpperCase() + filters.medium.slice(1)}`}
            {filters.category !== 'all' && ` - ${filters.category.charAt(0).toUpperCase() + filters.category.slice(1)}`}
          </p>
          
          {/* Multi-Image Info */}
          <div className="hidden md:flex items-center text-xs text-gray-500 bg-gray-100 px-3 py-1 rounded-full">
            <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
            </svg>
            Click thumbnails to view all images
          </div>
        </div>

        {/* View Toggle */}
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setViewMode('grid')}
            className={`p-2 rounded-lg transition-colors ${
              viewMode === 'grid' 
                ? 'bg-mocha text-white' 
                : 'text-gray-600 hover:text-mocha hover:bg-gray-100'
            }`}
            title="Grid View"
          >
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path d="M5 3a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2V5a2 2 0 00-2-2H5zM5 11a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2v-2a2 2 0 00-2-2H5zM11 5a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V5zM11 13a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
            </svg>
          </button>
          <button
            onClick={() => setViewMode('list')}
            className={`p-2 rounded-lg transition-colors ${
              viewMode === 'list' 
                ? 'bg-mocha text-white' 
                : 'text-gray-600 hover:text-mocha hover:bg-gray-100'
            }`}
            title="List View"
          >
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
            </svg>
          </button>
        </div>
      </motion.div>

      {/* Loading Overlay */}
      <AnimatePresence>
        {loading && (
          <motion.div
            className="absolute inset-0 bg-white/80 backdrop-blur-sm flex items-center justify-center z-10 rounded-lg"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <motion.div
              className="flex space-x-1"
              initial="hidden"
              animate="visible"
              variants={{
                visible: {
                  transition: {
                    staggerChildren: 0.2
                  }
                }
              }}
            >
              {[0, 1, 2].map((i) => (
                <motion.div
                  key={i}
                  className="w-3 h-3 bg-mocha rounded-full"
                  variants={{
                    hidden: { y: 0 },
                    visible: {
                      y: [-10, 0],
                      transition: {
                        duration: 0.6,
                        repeat: Infinity,
                        repeatType: "mirror"
                      }
                    }
                  }}
                />
              ))}
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Shop Grid */}
      <AnimatePresence mode="wait">
        {artworks.length > 0 ? (
          <motion.div
            key="shop-grid"
            className={`grid gap-6 ${
              viewMode === 'grid' 
                ? 'grid-cols-1 md:grid-cols-2 xl:grid-cols-3' 
                : 'grid-cols-1 max-w-4xl mx-auto'
            }`}
            variants={gridVariants}
            initial="hidden"
            animate="visible"
            exit="hidden"
          >
            {artworks.map((artwork, index) => (
              <ArtworkCardShop
                key={artwork.id || index}
                artwork={artwork}
                index={index}
              />
            ))}
          </motion.div>
        ) : (
          <motion.div key="empty-state">
            <EmptyState />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Load More Button (for future pagination) */}
      {artworks.length > 0 && artworks.hasNext && (
        <motion.div 
          className="text-center mt-12"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
        >
          <button 
            className="btn-primary"
            onClick={() => {
              // Handle load more
            }}
          >
            Load More Artworks
          </button>
        </motion.div>
      )}
    </motion.div>
  );
};

export default ShopGrid;
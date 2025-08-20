import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import ArtworkCard from './ArtworkCard';
import ArtworkCardMultiImage from './ArtworkCardMultiImage';
import GalleryFilters from './GalleryFilters';
import axios from 'axios';

const GalleryGrid = ({ 
  initialArtworks = [],
  showFilters = true,
  endpoint = '/htmx/gallery-filter/',
  medium = 'all',
  category = 'all'
}) => {
  const [artworks, setArtworks] = useState(initialArtworks);
  const [filters, setFilters] = useState({ medium, category });
  const [loading, setLoading] = useState(false);
  const [totalCount, setTotalCount] = useState(initialArtworks.length);

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

  // Stats animation variants
  const statsVariants = {
    hidden: { opacity: 0, y: -20 },
    visible: { 
      opacity: 1, 
      y: 0,
      transition: { duration: 0.5 }
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

  // Load more animation
  const loadMoreVariants = {
    hidden: { opacity: 0, scale: 0.8 },
    visible: { 
      opacity: 1, 
      scale: 1,
      transition: { type: "spring", stiffness: 300, damping: 24 }
    }
  };

  // Handle filter changes
  const handleFilterChange = async (newFilters) => {
    setLoading(true);
    setFilters(newFilters);

    try {
      const response = await axios.get(endpoint, {
        params: newFilters,
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        }
      });

      // Assuming the endpoint returns JSON with artwork data
      if (response.data.artworks) {
        setArtworks(response.data.artworks);
        setTotalCount(response.data.total_count || response.data.artworks.length);
      }
    } catch (error) {
      console.error('Error filtering artworks:', error);
    } finally {
      setLoading(false);
    }
  };

  // Empty state component
  const EmptyState = () => (
    <motion.div
      className="text-center py-12"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
    >
      <motion.div 
        className="w-24 h-24 mx-auto mb-4 rounded-full bg-neutral-100 flex items-center justify-center"
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ type: "spring", stiffness: 300, damping: 24, delay: 0.2 }}
      >
        <svg className="w-12 h-12 text-neutral-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
      </motion.div>
      <h3 className="text-xl font-playfair font-semibold text-neutral-800 mb-2">No Artworks Found</h3>
      <p className="text-neutral-600 mb-4">
        {filters.medium !== 'all' || filters.category !== 'all'
          ? 'Try adjusting your filters to see more artworks.'
          : 'Check back later for new artworks.'}
      </p>
      {(filters.medium !== 'all' || filters.category !== 'all') && (
        <motion.button
          className="btn-outline"
          onClick={() => handleFilterChange({ medium: 'all', category: 'all' })}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          Clear Filters
        </motion.button>
      )}
    </motion.div>
  );

  return (
    <motion.div
      className="gallery-container"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      {/* Gallery Filters */}
      {showFilters && (
        <GalleryFilters
          currentMedium={filters.medium}
          currentCategory={filters.category}
          onFilterChange={handleFilterChange}
          loading={loading}
        />
      )}

      {/* Gallery Stats */}
      <motion.div 
        className="flex justify-between items-center mb-6"
        variants={statsVariants}
      >
        <p className="text-neutral-600">
          Showing {totalCount} artwork{totalCount !== 1 ? 's' : ''}
          {filters.medium !== 'all' && ` in ${filters.medium.charAt(0).toUpperCase() + filters.medium.slice(1)}`}
          {filters.category !== 'all' && ` - ${filters.category.charAt(0).toUpperCase() + filters.category.slice(1)}`}
        </p>

        {/* View Toggle */}
        <div className="flex space-x-2">
          <motion.button 
            className="p-2 text-neutral-600 hover:text-primary-500 transition-colors"
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            title="Grid View"
          >
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path d="M5 3a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2V5a2 2 0 00-2-2H5zM5 11a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2v-2a2 2 0 00-2-2H5zM11 5a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V5zM11 13a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
            </svg>
          </motion.button>
          <motion.button 
            className="p-2 text-neutral-600 hover:text-primary-500 transition-colors"
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            title="List View"
          >
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
            </svg>
          </motion.button>
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
                  className="w-3 h-3 bg-primary-500 rounded-full"
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

      {/* Gallery Grid */}
      <AnimatePresence mode="wait">
        {artworks.length > 0 ? (
          <motion.div
            key="gallery-grid"
            className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6"
            variants={gridVariants}
            initial="hidden"
            animate="visible"
            exit="hidden"
          >
            {artworks.map((artwork, index) => (
              <ArtworkCardMultiImage
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
          className="text-center mt-8"
          variants={loadMoreVariants}
        >
          <motion.button
            className="btn-primary"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => {/* Handle load more */}}
          >
            Load More Artworks
          </motion.button>
        </motion.div>
      )}
    </motion.div>
  );
};

export default GalleryGrid;
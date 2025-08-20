import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const GalleryFilters = ({ 
  currentMedium = 'all',
  currentCategory = 'all',
  onFilterChange,
  loading = false
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState({
    medium: currentMedium,
    category: currentCategory
  });

  const mediaChoices = [
    { value: 'all', label: 'All Media' },
    { value: 'watercolor', label: 'Watercolor' },
    { value: 'oil', label: 'Oil Painting' },
    { value: 'acrylic', label: 'Acrylic' },
    { value: 'mixed', label: 'Mixed Media' }
  ];

  const categoryChoices = [
    { value: 'all', label: 'All Categories' },
    { value: 'landscape', label: 'Landscapes' },
    { value: 'portrait', label: 'Portraits' },
    { value: 'still_life', label: 'Still Life' },
    { value: 'abstract', label: 'Abstract' }
  ];

  const quickFilters = [
    { medium: 'watercolor', category: 'all', label: 'Watercolors' },
    { medium: 'oil', category: 'all', label: 'Oil Paintings' },
    { medium: 'all', category: 'landscape', label: 'Landscapes' },
    { medium: 'all', category: 'portrait', label: 'Portraits' }
  ];

  // Animation variants
  const containerVariants = {
    hidden: { opacity: 0, y: -20 },
    visible: { 
      opacity: 1, 
      y: 0,
      transition: {
        type: "spring",
        stiffness: 300,
        damping: 24,
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, x: -10 },
    visible: { 
      opacity: 1, 
      x: 0,
      transition: { type: "spring", stiffness: 300, damping: 24 }
    }
  };

  const quickFilterVariants = {
    hidden: { opacity: 0, scale: 0.8 },
    visible: { 
      opacity: 1, 
      scale: 1,
      transition: { type: "spring", stiffness: 300, damping: 24 }
    }
  };

  // Handle filter changes
  const handleFilterChange = (key, value) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);
    onFilterChange?.(newFilters);
  };

  // Handle search
  const handleSearch = (query) => {
    setSearchQuery(query);
    // Debounced search implementation would go here
    const searchFilters = { ...filters, search: query };
    onFilterChange?.(searchFilters);
  };

  // Handle quick filter click
  const handleQuickFilter = (filter) => {
    const newFilters = { medium: filter.medium, category: filter.category };
    setFilters(newFilters);
    onFilterChange?.(newFilters);
  };

  // Clear all filters
  const clearFilters = () => {
    const clearedFilters = { medium: 'all', category: 'all' };
    setFilters(clearedFilters);
    setSearchQuery('');
    onFilterChange?.(clearedFilters);
  };

  const hasActiveFilters = filters.medium !== 'all' || filters.category !== 'all' || searchQuery;

  return (
    <motion.div
      className="gallery-filters mb-8 p-6 bg-neutral-50 rounded-lg border relative overflow-hidden"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      {/* Loading overlay */}
      <AnimatePresence>
        {loading && (
          <motion.div
            className="absolute inset-0 bg-white/80 backdrop-blur-sm flex items-center justify-center z-10"
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
                  transition: { staggerChildren: 0.2 }
                }
              }}
            >
              {[0, 1, 2].map((i) => (
                <motion.div
                  key={i}
                  className="w-2 h-2 bg-primary-500 rounded-full"
                  variants={{
                    hidden: { scale: 0 },
                    visible: {
                      scale: [0, 1, 0],
                      transition: {
                        duration: 1.2,
                        repeat: Infinity,
                        ease: "easeInOut"
                      }
                    }
                  }}
                />
              ))}
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
        
        {/* Filter Controls */}
        <motion.div 
          className="flex flex-col sm:flex-row space-y-4 sm:space-y-0 sm:space-x-6"
          variants={itemVariants}
        >
          {/* Medium Filter */}
          <div className="flex flex-col space-y-2">
            <label className="text-sm font-medium text-neutral-700">Medium</label>
            <motion.select
              name="medium"
              value={filters.medium}
              onChange={(e) => handleFilterChange('medium', e.target.value)}
              className="form-select text-sm min-w-[140px]"
              whileFocus={{ scale: 1.02 }}
              transition={{ type: "spring", stiffness: 300, damping: 24 }}
            >
              {mediaChoices.map(choice => (
                <option key={choice.value} value={choice.value}>
                  {choice.label}
                </option>
              ))}
            </motion.select>
          </div>
          
          {/* Category Filter */}
          <div className="flex flex-col space-y-2">
            <label className="text-sm font-medium text-neutral-700">Category</label>
            <motion.select
              name="category"
              value={filters.category}
              onChange={(e) => handleFilterChange('category', e.target.value)}
              className="form-select text-sm min-w-[150px]"
              whileFocus={{ scale: 1.02 }}
              transition={{ type: "spring", stiffness: 300, damping: 24 }}
            >
              {categoryChoices.map(choice => (
                <option key={choice.value} value={choice.value}>
                  {choice.label}
                </option>
              ))}
            </motion.select>
          </div>
        </motion.div>
        
        {/* Search and Actions */}
        <motion.div 
          className="flex flex-col sm:flex-row space-y-3 sm:space-y-0 sm:space-x-3"
          variants={itemVariants}
        >
          {/* Search */}
          <div className="relative">
            <motion.input
              type="search"
              placeholder="Search artworks..."
              value={searchQuery}
              onChange={(e) => handleSearch(e.target.value)}
              className="w-full sm:w-64 pl-10 pr-4 py-2 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-sm"
              whileFocus={{ scale: 1.02 }}
              transition={{ type: "spring", stiffness: 300, damping: 24 }}
            />
            <svg className="absolute left-3 top-2.5 w-4 h-4 text-neutral-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          
          {/* Clear Filters */}
          <AnimatePresence>
            {hasActiveFilters && (
              <motion.button
                type="button"
                className="btn-outline text-sm whitespace-nowrap"
                onClick={clearFilters}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.8 }}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                transition={{ type: "spring", stiffness: 300, damping: 24 }}
              >
                Clear Filters
              </motion.button>
            )}
          </AnimatePresence>
        </motion.div>
      </div>
      
      {/* Quick Filter Tags */}
      <motion.div 
        className="mt-4 flex flex-wrap gap-2"
        variants={itemVariants}
      >
        <span className="text-sm text-neutral-600 mr-2">Quick filters:</span>
        
        {quickFilters.map((filter, index) => (
          <motion.button
            key={`${filter.medium}-${filter.category}`}
            className={`px-3 py-1 text-xs rounded-full border transition-colors ${
              filters.medium === filter.medium && filters.category === filter.category
                ? 'bg-primary-100 border-primary-300 text-primary-700'
                : 'bg-white border-neutral-300 hover:border-primary-300 hover:text-primary-600'
            }`}
            onClick={() => handleQuickFilter(filter)}
            variants={quickFilterVariants}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            transition={{ 
              type: "spring", 
              stiffness: 300, 
              damping: 24,
              delay: index * 0.05 
            }}
          >
            {filter.label}
          </motion.button>
        ))}
      </motion.div>
    </motion.div>
  );
};

export default GalleryFilters;
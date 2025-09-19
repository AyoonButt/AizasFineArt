import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const ArtworkCardMultiImage = ({ artwork, index = 0 }) => {
  const [isImageLoaded, setIsImageLoaded] = useState(false);
  const [isWishlisted, setIsWishlisted] = useState(false);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [allImages, setAllImages] = useState([]);

  // Build array of all available images
  useEffect(() => {
    const images = [];
    
    // Add main image if available
    if (artwork.main_image_url && artwork.main_image_url !== 'https://via.placeholder.com/800x600?text=Artwork') {
      images.push({
        url: artwork.main_image_url,
        type: 'main',
        label: 'Main View'
      });
    }
    
    // Add frame images
    [1, 2, 3, 4].forEach(frameNum => {
      const frameUrl = artwork[`frame${frameNum}_image_url`];
      if (frameUrl && frameUrl.trim()) {
        images.push({
          url: frameUrl,
          type: 'frame',
          label: `Frame ${frameNum}`
        });
      }
    });
    
    // Fallback to main image or placeholder if no images
    if (images.length === 0) {
      images.push({
        url: artwork.image || artwork.main_image_url || '/static/dist/images/placeholder-artwork.jpg',
        type: 'main',
        label: 'Main View'
      });
    }
    
    setAllImages(images);
  }, [artwork]);

  // Card animation variants
  const cardVariants = {
    hidden: { 
      opacity: 0, 
      y: 30,
      scale: 0.9
    },
    visible: { 
      opacity: 1, 
      y: 0,
      scale: 1,
      transition: {
        type: "spring",
        stiffness: 300,
        damping: 24,
        delay: index * 0.1
      }
    }
  };

  // Hover animation variants
  const hoverVariants = {
    rest: { 
      scale: 1,
      y: 0,
      transition: { type: "spring", stiffness: 300, damping: 24 }
    },
    hover: { 
      scale: 1.03,
      y: -8,
      transition: { type: "spring", stiffness: 300, damping: 24 }
    }
  };

  // Image cycling on hover
  const handleImageCycle = () => {
    if (allImages.length > 1) {
      setCurrentImageIndex((prev) => (prev + 1) % allImages.length);
    }
  };

  // Reset to first image when not hovering
  const handleMouseLeave = () => {
    if (allImages.length > 1) {
      setTimeout(() => setCurrentImageIndex(0), 200);
    }
  };

  // Wishlist toggle
  const handleWishlistToggle = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    try {
      const response = await fetch('/htmx/wishlist/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value
        },
        body: JSON.stringify({ 
          artwork_id: artwork.id,
          action: isWishlisted ? 'remove' : 'add'
        })
      });

      if (response.ok) {
        setIsWishlisted(!isWishlisted);
      }
    } catch (error) {
      console.error('Error toggling wishlist:', error);
    }
  };

  const getOriginalBadge = () => {
    return artwork.original_available ? 
      { class: 'bg-primary-500 text-white', text: 'Original' } : 
      null;
  };

  const currentImage = allImages[currentImageIndex] || allImages[0];

  return (
    <motion.div
      className="artwork-card card group relative overflow-hidden cursor-pointer"
      variants={cardVariants}
      initial="hidden"
      animate="visible"
      whileHover="hover"
      onMouseEnter={handleImageCycle}
      onMouseLeave={handleMouseLeave}
    >
      <motion.div variants={hoverVariants}>
        <a 
          href={artwork.get_display_url || '#'} 
          className="block"
        >
          {/* Image Container */}
          <div className="relative overflow-hidden aspect-square">
            {/* Loading placeholder */}
            {!isImageLoaded && (
              <div className="absolute inset-0 bg-gradient-to-br from-neutral-100 to-neutral-200 flex items-center justify-center">
                <motion.div
                  className="w-8 h-8 border-2 border-primary-300 border-t-primary-600 rounded-full"
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                />
              </div>
            )}

            {/* Image Slider */}
            <AnimatePresence mode="wait">
              <motion.img 
                key={currentImageIndex}
                src={currentImage?.url || '/static/dist/images/placeholder-artwork.jpg'} 
                alt={artwork.alt_text || artwork.title || 'Artwork'}
                className="artwork-image w-full h-full object-cover"
                initial={{ opacity: 0 }}
                animate={{ opacity: isImageLoaded ? 1 : 0 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.3 }}
                loading="lazy"
                onLoad={() => setIsImageLoaded(true)}
                onError={(e) => {
                  e.target.src = '/static/dist/images/placeholder-artwork.jpg';
                  setIsImageLoaded(true);
                }}
              />
            </AnimatePresence>
            
            {/* Image Count Indicator */}
            {allImages.length > 1 && (
              <motion.div 
                className="absolute top-3 left-3 bg-black/60 text-white text-xs px-2 py-1 rounded-full"
                initial={{ opacity: 0 }}
                whileHover={{ opacity: 1 }}
                transition={{ delay: 0.1 }}
              >
                {currentImageIndex + 1}/{allImages.length}
              </motion.div>
            )}

            {/* Image Type Indicator */}
            {currentImage?.type === 'frame' && (
              <motion.div 
                className="absolute bottom-3 left-3 bg-mocha/80 text-white text-xs px-2 py-1 rounded"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 10 }}
                transition={{ duration: 0.2 }}
              >
                {currentImage.label}
              </motion.div>
            )}
            
            {/* Artwork Overlay */}
            <motion.div 
              className="artwork-overlay absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity"
            >
              <div className="absolute bottom-4 left-4 right-4 text-white">
                <motion.div
                  initial={{ y: 20, opacity: 0 }}
                  whileHover={{ y: 0, opacity: 1 }}
                  transition={{ delay: 0.1 }}
                >
                  <h3 className="font-playfair font-semibold text-lg mb-1 line-clamp-2">
                    {artwork.title}
                  </h3>
                  {artwork.medium && (
                    <p className="text-sm opacity-90">
                      {artwork.medium} • {artwork.dimensions_width && artwork.dimensions_height ? 
                        `${artwork.dimensions_width}" × ${artwork.dimensions_height}"` : 'Various Sizes'}
                    </p>
                  )}
                  
                  {/* Original Badge */}
                  {getOriginalBadge() && (
                    <motion.span 
                      className={`inline-block mt-2 px-3 py-1 text-xs font-medium rounded-full ${getOriginalBadge().class}`}
                      initial={{ scale: 1, opacity: 1 }}
                      animate={{ scale: 1, opacity: 1 }}
                      transition={{ delay: 0.1, type: "spring", stiffness: 300, damping: 24 }}
                    >
                      {getOriginalBadge().text}
                    </motion.span>
                  )}
                </motion.div>
              </div>

              {/* Price Display */}
              {artwork.original_price && artwork.status === 'available' && (
                <motion.div 
                  className="absolute top-4 right-4 bg-white/20 backdrop-blur-sm rounded-full px-3 py-1"
                  initial={{ scale: 0, opacity: 0 }}
                  whileHover={{ scale: 1, opacity: 1 }}
                  transition={{ delay: 0.1 }}
                >
                  <span className="text-white font-medium text-sm">
                    ${artwork.original_price}
                  </span>
                </motion.div>
              )}
            </motion.div>
          </div>
          
          {/* Card Content */}
          <div className="p-4">
            {/* Title and Medium */}
            <div className="mb-2">
              <h3 className="font-playfair font-semibold text-lg text-neutral-800 group-hover:text-primary-600 transition-colors line-clamp-1">
                {artwork.title}
              </h3>
              {artwork.medium && (
                <p className="text-sm text-neutral-600">
                  {artwork.medium}
                </p>
              )}
            </div>
            
            {/* Dimensions */}
            {artwork.dimensions_width && artwork.dimensions_height && (
              <p className="text-sm text-neutral-500 mb-2">
                {artwork.dimensions_width}" × {artwork.dimensions_height}"
              </p>
            )}
            
            {/* Price and Status */}
            <div className="flex items-center justify-between mt-3">
              {artwork.original_price && artwork.status === 'available' && (
                <div className="price-display">
                  <span className="font-semibold text-lg">
                    ${typeof artwork.original_price === 'number' ? artwork.original_price.toFixed(0) : artwork.original_price}
                  </span>
                </div>
              )}
              
              <div className="flex items-center gap-2">
                {getOriginalBadge() && (
                  <span className={`${getOriginalBadge().class} text-xs px-2 py-1 rounded-full font-medium`}>
                    {getOriginalBadge().text}
                  </span>
                )}
              </div>
            </div>

            {/* Multi-Image Indicator */}
            {allImages.length > 1 && (
              <div className="flex items-center justify-center mt-3 space-x-1">
                {allImages.map((_, idx) => (
                  <div 
                    key={idx}
                    className={`w-1.5 h-1.5 rounded-full transition-colors ${
                      idx === currentImageIndex ? 'bg-mocha' : 'bg-gray-300'
                    }`}
                  />
                ))}
              </div>
            )}
          </div>
        </a>

        {/* Quick Actions */}
        <div className="absolute top-3 right-3 opacity-0 group-hover:opacity-100 transition-opacity">
          <div className="flex space-x-2">
            {/* Wishlist Button */}
            <motion.button
              className="w-8 h-8 bg-white/90 hover:bg-white rounded-full flex items-center justify-center shadow-sm"
              onClick={handleWishlistToggle}
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              title={isWishlisted ? "Remove from Wishlist" : "Add to Wishlist"}
            >
              <motion.svg 
                className={`w-4 h-4 transition-colors ${isWishlisted ? 'text-red-500 fill-current' : 'text-neutral-600'}`}
                fill={isWishlisted ? "currentColor" : "none"} 
                stroke="currentColor" 
                viewBox="0 0 24 24"
                animate={isWishlisted ? { scale: [1, 1.2, 1] } : { scale: 1 }}
                transition={{ duration: 0.3 }}
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
              </motion.svg>
            </motion.button>
            
            {/* View All Images Button */}
            {allImages.length > 1 && (
              <motion.button
                className="w-8 h-8 bg-white/90 hover:bg-white rounded-full flex items-center justify-center shadow-sm"
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                title={`View all ${allImages.length} images`}
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  // Handle view all images functionality
                }}
              >
                <svg className="w-4 h-4 text-neutral-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </motion.button>
            )}
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
};

export default ArtworkCardMultiImage;
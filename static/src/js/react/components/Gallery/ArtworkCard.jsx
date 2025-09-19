import React, { useState } from 'react';
import { motion } from 'framer-motion';

const ArtworkCard = ({ artwork, index = 0 }) => {
  const [isImageLoaded, setIsImageLoaded] = useState(false);
  const [isWishlisted, setIsWishlisted] = useState(false);

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
      rotateX: 0,
      transition: { type: "spring", stiffness: 300, damping: 24 }
    },
    hover: { 
      scale: 1.03,
      y: -8,
      rotateX: 5,
      transition: { type: "spring", stiffness: 300, damping: 24 }
    }
  };

  // Overlay animation variants
  const overlayVariants = {
    rest: { opacity: 0 },
    hover: { 
      opacity: 1,
      transition: { duration: 0.3 }
    }
  };

  // Image loading animation
  const imageVariants = {
    loading: { opacity: 0 },
    loaded: { 
      opacity: 1,
      transition: { duration: 0.5 }
    }
  };

  // Wishlist toggle
  const handleWishlistToggle = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    try {
      // API call to toggle wishlist
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
    return artwork.type === 'original' ? 
      { class: 'bg-primary-500 text-white', text: 'Original' } : 
      null;
  };

  return (
    <motion.div
      className="artwork-card card group relative overflow-hidden cursor-pointer"
      variants={cardVariants}
      initial="hidden"
      animate="visible"
      whileHover="hover"
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

            {/* Artwork Image */}
            <motion.img 
              src={artwork.image || '/static/dist/images/placeholder-artwork.jpg'} 
              alt={artwork.title || 'Artwork'}
              className="artwork-image w-full h-full object-cover"
              variants={imageVariants}
              initial="loading"
              animate={isImageLoaded ? "loaded" : "loading"}
              loading="lazy"
              onLoad={() => setIsImageLoaded(true)}
              onError={(e) => {
                e.target.src = '/static/dist/images/placeholder-artwork.jpg';
                setIsImageLoaded(true);
              }}
            />
            
            {/* Artwork Overlay */}
            <motion.div 
              className="artwork-overlay absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent"
              variants={overlayVariants}
              initial="rest"
              whileHover="hover"
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
                      {artwork.medium} • {artwork.width && artwork.height ? `${artwork.width}" × ${artwork.height}"` : 'Various Sizes'}
                    </p>
                  )}
                  
                  {/* Status Badge */}
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
              {artwork.price && (
                <motion.div 
                  className="absolute top-4 right-4 bg-white/20 backdrop-blur-sm rounded-full px-3 py-1"
                  initial={{ scale: 0, opacity: 0 }}
                  whileHover={{ scale: 1, opacity: 1 }}
                  transition={{ delay: 0.1 }}
                >
                  <span className="text-white font-medium text-sm">
                    ${artwork.price}
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
            {artwork.width && artwork.height && (
              <p className="text-sm text-neutral-500 mb-2">
                {artwork.width}" × {artwork.height}"
                {artwork.depth && ` × ${artwork.depth}"`}
              </p>
            )}
            
            {/* Price and Status */}
            <div className="flex items-center justify-between mt-3">
              {artwork.price && artwork.status === 'available' && (
                <div className="price-display">
                  <span className="font-semibold text-lg">
                    ${typeof artwork.price === 'number' ? artwork.price.toFixed(0) : artwork.price}
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
            
            {/* Share Button */}
            <motion.button
              className="w-8 h-8 bg-white/90 hover:bg-white rounded-full flex items-center justify-center shadow-sm"
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              title="Share"
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
                // Handle share functionality
              }}
            >
              <svg className="w-4 h-4 text-neutral-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z" />
              </svg>
            </motion.button>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
};

export default ArtworkCard;
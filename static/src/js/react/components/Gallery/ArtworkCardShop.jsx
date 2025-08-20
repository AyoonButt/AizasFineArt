import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const ArtworkCardShop = ({ artwork, index = 0 }) => {
  const [isImageLoaded, setIsImageLoaded] = useState(false);
  const [isWishlisted, setIsWishlisted] = useState(false);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [allImages, setAllImages] = useState([]);

  // Build array of all 5 image slots (always show 5 thumbnails)
  useEffect(() => {
    const images = [];
    
    // Always create 5 image slots (1 main + 4 frames)
    for (let i = 0; i < 5; i++) {
      let imageData = null;
      
      if (i === 0) {
        // Main image slot
        if (artwork.all_images_transformed && artwork.all_images_transformed[0]) {
          imageData = {
            url: artwork.all_images_transformed[0],
            thumbnailUrl: artwork.all_images_thumbnails && artwork.all_images_thumbnails[0] 
              ? artwork.all_images_thumbnails[0] 
              : artwork.all_images_transformed[0],
            type: 'main',
            label: 'Main View',
            hasImage: true
          };
        } else if (artwork.main_image_url && artwork.main_image_url !== 'https://via.placeholder.com/800x600?text=Artwork') {
          imageData = {
            url: artwork.main_image_url,
            thumbnailUrl: artwork.main_image_url,
            type: 'main',
            label: 'Main View',
            hasImage: true
          };
        }
      } else {
        // Frame image slots
        const frameIndex = i;
        if (artwork.all_images_transformed && artwork.all_images_transformed[frameIndex]) {
          imageData = {
            url: artwork.all_images_transformed[frameIndex],
            thumbnailUrl: artwork.all_images_thumbnails && artwork.all_images_thumbnails[frameIndex] 
              ? artwork.all_images_thumbnails[frameIndex] 
              : artwork.all_images_transformed[frameIndex],
            type: 'frame',
            label: `Frame ${i}`,
            hasImage: true
          };
        } else {
          const frameUrl = artwork[`frame${i}_image_url`];
          if (frameUrl && frameUrl.trim()) {
            imageData = {
              url: frameUrl,
              thumbnailUrl: frameUrl,
              type: 'frame',
              label: `Frame ${i}`,
              hasImage: true
            };
          }
        }
      }
      
      // If no image data, create empty slot
      if (!imageData) {
        imageData = {
          url: null,
          thumbnailUrl: null,
          type: i === 0 ? 'main' : 'frame',
          label: i === 0 ? 'Main View' : `Frame ${i}`,
          hasImage: false
        };
      }
      
      images.push(imageData);
    }
    
    // Ensure we have at least a main image (fallback to placeholder)
    if (!images[0].hasImage) {
      images[0] = {
        url: artwork.image || artwork.main_image_url || '/static/dist/images/placeholder-artwork.jpg',
        thumbnailUrl: '/static/dist/images/placeholder-artwork.jpg',
        type: 'main',
        label: 'Main View',
        hasImage: true
      };
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

  // Thumbnail click handler
  const handleThumbnailClick = (imageIndex) => {
    setCurrentImageIndex(imageIndex);
    setIsImageLoaded(false); // Reset loading state for new image
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
      className="artwork-card-shop card group relative overflow-hidden bg-white shadow-sm hover:shadow-lg transition-shadow duration-300"
      variants={cardVariants}
      initial="hidden"
      animate="visible"
    >
      <div className="p-4">
        <a 
          href={artwork.get_absolute_url || '#'} 
          className="block"
        >
          {/* Main Image and Thumbnails Container */}
          <div className="flex gap-4">
            
            {/* Thumbnail Navigation Sidebar - Always show for 5-image layout */}
            <div className="flex-shrink-0 w-16 space-y-2">
              {allImages.map((image, index) => (
                <motion.button
                  key={index}
                  onClick={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    // Only switch to images that actually exist
                    if (image.hasImage) {
                      handleThumbnailClick(index);
                    }
                  }}
                  disabled={!image.hasImage}
                  className={`w-14 h-14 rounded-lg overflow-hidden border-2 transition-all duration-200 relative ${
                    currentImageIndex === index 
                      ? 'border-mocha shadow-md' 
                      : image.hasImage
                        ? 'border-gray-200 hover:border-gray-300 cursor-pointer'
                        : 'border-gray-100 cursor-not-allowed'
                  }`}
                  whileHover={image.hasImage ? { scale: 1.05 } : {}}
                  whileTap={image.hasImage ? { scale: 0.95 } : {}}
                  title={image.hasImage ? `View ${image.label}` : `${image.label} - No image available`}
                >
                  {image.hasImage ? (
                    <img
                      src={image.thumbnailUrl || image.url || '/static/dist/images/placeholder-artwork.jpg'}
                      alt={`${artwork.title} - ${image.label}`}
                      className="w-full h-full object-cover"
                      loading="lazy"
                    />
                  ) : (
                    <div className="w-full h-full bg-gray-50 flex items-center justify-center">
                      <svg className="w-6 h-6 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                      </svg>
                    </div>
                  )}
                  
                  {/* Active indicator */}
                  {currentImageIndex === index && image.hasImage && (
                    <motion.div 
                      className="absolute inset-0 bg-mocha bg-opacity-20 flex items-center justify-center"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                    >
                      <div className="w-2 h-2 bg-mocha rounded-full"></div>
                    </motion.div>
                  )}
                  
                  {/* Empty slot indicator */}
                  {!image.hasImage && (
                    <div className="absolute bottom-1 right-1">
                      <div className="w-1.5 h-1.5 bg-gray-300 rounded-full"></div>
                    </div>
                  )}
                </motion.button>
              ))}
            </div>
            
            {/* Main Image Container */}
            <div className="flex-1 relative">
              <div className="relative overflow-hidden aspect-square rounded-lg">
                {/* Loading placeholder */}
                {!isImageLoaded && (
                  <div className="absolute inset-0 bg-gradient-to-br from-neutral-100 to-neutral-200 flex items-center justify-center">
                    <motion.div
                      className="w-8 h-8 border-2 border-mocha border-t-transparent rounded-full"
                      animate={{ rotate: 360 }}
                      transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                    />
                  </div>
                )}

                {/* Main Image */}
                <AnimatePresence mode="wait">
                  {currentImage?.hasImage ? (
                    <motion.img 
                      key={currentImageIndex}
                      src={currentImage.url || '/static/dist/images/placeholder-artwork.jpg'} 
                      alt={artwork.alt_text || artwork.title || 'Artwork'}
                      className="w-full h-full object-cover"
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
                  ) : (
                    <motion.div
                      key={`empty-${currentImageIndex}`}
                      className="w-full h-full bg-gray-100 flex items-center justify-center"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      transition={{ duration: 0.3 }}
                    >
                      <div className="text-center text-gray-400">
                        <svg className="w-16 h-16 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                        </svg>
                        <p className="text-sm">{currentImage?.label || 'No Image'}</p>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>

                {/* Image Type Badge */}
                {currentImage?.type === 'frame' && currentImage?.hasImage && (
                  <motion.div 
                    className="absolute top-3 left-3 bg-black bg-opacity-60 text-white text-xs px-2 py-1 rounded"
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.2 }}
                  >
                    {currentImage.label}
                  </motion.div>
                )}

                {/* Status Badge */}
                {artwork.status && artwork.status !== 'available' && (
                  <motion.div 
                    className="absolute top-3 right-3"
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.3 }}
                  >
                    <span className={getStatusBadge(artwork.status).class}>
                      {getStatusBadge(artwork.status).text}
                    </span>
                  </motion.div>
                )}

                {/* Wishlist Button */}
                <div className="absolute top-3 right-3 opacity-0 group-hover:opacity-100 transition-opacity">
                  <motion.button
                    className="w-8 h-8 bg-white bg-opacity-90 hover:bg-white rounded-full flex items-center justify-center shadow-sm"
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
                </div>
              </div>
            </div>
          </div>
        </a>

        {/* Artwork Info */}
        <div className="mt-4">
          <div className="flex items-start justify-between">
            <div className="flex-1 min-w-0">
              <h3 className="text-lg font-semibold text-gray-900 group-hover:text-mocha transition-colors truncate">
                {artwork.title}
              </h3>
              
              <div className="flex items-center gap-2 mt-1 text-sm text-gray-600">
                {artwork.medium && (
                  <span className="capitalize">{artwork.medium}</span>
                )}
                {artwork.medium && artwork.dimensions_width && artwork.dimensions_height && (
                  <span>•</span>
                )}
                {artwork.dimensions_width && artwork.dimensions_height && (
                  <span>{artwork.dimensions_width}" × {artwork.dimensions_height}"</span>
                )}
              </div>

              {artwork.year_created && (
                <p className="text-sm text-gray-500 mt-1">
                  {artwork.year_created}
                </p>
              )}
            </div>

            <div className="text-right ml-4 flex flex-col items-end">
              {artwork.original_price && artwork.status === 'available' ? (
                <div className="text-lg font-bold text-mocha">
                  ${typeof artwork.original_price === 'number' 
                    ? artwork.original_price.toFixed(0) 
                    : artwork.original_price}
                </div>
              ) : (
                <div className="text-sm text-gray-500">
                  Price on request
                </div>
              )}

              {getOriginalBadge() && (
                <span className={`${getOriginalBadge().class} text-xs px-2 py-1 rounded-full font-medium mt-2`}>
                  {getOriginalBadge().text}
                </span>
              )}

              {artwork.prints_available && (
                <div className="text-xs text-gray-500 mt-1">
                  Prints available
                </div>
              )}
            </div>
          </div>

          {/* Image Navigation Dots (for single row layout) */}
          <div className="flex items-center justify-center mt-4 space-x-2">
            {allImages.map((image, idx) => (
              <button
                key={idx}
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  // Only switch to images that actually exist
                  if (image.hasImage) {
                    handleThumbnailClick(idx);
                  }
                }}
                disabled={!image.hasImage}
                className={`w-2 h-2 rounded-full transition-all duration-200 ${
                  idx === currentImageIndex 
                    ? 'bg-mocha w-6' 
                    : image.hasImage
                      ? 'bg-gray-300 hover:bg-gray-400 cursor-pointer'
                      : 'bg-gray-200 cursor-not-allowed'
                }`}
                title={image.hasImage ? `View ${image.label}` : `${image.label} - No image available`}
              />
            ))}
          </div>

          {/* Add to Cart / View Details Buttons */}
          {artwork.status === 'available' && (
            <div className="flex gap-2 mt-4">
              <button 
                className="flex-1 bg-mocha text-white px-4 py-2 rounded-lg hover:bg-mocha-600 transition-colors text-sm font-medium"
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  // Handle add to cart
                }}
              >
                Add to Cart
              </button>
              <button 
                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors text-sm font-medium"
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  // Handle quick view
                }}
              >
                Quick View
              </button>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
};

export default ArtworkCardShop;
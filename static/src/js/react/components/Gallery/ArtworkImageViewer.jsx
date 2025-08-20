import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const ArtworkImageViewer = ({ artwork = {}, isWishlisted = false, className = '' }) => {
  // Extract all 5 images (main + 4 frames)
  const allImages = [
    {
      id: 'main',
      url: artwork.gallery_url || artwork.main_image_url,
      thumbnailUrl: artwork.thumbnail_url,
      alt: `${artwork.title} - Main View`,
      label: 'Main'
    },
    {
      id: 'frame1',
      url: artwork.frame1_image_url,
      thumbnailUrl: artwork.frame1_image_url,
      alt: `${artwork.title} - Frame 1`,
      label: 'Frame 1'
    },
    {
      id: 'frame2',
      url: artwork.frame2_image_url,
      thumbnailUrl: artwork.frame2_image_url,
      alt: `${artwork.title} - Frame 2`,
      label: 'Frame 2'
    },
    {
      id: 'frame3',
      url: artwork.frame3_image_url,
      thumbnailUrl: artwork.frame3_image_url,
      alt: `${artwork.title} - Frame 3`,
      label: 'Frame 3'
    },
    {
      id: 'frame4',
      url: artwork.frame4_image_url,
      thumbnailUrl: artwork.frame4_image_url,
      alt: `${artwork.title} - Frame 4`,
      label: 'Frame 4'
    }
  ];

  // Set initial active image to main
  const [activeImageId, setActiveImageId] = useState('main');
  const [isLoading, setIsLoading] = useState(false);
  const [wishlistState, setWishlistState] = useState(isWishlisted);
  const [isWishlistLoading, setIsWishlistLoading] = useState(false);

  // Get currently active image
  const activeImage = allImages.find(img => img.id === activeImageId) || allImages[0];

  // Handle image selection
  const handleImageSelect = (imageId) => {
    const selectedImage = allImages.find(img => img.id === imageId);
    if (selectedImage && selectedImage.url) {
      setIsLoading(true);
      setActiveImageId(imageId);
    }
  };

  // Handle image load completion
  const handleImageLoad = () => {
    setIsLoading(false);
  };

  // Handle wishlist toggle
  const handleWishlistToggle = () => {
    if (isWishlistLoading || !window.toggleWishlist) return;
    
    setIsWishlistLoading(true);
    window.toggleWishlist(artwork.id, (response) => {
      setIsWishlistLoading(false);
      if (!response.error) {
        setWishlistState(response.added);
      }
    });
  };

  // Animation variants
  const imageVariants = {
    enter: {
      opacity: 0,
      scale: 1.05,
      transition: { duration: 0.3 }
    },
    center: {
      opacity: 1,
      scale: 1,
      transition: { duration: 0.3 }
    },
    exit: {
      opacity: 0,
      scale: 0.95,
      transition: { duration: 0.2 }
    }
  };

  const thumbnailVariants = {
    inactive: {
      scale: 1,
      opacity: 0.7
    },
    active: {
      scale: 1.05,
      opacity: 1
    },
    hover: {
      scale: 1.1,
      opacity: 1
    }
  };

  return (
    <div className={`flex gap-6 ${className}`}>
      {/* Thumbnail Column */}
      <div className="flex flex-col space-y-3 w-20">
        {allImages.map((image, index) => (
          <motion.button
            key={image.id}
            onClick={() => handleImageSelect(image.id)}
            className={`
              aspect-square rounded-lg overflow-hidden border-2 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2
              ${activeImageId === image.id 
                ? 'border-mocha shadow-lg' 
                : image.url 
                  ? 'border-neutral-200 hover:border-mocha cursor-pointer' 
                  : 'border-gray-100 cursor-not-allowed'
              }
            `}
            disabled={!image.url}
            variants={thumbnailVariants}
            initial="inactive"
            animate={activeImageId === image.id ? "active" : "inactive"}
            whileHover={image.url ? "hover" : "inactive"}
            whileTap={image.url ? { scale: 0.95 } : {}}
          >
            {image.url ? (
              <img 
                src={image.thumbnailUrl || image.url} 
                alt={image.alt}
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
            {activeImageId === image.id && (
              <motion.div
                className="absolute inset-0 rounded-lg border-2 border-mocha"
                layoutId="activeIndicator"
                transition={{ type: "spring", stiffness: 300, damping: 30 }}
              />
            )}
          </motion.button>
        ))}
      </div>

      {/* Main Image Display */}
      <div className="flex-1 relative">
        <div className="relative aspect-[4/5] rounded-2xl overflow-hidden shadow-soft bg-gray-100">
          <AnimatePresence mode="wait">
            <motion.img
              key={activeImageId}
              src={activeImage.url}
              alt={activeImage.alt}
              className="w-full h-full object-cover"
              variants={imageVariants}
              initial="enter"
              animate="center"
              exit="exit"
              onLoad={handleImageLoad}
            />
          </AnimatePresence>
          
          {/* Loading Overlay */}
          <AnimatePresence>
            {isLoading && (
              <motion.div
                className="absolute inset-0 bg-white/80 flex items-center justify-center"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-mocha"></div>
              </motion.div>
            )}
          </AnimatePresence>
          
          {/* Wishlist Button */}
          <motion.button
            onClick={handleWishlistToggle}
            disabled={isWishlistLoading}
            className={`absolute top-4 right-4 w-10 h-10 rounded-full flex items-center justify-center transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 ${
              wishlistState 
                ? 'bg-red-500 text-white hover:bg-red-600 focus:ring-red-500' 
                : 'bg-black/50 backdrop-blur-sm text-white hover:bg-black/70 focus:ring-white focus:ring-offset-black/50'
            }`}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            title={wishlistState ? 'Remove from Wishlist' : 'Add to Wishlist'}
          >
            {isWishlistLoading ? (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current"></div>
            ) : (
              <svg className="w-5 h-5" fill={wishlistState ? 'currentColor' : 'none'} stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"></path>
              </svg>
            )}
          </motion.button>

          {/* Image Counter */}
          <div className="absolute top-4 right-16 bg-black/50 backdrop-blur-sm rounded-full px-3 py-1 text-white text-sm font-medium">
            {allImages.findIndex(img => img.id === activeImageId) + 1} / {allImages.filter(img => img.url).length}
          </div>
          
          {/* Image Label */}
          <div className="absolute bottom-4 left-4 bg-black/50 backdrop-blur-sm rounded-lg px-3 py-2 text-white">
            <div className="text-sm font-medium">{activeImage.label}</div>
            {artwork.title && (
              <div className="text-xs opacity-90">{artwork.title}</div>
            )}
          </div>
        </div>
        
        {/* Navigation Arrows (optional) */}
        <div className="absolute top-1/2 -translate-y-1/2 left-4">
          <button
            onClick={() => {
              const currentIndex = allImages.findIndex(img => img.id === activeImageId);
              const availableImages = allImages.filter(img => img.url);
              const currentAvailableIndex = availableImages.findIndex(img => img.id === activeImageId);
              const prevIndex = currentAvailableIndex > 0 ? currentAvailableIndex - 1 : availableImages.length - 1;
              handleImageSelect(availableImages[prevIndex].id);
            }}
            className="w-10 h-10 bg-black/50 backdrop-blur-sm text-white rounded-full flex items-center justify-center hover:bg-black/70 transition-colors focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-black/50"
            disabled={allImages.filter(img => img.url).length <= 1}
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 19l-7-7 7-7"></path>
            </svg>
          </button>
        </div>
        
        <div className="absolute top-1/2 -translate-y-1/2 right-4">
          <button
            onClick={() => {
              const availableImages = allImages.filter(img => img.url);
              const currentAvailableIndex = availableImages.findIndex(img => img.id === activeImageId);
              const nextIndex = currentAvailableIndex < availableImages.length - 1 ? currentAvailableIndex + 1 : 0;
              handleImageSelect(availableImages[nextIndex].id);
            }}
            className="w-10 h-10 bg-black/50 backdrop-blur-sm text-white rounded-full flex items-center justify-center hover:bg-black/70 transition-colors focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-black/50"
            disabled={allImages.filter(img => img.url).length <= 1}
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7"></path>
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
};

export default ArtworkImageViewer;
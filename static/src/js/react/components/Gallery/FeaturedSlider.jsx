import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

// Component to handle individual artwork images with natural aspect ratios
const ArtworkImageContainer = ({ artwork, isCenter }) => {
    const [imageLoaded, setImageLoaded] = useState(false);
    const [imageDimensions, setImageDimensions] = useState({ width: 0, height: 0 });
    
    const targetWidth = isCenter ? 350 : 260;
    
    const handleImageLoad = (e) => {
        const img = e.target;
        const aspectRatio = img.naturalWidth / img.naturalHeight;
        const calculatedHeight = targetWidth / aspectRatio;
        
        setImageDimensions({ 
            width: targetWidth, 
            height: calculatedHeight 
        });
        setImageLoaded(true);
        
        // Add opacity transition
        img.classList.add('opacity-100');
        img.classList.remove('opacity-0');
    };
    
    const handleImageError = (e) => {
        // Fallback to next available image source
        if (isCenter && artwork.image_thumbnail) {
            e.target.src = artwork.image_thumbnail;
        } else if (artwork.image_url) {
            e.target.src = artwork.image_url;
        }
    };
    
    return (
        <div 
            className="relative overflow-hidden rounded-xl shadow-lg transition-all duration-300"
            style={{
                width: `${targetWidth}px`,
                height: imageLoaded ? `${imageDimensions.height}px` : `${targetWidth * 1.25}px`, // Default to 4:5 ratio
                flexShrink: 0
            }}
        >
            <img
                src={isCenter ? (artwork.image_gallery || artwork.image_thumbnail) : artwork.image_thumbnail}
                alt={artwork.alt_text || artwork.title}
                className="artwork-image w-full h-full object-cover opacity-0 transition-opacity duration-300"
                loading="eager"
                decoding="async"
                fetchpriority={isCenter ? "high" : "low"}
                style={{
                    backgroundColor: '#f3f4f6'
                }}
                onLoad={handleImageLoad}
                onError={handleImageError}
            />
            
            {/* Enhanced Gradient Overlay */}
            <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-transparent opacity-0 hover:opacity-100 transition-opacity duration-300">
            </div>
            
            {/* Fixed Position Info Overlay */}
            <div className={`absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-black/80 via-black/50 to-transparent text-white transition-all duration-300 ${
                isCenter ? 'opacity-100' : 'opacity-0 group-hover:opacity-100'
            }`}>
                <h3 className={`font-playfair font-semibold mb-1 line-clamp-2 ${
                    isCenter ? 'text-lg' : 'text-base'
                }`} style={{
                    textShadow: '2px 2px 4px rgba(0, 0, 0, 0.8), 1px 1px 2px rgba(0, 0, 0, 0.9)'
                }}>
                    {artwork.title}
                </h3>
                <p className={`opacity-90 ${
                    isCenter ? 'text-sm' : 'text-xs'
                }`} style={{
                    textShadow: '1px 1px 2px rgba(0, 0, 0, 0.8), 0px 0px 4px rgba(0, 0, 0, 0.6)'
                }}>
                    {artwork.medium} • {artwork.price_display}
                </p>
            </div>
            
        </div>
    );
};

const FeaturedSlider = ({ className = '' }) => {
    const [featuredArtworks, setFeaturedArtworks] = useState([]);
    const [currentIndex, setCurrentIndex] = useState(0);
    const [isLoading, setIsLoading] = useState(true);
    const [isPaused, setIsPaused] = useState(false);
    const [maxHeight, setMaxHeight] = useState(420); // Default height

    // Fetch featured artworks on component mount with performance optimizations
    useEffect(() => {
        const fetchFeaturedArtworks = async () => {
            try {
                // Optimized API call with minimal fields for performance
                const response = await fetch('/api/artworks/?featured=true&fields=id,title,slug,medium,price_display,image_thumbnail,image_gallery,image_url,alt_text,aspect_ratio', {
                    headers: {
                        'Accept': 'application/json',
                        'Cache-Control': 'max-age=600' // Cache for 10 minutes
                    }
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}`);
                }
                
                const data = await response.json();
                
                if (Array.isArray(data) && data.length > 0) {
                    // Aggressive preloading strategy for first 3 images
                    const preloadPromises = data.slice(0, 3).map((artwork, index) => {
                        return new Promise((resolve) => {
                            const img = new Image();
                            img.onload = resolve;
                            img.onerror = resolve; // Don't block on errors
                            // Use thumbnail for side images, gallery for center image
                            img.src = index === 0 ? artwork.image_gallery || artwork.image_thumbnail : artwork.image_thumbnail;
                        });
                    });
                    
                    // Set artworks immediately, don't wait for preloading
                    setFeaturedArtworks(data);
                    
                    // Calculate maximum height needed for all images
                    calculateMaxHeight(data);
                    
                    // Preload images in background
                    Promise.all(preloadPromises).then(() => {
                        console.log('Featured images preloaded');
                    });
                } else {
                    setFeaturedArtworks([]);
                }
            } catch (error) {
                console.warn('FeaturedSlider: API error:', error.message);
                setFeaturedArtworks([]);
            } finally {
                setIsLoading(false);
            }
        };

        fetchFeaturedArtworks();
    }, []);

    // Calculate the maximum height needed based on all featured artworks
    const calculateMaxHeight = async (artworks) => {
        const centerWidth = 350;
        const sideWidth = 260;
        let maxCenterHeight = 0;
        let maxSideHeight = 0;

        // Calculate heights for all artworks based on their aspect ratios
        const heightPromises = artworks.map(artwork => {
            return new Promise((resolve) => {
                const img = new Image();
                img.onload = () => {
                    const aspectRatio = img.naturalWidth / img.naturalHeight;
                    const centerHeight = centerWidth / aspectRatio;
                    const sideHeight = sideWidth / aspectRatio;
                    
                    resolve({ centerHeight, sideHeight });
                };
                img.onerror = () => {
                    // Fallback to default aspect ratio (4:5)
                    const centerHeight = centerWidth / 0.8;
                    const sideHeight = sideWidth / 0.8;
                    resolve({ centerHeight, sideHeight });
                };
                img.src = artwork.image_gallery || artwork.image_thumbnail || artwork.image_url;
            });
        });

        try {
            const heights = await Promise.all(heightPromises);
            
            heights.forEach(({ centerHeight, sideHeight }) => {
                maxCenterHeight = Math.max(maxCenterHeight, centerHeight);
                maxSideHeight = Math.max(maxSideHeight, sideHeight);
            });

            // Use the larger of center or side heights, plus padding
            const calculatedMaxHeight = Math.max(maxCenterHeight, maxSideHeight) + 80; // 80px for padding and controls
            
            // Set minimum of 420px, maximum of 600px for reasonable bounds
            const finalHeight = Math.max(420, Math.min(600, calculatedMaxHeight));
            
            setMaxHeight(finalHeight);
        } catch (error) {
            console.warn('Error calculating max height:', error);
            setMaxHeight(420); // Fallback to default
        }
    };

    // Preload adjacent images for smooth transitions
    useEffect(() => {
        if (featuredArtworks.length > 0) {
            const preloadImages = () => {
                // Preload next 2 images for smooth sliding
                for (let i = 1; i <= 2; i++) {
                    const nextIndex = (currentIndex + i) % featuredArtworks.length;
                    const artwork = featuredArtworks[nextIndex];
                    if (artwork && artwork.image_thumbnail) {
                        const img = new Image();
                        img.src = artwork.image_thumbnail;
                    }
                }
            };

            // Small delay to not block initial render
            const timeoutId = setTimeout(preloadImages, 100);
            return () => clearTimeout(timeoutId);
        }
    }, [currentIndex, featuredArtworks]);

    // Auto-advance slider
    useEffect(() => {
        if (!isPaused && featuredArtworks.length > 0) {
            const interval = setInterval(() => {
                setCurrentIndex((prevIndex) => 
                    (prevIndex + 1) % featuredArtworks.length
                );
            }, 4000); // 4 seconds between slides

            return () => clearInterval(interval);
        }
    }, [isPaused, featuredArtworks.length]);

    const goToSlide = (index) => {
        setCurrentIndex(index);
    };

    const goToPrevious = () => {
        setCurrentIndex((prevIndex) => 
            prevIndex === 0 ? featuredArtworks.length - 1 : prevIndex - 1
        );
    };

    const goToNext = () => {
        setCurrentIndex((prevIndex) => 
            (prevIndex + 1) % featuredArtworks.length
        );
    };

    // Get 5 artworks to display (2 left + center + 2 right) with position tracking
    const getDisplayArtworks = () => {
        if (featuredArtworks.length === 0) return [];
        
        const total = featuredArtworks.length;
        const artworks = [];
        
        // Show 5 artworks: 2 left + center + 2 right
        for (let i = -2; i <= 2; i++) {
            const index = (currentIndex + i + total) % total;
            artworks.push({
                ...featuredArtworks[index],
                position: i,
                isCenter: i === 0,
                slideId: `${featuredArtworks[index].id}-${currentIndex}-${i}` // Unique key for smooth transitions
            });
        }
        
        return artworks;
    };

    if (isLoading) {
        return (
            <div className={`featured-slider-loading ${className}`}>
                <div className="flex justify-center items-center" style={{ height: `${maxHeight}px` }}>
                    <div className="w-8 h-8 border-2 border-primary-200 border-t-primary-500 rounded-full animate-spin"></div>
                </div>
            </div>
        );
    }

    const displayArtworks = getDisplayArtworks();

    // Don't render anything if no featured artworks available
    if (featuredArtworks.length === 0) {
        return null;
    }

    return (
        <div 
            className={`featured-slider relative ${className}`}
            onMouseEnter={() => setIsPaused(true)}
            onMouseLeave={() => setIsPaused(false)}
        >
            {/* Dynamic Height Container based on largest images */}
            <div className="relative overflow-hidden" style={{ height: `${maxHeight}px` }}>
                <div className="flex items-center justify-center h-full">
                    {/* 5-Card Layout Container with consistent spacing */}
                    <div className="flex items-center justify-center space-x-6 w-full max-w-7xl mx-auto px-4">
                        <AnimatePresence mode="popLayout">
                            {displayArtworks.map((artwork) => (
                                <motion.div
                                    key={artwork.slideId}
                                    layout
                                    initial={{ 
                                        opacity: 0,
                                        x: artwork.position > 0 ? 100 : artwork.position < 0 ? -100 : 0
                                    }}
                                    animate={{ 
                                        opacity: artwork.isCenter ? 1 : 0.7,
                                        x: 0
                                    }}
                                    exit={{ 
                                        opacity: 0,
                                        x: artwork.position > 0 ? 100 : artwork.position < 0 ? -100 : 0
                                    }}
                                    transition={{ 
                                        duration: 0.5,
                                        ease: "easeInOut",
                                        layout: { duration: 0.5 }
                                    }}
                                    className={`artwork-slide cursor-pointer flex-shrink-0 group ${
                                        artwork.isCenter ? 'z-10' : 'z-0'
                                    }`}
                                    onClick={() => {
                                        if (artwork.isCenter) {
                                            // Navigate to artwork detail page using slug
                                            if (artwork.slug) {
                                                window.location.href = `/art/${artwork.slug}/`;
                                            }
                                        } else if (!artwork.isCenter) {
                                            goToSlide((currentIndex + artwork.position + featuredArtworks.length) % featuredArtworks.length);
                                        }
                                    }}
                                >
                                    <ArtworkImageContainer 
                                        artwork={artwork}
                                        isCenter={artwork.isCenter}
                                    />
                                </motion.div>
                            ))}
                        </AnimatePresence>
                    </div>
                </div>
            </div>

            {/* Dynamic Center Navigation Arrows */}
            <button
                className="absolute left-4 p-3 bg-gradient-to-r from-primary/90 to-primary/80 backdrop-blur-sm rounded-full text-white hover:from-primary hover:to-primary-600 hover:shadow-xl hover:scale-110 transition-all duration-300 z-30 shadow-lg"
                style={{ top: `${maxHeight / 2}px`, transform: 'translateY(-50%)' }} 
                onClick={goToPrevious}
                aria-label="Previous artwork"
            >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 19l-7-7 7-7"></path>
                </svg>
            </button>
            
            <button
                className="absolute right-4 p-3 bg-gradient-to-l from-primary/90 to-primary/80 backdrop-blur-sm rounded-full text-white hover:from-primary hover:to-primary-600 hover:shadow-xl hover:scale-110 transition-all duration-300 z-30 shadow-lg"
                style={{ top: `${maxHeight / 2}px`, transform: 'translateY(-50%)' }}
                onClick={goToNext}
                aria-label="Next artwork"
            >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7"></path>
                </svg>
            </button>
            
            
            {/* Progress Bar */}
            <div className="absolute bottom-0 left-0 right-0 h-1 bg-black/10 z-10">
                <motion.div 
                    className="h-full bg-gradient-to-r from-primary to-primary-600"
                    initial={{ width: 0 }}
                    animate={{ 
                        width: isPaused ? `${((currentIndex + 1) / featuredArtworks.length) * 100}%` : '100%' 
                    }}
                    transition={{ 
                        duration: isPaused ? 0.3 : 4,
                        ease: isPaused ? 'easeOut' : 'linear'
                    }}
                />
            </div>

        </div>
    );
};

export default FeaturedSlider;
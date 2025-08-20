import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const ArtworkShoppingCard = ({ 
  artwork, 
  user, 
  onAddToCart, 
  onWishlistToggle, 
  onImageClick, 
  className = '' 
}) => {
  const [selectedImage, setSelectedImage] = useState(0);
  const [selectedPrintOption, setSelectedPrintOption] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [showDetails, setShowDetails] = useState(false);
  const [actionFeedback, setActionFeedback] = useState(null);

  const allImages = useMemo(() => {
    const images = [artwork.main_image_url];
    if (artwork.detail_images) images.push(...artwork.detail_images);
    if (artwork.framed_images) images.push(...artwork.framed_images);
    if (artwork.lifestyle_images) images.push(...artwork.lifestyle_images);
    return images.filter(Boolean);
  }, [artwork]);

  useEffect(() => {
    if (artwork.prints_available && artwork.print_options?.length > 0) {
      setSelectedPrintOption(artwork.print_options[0]);
    }
  }, [artwork]);

  const handleImageSelect = useCallback((index) => {
    setSelectedImage(index);
    if (onImageClick) {
      onImageClick(allImages[index], index);
    }
  }, [allImages, onImageClick]);

  const handlePrintOptionChange = useCallback((option) => {
    setSelectedPrintOption(option);
  }, []);

  const handleAddToCart = useCallback(async (type = 'print') => {
    setIsLoading(true);
    try {
      const cartItem = type === 'original' 
        ? { artwork_id: artwork.id, type: 'original', price: artwork.original_price }
        : { 
            artwork_id: artwork.id, 
            type: 'print', 
            print_option: selectedPrintOption,
            price: selectedPrintOption?.price 
          };
      
      await onAddToCart(cartItem);
      setActionFeedback({ type: 'success', message: 'Added to cart!' });
      setTimeout(() => setActionFeedback(null), 3000);
    } catch (error) {
      setActionFeedback({ type: 'error', message: 'Failed to add to cart' });
      setTimeout(() => setActionFeedback(null), 3000);
    } finally {
      setIsLoading(false);
    }
  }, [artwork, selectedPrintOption, onAddToCart]);

  const handleWishlistToggle = useCallback(async () => {
    setIsLoading(true);
    try {
      await onWishlistToggle(artwork.id);
      setActionFeedback({ type: 'success', message: 'Wishlist updated!' });
      setTimeout(() => setActionFeedback(null), 3000);
    } catch (error) {
      setActionFeedback({ type: 'error', message: 'Failed to update wishlist' });
      setTimeout(() => setActionFeedback(null), 3000);
    } finally {
      setIsLoading(false);
    }
  }, [artwork.id, onWishlistToggle]);

  const isInWishlist = useMemo(() => {
    return user?.wishlist?.includes(artwork.id) || false;
  }, [user, artwork.id]);

  return (
    <div className={`artwork-shopping-card ${className}`}>
      <div className="artwork-shopping-card__container">
        {/* Image Viewer Section */}
        <ImageViewer
          images={allImages}
          selectedIndex={selectedImage}
          onImageSelect={handleImageSelect}
          artwork={artwork}
        />

        {/* Product Information Section */}
        <div className="artwork-shopping-card__info">
          <ProductInfo 
            artwork={artwork}
            showDetails={showDetails}
            onToggleDetails={() => setShowDetails(!showDetails)}
          />

          <PricingSelector
            artwork={artwork}
            selectedPrintOption={selectedPrintOption}
            onPrintOptionChange={handlePrintOptionChange}
          />

          <ActionButtons
            artwork={artwork}
            selectedPrintOption={selectedPrintOption}
            isLoading={isLoading}
            isInWishlist={isInWishlist}
            onAddToCart={handleAddToCart}
            onWishlistToggle={handleWishlistToggle}
            actionFeedback={actionFeedback}
          />

          <TrustIndicators />
        </div>
      </div>
    </div>
  );
};

const ImageViewer = ({ images, selectedIndex, onImageSelect, artwork }) => {
  const [isZoomed, setIsZoomed] = useState(false);

  return (
    <div className="image-viewer">
      <div className="image-viewer__main">
        <motion.img
          key={selectedIndex}
          src={images[selectedIndex]}
          alt={artwork.alt_text || `${artwork.title} by ${artwork.artist_name}`}
          className="image-viewer__main-image"
          onClick={() => setIsZoomed(true)}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.3 }}
          whileHover={{ scale: 1.02 }}
        />
        
        {images.length > 1 && (
          <div className="image-viewer__thumbnails">
            {images.map((image, index) => (
              <button
                key={index}
                className={`image-viewer__thumbnail ${
                  index === selectedIndex ? 'active' : ''
                }`}
                onClick={() => onImageSelect(index)}
                aria-label={`View image ${index + 1}`}
              >
                <img src={image} alt={`${artwork.title} view ${index + 1}`} />
              </button>
            ))}
          </div>
        )}
      </div>

      <AnimatePresence>
        {isZoomed && (
          <motion.div
            className="image-viewer__zoom-modal"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setIsZoomed(false)}
          >
            <motion.img
              src={images[selectedIndex]}
              alt={artwork.alt_text || `${artwork.title} by ${artwork.artist_name}`}
              className="image-viewer__zoom-image"
              initial={{ scale: 0.8 }}
              animate={{ scale: 1 }}
              exit={{ scale: 0.8 }}
            />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

const ProductInfo = ({ artwork, showDetails, onToggleDetails }) => {
  return (
    <div className="product-info">
      <div className="product-info__header">
        <h1 className="product-info__title">{artwork.title}</h1>
        <p className="product-info__artist">by {artwork.artist_name}</p>
      </div>

      <div className="product-info__specs">
        <span className="product-info__medium">{artwork.medium}</span>
        <span className="product-info__dimensions">
          {artwork.dimensions?.width}" × {artwork.dimensions?.height}"
        </span>
        <span className="product-info__year">{artwork.year_created}</span>
      </div>

      <div className="product-info__description">
        <p>{artwork.description}</p>
        
        {showDetails && artwork.story && (
          <motion.div
            className="product-info__story"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
          >
            <h4>Artist's Story</h4>
            <p>{artwork.story}</p>
          </motion.div>
        )}

        {artwork.story && (
          <button
            className="product-info__details-toggle"
            onClick={onToggleDetails}
          >
            {showDetails ? 'Less Details' : 'Read Artist\'s Story'}
          </button>
        )}
      </div>

      {artwork.tags && artwork.tags.length > 0 && (
        <div className="product-info__tags">
          {artwork.tags.map((tag, index) => (
            <span key={index} className="product-info__tag">
              {tag}
            </span>
          ))}
        </div>
      )}
    </div>
  );
};

const PricingSelector = ({ artwork, selectedPrintOption, onPrintOptionChange }) => {
  const bothAvailable = artwork.original_available && artwork.prints_available;
  const originalOnly = artwork.original_available && !artwork.prints_available;
  const printsOnly = !artwork.original_available && artwork.prints_available;

  return (
    <div className="pricing-selector">
      {(bothAvailable || originalOnly) && (
        <div className="pricing-selector__original">
          <h3>Original Artwork</h3>
          <div className="pricing-selector__price">
            ${artwork.original_price?.toLocaleString()}
          </div>
          {artwork.status === 'sold' && (
            <div className="pricing-selector__status sold">Sold</div>
          )}
          {artwork.edition_info && (
            <p className="pricing-selector__edition">{artwork.edition_info}</p>
          )}
        </div>
      )}

      {(bothAvailable || printsOnly) && artwork.print_options && (
        <div className="pricing-selector__prints">
          <h3>Prints Available</h3>
          <div className="pricing-selector__options">
            {artwork.print_options.map((option, index) => (
              <label key={index} className="pricing-selector__option">
                <input
                  type="radio"
                  name="print-option"
                  checked={selectedPrintOption?.size === option.size}
                  onChange={() => onPrintOptionChange(option)}
                />
                <div className="pricing-selector__option-info">
                  <span className="size">{option.size}</span>
                  <span className="material">{option.material}</span>
                  <span className="price">${option.price}</span>
                </div>
              </label>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

const ActionButtons = ({ 
  artwork, 
  selectedPrintOption, 
  isLoading, 
  isInWishlist, 
  onAddToCart, 
  onWishlistToggle,
  actionFeedback 
}) => {
  const canBuyOriginal = artwork.original_available && artwork.status === 'available';
  const canBuyPrints = artwork.prints_available && selectedPrintOption;

  return (
    <div className="action-buttons">
      <div className="action-buttons__primary">
        {canBuyOriginal && (
          <motion.button
            className="action-buttons__buy-original"
            onClick={() => onAddToCart('original')}
            disabled={isLoading}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            {isLoading ? 'Adding...' : 'Buy Original'}
          </motion.button>
        )}

        {canBuyPrints && (
          <motion.button
            className="action-buttons__add-print"
            onClick={() => onAddToCart('print')}
            disabled={isLoading}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            {isLoading ? 'Adding...' : 'Add Print to Cart'}
          </motion.button>
        )}
      </div>

      <div className="action-buttons__secondary">
        <motion.button
          className={`action-buttons__wishlist ${isInWishlist ? 'active' : ''}`}
          onClick={onWishlistToggle}
          disabled={isLoading}
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
        >
          <span className="heart-icon">♥</span>
          {isInWishlist ? 'In Wishlist' : 'Add to Wishlist'}
        </motion.button>

        <button className="action-buttons__share">
          Share
        </button>

        <button className="action-buttons__inquire">
          Inquire
        </button>
      </div>

      <AnimatePresence>
        {actionFeedback && (
          <motion.div
            className={`action-buttons__feedback ${actionFeedback.type}`}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
          >
            {actionFeedback.message}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

const TrustIndicators = () => {
  return (
    <div className="trust-indicators">
      <div className="trust-indicators__item">
        <span className="trust-indicators__icon">🎨</span>
        <span>Certificate of Authenticity</span>
      </div>
      <div className="trust-indicators__item">
        <span className="trust-indicators__icon">🔄</span>
        <span>30-Day Return Policy</span>
      </div>
      <div className="trust-indicators__item">
        <span className="trust-indicators__icon">🚚</span>
        <span>Free Shipping Over $100</span>
      </div>
      <div className="trust-indicators__item">
        <span className="trust-indicators__icon">🔒</span>
        <span>Secure Payment</span>
      </div>
    </div>
  );
};

export default ArtworkShoppingCard;
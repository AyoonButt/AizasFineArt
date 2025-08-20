import React, { useState, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const ArtworkImageManager = ({ 
  initialImages = {},
  onImagesChange,
  isEditing = false,
  className = ''
}) => {
  // State for all 5 images
  const [images, setImages] = useState({
    main: initialImages.main || null,
    frame1: initialImages.frame1 || null,
    frame2: initialImages.frame2 || null,
    frame3: initialImages.frame3 || null,
    frame4: initialImages.frame4 || null
  });

  // File input refs
  const fileInputs = {
    main: useRef(null),
    frame1: useRef(null),
    frame2: useRef(null),
    frame3: useRef(null),
    frame4: useRef(null)
  };

  // Current preview image
  const [currentPreview, setCurrentPreview] = useState('main');
  const [draggedOver, setDraggedOver] = useState(null);

  // Handle file selection
  const handleFileSelect = useCallback((imageType, file) => {
    if (file && file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const newImages = {
          ...images,
          [imageType]: {
            file: file,
            url: e.target.result,
            name: file.name
          }
        };
        setImages(newImages);
        if (onImagesChange) {
          onImagesChange(newImages);
        }
      };
      reader.readAsDataURL(file);
    }
  }, [images, onImagesChange]);

  // Handle drag and drop
  const handleDragOver = useCallback((e, imageType) => {
    e.preventDefault();
    setDraggedOver(imageType);
  }, []);

  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    setDraggedOver(null);
  }, []);

  const handleDrop = useCallback((e, imageType) => {
    e.preventDefault();
    setDraggedOver(null);
    
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFileSelect(imageType, files[0]);
    }
  }, [handleFileSelect]);

  // Remove image
  const removeImage = useCallback((imageType) => {
    const newImages = {
      ...images,
      [imageType]: null
    };
    setImages(newImages);
    if (onImagesChange) {
      onImagesChange(newImages);
    }
  }, [images, onImagesChange]);

  // Image slot configuration
  const imageSlots = [
    { key: 'main', label: 'Main Image', description: 'Primary artwork image' },
    { key: 'frame1', label: 'Frame 1', description: 'First frame variant' },
    { key: 'frame2', label: 'Frame 2', description: 'Second frame variant' },
    { key: 'frame3', label: 'Frame 3', description: 'Third frame variant' },
    { key: 'frame4', label: 'Frame 4', description: 'Fourth frame variant' }
  ];

  // Animation variants
  const containerVariants = {
    initial: { opacity: 0 },
    animate: { opacity: 1, transition: { staggerChildren: 0.1 } }
  };

  const itemVariants = {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 }
  };

  return (
    <motion.div 
      className={`artwork-image-manager ${className}`}
      variants={containerVariants}
      initial="initial"
      animate="animate"
    >
      {/* Preview Section */}
      <motion.div className="preview-section mb-8" variants={itemVariants}>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Image Preview</h3>
        <div className="preview-container relative bg-gray-50 rounded-lg overflow-hidden aspect-[4/3] max-w-2xl">
          {images[currentPreview] ? (
            <motion.img
              key={currentPreview}
              src={images[currentPreview].url || images[currentPreview]}
              alt={`${currentPreview} preview`}
              className="w-full h-full object-contain"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.3 }}
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-gray-400">
              <div className="text-center">
                <svg className="w-12 h-12 mx-auto mb-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" clipRule="evenodd" />
                </svg>
                <p>No image selected</p>
              </div>
            </div>
          )}
        </div>
        
        {/* Preview Navigation */}
        <div className="preview-nav flex gap-2 mt-4 flex-wrap">
          {imageSlots.map(({ key, label }) => (
            <button
              key={key}
              onClick={() => setCurrentPreview(key)}
              disabled={!images[key]}
              className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                currentPreview === key
                  ? 'bg-mocha text-white'
                  : images[key]
                    ? 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    : 'bg-gray-50 text-gray-400 cursor-not-allowed'
              }`}
            >
              {label}
            </button>
          ))}
        </div>
      </motion.div>

      {/* Upload Section */}
      <motion.div className="upload-section" variants={itemVariants}>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Image Uploads</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {imageSlots.map(({ key, label, description }) => (
            <motion.div 
              key={key}
              className="upload-slot"
              variants={itemVariants}
            >
              <input
                ref={fileInputs[key]}
                type="file"
                accept="image/*"
                className="sr-only"
                onChange={(e) => handleFileSelect(key, e.target.files[0])}
                name={`${key}_image_file`}
                required={false}
              />
              
              <div
                className={`upload-area relative border-2 border-dashed rounded-lg p-4 transition-all ${
                  draggedOver === key
                    ? 'border-lavender bg-lavender-50'
                    : images[key]
                      ? 'border-green-300 bg-green-50'
                      : 'border-gray-300 hover:border-gray-400'
                }`}
                onDragOver={(e) => handleDragOver(e, key)}
                onDragLeave={handleDragLeave}
                onDrop={(e) => handleDrop(e, key)}
              >
                {images[key] ? (
                  <div className="uploaded-image">
                    <img
                      src={images[key].url || images[key]}
                      alt={`${label} preview`}
                      className="w-full h-32 object-cover rounded-md mb-2"
                    />
                    <p className="text-sm text-gray-600 truncate mb-2">
                      {images[key].name || 'Uploaded image'}
                    </p>
                    <div className="flex gap-2">
                      <button
                        type="button"
                        onClick={() => fileInputs[key].current?.click()}
                        className="text-xs px-2 py-1 bg-gray-100 hover:bg-gray-200 rounded transition-colors"
                      >
                        Replace
                      </button>
                      <button
                        type="button"
                        onClick={() => removeImage(key)}
                        className="text-xs px-2 py-1 bg-red-100 hover:bg-red-200 text-red-700 rounded transition-colors"
                      >
                        Remove
                      </button>
                    </div>
                  </div>
                ) : (
                  <div 
                    className="upload-prompt text-center cursor-pointer"
                    onClick={() => fileInputs[key].current?.click()}
                  >
                    <svg className="w-8 h-8 mx-auto mb-2 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" clipRule="evenodd" />
                    </svg>
                    <p className="text-sm font-medium text-gray-600 mb-1">
                      {label} {key === 'main' && !isEditing && <span className="text-red-500">*</span>}
                    </p>
                    <p className="text-xs text-gray-500 mb-2">{description}</p>
                    <p className="text-xs text-gray-400">Click or drag to upload</p>
                  </div>
                )}
              </div>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* Instructions */}
      <motion.div className="instructions mt-6 p-4 bg-blue-50 rounded-lg" variants={itemVariants}>
        <h4 className="text-sm font-medium text-blue-900 mb-2">Upload Guidelines</h4>
        <ul className="text-xs text-blue-800 space-y-1">
          <li>• {isEditing ? 'Main image can be updated (optional)' : 'Main image is required'} - this will be the primary display image</li>
          <li>• Frame images show the artwork in different frame styles or contexts</li>
          <li>• Supported formats: JPG, PNG, WebP (max 10MB each)</li>
          <li>• Recommended resolution: 1200px or larger for best quality</li>
        </ul>
      </motion.div>
    </motion.div>
  );
};

export default ArtworkImageManager;
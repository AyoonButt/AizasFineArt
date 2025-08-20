import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import ArtworkImageManager from './ArtworkImageManager';

const ArtworkForm = ({ 
  initialData = {},
  categories = [],
  series = [],
  tags = [],
  onSubmit,
  isEditing = false,
  className = ''
}) => {
  // Form state
  const [formData, setFormData] = useState({
    title: '',
    category: '',
    series: '',
    medium: '',
    dimensions_width: '',
    dimensions_height: '',
    year_created: new Date().getFullYear(),
    description: '',
    inspiration: '',
    technique_notes: '',
    story: '',
    original_price: '',
    type: 'original',
    edition_info: '',
    meta_description: '',
    alt_text: '',
    tags: [],
    is_featured: false,
    is_active: true,
    ...initialData
  });

  // Image state - use preview URLs for display, but keep track of existing URLs
  const [images, setImages] = useState({
    main: initialData.main_image_preview || initialData.main_image_url || null,
    frame1: initialData.frame1_image_preview || initialData.frame1_image_url || null,
    frame2: initialData.frame2_image_preview || initialData.frame2_image_url || null,
    frame3: initialData.frame3_image_preview || initialData.frame3_image_url || null,
    frame4: initialData.frame4_image_preview || initialData.frame4_image_url || null,
  });

  // Form validation errors
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Handle input changes
  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  // Handle tag selection
  const handleTagChange = (tagId) => {
    setFormData(prev => ({
      ...prev,
      tags: prev.tags.includes(tagId)
        ? prev.tags.filter(id => id !== tagId)
        : [...prev.tags, tagId]
    }));
  };

  // Handle image changes
  const handleImagesChange = (newImages) => {
    setImages(newImages);
  };

  // Validate form
  const validateForm = () => {
    const newErrors = {};

    if (!formData.title.trim()) {
      newErrors.title = 'Title is required';
    }

    if (!formData.category) {
      newErrors.category = 'Category is required';
    }

    if (!formData.medium) {
      newErrors.medium = 'Medium is required';
    }

    if (!formData.dimensions_width || formData.dimensions_width <= 0) {
      newErrors.dimensions_width = 'Valid width is required';
    }

    if (!formData.dimensions_height || formData.dimensions_height <= 0) {
      newErrors.dimensions_height = 'Valid height is required';
    }

    if (!formData.year_created || formData.year_created < 1900 || formData.year_created > new Date().getFullYear()) {
      newErrors.year_created = 'Valid year is required';
    }

    if (!formData.description.trim()) {
      newErrors.description = 'Description is required';
    }

    // Only require main image for new artworks, not when editing existing ones
    if (!isEditing && !images.main) {
      newErrors.main_image = 'Main image is required';
    }

    if (formData.type === 'original' && (!formData.original_price || formData.original_price <= 0)) {
      newErrors.original_price = 'Original price is required when artwork type is "original"';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Remove any required attributes from hidden file inputs to prevent browser validation
    document.querySelectorAll('input[type="file"][name*="_image_file"]').forEach(input => {
      input.removeAttribute('required');
      input.required = false;
    });
    
    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);

    try {
      const formDataToSubmit = new FormData();

      // Add text fields - only include fields that are in the Django form
      const allowedFields = [
        'title', 'category', 'series', 'medium', 'dimensions_width', 
        'dimensions_height', 'year_created', 'description', 'inspiration', 
        'technique_notes', 'story', 'original_price', 'type', 'edition_info', 
        'meta_description', 'alt_text', 'tags', 'is_featured', 'is_active',
        'main_image_url', 'frame1_image_url', 'frame2_image_url', 
        'frame3_image_url', 'frame4_image_url'
      ];
      
      Object.keys(formData).forEach(key => {
        if (!allowedFields.includes(key)) {
          return; // Skip fields not in Django form
        }
        
        if (key === 'tags') {
          formData.tags.forEach(tagId => {
            formDataToSubmit.append('tags', tagId);
          });
        } else {
          formDataToSubmit.append(key, formData[key]);
        }
      });

      // Add image files
      if (images.main?.file) {
        formDataToSubmit.append('main_image_file', images.main.file);
      }
      if (images.frame1?.file) {
        formDataToSubmit.append('frame1_image_file', images.frame1.file);
      }
      if (images.frame2?.file) {
        formDataToSubmit.append('frame2_image_file', images.frame2.file);
      }
      if (images.frame3?.file) {
        formDataToSubmit.append('frame3_image_file', images.frame3.file);
      }
      if (images.frame4?.file) {
        formDataToSubmit.append('frame4_image_file', images.frame4.file);
      }

      if (onSubmit) {
        await onSubmit(formDataToSubmit);
      }
    } catch (error) {
      console.error('Form submission error:', error);
      setErrors({ submit: 'An error occurred while saving the artwork.' });
    } finally {
      setIsSubmitting(false);
    }
  };

  // Medium choices
  const mediumChoices = [
    { value: 'watercolor', label: 'Watercolor' },
    { value: 'oil', label: 'Oil' },
    { value: 'mixed', label: 'Mixed Media' },
    { value: 'digital', label: 'Digital' },
    { value: 'acrylic', label: 'Acrylic' }
  ];

  // Type choices
  const typeChoices = [
    { value: 'original', label: 'Original' },
    { value: 'print', label: 'Print' },
    { value: 'gallery', label: 'Gallery' }
  ];

  return (
    <motion.form 
      className={`artwork-form ${className}`}
      onSubmit={handleSubmit}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="space-y-8">
        {/* Image Management Section */}
        <section>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Artwork Images</h2>
          <ArtworkImageManager
            initialImages={images}
            onImagesChange={handleImagesChange}
            isEditing={isEditing}
          />
          {errors.main_image && (
            <p className="mt-2 text-sm text-red-600">{errors.main_image}</p>
          )}
        </section>

        {/* Basic Information */}
        <section className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div>
            <h3 className="text-lg font-medium text-gray-900 mb-4">Basic Information</h3>
            
            <div className="space-y-4">
              <div>
                <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
                  Title <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  id="title"
                  name="title"
                  value={formData.title}
                  onChange={handleInputChange}
                  className="form-input w-full"
                  placeholder="Enter artwork title"
                />
                {errors.title && <p className="mt-1 text-sm text-red-600">{errors.title}</p>}
              </div>

              <div>
                <label htmlFor="category" className="block text-sm font-medium text-gray-700 mb-1">
                  Category <span className="text-red-500">*</span>
                </label>
                <select
                  id="category"
                  name="category"
                  value={formData.category}
                  onChange={handleInputChange}
                  className="form-select w-full"
                >
                  <option value="">Select category...</option>
                  {categories.map(cat => (
                    <option key={cat.id} value={cat.id}>{cat.name}</option>
                  ))}
                </select>
                {errors.category && <p className="mt-1 text-sm text-red-600">{errors.category}</p>}
              </div>

              <div>
                <label htmlFor="series" className="block text-sm font-medium text-gray-700 mb-1">
                  Series
                </label>
                <select
                  id="series"
                  name="series"
                  value={formData.series}
                  onChange={handleInputChange}
                  className="form-select w-full"
                >
                  <option value="">Select series...</option>
                  {series.filter(s => s.category == formData.category).map(ser => (
                    <option key={ser.id} value={ser.id}>{ser.name}</option>
                  ))}
                </select>
              </div>

              <div>
                <label htmlFor="medium" className="block text-sm font-medium text-gray-700 mb-1">
                  Medium <span className="text-red-500">*</span>
                </label>
                <select
                  id="medium"
                  name="medium"
                  value={formData.medium}
                  onChange={handleInputChange}
                  className="form-select w-full"
                >
                  <option value="">Select medium...</option>
                  {mediumChoices.map(med => (
                    <option key={med.value} value={med.value}>{med.label}</option>
                  ))}
                </select>
                {errors.medium && <p className="mt-1 text-sm text-red-600">{errors.medium}</p>}
              </div>
            </div>
          </div>

          <div>
            <h3 className="text-lg font-medium text-gray-900 mb-4">Details</h3>
            
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label htmlFor="dimensions_width" className="block text-sm font-medium text-gray-700 mb-1">
                    Width (inches) <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="number"
                    id="dimensions_width"
                    name="dimensions_width"
                    value={formData.dimensions_width}
                    onChange={handleInputChange}
                    step="0.01"
                    className="form-input w-full"
                    placeholder="0.00"
                  />
                  {errors.dimensions_width && <p className="mt-1 text-sm text-red-600">{errors.dimensions_width}</p>}
                </div>
                
                <div>
                  <label htmlFor="dimensions_height" className="block text-sm font-medium text-gray-700 mb-1">
                    Height (inches) <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="number"
                    id="dimensions_height"
                    name="dimensions_height"
                    value={formData.dimensions_height}
                    onChange={handleInputChange}
                    step="0.01"
                    className="form-input w-full"
                    placeholder="0.00"
                  />
                  {errors.dimensions_height && <p className="mt-1 text-sm text-red-600">{errors.dimensions_height}</p>}
                </div>
              </div>

              <div>
                <label htmlFor="year_created" className="block text-sm font-medium text-gray-700 mb-1">
                  Year Created <span className="text-red-500">*</span>
                </label>
                <input
                  type="number"
                  id="year_created"
                  name="year_created"
                  value={formData.year_created}
                  onChange={handleInputChange}
                  className="form-input w-full"
                  min="1900"
                  max={new Date().getFullYear()}
                />
                {errors.year_created && <p className="mt-1 text-sm text-red-600">{errors.year_created}</p>}
              </div>

              <div>
                <label htmlFor="type" className="block text-sm font-medium text-gray-700 mb-1">
                  Type
                </label>
                <select
                  id="type"
                  name="type"
                  value={formData.type}
                  onChange={handleInputChange}
                  className="form-select w-full"
                >
                  {typeChoices.map(type => (
                    <option key={type.value} value={type.value}>{type.label}</option>
                  ))}
                </select>
              </div>
            </div>
          </div>
        </section>

        {/* Descriptions */}
        <section>
          <h3 className="text-lg font-medium text-gray-900 mb-4">Descriptions</h3>
          
          <div className="space-y-4">
            <div>
              <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
                Description <span className="text-red-500">*</span>
              </label>
              <textarea
                id="description"
                name="description"
                value={formData.description}
                onChange={handleInputChange}
                rows={4}
                className="form-textarea w-full"
                placeholder="Describe the artwork..."
              />
              {errors.description && <p className="mt-1 text-sm text-red-600">{errors.description}</p>}
            </div>

            <div>
              <label htmlFor="inspiration" className="block text-sm font-medium text-gray-700 mb-1">
                Inspiration
              </label>
              <textarea
                id="inspiration"
                name="inspiration"
                value={formData.inspiration}
                onChange={handleInputChange}
                rows={3}
                className="form-textarea w-full"
                placeholder="What inspired this piece?"
              />
            </div>

            <div>
              <label htmlFor="story" className="block text-sm font-medium text-gray-700 mb-1">
                Personal Story
              </label>
              <textarea
                id="story"
                name="story"
                value={formData.story}
                onChange={handleInputChange}
                rows={4}
                className="form-textarea w-full"
                placeholder="Personal story behind the artwork..."
              />
            </div>
          </div>
        </section>

        {/* Pricing */}
        {formData.type === 'original' && (
          <section>
            <h3 className="text-lg font-medium text-gray-900 mb-4">Pricing</h3>
            
            <div>
              <label htmlFor="original_price" className="block text-sm font-medium text-gray-700 mb-1">
                Original Price (USD) <span className="text-red-500">*</span>
              </label>
              <input
                type="number"
                id="original_price"
                name="original_price"
                value={formData.original_price}
                onChange={handleInputChange}
                step="0.01"
                className="form-input w-full"
                placeholder="0.00"
              />
              {errors.original_price && <p className="mt-1 text-sm text-red-600">{errors.original_price}</p>}
            </div>
          </section>
        )}

        {/* Tags */}
        <section>
          <h3 className="text-lg font-medium text-gray-900 mb-4">Tags</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
            {tags.map(tag => (
              <label key={tag.id} className="flex items-center">
                <input
                  type="checkbox"
                  checked={formData.tags.includes(tag.id)}
                  onChange={() => handleTagChange(tag.id)}
                  className="form-checkbox text-mocha"
                />
                <span className="ml-2 text-sm text-gray-700">{tag.name}</span>
              </label>
            ))}
          </div>
        </section>

        {/* Submit Button */}
        <div className="flex items-center justify-between pt-4 border-t">
          <div className="flex items-center space-x-4">
            <label className="flex items-center">
              <input
                type="checkbox"
                name="is_featured"
                checked={formData.is_featured}
                onChange={handleInputChange}
                className="form-checkbox"
              />
              <span className="ml-2 text-sm text-gray-700">Featured artwork</span>
            </label>
            
            <label className="flex items-center">
              <input
                type="checkbox"
                name="is_active"
                checked={formData.is_active}
                onChange={handleInputChange}
                className="form-checkbox"
              />
              <span className="ml-2 text-sm text-gray-700">Active</span>
            </label>
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="btn btn-primary"
          >
            {isSubmitting ? 'Saving...' : (isEditing ? 'Update Artwork' : 'Create Artwork')}
          </button>
        </div>

        {errors.submit && (
          <div className="p-3 bg-red-50 border border-red-200 rounded-md">
            <p className="text-sm text-red-600">{errors.submit}</p>
          </div>
        )}
      </div>
    </motion.form>
  );
};

export default ArtworkForm;
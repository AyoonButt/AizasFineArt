/**
 * Artwork Admin JavaScript enhancements
 */

(function($) {
    'use strict';

    $(document).ready(function() {
        // Initialize all enhancements
        initSeriesFiltering();
        initImagePreviewHandlers();
        initFormValidation();
        initPriceValidation();
        initSlugGeneration();
        fixImageFileInputs();
    });

    /**
     * Dynamic Series filtering based on Category selection
     */
    function initSeriesFiltering() {
        const categoryField = $('#id_category');
        const seriesField = $('#id_series');
        
        if (categoryField.length && seriesField.length) {
            categoryField.change(function() {
                const categoryId = $(this).val();
                
                if (categoryId) {
                    // Show loading state
                    seriesField.prop('disabled', true).html('<option>Loading...</option>');
                    
                    // Fetch series for the selected category
                    $.ajax({
                        url: '/admin/artwork/series/',
                        data: {
                            'category': categoryId,
                            'format': 'json'
                        },
                        success: function(data) {
                            seriesField.html('<option value="">---------</option>');
                            
                            if (data.length > 0) {
                                $.each(data, function(index, series) {
                                    seriesField.append(
                                        '<option value="' + series.id + '">' + series.name + '</option>'
                                    );
                                });
                            }
                            
                            seriesField.prop('disabled', false);
                        },
                        error: function() {
                            seriesField.html('<option value="">Error loading series</option>');
                            seriesField.prop('disabled', false);
                        }
                    });
                } else {
                    seriesField.html('<option value="">---------</option>').prop('disabled', false);
                }
            });
        }
    }

    /**
     * Image upload preview handlers
     */
    function initImagePreviewHandlers() {
        const imageFields = [
            'main_image_file',
            'frame1_image_file', 
            'frame2_image_file',
            'frame3_image_file',
            'frame4_image_file'
        ];

        imageFields.forEach(function(fieldName) {
            const fileInput = $('#id_' + fieldName);
            
            if (fileInput.length) {
                fileInput.change(function(e) {
                    handleImagePreview(e.target, fieldName);
                });
            }
        });
    }

    /**
     * Handle image preview for uploaded files
     */
    function handleImagePreview(input, fieldName) {
        const file = input.files[0];
        const previewContainer = $(input).closest('.form-row').find('.image-preview');
        
        if (file) {
            // Validate file
            if (!isValidImageFile(file)) {
                alert('Please select a valid image file (JPG, PNG, or WebP)');
                $(input).val('');
                return;
            }
            
            if (file.size > 10 * 1024 * 1024) { // 10MB
                alert('File size must be less than 10MB');
                $(input).val('');
                return;
            }
            
            // Create preview
            const reader = new FileReader();
            reader.onload = function(e) {
                let preview = previewContainer;
                
                if (!preview.length) {
                    preview = $('<div class="image-preview" style="margin-top: 10px;"></div>');
                    $(input).closest('.form-row').append(preview);
                }
                
                preview.html(
                    '<img src="' + e.target.result + '" alt="Preview" style="max-width: 200px; max-height: 200px; border: 2px solid #e5e7eb; border-radius: 8px;" />' +
                    '<div style="margin-top: 5px; font-size: 12px; color: #6b7280;">Preview of ' + fieldName.replace('_', ' ').replace('file', '') + '</div>'
                );
            };
            reader.readAsDataURL(file);
        } else {
            // Remove preview if no file selected
            $(input).closest('.form-row').find('.image-preview').remove();
        }
    }

    /**
     * Validate image file type
     */
    function isValidImageFile(file) {
        const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
        return validTypes.includes(file.type);
    }

    /**
     * Form validation enhancements
     */
    function initFormValidation() {
        const form = $('form');
        
        form.submit(function(e) {
            let isValid = true;
            const errors = [];
            
            // Validate required fields
            const title = $('#id_title').val().trim();
            if (!title) {
                errors.push('Title is required');
                $('#id_title').addClass('error');
                isValid = false;
            }
            
            const category = $('#id_category').val();
            if (!category) {
                errors.push('Category is required');
                $('#id_category').addClass('error');
                isValid = false;
            }
            
            const year = $('#id_year_created').val();
            if (!year || year < 1900 || year > new Date().getFullYear() + 1) {
                errors.push('Please enter a valid year');
                $('#id_year_created').addClass('error');
                isValid = false;
            }
            
            // Validate dimensions
            const width = parseFloat($('#id_dimensions_width').val());
            const height = parseFloat($('#id_dimensions_height').val());
            
            if (!width || width <= 0) {
                errors.push('Width must be greater than 0');
                $('#id_dimensions_width').addClass('error');
                isValid = false;
            }
            
            if (!height || height <= 0) {
                errors.push('Height must be greater than 0');
                $('#id_dimensions_height').addClass('error');
                isValid = false;
            }
            
            if (!isValid) {
                e.preventDefault();
                alert('Please fix the following errors:\n\n' + errors.join('\n'));
                
                // Scroll to first error
                const firstError = $('.error').first();
                if (firstError.length) {
                    $('html, body').animate({
                        scrollTop: firstError.offset().top - 100
                    }, 500);
                }
            }
        });
        
        // Remove error styling on input
        $('input, select, textarea').on('input change', function() {
            $(this).removeClass('error');
        });
    }

    /**
     * Price validation based on availability
     */
    function initPriceValidation() {
        const originalAvailable = $('#id_original_available');
        const originalPrice = $('#id_original_price');
        
        function togglePriceRequirement() {
            if (originalAvailable.is(':checked')) {
                originalPrice.prop('required', true);
                originalPrice.closest('.form-row').find('label').addClass('required');
            } else {
                originalPrice.prop('required', false);
                originalPrice.closest('.form-row').find('label').removeClass('required');
            }
        }
        
        originalAvailable.change(togglePriceRequirement);
        togglePriceRequirement(); // Initial call
    }

    /**
     * Auto-generate slug from title
     */
    function initSlugGeneration() {
        const titleField = $('#id_title');
        const slugField = $('#id_slug');
        
        if (titleField.length && slugField.length) {
            titleField.on('input', function() {
                if (!slugField.val()) { // Only auto-generate if slug is empty
                    const slug = generateSlug($(this).val());
                    slugField.val(slug);
                }
            });
        }
    }

    /**
     * Generate URL-friendly slug from text
     */
    function generateSlug(text) {
        return text
            .toLowerCase()
            .trim()
            .replace(/[^\w\s-]/g, '') // Remove special characters
            .replace(/[\s_-]+/g, '-') // Replace spaces and underscores with hyphens
            .replace(/^-+|-+$/g, ''); // Remove leading/trailing hyphens
    }

    /**
     * Add visual feedback for form state
     */
    $(document).on('input change', 'input, select, textarea', function() {
        const field = $(this);
        
        // Add 'modified' class for visual feedback
        if (field.val() !== field.prop('defaultValue')) {
            field.addClass('modified');
        } else {
            field.removeClass('modified');
        }
    });

    /**
     * Fix image file input validation issues
     */
    function fixImageFileInputs() {
        const imageFileInputs = [
            '#id_main_image_file',
            '#id_frame1_image_file', 
            '#id_frame2_image_file',
            '#id_frame3_image_file',
            '#id_frame4_image_file'
        ];

        imageFileInputs.forEach(function(selector) {
            const input = $(selector);
            if (input.length) {
                // Ensure these inputs are never marked as required
                input.removeAttr('required');
                input.prop('required', false);
                
                // Remove any hidden class that might cause focus issues
                input.removeClass('hidden');
                
                // Set proper accept attribute
                input.attr('accept', '.jpg,.jpeg,.png,.webp');
                
                // Add data attribute to mark as optional
                input.attr('data-required', 'false');
                
                // Prevent any external scripts from making these required
                input.on('DOMNodeInserted', function() {
                    $(this).removeAttr('required').prop('required', false);
                });
            }
        });
        
        // Also check for any hidden file inputs and fix them
        $('input[type="file"][name*="image_file"].hidden').each(function() {
            $(this).removeClass('hidden');
            $(this).removeAttr('required');
            $(this).prop('required', false);
        });
    }

})(django.jQuery);
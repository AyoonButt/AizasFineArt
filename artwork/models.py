from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.contrib.auth.models import User
from PIL import Image
import os
import uuid


class Tag(models.Model):
    """Tags for artwork categorization and filtering"""
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    color = models.CharField(max_length=7, default='#6B7280', help_text="Hex color for tag display")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name


class PrintOption(models.Model):
    """Print size and material options for artworks"""
    artwork = models.ForeignKey('Artwork', on_delete=models.CASCADE, related_name='print_options')
    size = models.CharField(max_length=20, help_text="e.g., '8x10', '11x14', '16x20'")
    material = models.CharField(max_length=50, help_text="e.g., 'Fine Art Paper', 'Canvas Print'")
    price = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.TextField(blank=True, help_text="Additional details about this print option")
    is_available = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['artwork', 'display_order', 'price']
        unique_together = ['artwork', 'size', 'material']
    
    def __str__(self):
        return f"{self.artwork.title} - {self.size} {self.material} (${self.price})"


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['display_order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('artwork:category_detail', kwargs={'slug': self.slug})


class Series(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='series')
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Series"
        ordering = ['display_order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.category.name} - {self.name}"

    def get_absolute_url(self):
        return reverse('artwork:series_detail', kwargs={'category_slug': self.category.slug, 'slug': self.slug})


class Artwork(models.Model):
    MEDIUM_CHOICES = [
        ('watercolor', 'Watercolor'),
        ('oil', 'Oil'),
        ('mixed', 'Mixed Media'),
        ('digital', 'Digital'),
        ('acrylic', 'Acrylic'),
    ]

    TYPE_CHOICES = [
        ('original', 'Original'),
        ('print', 'Print'),
        ('gallery', 'Gallery'),
    ]
    

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='artworks')
    series = models.ForeignKey(Series, on_delete=models.SET_NULL, null=True, blank=True, related_name='artworks')
    
    # Artwork details
    medium = models.CharField(max_length=20, choices=MEDIUM_CHOICES)
    dimensions_width = models.DecimalField(max_digits=6, decimal_places=2, help_text="Width in inches")
    dimensions_height = models.DecimalField(max_digits=6, decimal_places=2, help_text="Height in inches")
    year_created = models.PositiveIntegerField()
    
    # Descriptions
    description = models.TextField()
    inspiration = models.TextField(blank=True, help_text="Story behind the artwork")
    technique_notes = models.TextField(blank=True, help_text="Technical details about creation")
    
    # Pricing and availability
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Price for original artwork (required when type is 'original')")
    original_available = models.BooleanField(default=True, help_text="Whether the original artwork is available for purchase")
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='original', help_text="Artwork type - Original, Print, or Gallery")
    edition_info = models.CharField(max_length=200, blank=True, help_text="Edition information (limited edition, etc.)")
    
    # Artist story and personal connection
    story = models.TextField(blank=True, help_text="Personal story behind the artwork")
    
    # Images - 5 specific images (1 main + 4 frames)
    main_image_url = models.URLField(default='https://via.placeholder.com/800x600?text=Artwork', help_text="Primary artwork image URL")
    frame1_image_url = models.URLField(blank=True, default='', help_text="First frame variant image URL")
    frame2_image_url = models.URLField(blank=True, default='', help_text="Second frame variant image URL")
    frame3_image_url = models.URLField(blank=True, default='', help_text="Third frame variant image URL")
    frame4_image_url = models.URLField(blank=True, default='', help_text="Fourth frame variant image URL")
    
    # Cached resolved URLs (to avoid API calls during template rendering)
    _cached_image_url = models.TextField(blank=True, default='', help_text="Cached resolved image URL")
    _cached_thumbnail_url = models.TextField(blank=True, default='', help_text="Cached thumbnail URL")
    _cached_frame_urls = models.JSONField(default=dict, blank=True, help_text="Cached frame image URLs")  
    _url_cache_expires = models.DateTimeField(null=True, blank=True, help_text="When cached URLs expire")
    
    # SEO and metadata
    meta_description = models.CharField(max_length=160, blank=True)
    alt_text = models.CharField(max_length=125, blank=True, help_text="Alt text for primary image")
    
    # Additional metadata
    lumaprints_product_id = models.CharField(max_length=100, blank=True, help_text="Lumaprints product ID for prints")
    views = models.PositiveIntegerField(default=0)
    favorites = models.PositiveIntegerField(default=0, help_text="Number of times added to wishlist")
    
    # Tags for filtering and discovery
    tags = models.ManyToManyField('Tag', blank=True, related_name='artworks')
    
    # Management
    display_order = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_featured', 'display_order', '-created_at']

    def clean(self):
        from django.core.exceptions import ValidationError
        
        # Validate original_price is required for original artworks
        if self.type == 'original' and not self.original_price:
            raise ValidationError({'original_price': 'Original price is required when artwork type is "original".'})
    
    def save(self, *args, **kwargs):
        # Check if this is an update and if LumaPrints sync is needed
        is_update = self.pk is not None
        needs_luma_sync = False
        old_instance = None
        
        # For updates, get the old instance to compare key fields
        if is_update:
            try:
                old_instance = Artwork.objects.get(pk=self.pk)
                # Check if key LumaPrints fields changed
                luma_sync_fields = ['title', 'description', 'main_image_url', 'type', 'is_active']
                needs_luma_sync = any(
                    getattr(self, field) != getattr(old_instance, field)
                    for field in luma_sync_fields
                )
                
                # Handle type changes
                old_type = old_instance.type
                new_type = self.type
                
                # If changing FROM print to something else, delete LumaPrints product
                if old_type == 'print' and new_type != 'print' and old_instance.lumaprints_product_id:
                    self._handle_type_change('delete_product', old_instance)
                
                # If changing TO print from something else, create LumaPrints product
                elif old_type != 'print' and new_type == 'print':
                    needs_luma_sync = True  # Force sync for new print conversion
                    
            except Artwork.DoesNotExist:
                pass
        
        # Only run full_clean if we're not bypassing validation (for supabase URLs)
        skip_validation = kwargs.pop('skip_validation', False)
        if not skip_validation:
            # Temporarily store supabase URLs and replace with dummy URLs for validation
            supabase_urls = {}
            for field in ['main_image_url', 'frame1_image_url', 'frame2_image_url', 'frame3_image_url', 'frame4_image_url']:
                value = getattr(self, field)
                if value and value.startswith('supabase://'):
                    supabase_urls[field] = value
                    setattr(self, field, 'https://example.com/temp.jpg')
            
            # Run model validation with dummy URLs
            self.full_clean()
            
            # Restore the actual supabase URLs
            for field, url in supabase_urls.items():
                setattr(self, field, url)
        
        if not self.slug:
            self.slug = slugify(f"{self.title}-{self.year_created}")
        
        # Ensure slug uniqueness
        if Artwork.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
            self.slug = f"{self.slug}-{self.pk or 'new'}"
        
        super().save(*args, **kwargs)
        
        # TEMPORARILY DISABLED: LumaPrints sync was causing Django startup hangs
        # Re-enable after debugging server startup issues
        # Handle LumaPrints synchronization after save
        # if self.type == 'print' and needs_luma_sync:
        #     if self.lumaprints_product_id:
        #         # Update existing product
        #         self._sync_with_lumaprints('update')
        #     else:
        #         # Create new product (new artwork or type conversion)
        #         self._sync_with_lumaprints('create')

    def delete(self, *args, **kwargs):
        """Override delete to handle LumaPrints cleanup"""
        # TEMPORARILY DISABLED: LumaPrints sync was causing issues
        # Delete from LumaPrints if it's a print artwork
        # if self.type == 'print' and self.lumaprints_product_id:
        #     self._sync_with_lumaprints('delete')
        
        super().delete(*args, **kwargs)
    
    def _sync_with_lumaprints(self, action):
        """Handle LumaPrints synchronization in background thread"""
        try:
            import threading
            
            def sync_operation():
                """Background thread to sync with LumaPrints"""
                try:
                    from orders.luma_prints_api import (
                        create_luma_prints_product, 
                        update_luma_prints_product, 
                        delete_luma_prints_product
                    )
                    
                    if action == 'create':
                        result = create_luma_prints_product(self)
                        if result['status'] == 'success':
                            print(f"✓ Created LumaPrints product for '{self.title}' - ID: {result.get('product_id')}")
                        else:
                            print(f"⚠ Failed to create LumaPrints product for '{self.title}': {result.get('message')}")
                    
                    elif action == 'update':
                        result = update_luma_prints_product(self)
                        if result['status'] == 'success':
                            print(f"✓ Updated LumaPrints product for '{self.title}' - ID: {result.get('product_id')}")
                        else:
                            print(f"⚠ Failed to update LumaPrints product for '{self.title}': {result.get('message')}")
                    
                    elif action == 'delete':
                        result = delete_luma_prints_product(self)
                        if result['status'] == 'success':
                            print(f"✓ Deleted LumaPrints product for '{self.title}'")
                        else:
                            print(f"⚠ Failed to delete LumaPrints product for '{self.title}': {result.get('message')}")
                            
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"LumaPrints sync error for artwork '{self.title}' (ID: {self.id}): {str(e)}")
            
            # Start background sync thread
            thread = threading.Thread(target=sync_operation, daemon=True)
            thread.start()
            
        except Exception:
            # Don't fail the main operation if sync fails
            pass
    
    def _handle_type_change(self, action, old_instance):
        """Handle LumaPrints operations when artwork type changes"""
        try:
            import threading
            
            def type_change_operation():
                """Background thread to handle type change"""
                try:
                    from orders.luma_prints_api import delete_luma_prints_product
                    
                    if action == 'delete_product':
                        # Delete product when converting from print to non-print
                        result = delete_luma_prints_product(old_instance)
                        if result['status'] == 'success':
                            print(f"✓ Deleted LumaPrints product for '{old_instance.title}' (type changed to {self.type})")
                        else:
                            print(f"⚠ Failed to delete LumaPrints product for '{old_instance.title}': {result.get('message')}")
                            
                except Exception as e:
                    print(f"⚠ LumaPrints type change error for '{old_instance.title}': {str(e)}")
            
            # Start background operation thread
            thread = threading.Thread(target=type_change_operation, daemon=True)
            thread.start()
            
        except Exception:
            # Don't fail the main operation if sync fails
            pass

    def get_image(self, size='gallery', expires_in=86400):  # Extended to 24 hours
        """Get signed URL for private bucket with transformations and optimized caching"""
        if not self.main_image_url:
            return None
            
        try:
            from utils.supabase_client import supabase_storage
            
            # Handle private bucket URLs (supabase://)
            if self.main_image_url.startswith('supabase://'):
                file_path = self.main_image_url.replace('supabase://', '')
                
                # Optimized size configs for faster loading
                size_configs = {
                    'thumbnail': {'width': 300, 'height': 300, 'quality': 70, 'format': 'webp'},  # Reduced quality for speed
                    'small': {'width': 500, 'height': 500, 'quality': 75, 'format': 'webp'},     # Reduced quality for speed  
                    'medium': {'width': 600, 'height': 600, 'quality': 80, 'format': 'webp'},    # Smaller size & quality
                    'large': {'width': 1000, 'height': 1000, 'quality': 85, 'format': 'webp'},  # Smaller size
                    'gallery': {'width': 800, 'height': 600, 'quality': 80, 'format': 'webp'},   # Smaller & faster for carousel
                    'detail': {'width': 1600, 'height': 1200, 'quality': 95, 'format': 'origin'},
                    'social': {'width': 1200, 'height': 630, 'quality': 85, 'format': 'webp'},  # Open Graph
                }
                
                config = size_configs.get(size, {'width': 800, 'height': 800, 'quality': 85, 'format': 'webp'})
                return supabase_storage.get_transformed_url(
                    file_path, 
                    expires_in=expires_in,
                    **config
                )
            
            # Handle legacy public URLs
            elif 'supabase.co/storage' in self.main_image_url:
                file_path = self.main_image_url.split('/public/artwork-images/')[-1]
                # Use same optimized size configs as private URLs
                size_configs = {
                    'thumbnail': {'width': 300, 'height': 300, 'quality': 70, 'format': 'webp'},  # Reduced quality for speed
                    'small': {'width': 500, 'height': 500, 'quality': 75, 'format': 'webp'},     # Reduced quality for speed  
                    'medium': {'width': 600, 'height': 600, 'quality': 80, 'format': 'webp'},    # Smaller size & quality
                    'large': {'width': 1000, 'height': 1000, 'quality': 85, 'format': 'webp'},  # Smaller size
                    'gallery': {'width': 800, 'height': 600, 'quality': 80, 'format': 'webp'},   # Smaller & faster for carousel
                    'detail': {'width': 1600, 'height': 1200, 'quality': 95, 'format': 'origin'},
                    'social': {'width': 1200, 'height': 630, 'quality': 85, 'format': 'webp'},
                }
                config = size_configs.get(size, {'width': 800, 'height': 800, 'quality': 85, 'format': 'webp'})
                return supabase_storage.get_transformed_url(
                    file_path, 
                    expires_in=expires_in,
                    **config
                )
            
        except Exception as e:
            print(f"Image URL generation error: {e}")
        
        # Return original URL if not Supabase or transformation failed
        return self.main_image_url
    
    def get_simple_signed_url(self, expires_in=3600):  # Restored to production timeout
        """Get signed URL with just-in-time refresh when expired - enhanced with nonce and validation"""
        if not self.main_image_url:
            return None
            
        # If not a Supabase URL, return as-is
        if not self.main_image_url.startswith('supabase://'):
            return self.main_image_url
            
        from django.utils import timezone
        from utils.supabase_client import supabase_storage
        now = timezone.now()
        
        # Ultra-aggressive caching for sub-3s performance: skip validation if cache is fresh
        if (self._cached_image_url and self._url_cache_expires and 
            now < (self._url_cache_expires - timezone.timedelta(minutes=5))):
            # Return cached URL immediately without validation for maximum speed
            return self._cached_image_url
        
        # Cache expired, invalid, or missing - generate fresh URL with unique expiry for uniqueness
        try:
            file_path = self.main_image_url.replace('supabase://', '')
            
            # Use unique expiry time to ensure URL uniqueness and avoid deterministic signing
            unique_expires_in = supabase_storage.generate_unique_expiry(expires_in)
            signed_url_response = supabase_storage.client.storage.from_(supabase_storage.bucket).create_signed_url(
                file_path, 
                unique_expires_in
            )
            
            if signed_url_response and 'signedURL' in signed_url_response:
                cached_url = signed_url_response['signedURL']
                
                # Update cache
                self._cached_image_url = cached_url
                # Cache for safe buffer before token expiry (50 minutes for 60-minute tokens)
                self._url_cache_expires = now + timezone.timedelta(minutes=50)
                
                # Save cache to database (ignore failures - will regenerate next time)
                try:
                    self.save(update_fields=['_cached_image_url', '_url_cache_expires'])
                except Exception:
                    pass  # Continue if save fails - URL is still valid
                
                return cached_url
                
        except Exception as e:
            # Log error but continue with fallback
            print(f"Supabase URL generation failed for {self.main_image_url}: {e}")
            
            # Fallback: Try with standard expiry
            try:
                file_path = self.main_image_url.replace('supabase://', '')
                signed_url_response = supabase_storage.client.storage.from_(supabase_storage.bucket).create_signed_url(file_path, expires_in)
                
                if signed_url_response and 'signedURL' in signed_url_response:
                    return signed_url_response['signedURL']
                    
            except Exception:
                pass  # Silent fallback failure
            
        # Final fallback: return original URL
        return self.main_image_url
    
    # Removed _schedule_background_refresh - using simple just-in-time refresh instead
    
    # Removed _schedule_frame_refresh - using simple just-in-time refresh instead
    
    # Cache metrics removed - simpler just-in-time refresh doesn't need complex tracking
    
    def get_cached_thumbnail_url(self, expires_in=3600):
        """Get cached thumbnail URL with just-in-time refresh"""
        if not self.main_image_url:
            return None
            
        # Use the same just-in-time refresh system as simple signed URLs
        # This provides caching benefits and automatic refresh when expired
        return self.get_simple_signed_url(expires_in)
    
    @property
    def image_url(self):
        """Get displayable URL for templates - optimized thumbnails for shop/gallery"""
        # Use cached thumbnail URL with fallback to simple signed URL
        return self.get_cached_thumbnail_url()
    
    @property
    def thumbnail_url(self):
        """Get thumbnail URL for templates"""
        # Use cached thumbnail URL for performance
        return self.get_cached_thumbnail_url()
    
    def get_frame_simple_url(self, frame_num):
        """Get frame URL with just-in-time refresh when expired - enhanced with nonce and validation"""
        frame_url = getattr(self, f'frame{frame_num}_image_url', '')
        if not frame_url:
            return None
            
        # If not a Supabase URL, return as-is
        if not frame_url.startswith('supabase://'):
            return frame_url
            
        from django.utils import timezone
        from utils.supabase_client import supabase_storage
        now = timezone.now()
        cache_key = f'frame{frame_num}'
        
        # Two-tier validation: time-based AND URL accessibility
        if (self._cached_frame_urls and cache_key in self._cached_frame_urls and 
            self._url_cache_expires and now < (self._url_cache_expires - timezone.timedelta(minutes=10))):
            # Time-based check passed, now test URL accessibility
            if supabase_storage.validate_signed_url(self._cached_frame_urls[cache_key]):
                return self._cached_frame_urls[cache_key]
            else:
                # URL validation failed - cached URL is no longer accessible
                pass
        
        # Cache expired, invalid, or missing - generate fresh URL with unique expiry for uniqueness
        try:
            file_path = frame_url.replace('supabase://', '')
            
            # Use unique expiry time to ensure URL uniqueness and avoid deterministic signing
            unique_expires_in = supabase_storage.generate_unique_expiry(3600)
            signed_url_response = supabase_storage.client.storage.from_(supabase_storage.bucket).create_signed_url(
                file_path, 
                unique_expires_in
            )
            
            if signed_url_response and 'signedURL' in signed_url_response:
                cached_url = signed_url_response['signedURL']
                
                # Update cache
                if not self._cached_frame_urls:
                    self._cached_frame_urls = {}
                self._cached_frame_urls[cache_key] = cached_url
                
                # Cache for safe buffer before token expiry (50 minutes for 60-minute tokens)
                self._url_cache_expires = now + timezone.timedelta(minutes=50)
                
                # Save cache to database (ignore failures - will regenerate next time)
                try:
                    self.save(update_fields=['_cached_frame_urls', '_url_cache_expires'])
                except Exception:
                    pass  # Continue if save fails - URL is still valid
                
                return cached_url
                
        except Exception as e:
            # Log error but continue with fallback
            print(f"Frame URL generation failed for {frame_url}: {e}")
            
            # Fallback: Try with standard expiry
            try:
                file_path = frame_url.replace('supabase://', '')
                signed_url_response = supabase_storage.client.storage.from_(supabase_storage.bucket).create_signed_url(file_path, 3600)
                
                if signed_url_response and 'signedURL' in signed_url_response:
                    return signed_url_response['signedURL']
                    
            except Exception:
                pass  # Silent fallback failure
            
        # Final fallback
        return None
    
    @property
    def gallery_url(self):
        """Get gallery size URL for templates"""
        # TEMPORARILY DISABLED: Supabase calls causing Django startup hangs
        # return self.get_image('gallery')
        return self.main_image_url  # Return raw URL for now
    
    # Removed refresh_url_cache - no longer needed with just-in-time refresh
    
    def get_frame_image(self, frame_num, size='gallery', expires_in=86400):  # Extended to 24 hours
        """Get signed URL for frame image with transformations and optimized caching"""
        frame_url = getattr(self, f'frame{frame_num}_image_url', '')
        if not frame_url:
            return None
            
        try:
            from utils.supabase_client import supabase_storage
            
            # Handle private bucket URLs (supabase://)
            if frame_url.startswith('supabase://'):
                file_path = frame_url.replace('supabase://', '')
                
                # Use same optimized size configs as main image
                size_configs = {
                    'thumbnail': {'width': 300, 'height': 300, 'quality': 70, 'format': 'webp'},  # Reduced quality for speed
                    'small': {'width': 500, 'height': 500, 'quality': 75, 'format': 'webp'},     # Reduced quality for speed  
                    'medium': {'width': 600, 'height': 600, 'quality': 80, 'format': 'webp'},    # Smaller size & quality
                    'large': {'width': 1000, 'height': 1000, 'quality': 85, 'format': 'webp'},  # Smaller size
                    'gallery': {'width': 800, 'height': 600, 'quality': 80, 'format': 'webp'},   # Smaller & faster for carousel
                    'detail': {'width': 1600, 'height': 1200, 'quality': 95, 'format': 'origin'},
                    'social': {'width': 1200, 'height': 630, 'quality': 85, 'format': 'webp'},
                }
                
                config = size_configs.get(size, {'width': 800, 'height': 800, 'quality': 85, 'format': 'webp'})
                return supabase_storage.get_transformed_url(
                    file_path, 
                    expires_in=expires_in,
                    **config
                )
            
            # Handle legacy public URLs
            elif 'supabase.co/storage' in frame_url:
                file_path = frame_url.split('/public/artwork-images/')[-1]
                # Use same optimized size configs as main image
                size_configs = {
                    'thumbnail': {'width': 300, 'height': 300, 'quality': 70, 'format': 'webp'},  # Reduced quality for speed
                    'small': {'width': 500, 'height': 500, 'quality': 75, 'format': 'webp'},     # Reduced quality for speed  
                    'medium': {'width': 600, 'height': 600, 'quality': 80, 'format': 'webp'},    # Smaller size & quality
                    'large': {'width': 1000, 'height': 1000, 'quality': 85, 'format': 'webp'},  # Smaller size
                    'gallery': {'width': 800, 'height': 600, 'quality': 80, 'format': 'webp'},   # Smaller & faster for carousel
                    'detail': {'width': 1600, 'height': 1200, 'quality': 95, 'format': 'origin'},
                    'social': {'width': 1200, 'height': 630, 'quality': 85, 'format': 'webp'},
                }
                config = size_configs.get(size, {'width': 800, 'height': 800, 'quality': 85, 'format': 'webp'})
                return supabase_storage.get_transformed_url(
                    file_path, 
                    expires_in=expires_in,
                    **config
                )
            
        except Exception as e:
            print(f"Frame image URL generation error: {e}")
        
        # Return original URL if not Supabase or transformation failed
        return frame_url

    @property
    def all_images(self):
        """Get all 5 artwork images in order (main + 4 frames)"""
        images = []
        if self.main_image_url:
            images.append(self.main_image_url)
        if self.frame1_image_url:
            images.append(self.frame1_image_url)
        if self.frame2_image_url:
            images.append(self.frame2_image_url)
        if self.frame3_image_url:
            images.append(self.frame3_image_url)
        if self.frame4_image_url:
            images.append(self.frame4_image_url)
        return images
    
    @property
    def all_images_transformed(self):
        """Get all images with proper URL transformation"""
        images = []
        
        # Add main image
        main_img = self.get_image('gallery')
        if main_img:
            images.append(main_img)
        
        # Add frame images
        for i in range(1, 5):
            frame_img = self.get_frame_image(i, 'gallery')
            if frame_img:
                images.append(frame_img)
        
        return images
    
    @property
    def all_images_thumbnails(self):
        """Get all images as thumbnails with proper URL transformation"""
        images = []
        
        # Add main image thumbnail
        main_thumb = self.get_image('thumbnail')
        if main_thumb:
            images.append(main_thumb)
        
        # Add frame image thumbnails
        for i in range(1, 5):
            frame_thumb = self.get_frame_image(i, 'thumbnail')
            if frame_thumb:
                images.append(frame_thumb)
        
        return images
    
    @property
    def frame_images(self):
        """Get just the 4 frame images"""
        frames = []
        if self.frame1_image_url:
            frames.append(self.frame1_image_url)
        if self.frame2_image_url:
            frames.append(self.frame2_image_url)
        if self.frame3_image_url:
            frames.append(self.frame3_image_url)
        if self.frame4_image_url:
            frames.append(self.frame4_image_url)
        return frames
    
    @property
    def artist_name(self):
        """Return artist name (default to Aiza)"""
        return "Aiza"
    
    @property
    def dimensions(self):
        """Return dimensions as dict for template access"""
        return {
            'width': float(self.dimensions_width),
            'height': float(self.dimensions_height),
            'unit': 'inches'
        }
    
    @property
    def aspect_ratio(self):
        """Calculate aspect ratio for responsive layouts"""
        if self.dimensions_width and self.dimensions_height:
            return float(self.dimensions_width) / float(self.dimensions_height)
        return 1.0

    def __str__(self):
        return f"{self.title} ({self.year_created})"

    def get_absolute_url(self):
        # Primary detail URL for individual artwork pages (full details)
        if self.category:
            return reverse('artwork:detail', kwargs={'category_slug': self.category.slug, 'slug': self.slug})
        return f"/artwork/uncategorized/{self.slug}/"
    
    def get_display_url(self):
        # Display URL for gallery view (full-resolution image focus)
        if self.category:
            return reverse('artwork:display', kwargs={'category_slug': self.category.slug, 'slug': self.slug})
        return f"/artwork/display/uncategorized/{self.slug}/"

    @property
    def dimensions_display(self):
        return f"{self.dimensions_width}\" × {self.dimensions_height}\""

    def is_original_available(self):
        """Check if original artwork is available for purchase"""
        return self.type == 'original' and self.original_price is not None and self.original_available

    @property
    def prints_available(self):
        """Check if prints are available for this artwork"""
        # Prints are available if there are print options OR lumaprints product ID
        return self.print_options.filter(is_available=True).exists() or bool(self.lumaprints_product_id)

    @property
    def is_available(self):
        return self.is_original_available() or self.prints_available

    @property
    def price_display(self):
        if self.original_price:
            return f"${self.original_price:,.0f}"
        return "Price on request"


class ArtworkView(models.Model):
    """Track artwork page views for analytics"""
    artwork = models.ForeignKey(Artwork, on_delete=models.CASCADE, related_name='artwork_views')
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    referrer = models.URLField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['artwork', 'timestamp']),
        ]


class ArtworkInquiry(models.Model):
    """Handle inquiries about specific artworks"""
    artwork = models.ForeignKey(Artwork, on_delete=models.CASCADE, related_name='inquiries')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    message = models.TextField()
    inquiry_type = models.CharField(max_length=20, choices=[
        ('purchase', 'Purchase Inquiry'),
        ('general', 'General Question'),
        ('print', 'Print Inquiry'),
    ], default='general')
    
    is_responded = models.BooleanField(default=False)
    response_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Inquiry about {self.artwork.title} from {self.name}"


# UserProfile, Wishlist, Order, and OrderItem models belong in their respective apps


class CacheMetric(models.Model):
    """Tracks cache performance metrics"""
    
    METRIC_TYPES = [
        ('hit', 'Cache Hit'),
        ('miss', 'Cache Miss'),
        ('warming_success', 'Cache Warming Success'),
        ('warming_failure', 'Cache Warming Failure'),
        ('refresh_proactive', 'Proactive Refresh'),
        ('refresh_reactive', 'Reactive Refresh'),
        ('api_call', 'External API Call'),
        ('thread_pool_task', 'Thread Pool Task'),
    ]
    
    metric_type = models.CharField(max_length=20, choices=METRIC_TYPES)
    artwork_id = models.IntegerField(null=True, blank=True)
    response_time_ms = models.FloatField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['metric_type', 'timestamp']),
            models.Index(fields=['artwork_id', 'timestamp']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"{self.metric_type} - {self.timestamp}"
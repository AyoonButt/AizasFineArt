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

    def get_image(self, size='gallery', expires_in=86400):  # Extended to 24 hours
        """Get signed URL for private bucket with transformations and optimized caching"""
        if not self.main_image_url:
            return None
            
        try:
            from utils.supabase_client import supabase_storage
            
            # Handle private bucket URLs (supabase://)
            if self.main_image_url.startswith('supabase://'):
                file_path = self.main_image_url.replace('supabase://', '')
                
                # Optimized size configs with better quality settings
                size_configs = {
                    'thumbnail': {'width': 300, 'height': 300, 'quality': 75, 'format': 'webp'},
                    'small': {'width': 500, 'height': 500, 'quality': 80, 'format': 'webp'},
                    'medium': {'width': 800, 'height': 800, 'quality': 85, 'format': 'webp'},
                    'large': {'width': 1200, 'height': 1200, 'quality': 90, 'format': 'webp'},
                    'gallery': {'width': 1200, 'height': 800, 'quality': 90, 'format': 'webp'},
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
                    'thumbnail': {'width': 300, 'height': 300, 'quality': 75, 'format': 'webp'},
                    'small': {'width': 500, 'height': 500, 'quality': 80, 'format': 'webp'},
                    'medium': {'width': 800, 'height': 800, 'quality': 85, 'format': 'webp'},
                    'large': {'width': 1200, 'height': 1200, 'quality': 90, 'format': 'webp'},
                    'gallery': {'width': 1200, 'height': 800, 'quality': 90, 'format': 'webp'},
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
    
    @property
    def image_url(self):
        """Get displayable URL for templates - automatically handles supabase:// URLs"""
        return self.get_image('medium')
    
    @property
    def thumbnail_url(self):
        """Get thumbnail URL for templates"""
        return self.get_image('thumbnail')
    
    @property
    def gallery_url(self):
        """Get gallery size URL for templates"""
        return self.get_image('gallery')
    
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
                    'thumbnail': {'width': 300, 'height': 300, 'quality': 75, 'format': 'webp'},
                    'small': {'width': 500, 'height': 500, 'quality': 80, 'format': 'webp'},
                    'medium': {'width': 800, 'height': 800, 'quality': 85, 'format': 'webp'},
                    'large': {'width': 1200, 'height': 1200, 'quality': 90, 'format': 'webp'},
                    'gallery': {'width': 1200, 'height': 800, 'quality': 90, 'format': 'webp'},
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
                    'thumbnail': {'width': 300, 'height': 300, 'quality': 75, 'format': 'webp'},
                    'small': {'width': 500, 'height': 500, 'quality': 80, 'format': 'webp'},
                    'medium': {'width': 800, 'height': 800, 'quality': 85, 'format': 'webp'},
                    'large': {'width': 1200, 'height': 1200, 'quality': 90, 'format': 'webp'},
                    'gallery': {'width': 1200, 'height': 800, 'quality': 90, 'format': 'webp'},
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
        # Primary detail URL for individual artwork pages
        return reverse('artwork_detail', kwargs={'slug': self.slug})

    @property
    def dimensions_display(self):
        return f"{self.dimensions_width}\" × {self.dimensions_height}\""

    @property
    def original_available(self):
        """Check if original artwork is available for purchase"""
        return self.type == 'original' and self.original_price is not None

    @property
    def prints_available(self):
        """Check if prints are available for this artwork"""
        # Prints are available if there are print options OR lumaprints product ID
        return self.print_options.filter(is_available=True).exists() or bool(self.lumaprints_product_id)

    @property
    def is_available(self):
        return self.original_available or self.prints_available

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
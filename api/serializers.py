from rest_framework import serializers
from artwork.models import Artwork, Category
from userprofiles.models import UserWishlist
from blog.models import BlogPost
from orders.models import Cart, CartItem


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']


class ArtworkListSerializer(serializers.ModelSerializer):
    """Serializer for artwork list view with basic image support"""
    category = CategorySerializer(read_only=True)
    image_thumbnail = serializers.SerializerMethodField()
    image_gallery = serializers.SerializerMethodField() 
    image_url = serializers.SerializerMethodField()
    price_display = serializers.SerializerMethodField()
    aspect_ratio = serializers.SerializerMethodField()
    
    class Meta:
        model = Artwork
        fields = [
            'id', 'title', 'slug', 'category', 'medium', 'year_created',
            'original_price', 'price_display', 'is_featured', 'dimensions_width', 'dimensions_height',
            'image_thumbnail', 'image_gallery', 'image_url',
            'aspect_ratio', 'alt_text', 'views'
        ]
    
    def get_image_thumbnail(self, obj):
        """Get cached image URL for thumbnails - fast performance"""
        return obj.get_simple_signed_url()
    
    def get_image_gallery(self, obj):
        """Get cached image URL for gallery - fast performance"""
        return obj.get_simple_signed_url()
    
    def get_image_url(self, obj):
        """Get cached image URL - fast performance"""
        return obj.get_simple_signed_url()
    
    def get_price_display(self, obj):
        if obj.original_price:
            return f"${obj.original_price:,.0f}"
        return "Price on request"
    
    def get_aspect_ratio(self, obj):
        if obj.dimensions_width and obj.dimensions_height:
            return float(obj.dimensions_width) / float(obj.dimensions_height)
        return 1.25


class ArtworkDetailSerializer(serializers.ModelSerializer):
    """Serializer for artwork detail view with 5-image support"""
    category = CategorySerializer(read_only=True)
    image_detail = serializers.SerializerMethodField()
    image_gallery = serializers.SerializerMethodField()
    image_social = serializers.SerializerMethodField()
    price_display = serializers.ReadOnlyField()
    dimensions_display = serializers.ReadOnlyField()
    aspect_ratio = serializers.ReadOnlyField()
    is_available = serializers.ReadOnlyField()
    all_images = serializers.ReadOnlyField()  # Raw URLs for reference
    all_images_transformed = serializers.ReadOnlyField()  # Transformed URLs for display
    all_images_thumbnails = serializers.ReadOnlyField()  # Thumbnail URLs for navigation
    frame_images = serializers.ReadOnlyField()  # Raw frame URLs
    
    class Meta:
        model = Artwork
        fields = [
            'id', 'title', 'slug', 'category', 'description', 'inspiration',
            'technique_notes', 'story', 'medium', 'dimensions_width', 'dimensions_height',
            'dimensions_display', 'year_created', 'original_price', 'price_display',
            'is_available', 'is_featured', 'type',
            'image_detail', 'image_gallery', 'image_social', 
            'main_image_url', 'frame1_image_url', 'frame2_image_url', 'frame3_image_url', 'frame4_image_url',
            'all_images', 'all_images_transformed', 'all_images_thumbnails', 'frame_images',
            'alt_text', 'meta_description', 'views', 'aspect_ratio'
        ]
    
    def get_image_detail(self, obj):
        return obj.get_image('detail')
    
    def get_image_gallery(self, obj):
        return obj.get_image('gallery')
    
    def get_image_social(self, obj):
        return obj.get_image('social')


class WishlistSerializer(serializers.ModelSerializer):
    """Serializer for wishlist items"""
    artwork = ArtworkListSerializer(read_only=True)
    
    class Meta:
        model = UserWishlist
        fields = ['id', 'artwork', 'notes', 'created_at']


class BlogPostListSerializer(serializers.ModelSerializer):
    """Serializer for blog post list"""
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    reading_time = serializers.ReadOnlyField()
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'slug', 'excerpt', 'featured_image_url',
            'featured_image_alt', 'author_name', 'category_name',
            'is_featured', 'reading_time', 'published_at', 'created_at'
        ]


class BlogPostDetailSerializer(serializers.ModelSerializer):
    """Serializer for blog post detail"""
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    reading_time = serializers.ReadOnlyField()
    category_name = serializers.CharField(source='category.name', read_only=True)
    next_post = serializers.SerializerMethodField()
    previous_post = serializers.SerializerMethodField()
    
    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'slug', 'content', 'excerpt', 
            'featured_image_url', 'featured_image_alt', 'featured_image_caption',
            'gallery_images', 'author_name', 'category_name',
            'tags', 'is_featured', 'reading_time', 'published_at',
            'meta_description', 'next_post', 'previous_post'
        ]
    
    def get_next_post(self, obj):
        next_post = obj.get_next_post()
        if next_post:
            return {
                'title': next_post.title,
                'slug': next_post.slug,
                'excerpt': next_post.excerpt
            }
        return None
    
    def get_previous_post(self, obj):
        previous_post = obj.get_previous_post()
        if previous_post:
            return {
                'title': previous_post.title,
                'slug': previous_post.slug,
                'excerpt': previous_post.excerpt
            }
        return None


class NewsletterSignupSerializer(serializers.Serializer):
    """Serializer for newsletter signup"""
    email = serializers.EmailField()
    name = serializers.CharField(max_length=100, required=False)
    gdpr_consent = serializers.BooleanField(default=True)
    
    def validate_email(self, value):
        # Additional email validation if needed
        return value.lower()


class ContactFormSerializer(serializers.Serializer):
    """Serializer for contact form"""
    name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    subject = serializers.CharField(max_length=200)
    message = serializers.CharField()
    form_type = serializers.ChoiceField(
        choices=[
            ('general', 'General Inquiry'),
            ('press', 'Press Inquiry'),
            ('purchase', 'Purchase Inquiry')
        ],
        default='general'
    )
    phone = serializers.CharField(max_length=20, required=False)


class CartItemSerializer(serializers.ModelSerializer):
    """Serializer for cart items"""
    artwork = ArtworkListSerializer(read_only=True)
    total_price = serializers.ReadOnlyField()
    item_type_display = serializers.ReadOnlyField()
    
    class Meta:
        model = CartItem
        fields = [
            'id', 'artwork', 'item_type', 'item_type_display', 
            'quantity', 'unit_price', 'total_price', 'created_at'
        ]


class CartSerializer(serializers.ModelSerializer):
    """Serializer for shopping cart"""
    items = CartItemSerializer(many=True, read_only=True)
    subtotal = serializers.ReadOnlyField()
    shipping_cost = serializers.ReadOnlyField()
    total = serializers.ReadOnlyField()
    item_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Cart
        fields = [
            'id', 'items', 'subtotal', 'shipping_cost', 'total', 
            'item_count', 'created_at', 'updated_at'
        ]
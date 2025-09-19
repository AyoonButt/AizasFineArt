from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings
import json

from artwork.models import Artwork
from userprofiles.models import UserWishlist, UserProfile
from blog.models import BlogPost, BlogSubscriber
from orders.models import Cart, CartItem
from .serializers import (
    ArtworkListSerializer, ArtworkDetailSerializer,
    WishlistSerializer, BlogPostListSerializer, BlogPostDetailSerializer,
    ContactFormSerializer, NewsletterSignupSerializer,
    CartSerializer, CartItemSerializer
)


class ArtworkListAPIView(generics.ListAPIView):
    """List artworks with filtering and pagination"""
    serializer_class = ArtworkListSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        # Base queryset with performance optimizations
        queryset = Artwork.objects.filter(is_active=True).select_related('category')
        
        # Apply filters
        medium = self.request.query_params.get('medium')
        category = self.request.query_params.get('category')
        featured = self.request.query_params.get('featured')
        price_min = self.request.query_params.get('price_min')
        price_max = self.request.query_params.get('price_max')
        fields = self.request.query_params.get('fields')
        
        # Apply other filters first
        if medium:
            queryset = queryset.filter(medium=medium)
        if category:
            queryset = queryset.filter(category__slug=category)
        if price_min:
            queryset = queryset.filter(original_price__gte=price_min)
        if price_max:
            queryset = queryset.filter(original_price__lte=price_max)
        
        # Apply ordering
        queryset = queryset.order_by('-is_featured', '-created_at')
        
        # Performance optimization for featured artworks - apply after ordering
        if featured == 'true':
            queryset = queryset.filter(is_featured=True)
            # Limit featured artworks for performance and pre-warm cache
            queryset = queryset[:10]
            
            # Pre-warm URL cache for featured artworks to avoid API delays
            self._prewarm_url_cache(queryset)
            
        return queryset
    
    def _prewarm_url_cache(self, queryset):
        """Pre-warm URL cache for better performance"""
        from django.utils import timezone
        
        for artwork in queryset:
            # Check if cache needs refreshing
            now = timezone.now()
            cache_expired = (not artwork._cached_image_url or 
                           not artwork._url_cache_expires or 
                           now > (artwork._url_cache_expires - timezone.timedelta(minutes=5)))
            
            if cache_expired:
                # Warm the cache by calling get_simple_signed_url
                # This will cache URLs for both full-size and thumbnail access
                artwork.get_simple_signed_url()


class ArtworkDetailAPIView(generics.RetrieveAPIView):
    """Get individual artwork details"""
    queryset = Artwork.objects.filter(is_active=True)
    serializer_class = ArtworkDetailSerializer
    permission_classes = [AllowAny]


class WishlistAPIView(APIView):
    """Get user's wishlist"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        wishlist_items = UserWishlist.objects.filter(
            user=request.user
        ).select_related('artwork__category')
        
        serializer = WishlistSerializer(wishlist_items, many=True)
        return Response({
            'success': True,
            'items': serializer.data
        })


class WishlistStatusAPIView(APIView):
    """Get wishlist status for frontend state management"""
    permission_classes = [AllowAny]  # Allow for both authenticated and guest users
    
    def get(self, request):
        if request.user.is_authenticated:
            # Return actual wishlist IDs for authenticated users
            wishlisted_ids = list(UserWishlist.objects.filter(
                user=request.user
            ).values_list('artwork_id', flat=True))
            
            return Response({
                'success': True,
                'is_authenticated': True,
                'wishlisted_artwork_ids': wishlisted_ids
            })
        else:
            # For guest users, return empty (they should use localStorage fallback)
            return Response({
                'success': True,
                'is_authenticated': False,
                'wishlisted_artwork_ids': []
            })


class WishlistToggleAPIView(APIView):
    """Add/remove artwork from wishlist"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, artwork_id=None):
        return self._toggle_wishlist(request, artwork_id)
    
    def put(self, request, artwork_id=None):
        return self._toggle_wishlist(request, artwork_id)
    
    def _toggle_wishlist(self, request, artwork_id=None):
        # Support both URL parameter and request body
        if not artwork_id:
            artwork_id = request.data.get('artwork_id')
        
        if not artwork_id:
            return Response(
                {'error': 'artwork_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        artwork = get_object_or_404(Artwork, id=artwork_id, is_active=True)
        wishlist_item, created = UserWishlist.objects.get_or_create(
            user=request.user,
            artwork=artwork
        )
        
        if not created:
            # Remove from wishlist
            wishlist_item.delete()
            return Response({
                'success': True,
                'action': 'removed',
                'is_wishlisted': False,
                'message': f'Removed {artwork.title} from wishlist'
            })
        else:
            # Added to wishlist
            return Response({
                'success': True,
                'action': 'added', 
                'is_wishlisted': True,
                'message': f'Added {artwork.title} to wishlist'
            })
    
    # Support PUT method as well for frontend compatibility
    def put(self, request, artwork_id=None):
        return self.post(request, artwork_id)


class WishlistRemoveAPIView(APIView):
    """Remove item from wishlist by item ID"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            item_id = request.data.get('item_id')
            
            if not item_id:
                return Response(
                    {'error': 'item_id is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            wishlist_item = get_object_or_404(UserWishlist, id=item_id, user=request.user)
            artwork_title = wishlist_item.artwork.title
            wishlist_item.delete()
            
            return Response({
                'success': True,
                'message': f'Removed {artwork_title} from wishlist'
            })
            
        except Exception as e:
            return Response(
                {'success': False, 'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class WishlistClearAPIView(APIView):
    """Clear entire wishlist"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            deleted_count = UserWishlist.objects.filter(user=request.user).count()
            UserWishlist.objects.filter(user=request.user).delete()
            
            return Response({
                'success': True,
                'message': f'Cleared {deleted_count} item(s) from wishlist'
            })
            
        except Exception as e:
            return Response(
                {'success': False, 'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


def get_or_create_cart(request):
    """Get or create cart for user or session"""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_id=session_key)
    return cart


class CartAPIView(APIView):
    """Get cart contents and summary"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        cart = get_or_create_cart(request)
        
        # Get shipping country from query params (default to US)
        shipping_country = request.GET.get('country', 'US')
        
        # Build cart items data
        cart_items = []
        for item in cart.items.select_related('artwork').all():
            cart_items.append({
                'id': item.id,
                'artwork': {
                    'id': item.artwork.id,
                    'title': item.artwork.title,
                    'slug': item.artwork.slug,
                    'thumbnail_url': item.artwork.get_image('thumbnail'),
                    'gallery_url': item.artwork.get_image('gallery'),
                },
                'item_type': item.item_type,
                'item_type_display': item.item_type_display,
                'quantity': item.quantity,
                'unit_price': float(item.unit_price),
                'total_price': float(item.total_price),
            })
        
        # Calculate totals based on shipping country
        shipping_cost = cart.shipping_cost(shipping_country)
        total = cart.total_for_country(shipping_country)
        
        return Response({
            'success': True,
            'items': cart_items,
            'subtotal': float(cart.subtotal),
            'shipping': float(shipping_cost),
            'tax': float(cart.tax_amount),  # Will be 0 since Stripe handles tax
            'total': float(total),
            'item_count': cart.item_count,
            'shipping_country': shipping_country,
        })


class CartItemAPIView(APIView):
    """Manage individual cart items"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Add item to cart"""
        try:
            artwork_id = request.data.get('artwork_id')
            item_type = request.data.get('item_type')
            quantity = int(request.data.get('quantity', 1))
            price = float(request.data.get('price', 0))
            
            # Validate required data
            if not all([artwork_id, item_type, price]):
                return Response(
                    {'success': False, 'error': 'Missing required fields'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            artwork = get_object_or_404(Artwork, id=artwork_id)
            cart = get_or_create_cart(request)
            
            # Add or update cart item
            # For original artworks, force quantity to 1
            actual_quantity = 1 if item_type == 'original' else quantity
            
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                artwork=artwork,
                item_type=item_type,
                defaults={'quantity': actual_quantity, 'unit_price': price}
            )
            
            if not created:
                # For original artworks, don't allow quantity increases
                if item_type == 'original':
                    return Response({
                        'success': True,
                        'message': 'Original artwork already in cart (quantity locked at 1)',
                        'cart_count': cart.item_count,
                        'item_id': cart_item.id,
                    })
                else:
                    cart_item.quantity += quantity
                    cart_item.save()
            
            return Response({
                'success': True,
                'message': 'Item added to cart',
                'cart_count': cart.item_count,
                'item_id': cart_item.id,
            })
            
        except Exception as e:
            return Response(
                {'success': False, 'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def put(self, request):
        """Update cart item quantity"""
        try:
            item_id = request.data.get('item_id')
            quantity = int(request.data.get('quantity', 1))
            
            cart = get_or_create_cart(request)
            cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
            
            if quantity <= 0:
                cart_item.delete()
                message = 'Item removed from cart'
            else:
                # For original artworks, quantity is locked at 1
                if cart_item.item_type == 'original':
                    if quantity != 1:
                        return Response({
                            'success': False,
                            'message': 'Original artworks are limited to quantity 1',
                        }, status=status.HTTP_400_BAD_REQUEST)
                else:
                    cart_item.quantity = min(quantity, 10)  # Max 10 items
                    cart_item.save()
                message = 'Cart updated'
            
            return Response({
                'success': True,
                'message': message,
                'cart_count': cart.item_count,
            })
            
        except Exception as e:
            return Response(
                {'success': False, 'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def delete(self, request):
        """Remove item from cart"""
        try:
            item_id = request.data.get('item_id')
            
            cart = get_or_create_cart(request)
            cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
            cart_item.delete()
            
            return Response({
                'success': True,
                'message': 'Item removed from cart',
                'cart_count': cart.item_count,
            })
            
        except Exception as e:
            return Response(
                {'success': False, 'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class CartBulkAddAPIView(APIView):
    """Add multiple items to cart at once"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Add multiple items to cart"""
        try:
            items = request.data.get('items', [])
            
            if not items:
                return Response(
                    {'success': False, 'error': 'No items provided'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            cart = get_or_create_cart(request)
            
            for item_data in items:
                artwork_id = item_data.get('artwork_id')
                item_type = item_data.get('item_type')
                quantity = int(item_data.get('quantity', 1))
                price = float(item_data.get('price', 0))
                
                if not all([artwork_id, item_type, price]):
                    continue
                
                artwork = get_object_or_404(Artwork, id=artwork_id)
                
                # For original artworks, force quantity to 1
                actual_quantity = 1 if item_type == 'original' else quantity
                
                cart_item, created = CartItem.objects.get_or_create(
                    cart=cart,
                    artwork=artwork,
                    item_type=item_type,
                    defaults={'quantity': actual_quantity, 'unit_price': price}
                )
                
                if not created:
                    # For original artworks, don't allow quantity increases
                    if item_type == 'original':
                        # Original already in cart, skip adding
                        continue
                    else:
                        cart_item.quantity += quantity
                        cart_item.save()
            
            return Response({
                'success': True,
                'message': f'{len(items)} item(s) added to cart',
                'cart_count': cart.item_count,
            })
            
        except Exception as e:
            return Response(
                {'success': False, 'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class NewsletterSignupAPIView(APIView):
    """Newsletter subscription endpoint"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = NewsletterSignupSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            name = serializer.validated_data.get('name', '')
            
            # Create or update subscriber
            subscriber, created = BlogSubscriber.objects.get_or_create(
                email=email,
                defaults={
                    'name': name,
                    'subscription_source': 'website_signup',
                    'ip_address': self.get_client_ip(request)
                }
            )
            
            if created:
                # Send welcome email (implement based on email service)
                # send_welcome_email(subscriber)
                
                return Response({
                    'message': 'Successfully subscribed to newsletter!',
                    'email': email
                })
            else:
                return Response({
                    'message': 'Email already subscribed',
                    'email': email
                })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class ContactFormAPIView(APIView):
    """Contact form submission endpoint"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = ContactFormSerializer(data=request.data)
        
        if serializer.is_valid():
            # Process contact form
            name = serializer.validated_data['name']
            email = serializer.validated_data['email']
            subject = serializer.validated_data['subject']
            message = serializer.validated_data['message']
            form_type = serializer.validated_data.get('form_type', 'general')
            
            # Send email notification
            try:
                send_mail(
                    subject=f'[Aiza\'s Fine Art] {subject}',
                    message=f'From: {name} ({email})\n\nMessage:\n{message}',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=['aizasfineart@gmail.com'],
                    fail_silently=False,
                )
                
                return Response({
                    'message': 'Message sent successfully! We\'ll get back to you within 24 hours.',
                    'success': True
                })
                
            except Exception as e:
                return Response({
                    'error': 'Failed to send message. Please try again.',
                    'success': False
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BlogPostListAPIView(generics.ListAPIView):
    """List published blog posts"""
    serializer_class = BlogPostListSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        return BlogPost.objects.filter(
            status='published'
        ).select_related('author').order_by('-published_at')


class BlogPostDetailAPIView(generics.RetrieveAPIView):
    """Get individual blog post"""
    serializer_class = BlogPostDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'
    
    def get_queryset(self):
        return BlogPost.objects.filter(status='published').select_related('author')


@api_view(['POST'])
@permission_classes([AllowAny])
def artworks_by_ids(request):
    """Get artwork data for wishlist IDs"""
    try:
        data = json.loads(request.body)
        artwork_ids = data.get('artwork_ids', [])
        
        if not artwork_ids:
            return Response({
                'success': True, 
                'artworks': []
            })
        
        # Convert string IDs to integers
        try:
            artwork_ids = [int(id) for id in artwork_ids]
        except (ValueError, TypeError):
            return Response({
                'success': False,
                'error': 'Invalid artwork IDs'
            }, status=400)
        
        # Fetch artworks
        artworks = Artwork.objects.filter(
            id__in=artwork_ids, 
            is_active=True
        ).select_related('category')
        
        # Serialize artwork data
        artwork_data = []
        for artwork in artworks:
            artwork_data.append({
                'id': artwork.id,
                'title': artwork.title,
                'slug': artwork.slug,
                'main_image_url': artwork.main_image_url,
                'original_price': float(artwork.original_price) if artwork.original_price else None,
                'original_available': artwork.original_available,
                'prints_available': artwork.prints_available,
                'medium': artwork.get_medium_display(),
                'dimensions_display': artwork.dimensions_display,
                'category': artwork.category.name if artwork.category else None,
                'url': f'/art/{artwork.slug}/',
                'price_display': artwork.price_display,
            })
        
        return Response({
            'success': True,
            'artworks': artwork_data
        })
        
    except json.JSONDecodeError:
        return Response({
            'success': False,
            'error': 'Invalid JSON'
        }, status=400)
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)

from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q, Count, F, Sum
from django.db import models
from django.http import JsonResponse
from artwork.models import Artwork, Category, Tag, Series
from artwork.forms import ArtworkForm
from blog.models import BlogPost
from orders.models import Cart, CartItem
from userprofiles.models import UserWishlist
import json


class HomePage(TemplateView):
    """Homepage with featured artwork carousel and artist intro"""
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Featured artworks for hero carousel
        context['featured_artworks'] = Artwork.objects.filter(
            is_featured=True, 
            is_active=True
        ).select_related('category')[:8]
        
        # Latest available artworks
        context['latest_artworks'] = Artwork.objects.filter(
            is_active=True
        ).select_related('category')[:6]
        
        # Latest blog posts for content
        context['recent_posts'] = BlogPost.objects.filter(
            status='published'
        )[:3]
        
        return context


class AboutView(TemplateView):
    """About page with artist story and studio information"""
    template_name = 'about.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add any specific context for about page
        context['page_title'] = 'About Aiza - Fort Worth Artist'
        context['meta_description'] = 'Learn about Aiza, a TCU Chemistry major turned watercolor and oil painter based in Fort Worth, Texas. Discover her artistic journey and healing through art.'
        
        return context


class GalleryView(ListView):
    """Gallery page with masonry layout and filtering by medium"""
    model = Artwork
    template_name = 'gallery.html'
    context_object_name = 'artworks'
    paginate_by = 20
    
    def get_queryset(self):
        # Optimized query: only select needed fields for gallery display
        queryset = Artwork.objects.only(
            'id', 'title', 'slug', 'main_image_url', 'medium', 
            'original_price', 'original_available', 'type', 'is_featured',
            'display_order', 'created_at', 'category_id'
        ).filter(
            is_active=True
        ).select_related('category')
        
        # Filter by medium from URL path
        medium_filter = self.kwargs.get('medium')
        if medium_filter:
            # Map URL slugs to model choices
            medium_map = {
                'watercolors': 'watercolor',
                'oils': 'oil',
                'mixed-media': 'mixed_media',
                'digital': 'digital'
            }
            if medium_filter in medium_map:
                queryset = queryset.filter(medium=medium_map[medium_filter])
        
        # Apply additional filters from query parameters
        featured = self.request.GET.get('featured')
        search = self.request.GET.get('q')
        
        if featured == 'true':
            queryset = queryset.filter(is_featured=True)
        # Skip complex search with tags to improve performance - implement via AJAX later
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(description__icontains=search)
            ).distinct()
            
        return queryset.order_by('-is_featured', 'display_order', '-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Optimized filter options - only select needed fields
        context['medium_choices'] = Artwork.MEDIUM_CHOICES
        context['categories'] = Category.objects.only('id', 'name', 'slug').filter(is_active=True)
        context['current_medium'] = self.kwargs.get('medium', '')
        context['current_filters'] = {
            'status': self.request.GET.get('status', ''),
            'featured': self.request.GET.get('featured', ''),
            'search': self.request.GET.get('q', ''),
        }
        
        # Add breadcrumb context
        medium_filter = self.kwargs.get('medium')
        if medium_filter:
            medium_display_map = {
                'watercolors': 'Watercolors',
                'oils': 'Oil Paintings', 
                'mixed-media': 'Mixed Media',
                'digital': 'Digital Art'
            }
            context['page_title'] = medium_display_map.get(medium_filter, 'Gallery')
            context['breadcrumb_medium'] = medium_display_map.get(medium_filter)
        else:
            context['page_title'] = 'Gallery'
        
        return context


class PortfolioView(ListView):
    """Portfolio page with masonry gallery and filtering - DEPRECATED: Use GalleryView"""
    model = Artwork
    template_name = 'portfolio.html'
    context_object_name = 'artworks'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Artwork.objects.filter(
            is_active=True
        ).select_related('category')
        
        # Apply filters from query parameters
        medium = self.request.GET.get('medium')
        featured = self.request.GET.get('featured')
        
        if medium:
            queryset = queryset.filter(medium=medium)
        if featured == 'true':
            queryset = queryset.filter(is_featured=True)
            
        return queryset.order_by('-is_featured', 'display_order', '-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Optimized filter options - only select needed fields
        context['medium_choices'] = Artwork.MEDIUM_CHOICES
        context['categories'] = Category.objects.only('id', 'name', 'slug').filter(is_active=True)
        context['current_filters'] = {
            'medium': self.request.GET.get('medium', ''),
            'status': self.request.GET.get('status', ''),
            'featured': self.request.GET.get('featured', ''),
        }
        
        return context


class ShopView(TemplateView):
    """Shop page with React multi-image component"""
    template_name = 'shop_react.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add basic context for React component
        context['categories'] = Category.objects.filter(is_active=True)
        context['medium_choices'] = Artwork.MEDIUM_CHOICES
        
        return context


class ShopDjangoView(ListView):
    """Traditional Django shop page (fallback)"""
    model = Artwork
    template_name = 'shop.html'
    context_object_name = 'artworks'
    paginate_by = 20
    
    def get_queryset(self):
        # Optimized query: only select needed fields and avoid prefetch_related
        return Artwork.objects.only(
            'id', 'title', 'slug', 'main_image_url', 'medium', 
            'original_price', 'original_available', 'type', 'is_featured',
            'display_order', 'category_id'
        ).filter(
            type__in=['original', 'print'],  # Use __in instead of Q() for better performance
            is_active=True
        ).select_related('category').order_by('-is_featured', 'display_order')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Optimized context queries - only select needed fields
        context['categories'] = Category.objects.only('id', 'name', 'slug').filter(is_active=True)
        context['medium_choices'] = Artwork.MEDIUM_CHOICES
        
        # Skip complex tag query to improve performance - can be added via AJAX later
        context['popular_tags'] = []
        
        # Current filters for form state
        context['current_filters'] = {
            'medium': self.request.GET.get('medium', ''),
            'status': self.request.GET.get('status', ''),
            'price_range': self.request.GET.get('price_range', ''),
            'category': self.request.GET.get('category', ''),
        }
        
        return context


class ArtworkDetailView(DetailView):
    """Individual artwork detail page"""
    model = Artwork
    template_name = 'artwork_detail.html'
    context_object_name = 'artwork'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_object(self):
        artwork = get_object_or_404(
            Artwork.objects.select_related('category'),
            slug=self.kwargs['slug'],
            is_active=True
        )
        
        # Track artwork view asynchronously to avoid blocking page load
        # Using F() expression to prevent race conditions
        Artwork.objects.filter(id=artwork.id).update(views=F('views') + 1)
        
        return artwork
    
    def get_batch_frame_images(self):
        """Get frame image URLs using fast method without transformations"""
        frame_images = {}
        
        # Use simple URLs for better performance, only include frames that exist
        for i in range(1, 5):
            raw_frame_url = getattr(self.object, f'frame{i}_image_url', '')
            if raw_frame_url:  # Only process frames that have URLs
                frame_url = self.object.get_frame_simple_url(i)
                if frame_url:  # Only include if we successfully get a cached URL
                    frame_images[f'frame{i}'] = {
                        'gallery': frame_url,
                        'thumbnail': frame_url,  # Use same URL for both for now
                    }
        
        return frame_images
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Pre-cache main image URL to avoid multiple calls in template
        context['cached_main_image'] = self.object.image_url
        context['cached_gallery_url'] = self.object.gallery_url
        
        # Related artworks (same medium or category) - optimized query
        context['related_artworks'] = Artwork.objects.only(
            'id', 'title', 'slug', 'main_image_url', 'medium', 'original_price', 'type', 'category_id'
        ).filter(
            Q(medium=self.object.medium) | Q(category=self.object.category),
            is_active=True
        ).exclude(id=self.object.id).select_related('category')[:4]
        
        # Check if user has wishlisted this artwork (session-based for now)
        context['is_wishlisted'] = self.request.session.get(f'wishlist_{self.object.id}', False)
        
        # Batch generate all frame image URLs to reduce Supabase API calls
        context['frame_images'] = self.get_batch_frame_images()
        
        # SEO context
        context['page_title'] = f"{self.object.title} - {self.object.category.name} by Aiza"
        context['meta_description'] = self.object.meta_description or self.object.description[:160]
        context['og_image'] = context['cached_main_image']  # Use pre-cached URL
        
        return context


class ContactView(TemplateView):
    """Contact page with multiple inquiry forms"""
    template_name = 'contact.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add contact information
        context['contact_info'] = {
            'email': 'aizasfineart@gmail.com',
            'location': 'Fort Worth, TX',
            'instagram': '@aizasfineart',
            'facebook': 'aizasfineart',
            'tiktok': '@aizasfineart',
            'youtube': 'aizasfineart'
        }
        
        return context


# SPA Views (will load React components)
class ArtistDashboardMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin to ensure only the artist (admin) can access dashboard"""
    login_url = '/accounts/login/'
    
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser


class UserDashboardView(ArtistDashboardMixin, TemplateView):
    """Artist dashboard for managing artworks and business"""
    template_name = 'dashboard/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Artwork statistics - new Type based metrics
        context['total_artworks'] = Artwork.objects.count()
        context['originals_count'] = Artwork.objects.filter(type='original').count()
        context['prints_count'] = Artwork.objects.filter(type='print').count()
        context['featured_artworks'] = Artwork.objects.filter(is_featured=True).count()
        
        # Recent artworks
        context['recent_artworks'] = Artwork.objects.order_by('-created_at')[:5]
        
        # Medium breakdown
        context['medium_stats'] = Artwork.objects.values('medium').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Type breakdown by artwork type
        context['type_stats'] = [
            {
                'type': 'Original Artworks',
                'count': Artwork.objects.filter(type='original').count()
            },
            {
                'type': 'Print Artworks', 
                'count': Artwork.objects.filter(type='print').count()
            },
            {
                'type': 'Gallery Only',
                'count': Artwork.objects.filter(type='gallery').count()
            }
        ]
        
        # Purchase analytics by medium (from OrderItems)
        from orders.models import OrderItem
        context['purchases_by_medium'] = OrderItem.objects.filter(
            artwork__isnull=False
        ).values('artwork__medium').annotate(
            count=Count('id'),
            total_sales=Sum('total_price')
        ).order_by('-count')
        
        # Purchase analytics by type (Original vs Print)
        context['purchases_by_type'] = [
            {
                'type': 'Original Sales',
                'count': OrderItem.objects.filter(item_type='original').count(),
                'total_sales': OrderItem.objects.filter(item_type='original').aggregate(
                    total=Sum('total_price')
                )['total'] or 0
            },
            {
                'type': 'Print Sales',
                'count': OrderItem.objects.filter(item_type__startswith='print').count(),
                'total_sales': OrderItem.objects.filter(item_type__startswith='print').aggregate(
                    total=Sum('total_price')
                )['total'] or 0
            }
        ]
        
        return context


class ArtworkCreateView(ArtistDashboardMixin, TemplateView):
    """Create new artwork with React form"""
    template_name = 'dashboard/artwork_form_react.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Prepare data for React component
        context['initial_data'] = json.dumps({})
        context['categories_json'] = json.dumps([
            {'id': cat.id, 'name': cat.name} 
            for cat in Category.objects.filter(is_active=True)
        ])
        context['series_json'] = json.dumps([
            {'id': ser.id, 'name': ser.name, 'category': ser.category_id}
            for ser in Series.objects.filter(is_active=True)
        ])
        context['tags_json'] = json.dumps([
            {'id': tag.id, 'name': tag.name}
            for tag in Tag.objects.filter(is_active=True)
        ])
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Handle form submission from React component"""
        print(f"POST data: {request.POST}")
        print(f"FILES data: {request.FILES}")
        
        # Filter out non-form fields from POST data
        allowed_fields = [
            'title', 'category', 'series', 'medium', 'dimensions_width', 
            'dimensions_height', 'year_created', 'description', 'inspiration', 
            'technique_notes', 'story', 'original_price', 'type', 'edition_info', 
            'meta_description', 'alt_text', 'tags', 'is_featured', 'is_active',
            'main_image_url', 'frame1_image_url', 'frame2_image_url', 
            'frame3_image_url', 'frame4_image_url', 'csrfmiddlewaretoken'
        ]
        
        # Create a mutable copy of POST data and remove unwanted fields
        filtered_post_data = request.POST.copy()
        for key in list(filtered_post_data.keys()):
            if key not in allowed_fields:
                del filtered_post_data[key]
        
        form = ArtworkForm(filtered_post_data, request.FILES)
        
        if form.is_valid():
            artwork = form.save(commit=False)
            
            # Manually handle URL fields since they're not in the form
            artwork.main_image_url = filtered_post_data.get('main_image_url', '')
            artwork.frame1_image_url = filtered_post_data.get('frame1_image_url', '')
            artwork.frame2_image_url = filtered_post_data.get('frame2_image_url', '')
            artwork.frame3_image_url = filtered_post_data.get('frame3_image_url', '')
            artwork.frame4_image_url = filtered_post_data.get('frame4_image_url', '')
            
            # Handle Supabase image uploads
            from utils.supabase_client import supabase_storage
            
            try:
                # Upload main image
                if form.cleaned_data.get('main_image_file'):
                    main_file = form.cleaned_data['main_image_file']
                    filename = supabase_storage.generate_unique_filename(main_file.name, artwork.title)
                    main_file.seek(0)
                    url = supabase_storage.upload_image(filename, main_file.read(), content_type=main_file.content_type)
                    if url:
                        artwork.main_image_url = f"supabase://{filename}"
                
                # Upload frame images
                for i in range(1, 5):
                    file_field = f'frame{i}_image_file'
                    url_field = f'frame{i}_image_url'
                    
                    if form.cleaned_data.get(file_field):
                        frame_file = form.cleaned_data[file_field]
                        filename = supabase_storage.generate_unique_filename(frame_file.name, f"{artwork.title}_frame{i}")
                        frame_file.seek(0)
                        url = supabase_storage.upload_image(filename, frame_file.read(), content_type=frame_file.content_type)
                        if url:
                            setattr(artwork, url_field, f"supabase://{filename}")
                
                # Temporarily store supabase URLs
                supabase_urls = {}
                for field in ['main_image_url', 'frame1_image_url', 'frame2_image_url', 'frame3_image_url', 'frame4_image_url']:
                    value = getattr(artwork, field)
                    if value and value.startswith('supabase://'):
                        supabase_urls[field] = value
                        # Set to a valid dummy URL for model validation
                        setattr(artwork, field, 'https://example.com/temp.jpg')
                
                artwork.save()
                form.save_m2m()
                
                # Restore the actual supabase URLs after save
                for field, url in supabase_urls.items():
                    setattr(artwork, field, url)
                
                # Save again with the actual URLs (bypass validation)
                if supabase_urls:
                    artwork.save(update_fields=list(supabase_urls.keys()))
                
                return JsonResponse({
                    'success': True,
                    'redirect': reverse_lazy('dashboard')
                })
                
            except Exception as e:
                print(f"Upload error: {e}")
                return JsonResponse({
                    'success': False,
                    'message': f'Error uploading images: {str(e)}'
                }, status=400)
        
        print(f"Form validation failed - errors: {form.errors}")
        print(f"Form non-field errors: {form.non_field_errors()}")
        
        # Convert ErrorList objects to plain strings for JSON serialization
        errors_dict = {}
        for field, error_list in form.errors.items():
            errors_dict[field] = [str(error) for error in error_list]
        
        return JsonResponse({
            'success': False,
            'errors': errors_dict,
            'message': 'Please correct the errors and try again.'
        }, status=400)


class ArtworkUpdateView(ArtistDashboardMixin, TemplateView):
    """Edit existing artwork with React form"""
    template_name = 'dashboard/artwork_form_react.html'
    
    def get_object(self):
        return get_object_or_404(Artwork, pk=self.kwargs['pk'])
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        artwork = self.get_object()
        
        # Prepare initial data for React component
        initial_data = {
            'title': artwork.title,
            'category': artwork.category_id if artwork.category else '',
            'series': artwork.series_id if artwork.series else '',
            'medium': artwork.medium,
            'dimensions_width': str(artwork.dimensions_width),
            'dimensions_height': str(artwork.dimensions_height),
            'year_created': artwork.year_created,
            'description': artwork.description,
            'inspiration': artwork.inspiration,
            'technique_notes': artwork.technique_notes,
            'story': artwork.story,
            'original_price': str(artwork.original_price) if artwork.original_price else '',
            'type': artwork.type,
            'edition_info': artwork.edition_info,
            'meta_description': artwork.meta_description,
            'alt_text': artwork.alt_text,
            'tags': [tag.id for tag in artwork.tags.all()],
            'is_featured': artwork.is_featured,
            'is_active': artwork.is_active,
            'main_image_url': artwork.main_image_url,
            'frame1_image_url': artwork.frame1_image_url,
            'frame2_image_url': artwork.frame2_image_url,
            'frame3_image_url': artwork.frame3_image_url,
            'frame4_image_url': artwork.frame4_image_url,
            # Add transformed URLs for preview display
            'main_image_preview': artwork.get_image('gallery'),
            'frame1_image_preview': artwork.get_frame_image(1, 'gallery') if artwork.frame1_image_url else '',
            'frame2_image_preview': artwork.get_frame_image(2, 'gallery') if artwork.frame2_image_url else '',
            'frame3_image_preview': artwork.get_frame_image(3, 'gallery') if artwork.frame3_image_url else '',
            'frame4_image_preview': artwork.get_frame_image(4, 'gallery') if artwork.frame4_image_url else '',
            'main_image_thumbnail': artwork.get_image('thumbnail'),
            'frame1_image_thumbnail': artwork.get_frame_image(1, 'thumbnail') if artwork.frame1_image_url else '',
            'frame2_image_thumbnail': artwork.get_frame_image(2, 'thumbnail') if artwork.frame2_image_url else '',
            'frame3_image_thumbnail': artwork.get_frame_image(3, 'thumbnail') if artwork.frame3_image_url else '',
            'frame4_image_thumbnail': artwork.get_frame_image(4, 'thumbnail') if artwork.frame4_image_url else '',
        }
        
        context['object'] = artwork
        context['initial_data'] = json.dumps(initial_data)
        context['categories_json'] = json.dumps([
            {'id': cat.id, 'name': cat.name} 
            for cat in Category.objects.filter(is_active=True)
        ])
        context['series_json'] = json.dumps([
            {'id': ser.id, 'name': ser.name, 'category': ser.category_id}
            for ser in Series.objects.filter(is_active=True)
        ])
        context['tags_json'] = json.dumps([
            {'id': tag.id, 'name': tag.name}
            for tag in Tag.objects.filter(is_active=True)
        ])
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Handle form submission from React component"""
        artwork = self.get_object()
        print(f"Editing artwork: {artwork.title} (ID: {artwork.id})")
        print(f"POST data: {request.POST}")
        print(f"FILES data: {request.FILES}")
        
        # Create form with all POST data (form now includes URL fields)
        form = ArtworkForm(request.POST, request.FILES, instance=artwork)
        
        if form.is_valid():
            try:
                # Handle file uploads to Supabase if any files are provided
                if any(form.cleaned_data.get(f) for f in ['main_image_file', 'frame1_image_file', 'frame2_image_file', 'frame3_image_file', 'frame4_image_file']):
                    # Only attempt Supabase upload if files are present
                    try:
                        from utils.supabase_client import supabase_storage
                        
                        # Upload main image if provided
                        if form.cleaned_data.get('main_image_file'):
                            main_file = form.cleaned_data['main_image_file']
                            filename = supabase_storage.generate_unique_filename(main_file.name, artwork.title)
                            main_file.seek(0)
                            url = supabase_storage.upload_image(filename, main_file.read(), content_type=main_file.content_type)
                            if url:
                                form.cleaned_data['main_image_url'] = f"supabase://{filename}"
                        
                        # Upload frame images if provided
                        for i in range(1, 5):
                            file_field = f'frame{i}_image_file'
                            url_field = f'frame{i}_image_url'
                            
                            if form.cleaned_data.get(file_field):
                                frame_file = form.cleaned_data[file_field]
                                filename = supabase_storage.generate_unique_filename(frame_file.name, f"{artwork.title}_frame{i}")
                                frame_file.seek(0)
                                url = supabase_storage.upload_image(filename, frame_file.read(), content_type=frame_file.content_type)
                                if url:
                                    form.cleaned_data[url_field] = f"supabase://{filename}"
                    
                    except Exception as upload_error:
                        print(f"Supabase upload failed: {upload_error}")
                        # Continue without upload if Supabase fails
                
                # Save the form (includes URL fields now)
                artwork = form.save()
                
                return JsonResponse({
                    'success': True,
                    'redirect': reverse_lazy('dashboard')
                })
                
            except Exception as e:
                print(f"Error saving artwork: {str(e)}")
                return JsonResponse({
                    'success': False,
                    'message': f'Error saving artwork: {str(e)}'
                }, status=400)
        
        print(f"Form validation failed - errors: {form.errors}")
        print(f"Form non-field errors: {form.non_field_errors()}")
        
        # Convert ErrorList objects to plain strings for JSON serialization
        errors_dict = {}
        for field, error_list in form.errors.items():
            errors_dict[field] = [str(error) for error in error_list]
        
        return JsonResponse({
            'success': False,
            'errors': errors_dict,
            'message': 'Please correct the errors and try again.'
        }, status=400)


class ArtworkDeleteView(ArtistDashboardMixin, DeleteView):
    """Delete artwork"""
    model = Artwork
    template_name = 'dashboard/artwork_confirm_delete.html'
    success_url = reverse_lazy('dashboard')
    
    def delete(self, request, *args, **kwargs):
        artwork = self.get_object()
        messages.success(request, f'Artwork "{artwork.title}" was deleted successfully!')
        return super().delete(request, *args, **kwargs)


class ArtworkListView(ArtistDashboardMixin, ListView):
    """List all artworks for management"""
    model = Artwork
    template_name = 'dashboard/artwork_list.html'
    context_object_name = 'artworks'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Artwork.objects.all().select_related('category', 'series').prefetch_related('tags')
        
        # Filter by medium
        medium = self.request.GET.get('medium')
        if medium:
            queryset = queryset.filter(medium=medium)
            
        # Filter by featured
        featured = self.request.GET.get('featured')
        if featured == 'true':
            queryset = queryset.filter(is_featured=True)
        elif featured == 'false':
            queryset = queryset.filter(is_featured=False)
            
        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )
            
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['medium_choices'] = Artwork.MEDIUM_CHOICES
        context['current_filters'] = {
            'medium': self.request.GET.get('medium', ''),
            'featured': self.request.GET.get('featured', ''),
            'search': self.request.GET.get('search', ''),
        }
        return context


def toggle_artwork_featured(request, pk):
    """AJAX endpoint to toggle artwork featured status"""
    if not (request.user.is_staff or request.user.is_superuser):
        return JsonResponse({'error': 'Permission denied'}, status=403)
        
    if request.method == 'POST':
        artwork = get_object_or_404(Artwork, pk=pk)
        artwork.is_featured = not artwork.is_featured
        artwork.save()
        
        return JsonResponse({
            'success': True,
            'is_featured': artwork.is_featured,
            'message': f'"{artwork.title}" {"featured" if artwork.is_featured else "unfeatured"} successfully!'
        })
        
    return JsonResponse({'error': 'Invalid request'}, status=400)


def bulk_artwork_action(request):
    """AJAX endpoint for bulk operations on artworks"""
    if not (request.user.is_staff or request.user.is_superuser):
        return JsonResponse({'error': 'Permission denied'}, status=403)
        
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        action = data.get('action')
        artwork_ids = data.get('artwork_ids', [])
        
        if not artwork_ids:
            return JsonResponse({'error': 'No artworks selected'}, status=400)
            
        artworks = Artwork.objects.filter(id__in=artwork_ids)
        count = artworks.count()
        
        if action == 'feature':
            artworks.update(is_featured=True)
            message = f'{count} artwork(s) marked as featured'
        elif action == 'unfeature':
            artworks.update(is_featured=False)
            message = f'{count} artwork(s) removed from featured'
        elif action == 'activate':
            artworks.update(is_active=True)
            message = f'{count} artwork(s) activated'
        elif action == 'deactivate':
            artworks.update(is_active=False)
            message = f'{count} artwork(s) deactivated'
        elif action == 'delete':
            artworks.delete()
            message = f'{count} artwork(s) deleted'
        else:
            return JsonResponse({'error': 'Invalid action'}, status=400)
            
        return JsonResponse({'success': True, 'message': message})
        
    return JsonResponse({'error': 'Invalid request'}, status=400)


class CheckoutView(TemplateView):
    """Checkout flow SPA page"""
    template_name = 'spa/checkout.html'


# Legal Pages
class PrivacyView(TemplateView):
    template_name = 'legal/privacy.html'


class ShippingView(TemplateView):
    template_name = 'legal/shipping.html'


class FAQView(TemplateView):
    template_name = 'legal/faq.html'


class TermsView(TemplateView):
    template_name = 'legal/terms.html'


# Cart and Wishlist Views
class CartView(TemplateView):
    """Shopping cart page"""
    template_name = 'cart.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Shopping Cart'
        return context


class WishlistView(TemplateView):
    """Wishlist page"""
    template_name = 'wishlist.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'My Wishlist'
        return context


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


# Cart API Views
def cart_api(request):
    """API endpoint to get cart contents"""
    if request.method == 'GET':
        cart = get_or_create_cart(request)
        
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
                'price': float(item.unit_price),
                'total': float(item.total_price),
            })
        
        return JsonResponse({
            'success': True,
            'cart': {
                'subtotal': float(cart.subtotal),
                'shipping': float(cart.shipping_cost),
                'tax': float(cart.tax_amount),
                'total': float(cart.total),
            },
            'items': cart_items,
            'item_count': cart.item_count,
        })
    
    return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)


def cart_add(request):
    """API endpoint to add item to cart"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            artwork_id = data.get('artwork_id')
            item_type = data.get('item_type')
            quantity = int(data.get('quantity', 1))
            price = float(data.get('price', 0))
            
            # Validate data
            if not all([artwork_id, item_type, price]):
                return JsonResponse({'success': False, 'message': 'Missing required fields'})
            
            artwork = get_object_or_404(Artwork, id=artwork_id)
            cart = get_or_create_cart(request)
            
            # Add or update cart item
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                artwork=artwork,
                item_type=item_type,
                defaults={'quantity': quantity, 'unit_price': price}
            )
            
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Item added to cart',
                'cart_count': cart.item_count,
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)


def cart_add_multiple(request):
    """API endpoint to add multiple items to cart"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            items = data.get('items', [])
            
            if not items:
                return JsonResponse({'success': False, 'message': 'No items provided'})
            
            cart = get_or_create_cart(request)
            
            for item_data in items:
                artwork_id = item_data.get('artwork_id')
                item_type = item_data.get('item_type')
                quantity = int(item_data.get('quantity', 1))
                price = float(item_data.get('price', 0))
                
                if not all([artwork_id, item_type, price]):
                    continue
                
                artwork = get_object_or_404(Artwork, id=artwork_id)
                
                cart_item, created = CartItem.objects.get_or_create(
                    cart=cart,
                    artwork=artwork,
                    item_type=item_type,
                    defaults={'quantity': quantity, 'unit_price': price}
                )
                
                if not created:
                    cart_item.quantity += quantity
                    cart_item.save()
            
            return JsonResponse({
                'success': True,
                'message': f'{len(items)} item(s) added to cart',
                'cart_count': cart.item_count,
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)


def cart_update(request):
    """API endpoint to update cart item quantity"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            item_id = data.get('item_id')
            quantity = int(data.get('quantity', 1))
            
            cart = get_or_create_cart(request)
            cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
            
            if quantity <= 0:
                cart_item.delete()
            else:
                cart_item.quantity = min(quantity, 10)  # Max 10 items
                cart_item.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Cart updated',
                'cart_count': cart.item_count,
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)


def cart_remove(request):
    """API endpoint to remove item from cart"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            item_id = data.get('item_id')
            
            cart = get_or_create_cart(request)
            cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
            cart_item.delete()
            
            return JsonResponse({
                'success': True,
                'message': 'Item removed from cart',
                'cart_count': cart.item_count,
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)


# Wishlist API Views
def wishlist_api(request):
    """API endpoint to get wishlist contents"""
    if request.method == 'GET':
        if request.user.is_authenticated:
            # Limit initial load to 50 items to improve performance
            wishlist_items = UserWishlist.objects.filter(user=request.user).select_related('artwork', 'artwork__category')[:50]
            
            items_data = []
            for item in wishlist_items:
                artwork = item.artwork
                
                # Pre-generate image URLs efficiently - only call get_image once per size
                gallery_url = artwork.get_image('gallery') if artwork.main_image_url else None
                thumbnail_url = artwork.get_image('thumbnail') if artwork.main_image_url else None
                
                items_data.append({
                    'id': item.id,
                    'artwork': {
                        'id': artwork.id,
                        'title': artwork.title,
                        'slug': artwork.slug,
                        'gallery_url': gallery_url,
                        'thumbnail_url': thumbnail_url,
                        'main_image_url': gallery_url,  # Use already generated gallery URL
                        'status': artwork.status,
                        'original_price': float(artwork.original_price) if artwork.original_price else None,
                        'type': artwork.type,
                        'medium_display': artwork.get_medium_display(),
                        'category': artwork.category.name if artwork.category else '',
                        'dimensions_display': artwork.dimensions_display,
                    },
                    'created_at': item.created_at.isoformat(),
                })
            
            return JsonResponse({
                'success': True,
                'items': items_data,
                'count': len(items_data),
            })
        else:
            # For guest users, use session-based wishlist
            wishlist = request.session.get('wishlist', [])
            return JsonResponse({
                'success': True,
                'items': [],
                'count': 0,
                'message': 'Please log in to view your wishlist'
            })
    
    return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)


def wishlist_remove(request):
    """API endpoint to remove item from wishlist"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            item_id = data.get('item_id')
            
            if request.user.is_authenticated:
                wishlist_item = get_object_or_404(UserWishlist, id=item_id, user=request.user)
                wishlist_item.delete()
                
                return JsonResponse({
                    'success': True,
                    'message': 'Item removed from wishlist',
                })
            else:
                return JsonResponse({'success': False, 'message': 'Please log in'})
                
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)


def wishlist_clear(request):
    """API endpoint to clear entire wishlist"""
    if request.method == 'POST':
        if request.user.is_authenticated:
            UserWishlist.objects.filter(user=request.user).delete()
            return JsonResponse({
                'success': True,
                'message': 'Wishlist cleared',
            })
        else:
            return JsonResponse({'success': False, 'message': 'Please log in'})
    
    return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)
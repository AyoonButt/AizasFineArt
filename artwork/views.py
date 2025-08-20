from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, FormView
from django.db.models import Q, Prefetch
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.urls import reverse_lazy
from .models import Artwork, Category, Series, ArtworkInquiry, ArtworkView
from .forms import ArtworkInquiryForm


class GalleryView(ListView):
    model = Artwork
    template_name = 'artwork/gallery.html'
    context_object_name = 'artworks'
    paginate_by = 12

    def get_queryset(self):
        queryset = Artwork.objects.filter(is_active=True).select_related(
            'category', 'series'
        ).prefetch_related('wishlisted_by')
        
        # Apply filters
        category = self.request.GET.get('category')
        medium = self.request.GET.get('medium')
        status = self.request.GET.get('status')
        price_range = self.request.GET.get('price_range')
        sort_by = self.request.GET.get('sort', 'newest')

        if category:
            queryset = queryset.filter(category__slug=category)
        
        if medium:
            queryset = queryset.filter(medium=medium)
            
        if status:
            queryset = queryset.filter(status=status)
            
        if price_range:
            if price_range == 'under_500':
                queryset = queryset.filter(price__lt=500)
            elif price_range == '500_1000':
                queryset = queryset.filter(price__gte=500, price__lt=1000)
            elif price_range == 'over_1000':
                queryset = queryset.filter(price__gte=1000)

        # Apply sorting
        if sort_by == 'newest':
            queryset = queryset.order_by('-created_at')
        elif sort_by == 'oldest':
            queryset = queryset.order_by('created_at')
        elif sort_by == 'price_low':
            queryset = queryset.order_by('price')
        elif sort_by == 'price_high':
            queryset = queryset.order_by('-price')
        elif sort_by == 'title':
            queryset = queryset.order_by('title')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add filter context
        context['categories'] = Category.objects.filter(is_active=True)
        context['mediums'] = Artwork.MEDIUM_CHOICES
        context['current_filters'] = {
            'category': self.request.GET.get('category'),
            'medium': self.request.GET.get('medium'),
            'status': self.request.GET.get('status'),
            'price_range': self.request.GET.get('price_range'),
            'sort': self.request.GET.get('sort', 'newest'),
        }
        
        # Add featured artworks
        context['featured_artworks'] = Artwork.objects.filter(
            is_active=True, is_featured=True
        ).select_related('category')[:3]
        
        return context


class CategoryDetailView(DetailView):
    model = Category
    template_name = 'artwork/category_detail.html'
    context_object_name = 'category'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get artworks in this category
        artworks = Artwork.objects.filter(
            category=self.object, is_active=True
        ).select_related('series')
        
        # Paginate artworks
        paginator = Paginator(artworks, 12)
        page_number = self.request.GET.get('page')
        context['artworks'] = paginator.get_page(page_number)
        
        # Get series in this category
        context['series'] = Series.objects.filter(
            category=self.object, is_active=True
        )
        
        return context


class SeriesDetailView(DetailView):
    model = Series
    template_name = 'artwork/series_detail.html'
    context_object_name = 'series'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_object(self):
        return get_object_or_404(
            Series,
            slug=self.kwargs['slug'],
            category__slug=self.kwargs['category_slug']
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get artworks in this series
        artworks = Artwork.objects.filter(
            series=self.object, is_active=True
        )
        
        # Paginate artworks
        paginator = Paginator(artworks, 12)
        page_number = self.request.GET.get('page')
        context['artworks'] = paginator.get_page(page_number)
        
        return context


class ArtworkDetailView(DetailView):
    model = Artwork
    template_name = 'artwork/detail.html'
    context_object_name = 'artwork'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_object(self):
        artwork = get_object_or_404(
            Artwork.objects.select_related('category', 'series'),
            slug=self.kwargs['slug'],
            category__slug=self.kwargs['category_slug'],
            is_active=True
        )
        
        # Track artwork view
        if self.request.user.is_authenticated:
            ArtworkView.objects.create(
                artwork=artwork,
                ip_address=self.get_client_ip(),
                user_agent=self.request.META.get('HTTP_USER_AGENT', '')
            )
        
        return artwork

    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get related artworks
        context['related_artworks'] = Artwork.objects.filter(
            Q(category=self.object.category) | Q(medium=self.object.medium),
            is_active=True
        ).exclude(pk=self.object.pk).select_related('category')[:4]
        
        # Check if user has wishlisted this artwork
        if self.request.user.is_authenticated:
            context['is_wishlisted'] = self.request.user.wishlists.filter(
                artwork=self.object
            ).exists()
        
        # Add inquiry form
        context['inquiry_form'] = ArtworkInquiryForm()
        
        # Add SEO context
        context['meta_title'] = f"{self.object.title} - {self.object.category.name} by Aiza"
        context['meta_description'] = self.object.meta_description or self.object.description[:160]
        
        return context


class ArtworkSearchView(ListView):
    model = Artwork
    template_name = 'artwork/search_results.html'
    context_object_name = 'artworks'
    paginate_by = 12

    def get_queryset(self):
        query = self.request.GET.get('q', '').strip()
        if not query:
            return Artwork.objects.none()

        return Artwork.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(inspiration__icontains=query) |
            Q(medium__icontains=query) |
            Q(category__name__icontains=query) |
            Q(series__name__icontains=query),
            is_active=True
        ).select_related('category', 'series').distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        context['total_results'] = self.get_queryset().count()
        return context


class ArtworkFilterView(ListView):
    model = Artwork
    template_name = 'artwork/filter_results.html'
    context_object_name = 'artworks'
    paginate_by = 12

    def get_queryset(self):
        queryset = Artwork.objects.filter(is_active=True).select_related('category', 'series')
        
        # Apply AJAX filters
        filters = {}
        for key, value in self.request.GET.items():
            if value and key != 'page':
                filters[key] = value

        if 'categories' in filters:
            category_slugs = filters['categories'].split(',')
            queryset = queryset.filter(category__slug__in=category_slugs)
        
        if 'mediums' in filters:
            mediums = filters['mediums'].split(',')
            queryset = queryset.filter(medium__in=mediums)
            
        if 'min_price' in filters:
            queryset = queryset.filter(price__gte=filters['min_price'])
            
        if 'max_price' in filters:
            queryset = queryset.filter(price__lte=filters['max_price'])

        return queryset

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Return JSON for AJAX requests
            artworks_data = []
            for artwork in context['artworks']:
                artworks_data.append({
                    'id': artwork.id,
                    'title': artwork.title,
                    'url': artwork.get_absolute_url(),
                    'primary_image': artwork.primary_image.url if artwork.primary_image else None,
                    'alt_text': artwork.alt_text,
                    'price_display': artwork.price_display,
                    'medium': artwork.get_medium_display(),
                    'dimensions_display': artwork.dimensions_display,
                    'category': artwork.category.name,
                    'is_available': artwork.is_available,
                })
            
            return JsonResponse({
                'artworks': artworks_data,
                'has_next': context['page_obj'].has_next(),
                'has_previous': context['page_obj'].has_previous(),
                'page_number': context['page_obj'].number,
                'total_pages': context['paginator'].num_pages,
            })
        
        return super().render_to_response(context, **response_kwargs)


class ArtworkInquiryView(FormView):
    form_class = ArtworkInquiryForm
    template_name = 'artwork/inquiry_form.html'
    success_url = reverse_lazy('artwork:gallery')

    def dispatch(self, request, *args, **kwargs):
        self.artwork = get_object_or_404(Artwork, id=kwargs['artwork_id'], is_active=True)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['artwork'] = self.artwork
        return context

    def form_valid(self, form):
        inquiry = form.save(commit=False)
        inquiry.artwork = self.artwork
        inquiry.save()
        
        messages.success(
            self.request,
            f"Your inquiry about '{self.artwork.title}' has been sent successfully. "
            "We'll get back to you within 24 hours."
        )
        
        # Send notification email (implement based on your email setup)
        # send_inquiry_notification(inquiry)
        
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Inquiry sent successfully!'})
        
        return super().form_valid(form)

    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False, 
                'errors': form.errors,
                'message': 'Please correct the errors and try again.'
            })
        
        return super().form_invalid(form)

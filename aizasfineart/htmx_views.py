"""
HTMX-specific views for partial page updates and interactive components
"""

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db.models import Q
from artwork.models import Artwork, Category, Tag, PrintOption
import json


@require_http_methods(["GET"])
def gallery_filter(request):
    """Filter gallery items based on medium/category"""
    medium = request.GET.get('medium', 'all')
    category = request.GET.get('category', 'all')
    
    # Mock data for now - replace with actual model queries
    artworks = [
        {
            'id': 1,
            'title': 'Magnolias',
            'medium': 'watercolor',
            'category': 'floral',
            'image': 'dist/images/Shop/Magnolias/magnolias_lowres.jpg',
            'price': 350,
            'available': True
        },
        {
            'id': 2,
            'title': 'The Quiet Coast',
            'medium': 'watercolor',
            'category': 'landscape',
            'image': 'dist/images/Shop/The Quiet Coast/thequietcoast_mockup_nb.jpg',
            'price': 425,
            'available': True
        },
        {
            'id': 3,
            'title': 'Snowdrops',
            'medium': 'watercolor',
            'category': 'floral',
            'image': 'dist/images/Shop/Snowdrops/snowdrops_lowres.jpg',
            'price': 275,
            'available': True
        },
        {
            'id': 4,
            'title': 'Hibiscus',
            'medium': 'oil',
            'category': 'floral',
            'image': 'dist/images/Shop/Hibiscus/hibiscus_mockup_nb.jpg',
            'price': 485,
            'available': True
        },
        {
            'id': 5,
            'title': 'Kingfisher',
            'medium': 'watercolor',
            'category': 'wildlife',
            'image': 'dist/images/Shop/Kingfisher/kingfisher_mockup_nb.jpg',
            'price': 395,
            'available': True
        },
        {
            'id': 6,
            'title': 'Velka Fatra',
            'medium': 'oil',
            'category': 'landscape',
            'image': 'dist/images/Shop/Velka Fatra/velkafatra_mockup.jpg',
            'price': 650,
            'available': True
        }
    ]
    
    # Filter artworks
    filtered_artworks = artworks
    if medium != 'all':
        filtered_artworks = [a for a in filtered_artworks if a['medium'] == medium]
    if category != 'all':
        filtered_artworks = [a for a in filtered_artworks if a['category'] == category]
    
    # Use Django Component instead of partial template
    return component.render_to_response(request, 'gallery_grid', {
        'artworks': filtered_artworks,
        'medium': medium,
        'category': category,
        'total_count': len(filtered_artworks)
    })


@require_http_methods(["GET"])
def search_artworks(request):
    """Search artworks by title/description"""
    query = request.GET.get('q', '').strip()
    
    # Mock search results - replace with actual search logic
    if query:
        results = [
            {
                'id': 1,
                'title': 'Magnolias',
                'medium': 'Watercolor',
                'image': 'dist/images/Shop/Magnolias/magnolias_lowres.jpg',
                'price': 350
            }
        ] if 'magnolia' in query.lower() else []
    else:
        results = []
    
    context = {
        'results': results,
        'query': query
    }
    
    return render(request, 'partials/search_results.html', context)


@require_http_methods(["POST"])
def toggle_wishlist(request):
    """Add/remove item from wishlist"""
    try:
        data = json.loads(request.body)
        artwork_id = data.get('artwork_id')
        action = data.get('action')  # 'add' or 'remove'
        
        # Mock wishlist logic - replace with actual implementation
        wishlist_count = 3 if action == 'add' else 2
        
        return JsonResponse({
            'success': True,
            'action': action,
            'wishlist_count': wishlist_count,
            'message': f'{"Added to" if action == "add" else "Removed from"} wishlist'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@require_http_methods(["POST"])
def newsletter_signup(request):
    """Handle newsletter signup"""
    email = request.POST.get('email', '').strip()
    
    if not email:
        return component.render_to_response(request, 'newsletter_form', {
            'email': email,
            'error_message': 'Please enter a valid email address.'
        })
    
    # Mock signup logic - replace with actual implementation
    # For now, always return success
    return component.render_to_response(request, 'newsletter_form', {
        'success_message': 'Thank you for subscribing! You\'ll receive our latest updates.'
    })


@require_http_methods(["GET"])
def load_more_artworks(request):
    """Load more artworks for infinite scroll"""
    page = int(request.GET.get('page', 2))
    per_page = 6
    
    # Mock pagination - replace with actual model queries
    all_artworks = [
        # This would be your actual artwork queryset
        {'id': i, 'title': f'Artwork {i}', 'image': 'placeholder.jpg'} 
        for i in range(1, 25)
    ]
    
    start = (page - 1) * per_page
    end = start + per_page
    artworks = all_artworks[start:end]
    
    context = {
        'artworks': artworks,
        'page': page,
        'has_more': end < len(all_artworks)
    }
    
    return render(request, 'partials/artwork_items.html', context)


@require_http_methods(["POST"])
def contact_form(request):
    """Handle contact form submission"""
    from components.components import ContactForm
    
    form = ContactForm(request.POST)
    
    if form.is_valid():
        # Mock form processing - replace with actual implementation
        return component.render_to_response(request, 'contact_form', {
            'form': ContactForm(),  # Fresh form
            'success_message': 'Thank you for your message! I\'ll get back to you soon.'
        })
    else:
        return component.render_to_response(request, 'contact_form', {
            'form': form,
            'error_message': 'Please correct the errors below.'
        })


@require_http_methods(["POST"]) 
def commission_inquiry(request):
    """Handle commission inquiry form"""
    name = request.POST.get('name', '').strip()
    email = request.POST.get('email', '').strip()
    size = request.POST.get('size', '').strip()
    medium = request.POST.get('medium', '').strip()
    description = request.POST.get('description', '').strip()
    
    if not all([name, email, size, medium, description]):
        return render(request, 'components/commission_form.html', {
            'error_message': 'Please fill in all required fields.'
        })
    
    # Mock commission inquiry processing
    return render(request, 'components/commission_form.html', {
        'success_message': 'Thank you for your commission inquiry! I\'ll review your project and get back to you within 24 hours.'
    })


# ===== SHOP HTMX VIEWS =====

@require_http_methods(["GET"])
def shop_artwork_list(request):
    """Return filtered artwork list for shop page"""
    # Get filter parameters
    categories = request.GET.getlist('category')
    mediums = request.GET.getlist('medium')
    price_range = request.GET.get('price_range', 'all')
    availability = request.GET.getlist('availability')
    tag_slug = request.GET.get('tag')
    sort_by = request.GET.get('sort', 'featured')
    page = request.GET.get('page', 1)
    
    # Start with active artworks that should appear in shop
    # Show original and print artworks only (exclude gallery)
    # Gallery type artworks are not for sale
    artworks = Artwork.objects.filter(
        is_active=True,
        type__in=['original', 'print']
    )
    
    # Apply filters
    if categories and 'all' not in categories:
        artworks = artworks.filter(category__slug__in=categories)
    
    if mediums:
        artworks = artworks.filter(medium__in=mediums)
    
    if price_range != 'all':
        if price_range == '0-100':
            artworks = artworks.filter(
                Q(original_price__lte=100) | Q(print_options__price__lte=100)
            ).distinct()
        elif price_range == '100-500':
            artworks = artworks.filter(
                Q(original_price__range=(100, 500)) | Q(print_options__price__range=(100, 500))
            ).distinct()
        elif price_range == '500-1000':
            artworks = artworks.filter(
                Q(original_price__range=(500, 1000)) | Q(print_options__price__range=(500, 1000))
            ).distinct()
        elif price_range == '1000+':
            artworks = artworks.filter(
                Q(original_price__gte=1000) | Q(print_options__price__gte=1000)
            ).distinct()
    
    if availability:
        if 'originals' in availability and 'prints' not in availability:
            artworks = artworks.filter(type='original')
        elif 'prints' in availability and 'originals' not in availability:
            artworks = artworks.filter(type='print')
        elif 'originals' in availability and 'prints' in availability:
            artworks = artworks.filter(type__in=['original', 'print'])
    
    if tag_slug:
        artworks = artworks.filter(tags__slug=tag_slug)
    
    # Apply sorting
    if sort_by == 'featured':
        artworks = artworks.order_by('-is_featured', 'display_order', '-created_at')
    elif sort_by == 'newest':
        artworks = artworks.order_by('-created_at')
    elif sort_by == 'price_low':
        artworks = artworks.order_by('original_price')
    elif sort_by == 'price_high':
        artworks = artworks.order_by('-original_price')
    elif sort_by == 'title':
        artworks = artworks.order_by('title')
    elif sort_by == 'popularity':
        artworks = artworks.order_by('-views', '-favorites')
    
    # Pagination
    paginator = Paginator(artworks, 12)
    page_obj = paginator.get_page(page)
    
    # Set has_more header for infinite scroll
    has_more = page_obj.has_next()
    
    context = {
        'artworks': page_obj.object_list,
        'has_more': has_more,
        'next_page': page_obj.next_page_number() if has_more else None,
    }
    
    response = render(request, 'components/artwork_grid.html', context)
    if has_more:
        response['X-Has-More'] = 'true'
    else:
        response['X-Has-More'] = 'false'
    
    return response


@require_http_methods(["GET"])
def shop_filters(request):
    """Return filter options for shop sidebar"""
    categories = Category.objects.filter(is_active=True).prefetch_related('artworks')
    tags = Tag.objects.filter(is_active=True, artworks__is_active=True).distinct()[:10]
    
    medium_choices = Artwork.MEDIUM_CHOICES
    
    context = {
        'categories': categories,
        'popular_tags': tags,
        'medium_choices': medium_choices,
    }
    
    return render(request, 'components/shop_filters.html', context)


@require_http_methods(["GET"])
def artwork_pricing_partial(request, artwork_id):
    """Return updated pricing section for artwork"""
    artwork = get_object_or_404(Artwork, id=artwork_id, is_active=True)
    print_option_id = request.GET.get('print_option')
    
    selected_print_option = None
    if print_option_id:
        try:
            selected_print_option = artwork.print_options.get(id=print_option_id, is_available=True)
        except PrintOption.DoesNotExist:
            selected_print_option = artwork.print_options.filter(is_available=True).first()
    else:
        selected_print_option = artwork.print_options.filter(is_available=True).first()
    
    context = {
        'artwork': artwork,
        'selected_print_option': selected_print_option,
    }
    
    return render(request, 'components/artwork_pricing.html', context)


@require_http_methods(["GET"])
def artwork_image_partial(request, artwork_id):
    """Return updated main image for artwork"""
    artwork = get_object_or_404(Artwork, id=artwork_id, is_active=True)
    image_index = int(request.GET.get('image_index', 0))
    
    all_images = artwork.all_images
    if 0 <= image_index < len(all_images):
        image_url = all_images[image_index]
    else:
        image_url = artwork.main_image_url
    
    context = {
        'artwork': artwork,
        'image_url': image_url,
        'image_index': image_index,
    }
    
    return render(request, 'components/artwork_image.html', context)


@require_http_methods(["GET"])
def toggle_story_partial(request, artwork_id):
    """Toggle artist story visibility"""
    artwork = get_object_or_404(Artwork, id=artwork_id, is_active=True)
    show = request.GET.get('show', 'true') == 'true'
    
    context = {
        'artwork': artwork,
        'show_story': show,
    }
    
    return render(request, 'components/artwork_story.html', context)


@require_http_methods(["POST"])
def add_to_cart(request):
    """Add artwork to cart"""
    artwork_id = request.POST.get('artwork_id')
    item_type = request.POST.get('type')  # 'original' or 'print'
    print_option_id = request.POST.get('print_option')
    
    try:
        artwork = Artwork.objects.get(id=artwork_id, is_active=True)
        
        if item_type == 'original':
            if artwork.type != 'original':
                return JsonResponse({
                    'success': False,
                    'message': 'Original artwork is not available'
                })
            price = artwork.original_price
            item_description = f"{artwork.title} (Original)"
            
        elif item_type == 'print':
            if artwork.type != 'print':
                return JsonResponse({
                    'success': False,
                    'message': 'Prints are not available for this artwork'
                })
            
            if print_option_id:
                try:
                    print_option = artwork.print_options.get(id=print_option_id, is_available=True)
                    price = print_option.price
                    item_description = f"{artwork.title} Print ({print_option.size} {print_option.material})"
                except PrintOption.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'message': 'Selected print option is not available'
                    })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Please select a print option'
                })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Invalid item type'
            })
        
        # TODO: Implement actual cart logic here
        # For now, just return success
        
        return JsonResponse({
            'success': True,
            'message': f'Added {item_description} to cart',
            'artwork_id': artwork_id,
            'price': float(price)
        })
        
    except Artwork.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Artwork not found'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error adding to cart: {str(e)}'
        })


@require_http_methods(["PUT"])
def toggle_wishlist(request, artwork_id):
    """Toggle artwork in user's wishlist"""
    try:
        artwork = Artwork.objects.get(id=artwork_id, is_active=True)
        
        # Simulate toggling
        in_wishlist = request.session.get(f'wishlist_{artwork_id}', False)
        in_wishlist = not in_wishlist
        request.session[f'wishlist_{artwork_id}'] = in_wishlist
        
        # Update favorites count
        if in_wishlist:
            artwork.favorites += 1
        else:
            artwork.favorites = max(0, artwork.favorites - 1)
        artwork.save()
        
        # Return HTML for HTMX to swap
        return render(request, 'components/wishlist_button.html', {
            'artwork': artwork,
            'in_wishlist': in_wishlist
        })
        
    except Artwork.DoesNotExist:
        return HttpResponse('<button class="w-8 h-8 bg-white/90 rounded-full flex items-center justify-center shadow-sm opacity-50" disabled>❌</button>')


@require_http_methods(["POST"])
def join_waitlist(request, artwork_id):
    """Join waitlist for unavailable artwork"""
    email = request.POST.get('email', '').strip()
    
    if not email:
        return JsonResponse({
            'success': False,
            'message': 'Please provide a valid email address'
        })
    
    try:
        artwork = Artwork.objects.get(id=artwork_id, is_active=True)
        
        # TODO: Implement actual waitlist logic
        # For now, just return success
        
        return JsonResponse({
            'success': True,
            'message': 'You\'ve been added to the waitlist! We\'ll notify you when this artwork becomes available.'
        })
        
    except Artwork.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Artwork not found'
        })


@require_http_methods(["GET"])
def cart_count(request):
    """Return current cart count"""
    # TODO: Implement actual cart count logic
    # For now, return mock count
    count = request.session.get('cart_count', 0)
    
    return JsonResponse({
        'count': count
    })
"""
URL Configuration for aizasfineart project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.shortcuts import redirect

from . import views, htmx_views

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Main pages (Django templates for SEO)
    path('', views.HomePage.as_view(), name='home'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('portfolio/', views.PortfolioView.as_view(), name='portfolio'),  # Keep for backward compatibility
    path('gallery/', views.GalleryView.as_view(), name='gallery'),
    path('gallery/<str:medium>/', views.GalleryView.as_view(), name='gallery_medium'),
    path('react-demo/', TemplateView.as_view(template_name='react_demo.html'), name='react_demo'),
    path('stripe-test/', TemplateView.as_view(template_name='stripe_test.html', extra_context={'stripe_public_key': getattr(settings, 'STRIPE_PUBLISHABLE_KEY', '')}), name='stripe_test'),
    path('debug-stripe/', TemplateView.as_view(template_name='debug_stripe.html', extra_context={'stripe_public_key': getattr(settings, 'STRIPE_PUBLISHABLE_KEY', '')}), name='debug_stripe'),
    path('shop/', views.ShopDjangoView.as_view(), name='shop'),
    path('shop-react/', views.ShopView.as_view(), name='shop_react'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    
    # Artwork detail pages
    path('art/<slug:slug>/', views.ArtworkDetailView.as_view(), name='artwork_detail'),
    
    # App includes
    path('art/', include('artwork.urls', namespace='artwork')),
    path('blog/', include('blog.urls', namespace='blog')),
    path('orders/', include('orders.urls', namespace='orders')),
    path('users/', include('userprofiles.urls', namespace='userprofiles')),
    
    # API endpoints
    path('api/', include('api.urls', namespace='api')),
    
    # Monitoring endpoints
    path('metrics/', include('artwork.urls_metrics')),
    
    # HTMX endpoints for shop
    path('shop/artworks/', htmx_views.shop_artwork_list, name='shop_artwork_list'),
    path('shop/filters/', htmx_views.shop_filters, name='shop_filters'),
    path('artwork/<int:artwork_id>/pricing/', htmx_views.artwork_pricing_partial, name='artwork_pricing_partial'),
    path('artwork/<int:artwork_id>/image/', htmx_views.artwork_image_partial, name='artwork_image_partial'),
    path('artwork/<int:artwork_id>/story/', htmx_views.toggle_story_partial, name='toggle_story_partial'),
    path('cart/add/', htmx_views.add_to_cart, name='add_to_cart'),
    path('cart/count/', htmx_views.cart_count, name='cart_count'),
    path('wishlist/<int:artwork_id>/', htmx_views.toggle_wishlist, name='toggle_wishlist'),
    path('waitlist/<int:artwork_id>/', htmx_views.join_waitlist, name='join_waitlist'),
    
    # Other HTMX endpoints
    path('htmx/gallery-filter/', htmx_views.gallery_filter, name='htmx_gallery_filter'),
    path('htmx/search/', htmx_views.search_artworks, name='htmx_search'),
    path('htmx/newsletter/', htmx_views.newsletter_signup, name='htmx_newsletter'),
    path('htmx/contact/', htmx_views.contact_form, name='htmx_contact'),
    path('htmx/commission/', htmx_views.commission_inquiry, name='htmx_commission'),
    path('htmx/load-more/', htmx_views.load_more_artworks, name='htmx_load_more'),
    
    # User authentication
    path('accounts/', include('allauth.urls')),
    
    # Artist Dashboard
    path('dashboard/', views.UserDashboardView.as_view(), name='dashboard'),
    path('dashboard/artworks/', views.ArtworkListView.as_view(), name='artwork_list'),
    path('dashboard/artworks/create/', views.ArtworkCreateView.as_view(), name='artwork_create'),
    path('dashboard/artworks/<int:pk>/edit/', views.ArtworkUpdateView.as_view(), name='artwork_update'),
    path('dashboard/artworks/<int:pk>/delete/', views.ArtworkDeleteView.as_view(), name='artwork_delete'),
    path('dashboard/artwork/<int:pk>/toggle-featured/', views.toggle_artwork_featured, name='toggle_artwork_featured'),
    path('dashboard/artwork/bulk-action/', views.bulk_artwork_action, name='bulk_artwork_action'),
    
    # Cart and Wishlist
    path('cart/', views.CartView.as_view(), name='cart'),
    path('wishlist/', views.WishlistView.as_view(), name='wishlist'),
    
    # Cart API endpoints
    path('cart/api/', views.cart_api, name='cart_api'),
    path('cart/add/', views.cart_add, name='cart_add_api'),
    path('cart/add-multiple/', views.cart_add_multiple, name='cart_add_multiple'),
    path('cart/update/', views.cart_update, name='cart_update'),
    path('cart/remove/', views.cart_remove, name='cart_remove'),
    
    # Wishlist API endpoints
    path('wishlist/api/', views.wishlist_api, name='wishlist_api'),
    path('wishlist/remove/', views.wishlist_remove, name='wishlist_remove'),
    path('wishlist/clear/', views.wishlist_clear, name='wishlist_clear'),
    
    # Checkout (redirect to new orders checkout)
    path('checkout/', lambda request: redirect('/orders/checkout/')),
    
    # Legal pages
    path('privacy/', views.PrivacyView.as_view(), name='privacy'),
    path('shipping/', views.ShippingView.as_view(), name='shipping'),
    path('faq/', views.FAQView.as_view(), name='faq'),
    path('terms/', views.TermsView.as_view(), name='terms'),
    
    # Legacy auth redirects (redirect to allauth URLs)
    path('login/', lambda request: redirect('/accounts/login/')),
    path('signup/', lambda request: redirect('/accounts/signup/')),
    path('logout/', lambda request: redirect('/accounts/logout/')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
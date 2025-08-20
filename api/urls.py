from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    # Artwork API endpoints
    path('artworks/', views.ArtworkListAPIView.as_view(), name='artwork_list'),
    path('artworks/<int:pk>/', views.ArtworkDetailAPIView.as_view(), name='artwork_detail'),
    path('artworks/by-ids/', views.artworks_by_ids, name='artworks_by_ids'),
    
    # Wishlist API endpoints
    path('wishlist/', views.WishlistAPIView.as_view(), name='wishlist'),
    path('wishlist/status/', views.WishlistStatusAPIView.as_view(), name='wishlist_status'),
    path('wishlist/toggle/', views.WishlistToggleAPIView.as_view(), name='wishlist_toggle_post'),
    path('wishlist/toggle/<int:artwork_id>/', views.WishlistToggleAPIView.as_view(), name='wishlist_toggle'),
    path('wishlist/remove/', views.WishlistRemoveAPIView.as_view(), name='wishlist_remove'),
    path('wishlist/clear/', views.WishlistClearAPIView.as_view(), name='wishlist_clear'),
    
    # Cart API endpoints
    path('cart/', views.CartAPIView.as_view(), name='cart'),
    path('cart/items/', views.CartItemAPIView.as_view(), name='cart_item'),
    path('cart/add/', views.CartItemAPIView.as_view(), name='cart_add'),
    path('cart/add-multiple/', views.CartBulkAddAPIView.as_view(), name='cart_bulk_add'),
    path('cart/update/', views.CartItemAPIView.as_view(), name='cart_update'),
    path('cart/remove/', views.CartItemAPIView.as_view(), name='cart_remove'),
    
    # Newsletter and contact
    path('newsletter/', views.NewsletterSignupAPIView.as_view(), name='newsletter'),
    path('contact/', views.ContactFormAPIView.as_view(), name='contact'),
    
    # Blog API endpoints
    path('blog/posts/', views.BlogPostListAPIView.as_view(), name='blog_posts'),
    path('blog/posts/<slug:slug>/', views.BlogPostDetailAPIView.as_view(), name='blog_post_detail'),
]
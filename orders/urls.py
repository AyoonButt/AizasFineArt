from django.urls import path
from . import views, api_views, checkout_views

app_name = 'orders'

urlpatterns = [
    # Root URL - redirect to order history
    path('', views.order_history, name='index'),
    
    # Cart URLs
    path('cart/', views.CartView.as_view(), name='cart'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/', views.remove_from_cart, name='remove_from_cart'),
    
    # Checkout URLs
    path('checkout/', checkout_views.checkout, name='checkout'),
    path('checkout/direct/', views.DirectCheckoutView.as_view(), name='direct_checkout'),
    path('checkout/setup/', views.setup_direct_checkout, name='setup_direct_checkout'),
    path('checkout/clear/', views.clear_direct_checkout, name='clear_direct_checkout'),
    path('checkout/confirm-payment/', checkout_views.confirm_payment, name='confirm_payment'),
    path('checkout/success/<int:order_id>/', checkout_views.order_success, name='order_success'),
    path('apply-coupon/', views.apply_coupon, name='apply_coupon'),
    
    # Order management
    path('confirmation/<str:order_number>/', views.OrderConfirmationView.as_view(), name='confirmation'),
    path('history/', views.order_history, name='history'),
    path('detail/<str:order_number>/', views.OrderDetailView.as_view(), name='detail'),
    path('cancel/<str:order_number>/', views.cancel_order, name='cancel'),
    path('refund/<str:order_number>/', views.request_refund, name='refund'),
    
    # API endpoints for Stripe integration
    path('api/create-payment-intent/', views.create_payment_intent, name='create_payment_intent'),
    
    # Order tracking API endpoints
    path('api/<str:order_number>/status/', api_views.order_status_api, name='order_status_api'),
    path('api/<str:order_number>/refresh/', api_views.refresh_order_status, name='refresh_order_status'),
    
    # Webhook endpoints
    path('webhooks/luma-prints/', api_views.luma_prints_webhook, name='luma_prints_webhook'),
]
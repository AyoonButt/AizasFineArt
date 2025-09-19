"""
Enhanced Checkout Views with Stripe Integration
Handles billing/shipping info and payment processing via Stripe
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.conf import settings
import stripe
import json
import logging

from .models import Order, OrderItem, Cart
from .stripe_service import StripeCustomerService, StripeCheckoutService
from .forms import CheckoutForm, ShippingAddressForm

logger = logging.getLogger(__name__)

@login_required
def checkout(request):
    """Enhanced checkout with Stripe integration"""
    # Get user's cart
    try:
        cart = Cart.objects.get(user=request.user)
        if not cart.items.exists():
            messages.warning(request, "Your cart is empty.")
            return redirect('orders:cart')
    except Cart.DoesNotExist:
        messages.warning(request, "Your cart is empty.")
        return redirect('orders:cart')
    
    # Get or create Stripe customer
    customer = StripeCustomerService.create_or_get_customer(request.user)
    
    # Get saved payment methods
    payment_methods = StripeCustomerService.get_customer_payment_methods(customer.id)
    
    # Pre-fill forms with saved data
    initial_data = {}
    if hasattr(request.user, 'profile'):
        profile = request.user.profile
        initial_data = {
            'email': request.user.email,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'phone': profile.phone,
            'address_line_1': profile.address_line_1,
            'address_line_2': profile.address_line_2,
            'city': profile.city,
            'state': profile.state,
            'postal_code': profile.postal_code,
            'country': profile.country or 'US',
        }
    
    if request.method == 'POST':
        return handle_checkout_submission(request, cart, customer)
    
    # Create payment intent for new payment method
    payment_intent = None
    if not payment_methods.data:  # No saved payment methods
        try:
            payment_intent = StripeCustomerService.create_payment_intent(
                amount=cart.total,
                customer_id=customer.id,
                save_payment_method=True
            )
        except Exception as e:
            logger.error(f"Error creating payment intent: {e}")
            messages.error(request, "Unable to initialize payment. Please try again.")
            return redirect('orders:cart')
    
    context = {
        'cart': cart,
        'customer': customer,
        'payment_methods': payment_methods.data,
        'initial_data': initial_data,
        'stripe_public_key': settings.STRIPE_PUBLISHABLE_KEY,
        'client_secret': payment_intent.client_secret if payment_intent else None,
        'has_saved_info': bool(initial_data.get('address_line_1')),
    }
    
    return render(request, 'orders/checkout.html', context)

def handle_checkout_submission(request, cart, customer):
    """Handle checkout form submission"""
    payment_method_type = request.POST.get('payment_method_type')  # 'saved' or 'new'
    save_info = request.POST.get('save_info') == 'on'
    
    try:
        if payment_method_type == 'saved':
            # Using saved payment method
            payment_method_id = request.POST.get('saved_payment_method')
            if not payment_method_id:
                messages.error(request, "Please select a payment method.")
                return redirect('orders:checkout')
            
            # Create and confirm payment intent
            payment_intent = StripeCustomerService.create_payment_intent(
                amount=cart.total,
                customer_id=customer.id,
                payment_method_id=payment_method_id
            )
            
        else:
            # New payment method - handle via JavaScript
            return JsonResponse({
                'requires_action': True,
                'payment_intent_id': request.POST.get('payment_intent_id')
            })
        
        # Update customer info if save_info is checked
        if save_info:
            update_customer_info(request, customer.id)
        
        # Create order if payment succeeded
        if payment_intent.status == 'succeeded':
            order = create_order_from_cart(request.user, cart, payment_intent)
            cart.clear()
            
            messages.success(request, f"Order #{order.order_number} placed successfully!")
            return redirect('orders:order_success', order_id=order.id)
        else:
            messages.error(request, "Payment failed. Please try again.")
            return redirect('orders:checkout')
            
    except stripe.error.CardError as e:
        messages.error(request, f"Payment failed: {e.user_message}")
        return redirect('orders:checkout')
    except Exception as e:
        logger.error(f"Checkout error: {e}")
        messages.error(request, "An error occurred during checkout. Please try again.")
        return redirect('orders:checkout')

@require_POST
@csrf_exempt
def confirm_payment(request):
    """AJAX endpoint to confirm payment intent"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    try:
        data = json.loads(request.body)
        payment_intent_id = data.get('payment_intent_id')
        save_info = data.get('save_info', False)
        
        # Get payment intent
        stripe.api_key = settings.STRIPE_SECRET_KEY
        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        
        if payment_intent.status == 'succeeded':
            # Get cart and create order
            cart = Cart.objects.get(user=request.user)
            order = create_order_from_cart(request.user, cart, payment_intent)
            
            # Save customer info if requested
            if save_info:
                customer = StripeCustomerService.create_or_get_customer(request.user)
                update_customer_info_from_payment_intent(request.user, payment_intent)
            
            # Clear cart
            cart.clear()
            
            return JsonResponse({
                'success': True,
                'order_id': order.id,
                'redirect_url': reverse('orders:order_success', kwargs={'order_id': order.id})
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Payment not completed'
            })
            
    except Exception as e:
        logger.error(f"Payment confirmation error: {e}")
        return JsonResponse({
            'success': False,
            'error': 'An error occurred processing your payment'
        }, status=500)

def update_customer_info(request, customer_id):
    """Update Stripe customer with form data"""
    try:
        # Update Stripe customer
        customer_data = {
            'email': request.POST.get('email'),
            'name': f"{request.POST.get('first_name')} {request.POST.get('last_name')}",
            'phone': request.POST.get('phone'),
            'address': {
                'line1': request.POST.get('address_line_1'),
                'line2': request.POST.get('address_line_2', ''),
                'city': request.POST.get('city'),
                'state': request.POST.get('state'),
                'postal_code': request.POST.get('postal_code'),
                'country': request.POST.get('country', 'US')
            }
        }
        
        customer_data['shipping'] = {
            'name': customer_data['name'],
            'address': customer_data['address']
        }
        
        StripeCustomerService.update_customer_info(customer_id, **customer_data)
        
        # Update local profile
        if hasattr(request.user, 'profile'):
            profile = request.user.profile
            profile.phone = request.POST.get('phone', '')
            profile.address_line_1 = request.POST.get('address_line_1', '')
            profile.address_line_2 = request.POST.get('address_line_2', '')
            profile.city = request.POST.get('city', '')
            profile.state = request.POST.get('state', '')
            profile.postal_code = request.POST.get('postal_code', '')
            profile.country = request.POST.get('country', 'US')
            profile.save_payment_info = True
            profile.save()
        
        # Update user name if provided
        if request.POST.get('first_name'):
            request.user.first_name = request.POST.get('first_name')
        if request.POST.get('last_name'):
            request.user.last_name = request.POST.get('last_name')
        request.user.save()
        
    except Exception as e:
        logger.error(f"Error updating customer info: {e}")

def update_customer_info_from_payment_intent(user, payment_intent):
    """Update customer info from successful payment intent"""
    try:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        # Get payment method details
        payment_method = stripe.PaymentMethod.retrieve(payment_intent.payment_method)
        billing_details = payment_method.billing_details
        
        if hasattr(user, 'profile') and billing_details:
            profile = user.profile
            
            # Update from billing details
            if billing_details.address:
                addr = billing_details.address
                profile.address_line_1 = addr.line1 or ''
                profile.address_line_2 = addr.line2 or ''
                profile.city = addr.city or ''
                profile.state = addr.state or ''
                profile.postal_code = addr.postal_code or ''
                profile.country = addr.country or 'US'
            
            if billing_details.phone:
                profile.phone = billing_details.phone
            
            profile.save_payment_info = True
            profile.save()
            
            # Update user name
            if billing_details.name:
                name_parts = billing_details.name.split(' ', 1)
                user.first_name = name_parts[0]
                if len(name_parts) > 1:
                    user.last_name = name_parts[1]
                user.save()
        
    except Exception as e:
        logger.error(f"Error updating customer info from payment intent: {e}")

def create_order_from_cart(user, cart, payment_intent):
    """Create order from cart and payment intent"""
    from decimal import Decimal
    
    # Create order
    order = Order.objects.create(
        user=user,
        email=user.email,
        status='confirmed',
        subtotal=cart.subtotal,
        tax_amount=cart.tax_amount,
        shipping_cost=cart.shipping_cost,
        total=cart.total,
        stripe_payment_intent_id=payment_intent.id,
        payment_status='paid'
    )
    
    # Create order items
    for cart_item in cart.items.all():
        OrderItem.objects.create(
            order=order,
            artwork=cart_item.artwork,
            item_type=cart_item.item_type,
            print_size=cart_item.print_size,
            frame_option=cart_item.frame_option,
            quantity=cart_item.quantity,
            unit_price=cart_item.unit_price,
            total_price=cart_item.total_price
        )
    
    # Update shipping info from Stripe if available
    try:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        customer = stripe.Customer.retrieve(payment_intent.customer)
        
        if customer.shipping:
            order.shipping_name = customer.shipping.name
            addr = customer.shipping.address
            order.shipping_address_line_1 = addr.line1
            order.shipping_address_line_2 = addr.line2 or ''
            order.shipping_city = addr.city
            order.shipping_state = addr.state
            order.shipping_postal_code = addr.postal_code
            order.shipping_country = addr.country
            order.save()
            
    except Exception as e:
        logger.error(f"Error updating order shipping info: {e}")
    
    return order

@login_required
def order_success(request, order_id):
    """Order success page"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    context = {
        'order': order,
        'show_save_info_message': request.GET.get('saved_info') == 'true'
    }
    
    return render(request, 'orders/order_success.html', context)
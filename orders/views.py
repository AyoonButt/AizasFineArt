import json
import stripe
from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from django.db import transaction

from .models import Order, OrderItem, Cart, CartItem, OrderStatusUpdate, RefundRequest
from .luma_prints_api import send_print_order_to_luma, LumaPrintsWebhookHandler
from artwork.models import Artwork
from userprofiles.models import UserProfile


def get_item_price(artwork, item_type):
    """
    Centralized pricing function to ensure consistency across cart and checkout
    SECURITY: Always use server-side pricing, never trust frontend prices
    """
    if item_type == 'original':
        return artwork.price if artwork.price else Decimal('0.00')
    else:
        # Print pricing - MUST match frontend display prices
        print_prices = {
            'print-8x10': Decimal('45.00'),
            'print-11x14': Decimal('65.00'), 
            'print-16x20': Decimal('95.00'),
            'print-24x30': Decimal('155.00'),
        }
        return print_prices.get(item_type, Decimal('45.00'))


# Configure Stripe
stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')
stripe.api_version = '2023-10-16'  # Required for automatic tax


class CheckoutView(View):
    """Handle checkout page display and processing"""
    
    def get(self, request):
        """Display checkout page with cart items"""
        # Clear any leftover direct checkout items to avoid conflicts
        if 'direct_checkout_items' in request.session:
            del request.session['direct_checkout_items']
            print("Cleared leftover direct checkout items for cart checkout")
        
        # Get or create cart
        cart = self.get_or_create_cart(request)
        
        if not cart.items.exists():
            messages.warning(request, 'Your cart is empty.')
            return redirect('shop')
        
        context = {
            'cart': cart,
            'stripe_public_key': getattr(settings, 'STRIPE_PUBLISHABLE_KEY', ''),
        }
        
        return render(request, 'checkout.html', context)
    
    def post(self, request):
        """Process completed checkout"""
        try:
            with transaction.atomic():
                # Get cart
                cart = self.get_or_create_cart(request)
                
                if not cart.items.exists():
                    return JsonResponse({'error': 'Cart is empty'}, status=400)
                
                # Create order from form data
                order = self.create_order_from_request(request, cart)
                
                # Clear cart
                cart.items.all().delete()
                
                # Send confirmation emails
                self.send_order_emails(order)
                
                # Send print orders to Luma Prints if applicable
                print_result = send_print_order_to_luma(order)
                if print_result['status'] == 'success':
                    notes = f"Order confirmed and payment processed. Print order sent to Luma Prints (ID: {print_result.get('luma_order_id', 'N/A')})"
                else:
                    notes = f"Order confirmed and payment processed. Print order issue: {print_result['message']}"
                
                # Update order status
                OrderStatusUpdate.objects.create(
                    order=order,
                    new_status='confirmed',
                    notes=notes
                )
                
                return JsonResponse({
                    'success': True,
                    'order_number': order.order_number,
                    'redirect_url': f'/orders/confirmation/{order.order_number}/'
                })
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def get_or_create_cart(self, request):
        """Get or create cart for user or session"""
        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
        else:
            session_id = request.session.session_key
            if not session_id:
                request.session.create()
                session_id = request.session.session_key
            cart, created = Cart.objects.get_or_create(session_id=session_id)
        
        return cart
    
    def create_order_from_request(self, request, cart):
        """Create order from checkout form data"""
        # Extract form data
        form_data = request.POST
        
        # Get shipping country for accurate calculations
        shipping_country = form_data.get('billing_country', 'US')
        
        # Get Stripe payment intent to retrieve calculated tax
        payment_intent_id = form_data.get('payment_intent_id', '')
        stripe_tax_amount = Decimal('0.00')
        
        if payment_intent_id:
            try:
                intent = stripe.PaymentIntent.retrieve(payment_intent_id)
                if hasattr(intent, 'automatic_tax') and intent.automatic_tax and intent.automatic_tax.amount:
                    stripe_tax_amount = Decimal(str(intent.automatic_tax.amount / 100))
                    print(f"Retrieved Stripe tax amount: ${stripe_tax_amount}")
            except Exception as e:
                print(f"Failed to retrieve Stripe tax data: {e}")
        
        # Calculate totals using cart's methods for consistency
        subtotal = cart.subtotal
        shipping_amount = cart.shipping_cost(shipping_country)
        tax_amount = stripe_tax_amount  # Use Stripe calculated tax
        total_amount = subtotal + shipping_amount + tax_amount
        
        # Create order
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            subtotal=subtotal,
            tax_amount=tax_amount,
            shipping_amount=shipping_amount,
            total_amount=total_amount,
            
            # Customer information
            billing_name=f"{form_data.get('first_name', '')} {form_data.get('last_name', '')}".strip(),
            billing_email=form_data.get('email', ''),
            billing_phone=form_data.get('phone', ''),
            billing_address_1=form_data.get('billing_address_1', ''),
            billing_address_2=form_data.get('billing_address_2', ''),
            billing_city=form_data.get('billing_city', ''),
            billing_state=form_data.get('billing_state', ''),
            billing_postal_code=form_data.get('billing_postal_code', ''),
            billing_country=form_data.get('billing_country', 'US'),
            
            # Shipping information (use billing if same)
            shipping_name=form_data.get('shipping_first_name', '') and f"{form_data.get('shipping_first_name', '')} {form_data.get('shipping_last_name', '')}".strip(),
            shipping_address_1=form_data.get('shipping_address_1', ''),
            shipping_address_2=form_data.get('shipping_address_2', ''),
            shipping_city=form_data.get('shipping_city', ''),
            shipping_state=form_data.get('shipping_state', ''),
            shipping_postal_code=form_data.get('shipping_postal_code', ''),
            shipping_country=form_data.get('shipping_country', ''),
            
            # Payment information
            payment_method='stripe',
            stripe_payment_intent_id=form_data.get('payment_intent_id', ''),
            
            # Notes
            notes=form_data.get('order_notes', ''),
            
            # Status
            status='confirmed',
            payment_status='completed',
            confirmed_at=timezone.now()
        )
        
        # Create order items from cart
        for cart_item in cart.items.all():
            order_item = OrderItem.objects.create(
                order=order,
                artwork=cart_item.artwork,
                item_type=cart_item.item_type,
                title=cart_item.artwork.title,
                description=f"{cart_item.artwork.title} - {cart_item.get_item_type_display()}",
                unit_price=cart_item.unit_price,
                quantity=cart_item.quantity,
                total_price=cart_item.total_price,
                
                # Print specifications if applicable
                print_size=cart_item.get_item_type_display() if 'print' in cart_item.item_type else '',
            )
            # Note: Original artwork availability is automatically handled by OrderItem.save() method
        
        return order
    
    def calculate_tax(self, subtotal):
        """Calculate tax amount (Texas sales tax)"""
        tax_rate = Decimal('0.0825')  # 8.25% Texas sales tax
        return subtotal * tax_rate
    
    def send_order_emails(self, order):
        """Send confirmation emails to customer and admin"""
        try:
            # Customer confirmation email
            customer_subject = f'Order Confirmation - {order.order_number}'
            customer_message = render_to_string('emails/order_confirmation.html', {'order': order})
            
            send_mail(
                customer_subject,
                customer_message,
                settings.DEFAULT_FROM_EMAIL,
                [order.billing_email],
                html_message=customer_message
            )
            
            # Admin notification email
            admin_subject = f'New Order Received - {order.order_number}'
            admin_message = render_to_string('emails/admin_order_notification.html', {'order': order})
            
            send_mail(
                admin_subject,
                admin_message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.ADMIN_EMAIL] if hasattr(settings, 'ADMIN_EMAIL') else [settings.DEFAULT_FROM_EMAIL],
                html_message=admin_message
            )
            
        except Exception as e:
            # Log email error but don't fail the order
            print(f"Failed to send order emails: {e}")


@require_POST
def create_payment_intent(request):
    """Create Stripe PaymentIntent for checkout with automatic tax calculation"""
    try:
        # Extract shipping country from form data
        shipping_country = request.POST.get('billing_country', 'US')
        print(f"=== PAYMENT INTENT CREATION ===")
        print(f"Shipping country: {shipping_country}")
        
        # Check if this is a direct checkout
        direct_items = request.session.get('direct_checkout_items')
        print(f"Direct checkout items in session: {len(direct_items) if direct_items else 0}")
        
        if direct_items:
            # Handle direct checkout
            temp_cart = DirectCheckoutView().create_temp_cart(direct_items)
            subtotal = temp_cart.subtotal
            shipping_amount = temp_cart.shipping_cost(shipping_country)
            
            # Create line items for Stripe tax calculation
            line_items = []
            for item in temp_cart.all():
                line_items.append({
                    'amount': int(item.unit_price * 100),  # Convert to cents
                    'quantity': item.quantity,
                    'reference': f"{item.artwork.id}_{item.item_type}",
                    'tax_code': 'txcd_99999999',  # General tangible goods
                })
            
            # Add shipping as line item if applicable
            if shipping_amount > 0:
                line_items.append({
                    'amount': int(shipping_amount * 100),
                    'quantity': 1,
                    'reference': 'shipping',
                    'tax_code': 'txcd_92010001',  # Shipping
                })
            
            metadata = {
                'direct_checkout': 'true',
                'user_id': str(request.user.id) if request.user.is_authenticated else 'anonymous',
                'shipping_country': shipping_country,
            }
        else:
            print("Using regular cart checkout (no direct items)")
            # Handle regular cart checkout
            if request.user.is_authenticated:
                cart = Cart.objects.get(user=request.user)
            else:
                session_id = request.session.session_key
                cart = Cart.objects.get(session_id=session_id)
            
            if not cart.items.exists():
                return JsonResponse({'error': 'Cart is empty'}, status=400)
            
            subtotal = cart.subtotal
            shipping_amount = cart.shipping_cost(shipping_country)
            
            # Create line items for Stripe tax calculation
            line_items = []
            for item in cart.items.all():
                line_items.append({
                    'amount': int(item.unit_price * 100),  # Convert to cents
                    'quantity': item.quantity,
                    'reference': f"{item.artwork.id}_{item.item_type}",
                    'tax_code': 'txcd_99999999',  # General tangible goods
                })
            
            # Add shipping as line item if applicable
            if shipping_amount > 0:
                line_items.append({
                    'amount': int(shipping_amount * 100),
                    'quantity': 1,
                    'reference': 'shipping',
                    'tax_code': 'txcd_92010001',  # Shipping
                })
            
            metadata = {
                'cart_id': str(cart.id),
                'user_id': str(request.user.id) if request.user.is_authenticated else 'anonymous',
                'shipping_country': shipping_country,
            }
        
        # Calculate total before tax for PaymentIntent
        total_before_tax = subtotal + shipping_amount
        
        print(f"Subtotal: ${subtotal}, Shipping: ${shipping_amount}, Total before tax: ${total_before_tax}")
        print(f"Line items count: {len(line_items)}")
        
        # For now, create PaymentIntent without automatic tax (will be handled at checkout confirmation)
        # This allows the checkout to work while Stripe automatic tax requires additional setup
        stripe_cents = int(total_before_tax * 100)
        
        print(f"Creating PaymentIntent for ${total_before_tax} (before tax)")
        
        intent = stripe.PaymentIntent.create(
            amount=stripe_cents,  # Amount before tax
            currency='usd',
            metadata=metadata,
            automatic_payment_methods={
                'enabled': True,
            }
        )
        
        # For now, we'll calculate a simple estimated tax for display purposes
        # In production, you would either:
        # 1. Set up Stripe Tax properly with business verification
        # 2. Use a third-party tax service like TaxJar
        # 3. Calculate tax manually based on rates
        
        estimated_tax = Decimal('0.00')
        if shipping_country == 'US':
            # Simple estimation for US orders (you would use proper tax rates)
            # This is just for demonstration - replace with actual tax calculation
            estimated_tax = (total_before_tax * Decimal('0.08')).quantize(Decimal('0.01'))  # Rough 8% estimate
        
        final_total = total_before_tax + estimated_tax
        calculated_tax = estimated_tax
        
        print(f"Estimated tax: ${calculated_tax}")
        print(f"Final total with estimated tax: ${final_total}")
        
        print(f"Stripe PaymentIntent created: {intent.id} for ${final_total}")
        
        return JsonResponse({
            'client_secret': intent.client_secret,
            'amount': float(final_total),
            'subtotal': float(subtotal),
            'shipping': float(shipping_amount),
            'tax': float(calculated_tax),
            'stripe_tax_enabled': hasattr(intent, 'automatic_tax') and intent.automatic_tax is not None
        })
        
    except Cart.DoesNotExist:
        return JsonResponse({'error': 'Cart not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


class CartView(View):
    """Handle cart operations"""
    
    def get(self, request):
        """Display cart page"""
        # Clear any leftover direct checkout items when viewing cart
        if 'direct_checkout_items' in request.session:
            del request.session['direct_checkout_items']
            print("Cleared leftover direct checkout items for cart view")
        
        cart = self.get_or_create_cart(request)
        
        context = {
            'cart': cart,
        }
        
        return render(request, 'cart.html', context)
    
    def get_or_create_cart(self, request):
        """Get or create cart for user or session"""
        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
        else:
            session_id = request.session.session_key
            if not session_id:
                request.session.create()
                session_id = request.session.session_key
            cart, created = Cart.objects.get_or_create(session_id=session_id)
        
        return cart


@require_POST
def add_to_cart(request):
    """Add item to cart via AJAX"""
    try:
        artwork_id = request.POST.get('artwork_id')
        item_type = request.POST.get('item_type', 'original')
        quantity = int(request.POST.get('quantity', 1))
        
        artwork = get_object_or_404(Artwork, id=artwork_id)
        
        # Get or create cart
        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
        else:
            session_id = request.session.session_key
            if not session_id:
                request.session.create()
                session_id = request.session.session_key
            cart, created = Cart.objects.get_or_create(session_id=session_id)
        
        # Use centralized pricing function for consistency and security
        unit_price = get_item_price(artwork, item_type)
        
        # Add or update cart item
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            artwork=artwork,
            item_type=item_type,
            defaults={
                'quantity': quantity,
                'unit_price': unit_price
            }
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        return JsonResponse({
            'success': True,
            'item_count': cart.item_count,
            'cart_total': float(cart.total),
            'message': f'{artwork.title} added to cart'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_POST
def update_cart_item(request):
    """Update cart item quantity via AJAX"""
    try:
        item_id = request.POST.get('item_id')
        quantity = int(request.POST.get('quantity', 1))
        
        # Get cart item
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
        else:
            session_id = request.session.session_key
            cart_item = CartItem.objects.get(id=item_id, cart__session_id=session_id)
        
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
        else:
            cart_item.delete()
        
        cart = cart_item.cart
        
        return JsonResponse({
            'success': True,
            'item_count': cart.item_count,
            'cart_total': float(cart.total),
            'item_total': float(cart_item.total_price) if quantity > 0 else 0
        })
        
    except CartItem.DoesNotExist:
        return JsonResponse({'error': 'Item not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_POST
def remove_from_cart(request):
    """Remove item from cart via AJAX"""
    try:
        item_id = request.POST.get('item_id')
        
        # Get and delete cart item
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
        else:
            session_id = request.session.session_key
            cart_item = CartItem.objects.get(id=item_id, cart__session_id=session_id)
        
        cart = cart_item.cart
        cart_item.delete()
        
        return JsonResponse({
            'success': True,
            'item_count': cart.item_count,
            'cart_total': float(cart.total),
            'message': 'Item removed from cart'
        })
        
    except CartItem.DoesNotExist:
        return JsonResponse({'error': 'Item not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_POST
def apply_coupon(request):
    """Apply coupon code to cart"""
    try:
        data = json.loads(request.body)
        coupon_code = data.get('coupon_code', '').upper()
        
        # Simple coupon validation (expand as needed)
        valid_coupons = {
            'WELCOME10': 0.10,  # 10% off
            'SAVE15': 0.15,     # 15% off
            'FIRSTORDER': 0.20, # 20% off first order
        }
        
        if coupon_code not in valid_coupons:
            return JsonResponse({'success': False, 'message': 'Invalid coupon code'})
        
        discount_rate = valid_coupons[coupon_code]
        
        # Apply coupon to session (or implement proper coupon model)
        request.session['coupon_code'] = coupon_code
        request.session['coupon_discount'] = discount_rate
        
        return JsonResponse({
            'success': True,
            'message': f'Coupon applied! {int(discount_rate * 100)}% discount',
            'discount_rate': discount_rate
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


class OrderConfirmationView(View):
    """Display order confirmation page"""
    
    def get(self, request, order_number):
        """Show order confirmation"""
        order = get_object_or_404(Order, order_number=order_number)
        
        # Security: only show to order owner or admin
        if request.user.is_authenticated:
            if order.user != request.user and not request.user.is_staff:
                messages.error(request, 'Order not found.')
                return redirect('home')
        
        context = {
            'order': order,
        }
        
        return render(request, 'orders/confirmation.html', context)


@login_required
def order_history(request):
    """Display user's order history"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'orders': orders,
    }
    
    return render(request, 'orders/history.html', context)


class OrderDetailView(View):
    """Display detailed order information"""
    
    @method_decorator(login_required)
    def get(self, request, order_number):
        """Show detailed order information with tracking data"""
        order = get_object_or_404(Order, order_number=order_number)
        
        # Security: only show to order owner or admin
        if order.user != request.user and not request.user.is_staff:
            messages.error(request, 'Order not found.')
            return redirect('orders:history')
        
        # Prepare order tracking data for React component
        # Handle tracking stages with proper datetime serialization
        tracking_stages = []
        for stage in order.tracking_stages:
            stage_data = {
                'key': stage['key'],
                'title': stage['title'],
                'description': stage['description'],
                'completed': stage['completed'],
                'timestamp': stage['timestamp'].isoformat() if stage['timestamp'] else None,
                'icon': stage['icon']
            }
            tracking_stages.append(stage_data)
        
        order_tracking_data = {
            'order_number': order.order_number,
            'status': order.status,
            'tracking_number': order.tracking_number or '',
            'carrier': order.carrier or '',
            'carrier_tracking_url': order.get_carrier_tracking_url(),
            'tracking_percentage': order.tracking_percentage,
            'tracking_stages': tracking_stages,
            'luma_prints_status': order.luma_prints_status or '',
            'luma_prints_tracking_url': order.luma_prints_tracking_url or '',
            'luma_prints_updated_at': order.luma_prints_updated_at.isoformat() if order.luma_prints_updated_at else None,
            'estimated_delivery': order.estimated_delivery.isoformat() if order.estimated_delivery else None,
            'status_updates': [
                {
                    'id': update.id,
                    'new_status': update.new_status,
                    'notes': update.notes,
                    'timestamp': update.timestamp.isoformat(),
                } for update in order.status_updates.all()[:10]  # Latest 10 updates
            ]
        }
        
        context = {
            'order': order,
            'order_tracking_data': json.dumps(order_tracking_data),
        }
        
        return render(request, 'orders/order_detail_tracking.html', context)


@login_required
@require_POST
def cancel_order(request, order_number):
    """Cancel an order if allowed"""
    try:
        order = get_object_or_404(Order, order_number=order_number)
        
        # Security: only allow order owner or admin
        if order.user != request.user and not request.user.is_staff:
            return JsonResponse({'success': False, 'message': 'Order not found'}, status=404)
        
        # Check if order can be cancelled
        if not order.can_be_cancelled():
            return JsonResponse({
                'success': False, 
                'message': 'This order cannot be cancelled. Please contact support if you need assistance.'
            }, status=400)
        
        with transaction.atomic():
            # Update order status
            old_status = order.status
            order.status = 'cancelled'
            order.save()
            
            # Create status update record
            OrderStatusUpdate.objects.create(
                order=order,
                previous_status=old_status,
                new_status='cancelled',
                notes=f"Order cancelled by customer: {request.user.get_full_name() or request.user.username}",
                updated_by=request.user
            )
            
            # If payment was completed, we should process refund automatically
            if order.payment_status == 'completed':
                try:
                    # Attempt to refund via Stripe
                    if order.stripe_payment_intent_id:
                        refund = stripe.Refund.create(
                            payment_intent=order.stripe_payment_intent_id,
                            reason='requested_by_customer'
                        )
                        
                        # Update payment status
                        order.payment_status = 'refunded'
                        order.save()
                        
                        # Create additional status update for refund
                        OrderStatusUpdate.objects.create(
                            order=order,
                            previous_status='cancelled',
                            new_status='cancelled',
                            notes=f"Automatic refund processed: {refund.id}",
                            updated_by=request.user
                        )
                        
                except stripe.error.StripeError as e:
                    # Log the error but don't fail the cancellation
                    OrderStatusUpdate.objects.create(
                        order=order,
                        previous_status='cancelled',
                        new_status='cancelled',
                        notes=f"Order cancelled but automatic refund failed: {str(e)}. Manual refund required.",
                        updated_by=request.user
                    )
            
            # Send cancellation email
            try:
                customer_subject = f'Order Cancellation Confirmation - {order.order_number}'
                customer_message = render_to_string('emails/order_cancelled.html', {'order': order})
                
                send_mail(
                    customer_subject,
                    customer_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [order.billing_email],
                    html_message=customer_message
                )
                
                # Notify admin
                admin_subject = f'Order Cancelled - {order.order_number}'
                admin_message = render_to_string('emails/admin_order_cancelled.html', {
                    'order': order,
                    'cancelled_by': request.user
                })
                
                send_mail(
                    admin_subject,
                    admin_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.ADMIN_EMAIL] if hasattr(settings, 'ADMIN_EMAIL') else [settings.DEFAULT_FROM_EMAIL],
                    html_message=admin_message
                )
                
            except Exception as e:
                # Log email error but don't fail the cancellation
                print(f"Failed to send cancellation emails: {e}")
        
        return JsonResponse({
            'success': True,
            'message': 'Order has been successfully cancelled.'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


@login_required
@require_POST
def request_refund(request, order_number):
    """Submit a refund request for an order"""
    try:
        data = json.loads(request.body)
        reason = data.get('reason', '').strip()
        
        if not reason:
            return JsonResponse({'success': False, 'message': 'Please provide a reason for the refund'}, status=400)
        
        order = get_object_or_404(Order, order_number=order_number)
        
        # Security: only allow order owner or admin
        if order.user != request.user and not request.user.is_staff:
            return JsonResponse({'success': False, 'message': 'Order not found'}, status=404)
        
        # Check if order can be refunded
        if not order.can_be_refunded():
            return JsonResponse({
                'success': False, 
                'message': 'This order is not eligible for refund. Please contact support if you need assistance.'
            }, status=400)
        
        # Check if refund request already exists
        if hasattr(order, 'refund_request'):
            return JsonResponse({
                'success': False, 
                'message': 'A refund request has already been submitted for this order.'
            }, status=400)
        
        with transaction.atomic():
            # Create refund request
            refund_request = RefundRequest.objects.create(
                order=order,
                reason=reason,
                refund_amount=order.total_amount
            )
            
            # Create status update record
            OrderStatusUpdate.objects.create(
                order=order,
                previous_status=order.status,
                new_status=order.status,  # Status doesn't change until admin approves
                notes=f"Refund requested by customer: {reason}",
                updated_by=request.user
            )
            
            # Send refund request emails
            try:
                # Customer confirmation
                customer_subject = f'Refund Request Received - {order.order_number}'
                customer_message = render_to_string('emails/refund_request_confirmation.html', {
                    'order': order,
                    'refund_request': refund_request
                })
                
                send_mail(
                    customer_subject,
                    customer_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [order.billing_email],
                    html_message=customer_message
                )
                
                # Admin notification
                admin_subject = f'Refund Request - {order.order_number}'
                admin_message = render_to_string('emails/admin_refund_request.html', {
                    'order': order,
                    'refund_request': refund_request,
                    'requested_by': request.user
                })
                
                send_mail(
                    admin_subject,
                    admin_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.ADMIN_EMAIL] if hasattr(settings, 'ADMIN_EMAIL') else [settings.DEFAULT_FROM_EMAIL],
                    html_message=admin_message
                )
                
            except Exception as e:
                # Log email error but don't fail the request
                print(f"Failed to send refund request emails: {e}")
        
        return JsonResponse({
            'success': True,
            'message': 'Refund request has been submitted successfully. You will receive an email confirmation shortly.'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid request data'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


class DirectCheckoutView(View):
    """Handle direct checkout for Buy Now functionality (bypasses cart)"""
    
    def get(self, request):
        """Display checkout page with direct items"""
        # Get direct checkout items from session
        direct_items = request.session.get('direct_checkout_items', [])
        
        if not direct_items:
            messages.warning(request, 'No items selected for checkout.')
            return redirect('shop')
        
        # Create temporary cart-like object for template
        temp_cart = self.create_temp_cart(direct_items)
        
        context = {
            'cart': temp_cart,
            'direct_checkout': True,
            'stripe_public_key': getattr(settings, 'STRIPE_PUBLISHABLE_KEY', ''),
        }
        
        return render(request, 'checkout.html', context)
    
    def post(self, request):
        """Process direct checkout (same as regular checkout but uses session items)"""
        try:
            with transaction.atomic():
                # Get direct checkout items from session
                direct_items = request.session.get('direct_checkout_items', [])
                
                if not direct_items:
                    return JsonResponse({'error': 'No items for checkout'}, status=400)
                
                # Create temporary cart object
                temp_cart = self.create_temp_cart(direct_items)
                
                # Create order from form data (similar to regular checkout)
                order = self.create_order_from_direct_items(request, direct_items, temp_cart)
                
                # Clear direct checkout items from session
                if 'direct_checkout_items' in request.session:
                    del request.session['direct_checkout_items']
                
                # Send confirmation emails
                self.send_order_emails(order)
                
                # Send print orders to Luma Prints if applicable
                print_result = send_print_order_to_luma(order)
                if print_result['status'] == 'success':
                    notes = f"Direct checkout order confirmed. Print order sent to Luma Prints (ID: {print_result.get('luma_order_id', 'N/A')})"
                else:
                    notes = f"Direct checkout order confirmed. Print order issue: {print_result['message']}"
                
                # Update order status
                OrderStatusUpdate.objects.create(
                    order=order,
                    new_status='confirmed',
                    notes=notes
                )
                
                return JsonResponse({
                    'success': True,
                    'order_number': order.order_number,
                    'redirect_url': f'/orders/confirmation/{order.order_number}/'
                })
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def create_temp_cart(self, direct_items):
        """Create a temporary cart-like object for template rendering"""
        from decimal import Decimal
        
        class TempCart:
            def __init__(self, items_data):
                self.items_data = items_data
                self._items = []
                self._subtotal = Decimal('0')
                
                # Process items
                for item_data in items_data:
                    artwork = Artwork.objects.get(id=item_data['artwork_id'])
                    
                    # SERVER-SIDE PRICE LOOKUP (SECURE)
                    # Don't trust frontend prices - use server-side pricing
                    item_type = item_data['item_type']
                    unit_price = get_item_price(artwork, item_type)
                    
                    print(f"  {item_type}: ${unit_price}")
                    
                    # Create temp item object
                    temp_item = type('TempItem', (), {
                        'id': f"temp_{item_data['artwork_id']}_{item_data['item_type']}",
                        'artwork': artwork,
                        'item_type': item_data['item_type'],
                        'quantity': item_data['quantity'],
                        'unit_price': unit_price,  # Use server-side price
                        'total_price': unit_price * item_data['quantity'],
                        'item_type_display': self.get_item_type_display(item_data['item_type'])
                    })()
                    
                    self._items.append(temp_item)
                    self._subtotal += temp_item.total_price
            
            def get_item_type_display(self, item_type):
                type_map = {
                    'original': 'Original Artwork',
                    'print-8x10': '8" × 10" Print',
                    'print-11x14': '11" × 14" Print', 
                    'print-16x20': '16" × 20" Print',
                    'print-24x30': '24" × 30" Print',
                }
                return type_map.get(item_type, item_type)
            
            @property
            def subtotal(self):
                return self._subtotal
            
            def shipping_cost(self, shipping_country='US'):
                """Calculate shipping cost based on country"""
                if self._subtotal <= 0:
                    return Decimal('0.00')
                    
                # Free shipping for US, $12 flat rate for international
                if shipping_country == 'US':
                    return Decimal('0.00')  # Free shipping for US
                else:
                    return Decimal('12.00')  # Flat rate for international
            
            @property
            def tax_amount(self):
                """Tax amount placeholder - will be calculated by Stripe"""
                return Decimal('0.00')  # Stripe will handle tax calculation
            
            def total(self, shipping_country='US', tax_amount=None):
                """Calculate total including shipping and tax"""
                shipping = self.shipping_cost(shipping_country)
                tax = tax_amount if tax_amount is not None else self.tax_amount
                return (self.subtotal + shipping + tax).quantize(Decimal('0.01'))
            
            @property
            def item_count(self):
                return sum(item.quantity for item in self._items)
            
            def all(self):
                return self._items
        
        # For template compatibility
        temp_cart = TempCart(direct_items)
        temp_cart.items = type('Items', (), {'all': lambda: temp_cart.all()})()
        
        return temp_cart
    
    def create_order_from_direct_items(self, request, direct_items, temp_cart):
        """Create order from direct checkout items"""
        # Extract form data
        form_data = request.POST
        
        # Get shipping country for accurate calculations
        shipping_country = form_data.get('billing_country', 'US')
        
        # Get Stripe payment intent to retrieve calculated tax
        payment_intent_id = form_data.get('payment_intent_id', '')
        stripe_tax_amount = Decimal('0.00')
        
        if payment_intent_id:
            try:
                intent = stripe.PaymentIntent.retrieve(payment_intent_id)
                if hasattr(intent, 'automatic_tax') and intent.automatic_tax and intent.automatic_tax.amount:
                    stripe_tax_amount = Decimal(str(intent.automatic_tax.amount / 100))
                    print(f"Direct checkout - Retrieved Stripe tax amount: ${stripe_tax_amount}")
            except Exception as e:
                print(f"Direct checkout - Failed to retrieve Stripe tax data: {e}")
        
        # Calculate totals using temp cart's methods for consistency
        subtotal = temp_cart.subtotal
        shipping_amount = temp_cart.shipping_cost(shipping_country)
        tax_amount = stripe_tax_amount  # Use Stripe calculated tax
        total_amount = subtotal + shipping_amount + tax_amount
        
        # Create order
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            subtotal=subtotal,
            tax_amount=tax_amount,
            shipping_amount=shipping_amount,
            total_amount=total_amount,
            
            # Customer information
            billing_name=f"{form_data.get('first_name', '')} {form_data.get('last_name', '')}".strip(),
            billing_email=form_data.get('email', ''),
            billing_phone=form_data.get('phone', ''),
            billing_address_1=form_data.get('billing_address_1', ''),
            billing_address_2=form_data.get('billing_address_2', ''),
            billing_city=form_data.get('billing_city', ''),
            billing_state=form_data.get('billing_state', ''),
            billing_postal_code=form_data.get('billing_postal_code', ''),
            billing_country=form_data.get('billing_country', 'US'),
            
            # Shipping information
            shipping_name=form_data.get('shipping_first_name', '') and f"{form_data.get('shipping_first_name', '')} {form_data.get('shipping_last_name', '')}".strip(),
            shipping_address_1=form_data.get('shipping_address_1', ''),
            shipping_address_2=form_data.get('shipping_address_2', ''),
            shipping_city=form_data.get('shipping_city', ''),
            shipping_state=form_data.get('shipping_state', ''),
            shipping_postal_code=form_data.get('shipping_postal_code', ''),
            shipping_country=form_data.get('shipping_country', ''),
            
            # Payment information
            payment_method='stripe',
            stripe_payment_intent_id=form_data.get('payment_intent_id', ''),
            
            # Notes
            notes=form_data.get('order_notes', ''),
            
            # Status
            status='confirmed',
            payment_status='completed',
            confirmed_at=timezone.now()
        )
        
        # Create order items from direct items
        for item_data in direct_items:
            artwork = Artwork.objects.get(id=item_data['artwork_id'])
            
            OrderItem.objects.create(
                order=order,
                artwork=artwork,
                item_type=item_data['item_type'],
                title=artwork.title,
                description=f"{artwork.title} - {temp_cart.get_item_type_display(item_data['item_type'])}",
                unit_price=Decimal(str(item_data['price'])),
                quantity=item_data['quantity'],
                total_price=Decimal(str(item_data['price'])) * item_data['quantity'],
                
                # Print specifications if applicable
                print_size=temp_cart.get_item_type_display(item_data['item_type']) if 'print' in item_data['item_type'] else '',
            )
        
        return order
    
    def calculate_tax(self, subtotal):
        """Calculate tax amount (Texas sales tax)"""
        tax_rate = Decimal('0.0825')  # 8.25% Texas sales tax
        return subtotal * tax_rate
    
    def send_order_emails(self, order):
        """Send confirmation emails to customer and admin"""
        try:
            # Customer confirmation email
            customer_subject = f'Order Confirmation - {order.order_number}'
            customer_message = render_to_string('emails/order_confirmation.html', {'order': order})
            
            send_mail(
                customer_subject,
                customer_message,
                settings.DEFAULT_FROM_EMAIL,
                [order.billing_email],
                html_message=customer_message
            )
            
            # Admin notification email
            admin_subject = f'New Order Received - {order.order_number}'
            admin_message = render_to_string('emails/admin_order_notification.html', {'order': order})
            
            send_mail(
                admin_subject,
                admin_message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.ADMIN_EMAIL] if hasattr(settings, 'ADMIN_EMAIL') else [settings.DEFAULT_FROM_EMAIL],
                html_message=admin_message
            )
            
        except Exception as e:
            # Log email error but don't fail the order
            print(f"Failed to send order emails: {e}")


@require_POST  
def clear_direct_checkout(request):
    """Clear direct checkout items from session"""
    if 'direct_checkout_items' in request.session:
        del request.session['direct_checkout_items']
    return JsonResponse({'success': True})


@require_POST
def setup_direct_checkout(request):
    """Set up direct checkout items in session"""
    try:
        data = json.loads(request.body)
        items = data.get('items', [])
        
        print(f"=== DIRECT CHECKOUT SETUP ===")
        print(f"Received {len(items)} items:")
        for i, item in enumerate(items):
            print(f"  {i+1}. {item.get('item_type')} - qty:{item.get('quantity')} - artwork_id:{item.get('artwork_id')}")
        print(f"Raw items data: {items}")
        print(f"=== END SETUP ===")
        
        if not items:
            return JsonResponse({'error': 'No items provided'}, status=400)
        
        # Store items in session for direct checkout
        request.session['direct_checkout_items'] = items
        
        return JsonResponse({
            'success': True,
            'redirect_url': '/orders/checkout/direct/'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_POST
def luma_prints_webhook(request):
    """Handle webhooks from Luma Prints"""
    try:
        # Get webhook data
        payload = json.loads(request.body)
        signature = request.headers.get('X-Luma-Signature', '')
        
        # Process webhook
        handler = LumaPrintsWebhookHandler()
        result = handler.handle_webhook(payload, signature)
        
        if result['status'] == 'success':
            return JsonResponse({'status': 'ok'})
        else:
            return JsonResponse(result, status=400)
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

"""
User Profile Management Views
Handles profile editing, payment methods, and account deletion
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.models import User
import stripe
import logging

from .models import UserProfile
from .forms import UserProfileForm, PersonalInfoForm
from orders.stripe_service import StripeCustomerService

logger = logging.getLogger(__name__)

@login_required
def profile_dashboard(request):
    """Main profile dashboard"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Get Stripe customer info
    stripe_customer = None
    payment_methods = []
    if profile.stripe_customer_id:
        try:
            stripe_customer = StripeCustomerService.create_or_get_customer(request.user)
            payment_methods = StripeCustomerService.get_customer_payment_methods(profile.stripe_customer_id)
        except Exception as e:
            logger.error(f"Error fetching Stripe data for user {request.user.id}: {e}")
    
    # Get recent orders
    recent_orders = request.user.orders.all().order_by('-created_at')[:5]
    
    context = {
        'profile': profile,
        'stripe_customer': stripe_customer,
        'payment_methods': payment_methods.data if payment_methods else [],
        'recent_orders': recent_orders,
        'has_saved_payment_info': bool(payment_methods.data if payment_methods else False),
    }
    
    return render(request, 'userprofiles/profile_dashboard.html', context)

@login_required
def edit_personal_info(request):
    """Edit personal information"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        user_form = PersonalInfoForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            
            # Sync with Stripe if customer exists
            if profile.stripe_customer_id:
                try:
                    StripeCustomerService.sync_customer_with_profile(request.user)
                    messages.success(request, 'Profile updated successfully! Your billing information has been synced.')
                except Exception as e:
                    logger.error(f"Error syncing with Stripe: {e}")
                    messages.success(request, 'Profile updated successfully! (Note: Billing info sync had an issue)')
            else:
                messages.success(request, 'Profile updated successfully!')
            
            return redirect('userprofiles:profile_dashboard')
    else:
        user_form = PersonalInfoForm(instance=request.user)
        profile_form = UserProfileForm(instance=profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'profile': profile
    }
    
    return render(request, 'userprofiles/edit_personal_info.html', context)

@login_required
def manage_payment_methods(request):
    """Manage saved payment methods"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Get Stripe customer and payment methods
    customer = StripeCustomerService.create_or_get_customer(request.user)
    payment_methods = StripeCustomerService.get_customer_payment_methods(customer.id)
    
    context = {
        'profile': profile,
        'customer': customer,
        'payment_methods': payment_methods.data,
        'stripe_public_key': settings.STRIPE_PUBLISHABLE_KEY,
    }
    
    return render(request, 'userprofiles/manage_payment_methods.html', context)

@login_required
def add_payment_method(request):
    """Add new payment method"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    customer = StripeCustomerService.create_or_get_customer(request.user)
    
    # Create setup intent
    try:
        setup_intent = StripeCustomerService.create_setup_intent(customer.id)
    except Exception as e:
        logger.error(f"Error creating setup intent: {e}")
        messages.error(request, "Unable to initialize payment method setup. Please try again.")
        return redirect('userprofiles:manage_payment_methods')
    
    context = {
        'profile': profile,
        'customer': customer,
        'client_secret': setup_intent.client_secret,
        'stripe_public_key': settings.STRIPE_PUBLISHABLE_KEY,
    }
    
    return render(request, 'userprofiles/add_payment_method.html', context)

@require_POST
@login_required
def delete_payment_method(request, payment_method_id):
    """Delete a payment method"""
    try:
        success = StripeCustomerService.delete_payment_method(payment_method_id)
        if success:
            messages.success(request, 'Payment method removed successfully.')
        else:
            messages.error(request, 'Failed to remove payment method.')
    except Exception as e:
        logger.error(f"Error deleting payment method {payment_method_id}: {e}")
        messages.error(request, 'An error occurred while removing the payment method.')
    
    return redirect('userprofiles:manage_payment_methods')

@login_required
def manage_addresses(request):
    """Manage shipping addresses"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Get current address from Stripe if available
    stripe_address = None
    if profile.stripe_customer_id:
        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            customer = stripe.Customer.retrieve(profile.stripe_customer_id)
            stripe_address = customer.get('shipping', {}).get('address')
        except Exception as e:
            logger.error(f"Error fetching Stripe address: {e}")
    
    if request.method == 'POST':
        # Update address in both local profile and Stripe
        address_data = {
            'line1': request.POST.get('address_line_1'),
            'line2': request.POST.get('address_line_2', ''),
            'city': request.POST.get('city'),
            'state': request.POST.get('state'),
            'postal_code': request.POST.get('postal_code'),
            'country': request.POST.get('country', 'US')
        }
        
        # Update local profile
        profile.address_line_1 = address_data['line1']
        profile.address_line_2 = address_data['line2']
        profile.city = address_data['city']
        profile.state = address_data['state']
        profile.postal_code = address_data['postal_code']
        profile.country = address_data['country']
        profile.save()
        
        # Update Stripe customer
        if profile.stripe_customer_id:
            try:
                StripeCustomerService.update_customer_info(
                    profile.stripe_customer_id,
                    address=address_data,
                    shipping={
                        'name': request.user.get_full_name() or request.user.username,
                        'address': address_data
                    }
                )
                messages.success(request, 'Address updated successfully!')
            except Exception as e:
                logger.error(f"Error updating Stripe address: {e}")
                messages.success(request, 'Address updated locally, but there was an issue syncing with billing system.')
        else:
            messages.success(request, 'Address updated successfully!')
        
        return redirect('userprofiles:manage_addresses')
    
    context = {
        'profile': profile,
        'stripe_address': stripe_address,
    }
    
    return render(request, 'userprofiles/manage_addresses.html', context)

@login_required
def billing_portal(request):
    """Redirect to Stripe Customer Portal for full billing management"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if not profile.stripe_customer_id:
        # Create customer first
        customer = StripeCustomerService.create_or_get_customer(request.user)
    
    try:
        portal_session = StripeCustomerService.create_customer_portal_session(
            profile.stripe_customer_id,
            request.build_absolute_uri(reverse('userprofiles:profile_dashboard'))
        )
        return redirect(portal_session.url)
    except Exception as e:
        logger.error(f"Error creating billing portal session: {e}")
        messages.error(request, "Unable to access billing portal. Please try again.")
        return redirect('userprofiles:profile_dashboard')

@login_required
def account_settings(request):
    """Account settings and privacy controls"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Update privacy settings
        profile.profile_public = request.POST.get('profile_public') == 'on'
        profile.show_purchase_history = request.POST.get('show_purchase_history') == 'on'
        profile.newsletter_subscription = request.POST.get('newsletter_subscription') == 'on'
        profile.email_notifications = request.POST.get('email_notifications') == 'on'
        profile.save()
        
        messages.success(request, 'Account settings updated successfully!')
        return redirect('userprofiles:account_settings')
    
    context = {
        'profile': profile,
    }
    
    return render(request, 'userprofiles/account_settings.html', context)

@login_required
def delete_account_confirm(request):
    """Account deletion confirmation page"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Get user's data summary
    orders_count = request.user.orders.count()
    wishlist_count = request.user.wishlists.count()
    has_payment_methods = bool(profile.stripe_customer_id)
    
    context = {
        'profile': profile,
        'orders_count': orders_count,
        'wishlist_count': wishlist_count,
        'has_payment_methods': has_payment_methods,
    }
    
    return render(request, 'userprofiles/delete_account_confirm.html', context)

@require_POST
@login_required
def delete_account(request):
    """Delete user account and all associated data"""
    if request.POST.get('confirm_delete') != 'DELETE':
        messages.error(request, 'Account deletion not confirmed properly.')
        return redirect('userprofiles:delete_account_confirm')
    
    user = request.user
    profile = getattr(user, 'profile', None)
    
    try:
        # Delete Stripe data first
        if profile and profile.stripe_customer_id:
            try:
                profile.delete_stripe_data()
                logger.info(f"Deleted Stripe data for user {user.id}")
            except Exception as e:
                logger.error(f"Error deleting Stripe data for user {user.id}: {e}")
                # Continue with account deletion even if Stripe deletion fails
        
        # Log the deletion
        logger.info(f"User {user.id} ({user.username}) requested account deletion")
        
        # Delete user (cascade will handle related objects)
        user.delete()
        
        # Logout and redirect
        logout(request)
        messages.success(request, 'Your account has been successfully deleted. We\'re sorry to see you go!')
        return redirect('home')
        
    except Exception as e:
        logger.error(f"Error deleting account for user {user.id}: {e}")
        messages.error(request, 'An error occurred while deleting your account. Please contact support.')
        return redirect('userprofiles:delete_account_confirm')

@require_POST
@login_required
def sync_stripe_data(request):
    """Manually sync data from Stripe to local profile"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if not profile.stripe_customer_id:
        messages.warning(request, 'No Stripe customer data to sync.')
        return redirect('userprofiles:profile_dashboard')
    
    try:
        profile.sync_from_stripe()
        messages.success(request, 'Profile data synced from billing system successfully!')
    except Exception as e:
        logger.error(f"Error syncing Stripe data for user {request.user.id}: {e}")
        messages.error(request, 'Failed to sync data from billing system.')
    
    return redirect('userprofiles:profile_dashboard')
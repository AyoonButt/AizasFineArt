"""
Stripe Customer and Payment Management Service
Handles secure storage of billing/shipping info and payment methods
"""

import stripe
from django.conf import settings
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)

class StripeCustomerService:
    """Service for managing Stripe customers and payment methods"""
    
    @staticmethod
    def create_or_get_customer(user):
        """Create or retrieve Stripe customer for user"""
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        # Check if user already has a Stripe customer ID
        if hasattr(user, 'profile') and user.profile.stripe_customer_id:
            try:
                customer = stripe.Customer.retrieve(user.profile.stripe_customer_id)
                logger.info(f"Retrieved existing Stripe customer for user {user.id}")
                return customer
            except stripe.error.InvalidRequestError:
                logger.warning(f"Invalid Stripe customer ID for user {user.id}, creating new one")
        
        # Create new customer
        customer_data = {
            'email': user.email,
            'name': user.get_full_name() or user.username,
            'metadata': {
                'user_id': user.id,
                'username': user.username
            }
        }
        
        # Add existing profile data if available
        if hasattr(user, 'profile'):
            profile = user.profile
            if profile.phone:
                customer_data['phone'] = profile.phone
            
            # Add address if available
            if profile.address_line_1:
                customer_data['address'] = {
                    'line1': profile.address_line_1,
                    'line2': profile.address_line_2,
                    'city': profile.city,
                    'state': profile.state,
                    'postal_code': profile.postal_code,
                    'country': profile.country or 'US'
                }
                
                customer_data['shipping'] = {
                    'name': user.get_full_name() or user.username,
                    'address': customer_data['address']
                }
        
        try:
            customer = stripe.Customer.create(**customer_data)
            
            # Save customer ID to user profile
            if hasattr(user, 'profile'):
                user.profile.stripe_customer_id = customer.id
                user.profile.save(update_fields=['stripe_customer_id'])
            
            logger.info(f"Created new Stripe customer for user {user.id}")
            return customer
            
        except stripe.error.StripeError as e:
            logger.error(f"Error creating Stripe customer for user {user.id}: {e}")
            raise
    
    @staticmethod
    def create_setup_intent(customer_id, usage='off_session'):
        """Create setup intent for saving payment methods"""
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        try:
            setup_intent = stripe.SetupIntent.create(
                customer=customer_id,
                usage=usage,  # 'off_session' for future payments, 'on_session' for immediate
                payment_method_types=['card'],
                metadata={'purpose': 'save_payment_method'}
            )
            return setup_intent
        except stripe.error.StripeError as e:
            logger.error(f"Error creating setup intent for customer {customer_id}: {e}")
            raise
    
    @staticmethod
    def get_customer_payment_methods(customer_id):
        """Get all saved payment methods for customer"""
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        try:
            payment_methods = stripe.PaymentMethod.list(
                customer=customer_id,
                type='card'
            )
            return payment_methods
        except stripe.error.StripeError as e:
            logger.error(f"Error retrieving payment methods for customer {customer_id}: {e}")
            return {'data': []}
    
    @staticmethod
    def delete_payment_method(payment_method_id):
        """Delete a specific payment method"""
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        try:
            stripe.PaymentMethod.detach(payment_method_id)
            logger.info(f"Deleted payment method {payment_method_id}")
            return True
        except stripe.error.StripeError as e:
            logger.error(f"Error deleting payment method {payment_method_id}: {e}")
            return False
    
    @staticmethod
    def update_customer_info(customer_id, **kwargs):
        """Update customer information in Stripe"""
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        try:
            customer = stripe.Customer.modify(customer_id, **kwargs)
            logger.info(f"Updated customer {customer_id} information")
            return customer
        except stripe.error.StripeError as e:
            logger.error(f"Error updating customer {customer_id}: {e}")
            raise
    
    @staticmethod
    def create_customer_portal_session(customer_id, return_url):
        """Create Stripe Customer Portal session for full billing management"""
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        try:
            portal_session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=return_url
            )
            return portal_session
        except stripe.error.StripeError as e:
            logger.error(f"Error creating customer portal session for {customer_id}: {e}")
            raise
    
    @staticmethod
    def create_payment_intent(amount, customer_id, payment_method_id=None, save_payment_method=False):
        """Create payment intent for checkout"""
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        payment_intent_data = {
            'amount': int(amount * 100),  # Convert to cents
            'currency': 'usd',
            'customer': customer_id,
            'metadata': {'source': 'aizas_fine_art_checkout'}
        }
        
        # If using saved payment method
        if payment_method_id:
            payment_intent_data.update({
                'payment_method': payment_method_id,
                'confirmation_method': 'manual',
                'confirm': True
            })
        else:
            # For new payment methods
            payment_intent_data['setup_future_usage'] = 'off_session' if save_payment_method else None
        
        try:
            payment_intent = stripe.PaymentIntent.create(**payment_intent_data)
            return payment_intent
        except stripe.error.StripeError as e:
            logger.error(f"Error creating payment intent: {e}")
            raise
    
    @staticmethod
    def confirm_payment_intent(payment_intent_id, payment_method_id=None):
        """Confirm payment intent with payment method"""
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        try:
            if payment_method_id:
                payment_intent = stripe.PaymentIntent.confirm(
                    payment_intent_id,
                    payment_method=payment_method_id
                )
            else:
                payment_intent = stripe.PaymentIntent.confirm(payment_intent_id)
            
            return payment_intent
        except stripe.error.StripeError as e:
            logger.error(f"Error confirming payment intent {payment_intent_id}: {e}")
            raise
    
    @staticmethod
    def sync_customer_with_profile(user):
        """Sync Stripe customer data with user profile"""
        if not hasattr(user, 'profile') or not user.profile.stripe_customer_id:
            return
        
        stripe.api_key = settings.STRIPE_SECRET_KEY
        profile = user.profile
        
        try:
            customer = stripe.Customer.retrieve(user.profile.stripe_customer_id)
            
            # Prepare update data
            update_data = {
                'email': user.email,
                'name': user.get_full_name() or user.username,
            }
            
            # Add phone if available
            if profile.phone:
                update_data['phone'] = profile.phone
            
            # Add address if available
            if profile.address_line_1:
                update_data['address'] = {
                    'line1': profile.address_line_1,
                    'line2': profile.address_line_2 or '',
                    'city': profile.city,
                    'state': profile.state,
                    'postal_code': profile.postal_code,
                    'country': profile.country or 'US'
                }
                
                update_data['shipping'] = {
                    'name': user.get_full_name() or user.username,
                    'address': update_data['address']
                }
            
            # Update customer in Stripe
            stripe.Customer.modify(customer.id, **update_data)
            logger.info(f"Synced profile data to Stripe for user {user.id}")
            
        except stripe.error.StripeError as e:
            logger.error(f"Error syncing customer data for user {user.id}: {e}")

class StripeCheckoutService:
    """Service specifically for checkout operations"""
    
    @staticmethod
    def create_checkout_session(line_items, customer_id, success_url, cancel_url, mode='payment'):
        """Create Stripe Checkout session (alternative to custom checkout)"""
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        try:
            session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=['card'],
                line_items=line_items,
                mode=mode,
                success_url=success_url,
                cancel_url=cancel_url,
                billing_address_collection='auto',
                shipping_address_collection={
                    'allowed_countries': ['US', 'CA']
                },
                payment_intent_data={
                    'setup_future_usage': 'off_session'
                }
            )
            return session
        except stripe.error.StripeError as e:
            logger.error(f"Error creating checkout session: {e}")
            raise
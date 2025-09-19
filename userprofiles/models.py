from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Contact information
    phone = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    
    # Address information
    address_line_1 = models.CharField(max_length=100, blank=True)
    address_line_2 = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=50, blank=True)
    state = models.CharField(max_length=50, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=50, default='United States')
    
    # Preferences
    newsletter_subscription = models.BooleanField(default=True)
    email_notifications = models.BooleanField(default=True)
    preferred_contact_method = models.CharField(max_length=10, choices=[
        ('email', 'Email'),
        ('phone', 'Phone'),
        ('mail', 'Mail'),
    ], default='email')
    
    # Art preferences
    favorite_mediums = models.JSONField(default=list, blank=True, help_text="Array of favorite art mediums")
    favorite_subjects = models.JSONField(default=list, blank=True, help_text="Array of favorite art subjects")
    price_range_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_range_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Social media
    instagram_handle = models.CharField(max_length=100, blank=True)
    facebook_profile = models.URLField(blank=True)
    
    # Stripe integration
    stripe_customer_id = models.CharField(max_length=100, blank=True, null=True, help_text="Stripe customer ID")
    save_payment_info = models.BooleanField(default=False, help_text="User opted to save payment info")
    
    # Account information
    is_collector = models.BooleanField(default=False, help_text="Serious art collector status")
    is_artist = models.BooleanField(default=False, help_text="Fellow artist")
    referral_source = models.CharField(max_length=100, blank=True, help_text="How they found the website")
    
    # Privacy settings
    profile_public = models.BooleanField(default=False)
    show_purchase_history = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_active = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}'s Profile"

    def get_absolute_url(self):
        return reverse('userprofiles:profile', kwargs={'user_id': self.user.id})

    @property
    def full_address(self):
        """Return formatted full address"""
        address_parts = [
            self.address_line_1,
            self.address_line_2,
            f"{self.city}, {self.state} {self.postal_code}",
            self.country
        ]
        return "\n".join([part for part in address_parts if part])

    @property
    def display_name(self):
        """Return user's display name"""
        return self.user.get_full_name() or self.user.username

    def update_last_active(self):
        """Update last active timestamp"""
        self.last_active = timezone.now()
        self.save(update_fields=['last_active'])
    
    def get_stripe_customer(self):
        """Get or create Stripe customer"""
        from orders.stripe_service import StripeCustomerService
        return StripeCustomerService.create_or_get_customer(self.user)
    
    def get_saved_payment_methods(self):
        """Get user's saved payment methods from Stripe"""
        if not self.stripe_customer_id:
            return []
        from orders.stripe_service import StripeCustomerService
        return StripeCustomerService.get_customer_payment_methods(self.stripe_customer_id)
    
    def sync_from_stripe(self):
        """Sync profile data from Stripe customer"""
        if not self.stripe_customer_id:
            return
        
        try:
            import stripe
            from django.conf import settings
            stripe.api_key = settings.STRIPE_SECRET_KEY
            
            customer = stripe.Customer.retrieve(self.stripe_customer_id)
            
            # Update address from Stripe if available
            if customer.get('address'):
                addr = customer['address']
                self.address_line_1 = addr.get('line1', '')
                self.address_line_2 = addr.get('line2', '')
                self.city = addr.get('city', '')
                self.state = addr.get('state', '')
                self.postal_code = addr.get('postal_code', '')
                self.country = addr.get('country', 'US')
            
            # Update phone from Stripe if available
            if customer.get('phone'):
                self.phone = customer['phone']
            
            self.save()
        except Exception as e:
            print(f"Error syncing from Stripe: {e}")
    
    def delete_stripe_data(self):
        """Delete all Stripe data when user deletes account"""
        if not self.stripe_customer_id:
            return
        
        try:
            import stripe
            from django.conf import settings
            stripe.api_key = settings.STRIPE_SECRET_KEY
            
            # Delete all payment methods
            payment_methods = stripe.PaymentMethod.list(
                customer=self.stripe_customer_id
            )
            for pm in payment_methods.data:
                stripe.PaymentMethod.detach(pm.id)
            
            # Delete customer (this will delete all associated data)
            stripe.Customer.delete(self.stripe_customer_id)
            
        except Exception as e:
            print(f"Error deleting Stripe data: {e}")


class UserWishlist(models.Model):
    """User's wishlist of artworks"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlists')
    artwork = models.ForeignKey('artwork.Artwork', on_delete=models.CASCADE, related_name='wishlisted_by')
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, help_text="Personal notes about this artwork")

    class Meta:
        unique_together = ['user', 'artwork']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.artwork.title}"


class UserNotification(models.Model):
    """User notifications system"""
    NOTIFICATION_TYPES = [
        ('order_update', 'Order Update'),
        ('inquiry_response', 'Inquiry Response'),
        ('new_artwork', 'New Artwork'),
        ('price_drop', 'Price Drop'),
        ('exhibition', 'Exhibition Notice'),
        ('newsletter', 'Newsletter'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Optional related objects
    artwork = models.ForeignKey('artwork.Artwork', on_delete=models.CASCADE, null=True, blank=True)
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, null=True, blank=True)
    
    # Status
    is_read = models.BooleanField(default=False)
    is_emailed = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.title}"

    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])


class UserActivityLog(models.Model):
    """Track user activity for analytics and personalization"""
    ACTIVITY_TYPES = [
        ('login', 'User Login'),
        ('logout', 'User Logout'),
        ('view_artwork', 'Viewed Artwork'),
        ('add_wishlist', 'Added to Wishlist'),
        ('remove_wishlist', 'Removed from Wishlist'),
        ('place_order', 'Placed Order'),
        ('inquiry', 'Sent Inquiry'),
        ('profile_update', 'Updated Profile'),
        ('password_change', 'Changed Password'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_log')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    description = models.CharField(max_length=200, blank=True)
    
    # Optional related objects
    artwork = models.ForeignKey('artwork.Artwork', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Request metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    referrer = models.URLField(blank=True)
    
    # Timestamp
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'activity_type', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.get_activity_type_display()} - {self.timestamp}"

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal
import uuid


class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    # Order identification
    order_number = models.CharField(max_length=20, unique=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    
    # Order details
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    # Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Customer information
    billing_name = models.CharField(max_length=100)
    billing_email = models.EmailField()
    billing_phone = models.CharField(max_length=20, blank=True)
    billing_address_1 = models.CharField(max_length=100)
    billing_address_2 = models.CharField(max_length=100, blank=True)
    billing_city = models.CharField(max_length=50)
    billing_state = models.CharField(max_length=50)
    billing_postal_code = models.CharField(max_length=20)
    billing_country = models.CharField(max_length=50, default='United States')
    
    # Shipping information
    shipping_name = models.CharField(max_length=100, blank=True)
    shipping_address_1 = models.CharField(max_length=100, blank=True)
    shipping_address_2 = models.CharField(max_length=100, blank=True)
    shipping_city = models.CharField(max_length=50, blank=True)
    shipping_state = models.CharField(max_length=50, blank=True)
    shipping_postal_code = models.CharField(max_length=20, blank=True)
    shipping_country = models.CharField(max_length=50, blank=True)
    
    # Payment information
    payment_method = models.CharField(max_length=50, blank=True)
    payment_reference = models.CharField(max_length=100, blank=True)
    stripe_payment_intent_id = models.CharField(max_length=100, blank=True, help_text="Stripe PaymentIntent ID")
    stripe_charge_id = models.CharField(max_length=100, blank=True, help_text="Stripe Charge ID")
    luma_prints_order_id = models.CharField(max_length=100, blank=True, help_text="Luma Prints Order ID")
    
    # Shipping information
    shipping_method = models.CharField(max_length=50, blank=True)
    tracking_number = models.CharField(max_length=100, blank=True)
    carrier = models.CharField(max_length=50, blank=True, help_text="Shipping carrier (UPS, FedEx, USPS, etc.)")
    estimated_delivery = models.DateTimeField(null=True, blank=True, help_text="Estimated delivery date")
    
    # LumaPrints tracking information
    luma_prints_status = models.CharField(max_length=50, blank=True, help_text="Status from LumaPrints")
    luma_prints_tracking_url = models.URLField(blank=True, help_text="LumaPrints tracking URL")
    luma_prints_updated_at = models.DateTimeField(null=True, blank=True, help_text="Last update from LumaPrints")
    
    # Special instructions
    notes = models.TextField(blank=True, help_text="Customer notes")
    internal_notes = models.TextField(blank=True, help_text="Internal notes for staff")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)

    def _generate_order_number(self):
        """Generate unique order number"""
        prefix = "AF"  # Aiza's Fine Art
        timestamp = timezone.now().strftime("%Y%m%d")
        random_suffix = str(uuid.uuid4())[:6].upper()
        return f"{prefix}{timestamp}{random_suffix}"

    def __str__(self):
        return f"Order {self.order_number} - {self.user.username}"

    def get_absolute_url(self):
        return reverse('orders:detail', kwargs={'order_number': self.order_number})

    @property
    def billing_address_display(self):
        """Return formatted billing address"""
        address_parts = [
            self.billing_address_1,
            self.billing_address_2,
            f"{self.billing_city}, {self.billing_state} {self.billing_postal_code}",
            self.billing_country
        ]
        return "\n".join([part for part in address_parts if part])

    @property
    def shipping_address_display(self):
        """Return formatted shipping address or billing if same"""
        if not self.shipping_address_1:
            return self.billing_address_display
        
        address_parts = [
            self.shipping_address_1,
            self.shipping_address_2,
            f"{self.shipping_city}, {self.shipping_state} {self.shipping_postal_code}",
            self.shipping_country
        ]
        return "\n".join([part for part in address_parts if part])

    def can_be_cancelled(self):
        """Check if order can be cancelled"""
        return self.status in ['pending', 'confirmed']

    def can_be_refunded(self):
        """Check if order can be refunded"""
        return self.status in ['delivered'] and self.payment_status == 'completed'
    
    @property
    def tracking_stages(self):
        """Return tracking stages with completion status"""
        stages = [
            {
                'key': 'confirmed',
                'title': 'Order Confirmed',
                'description': 'Your order has been received and confirmed',
                'completed': self.status in ['confirmed', 'processing', 'shipped', 'delivered'],
                'timestamp': self.confirmed_at,
                'icon': 'check-circle'
            },
            {
                'key': 'processing',
                'title': 'In Production',
                'description': 'Your prints are being prepared',
                'completed': self.status in ['processing', 'shipped', 'delivered'],
                'timestamp': None,  # Will be filled from status updates
                'icon': 'cog'
            },
            {
                'key': 'shipped',
                'title': 'Shipped',
                'description': 'Your package is on its way',
                'completed': self.status in ['shipped', 'delivered'],
                'timestamp': self.shipped_at,
                'icon': 'truck'
            },
            {
                'key': 'delivered',
                'title': 'Delivered',
                'description': 'Package delivered successfully',
                'completed': self.status == 'delivered',
                'timestamp': self.delivered_at,
                'icon': 'home'
            }
        ]
        
        # Add processing timestamp from status updates
        processing_update = self.status_updates.filter(new_status='processing').first()
        if processing_update:
            stages[1]['timestamp'] = processing_update.timestamp
            
        return stages
    
    @property
    def current_stage(self):
        """Get current tracking stage"""
        status_map = {
            'pending': 0,
            'confirmed': 0,
            'processing': 1,
            'shipped': 2,
            'delivered': 3,
            'cancelled': -1,
            'refunded': -1
        }
        return status_map.get(self.status, 0)
    
    @property
    def tracking_percentage(self):
        """Get completion percentage for progress bar"""
        if self.status in ['cancelled', 'refunded']:
            return 0
        current = self.current_stage
        if current < 0:
            return 0
        return min(100, (current + 1) * 25)  # 25% per stage
    
    def get_carrier_tracking_url(self):
        """Generate carrier tracking URL if tracking number exists"""
        if not self.tracking_number or not self.carrier:
            return None
            
        urls = {
            'UPS': f'https://www.ups.com/track?track=yes&trackNums={self.tracking_number}',
            'FEDEX': f'https://www.fedex.com/apps/fedextrack/?tracknumbers={self.tracking_number}',
            'USPS': f'https://tools.usps.com/go/TrackConfirmAction?qtc_tLabels1={self.tracking_number}',
            'DHL': f'https://www.dhl.com/us-en/home/tracking/tracking-express.html?submit=1&tracking-id={self.tracking_number}'
        }
        
        return urls.get(self.carrier.upper(), None)


class OrderItem(models.Model):
    ITEM_TYPE_CHOICES = [
        ('original', 'Original Artwork'),
        ('print', 'Print'),
        ('shipping', 'Shipping'),
        ('tax', 'Tax'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    artwork = models.ForeignKey('artwork.Artwork', on_delete=models.CASCADE, null=True, blank=True)
    
    item_type = models.CharField(max_length=20, choices=ITEM_TYPE_CHOICES, default='original')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Pricing
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Print specifications (if applicable)
    print_size = models.CharField(max_length=50, blank=True)
    print_material = models.CharField(max_length=50, blank=True)
    print_finish = models.CharField(max_length=50, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)
        
        # Mark original artwork as sold after successful order item creation
        if self.item_type == 'original' and self.artwork and self.order.payment_status == 'completed':
            self.mark_original_as_sold()

    def mark_original_as_sold(self):
        """Mark the original artwork as no longer available"""
        if self.artwork and self.item_type == 'original':
            self.artwork.original_available = False
            self.artwork.save()

    def __str__(self):
        return f"{self.title} (x{self.quantity}) - Order {self.order.order_number}"


class OrderStatusUpdate(models.Model):
    """Track order status changes for transparency"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_updates')
    previous_status = models.CharField(max_length=20, blank=True)
    new_status = models.CharField(max_length=20)
    notes = models.TextField(blank=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"Order {self.order.order_number} - {self.new_status}"


class RefundRequest(models.Model):
    REFUND_STATUS_CHOICES = [
        ('requested', 'Requested'),
        ('approved', 'Approved'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('denied', 'Denied'),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='refund_request')
    reason = models.TextField()
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=REFUND_STATUS_CHOICES, default='requested')
    
    # Processing information
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    processing_notes = models.TextField(blank=True)
    refund_reference = models.CharField(max_length=100, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Refund Request - Order {self.order.order_number}"


class Cart(models.Model):
    """Shopping cart for users (both logged-in and guest via session)"""
    session_id = models.CharField(max_length=40, blank=True, null=True, help_text="For guest carts")
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'orders_cart'
        
    def __str__(self):
        if self.user:
            return f"Cart for {self.user.username}"
        return f"Guest Cart {self.session_id}"
    
    @property
    def subtotal(self):
        """Calculate subtotal of all cart items"""
        return sum(item.total_price for item in self.items.all())
    
    def shipping_cost(self, shipping_country='US'):
        """Calculate shipping cost based on country"""
        if self.subtotal <= 0:
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
        """Total number of items in cart"""
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    """Individual items in a shopping cart"""
    ITEM_TYPE_CHOICES = [
        ('original', 'Original Artwork'),
        ('print-8x10', '8" × 10" Print'),
        ('print-11x14', '11" × 14" Print'),
        ('print-16x20', '16" × 20" Print'),
        ('print-24x30', '24" × 30" Print'),
    ]
    
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    artwork = models.ForeignKey('artwork.Artwork', on_delete=models.CASCADE)
    item_type = models.CharField(max_length=20, choices=ITEM_TYPE_CHOICES)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'orders_cartitem'
        unique_together = ['cart', 'artwork', 'item_type']
        
    def __str__(self):
        return f"{self.artwork.title} - {self.get_item_type_display()} (×{self.quantity})"
    
    @property
    def total_price(self):
        """Calculate total price for this cart item"""
        return self.unit_price * self.quantity
    
    @property
    def item_type_display(self):
        """Get display name for item type"""
        return dict(self.ITEM_TYPE_CHOICES).get(self.item_type, self.item_type)

# Checkout System Setup Guide

This guide will help you set up and test the complete checkout system with Stripe payments, email notifications, and Luma Prints integration.

## Prerequisites

1. **Django Environment**: Ensure your Django application is running
2. **Database**: Orders models have been migrated (already done)
3. **Required Packages**: All dependencies installed from requirements.txt

## Environment Variables Setup

Add these variables to your `.env` file:

### Stripe Configuration (Required)
```env
STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key_here
STRIPE_SECRET_KEY=sk_test_your_secret_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
```

### Email Configuration (Required for notifications)
```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
DEFAULT_FROM_EMAIL=hello@aizasfineart.com
ADMIN_EMAIL=admin@aizasfineart.com
```

### Luma Prints Integration (Optional for testing)
```env
LUMA_PRINTS_API_KEY=your_lumaprints_api_key
LUMA_PRINTS_BASE_URL=https://api.lumaprints.com/v1
LUMA_PRINTS_TEST_MODE=True
LUMA_PRINTS_WEBHOOK_SECRET=your_lumaprints_webhook_secret
```

## Step-by-Step Setup

### 1. Get Stripe Test Keys

1. Go to [Stripe Dashboard](https://dashboard.stripe.com/)
2. Make sure you're in **Test mode** (toggle in left sidebar)
3. Go to **Developers > API keys**
4. Copy your **Publishable key** and **Secret key**
5. Add them to your `.env` file

### 2. Configure Email (Gmail Example)

1. Enable 2-factor authentication on your Gmail account
2. Generate an [App Password](https://support.google.com/accounts/answer/185833)
3. Use your Gmail address as `EMAIL_HOST_USER`
4. Use the generated app password as `EMAIL_HOST_PASSWORD`

### 3. Install Additional Dependencies

```bash
pip install stripe>=7.0.0 requests>=2.31.0
```

### 4. Run Migrations (Already Done)

```bash
python manage.py makemigrations orders
python manage.py migrate
```

### 5. Create Test Artwork (If Needed)

```python
# Django shell: python manage.py shell
from artwork.models import Artwork
from decimal import Decimal

# Create test artwork if none exists
artwork = Artwork.objects.create(
    title="Test Watercolor",
    medium="watercolor",
    price=Decimal('250.00'),
    status="available",
    gallery_image="https://picsum.photos/400/500?random=1",
    description="Test artwork for checkout system"
)
```

## Testing the Checkout Flow

### 1. Test Cart Functionality

1. Navigate to `/shop/` or `/gallery/`
2. Add items to cart using the "Add to Cart" buttons
3. Verify cart updates with item count and totals
4. Visit `/orders/cart/` to see cart contents

### 2. Test Checkout Process

1. With items in cart, navigate to `/orders/checkout/`
2. Fill out the checkout form with test data:
   - **Name**: John Doe
   - **Email**: Your test email
   - **Address**: Use real address for shipping calculations
   
3. Use Stripe test card numbers:
   - **Success**: `4242424242424242`
   - **Declined**: `4000000000000002`
   - **Authentication Required**: `4000002500003155`
   - **Expiry**: Any future date (e.g., `12/25`)
   - **CVC**: Any 3 digits (e.g., `123`)

### 3. Verify Order Processing

After successful payment, verify:

1. **Order Creation**: Check Django admin `/admin/orders/order/`
2. **Email Notifications**: 
   - Customer confirmation email sent
   - Admin notification email sent
3. **Order Status**: Should be "Confirmed" with "Completed" payment
4. **Luma Prints**: If configured, print orders sent automatically

### 4. Test Order Confirmation

1. After checkout, you should be redirected to order confirmation page
2. Check that all order details are displayed correctly
3. Verify order number format: `AF20250812XXXXXX`

## API Endpoints

The checkout system provides these endpoints:

- `POST /orders/cart/add/` - Add items to cart
- `POST /orders/cart/update/` - Update cart item quantities  
- `POST /orders/cart/remove/` - Remove items from cart
- `GET /orders/checkout/` - Display checkout page
- `POST /orders/checkout/` - Process checkout
- `POST /orders/api/create-payment-intent/` - Create Stripe payment intent
- `POST /orders/apply-coupon/` - Apply coupon codes
- `GET /orders/confirmation/<order_number>/` - Order confirmation
- `POST /orders/webhooks/luma-prints/` - Luma Prints webhooks

## Webhook Configuration

### Stripe Webhooks (Optional for Testing)

1. In Stripe Dashboard, go to **Developers > Webhooks**
2. Add endpoint: `https://yourdomain.com/stripe-webhooks/`
3. Select events: `payment_intent.succeeded`, `payment_intent.payment_failed`
4. Copy webhook secret to `.env`

### Luma Prints Webhooks (Optional)

1. In Luma Prints dashboard, configure webhook URL:
   `https://yourdomain.com/orders/webhooks/luma-prints/`
2. Select events for order status updates

## Troubleshooting

### Common Issues

1. **Stripe Not Loading**
   - Check `STRIPE_PUBLISHABLE_KEY` is set correctly
   - Verify Stripe script is loaded in template
   - Check browser console for JavaScript errors

2. **Email Not Sending**
   - Verify email credentials in `.env`
   - Check Django logs for email errors
   - Test with Django shell: `send_mail(...)`

3. **Payment Intent Errors**
   - Check `STRIPE_SECRET_KEY` is correct
   - Verify cart has items before checkout
   - Check network tab for API call errors

4. **Cart Not Working**
   - Verify session middleware is enabled
   - Check that cart items are being created
   - Clear browser cookies and try again

### Debug Mode

For testing, you can enable more verbose logging:

```python
# In settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'orders': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

## Production Considerations

Before deploying to production:

1. **Switch to Live Stripe Keys**: Use `pk_live_...` and `sk_live_...`
2. **Configure Real Email Service**: Consider using SendGrid, Mailgun, or similar
3. **Set Up Proper SSL**: Required for Stripe payments
4. **Configure Webhooks**: Set up webhook endpoints for real-time updates
5. **Test with Real Cards**: Use small amounts for final testing
6. **Set up Monitoring**: Track payment success rates and errors

## Security Notes

- Never commit API keys to version control
- Use environment variables for all secrets
- Validate all payment amounts server-side
- Implement rate limiting for cart operations
- Use HTTPS in production
- Validate webhook signatures

## Support

For issues with:
- **Stripe Integration**: Check [Stripe Documentation](https://stripe.com/docs)
- **Email Delivery**: Check email provider documentation
- **Luma Prints**: Contact Luma Prints support
- **Django Issues**: Check Django documentation or project logs

## Test Checklist

- [ ] Stripe test keys configured
- [ ] Email credentials configured  
- [ ] Cart functionality working
- [ ] Checkout form validation working
- [ ] Stripe payment processing working
- [ ] Order creation successful
- [ ] Email notifications sent
- [ ] Order confirmation page displays
- [ ] Admin can view orders
- [ ] Luma Prints integration working (if configured)

Once all items are checked, your checkout system is ready for production!
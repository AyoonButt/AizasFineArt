/**
 * Checkout Initialization Script
 * Initializes CheckoutManager and handles form interactions
 */
console.log('checkout-init.js loaded');

document.addEventListener('DOMContentLoaded', function() {
    console.log('=== CHECKOUT INITIALIZATION ===');
    console.log('DOM loaded, initializing checkout...');
    console.log('CheckoutManager available:', typeof CheckoutManager !== 'undefined');
    console.log('Stripe available:', typeof Stripe !== 'undefined');
    console.log('Available global objects:', Object.keys(window).filter(key => key.includes('Check') || key.includes('Stripe')));
    
    // Get Stripe key from form data attribute
    const form = document.getElementById('checkout-form');
    console.log('Form element found:', !!form);
    const stripeKey = form?.dataset.stripeKey;
    
    console.log('Stripe key:', stripeKey ? stripeKey.substring(0, 20) + '...' : 'NOT_FOUND');
    console.log('Stripe key format valid:', stripeKey ? stripeKey.startsWith('pk_') : false);
    
    // Initialize checkout functionality
    if (typeof CheckoutManager !== 'undefined' && stripeKey) {
        try {
            // Add loading indicator
            const cardElement = document.getElementById('card-element');
            if (cardElement) {
                cardElement.innerHTML = '<div class="text-center py-4 text-neutral-500">Loading payment form...</div>';
            }
            
            window.checkout = new CheckoutManager({
                stripePublicKey: stripeKey,
                csrfToken: document.querySelector('[name=csrfmiddlewaretoken]')?.value,
                submitUrl: '/orders/checkout/',
            });
            console.log('CheckoutManager initialized successfully');
            
            // Remove loading indicator after a short delay
            setTimeout(() => {
                const loadingDiv = cardElement?.querySelector('.text-center');
                if (loadingDiv && cardElement.children.length > 1) {
                    loadingDiv.remove();
                }
            }, 2000);
            
        } catch (error) {
            console.error('CheckoutManager initialization failed:', error);
            
            // Show error in card element
            const cardElement = document.getElementById('card-element');
            if (cardElement) {
                cardElement.innerHTML = '<div class="text-center py-4 text-red-600">Failed to load payment form. Please refresh the page.</div>';
            }
        }
    } else {
        if (typeof CheckoutManager === 'undefined') {
            console.error('CheckoutManager class not found - checkout.js may not have loaded');
            console.log('Available global objects:', Object.keys(window).filter(key => key.includes('Check') || key.includes('Stripe')));
        }
        if (!stripeKey) {
            console.error('Stripe key not found - check form data-stripe-key attribute');
            console.log('Form element:', form);
        }
        
        // Show detailed error in card element
        const cardElement = document.getElementById('card-element');
        if (cardElement) {
            let errorMessage = 'Payment system unavailable: ';
            if (typeof CheckoutManager === 'undefined') {
                errorMessage += 'CheckoutManager not loaded. ';
            }
            if (!stripeKey) {
                errorMessage += 'Stripe key missing. ';
            }
            if (typeof Stripe === 'undefined') {
                errorMessage += 'Stripe.js not loaded. ';
            }
            
            cardElement.innerHTML = `
                <div class="text-center py-4 text-red-600">
                    <div class="font-medium">Payment System Error</div>
                    <div class="text-sm mt-1">${errorMessage}</div>
                    <div class="text-xs mt-2">Check console for details</div>
                </div>
            `;
        }
    }

    // Handle shipping address toggle
    const sameAsBillingCheckbox = document.getElementById('same_as_billing');
    const shippingFields = document.getElementById('shipping-fields');
    
    if (sameAsBillingCheckbox && shippingFields) {
        sameAsBillingCheckbox.addEventListener('change', function() {
            if (this.checked) {
                shippingFields.classList.add('hidden');
                // Clear shipping fields when hiding
                shippingFields.querySelectorAll('input, select').forEach(field => {
                    field.removeAttribute('required');
                });
            } else {
                shippingFields.classList.remove('hidden');
                // Add required attribute to shipping fields when showing
                shippingFields.querySelectorAll('input[name$="_first_name"], input[name$="_last_name"], input[name$="_address_1"], input[name$="_city"], input[name$="_state"], input[name$="_postal_code"], select[name$="_country"]').forEach(field => {
                    field.setAttribute('required', 'required');
                });
            }
        });
    }

    // Auto-fill shipping with billing when same address is checked
    const billingFields = ['first_name', 'last_name', 'address_1', 'address_2', 'city', 'state', 'postal_code', 'country'];
    billingFields.forEach(fieldName => {
        const billingField = document.getElementById('billing_' + fieldName);
        if (billingField) {
            billingField.addEventListener('input', function() {
                if (sameAsBillingCheckbox && sameAsBillingCheckbox.checked) {
                    const shippingField = document.getElementById('shipping_' + fieldName);
                    if (shippingField) {
                        shippingField.value = this.value;
                    }
                }
            });
        }
    });

    // Coupon code handling
    const applyCouponBtn = document.getElementById('apply-coupon');
    const couponInput = document.getElementById('coupon_code');
    
    if (applyCouponBtn && couponInput) {
        applyCouponBtn.addEventListener('click', function() {
            const code = couponInput.value.trim();
            if (!code) return;
            
            this.textContent = 'Applying...';
            this.disabled = true;
            
            // Apply coupon via AJAX
            fetch('/orders/apply-coupon/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify({ coupon_code: code })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Refresh order summary
                    location.reload();
                } else {
                    alert(data.message || 'Invalid coupon code');
                }
            })
            .catch(error => {
                console.error('Coupon error:', error);
                alert('Error applying coupon');
            })
            .finally(() => {
                this.textContent = 'Apply';
                this.disabled = false;
            });
        });

        // Allow Enter key to apply coupon
        couponInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                applyCouponBtn.click();
            }
        });
    }
});
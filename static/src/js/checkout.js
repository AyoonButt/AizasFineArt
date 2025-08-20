/**
 * Checkout Manager - Handles Stripe payment processing and form validation
 */
console.log('checkout.js loaded');
class CheckoutManager {
    constructor(options = {}) {
        this.stripe = null;
        this.elements = null;
        this.cardElement = null;
        this.paymentIntent = null;
        
        this.options = {
            stripePublicKey: options.stripePublicKey || '',
            csrfToken: options.csrfToken || '',
            submitUrl: options.submitUrl || '/orders/checkout/',
            ...options
        };
        
        // Check if this is direct checkout mode and update submitUrl accordingly
        const form = document.getElementById('checkout-form');
        if (form && form.hasAttribute('data-direct-checkout')) {
            this.options.submitUrl = '/orders/checkout/direct/';
            console.log('Direct checkout mode detected - using /orders/checkout/direct/');
        }
        
        this.form = document.getElementById('checkout-form');
        this.submitButton = document.getElementById('submit-payment');
        this.cardErrors = document.getElementById('card-errors');
        this.loadingOverlay = document.getElementById('checkout-loading');
        
        this.init();
    }
    
    async init() {
        if (!this.options.stripePublicKey) {
            console.error('Stripe public key is required');
            this.showError('Payment system configuration error. Please contact support.');
            return;
        }
        
        console.log('Initializing Stripe with key:', this.options.stripePublicKey.substring(0, 8) + '...');
        
        try {
            // Validate key format
            if (!this.options.stripePublicKey.startsWith('pk_')) {
                throw new Error('Invalid Stripe public key format');
            }
            
            // Initialize Stripe with explicit locale and API version
            this.stripe = Stripe(this.options.stripePublicKey, {
                locale: 'en',
                apiVersion: '2022-11-15'
            });
            
            // Create elements instance
            this.elements = this.stripe.elements({
                fonts: [
                    {
                        cssSrc: 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap'
                    }
                ]
            });
            
            console.log('Stripe initialized successfully');
            
            // Create and mount card element
            this.createCardElement();
            
            // Set up form submission
            this.setupFormSubmission();
            
            // Set up real-time validation
            this.setupValidation();
            
            // Initialize total display with current country selection
            const initialCountry = this.form.billing_country?.value || 'US';
            this.updateTotalDisplay(initialCountry);
            
            console.log('CheckoutManager initialization complete');
            
        } catch (error) {
            console.error('Failed to initialize Stripe:', error);
            this.showError('Failed to load payment system. Please refresh the page and try again.');
        }
    }
    
    createCardElement() {
        // Clear any existing card element
        const cardContainer = document.getElementById('card-element');
        if (cardContainer) {
            cardContainer.innerHTML = '';
        }
        
        // Enhanced styling for better compatibility
        const style = {
            base: {
                color: '#1f2937',
                fontFamily: 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
                fontSmoothing: 'antialiased',
                fontSize: '16px',
                lineHeight: '24px',
                '::placeholder': {
                    color: '#9ca3af'
                },
                iconColor: '#6b7280'
            },
            invalid: {
                color: '#dc2626',
                iconColor: '#dc2626'
            },
            complete: {
                color: '#059669',
                iconColor: '#059669'
            }
        };
        
        // Create card element with enhanced options
        const cardOptions = {
            style: style,
            hidePostalCode: false,
            iconStyle: 'solid'
        };
        
        try {
            this.cardElement = this.elements.create('card', cardOptions);
            this.cardElement.mount('#card-element');
            
            console.log('Stripe card element mounted successfully');
            
            // Enhanced event handling
            this.cardElement.on('change', (event) => {
                console.log('Card element change:', event);
                
                if (event.error) {
                    this.showError(event.error.message);
                } else {
                    this.clearError();
                }
                
                // Update submit button state based on completeness
                if (this.submitButton) {
                    if (event.complete) {
                        this.submitButton.disabled = false;
                    } else if (event.empty) {
                        this.submitButton.disabled = true;
                    }
                }
            });
            
            this.cardElement.on('ready', () => {
                console.log('Stripe card element is ready');
                // Focus the card element for better UX
                this.cardElement.focus();
            });
            
        } catch (error) {
            console.error('Failed to create card element:', error);
            this.showError('Failed to load payment form. Please refresh the page.');
        }
    }
    
    setupFormSubmission() {
        if (!this.form) return;
        
        this.form.addEventListener('submit', async (event) => {
            event.preventDefault();
            await this.handleSubmit();
        });
    }
    
    setupValidation() {
        // Real-time form validation
        const requiredFields = this.form.querySelectorAll('[required]');
        requiredFields.forEach(field => {
            field.addEventListener('blur', () => this.validateField(field));
            field.addEventListener('input', () => this.clearFieldError(field));
        });
        
        // Email format validation
        const emailField = this.form.querySelector('#email');
        if (emailField) {
            emailField.addEventListener('blur', () => this.validateEmail(emailField));
        }
        
        // Phone number formatting
        const phoneField = this.form.querySelector('#phone');
        if (phoneField) {
            phoneField.addEventListener('input', (e) => this.formatPhoneNumber(e.target));
        }
        
        // Postal code formatting
        const postalFields = this.form.querySelectorAll('[name$="_postal_code"]');
        postalFields.forEach(field => {
            field.addEventListener('input', (e) => this.formatPostalCode(e.target));
        });
        
        // Real-time address monitoring for shipping and tax updates
        this.setupAddressMonitoring();
    }
    
    setupAddressMonitoring() {
        // Monitor address fields for real-time order summary updates
        const addressFields = [
            'billing_country',
            'billing_state', 
            'billing_postal_code',
            'billing_city',
            'billing_address_1'
        ];
        
        // Add listeners to billing address fields
        addressFields.forEach(fieldName => {
            const field = this.form.querySelector(`[name="${fieldName}"]`);
            if (field) {
                field.addEventListener('change', () => this.handleAddressChange());
                field.addEventListener('blur', () => this.handleAddressChange());
            }
        });
        
        // Also monitor shipping fields if different from billing
        const shippingFields = [
            'shipping_country',
            'shipping_state',
            'shipping_postal_code', 
            'shipping_city',
            'shipping_address_1'
        ];
        
        shippingFields.forEach(fieldName => {
            const field = this.form.querySelector(`[name="${fieldName}"]`);
            if (field) {
                field.addEventListener('change', () => this.handleAddressChange());
                field.addEventListener('blur', () => this.handleAddressChange());
            }
        });
        
        // Monitor "same as billing" checkbox
        const sameAsBilling = this.form.querySelector('#same_as_billing');
        if (sameAsBilling) {
            sameAsBilling.addEventListener('change', () => this.handleAddressChange());
        }
        
        console.log('Address monitoring set up for real-time shipping and tax updates');
    }
    
    async handleSubmit() {
        if (!this.validateForm()) {
            return;
        }
        
        this.setLoading(true);
        
        try {
            // Create payment intent
            const { paymentIntent, error } = await this.createPaymentIntent();
            
            if (error) {
                throw new Error(error);
            }
            
            this.paymentIntent = paymentIntent;
            
            // Confirm payment with Stripe
            const confirmResult = await this.confirmPayment();
            
            if (confirmResult.error) {
                throw new Error(confirmResult.error.message);
            }
            
            // Submit final order
            await this.submitOrder(confirmResult.paymentIntent);
            
        } catch (error) {
            console.error('Payment failed:', error);
            this.showError(error.message);
            this.setLoading(false);
        }
    }
    
    async createPaymentIntent() {
        console.log('Creating payment intent...');
        
        // Log the displayed total from the UI
        const displayedTotal = document.querySelector('#order-summary .font-bold.text-xl')?.textContent || 'not found';
        const displayedSubtotal = document.querySelector('#order-summary [class*="subtotal"]')?.textContent || 'not found';
        const displayedShipping = document.querySelector('#order-summary [class*="shipping"]')?.textContent || 'not found';  
        const displayedTax = document.querySelector('#order-summary [class*="tax"]')?.textContent || 'not found';
        
        console.log('=== PAYMENT AMOUNT VERIFICATION ===');
        console.log('Frontend Display:');
        console.log('  Subtotal:', displayedSubtotal);
        console.log('  Shipping:', displayedShipping);
        console.log('  Tax:', displayedTax);
        console.log('  Total:', displayedTotal);
        
        const formData = new FormData(this.form);
        
        try {
            const response = await fetch('/orders/api/create-payment-intent/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.options.csrfToken,
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: new URLSearchParams(formData)
            });
            
            console.log('Payment intent response status:', response.status);
            
            const data = await response.json();
            console.log('Backend Calculation:');
            console.log('  Server total:', data.amount ? `$${data.amount}` : 'not found');
            console.log('  Subtotal:', data.subtotal ? `$${data.subtotal}` : 'not found');
            console.log('  Shipping:', data.shipping ? `$${data.shipping}` : 'not found');
            console.log('  Tax:', data.tax ? `$${data.tax}` : 'not found');
            console.log('  Stripe tax enabled:', data.stripe_tax_enabled || 'estimated');
            console.log('Payment Verification:');
            console.log('  Frontend total:', displayedTotal);
            console.log('  Backend total:', data.amount ? `$${data.amount}` : 'not found');
            console.log('  Match:', displayedTotal === `$${data.amount}` ? '✅ YES' : `❌ NO`);
            console.log('=== END PAYMENT VERIFICATION ===');
            
            // Update checkout summary with Stripe calculations
            this.updateCheckoutSummary(data);
            
            if (!response.ok) {
                return { error: data.error || `Server error: ${response.status}` };
            }
            
            if (!data.client_secret) {
                return { error: 'Invalid payment intent response' };
            }
            
            return { paymentIntent: data };
            
        } catch (error) {
            console.error('Payment intent creation failed:', error);
            return { error: 'Network error. Please check your connection and try again.' };
        }
    }
    
    async confirmPayment() {
        console.log('Confirming payment...');
        
        const billingDetails = this.getBillingDetails();
        console.log('Billing details:', billingDetails);
        
        try {
            const result = await this.stripe.confirmCardPayment(
                this.paymentIntent.client_secret,
                {
                    payment_method: {
                        card: this.cardElement,
                        billing_details: billingDetails
                    }
                }
            );
            
            console.log('Payment confirmation result:', result);
            return result;
            
        } catch (error) {
            console.error('Payment confirmation error:', error);
            return { 
                error: { 
                    message: error.message || 'Payment confirmation failed. Please try again.' 
                } 
            };
        }
    }
    
    async submitOrder(paymentIntent) {
        const formData = new FormData(this.form);
        formData.append('payment_intent_id', paymentIntent.id);
        formData.append('stripe_payment_method', paymentIntent.payment_method);
        
        const response = await fetch(this.options.submitUrl, {
            method: 'POST',
            headers: {
                'X-CSRFToken': this.options.csrfToken
            },
            body: formData
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to complete order');
        }
        
        // Redirect to success page
        window.location.href = data.redirect_url || '/order-confirmation/';
    }
    
    getBillingDetails() {
        const form = this.form;
        
        return {
            name: `${form.first_name.value} ${form.last_name.value}`.trim(),
            email: form.email.value,
            phone: form.phone.value || undefined,
            address: {
                line1: form.billing_address_1.value,
                line2: form.billing_address_2.value || undefined,
                city: form.billing_city.value,
                state: form.billing_state.value,
                postal_code: form.billing_postal_code.value,
                country: form.billing_country.value
            }
        };
    }
    
    validateForm() {
        let isValid = true;
        const requiredFields = this.form.querySelectorAll('[required]');
        
        requiredFields.forEach(field => {
            if (!this.validateField(field)) {
                isValid = false;
            }
        });
        
        // Validate email format
        const emailField = this.form.querySelector('#email');
        if (emailField && !this.validateEmail(emailField)) {
            isValid = false;
        }
        
        return isValid;
    }
    
    validateField(field) {
        const value = field.value.trim();
        
        if (field.hasAttribute('required') && !value) {
            this.showFieldError(field, 'This field is required');
            return false;
        }
        
        this.clearFieldError(field);
        return true;
    }
    
    validateEmail(field) {
        const email = field.value.trim();
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        
        if (email && !emailRegex.test(email)) {
            this.showFieldError(field, 'Please enter a valid email address');
            return false;
        }
        
        return true;
    }
    
    formatPhoneNumber(field) {
        let value = field.value.replace(/\D/g, '');
        
        if (value.length >= 6) {
            value = `${value.slice(0, 3)}-${value.slice(3, 6)}-${value.slice(6, 10)}`;
        } else if (value.length >= 3) {
            value = `${value.slice(0, 3)}-${value.slice(3)}`;
        }
        
        field.value = value;
    }
    
    formatPostalCode(field) {
        // US ZIP code format
        let value = field.value.replace(/\D/g, '');
        
        if (value.length > 5) {
            value = `${value.slice(0, 5)}-${value.slice(5, 9)}`;
        }
        
        field.value = value;
    }
    
    showFieldError(field, message) {
        this.clearFieldError(field);
        
        field.classList.add('border-red-500', 'focus:ring-red-500');
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'field-error text-red-600 text-xs mt-1';
        errorDiv.textContent = message;
        
        field.parentNode.appendChild(errorDiv);
    }
    
    clearFieldError(field) {
        field.classList.remove('border-red-500', 'focus:ring-red-500');
        
        const existingError = field.parentNode.querySelector('.field-error');
        if (existingError) {
            existingError.remove();
        }
    }
    
    showError(message) {
        if (this.cardErrors) {
            this.cardErrors.textContent = message;
            this.cardErrors.classList.remove('hidden');
        } else {
            alert(message);
        }
    }
    
    clearError() {
        if (this.cardErrors) {
            this.cardErrors.textContent = '';
            this.cardErrors.classList.add('hidden');
        }
    }
    
    async handleAddressChange() {
        // Debounce rapid changes
        clearTimeout(this.addressChangeTimeout);
        this.addressChangeTimeout = setTimeout(async () => {
            await this.updateOrderSummaryRealtime();
        }, 500);
    }
    
    async updateOrderSummaryRealtime() {
        try {
            console.log('🔄 Updating order summary based on address changes...');
            
            // Get current shipping country
            const billingCountry = this.form.billing_country?.value || 'US';
            const sameAsBilling = this.form.same_as_billing?.checked !== false;
            const shippingCountry = sameAsBilling ? billingCountry : (this.form.shipping_country?.value || billingCountry);
            
            console.log(`Shipping country: ${shippingCountry} (same as billing: ${sameAsBilling})`);
            
            // Update shipping immediately based on country
            this.updateShippingDisplay(shippingCountry);
            
            // Check if we have enough address info for tax calculation
            const hasMinimalAddress = this.hasMinimalAddressInfo();
            
            if (hasMinimalAddress) {
                console.log('🧮 Sufficient address info - triggering tax calculation');
                await this.calculateTaxRealtime(shippingCountry);
            } else {
                console.log('⏳ Insufficient address info for tax calculation');
                this.updateTaxDisplay('Calculated at checkout');
            }
            
        } catch (error) {
            console.error('Failed to update order summary:', error);
        }
    }
    
    updateShippingDisplay(country) {
        const shippingElement = document.getElementById('checkout-shipping');
        if (!shippingElement) return;
        
        if (country === 'US') {
            shippingElement.innerHTML = '<span class="text-green-600">Free (US)</span>';
        } else {
            shippingElement.innerHTML = '$12.00 (International)';
        }
        
        // Update total display (subtotal + shipping, tax will be added when calculated)
        this.updateTotalDisplay(country);
    }
    
    updateTotalDisplay(country, taxAmount = 0) {
        // Get current subtotal from the order summary using ID (most reliable)
        const subtotalElement = document.getElementById('checkout-subtotal');
        const subtotalText = subtotalElement?.textContent || '$0.00';
        const subtotal = parseFloat(subtotalText.replace('$', '')) || 0;
        
        console.log(`💰 Updating total: Subtotal: $${subtotal}, Country: ${country}`);
        
        const shipping = country === 'US' ? 0 : 12;
        const tax = parseFloat(taxAmount) || 0;
        const total = subtotal + shipping + tax;
        
        console.log(`💰 Calculated total: $${subtotal} + $${shipping} + $${tax} = $${total}`);
        
        // Target the total element by ID (most reliable)
        const totalElement = document.getElementById('checkout-total');
        
        if (totalElement) {
            totalElement.textContent = `$${total.toFixed(2)}`;
            console.log(`✅ Updated total display to: $${total.toFixed(2)}`);
        } else {
            console.log('❌ Could not find total element by ID, trying fallback selectors...');
            
            // Fallback selectors
            const fallbackSelectors = [
                '#order-summary .flex.justify-between.text-base.font-semibold .text-neutral-800:last-child',
                '#order-summary .font-semibold .text-neutral-800:last-child',
                '#order-summary .border-t .text-neutral-800:last-child', 
                '#order-summary .pt-2 .text-neutral-800:last-child'
            ];
            
            for (const selector of fallbackSelectors) {
                const fallbackElement = document.querySelector(selector);
                if (fallbackElement) {
                    fallbackElement.textContent = `$${total.toFixed(2)}`;
                    console.log(`✅ Updated total via fallback selector: ${selector}`);
                    return;
                }
            }
            
            console.log('❌ All selectors failed - could not update total');
        }
    }
    
    updateTaxDisplay(taxText) {
        const taxElement = document.getElementById('checkout-tax');
        if (taxElement) {
            taxElement.textContent = taxText;
        }
    }
    
    hasMinimalAddressInfo() {
        // Check if we have enough info for tax calculation
        const billingCountry = this.form.billing_country?.value;
        const billingState = this.form.billing_state?.value;
        const billingPostal = this.form.billing_postal_code?.value;
        
        // For US addresses, we need state and postal code
        if (billingCountry === 'US') {
            return billingState && billingPostal && billingPostal.length >= 5;
        }
        
        // For other countries, country is sufficient
        return billingCountry && billingCountry !== 'US';
    }
    
    async calculateTaxRealtime(shippingCountry) {
        try {
            // Create a minimal form data for tax calculation
            const formData = new FormData();
            formData.append('billing_country', shippingCountry);
            formData.append('billing_state', this.form.billing_state?.value || '');
            formData.append('billing_postal_code', this.form.billing_postal_code?.value || '');
            formData.append('billing_city', this.form.billing_city?.value || '');
            formData.append('billing_address_1', this.form.billing_address_1?.value || '');
            
            // Add CSRF token
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || this.options.csrfToken;
            formData.append('csrfmiddlewaretoken', csrfToken);
            
            console.log('🔄 Calling create payment intent for tax calculation...');
            
            const response = await fetch('/orders/api/create-payment-intent/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                },
                body: formData
            });
            
            if (response.ok) {
                const data = await response.json();
                console.log('✅ Tax calculation response:', data);
                
                if (data.tax > 0) {
                    this.updateTaxDisplay(`$${data.tax.toFixed(2)} (estimated)`);
                    this.updateTotalDisplay(shippingCountry, data.tax);
                } else {
                    this.updateTaxDisplay('Calculated at checkout');
                    this.updateTotalDisplay(shippingCountry, 0);
                }
            } else {
                console.log('❌ Tax calculation failed, keeping placeholder');
                this.updateTaxDisplay('Calculated at checkout');
            }
            
        } catch (error) {
            console.error('Real-time tax calculation failed:', error);
            this.updateTaxDisplay('Calculated at checkout');
        }
    }
    
    updateCheckoutSummary(data) {
        // Update shipping display based on billing country
        const billingCountry = this.form.billing_country?.value || 'US';
        const shippingElement = document.getElementById('checkout-shipping');
        const taxElement = document.getElementById('checkout-tax');
        const totalElement = document.querySelector('#order-summary .font-bold.text-xl, #order-summary [class*="total"]');
        
        if (shippingElement && data.shipping !== undefined) {
            if (data.shipping === 0) {
                shippingElement.innerHTML = '<span class="text-green-600">Free (US)</span>';
            } else {
                shippingElement.innerHTML = `$${data.shipping.toFixed(2)} (International)`;
            }
        }
        
        if (taxElement && data.tax !== undefined) {
            if (data.tax > 0) {
                taxElement.textContent = `$${data.tax.toFixed(2)} (estimated)`;
            } else {
                taxElement.textContent = 'Calculated at checkout';
            }
        }
        
        // Update total using the new ID
        const totalElementById = document.getElementById('checkout-total');
        if (totalElementById && data.amount !== undefined) {
            totalElementById.textContent = `$${data.amount.toFixed(2)}`;
        } else if (totalElement && data.amount !== undefined) {
            totalElement.textContent = `$${data.amount.toFixed(2)}`;
        }
    }
    
    setLoading(loading) {
        if (this.submitButton) {
            this.submitButton.disabled = loading;
            
            const buttonText = this.submitButton.querySelector('#button-text');
            const buttonSpinner = this.submitButton.querySelector('#button-spinner');
            
            if (buttonText && buttonSpinner) {
                if (loading) {
                    buttonText.classList.add('hidden');
                    buttonSpinner.classList.remove('hidden');
                } else {
                    buttonText.classList.remove('hidden');
                    buttonSpinner.classList.add('hidden');
                }
            }
        }
        
        if (this.loadingOverlay) {
            if (loading) {
                this.loadingOverlay.classList.remove('hidden');
            } else {
                this.loadingOverlay.classList.add('hidden');
            }
        }
    }
}

// Make CheckoutManager available globally
window.CheckoutManager = CheckoutManager;
console.log('CheckoutManager attached to window:', typeof window.CheckoutManager);
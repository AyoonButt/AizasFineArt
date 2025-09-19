"""
Order and Checkout Forms for Stripe Integration
"""

from django import forms
from django.contrib.auth.models import User
from .models import Order


class CheckoutForm(forms.Form):
    """Form for checkout with billing/shipping information"""
    
    # Personal Information
    email = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(attrs={
            'class': 'form-input w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent',
            'placeholder': 'Email Address',
            'required': True
        })
    )
    
    first_name = forms.CharField(
        label="First Name",
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-input w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent',
            'placeholder': 'First Name',
            'required': True
        })
    )
    
    last_name = forms.CharField(
        label="Last Name",
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-input w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent',
            'placeholder': 'Last Name',
            'required': True
        })
    )
    
    phone = forms.CharField(
        label="Phone Number",
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent',
            'placeholder': 'Phone Number (Optional)'
        })
    )
    
    # Billing/Shipping Address
    address_line_1 = forms.CharField(
        label="Street Address",
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-input w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent',
            'placeholder': 'Street Address',
            'required': True
        })
    )
    
    address_line_2 = forms.CharField(
        label="Apartment, Suite, etc.",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent',
            'placeholder': 'Apartment, Suite, etc. (Optional)'
        })
    )
    
    city = forms.CharField(
        label="City",
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-input w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent',
            'placeholder': 'City',
            'required': True
        })
    )
    
    state = forms.CharField(
        label="State/Province",
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-input w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent',
            'placeholder': 'State/Province',
            'required': True
        })
    )
    
    postal_code = forms.CharField(
        label="ZIP/Postal Code",
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-input w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent',
            'placeholder': 'ZIP/Postal Code',
            'required': True
        })
    )
    
    country = forms.ChoiceField(
        label="Country",
        choices=[
            ('US', 'United States'),
            ('CA', 'Canada'),
            ('GB', 'United Kingdom'),
            ('AU', 'Australia'),
            ('DE', 'Germany'),
            ('FR', 'France'),
            ('IT', 'Italy'),
            ('ES', 'Spain'),
            ('NL', 'Netherlands'),
            ('CH', 'Switzerland'),
            ('SE', 'Sweden'),
            ('NO', 'Norway'),
            ('DK', 'Denmark'),
            ('FI', 'Finland'),
            ('BE', 'Belgium'),
            ('AT', 'Austria'),
            ('IE', 'Ireland'),
            ('NZ', 'New Zealand'),
            ('JP', 'Japan'),
            ('SG', 'Singapore'),
        ],
        initial='US',
        widget=forms.Select(attrs={
            'class': 'form-select w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent'
        })
    )
    
    # Payment Options
    payment_method_type = forms.ChoiceField(
        label="Payment Method",
        choices=[
            ('new', 'New Payment Method'),
            ('saved', 'Use Saved Payment Method'),
        ],
        initial='new',
        widget=forms.RadioSelect(attrs={
            'class': 'form-radio h-4 w-4 text-primary border-gray-300 focus:ring-2 focus:ring-primary'
        })
    )
    
    saved_payment_method = forms.ChoiceField(
        label="Saved Payment Methods",
        choices=[],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent'
        })
    )
    
    # Save Information
    save_info = forms.BooleanField(
        label="Save my information for faster checkout next time",
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-checkbox h-4 w-4 text-primary border-gray-300 rounded focus:ring-2 focus:ring-primary'
        })
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        payment_methods = kwargs.pop('payment_methods', [])
        super().__init__(*args, **kwargs)
        
        # Pre-fill with user data if available
        if user and hasattr(user, 'profile'):
            profile = user.profile
            self.fields['email'].initial = user.email
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['phone'].initial = profile.phone
            self.fields['address_line_1'].initial = profile.address_line_1
            self.fields['address_line_2'].initial = profile.address_line_2
            self.fields['city'].initial = profile.city
            self.fields['state'].initial = profile.state
            self.fields['postal_code'].initial = profile.postal_code
            self.fields['country'].initial = profile.country or 'US'
        
        # Set up saved payment methods
        if payment_methods:
            choices = []
            for pm in payment_methods:
                card = pm.card
                label = f"**** **** **** {card.last4} ({card.brand.title()} expires {card.exp_month:02d}/{card.exp_year})"
                choices.append((pm.id, label))
            self.fields['saved_payment_method'].choices = choices
            
            # If user has saved payment methods, default to using them
            if choices:
                self.fields['payment_method_type'].initial = 'saved'
                self.fields['saved_payment_method'].initial = choices[0][0]
        else:
            # Hide saved payment method options if none exist
            self.fields['payment_method_type'].choices = [('new', 'New Payment Method')]
            self.fields['payment_method_type'].initial = 'new'
            self.fields['saved_payment_method'].widget = forms.HiddenInput()


class ShippingAddressForm(forms.Form):
    """Simplified form for shipping address only"""
    
    address_line_1 = forms.CharField(
        label="Street Address",
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-input w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent',
            'placeholder': 'Street Address',
            'required': True
        })
    )
    
    address_line_2 = forms.CharField(
        label="Apartment, Suite, etc.",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent',
            'placeholder': 'Apartment, Suite, etc. (Optional)'
        })
    )
    
    city = forms.CharField(
        label="City",
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-input w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent',
            'placeholder': 'City',
            'required': True
        })
    )
    
    state = forms.CharField(
        label="State/Province",
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-input w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent',
            'placeholder': 'State/Province',
            'required': True
        })
    )
    
    postal_code = forms.CharField(
        label="ZIP/Postal Code",
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-input w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent',
            'placeholder': 'ZIP/Postal Code',
            'required': True
        })
    )
    
    country = forms.ChoiceField(
        label="Country",
        choices=[
            ('US', 'United States'),
            ('CA', 'Canada'),
            ('GB', 'United Kingdom'),
            ('AU', 'Australia'),
            ('DE', 'Germany'),
            ('FR', 'France'),
            ('IT', 'Italy'),
            ('ES', 'Spain'),
            ('NL', 'Netherlands'),
            ('CH', 'Switzerland'),
            ('SE', 'Sweden'),
            ('NO', 'Norway'),
            ('DK', 'Denmark'),
            ('FI', 'Finland'),
            ('BE', 'Belgium'),
            ('AT', 'Austria'),
            ('IE', 'Ireland'),
            ('NZ', 'New Zealand'),
            ('JP', 'Japan'),
            ('SG', 'Singapore'),
        ],
        initial='US',
        widget=forms.Select(attrs={
            'class': 'form-select w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent'
        })
    )
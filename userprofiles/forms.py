"""
User Profile Forms for Profile Management and Account Settings
"""

from django import forms
from django.contrib.auth.models import User
from .models import UserProfile


class PersonalInfoForm(forms.ModelForm):
    """Form for editing user's personal information"""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent',
                'placeholder': 'First Name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent',
                'placeholder': 'Last Name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent',
                'placeholder': 'Email Address'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True


class UserProfileForm(forms.ModelForm):
    """Form for editing user profile information"""
    
    class Meta:
        model = UserProfile
        fields = [
            'phone', 'date_of_birth', 'address_line_1', 'address_line_2', 
            'city', 'state', 'postal_code', 'country',
            'newsletter_subscription', 'email_notifications', 
            'preferred_contact_method', 'favorite_mediums', 'favorite_subjects',
            'price_range_min', 'price_range_max', 'instagram_handle', 
            'facebook_profile', 'is_collector', 'is_artist', 'referral_source'
        ]
        widgets = {
            'phone': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent',
                'placeholder': 'Phone Number'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-input w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent',
                'type': 'date'
            }),
            'address_line_1': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent',
                'placeholder': 'Street Address'
            }),
            'address_line_2': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent',
                'placeholder': 'Apartment, Suite, etc. (Optional)'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent',
                'placeholder': 'City'
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent',
                'placeholder': 'State/Province'
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent',
                'placeholder': 'ZIP/Postal Code'
            }),
            'country': forms.Select(attrs={
                'class': 'form-select w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent'
            }),
            'preferred_contact_method': forms.Select(attrs={
                'class': 'form-select w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent'
            }),
            'price_range_min': forms.NumberInput(attrs={
                'class': 'form-input w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent',
                'placeholder': 'Minimum Budget',
                'step': '0.01'
            }),
            'price_range_max': forms.NumberInput(attrs={
                'class': 'form-input w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent',
                'placeholder': 'Maximum Budget',
                'step': '0.01'
            }),
            'instagram_handle': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent',
                'placeholder': '@username'
            }),
            'facebook_profile': forms.URLInput(attrs={
                'class': 'form-input w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent',
                'placeholder': 'Facebook Profile URL'
            }),
            'referral_source': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent',
                'placeholder': 'How did you find us?'
            }),
            'newsletter_subscription': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-4 w-4 text-primary border-gray-300 rounded focus:ring-2 focus:ring-primary'
            }),
            'email_notifications': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-4 w-4 text-primary border-gray-300 rounded focus:ring-2 focus:ring-primary'
            }),
            'is_collector': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-4 w-4 text-primary border-gray-300 rounded focus:ring-2 focus:ring-primary'
            }),
            'is_artist': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-4 w-4 text-primary border-gray-300 rounded focus:ring-2 focus:ring-primary'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Country choices
        self.fields['country'].choices = [
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
        ]
        
        # Medium choices (for favorite_mediums field)
        self.fields['favorite_mediums'].help_text = "Select your favorite art mediums (comma-separated): watercolor, oil, acrylic, mixed media, etc."
        
        # Subject choices (for favorite_subjects field)
        self.fields['favorite_subjects'].help_text = "Select your favorite art subjects (comma-separated): landscape, portrait, abstract, still life, etc."


class AddressForm(forms.ModelForm):
    """Simplified form for address management"""
    
    class Meta:
        model = UserProfile
        fields = ['address_line_1', 'address_line_2', 'city', 'state', 'postal_code', 'country']
        widgets = {
            'address_line_1': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent',
                'placeholder': 'Street Address',
                'required': True
            }),
            'address_line_2': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent',
                'placeholder': 'Apartment, Suite, etc. (Optional)'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent',
                'placeholder': 'City',
                'required': True
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent',
                'placeholder': 'State/Province',
                'required': True
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent',
                'placeholder': 'ZIP/Postal Code',
                'required': True
            }),
            'country': forms.Select(attrs={
                'class': 'form-select w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Make required fields required
        self.fields['address_line_1'].required = True
        self.fields['city'].required = True
        self.fields['state'].required = True
        self.fields['postal_code'].required = True
        
        # Country choices
        self.fields['country'].choices = [
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
        ]


class PrivacySettingsForm(forms.ModelForm):
    """Form for privacy and notification settings"""
    
    class Meta:
        model = UserProfile
        fields = [
            'profile_public', 'show_purchase_history', 
            'newsletter_subscription', 'email_notifications'
        ]
        widgets = {
            'profile_public': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-4 w-4 text-primary border-gray-300 rounded focus:ring-2 focus:ring-primary'
            }),
            'show_purchase_history': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-4 w-4 text-primary border-gray-300 rounded focus:ring-2 focus:ring-primary'
            }),
            'newsletter_subscription': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-4 w-4 text-primary border-gray-300 rounded focus:ring-2 focus:ring-primary'
            }),
            'email_notifications': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-4 w-4 text-primary border-gray-300 rounded focus:ring-2 focus:ring-primary'
            }),
        }
from django import forms
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from .models import ArtworkInquiry, Artwork, Category, Series, Tag


class SupabaseURLField(forms.CharField):
    """Custom field that accepts both regular URLs and supabase:// URLs"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.widget = forms.URLInput()
    
    def to_python(self, value):
        """Convert the value to a string"""
        if value is None:
            return ''
        return str(value).strip()
    
    def validate(self, value):
        # Call parent validation for basic CharField validation
        super().validate(value)
        
        # If empty or supabase URL, no additional validation needed
        if not value or value.startswith('supabase://'):
            return
            
        # For regular URLs, validate using Django's URL validator
        from django.core.validators import URLValidator
        validator = URLValidator()
        try:
            validator(value)
        except ValidationError:
            raise ValidationError('Enter a valid URL.')
    
    def clean(self, value):
        # Convert value to string and strip whitespace
        value = self.to_python(value)
        
        # If empty and not required, return empty string
        if not value and not self.required:
            return ''
            
        # Run validation
        self.validate(value)
        
        return value


class ArtworkInquiryForm(forms.ModelForm):
    class Meta:
        model = ArtworkInquiry
        fields = ['name', 'email', 'phone', 'inquiry_type', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Your full name',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'your.email@example.com',
                'required': True
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '(555) 123-4567 (optional)'
            }),
            'inquiry_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Tell us about your interest in this artwork...',
                'rows': 5,
                'required': True
            }),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['inquiry_type'].choices = [
            ('', 'Select inquiry type...'),
        ] + list(self.fields['inquiry_type'].choices)[1:]


class ArtworkForm(forms.ModelForm):
    """Form for creating and editing artwork with 5 image uploads"""
    
    # File upload fields for images
    main_image_file = forms.ImageField(
        required=False, 
        help_text="Main artwork image (JPG, PNG, WebP up to 10MB)",
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-file-input',
            'accept': '.jpg,.jpeg,.png,.webp',
            'data-required': 'false',  # Explicitly mark as not required
        })
    )
    frame1_image_file = forms.ImageField(
        required=False, 
        help_text="First frame variant (JPG, PNG, WebP up to 10MB)",
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-file-input',
            'accept': '.jpg,.jpeg,.png,.webp',
        })
    )
    frame2_image_file = forms.ImageField(
        required=False, 
        help_text="Second frame variant (JPG, PNG, WebP up to 10MB)",
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-file-input',
            'accept': '.jpg,.jpeg,.png,.webp',
        })
    )
    frame3_image_file = forms.ImageField(
        required=False, 
        help_text="Third frame variant (JPG, PNG, WebP up to 10MB)",
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-file-input',
            'accept': '.jpg,.jpeg,.png,.webp',
        })
    )
    frame4_image_file = forms.ImageField(
        required=False, 
        help_text="Fourth frame variant (JPG, PNG, WebP up to 10MB)",
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-file-input',
            'accept': '.jpg,.jpeg,.png,.webp',
        })
    )
    
    # URL fields for existing images
    main_image_url = SupabaseURLField(required=False, widget=forms.HiddenInput())
    frame1_image_url = SupabaseURLField(required=False, widget=forms.HiddenInput())
    frame2_image_url = SupabaseURLField(required=False, widget=forms.HiddenInput())
    frame3_image_url = SupabaseURLField(required=False, widget=forms.HiddenInput())
    frame4_image_url = SupabaseURLField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = Artwork
        fields = [
            'title', 'category', 'series', 'medium', 'dimensions_width', 
            'dimensions_height', 'year_created', 'description', 'inspiration', 
            'technique_notes', 'story', 'original_price', 'type', 'edition_info', 
            'meta_description', 'alt_text', 'tags', 'is_featured', 'is_active',
            'main_image_url', 'frame1_image_url', 'frame2_image_url', 
            'frame3_image_url', 'frame4_image_url'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input w-full',
                'placeholder': 'Enter artwork title'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select w-full'
            }),
            'series': forms.Select(attrs={
                'class': 'form-select w-full'
            }),
            'medium': forms.Select(attrs={
                'class': 'form-select w-full'
            }),
            'dimensions_width': forms.NumberInput(attrs={
                'class': 'form-input w-full',
                'placeholder': 'Width in inches',
                'step': '0.01'
            }),
            'dimensions_height': forms.NumberInput(attrs={
                'class': 'form-input w-full',
                'placeholder': 'Height in inches',
                'step': '0.01'
            }),
            'year_created': forms.NumberInput(attrs={
                'class': 'form-input w-full',
                'placeholder': 'Year artwork was created'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-textarea w-full',
                'rows': 4,
                'placeholder': 'Describe the artwork...'
            }),
            'inspiration': forms.Textarea(attrs={
                'class': 'form-textarea w-full',
                'rows': 3,
                'placeholder': 'What inspired this piece?'
            }),
            'technique_notes': forms.Textarea(attrs={
                'class': 'form-textarea w-full',
                'rows': 3,
                'placeholder': 'Technical details about creation...'
            }),
            'story': forms.Textarea(attrs={
                'class': 'form-textarea w-full',
                'rows': 4,
                'placeholder': 'Personal story behind the artwork...'
            }),
            'original_price': forms.NumberInput(attrs={
                'class': 'form-input w-full',
                'placeholder': 'Price in USD',
                'step': '0.01'
            }),
            'edition_info': forms.TextInput(attrs={
                'class': 'form-input w-full',
                'placeholder': 'Limited edition info (optional)'
            }),
            'meta_description': forms.Textarea(attrs={
                'class': 'form-textarea w-full',
                'rows': 2,
                'placeholder': 'SEO description (160 characters max)'
            }),
            'alt_text': forms.TextInput(attrs={
                'class': 'form-input w-full',
                'placeholder': 'Descriptive alt text for accessibility'
            }),
            'type': forms.Select(attrs={
                'class': 'form-select w-full'
            }),
            'tags': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-checkbox-grid'
            }),
            'is_featured': forms.CheckboxInput(attrs={
                'class': 'form-checkbox'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-checkbox'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filter series based on selected category
        if 'category' in self.data:
            try:
                category_id = int(self.data.get('category'))
                self.fields['series'].queryset = Series.objects.filter(category_id=category_id).order_by('name')
            except (ValueError, TypeError):
                self.fields['series'].queryset = Series.objects.none()
        elif self.instance.pk:
            self.fields['series'].queryset = self.instance.category.series.order_by('name')
        else:
            self.fields['series'].queryset = Series.objects.none()

    def clean_main_image_file(self):
        """Validate main image file"""
        image = self.cleaned_data.get('main_image_file')
        if image:
            if image.size > 10 * 1024 * 1024:  # 10MB limit
                raise forms.ValidationError("Image file too large. Maximum size is 10MB.")
            if not image.name.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                raise forms.ValidationError("Please upload a JPG, PNG, or WebP image.")
        return image
    
    def clean_frame1_image_file(self):
        """Validate frame1 image file"""
        return self._validate_frame_image(self.cleaned_data.get('frame1_image_file'))
    
    def clean_frame2_image_file(self):
        """Validate frame2 image file"""
        return self._validate_frame_image(self.cleaned_data.get('frame2_image_file'))
    
    def clean_frame3_image_file(self):
        """Validate frame3 image file"""
        return self._validate_frame_image(self.cleaned_data.get('frame3_image_file'))
    
    def clean_frame4_image_file(self):
        """Validate frame4 image file"""
        return self._validate_frame_image(self.cleaned_data.get('frame4_image_file'))
    
    def _validate_frame_image(self, image):
        """Common validation for frame images"""
        if image:
            if image.size > 10 * 1024 * 1024:  # 10MB limit
                raise forms.ValidationError("Image file too large. Maximum size is 10MB.")
            if not image.name.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                raise forms.ValidationError("Please upload a JPG, PNG, or WebP image.")
        return image
    

    def clean(self):
        """Additional form validation"""
        cleaned_data = super().clean()
        
        # Validate price if type is original
        artwork_type = cleaned_data.get('type')
        original_price = cleaned_data.get('original_price')
        
        if artwork_type == 'original' and not original_price:
            raise forms.ValidationError({
                'original_price': 'Original price is required when artwork type is "original".'
            })
        
        # Auto-generate alt_text if not provided
        alt_text = cleaned_data.get('alt_text')
        if not alt_text:
            title = cleaned_data.get('title', '')
            medium = cleaned_data.get('medium', '')
            if title and medium:
                cleaned_data['alt_text'] = f"{title} - {medium.title()} artwork by Aiza"
            elif title:
                cleaned_data['alt_text'] = f"{title} - Artwork by Aiza"
            else:
                cleaned_data['alt_text'] = "Artwork by Aiza"
                        
        return cleaned_data
    
    def _post_clean(self):
        """Override to handle supabase:// URLs during model validation"""
        # Store original supabase URLs before model validation
        supabase_urls = {}
        url_fields = ['main_image_url', 'frame1_image_url', 'frame2_image_url', 'frame3_image_url', 'frame4_image_url']
        
        for field_name in url_fields:
            if field_name in self.cleaned_data:
                value = self.cleaned_data[field_name]
                if value and value.startswith('supabase://'):
                    supabase_urls[field_name] = value
                    # Replace with dummy URL for model validation
                    self.cleaned_data[field_name] = 'https://example.com/temp.jpg'
                    setattr(self.instance, field_name, 'https://example.com/temp.jpg')
        
        # Run normal model validation with dummy URLs
        super()._post_clean()
        
        # Restore original supabase URLs after validation
        for field_name, original_url in supabase_urls.items():
            self.cleaned_data[field_name] = original_url
            setattr(self.instance, field_name, original_url)

    def save(self, commit=True):
        """Override save to handle all field updates properly"""
        instance = super().save(commit=False)
        
        # Ensure all form fields are properly set on the instance
        # Skip many-to-many fields as they need special handling
        many_to_many_fields = [field.name for field in self._meta.model._meta.many_to_many]
        
        for field_name in self.fields:
            if (field_name in self.cleaned_data and 
                not field_name.endswith('_file') and 
                field_name not in many_to_many_fields):
                # Skip image file fields and many-to-many fields
                value = self.cleaned_data[field_name]
                setattr(instance, field_name, value)
        
        if commit:
            # Skip model validation since we already handled it in _post_clean
            instance.save(skip_validation=True)
            # Handle many-to-many relationships (like tags)
            self.save_m2m()
        
        return instance
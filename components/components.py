"""
All Django components for Aiza's Fine Art website
"""

from django_components import Component, register
from django.template.loader import render_to_string
from django import forms


# Gallery Components
@register("gallery_grid")
class GalleryGrid(Component):
    """
    Reusable gallery grid component that can be used with HTMX for filtering
    and pagination. Replaces the React gallery components.
    """
    
    template_name = "components/gallery/gallery_grid.html"
    
    def get_context_data(self, artworks=None, medium="all", category="all", show_filters=True, **kwargs):
        """
        Context data for the gallery grid component
        
        Args:
            artworks: QuerySet of artwork objects
            medium: Filter by medium (watercolor, oil, all)
            category: Filter by category 
            show_filters: Whether to show filter controls
        """
        return {
            "artworks": artworks or [],
            "medium": medium,
            "category": category, 
            "show_filters": show_filters,
            "total_count": len(artworks) if artworks else 0,
            **kwargs
        }
    
    class Media:
        css = {
            'all': ()
        }
        js = ()


@register("artwork_card")
class ArtworkCard(Component):
    """
    Individual artwork card component for the gallery
    """
    
    template_name = "components/gallery/artwork_card.html"
    
    def get_context_data(self, artwork, show_price=True, show_status=True, **kwargs):
        return {
            "artwork": artwork,
            "show_price": show_price,
            "show_status": show_status,
            **kwargs
        }


@register("gallery_filters")
class GalleryFilters(Component):
    """
    Filter controls for the gallery with HTMX integration
    """
    
    template_name = "components/gallery/gallery_filters.html"
    
    def get_context_data(self, current_medium="all", current_category="all", **kwargs):
        return {
            "current_medium": current_medium,
            "current_category": current_category,
            "media_choices": [
                ("all", "All Media"),
                ("watercolor", "Watercolor"),
                ("oil", "Oil Painting"),
                ("acrylic", "Acrylic"),
                ("mixed", "Mixed Media"),
            ],
            "category_choices": [
                ("all", "All Categories"),
                ("landscape", "Landscapes"),
                ("portrait", "Portraits"),
                ("still_life", "Still Life"),
                ("abstract", "Abstract"),
            ],
            **kwargs
        }


# Form Components
class ContactForm(forms.Form):
    """Contact form for the contact page"""
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Your full name'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'your.email@example.com'
        })
    )
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Subject of your message'
        })
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-textarea',
            'placeholder': 'Your message here...',
            'rows': 5
        })
    )


@register("contact_form")
class ContactFormComponent(Component):
    """
    Contact form component with HTMX integration
    """
    
    template_name = "components/forms/contact_form.html"
    
    def get_context_data(self, form=None, success_message=None, error_message=None, **kwargs):
        return {
            "form": form or ContactForm(),
            "success_message": success_message,
            "error_message": error_message,
            **kwargs
        }


@register("newsletter_form")  
class NewsletterForm(Component):
    """
    Newsletter signup form component
    """
    
    template_name = "components/forms/newsletter_form.html"
    
    def get_context_data(self, email="", success_message=None, error_message=None, **kwargs):
        return {
            "email": email,
            "success_message": success_message,
            "error_message": error_message,
            **kwargs
        }


@register("commission_form")
class CommissionForm(Component):
    """
    Commission inquiry form component
    """
    
    template_name = "components/forms/commission_form.html"
    
    def get_context_data(self, form=None, success_message=None, error_message=None, **kwargs):
        commission_form = form or forms.Form()
        # Add fields dynamically if no form provided
        if not form:
            commission_form.fields['name'] = forms.CharField(max_length=100)
            commission_form.fields['email'] = forms.EmailField()
            commission_form.fields['size'] = forms.CharField(max_length=50)
            commission_form.fields['medium'] = forms.ChoiceField(choices=[
                ('watercolor', 'Watercolor'),
                ('oil', 'Oil Painting'),
                ('acrylic', 'Acrylic'),
            ])
            commission_form.fields['description'] = forms.CharField(widget=forms.Textarea)
            commission_form.fields['budget'] = forms.CharField(max_length=50)
            
        return {
            "form": commission_form,
            "success_message": success_message,
            "error_message": error_message,
            **kwargs
        }


# Navigation Components
@register("navbar")
class Navbar(Component):
    """
    Main navigation bar component
    """
    
    template_name = "components/navigation/navbar.html"
    
    def get_context_data(self, user=None, current_page=None, **kwargs):
        return {
            "user": user,
            "current_page": current_page,
            "nav_items": [
                {"name": "Home", "url": "home", "url_name": "home"},
                {"name": "Portfolio", "url": "portfolio", "url_name": "portfolio"},
                {"name": "Shop", "url": "shop", "url_name": "shop"},
                {"name": "About", "url": "about", "url_name": "about"},
                {"name": "Contact", "url": "contact", "url_name": "contact"},
            ],
            **kwargs
        }


@register("breadcrumb")
class Breadcrumb(Component):
    """
    Breadcrumb navigation component
    """
    
    template_name = "components/navigation/breadcrumb.html"
    
    def get_context_data(self, items=None, **kwargs):
        """
        Args:
            items: List of dicts with 'name' and 'url' keys
        """
        return {
            "items": items or [],
            **kwargs
        }


@register("footer")
class Footer(Component):
    """
    Site footer component
    """
    
    template_name = "components/navigation/footer.html"
    
    def get_context_data(self, **kwargs):
        return {
            "social_links": [
                {
                    "name": "Instagram", 
                    "url": "https://www.instagram.com/aizasfineart/",
                    "icon": "instagram"
                },
                {
                    "name": "TikTok",
                    "url": "https://www.tiktok.com/@aizasfineart", 
                    "icon": "tiktok"
                },
                {
                    "name": "Facebook",
                    "url": "https://www.facebook.com/aizasfineart",
                    "icon": "facebook"
                },
                {
                    "name": "YouTube", 
                    "url": "https://www.youtube.com/@aizasfineart",
                    "icon": "youtube"
                },
            ],
            "quick_links": [
                {"name": "Gallery", "url": "/art/"},
                {"name": "Watercolors", "url": "/art/watercolor/"},
                {"name": "Oil Paintings", "url": "/art/oil/"},
                {"name": "About Aiza", "url": "/about/"},
            ],
            "support_links": [
                {"name": "Contact Us", "url": "/contact/"},
                {"name": "Shipping Info", "url": "/shipping/"},
                {"name": "Returns", "url": "/returns/"},
                {"name": "FAQ", "url": "/faq/"},
                {"name": "Care Guide", "url": "/care-guide/"},
            ],
            **kwargs
        }
import json
from django import template
from django.core.serializers.json import DjangoJSONEncoder

register = template.Library()


@register.filter
def featured_artworks_json(queryset):
    """Convert featured artworks queryset to JSON for React component"""
    artworks_data = []
    
    for artwork in queryset:
        artworks_data.append({
            'id': artwork.id,
            'title': artwork.title,
            'slug': artwork.slug,
            'medium': artwork.get_medium_display(),
            'price_display': artwork.price_display,
            'image_thumbnail': artwork.get_simple_signed_url(),
            'image_gallery': artwork.get_simple_signed_url(),  # Use same URL for both
            'image_url': artwork.get_simple_signed_url(),
            'alt_text': artwork.alt_text or artwork.title,
            'aspect_ratio': 0.8  # Default 4:5 ratio
        })
    
    return json.dumps(artworks_data, cls=DjangoJSONEncoder)
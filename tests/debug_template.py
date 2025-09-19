#!/usr/bin/env python3

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aizasfineart.settings')
django.setup()

from artwork.models import Artwork
from django.template import Template, Context
from django.template.loader import get_template

# Get artwork
artwork = Artwork.objects.select_related('category').get(slug='wide-images-2025')
print(f"Artwork: {artwork.title}")
print(f"Available fields: {[f.name for f in artwork._meta.fields]}")

# Test basic template rendering
try:
    template = get_template('artwork_detail.html')
    context = Context({'artwork': artwork})
    result = template.render(context)
    print("Template rendered successfully!")
except Exception as e:
    print(f"Template error: {e}")
    import traceback
    traceback.print_exc()
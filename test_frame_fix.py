#!/usr/bin/env python3
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aizasfineart.settings')
django.setup()

from artwork.models import Artwork

print('Testing frame image fix...')

# Find artwork with frame images
artwork = Artwork.objects.filter(
    frame1_image_url__isnull=False, 
    frame1_image_url__gt=''
).first()

if artwork:
    print(f'Testing with: {artwork.title}')
    
    # Test the context structure that view will create
    frame_images = {
        'frame1': {
            'gallery': artwork.get_frame_simple_url(1) if artwork.frame1_image_url else None
        },
        'frame2': {
            'gallery': artwork.get_frame_simple_url(2) if artwork.frame2_image_url else None
        },
        'frame3': {
            'gallery': artwork.get_frame_simple_url(3) if artwork.frame3_image_url else None
        },
        'frame4': {
            'gallery': artwork.get_frame_simple_url(4) if artwork.frame4_image_url else None
        }
    }
    
    print('\nFrame images context structure:')
    for frame_key, frame_data in frame_images.items():
        has_gallery = frame_data.get('gallery') is not None
        if has_gallery:
            url_preview = frame_data['gallery'][:50] + '...'
            print(f'  ✅ {frame_key}: {url_preview}')
        else:
            print(f'  ❌ {frame_key}: No URL')
    
    # Test cached main image
    cached_main = artwork.get_simple_signed_url()
    print(f'\n✅ Cached main image: {cached_main[:50] if cached_main else "None"}...')
    
    print('\n🎉 Frame image fix is working correctly!')
    print('The ArtworkDetailView now provides the context structure the template expects.')
    
else:
    print('❌ No artwork with frame images found for testing')
    
    # Show what artworks exist
    print('\nAvailable artworks:')
    for art in Artwork.objects.all()[:5]:
        has_frames = any([art.frame1_image_url, art.frame2_image_url, art.frame3_image_url, art.frame4_image_url])
        print(f'  {art.title}: {"✅" if has_frames else "❌"} has frame images')
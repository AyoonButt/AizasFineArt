# Supabase Image Storage Setup Guide

This guide will help you configure Supabase for storing and serving artwork images with dynamic transformations.

## 1. Create Supabase Project

1. Go to [supabase.com](https://supabase.com) and create an account
2. Create a new project
3. Note your project URL and anon key from Settings > API

## 2. Configure Storage Bucket

### Create Private Storage Bucket
```sql
-- Run in Supabase SQL Editor - Create PRIVATE bucket
INSERT INTO storage.buckets (id, name, public) 
VALUES ('artwork-images', 'artwork-images', false);
```

### Set Storage Policies for Private Bucket
```sql
-- Allow service role to manage all objects (for Django backend)
CREATE POLICY "Service Role Full Access" ON storage.objects FOR ALL 
USING (bucket_id = 'artwork-images' AND auth.role() = 'service_role');

-- Allow authenticated users to read their own uploads (optional)
CREATE POLICY "Authenticated Read Own" ON storage.objects FOR SELECT 
USING (bucket_id = 'artwork-images' AND auth.role() = 'authenticated');

-- Allow authenticated users to upload (for artist dashboard)
CREATE POLICY "Authenticated Upload" ON storage.objects FOR INSERT 
WITH CHECK (bucket_id = 'artwork-images' AND auth.role() = 'authenticated');

-- Allow authenticated users to update/delete (for artist dashboard)
CREATE POLICY "Authenticated Update" ON storage.objects FOR UPDATE 
USING (bucket_id = 'artwork-images' AND auth.role() = 'authenticated');

CREATE POLICY "Authenticated Delete" ON storage.objects FOR DELETE 
USING (bucket_id = 'artwork-images' AND auth.role() = 'authenticated');
```

## 3. Install Python Dependencies

Add to your `requirements.txt`:
```
supabase>=1.0.3
python-dotenv>=1.0.0
```

Run: `pip install supabase python-dotenv`

## 4. Environment Configuration

Create/update `.env` file:
```env
# Supabase Configuration
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_KEY=your-service-role-key-here
```

Add to `settings.py`:
```python
import os
from dotenv import load_dotenv

load_dotenv()

# Supabase Configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')
```

## 5. Image Storage Service

Create `utils/supabase_client.py`:
```python
import os
from supabase import create_client, Client
from django.conf import settings
from typing import Optional

class SupabaseStorageService:
    def __init__(self):
        self.client: Client = create_client(
            settings.SUPABASE_URL, 
            settings.SUPABASE_SERVICE_KEY
        )
        self.bucket = 'artwork-images'
    
    def upload_image(self, file_path: str, file_data: bytes, content_type: str = 'image/jpeg') -> Optional[str]:
        """Upload image to Supabase storage"""
        try:
            response = self.client.storage.from_(self.bucket).upload(
                file_path, 
                file_data,
                file_options={'content-type': content_type}
            )
            
            if response.status_code == 200:
                return self.get_public_url(file_path)
            return None
            
        except Exception as e:
            print(f"Upload error: {e}")
            return None
    
    def get_public_url(self, file_path: str) -> str:
        """Get public URL for image"""
        return f"{settings.SUPABASE_URL}/storage/v1/object/public/{self.bucket}/{file_path}"
    
    def get_transformed_url(self, file_path: str, width: int = None, height: int = None, 
                          quality: int = 80, format: str = 'webp') -> str:
        """Get URL with image transformations"""
        base_url = self.get_public_url(file_path)
        
        # Supabase image transformations
        params = []
        if width:
            params.append(f"width={width}")
        if height:
            params.append(f"height={height}")
        params.append(f"quality={quality}")
        params.append(f"format={format}")
        
        if params:
            return f"{base_url}?{'&'.join(params)}"
        return base_url
    
    def delete_image(self, file_path: str) -> bool:
        """Delete image from storage"""
        try:
            response = self.client.storage.from_(self.bucket).remove([file_path])
            return response.status_code == 200
        except Exception as e:
            print(f"Delete error: {e}")
            return False

# Singleton instance
supabase_storage = SupabaseStorageService()
```

## 6. Update Artwork Model

Add to `artwork/models.py`:
```python
from utils.supabase_client import supabase_storage

class Artwork(models.Model):
    # ... existing fields ...
    
    def get_image(self, size='medium'):
        """Get optimized image URL for different use cases"""
        if not self.main_image_url:
            return None
            
        # If it's already a Supabase URL with transformations, return as-is
        if '?' in self.main_image_url:
            return self.main_image_url
            
        # Extract file path from full URL for transformation
        if 'supabase.co/storage' in self.main_image_url:
            file_path = self.main_image_url.split('/public/artwork-images/')[-1]
            
            size_configs = {
                'thumbnail': {'width': 300, 'height': 300},
                'small': {'width': 500, 'height': 500},
                'medium': {'width': 800, 'height': 800},
                'large': {'width': 1200, 'height': 1200},
                'social': {'width': 1200, 'height': 630},  # Open Graph
            }
            
            config = size_configs.get(size, {'width': 800, 'height': 800})
            return supabase_storage.get_transformed_url(file_path, **config)
        
        # Return original URL if not Supabase
        return self.main_image_url
```

## 7. Dashboard Image Upload Form

Create `dashboard/forms.py`:
```python
from django import forms
from artwork.models import Artwork
from utils.supabase_client import supabase_storage
import uuid
import os

class ArtworkImageUploadForm(forms.ModelForm):
    image_file = forms.ImageField(
        required=False,
        help_text="Upload a high-quality image (JPEG, PNG, WebP)"
    )
    
    class Meta:
        model = Artwork
        fields = ['main_image_url', 'image_file']
        
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Handle file upload to Supabase
        if self.cleaned_data.get('image_file'):
            image_file = self.cleaned_data['image_file']
            
            # Generate unique filename
            ext = os.path.splitext(image_file.name)[1]
            filename = f"artwork/{uuid.uuid4()}{ext}"
            
            # Upload to Supabase
            file_data = image_file.read()
            url = supabase_storage.upload_image(
                filename, 
                file_data, 
                content_type=image_file.content_type
            )
            
            if url:
                instance.main_image_url = url
            else:
                raise forms.ValidationError("Failed to upload image to storage")
        
        if commit:
            instance.save()
        return instance
```

## 8. Update Dashboard Views

Update `aizasfineart/views.py`:
```python
from dashboard.forms import ArtworkImageUploadForm

class ArtworkCreateView(ArtistDashboardMixin, CreateView):
    model = Artwork
    form_class = ArtworkImageUploadForm
    template_name = 'dashboard/artwork_form.html'
    success_url = reverse_lazy('dashboard')

class ArtworkUpdateView(ArtistDashboardMixin, UpdateView):
    model = Artwork
    form_class = ArtworkImageUploadForm
    template_name = 'dashboard/artwork_form.html'
    success_url = reverse_lazy('dashboard')
```

## 9. Update Templates for Optimized Images

Update your templates to use optimized images:

**In `templates/gallery.html`:**
```html
<!-- Replace static image URLs with optimized versions -->
<img src="{{ artwork.get_image:'medium' }}" 
     srcset="{{ artwork.get_image:'small' }} 500w, 
             {{ artwork.get_image:'medium' }} 800w,
             {{ artwork.get_image:'large' }} 1200w"
     sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
     alt="{{ artwork.title }}"
     class="w-full h-auto rounded-lg"
     loading="lazy">
```

**In `templates/dashboard/artwork_form.html`:**
```html
<!-- Add file upload field -->
<div class="md:col-span-2">
    <label for="{{ form.image_file.id_for_label }}" class="block text-sm font-medium text-neutral-700 mb-2">
        Upload New Image
    </label>
    <input type="file" 
           name="{{ form.image_file.name }}" 
           id="{{ form.image_file.id_for_label }}"
           accept="image/*"
           class="w-full px-4 py-3 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors">
    <p class="text-xs text-neutral-500 mt-1">
        Or paste a URL below. File upload will override URL field.
    </p>
</div>
```

## 10. Image Optimization Best Practices

### Folder Structure in Supabase:
```
artwork-images/
├── artwork/           # Main artwork images
├── thumbnails/        # Auto-generated thumbnails
├── process/          # Process/behind-scenes images
└── temp/             # Temporary uploads
```

### Size Guidelines:
- **Upload**: High resolution (2400px+ width)
- **Gallery**: 800px width
- **Thumbnails**: 300px width
- **Social sharing**: 1200x630px
- **Mobile**: 500px width

## 11. Testing the Setup

1. **Upload Test**:
   ```python
   # In Django shell
   from utils.supabase_client import supabase_storage
   
   # Test upload
   with open('test_image.jpg', 'rb') as f:
       url = supabase_storage.upload_image('test/image.jpg', f.read())
       print(f"Uploaded: {url}")
   ```

2. **Transformation Test**:
   ```python
   # Test transformations
   thumb_url = supabase_storage.get_transformed_url('test/image.jpg', width=300, height=300)
   print(f"Thumbnail: {thumb_url}")
   ```

## 12. Migration Strategy

For existing artwork with external URLs:
```python
# Create management command: python manage.py migrate_images_to_supabase
from django.core.management.base import BaseCommand
from artwork.models import Artwork
import requests

class Command(BaseCommand):
    def handle(self, *args, **options):
        for artwork in Artwork.objects.filter(main_image_url__isnull=False):
            if 'supabase.co' not in artwork.main_image_url:
                # Download and re-upload to Supabase
                response = requests.get(artwork.main_image_url)
                if response.status_code == 200:
                    filename = f"artwork/{artwork.slug}.jpg"
                    new_url = supabase_storage.upload_image(
                        filename, 
                        response.content
                    )
                    if new_url:
                        artwork.main_image_url = new_url
                        artwork.save()
                        self.stdout.write(f"Migrated: {artwork.title}")
```

## Security Notes

- Never expose your service role key in frontend code
- Use row-level security policies
- Validate file types and sizes
- Consider implementing virus scanning for uploads
- Set up proper CORS policies

Your Supabase image storage is now ready! The system provides:
- ✅ Automatic image optimization
- ✅ Dynamic resizing and format conversion
- ✅ CDN delivery
- ✅ Secure upload workflow
- ✅ Professional image management
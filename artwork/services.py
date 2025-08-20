"""
Artwork services for handling image uploads and processing
"""
import os
import uuid
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.conf import settings


class ArtworkImageService:
    """Service for handling artwork image uploads"""
    
    def __init__(self):
        self.max_size = 10 * 1024 * 1024  # 10MB
        self.allowed_formats = ['JPEG', 'JPG', 'PNG', 'WEBP']
        self.max_dimension = 2400  # Max width or height
    
    def process_image_upload(self, artwork, field_name, uploaded_file):
        """
        Process an uploaded image file and return the URL to store
        
        Args:
            artwork: Artwork instance
            field_name: Name of the image field (main_image_file, frame1_image_file, etc.)
            uploaded_file: Django UploadedFile instance
            
        Returns:
            str: URL to store in the artwork field, or None if upload failed
        """
        if not uploaded_file:
            return None
            
        try:
            # Validate file
            if not self._validate_file(uploaded_file):
                raise ValueError("Invalid image file")
            
            # Process image
            processed_image = self._process_image(uploaded_file)
            
            # Generate unique filename
            filename = self._generate_filename(artwork, field_name, uploaded_file.name)
            
            # For now, return a placeholder URL structure
            # In production, this would upload to Supabase and return the actual URL
            # Example: supabase://artwork-images/artwork-123/main-uuid.webp
            supabase_url = f"supabase://artwork-images/{artwork.slug or 'new'}/{filename}"
            
            # TODO: Implement actual Supabase upload
            # supabase_url = self._upload_to_supabase(processed_image, filename)
            
            return supabase_url
            
        except Exception as e:
            print(f"Image upload error for {field_name}: {e}")
            return None
    
    def _validate_file(self, uploaded_file):
        """Validate uploaded image file"""
        # Check file size
        if uploaded_file.size > self.max_size:
            raise ValueError(f"File too large. Maximum size is {self.max_size // (1024*1024)}MB")
        
        # Check file format
        try:
            with Image.open(uploaded_file) as img:
                if img.format not in self.allowed_formats:
                    raise ValueError(f"Unsupported format. Allowed: {', '.join(self.allowed_formats)}")
                return True
        except Exception:
            raise ValueError("Invalid image file")
    
    def _process_image(self, uploaded_file):
        """Process and optimize image"""
        with Image.open(uploaded_file) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                # Create white background for transparency
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Resize if too large
            if img.width > self.max_dimension or img.height > self.max_dimension:
                img.thumbnail((self.max_dimension, self.max_dimension), Image.Resampling.LANCZOS)
            
            # Auto-rotate based on EXIF
            try:
                img = self._auto_rotate(img)
            except Exception:
                pass  # Ignore EXIF errors
            
            return img
    
    def _auto_rotate(self, img):
        """Auto-rotate image based on EXIF orientation"""
        try:
            from PIL.ExifTags import ORIENTATION
            exif = img._getexif()
            if exif is not None:
                orientation = exif.get(0x0112)  # ORIENTATION tag
                if orientation == 3:
                    img = img.rotate(180, expand=True)
                elif orientation == 6:
                    img = img.rotate(270, expand=True)
                elif orientation == 8:
                    img = img.rotate(90, expand=True)
        except Exception:
            pass
        return img
    
    def _generate_filename(self, artwork, field_name, original_name):
        """Generate unique filename for uploaded image"""
        # Extract original extension
        name, ext = os.path.splitext(original_name.lower())
        
        # Map field names to prefixes
        field_prefixes = {
            'main_image_file': 'main',
            'frame1_image_file': 'frame1',
            'frame2_image_file': 'frame2', 
            'frame3_image_file': 'frame3',
            'frame4_image_file': 'frame4',
        }
        
        prefix = field_prefixes.get(field_name, 'image')
        unique_id = str(uuid.uuid4())[:8]
        
        # Use WebP for better compression
        return f"{prefix}-{unique_id}.webp"
    
    def _upload_to_supabase(self, processed_image, filename):
        """
        Upload processed image to Supabase storage
        
        This is a placeholder for actual Supabase integration
        You would implement this using the Supabase client
        """
        # TODO: Implement Supabase upload
        # Example implementation:
        # 
        # from utils.supabase_client import supabase_storage
        # 
        # # Convert PIL Image to bytes
        # import io
        # img_bytes = io.BytesIO()
        # processed_image.save(img_bytes, format='WEBP', quality=90)
        # img_bytes.seek(0)
        # 
        # # Upload to Supabase
        # result = supabase_storage.upload_file(
        #     bucket='artwork-images',
        #     path=filename,
        #     file_data=img_bytes.getvalue(),
        #     content_type='image/webp'
        # )
        # 
        # if result['success']:
        #     return f"supabase://{filename}"
        # else:
        #     raise Exception(f"Upload failed: {result['error']}")
        
        # For now, return placeholder URL
        return f"supabase://artwork-images/{filename}"


# Global service instance
artwork_image_service = ArtworkImageService()
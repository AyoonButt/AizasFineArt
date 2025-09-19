import os
from supabase import create_client, Client
from django.conf import settings
from typing import Optional
import uuid

class SupabaseStorageService:
    def __init__(self):
        # Debug: Check if credentials are loaded
        print(f"SUPABASE_URL: {getattr(settings, 'SUPABASE_URL', 'NOT SET')}")
        print(f"SUPABASE_SECRET_KEY: {'SET' if getattr(settings, 'SUPABASE_SECRET_KEY', None) else 'NOT SET'}")
        
        if not getattr(settings, 'SUPABASE_URL', None) or not getattr(settings, 'SUPABASE_SECRET_KEY', None):
            raise Exception("Supabase credentials are not properly configured in settings")
        
        self.client: Client = create_client(
            settings.SUPABASE_URL, 
            settings.SUPABASE_SECRET_KEY
        )
        self.bucket = 'art-storage'
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        """Ensure the storage bucket exists"""
        try:
            # Try to list the bucket to see if it exists
            self.client.storage.from_(self.bucket).list()
            print(f"Bucket '{self.bucket}' exists and is accessible")
        except Exception as e:
            print(f"Bucket check failed: {e}")
            # Try to create the bucket
            try:
                print(f"Attempting to create bucket '{self.bucket}'...")
                response = self.client.storage.create_bucket(self.bucket, {"public": False})
                print(f"Bucket creation response: {response}")
                print(f"Successfully created private bucket '{self.bucket}'")
            except Exception as create_error:
                print(f"Failed to create bucket: {create_error}")
                print(f"Please manually create the '{self.bucket}' bucket in Supabase Storage dashboard")
    
    def upload_image(self, file_path: str, file_data: bytes, content_type: str = 'image/jpeg') -> Optional[str]:
        """Upload image to Supabase storage"""
        try:
            print(f"Attempting to upload to bucket '{self.bucket}' with path '{file_path}'")
            print(f"Content type: {content_type}, Data size: {len(file_data)} bytes")
            
            response = self.client.storage.from_(self.bucket).upload(
                file_path, 
                file_data,
                file_options={'content-type': content_type}
            )
            
            print(f"Upload response: {response}")
            
            # Supabase returns different response formats, check for success
            if hasattr(response, 'status_code'):
                success = response.status_code in [200, 201]
            elif isinstance(response, dict):
                success = not response.get('error') and response.get('data')
            else:
                success = bool(response)
            
            if success:
                print(f"Upload successful for {file_path}")
                return self.get_public_url(file_path)
            else:
                print(f"Upload failed for {file_path}: {response}")
                return None
            
        except Exception as e:
            print(f"Upload error for {file_path}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def generate_unique_expiry(self, base_expires_in: int = 3600) -> int:
        """Generate slightly randomized expiry time to force URL uniqueness
        
        Since Supabase ignores query parameters in URL signing, we vary the expiry time
        by a few seconds to force different signed URLs while maintaining performance.
        """
        import random
        # Add 1-60 second randomization to base expiry time
        variation = random.randint(1, 60)
        return base_expires_in + variation
    
    def validate_signed_url(self, url: str) -> bool:
        """Test if signed URL is still valid (returns HTTP 200)"""
        try:
            import requests
            response = requests.head(url, timeout=3)
            return response.status_code == 200
        except Exception as e:
            # URL validation failed - consider it invalid
            return False

    def get_signed_url(self, file_path: str, expires_in: int = 3600, force_unique: bool = False) -> str:
        """Get signed URL for private bucket access with optional uniqueness forcing"""
        try:
            # Use unique expiry time to force different URLs if requested
            if force_unique:
                expires_in = self.generate_unique_expiry(expires_in)
            
            response = self.client.storage.from_(self.bucket).create_signed_url(
                file_path, 
                expires_in
            )
            return response.get('signedURL', '')
        except Exception as e:
            print(f"Signed URL error: {e}")
            return ''
    
    def get_public_url(self, file_path: str) -> str:
        """Get authenticated URL for private bucket"""
        return f"{settings.SUPABASE_URL}/storage/v1/object/authenticated/{self.bucket}/{file_path}"
    
    def get_transformed_url(self, file_path: str, width: int = None, height: int = None, 
                          quality: int = 80, format: str = 'origin', expires_in: int = 3600, force_unique: bool = False) -> str:
        """Get signed URL with image transformations for private bucket with caching"""
        from django.core.cache import cache
        
        # Create cache key for this specific transformation
        cache_key = f"supabase_url_{file_path}_{width}_{height}_{quality}_{format}_{expires_in}"
        if force_unique:
            cache_key += "_unique"
        
        cached_url = cache.get(cache_key)
        
        if cached_url and not force_unique:  # Skip cache when forcing uniqueness to ensure freshness
            return cached_url
            
        try:
            # Use unique expiry time to force different URLs if requested
            working_expires_in = expires_in
            if force_unique:
                working_expires_in = self.generate_unique_expiry(expires_in)
                
            # Build transformation object for Supabase
            transform_options = {}
            if width:
                transform_options['width'] = width
            if height:
                transform_options['height'] = height
            transform_options['quality'] = quality
            
            # Fix format parameter for Supabase API compatibility
            # Supported formats: webp, avif (case sensitive), or omit for original
            if format and format.lower() == 'webp':
                transform_options['format'] = 'webp'
            elif format and format.lower() == 'avif':
                transform_options['format'] = 'avif'
            # Don't include format for 'origin' - let Supabase keep original format
            
            # Create signed URL with transformations only if we have size transformations
            try:
                if width or height:
                    response = self.client.storage.from_(self.bucket).create_signed_url(
                        file_path, 
                        working_expires_in,
                        {'transform': transform_options}
                    )
                else:
                    # No transformations needed, just get basic signed URL
                    response = self.client.storage.from_(self.bucket).create_signed_url(
                        file_path, 
                        working_expires_in
                    )
                
                signed_url = response.get('signedURL', '')
                
            except Exception as transform_error:
                # If transformation fails, fall back to simple signed URL
                print(f"Transformation failed for {file_path}, falling back to simple URL: {transform_error}")
                try:
                    response = self.client.storage.from_(self.bucket).create_signed_url(
                        file_path, 
                        working_expires_in
                    )
                    signed_url = response.get('signedURL', '')
                except Exception as fallback_error:
                    print(f"Fallback URL generation also failed for {file_path}: {fallback_error}")
                    return ''
            
            # Cache the URL for 90% of its expiration time to avoid serving expired URLs
            # Don't cache unique URLs since they should always be fresh
            if not force_unique:
                cache_timeout = int(working_expires_in * 0.9)
                cache.set(cache_key, signed_url, cache_timeout)
            
            return signed_url
            
        except Exception as e:
            print(f"Transformation error: {e}")
            # Fallback to basic signed URL
            return self.get_signed_url(file_path, expires_in, force_unique)
    
    def delete_image(self, file_path: str) -> bool:
        """Delete image from storage"""
        try:
            response = self.client.storage.from_(self.bucket).remove([file_path])
            return response.status_code == 200
        except Exception as e:
            print(f"Delete error: {e}")
            return False
    
    def generate_unique_filename(self, original_filename: str, artwork_title: str = None) -> str:
        """Generate unique filename for artwork images"""
        import os
        from django.utils.text import slugify
        
        # Get file extension
        _, ext = os.path.splitext(original_filename)
        
        # Create base name from artwork title or use UUID
        if artwork_title:
            base_name = slugify(artwork_title)[:50]  # Limit length
        else:
            base_name = str(uuid.uuid4())[:8]
        
        # Add timestamp and UUID for uniqueness
        unique_id = str(uuid.uuid4())[:8]
        return f"artwork/{base_name}-{unique_id}{ext}"

# Singleton instance
supabase_storage = SupabaseStorageService()
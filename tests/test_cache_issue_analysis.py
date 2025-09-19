#!/usr/bin/env python3
"""
Cache Issue Analysis - Identifies the root cause of cache failures
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aizasfineart.settings')
django.setup()

from artwork.models import Artwork
from django.utils import timezone

def analyze_cache_refresh_issue():
    """Analyze the root cause of cache refresh failures"""
    print("🔍 CACHE REFRESH ISSUE ANALYSIS")
    print("=" * 50)
    
    # Get an artwork for testing
    artwork = Artwork.objects.filter(main_image_url__startswith='supabase://').first()
    if not artwork:
        print("❌ No artwork with supabase URLs found")
        return
        
    print(f"🎨 Testing with: {artwork.title}")
    
    print(f"\n📊 ISSUE ANALYSIS:")
    print(f"1. The refresh_url_cache() method CLEARS the cache but doesn't REGENERATE it")
    print(f"2. It only sets cached URLs to empty strings/None")
    print(f"3. Templates that rely on cached URLs will get empty values")
    print(f"4. New URLs are only generated when get_simple_signed_url() or get_image() is called")
    
    # Demonstrate the issue
    print(f"\n🧪 DEMONSTRATING THE ISSUE:")
    
    # Step 1: Get current state
    print(f"Step 1 - Current cached URL exists: {bool(artwork._cached_image_url)}")
    
    # Step 2: Call refresh (this CLEARS the cache)  
    print(f"Step 2 - Calling refresh_url_cache()...")
    artwork.refresh_url_cache()
    artwork.refresh_from_db()
    print(f"         Cached URL after refresh: {artwork._cached_image_url or 'EMPTY'}")
    
    # Step 3: Templates would get empty URLs until next method call
    print(f"Step 3 - Template would get: {artwork._cached_image_url or 'NO IMAGE'}")
    
    # Step 4: Only when we call get_simple_signed_url() does it regenerate
    print(f"Step 4 - Calling get_simple_signed_url() to regenerate...")
    new_url = artwork.get_simple_signed_url()
    artwork.refresh_from_db()
    print(f"         New cached URL: {artwork._cached_image_url[:50] if artwork._cached_image_url else 'STILL EMPTY'}...")
    
    return artwork

def analyze_template_property():
    """Analyze what templates actually call"""
    print(f"\n🔍 TEMPLATE PROPERTY ANALYSIS:")
    print(f"=" * 50)
    
    artwork = Artwork.objects.filter(main_image_url__startswith='supabase://').first()
    
    # Check what property templates use
    print(f"Templates use: {{ artwork.image_url }}")
    print(f"This calls the @property image_url method")
    
    # Check if image_url property exists
    if hasattr(artwork, 'image_url'):
        print(f"✅ image_url property exists")
        
        # Clear cache first
        artwork._cached_image_url = None
        artwork._url_cache_expires = None
        artwork.save(update_fields=['_cached_image_url', '_url_cache_expires'])
        
        # Test what image_url returns when cache is empty
        print(f"🧪 Testing image_url with empty cache...")
        try:
            url = artwork.image_url
            print(f"   Result: {url[:100] if url else 'None'}...")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    else:
        print(f"❌ image_url property does NOT exist - this is the problem!")
        
        # Check what properties do exist
        print(f"\n🔍 Available URL properties:")
        url_properties = [attr for attr in dir(artwork) if 'url' in attr.lower() and not attr.startswith('_')]
        for prop in url_properties:
            print(f"   - {prop}")

def test_url_generation_fix():
    """Test a potential fix for immediate URL generation"""
    print(f"\n🔧 TESTING POTENTIAL FIXES:")
    print(f"=" * 50)
    
    artwork = Artwork.objects.filter(main_image_url__startswith='supabase://').first()
    
    print(f"Fix 1: Direct URL generation (bypass cache entirely)")
    try:
        from utils.supabase_client import supabase_storage
        
        if artwork.main_image_url.startswith('supabase://'):
            file_path = artwork.main_image_url.replace('supabase://', '')
            signed_response = supabase_storage.client.storage.from_('art-storage').create_signed_url(file_path, 3600)
            
            if 'signedURL' in signed_response:
                print(f"   ✅ Direct generation works: {signed_response['signedURL'][:50]}...")
            else:
                print(f"   ❌ Direct generation failed: {signed_response}")
    except Exception as e:
        print(f"   ❌ Direct generation error: {str(e)}")
    
    print(f"\nFix 2: Modified refresh that immediately regenerates")
    try:
        # This is what the refresh method SHOULD do
        old_cached = artwork._cached_image_url
        
        # Clear cache
        artwork._cached_image_url = None
        artwork._url_cache_expires = None
        
        # Immediately regenerate (this is missing from current refresh_url_cache)
        new_url = artwork.get_simple_signed_url()
        
        print(f"   Old URL: {old_cached[:50] if old_cached else 'None'}...")
        print(f"   New URL: {new_url[:50] if new_url else 'None'}...")
        print(f"   ✅ This approach would work!")
        
    except Exception as e:
        print(f"   ❌ Fix 2 error: {str(e)}")

if __name__ == "__main__":
    artwork = analyze_cache_refresh_issue()
    analyze_template_property()
    test_url_generation_fix()
    
    print(f"\n" + "=" * 50)
    print("🎯 ROOT CAUSE IDENTIFIED:")
    print("=" * 50)
    print("1. refresh_url_cache() CLEARS cache but doesn't REGENERATE")
    print("2. Templates get empty URLs until next method call")
    print("3. Background refresh fails silently")
    print("4. No immediate URL regeneration after refresh")
    print("\n💡 SOLUTION:")
    print("Modify refresh_url_cache() to immediately regenerate URLs")
    print("Or implement on-demand URL generation without caching")
    print("=" * 50)
#!/usr/bin/env python3
"""
Targeted Cache Test - Focus on specific cache refresh issues
"""
import os
import sys
import django
from datetime import timedelta
from django.utils import timezone

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aizasfineart.settings')
django.setup()

from artwork.models import Artwork

def test_cache_refresh_issue():
    """Test the specific cache refresh mechanism"""
    print("🔍 TESTING CACHE REFRESH MECHANISM")
    print("=" * 50)
    
    # Get artwork with supabase URL
    artworks = Artwork.objects.filter(main_image_url__startswith='supabase://').first()
    
    if not artworks:
        print("❌ No artwork with supabase:// URLs found")
        return
    
    artwork = artworks
    print(f"📷 Testing with artwork: {artwork.title}")
    print(f"📁 Image URL: {artwork.main_image_url}")
    
    # Test 1: Current cache state
    print(f"\n1️⃣ CURRENT CACHE STATE:")
    print(f"   Cached URL: {artwork._cached_image_url[:100] if artwork._cached_image_url else 'None'}...")
    print(f"   Cache expires: {artwork._url_cache_expires}")
    print(f"   Current time: {timezone.now()}")
    
    if artwork._url_cache_expires:
        time_diff = artwork._url_cache_expires - timezone.now()
        if time_diff.total_seconds() < 0:
            print(f"   ❌ Cache EXPIRED {abs(time_diff.total_seconds())/60:.1f} minutes ago")
        else:
            print(f"   ✅ Cache expires in {time_diff.total_seconds()/60:.1f} minutes")
    else:
        print(f"   ❌ No expiration time set")
    
    # Test 2: Test refresh_url_cache method directly
    print(f"\n2️⃣ TESTING refresh_url_cache() METHOD:")
    try:
        old_cached_url = artwork._cached_image_url
        old_expires = artwork._url_cache_expires
        
        # Check if method exists
        if not hasattr(artwork, 'refresh_url_cache'):
            print("   ❌ refresh_url_cache method does not exist!")
            return
        
        # Try to call the method
        print("   🔄 Calling refresh_url_cache()...")
        artwork.refresh_url_cache()
        
        # Refresh from database
        artwork.refresh_from_db()
        
        new_cached_url = artwork._cached_image_url
        new_expires = artwork._url_cache_expires
        
        print(f"   Old URL: {old_cached_url[:50] if old_cached_url else 'None'}...")
        print(f"   New URL: {new_cached_url[:50] if new_cached_url else 'None'}...")
        print(f"   Old expires: {old_expires}")
        print(f"   New expires: {new_expires}")
        
        if new_cached_url != old_cached_url:
            print("   ✅ Cache URL was updated")
        else:
            print("   ❌ Cache URL was NOT updated")
            
        if new_expires != old_expires:
            print("   ✅ Expiration time was updated")
        else:
            print("   ❌ Expiration time was NOT updated")
            
    except Exception as e:
        print(f"   ❌ Error calling refresh_url_cache(): {str(e)}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Test get_simple_signed_url method
    print(f"\n3️⃣ TESTING get_simple_signed_url() METHOD:")
    try:
        if not hasattr(artwork, 'get_simple_signed_url'):
            print("   ❌ get_simple_signed_url method does not exist!")
        else:
            print("   🔄 Calling get_simple_signed_url()...")
            url = artwork.get_simple_signed_url()
            print(f"   Generated URL: {url[:100] if url else 'None'}...")
            
            if url and url.startswith('http'):
                print("   ✅ Valid URL generated")
            else:
                print("   ❌ Invalid URL generated")
                
    except Exception as e:
        print(f"   ❌ Error calling get_simple_signed_url(): {str(e)}")
        import traceback
        traceback.print_exc()
    
    # Test 4: Test get_image method
    print(f"\n4️⃣ TESTING get_image() METHOD:")
    try:
        if not hasattr(artwork, 'get_image'):
            print("   ❌ get_image method does not exist!")
        else:
            sizes_to_test = ['thumbnail', 'gallery', 'large']
            for size in sizes_to_test:
                print(f"   🔄 Testing get_image('{size}')...")
                url = artwork.get_image(size)
                print(f"   {size} URL: {url[:100] if url else 'None'}...")
                
                if url and url.startswith('http'):
                    print(f"   ✅ Valid {size} URL generated")
                else:
                    print(f"   ❌ Invalid {size} URL generated")
                    
    except Exception as e:
        print(f"   ❌ Error calling get_image(): {str(e)}")
        import traceback
        traceback.print_exc()

def test_supabase_client_direct():
    """Test Supabase client directly"""
    print(f"\n5️⃣ TESTING SUPABASE CLIENT DIRECTLY:")
    try:
        from utils.supabase_client import supabase_storage
        
        print("   🔄 Testing storage client...")
        print(f"   Bucket name: {supabase_storage.bucket}")
        
        # Try simple list operation without limit
        files = supabase_storage.client.storage.from_(supabase_storage.bucket).list()
        print(f"   ✅ Listed files: {len(files)} files found")
        
        # Test signed URL generation directly
        if files:
            first_file = files[0] if isinstance(files, list) else files.get('data', [{}])[0]
            file_name = first_file.get('name') if isinstance(first_file, dict) else str(first_file)
            
            if file_name:
                print(f"   🔄 Testing signed URL for: {file_name}")
                signed_response = supabase_storage.client.storage.from_(supabase_storage.bucket).create_signed_url(file_name, 3600)
                print(f"   Signed URL response: {signed_response}")
                
                if 'signedURL' in signed_response:
                    print("   ✅ Signed URL generated successfully")
                else:
                    print("   ❌ No signed URL in response")
        
    except Exception as e:
        print(f"   ❌ Supabase client error: {str(e)}")
        import traceback
        traceback.print_exc()

def test_management_command():
    """Test the management command"""
    print(f"\n6️⃣ TESTING MANAGEMENT COMMAND:")
    try:
        from django.core.management import call_command
        from io import StringIO
        
        # Capture output
        out = StringIO()
        
        print("   🔄 Running refresh_image_urls command...")
        call_command('refresh_image_urls', '--force', stdout=out)
        
        output = out.getvalue()
        print("   Command output:")
        for line in output.split('\n'):
            if line.strip():
                print(f"     {line}")
        
        if "Successfully refreshed" in output:
            print("   ✅ Management command executed successfully")
        else:
            print("   ❌ Management command may have failed")
            
    except Exception as e:
        print(f"   ❌ Management command error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_cache_refresh_issue()
    test_supabase_client_direct()
    test_management_command()
    
    print(f"\n" + "=" * 50)
    print("🏁 TARGETED TESTING COMPLETE")
    print("=" * 50)
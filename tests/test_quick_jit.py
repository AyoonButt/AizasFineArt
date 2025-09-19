#!/usr/bin/env python3
"""
Quick Just-In-Time Refresh Test - No long waits
"""

import os
import sys
import django
import time
import requests
from datetime import timedelta
from django.utils import timezone

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aizasfineart.settings')
django.setup()

from artwork.models import Artwork

def test_cache_logic():
    """Test the cache hit/miss logic"""
    print("🧪 TESTING CACHE HIT/MISS LOGIC")
    print("=" * 50)
    
    artwork = Artwork.objects.filter(main_image_url__startswith='supabase://').first()
    
    if not artwork:
        print("❌ No artwork found")
        return
    
    print(f"📷 Testing with artwork: {artwork.title}")
    
    # Test 1: Clear cache and generate
    print(f"\n1️⃣ CLEAR CACHE & GENERATE")
    artwork._cached_image_url = ""
    artwork._url_cache_expires = None
    artwork.save(update_fields=['_cached_image_url', '_url_cache_expires'])
    
    url1 = artwork.get_simple_signed_url()
    print(f"Generated: {url1[:80] if url1 else 'None'}...")
    
    # Test 2: Immediate second call (should hit cache)
    print(f"\n2️⃣ IMMEDIATE SECOND CALL (SHOULD HIT CACHE)")
    url2 = artwork.get_simple_signed_url()
    print(f"Generated: {url2[:80] if url2 else 'None'}...")
    
    if url1 == url2:
        print("✅ Cache hit (same URL)")
    else:
        print("❌ Cache miss (different URL)")
    
    # Test 3: Manually expire cache
    print(f"\n3️⃣ MANUALLY EXPIRE CACHE")
    old_expiry = artwork._url_cache_expires
    artwork._url_cache_expires = timezone.now() - timedelta(seconds=60)  # Expired 1 minute ago
    artwork.save(update_fields=['_url_cache_expires'])
    
    print(f"Cache expiry set to: {artwork._url_cache_expires} (expired)")
    
    url3 = artwork.get_simple_signed_url()
    print(f"Generated: {url3[:80] if url3 else 'None'}...")
    
    if url1 != url3:
        print("✅ Cache refresh (different URL after expiry)")
    else:
        print("❌ Cache not refreshed (same URL)")
    
    # Test 4: Check cache logic conditions
    print(f"\n4️⃣ CACHE LOGIC ANALYSIS")
    artwork.refresh_from_db()  # Get latest from database
    
    now = timezone.now()
    print(f"Current time: {now}")
    print(f"Cache expires: {artwork._url_cache_expires}")
    print(f"Cached URL exists: {bool(artwork._cached_image_url)}")
    
    if artwork._cached_image_url and artwork._url_cache_expires:
        time_until_buffer = (artwork._url_cache_expires - now - timezone.timedelta(seconds=30)).total_seconds()
        print(f"Time until cache buffer expires: {time_until_buffer:.1f} seconds")
        
        should_use_cache = now < (artwork._url_cache_expires - timezone.timedelta(seconds=30))
        print(f"Should use cache: {should_use_cache}")
    else:
        print("Missing cache data - will generate fresh")

def test_actual_url_expiry():
    """Test what happens when actual Supabase JWT expires"""
    print(f"\n🔗 TESTING ACTUAL URL EXPIRY")
    print("=" * 50)
    
    artwork = Artwork.objects.filter(main_image_url__startswith='supabase://').first()
    
    # Generate a very short-lived URL (30 seconds)
    print("Generating 30-second URL...")
    try:
        from utils.supabase_client import supabase_storage
        file_path = artwork.main_image_url.replace('supabase://', '')
        signed_response = supabase_storage.client.storage.from_(supabase_storage.bucket).create_signed_url(file_path, 30)
        
        if 'signedURL' in signed_response:
            short_url = signed_response['signedURL']
            print(f"Short URL: {short_url[:80]}...")
            
            # Test immediately
            print("Testing URL immediately...")
            try:
                response = requests.head(short_url, timeout=5)
                print(f"✅ Status: {response.status_code}")
            except Exception as e:
                print(f"❌ Immediate test failed: {e}")
            
            # Wait 35 seconds then test
            print("Waiting 35 seconds for JWT to expire...")
            time.sleep(35)
            
            print("Testing expired URL...")
            try:
                response = requests.head(short_url, timeout=5)
                print(f"Status after expiry: {response.status_code}")
                if response.status_code == 200:
                    print("⚠️ URL still works (unexpected)")
                else:
                    print("✅ URL expired as expected")
            except Exception as e:
                print(f"✅ URL expired: {e}")
        
    except Exception as e:
        print(f"❌ Error testing short URL: {e}")

if __name__ == "__main__":
    try:
        test_cache_logic()
        test_actual_url_expiry()
        print(f"\n🏁 TESTING COMPLETE")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
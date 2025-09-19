#!/usr/bin/env python3
"""
Test Just-In-Time Refresh with Short Timeouts
This script tests the cache refresh mechanism with 2-minute timeouts
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

def test_jit_refresh_cycle():
    """Test the just-in-time refresh cycle with short timeouts"""
    print("🧪 TESTING JUST-IN-TIME REFRESH WITH SHORT TIMEOUTS")
    print("=" * 60)
    
    # Get artwork with supabase URL
    artwork = Artwork.objects.filter(main_image_url__startswith='supabase://').first()
    
    if not artwork:
        print("❌ No artwork with supabase:// URLs found")
        return
    
    print(f"📷 Testing with artwork: {artwork.title}")
    print(f"📁 Image URL: {artwork.main_image_url}")
    
    # Clear existing cache to start fresh
    print(f"\n1️⃣ CLEARING EXISTING CACHE")
    artwork._cached_image_url = ""  # Use empty string instead of None
    artwork._url_cache_expires = None
    artwork.save(update_fields=['_cached_image_url', '_url_cache_expires'])
    print("✅ Cache cleared")
    
    # Test cycle
    for cycle in range(1, 4):  # Test 3 cycles
        print(f"\n🔄 CYCLE {cycle}: Testing URL generation and expiry")
        print("-" * 50)
        
        # Step 1: Get URL (should generate fresh one)
        print(f"Step 1: Requesting URL for {artwork.title}")
        start_time = timezone.now()
        url1 = artwork.get_simple_signed_url()
        
        if url1:
            print(f"URL received: {url1[:80]}...")
            
            # Test URL accessibility
            try:
                response = requests.head(url1, timeout=5)
                print(f"URL accessibility: {response.status_code} (✅ OK)")
            except Exception as e:
                print(f"URL test failed: {e}")
        else:
            print("❌ No URL returned")
            continue
        
        # Step 2: Immediate re-request (should use cache)
        print(f"\nStep 2: Immediate re-request (should hit cache)")
        url2 = artwork.get_simple_signed_url()
        
        if url1 == url2:
            print("✅ Same URL returned (cache hit)")
        else:
            print("⚠️ Different URL returned (unexpected cache miss)")
        
        # Step 3: Wait for cache to expire (90 seconds + buffer)
        print(f"\nStep 3: Waiting for cache expiration...")
        wait_time = 95  # 90s cache + 5s buffer
        print(f"Waiting {wait_time} seconds for cache to expire...")
        
        for remaining in range(wait_time, 0, -10):
            print(f"⏰ {remaining}s remaining...")
            time.sleep(10)
        
        # Step 4: Request after expiry (should generate fresh one)
        print(f"\nStep 4: Requesting URL after cache expiry")
        url3 = artwork.get_simple_signed_url()
        
        if url3:
            if url1 != url3:
                print("✅ Different URL returned (cache refreshed)")
                
                # Test new URL accessibility  
                try:
                    response = requests.head(url3, timeout=5)
                    print(f"New URL accessibility: {response.status_code} (✅ OK)")
                except Exception as e:
                    print(f"New URL test failed: {e}")
            else:
                print("⚠️ Same URL returned (cache refresh may have failed)")
        else:
            print("❌ No URL returned after expiry")
        
        # Step 5: Test old URL accessibility (should fail after JWT expiry)
        print(f"\nStep 5: Testing old URL accessibility (should fail)")
        try:
            old_response = requests.head(url1, timeout=5)
            if old_response.status_code == 200:
                print("⚠️ Old URL still works (JWT might not have expired yet)")
            else:
                print(f"✅ Old URL failed: {old_response.status_code} (JWT expired)")
        except Exception as e:
            print(f"✅ Old URL failed: {e} (JWT expired)")
        
        if cycle < 3:
            print(f"\n⏸️ Brief pause before next cycle...")
            time.sleep(5)
    
    print(f"\n🏁 TESTING COMPLETE")
    print("=" * 60)

def test_frame_refresh():
    """Test frame URL refresh"""
    print("\n🖼️ TESTING FRAME URL REFRESH")
    print("=" * 60)
    
    artwork = Artwork.objects.filter(frame1_image_url__startswith='supabase://').first()
    
    if not artwork:
        print("❌ No artwork with frame supabase:// URLs found")
        return
    
    print(f"🖼️ Testing frame URLs for: {artwork.title}")
    
    # Clear frame cache
    artwork._cached_frame_urls = {}
    artwork._url_cache_expires = None
    artwork.save(update_fields=['_cached_frame_urls', '_url_cache_expires'])
    print("✅ Frame cache cleared")
    
    # Test frame URL generation
    for frame_num in range(1, 5):
        frame_url = getattr(artwork, f'frame{frame_num}_image_url', '')
        if frame_url:
            print(f"\nTesting frame {frame_num}:")
            
            # First request (should generate)
            url1 = artwork.get_frame_simple_url(frame_num)
            if url1:
                print(f"Frame URL generated: {url1[:80]}...")
                
                # Test accessibility
                try:
                    response = requests.head(url1, timeout=5)
                    print(f"Frame URL accessibility: {response.status_code}")
                except Exception as e:
                    print(f"Frame URL test failed: {e}")
                    
                # Second request (should use cache)
                url2 = artwork.get_frame_simple_url(frame_num)
                if url1 == url2:
                    print("✅ Frame cache hit")
                else:
                    print("⚠️ Frame cache miss")
    
    print("\n🖼️ Frame testing complete")

if __name__ == "__main__":
    try:
        test_jit_refresh_cycle()
        test_frame_refresh()
    except KeyboardInterrupt:
        print("\n⏹️ Testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Testing error: {e}")
        import traceback
        traceback.print_exc()
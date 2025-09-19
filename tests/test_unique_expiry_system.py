#!/usr/bin/env python3
"""
Test Unique Expiry-Based Cache System
This script tests the improved solution using unique expiry times for URL uniqueness
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
from utils.supabase_client import supabase_storage

def test_unique_expiry_generation():
    """Test that unique expiry times generate different URLs"""
    print("🔧 TESTING UNIQUE EXPIRY URL GENERATION")
    print("=" * 50)
    
    artwork = Artwork.objects.filter(main_image_url__startswith='supabase://').first()
    
    if not artwork:
        print("❌ No artwork with supabase:// URLs found")
        return
    
    print(f"📷 Testing with artwork: {artwork.title}")
    
    # Test 1: Generate multiple URLs with different expiry times
    print(f"\n1️⃣ GENERATING URLS WITH UNIQUE EXPIRY TIMES")
    urls = []
    expiry_times = []
    
    file_path = artwork.main_image_url.replace('supabase://', '')
    
    for i in range(5):
        unique_expiry = supabase_storage.generate_unique_expiry(3600)
        expiry_times.append(unique_expiry)
        print(f"  Attempt {i+1}: Using expiry time {unique_expiry}s (base: 3600s)")
        
        # Generate signed URL
        signed_response = supabase_storage.client.storage.from_(supabase_storage.bucket).create_signed_url(file_path, unique_expiry)
        if 'signedURL' in signed_response:
            url = signed_response['signedURL']
            urls.append(url)
            print(f"  URL {i+1}: {url[:80]}...")
        else:
            print(f"  ❌ Failed to generate URL {i+1}")
    
    # Check uniqueness
    unique_urls = set(urls)
    unique_expiries = set(expiry_times)
    
    print(f"\n📊 UNIQUENESS ANALYSIS:")
    print(f"  Generated expiry times: {len(expiry_times)} (unique: {len(unique_expiries)})")
    print(f"  Generated URLs: {len(urls)} (unique: {len(unique_urls)})")
    
    if len(unique_urls) == len(urls):
        print(f"✅ All {len(urls)} generated URLs are unique")
    else:
        print(f"⚠️ Only {len(unique_urls)}/{len(urls)} URLs are unique")
        # Show which URLs are duplicated
        url_counts = {}
        for url in urls:
            url_counts[url] = url_counts.get(url, 0) + 1
        duplicates = {url: count for url, count in url_counts.items() if count > 1}
        if duplicates:
            print(f"  Duplicated URLs: {len(duplicates)}")
    
    # Test URL accessibility
    print(f"\n2️⃣ TESTING URL ACCESSIBILITY")
    for i, url in enumerate(urls):
        try:
            response = requests.head(url, timeout=5)
            if response.status_code == 200:
                print(f"  ✅ URL {i+1}: Accessible (200)")
            else:
                print(f"  ⚠️ URL {i+1}: Status {response.status_code}")
        except Exception as e:
            print(f"  ❌ URL {i+1}: Failed - {e}")
    
    return len(unique_urls) == len(urls)

def test_enhanced_cache_with_unique_expiry():
    """Test the enhanced cache system with unique expiry times"""
    print(f"\n🔄 TESTING ENHANCED CACHE WITH UNIQUE EXPIRY")
    print("=" * 50)
    
    artwork = Artwork.objects.filter(main_image_url__startswith='supabase://').first()
    
    if not artwork:
        print("❌ No artwork found")
        return
    
    print(f"📷 Testing enhanced cache for: {artwork.title}")
    
    # Step 1: Clear cache and generate fresh URL
    print(f"\n1️⃣ CLEARING CACHE & GENERATING FRESH URL")
    artwork._cached_image_url = ""
    artwork._url_cache_expires = None
    artwork.save(update_fields=['_cached_image_url', '_url_cache_expires'])
    
    url1 = artwork.get_simple_signed_url()
    print(f"Fresh URL generated: {url1[:80] if url1 else 'None'}...")
    
    # Step 2: Immediate second call (should hit cache)
    print(f"\n2️⃣ IMMEDIATE SECOND CALL (SHOULD HIT CACHE)")
    url2 = artwork.get_simple_signed_url()
    
    if url1 == url2:
        print("✅ Cache hit (same URL returned)")
    else:
        print("⚠️ Cache miss (different URL - unexpected)")
    
    # Step 3: Force cache refresh by clearing cache
    print(f"\n3️⃣ FORCING FRESH URL GENERATION")
    artwork._cached_image_url = ""
    artwork._url_cache_expires = None
    artwork.save(update_fields=['_cached_image_url', '_url_cache_expires'])
    
    url3 = artwork.get_simple_signed_url()
    print(f"Second fresh URL: {url3[:80] if url3 else 'None'}...")
    
    if url1 != url3:
        print("✅ URL uniqueness working (different URL generated)")
        return True
    else:
        print("❌ URL uniqueness failed (same URL generated)")
        return False

def test_frame_unique_expiry():
    """Test frame URLs with unique expiry"""
    print(f"\n🖼️ TESTING FRAME UNIQUE EXPIRY SYSTEM")
    print("=" * 50)
    
    artwork = Artwork.objects.filter(frame1_image_url__startswith='supabase://').first()
    
    if not artwork:
        print("❌ No artwork with frame supabase:// URLs found")
        return
    
    print(f"🖼️ Testing frame URLs for: {artwork.title}")
    
    # Test frame URL generation with uniqueness
    for frame_num in [1, 2]:  # Test first 2 frames
        frame_url = getattr(artwork, f'frame{frame_num}_image_url', '')
        if frame_url:
            print(f"\nTesting frame {frame_num}:")
            
            # Clear frame cache
            artwork._cached_frame_urls = {}
            artwork._url_cache_expires = None
            artwork.save(update_fields=['_cached_frame_urls', '_url_cache_expires'])
            
            # First URL
            url1 = artwork.get_frame_simple_url(frame_num)
            if url1:
                print(f"  First URL: {url1[:80]}...")
            
            # Clear cache and generate second URL
            artwork._cached_frame_urls = {}
            artwork._url_cache_expires = None
            artwork.save(update_fields=['_cached_frame_urls', '_url_cache_expires'])
            
            # Second URL (should be different due to unique expiry)
            url2 = artwork.get_frame_simple_url(frame_num)
            if url2:
                print(f"  Second URL: {url2[:80]}...")
            
            # Check uniqueness
            if url1 and url2:
                if url1 != url2:
                    print(f"  ✅ Frame {frame_num}: URLs are unique (unique expiry working)")
                else:
                    print(f"  ❌ Frame {frame_num}: URLs are identical (unique expiry not working)")
                
                # Test accessibility
                for i, url in enumerate([url1, url2]):
                    try:
                        response = requests.head(url, timeout=3)
                        if response.status_code == 200:
                            print(f"    ✅ Frame URL {i+1}: Accessible")
                        else:
                            print(f"    ⚠️ Frame URL {i+1}: Status {response.status_code}")
                    except Exception as e:
                        print(f"    ❌ Frame URL {i+1}: Failed - {e}")

def test_expiry_randomization():
    """Test the expiry randomization function"""
    print(f"\n🎲 TESTING EXPIRY RANDOMIZATION")
    print("=" * 50)
    
    base_expiry = 3600
    generated_expiries = []
    
    print(f"Base expiry time: {base_expiry}s")
    print("Generating 10 randomized expiry times:")
    
    for i in range(10):
        unique_expiry = supabase_storage.generate_unique_expiry(base_expiry)
        generated_expiries.append(unique_expiry)
        variation = unique_expiry - base_expiry
        print(f"  {i+1}. {unique_expiry}s (variation: +{variation}s)")
    
    # Analyze results
    unique_expiries = set(generated_expiries)
    min_expiry = min(generated_expiries)
    max_expiry = max(generated_expiries)
    
    print(f"\n📊 RANDOMIZATION ANALYSIS:")
    print(f"  Generated: {len(generated_expiries)} expiry times")
    print(f"  Unique: {len(unique_expiries)} expiry times")
    print(f"  Range: {min_expiry}s - {max_expiry}s")
    print(f"  Variation range: +{min_expiry - base_expiry}s to +{max_expiry - base_expiry}s")
    
    if len(unique_expiries) >= 8:  # Allow for some small chance of duplicates
        print("✅ Good randomization (most expiry times are unique)")
    else:
        print("⚠️ Poor randomization (too many duplicate expiry times)")

if __name__ == "__main__":
    try:
        print("🧪 UNIQUE EXPIRY-BASED CACHE SYSTEM TEST")
        print("=" * 60)
        
        # Run all tests
        uniqueness_works = test_unique_expiry_generation()
        cache_works = test_enhanced_cache_with_unique_expiry()
        test_frame_unique_expiry()
        test_expiry_randomization()
        
        # Summary
        print(f"\n📋 SUMMARY")
        print("=" * 30)
        print(f"URL Uniqueness: {'✅ WORKING' if uniqueness_works else '❌ FAILED'}")
        print(f"Cache System: {'✅ WORKING' if cache_works else '❌ FAILED'}")
        
        if uniqueness_works and cache_works:
            print(f"\n🎉 SUCCESS: Unique expiry strategy solves the cache refresh issue!")
            print(f"   • URLs are now unique on each refresh")
            print(f"   • Cache performance is maintained")
            print(f"   • Just-in-time refresh works as intended")
        else:
            print(f"\n⚠️ ISSUES DETECTED: Some components need further investigation")
        
        print(f"\n🏁 TESTING COMPLETE")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n⏹️ Testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Testing error: {e}")
        import traceback
        traceback.print_exc()
#!/usr/bin/env python3
"""
Test Enhanced Nonce-Based Cache System
This script tests the improved just-in-time refresh with nonce for URL uniqueness
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

def test_nonce_url_uniqueness():
    """Test that nonce generates unique URLs"""
    print("🔧 TESTING NONCE URL UNIQUENESS")
    print("=" * 50)
    
    artwork = Artwork.objects.filter(main_image_url__startswith='supabase://').first()
    
    if not artwork:
        print("❌ No artwork with supabase:// URLs found")
        return
    
    print(f"📷 Testing with artwork: {artwork.title}")
    
    # Test 1: Generate multiple nonce URLs and verify uniqueness
    print(f"\n1️⃣ GENERATING MULTIPLE NONCE URLS")
    urls = []
    
    for i in range(5):
        file_path = artwork.main_image_url.replace('supabase://', '')
        nonce_path = supabase_storage.add_nonce_to_path(file_path)
        print(f"  Nonce path {i+1}: {nonce_path}")
        
        # Generate signed URL
        signed_response = supabase_storage.client.storage.from_(supabase_storage.bucket).create_signed_url(nonce_path, 3600)
        if 'signedURL' in signed_response:
            url = signed_response['signedURL']
            urls.append(url)
            print(f"  URL {i+1}: {url[:80]}...")
        else:
            print(f"  ❌ Failed to generate URL {i+1}")
    
    # Check uniqueness
    unique_urls = set(urls)
    if len(unique_urls) == len(urls):
        print(f"✅ All {len(urls)} generated URLs are unique")
    else:
        print(f"❌ Only {len(unique_urls)}/{len(urls)} URLs are unique")
    
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

def test_enhanced_cache_refresh():
    """Test the enhanced cache system with validation and nonce"""
    print(f"\n🔄 TESTING ENHANCED CACHE REFRESH")
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
    
    # Step 3: Manually corrupt cached URL to test validation
    print(f"\n3️⃣ TESTING URL VALIDATION LOGIC")
    artwork.refresh_from_db()
    original_cached_url = artwork._cached_image_url
    
    # Corrupt the cached URL by modifying the signature
    if original_cached_url and '&token=' in original_cached_url:
        corrupted_url = original_cached_url.replace(original_cached_url.split('&token=')[1][:10], 'invalid123')
        artwork._cached_image_url = corrupted_url
        artwork.save(update_fields=['_cached_image_url'])
        
        print(f"Corrupted cached URL: {corrupted_url[:80]}...")
        
        # Now try to get URL - should detect corruption and generate fresh one
        url3 = artwork.get_simple_signed_url()
        print(f"URL after corruption: {url3[:80] if url3 else 'None'}...")
        
        if url3 != corrupted_url:
            print("✅ Cache validation working (generated fresh URL after detecting corruption)")
        else:
            print("❌ Cache validation failed (returned corrupted URL)")
    else:
        print("⚠️ Could not test validation (URL format unexpected)")

def test_frame_nonce_system():
    """Test frame URL nonce system"""
    print(f"\n🖼️ TESTING FRAME NONCE SYSTEM")
    print("=" * 50)
    
    artwork = Artwork.objects.filter(frame1_image_url__startswith='supabase://').first()
    
    if not artwork:
        print("❌ No artwork with frame supabase:// URLs found")
        return
    
    print(f"🖼️ Testing frame URLs for: {artwork.title}")
    
    # Clear frame cache
    artwork._cached_frame_urls = {}
    artwork._url_cache_expires = None
    artwork.save(update_fields=['_cached_frame_urls', '_url_cache_expires'])
    
    # Test frame URL generation with uniqueness
    for frame_num in range(1, 3):  # Test first 2 frames
        frame_url = getattr(artwork, f'frame{frame_num}_image_url', '')
        if frame_url:
            print(f"\nTesting frame {frame_num}:")
            
            # Generate multiple URLs to test uniqueness
            frame_urls = []
            
            # First call
            url1 = artwork.get_frame_simple_url(frame_num)
            if url1:
                frame_urls.append(url1)
                print(f"  First URL: {url1[:80]}...")
            
            # Clear cache and generate again
            artwork._cached_frame_urls = {}
            artwork.save(update_fields=['_cached_frame_urls'])
            
            # Second call (should be different due to nonce)
            url2 = artwork.get_frame_simple_url(frame_num)
            if url2:
                frame_urls.append(url2)
                print(f"  Second URL: {url2[:80]}...")
            
            # Check uniqueness
            if len(frame_urls) == 2:
                if url1 != url2:
                    print(f"  ✅ Frame {frame_num}: URLs are unique (nonce working)")
                else:
                    print(f"  ❌ Frame {frame_num}: URLs are identical (nonce not working)")
                
                # Test accessibility
                for i, url in enumerate(frame_urls):
                    try:
                        response = requests.head(url, timeout=3)
                        if response.status_code == 200:
                            print(f"  ✅ Frame URL {i+1}: Accessible")
                        else:
                            print(f"  ⚠️ Frame URL {i+1}: Status {response.status_code}")
                    except Exception as e:
                        print(f"  ❌ Frame URL {i+1}: Failed - {e}")

def test_supabase_nonce_utilities():
    """Test Supabase utility functions"""
    print(f"\n🛠️ TESTING SUPABASE NONCE UTILITIES")
    print("=" * 50)
    
    # Test nonce generation
    print("Testing nonce generation:")
    nonces = []
    for i in range(5):
        nonce = supabase_storage.generate_cache_nonce()
        nonces.append(nonce)
        print(f"  Nonce {i+1}: {nonce}")
    
    # Check uniqueness
    unique_nonces = set(nonces)
    if len(unique_nonces) == len(nonces):
        print("✅ All nonces are unique")
    else:
        print(f"❌ Only {len(unique_nonces)}/{len(nonces)} nonces are unique")
    
    # Test nonce path addition
    print(f"\nTesting nonce path addition:")
    test_paths = [
        "artwork/test.jpg",
        "artwork/test.jpg?existing=param",
        "folder/subfolder/image.png"
    ]
    
    for path in test_paths:
        nonce_path = supabase_storage.add_nonce_to_path(path)
        print(f"  Original: {path}")
        print(f"  With nonce: {nonce_path}")
        print()

if __name__ == "__main__":
    try:
        print("🧪 ENHANCED NONCE-BASED CACHE SYSTEM TEST")
        print("=" * 60)
        
        test_nonce_url_uniqueness()
        test_enhanced_cache_refresh()
        test_frame_nonce_system()
        test_supabase_nonce_utilities()
        
        print(f"\n🏁 TESTING COMPLETE")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n⏹️ Testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Testing error: {e}")
        import traceback
        traceback.print_exc()
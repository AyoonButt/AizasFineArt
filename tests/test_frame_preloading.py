#!/usr/bin/env python3
"""
Test script to verify frame image preloading on artwork detail pages
"""

import os
import sys
import django
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin

# Setup Django environment
sys.path.append('/mnt/c/Users/ayoon/projects/AizasFineArt')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aizasfineart.settings')
django.setup()

from artwork.models import Artwork

class FramePreloadingTest:
    def __init__(self, base_url='http://localhost:8000'):
        self.base_url = base_url
        self.session = requests.Session()
        
    def test_artwork_detail_preloading(self, artwork_slug=None):
        """Test frame image preloading on artwork detail page"""
        
        # Get first artwork if no slug provided
        if not artwork_slug:
            artwork = Artwork.objects.filter(status='active').first()
            if not artwork:
                print("❌ No active artwork found in database")
                return False
            artwork_slug = artwork.slug
        
        url = f"{self.base_url}/artwork/{artwork_slug}/"
        print(f"🔍 Testing artwork detail page: {url}")
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Check for main image preload
            main_preload = soup.find('link', {
                'rel': 'preload',
                'as': 'image',
                'fetchpriority': 'high'
            })
            
            if main_preload:
                print(f"✅ Main image preload found: {main_preload.get('href', '')[:50]}...")
            else:
                print("❌ Main image preload NOT found")
            
            # Check for frame image preloads
            frame_preloads = soup.find_all('link', {
                'rel': 'preload',
                'as': 'image'
            })
            
            # Filter out main image preload to count frame preloads
            frame_only_preloads = [link for link in frame_preloads 
                                 if not link.get('fetchpriority') == 'high']
            
            print(f"📊 Frame image preloads found: {len(frame_only_preloads)}")
            
            for i, preload in enumerate(frame_only_preloads, 1):
                href = preload.get('href', '')
                print(f"   Frame {i}: {href[:60]}...")
                
                # Test if frame image is accessible
                self.test_image_accessibility(href)
            
            # Check for frame thumbnails in HTML
            frame_thumbnails = soup.find_all('button', {'data-image': re.compile(r'frame\d+')})
            print(f"🖼️  Frame thumbnails in HTML: {len(frame_thumbnails)}")
            
            # Check for preloadFrameImages JavaScript function
            scripts = soup.find_all('script')
            preload_js_found = False
            for script in scripts:
                if script.string and 'preloadFrameImages' in script.string:
                    preload_js_found = True
                    break
            
            if preload_js_found:
                print("✅ JavaScript preloading function found")
            else:
                print("❌ JavaScript preloading function NOT found")
            
            return len(frame_only_preloads) > 0 and preload_js_found
            
        except requests.RequestException as e:
            print(f"❌ Error fetching artwork page: {e}")
            return False
    
    def test_image_accessibility(self, image_url):
        """Test if frame image URL is accessible"""
        if not image_url:
            return False
            
        try:
            # Make HEAD request to check if image exists
            response = self.session.head(image_url, timeout=5)
            if response.status_code == 200:
                print(f"   ✅ Image accessible ({response.status_code})")
                return True
            else:
                print(f"   ❌ Image not accessible ({response.status_code})")
                return False
        except requests.RequestException as e:
            print(f"   ❌ Image request failed: {e}")
            return False
    
    def test_all_artworks_with_frames(self):
        """Test preloading for all artworks that have frame images"""
        artworks_with_frames = Artwork.objects.filter(
            status='active'
        ).exclude(
            frame1_gallery_url__isnull=True,
            frame2_gallery_url__isnull=True,
            frame3_gallery_url__isnull=True,
            frame4_gallery_url__isnull=True
        )
        
        print(f"🔍 Testing {artworks_with_frames.count()} artworks with frame images")
        
        results = []
        for artwork in artworks_with_frames[:5]:  # Test first 5 to avoid overwhelming
            print(f"\n📝 Testing: {artwork.title} ({artwork.slug})")
            result = self.test_artwork_detail_preloading(artwork.slug)
            results.append(result)
        
        success_rate = sum(results) / len(results) * 100 if results else 0
        print(f"\n📊 Success rate: {success_rate:.1f}% ({sum(results)}/{len(results)})")
        
        return success_rate >= 80  # 80% success rate threshold

def main():
    print("🚀 Starting Frame Image Preloading Test")
    print("=" * 50)
    
    tester = FramePreloadingTest()
    
    # Test single artwork first
    print("\n1️⃣ Testing single artwork...")
    single_result = tester.test_artwork_detail_preloading()
    
    # Test multiple artworks
    print("\n2️⃣ Testing multiple artworks...")
    multiple_result = tester.test_all_artworks_with_frames()
    
    print("\n" + "=" * 50)
    print("📋 TEST SUMMARY")
    print(f"Single artwork test: {'✅ PASS' if single_result else '❌ FAIL'}")
    print(f"Multiple artwork test: {'✅ PASS' if multiple_result else '❌ FAIL'}")
    
    overall_pass = single_result and multiple_result
    print(f"Overall result: {'✅ PASS' if overall_pass else '❌ FAIL'}")
    
    if not overall_pass:
        print("\n🔧 TROUBLESHOOTING TIPS:")
        print("- Check if Django development server is running")
        print("- Verify frame images exist in artwork model data")
        print("- Check template rendering and JavaScript inclusion")
        print("- Inspect network requests in browser dev tools")

if __name__ == '__main__':
    main()
#!/usr/bin/env python3
"""
Image Cache Diagnosis Test Script
This script tests the image URL caching system to identify failure points.
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
from utils.supabase_client import supabase_storage

class ImageCacheDiagnostic:
    def __init__(self):
        self.results = []
        self.errors = []
        
    def log_result(self, test_name, status, message, details=None):
        """Log test results"""
        result = {
            'test': test_name,
            'status': status,
            'message': message,
            'details': details,
            'timestamp': timezone.now()
        }
        self.results.append(result)
        status_symbol = "✓" if status == "PASS" else "✗" if status == "FAIL" else "⚠"
        print(f"{status_symbol} {test_name}: {message}")
        if details:
            print(f"  Details: {details}")
    
    def test_supabase_connection(self):
        """Test 1: Supabase connection and credentials"""
        try:
            from django.conf import settings
            
            # Check credentials
            supabase_url = getattr(settings, 'SUPABASE_URL', None)
            supabase_key = getattr(settings, 'SUPABASE_SECRET_KEY', None)
            
            if not supabase_url or not supabase_key:
                self.log_result(
                    "Supabase Credentials", 
                    "FAIL", 
                    "Missing Supabase credentials in settings",
                    f"URL: {'SET' if supabase_url else 'NOT SET'}, KEY: {'SET' if supabase_key else 'NOT SET'}"
                )
                return False
            
            # Test connection
            storage_service = supabase_storage
            storage_service.client.storage.from_(storage_service.bucket).list(limit=1)
            
            self.log_result(
                "Supabase Connection", 
                "PASS", 
                "Successfully connected to Supabase storage"
            )
            return True
            
        except Exception as e:
            self.log_result(
                "Supabase Connection", 
                "FAIL", 
                f"Supabase connection failed: {str(e)}"
            )
            return False
    
    def test_artwork_with_supabase_urls(self):
        """Test 2: Find artworks with supabase:// URLs"""
        try:
            artworks = Artwork.objects.filter(main_image_url__startswith='supabase://').select_related()
            count = artworks.count()
            
            if count == 0:
                self.log_result(
                    "Supabase URLs", 
                    "WARN", 
                    "No artworks found with supabase:// URLs"
                )
                return []
            
            self.log_result(
                "Supabase URLs", 
                "PASS", 
                f"Found {count} artworks with supabase:// URLs"
            )
            
            # Return first 3 for detailed testing
            return list(artworks[:3])
            
        except Exception as e:
            self.log_result(
                "Supabase URLs", 
                "FAIL", 
                f"Error querying artworks: {str(e)}"
            )
            return []
    
    def test_url_generation_methods(self, artwork):
        """Test 3: Test different URL generation methods"""
        methods_to_test = [
            ('get_simple_signed_url', artwork.get_simple_signed_url),
            ('get_image (gallery)', lambda: artwork.get_image('gallery')),
            ('get_image (thumbnail)', lambda: artwork.get_image('thumbnail')),
        ]
        
        for method_name, method in methods_to_test:
            try:
                url = method()
                if url and url.startswith('http'):
                    self.log_result(
                        f"URL Generation - {method_name}", 
                        "PASS", 
                        f"Generated valid URL: {url[:50]}..."
                    )
                else:
                    self.log_result(
                        f"URL Generation - {method_name}", 
                        "FAIL", 
                        f"Invalid URL generated: {url}"
                    )
            except Exception as e:
                self.log_result(
                    f"URL Generation - {method_name}", 
                    "FAIL", 
                    f"Exception during URL generation: {str(e)}"
                )
    
    def test_cache_state(self, artwork):
        """Test 4: Examine cache state"""
        cache_info = {
            'cached_image_url': artwork._cached_image_url,
            'cached_thumbnail_url': artwork._cached_thumbnail_url, 
            'cached_frame_urls': artwork._cached_frame_urls,
            'url_cache_expires': artwork._url_cache_expires,
            'now': timezone.now()
        }
        
        # Check if cache is expired
        if cache_info['url_cache_expires']:
            time_until_expiry = cache_info['url_cache_expires'] - cache_info['now']
            if time_until_expiry.total_seconds() < 0:
                status = "FAIL"
                message = f"Cache expired {abs(time_until_expiry.total_seconds())/60:.1f} minutes ago"
            elif time_until_expiry.total_seconds() < 1800:  # 30 minutes
                status = "WARN"
                message = f"Cache expires in {time_until_expiry.total_seconds()/60:.1f} minutes"
            else:
                status = "PASS"
                message = f"Cache expires in {time_until_expiry.total_seconds()/60:.1f} minutes"
        else:
            status = "FAIL"
            message = "No cache expiration time set"
        
        self.log_result(
            f"Cache State - {artwork.title}", 
            status, 
            message,
            cache_info
        )
        
        return cache_info
    
    def test_manual_refresh(self, artwork):
        """Test 5: Test manual cache refresh"""
        try:
            old_cached_url = artwork._cached_image_url
            old_expires = artwork._url_cache_expires
            
            # Manually refresh
            artwork.refresh_url_cache()
            artwork.refresh_from_db()
            
            new_cached_url = artwork._cached_image_url
            new_expires = artwork._url_cache_expires
            
            if new_cached_url != old_cached_url or new_expires != old_expires:
                self.log_result(
                    f"Manual Refresh - {artwork.title}", 
                    "PASS", 
                    "Cache was successfully refreshed",
                    {
                        'old_url': old_cached_url[:50] + '...' if old_cached_url else None,
                        'new_url': new_cached_url[:50] + '...' if new_cached_url else None,
                        'old_expires': old_expires,
                        'new_expires': new_expires
                    }
                )
            else:
                self.log_result(
                    f"Manual Refresh - {artwork.title}", 
                    "FAIL", 
                    "Cache refresh did not change cached values"
                )
                
        except Exception as e:
            self.log_result(
                f"Manual Refresh - {artwork.title}", 
                "FAIL", 
                f"Exception during manual refresh: {str(e)}"
            )
    
    def test_background_refresh_trigger(self, artwork):
        """Test 6: Test background refresh trigger conditions"""
        from django.utils import timezone
        
        # Force cache to be near expiry to trigger background refresh
        near_expiry = timezone.now() + timedelta(minutes=25)  # Should trigger proactive refresh
        
        artwork._url_cache_expires = near_expiry
        artwork.save(update_fields=['_url_cache_expires'])
        
        try:
            # This should trigger background refresh
            url = artwork.get_simple_signed_url()
            
            self.log_result(
                f"Background Refresh Trigger - {artwork.title}", 
                "PASS", 
                f"Background refresh triggered, got URL: {url[:50] if url else 'None'}..."
            )
            
        except Exception as e:
            self.log_result(
                f"Background Refresh Trigger - {artwork.title}", 
                "FAIL", 
                f"Background refresh failed: {str(e)}"
            )
    
    def test_url_accessibility(self, artwork):
        """Test 7: Test if generated URLs are actually accessible"""
        try:
            import requests
            from requests.adapters import HTTPAdapter
            from urllib3.util.retry import Retry
            
            # Get URL
            url = artwork.get_simple_signed_url()
            if not url:
                self.log_result(
                    f"URL Accessibility - {artwork.title}", 
                    "FAIL", 
                    "No URL generated to test"
                )
                return
            
            # Configure requests with retry
            session = requests.Session()
            retry = Retry(total=2, backoff_factor=0.3)
            adapter = HTTPAdapter(max_retries=retry)
            session.mount('http://', adapter)
            session.mount('https://', adapter)
            
            # Test URL
            response = session.head(url, timeout=10)
            
            if response.status_code == 200:
                self.log_result(
                    f"URL Accessibility - {artwork.title}", 
                    "PASS", 
                    f"URL is accessible (status: {response.status_code})"
                )
            else:
                self.log_result(
                    f"URL Accessibility - {artwork.title}", 
                    "FAIL", 
                    f"URL returned status {response.status_code}: {url}"
                )
                
        except Exception as e:
            self.log_result(
                f"URL Accessibility - {artwork.title}", 
                "FAIL", 
                f"Error testing URL accessibility: {str(e)}"
            )
    
    def run_full_diagnostic(self):
        """Run all diagnostic tests"""
        print("=" * 60)
        print("STARTING IMAGE CACHE DIAGNOSTIC TESTS")
        print("=" * 60)
        
        # Test 1: Supabase connection
        if not self.test_supabase_connection():
            print("\n❌ Supabase connection failed - stopping tests")
            return self.results
        
        # Test 2: Find artworks to test
        artworks = self.test_artwork_with_supabase_urls()
        if not artworks:
            print("\n❌ No artworks available for testing")
            return self.results
        
        # Run tests on each artwork
        for artwork in artworks:
            print(f"\n🎨 Testing artwork: {artwork.title}")
            print("-" * 40)
            
            # Test 3: URL generation methods
            self.test_url_generation_methods(artwork)
            
            # Test 4: Cache state
            self.test_cache_state(artwork)
            
            # Test 5: Manual refresh
            self.test_manual_refresh(artwork)
            
            # Test 6: Background refresh trigger
            self.test_background_refresh_trigger(artwork)
            
            # Test 7: URL accessibility 
            self.test_url_accessibility(artwork)
        
        return self.results
    
    def generate_report(self):
        """Generate a summary report"""
        print("\n" + "=" * 60)
        print("DIAGNOSTIC RESULTS SUMMARY")
        print("=" * 60)
        
        pass_count = sum(1 for r in self.results if r['status'] == 'PASS')
        fail_count = sum(1 for r in self.results if r['status'] == 'FAIL')
        warn_count = sum(1 for r in self.results if r['status'] == 'WARN')
        
        print(f"✓ PASSED: {pass_count}")
        print(f"✗ FAILED: {fail_count}")
        print(f"⚠ WARNINGS: {warn_count}")
        print(f"📊 TOTAL TESTS: {len(self.results)}")
        
        if fail_count > 0:
            print(f"\n🔍 CRITICAL ISSUES FOUND:")
            for result in self.results:
                if result['status'] == 'FAIL':
                    print(f"  • {result['test']}: {result['message']}")
        
        if warn_count > 0:
            print(f"\n⚠️ WARNINGS:")
            for result in self.results:
                if result['status'] == 'WARN':
                    print(f"  • {result['test']}: {result['message']}")

if __name__ == "__main__":
    diagnostic = ImageCacheDiagnostic()
    results = diagnostic.run_full_diagnostic()
    diagnostic.generate_report()
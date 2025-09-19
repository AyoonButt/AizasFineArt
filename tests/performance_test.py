#!/usr/bin/env python3
"""
Performance Testing Script for Aiza's Fine Art Website
Tests loading times for all major pages
"""

import time
import requests
import json
import statistics
from urllib.parse import urljoin
from datetime import datetime
import subprocess
import sys

class PerformanceTest:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        self.session = requests.Session()
        self.results = {}
        
        # Test pages configuration
        self.test_pages = {
            'home': '/',
            'gallery': '/gallery/',
            'shop': '/shop/',
            'about': '/about/',
            'contact': '/contact/',
            'portfolio': '/portfolio/',
            'artwork_detail': '/art/wide-images-2025/',
        }
        
        # Performance thresholds (in seconds)
        self.thresholds = {
            'excellent': 0.5,
            'good': 1.0,
            'needs_improvement': 2.0,
            'poor': 5.0
        }
    
    def warm_up_server(self):
        """Warm up the server with a few requests"""
        print("🔥 Warming up server...")
        for _ in range(3):
            try:
                response = self.session.get(self.base_url, timeout=10)
                if response.status_code == 200:
                    print("✅ Server warm-up successful")
                    return True
            except Exception as e:
                print(f"⚠️  Warm-up attempt failed: {e}")
                time.sleep(1)
        return False
    
    def test_page_performance(self, page_name, url, iterations=5):
        """Test a single page performance multiple times"""
        print(f"\n📊 Testing {page_name}: {url}")
        
        times = []
        response_sizes = []
        status_codes = []
        
        for i in range(iterations):
            try:
                # Clear any cached responses
                self.session.cookies.clear()
                
                start_time = time.time()
                response = self.session.get(urljoin(self.base_url, url), timeout=30)
                end_time = time.time()
                
                load_time = end_time - start_time
                times.append(load_time)
                response_sizes.append(len(response.content))
                status_codes.append(response.status_code)
                
                print(f"  Run {i+1}: {load_time:.3f}s ({response.status_code}) - {len(response.content)} bytes")
                
                # Small delay between requests
                time.sleep(0.5)
                
            except Exception as e:
                print(f"  ❌ Run {i+1} failed: {e}")
                continue
        
        if not times:
            return None
        
        # Calculate statistics
        avg_time = statistics.mean(times)
        median_time = statistics.median(times)
        min_time = min(times)
        max_time = max(times)
        std_dev = statistics.stdev(times) if len(times) > 1 else 0
        
        # Determine performance grade
        if avg_time <= self.thresholds['excellent']:
            grade = 'EXCELLENT'
        elif avg_time <= self.thresholds['good']:
            grade = 'GOOD'
        elif avg_time <= self.thresholds['needs_improvement']:
            grade = 'NEEDS IMPROVEMENT'
        else:
            grade = 'POOR'
        
        return {
            'page': page_name,
            'url': url,
            'iterations': len(times),
            'avg_time': avg_time,
            'median_time': median_time,
            'min_time': min_time,
            'max_time': max_time,
            'std_deviation': std_dev,
            'avg_response_size': statistics.mean(response_sizes),
            'status_codes': status_codes,
            'grade': grade,
            'raw_times': times
        }
    
    def test_concurrent_requests(self, page_name, url, concurrent_users=5):
        """Test how page performs under concurrent load"""
        print(f"\n🚀 Testing concurrent load for {page_name} ({concurrent_users} users)")
        
        import threading
        import queue
        
        results_queue = queue.Queue()
        
        def make_request():
            try:
                start_time = time.time()
                response = requests.get(urljoin(self.base_url, url), timeout=30)
                end_time = time.time()
                results_queue.put({
                    'time': end_time - start_time,
                    'status': response.status_code,
                    'size': len(response.content)
                })
            except Exception as e:
                results_queue.put({'error': str(e)})
        
        # Start concurrent requests
        threads = []
        start_time = time.time()
        
        for i in range(concurrent_users):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        total_time = time.time() - start_time
        
        # Collect results
        concurrent_times = []
        errors = []
        
        while not results_queue.empty():
            result = results_queue.get()
            if 'error' in result:
                errors.append(result['error'])
            else:
                concurrent_times.append(result['time'])
        
        if concurrent_times:
            avg_concurrent_time = statistics.mean(concurrent_times)
            print(f"  Average response time: {avg_concurrent_time:.3f}s")
            print(f"  Total test time: {total_time:.3f}s")
            print(f"  Successful requests: {len(concurrent_times)}/{concurrent_users}")
            if errors:
                print(f"  Errors: {len(errors)}")
        
        return {
            'concurrent_users': concurrent_users,
            'avg_response_time': statistics.mean(concurrent_times) if concurrent_times else None,
            'total_time': total_time,
            'successful_requests': len(concurrent_times),
            'errors': len(errors)
        }
    
    def check_static_assets(self):
        """Check if static assets are loading properly"""
        print("\n📦 Checking static assets...")
        
        static_assets = [
            '/static/dist/css/main.css',
            '/static/src/css/design-system.css',
            '/static/src/js/loading-optimizer.js',
            '/static/src/js/lazy-loader.js',
            '/static/src/js/performance-monitor.js',
            '/static/sw.js'
        ]
        
        asset_results = {}
        
        for asset in static_assets:
            try:
                start_time = time.time()
                response = self.session.get(urljoin(self.base_url, asset), timeout=10)
                load_time = time.time() - start_time
                
                asset_results[asset] = {
                    'status': response.status_code,
                    'load_time': load_time,
                    'size': len(response.content),
                    'content_type': response.headers.get('content-type', 'unknown')
                }
                
                status_icon = "✅" if response.status_code == 200 else "❌"
                print(f"  {status_icon} {asset}: {load_time:.3f}s ({response.status_code})")
                
            except Exception as e:
                asset_results[asset] = {'error': str(e)}
                print(f"  ❌ {asset}: ERROR - {e}")
        
        return asset_results
    
    def run_all_tests(self):
        """Run comprehensive performance tests"""
        print("🚀 Starting Performance Tests for Aiza's Fine Art")
        print(f"Base URL: {self.base_url}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if not self.warm_up_server():
            print("❌ Server warm-up failed. Exiting.")
            return None
        
        # Test static assets first
        static_results = self.check_static_assets()
        
        # Test each page
        page_results = {}
        for page_name, url in self.test_pages.items():
            result = self.test_page_performance(page_name, url)
            if result:
                page_results[page_name] = result
                
                # Test concurrent load for main pages
                if page_name in ['home', 'gallery', 'shop']:
                    concurrent_result = self.test_concurrent_requests(page_name, url)
                    page_results[page_name]['concurrent_test'] = concurrent_result
        
        # Compile final results
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'base_url': self.base_url,
            'static_assets': static_results,
            'page_tests': page_results,
            'summary': self.generate_summary(page_results)
        }
        
        return self.results
    
    def generate_summary(self, page_results):
        """Generate performance summary"""
        if not page_results:
            return {}
        
        all_times = []
        grades = {}
        
        for page_name, result in page_results.items():
            all_times.append(result['avg_time'])
            grades[result['grade']] = grades.get(result['grade'], 0) + 1
        
        return {
            'total_pages_tested': len(page_results),
            'overall_avg_time': statistics.mean(all_times),
            'fastest_page': min(page_results.items(), key=lambda x: x[1]['avg_time']),
            'slowest_page': max(page_results.items(), key=lambda x: x[1]['avg_time']),
            'grade_distribution': grades
        }
    
    def print_results(self):
        """Print formatted test results"""
        if not self.results:
            print("No results to display")
            return
        
        print("\n" + "="*80)
        print("🎯 PERFORMANCE TEST RESULTS")
        print("="*80)
        
        # Summary
        summary = self.results['summary']
        print(f"\n📋 SUMMARY:")
        print(f"  • Total pages tested: {summary['total_pages_tested']}")
        print(f"  • Overall average load time: {summary['overall_avg_time']:.3f}s")
        print(f"  • Fastest page: {summary['fastest_page'][0]} ({summary['fastest_page'][1]['avg_time']:.3f}s)")
        print(f"  • Slowest page: {summary['slowest_page'][0]} ({summary['slowest_page'][1]['avg_time']:.3f}s)")
        
        print(f"\n📊 GRADE DISTRIBUTION:")
        for grade, count in summary['grade_distribution'].items():
            print(f"  • {grade}: {count} pages")
        
        # Detailed results
        print(f"\n📄 DETAILED RESULTS:")
        for page_name, result in self.results['page_tests'].items():
            grade_icon = {
                'EXCELLENT': '🟢',
                'GOOD': '🟡', 
                'NEEDS IMPROVEMENT': '🟠',
                'POOR': '🔴'
            }.get(result['grade'], '⚪')
            
            print(f"\n{grade_icon} {page_name.upper()} ({result['url']})")
            print(f"  Grade: {result['grade']}")
            print(f"  Average: {result['avg_time']:.3f}s")
            print(f"  Median: {result['median_time']:.3f}s")
            print(f"  Range: {result['min_time']:.3f}s - {result['max_time']:.3f}s")
            print(f"  Std Dev: {result['std_deviation']:.3f}s")
            print(f"  Avg Size: {result['avg_response_size']/1024:.1f}KB")
            
            if 'concurrent_test' in result:
                ct = result['concurrent_test']
                print(f"  Concurrent Test (5 users): {ct['avg_response_time']:.3f}s avg")
        
        # Static assets summary
        print(f"\n📦 STATIC ASSETS:")
        working_assets = sum(1 for asset in self.results['static_assets'].values() 
                           if isinstance(asset, dict) and asset.get('status') == 200)
        total_assets = len(self.results['static_assets'])
        print(f"  Working: {working_assets}/{total_assets}")
        
        # Performance recommendations
        self.print_recommendations()
    
    def print_recommendations(self):
        """Print performance recommendations"""
        print(f"\n💡 RECOMMENDATIONS:")
        
        page_results = self.results['page_tests']
        slow_pages = [name for name, result in page_results.items() 
                     if result['avg_time'] > self.thresholds['good']]
        
        if slow_pages:
            print(f"  🔧 Optimize these slow pages: {', '.join(slow_pages)}")
            print(f"     - Enable compression (gzip)")
            print(f"     - Optimize database queries")
            print(f"     - Implement page caching")
        
        # Check for failed static assets
        failed_assets = [asset for asset, result in self.results['static_assets'].items()
                        if isinstance(result, dict) and result.get('status') != 200]
        
        if failed_assets:
            print(f"  📦 Fix these static assets: {', '.join(failed_assets)}")
        
        # General recommendations
        avg_time = self.results['summary']['overall_avg_time']
        if avg_time > self.thresholds['good']:
            print(f"  ⚡ General optimizations needed:")
            print(f"     - Enable browser caching")
            print(f"     - Optimize images (WebP format)")
            print(f"     - Minify CSS/JS")
            print(f"     - Use CDN for static assets")
    
    def save_results(self, filename="performance_test_results.json"):
        """Save results to JSON file"""
        if self.results:
            with open(filename, 'w') as f:
                json.dump(self.results, f, indent=2)
            print(f"\n💾 Results saved to {filename}")

def main():
    # Check if server is running
    try:
        response = requests.get("http://localhost:8001/", timeout=5)
        if response.status_code != 200:
            print("❌ Server not responding properly")
            return
    except:
        print("❌ Server not running. Please start with: python3 manage.py runserver 8001")
        return
    
    # Run tests
    tester = PerformanceTest()
    tester.run_all_tests()
    tester.print_results()
    tester.save_results()

if __name__ == "__main__":
    main()
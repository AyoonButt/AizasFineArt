#!/usr/bin/env python3
"""
Database Performance Analysis for Aiza's Fine Art
Identifies slow database queries causing page load issues
"""

import os
import sys
import django
import time
from django.db import connection
from django.test.utils import override_settings
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aizasfineart.settings')
django.setup()

from artwork.models import Artwork
from blog.models import BlogPost
from django.core.paginator import Paginator

class DatabasePerformanceTest:
    def __init__(self):
        self.query_times = {}
    
    def reset_queries(self):
        """Reset Django query log"""
        connection.queries.clear()
    
    def get_query_stats(self):
        """Get current query statistics"""
        queries = connection.queries
        total_time = sum(float(q['time']) for q in queries)
        return {
            'count': len(queries),
            'total_time': total_time,
            'queries': queries
        }
    
    def test_gallery_queries(self):
        """Test queries used by gallery page"""
        print("📊 Testing Gallery Page Queries...")
        self.reset_queries()
        
        start_time = time.time()
        
        # Simulate gallery page query
        artworks = Artwork.objects.filter(
            type__in=['original', 'print']
        ).select_related().prefetch_related().order_by('-created_at')
        
        # Force evaluation (like template would do)
        artwork_list = list(artworks[:20])  # First page
        
        end_time = time.time()
        python_time = end_time - start_time
        
        stats = self.get_query_stats()
        
        print(f"  • Artworks fetched: {len(artwork_list)}")
        print(f"  • Database queries: {stats['count']}")
        print(f"  • Total DB time: {stats['total_time']:.4f}s")
        print(f"  • Python time: {python_time:.4f}s")
        
        if stats['queries']:
            print(f"  • Slowest query: {max(stats['queries'], key=lambda x: float(x['time']))['time']}s")
        
        # Print slow queries
        slow_queries = [q for q in stats['queries'] if float(q['time']) > 0.01]
        if slow_queries:
            print(f"  ⚠️  {len(slow_queries)} slow queries (>10ms):")
            for query in slow_queries[:3]:  # Show top 3
                print(f"    - {query['time']}s: {query['sql'][:100]}...")
        
        return stats
    
    def test_shop_queries(self):
        """Test queries used by shop page"""
        print("\n🛒 Testing Shop Page Queries...")
        self.reset_queries()
        
        start_time = time.time()
        
        # Simulate shop page query with filters
        artworks = Artwork.objects.filter(
            type__in=['original', 'print']
        ).select_related().prefetch_related().order_by('-created_at')
        
        # Paginate like shop does
        paginator = Paginator(artworks, 24)
        page_obj = paginator.get_page(1)
        artwork_list = list(page_obj.object_list)
        
        end_time = time.time()
        python_time = end_time - start_time
        
        stats = self.get_query_stats()
        
        print(f"  • Artworks fetched: {len(artwork_list)}")
        print(f"  • Total artworks: {paginator.count}")
        print(f"  • Database queries: {stats['count']}")
        print(f"  • Total DB time: {stats['total_time']:.4f}s")
        print(f"  • Python time: {python_time:.4f}s")
        
        # Print slow queries
        slow_queries = [q for q in stats['queries'] if float(q['time']) > 0.01]
        if slow_queries:
            print(f"  ⚠️  {len(slow_queries)} slow queries (>10ms):")
            for query in slow_queries[:3]:
                print(f"    - {query['time']}s: {query['sql'][:100]}...")
        
        return stats
    
    def test_portfolio_queries(self):
        """Test queries used by portfolio page"""
        print("\n🎨 Testing Portfolio Page Queries...")
        self.reset_queries()
        
        start_time = time.time()
        
        # Portfolio page typically shows all artworks in a grid
        artworks = Artwork.objects.all().select_related().prefetch_related()
        artwork_list = list(artworks)
        
        end_time = time.time()
        python_time = end_time - start_time
        
        stats = self.get_query_stats()
        
        print(f"  • Artworks fetched: {len(artwork_list)}")
        print(f"  • Database queries: {stats['count']}")
        print(f"  • Total DB time: {stats['total_time']:.4f}s")
        print(f"  • Python time: {python_time:.4f}s")
        
        slow_queries = [q for q in stats['queries'] if float(q['time']) > 0.01]
        if slow_queries:
            print(f"  ⚠️  {len(slow_queries)} slow queries (>10ms):")
            for query in slow_queries[:3]:
                print(f"    - {query['time']}s: {query['sql'][:100]}...")
        
        return stats
    
    def test_optimized_queries(self):
        """Test optimized versions of the queries"""
        print("\n⚡ Testing Optimized Queries...")
        
        # Test 1: Gallery with optimized query
        print("\n  🔧 Optimized Gallery Query:")
        self.reset_queries()
        start_time = time.time()
        
        # Only select needed fields, add proper indexes
        artworks = Artwork.objects.only(
            'id', 'title', 'main_image_url', 'medium', 'created_at',
            'original_available', 'type', 'is_featured'
        ).filter(
            type__in=['original', 'print']
        ).order_by('-created_at')[:20]
        
        artwork_list = list(artworks)
        end_time = time.time()
        
        stats = self.get_query_stats()
        print(f"    • DB time: {stats['total_time']:.4f}s")
        print(f"    • Python time: {end_time - start_time:.4f}s")
        print(f"    • Queries: {stats['count']}")
        
        # Test 2: Shop with optimized query
        print("\n  🔧 Optimized Shop Query:")
        self.reset_queries()
        start_time = time.time()
        
        artworks = Artwork.objects.only(
            'id', 'title', 'main_image_url', 'medium', 'original_price',
            'original_available', 'type'
        ).filter(
            type__in=['original', 'print']
        )
        
        # Use database-level pagination
        paginator = Paginator(artworks, 24)
        page_obj = paginator.get_page(1)
        artwork_list = list(page_obj.object_list)
        end_time = time.time()
        
        stats = self.get_query_stats()
        print(f"    • DB time: {stats['total_time']:.4f}s")
        print(f"    • Python time: {end_time - start_time:.4f}s")
        print(f"    • Queries: {stats['count']}")
    
    def check_database_indexes(self):
        """Check if proper database indexes exist"""
        print("\n📋 Checking Database Indexes...")
        
        with connection.cursor() as cursor:
            # Check indexes on artwork table (SQLite syntax)
            cursor.execute("""
                SELECT name, sql 
                FROM sqlite_master 
                WHERE type='index' AND tbl_name='artwork_artwork'
            """)
            
            indexes = cursor.fetchall()
            print(f"  • Found {len(indexes)} indexes on artwork table:")
            
            essential_indexes = {
                'created_at': False,
                'type': False,
                'medium': False,
                'original_available': False,
                'is_featured': False
            }
            
            for index_name, index_def in indexes:
                if index_def:  # Skip auto-indexes without SQL
                    print(f"    - {index_name}")
                    for field in essential_indexes:
                        if field in index_def:
                            essential_indexes[field] = True
            
            print("\n  📊 Essential Index Status:")
            for field, exists in essential_indexes.items():
                status = "✅" if exists else "❌"
                print(f"    {status} {field}")
            
            missing_indexes = [field for field, exists in essential_indexes.items() if not exists]
            if missing_indexes:
                print(f"\n  ⚠️  Missing indexes for: {', '.join(missing_indexes)}")
                self.suggest_index_creation(missing_indexes)
    
    def suggest_index_creation(self, missing_indexes):
        """Suggest database index creation commands"""
        print("\n💡 Suggested Index Creation:")
        
        table_name = "artwork_artwork"
        for field in missing_indexes:
            print(f"  CREATE INDEX idx_{table_name}_{field} ON {table_name}({field});")
    
    def analyze_artwork_count(self):
        """Analyze artwork count and data distribution"""
        print("\n📈 Artwork Data Analysis:")
        
        total_artworks = Artwork.objects.count()
        original_count = Artwork.objects.filter(type='original').count()
        print_count = Artwork.objects.filter(type='print').count()
        gallery_count = Artwork.objects.filter(type='gallery').count()
        
        print(f"  • Total artworks: {total_artworks}")
        print(f"  • Originals: {original_count}")
        print(f"  • Prints: {print_count}")
        print(f"  • Gallery: {gallery_count}")
        
        # Check for artworks without images (using main_image_url field)
        no_image = Artwork.objects.filter(main_image_url__isnull=True).count()
        placeholder_image = Artwork.objects.filter(main_image_url__contains='placeholder').count()
        print(f"  • Without images: {no_image}")
        print(f"  • With placeholder images: {placeholder_image}")
        
        # Performance impact analysis
        if total_artworks > 1000:
            print("  ⚠️  Large dataset detected - pagination essential")
        if no_image > 0:
            print("  ⚠️  Missing images may cause template issues")
    
    def run_full_analysis(self):
        """Run complete database performance analysis"""
        print("🔍 Database Performance Analysis")
        print("=" * 50)
        
        self.analyze_artwork_count()
        self.check_database_indexes()
        
        gallery_stats = self.test_gallery_queries()
        shop_stats = self.test_shop_queries()
        portfolio_stats = self.test_portfolio_queries()
        
        self.test_optimized_queries()
        
        print("\n" + "=" * 50)
        print("📊 SUMMARY:")
        print(f"  • Gallery: {gallery_stats['total_time']:.4f}s ({gallery_stats['count']} queries)")
        print(f"  • Shop: {shop_stats['total_time']:.4f}s ({shop_stats['count']} queries)")
        print(f"  • Portfolio: {portfolio_stats['total_time']:.4f}s ({portfolio_stats['count']} queries)")
        
        total_db_time = gallery_stats['total_time'] + shop_stats['total_time'] + portfolio_stats['total_time']
        if total_db_time > 0.1:
            print(f"\n⚠️  High database load detected: {total_db_time:.4f}s total")
            print("   Recommendations:")
            print("   - Add database indexes")
            print("   - Optimize queries with select_related()")
            print("   - Implement query result caching")
            print("   - Use database connection pooling")

if __name__ == "__main__":
    # Enable query logging for debugging (SQLite doesn't support init_command)
    from django.conf import settings
    settings.DEBUG = True  # Enable query logging
    
    # Run analysis
    analyzer = DatabasePerformanceTest()
    analyzer.run_full_analysis()
"""
Management command to create sample artwork data for testing
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from artwork.models import Artwork, Category, Series, Tag


class Command(BaseCommand):
    help = 'Create sample artwork data for testing the admin interface'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=5,
            help='Number of sample artworks to create'
        )
    
    def handle(self, *args, **options):
        count = options['count']
        
        self.stdout.write('Creating sample artwork data...')
        
        # Create categories if they don't exist
        categories_data = [
            {'name': 'Landscapes', 'description': 'Natural landscapes and scenery'},
            {'name': 'Portraits', 'description': 'People and character studies'},
            {'name': 'Still Life', 'description': 'Objects and compositions'},
            {'name': 'Abstract', 'description': 'Non-representational art'},
        ]
        
        categories = []
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            categories.append(category)
            if created:
                self.stdout.write(f'Created category: {category.name}')
        
        # Create series for categories
        series_data = [
            {'name': 'Mountain Views', 'category': categories[0]},
            {'name': 'Ocean Scenes', 'category': categories[0]},
            {'name': 'Character Studies', 'category': categories[1]},
            {'name': 'Family Portraits', 'category': categories[1]},
        ]
        
        series_list = []
        for series_data in series_data:
            series, created = Series.objects.get_or_create(
                name=series_data['name'],
                category=series_data['category'],
                defaults={'description': f"Series of {series_data['name'].lower()}"}
            )
            series_list.append(series)
            if created:
                self.stdout.write(f'Created series: {series.name}')
        
        # Create tags (handle existing tags gracefully)
        tag_names = ['watercolor', 'oil', 'nature', 'portrait', 'peaceful', 'vibrant', 'detailed', 'minimalist']
        tags = []
        for tag_name in tag_names:
            try:
                tag, created = Tag.objects.get_or_create(
                    name=tag_name,
                    defaults={'color': '#6B7280'}
                )
                tags.append(tag)
                if created:
                    self.stdout.write(f'Created tag: {tag.name}')
            except Exception as e:
                # If tag creation fails, try to get existing tag
                try:
                    tag = Tag.objects.get(name=tag_name)
                    tags.append(tag)
                    self.stdout.write(f'Using existing tag: {tag.name}')
                except Tag.DoesNotExist:
                    self.stdout.write(f'Failed to create or find tag: {tag_name} - {e}')
        
        # Sample artwork data
        sample_artworks = [
            {
                'title': 'Sunset Over Mountains',
                'category': categories[0],
                'series': series_list[0],
                'medium': 'watercolor',
                'description': 'A breathtaking watercolor painting of a sunset over mountain peaks.',
                'inspiration': 'Inspired by a hiking trip to the Rocky Mountains.',
                'technique_notes': 'Used wet-on-wet technique for soft cloud effects.',
                'dimensions_width': 16.0,
                'dimensions_height': 12.0,
                'year_created': 2023,
                'original_price': 450.00,
                'story': 'This piece captures the magical moment when the sun sets behind the peaks.',
            },
            {
                'title': 'Ocean Waves at Dawn',
                'category': categories[0],
                'series': series_list[1],
                'medium': 'oil',
                'description': 'Dynamic oil painting of ocean waves crashing at dawn.',
                'inspiration': 'Early morning walks on the California coast.',
                'technique_notes': 'Built up texture with palette knife work.',
                'dimensions_width': 20.0,
                'dimensions_height': 16.0,
                'year_created': 2023,
                'original_price': 750.00,
                'story': 'The power and beauty of the ocean has always fascinated me.',
            },
            {
                'title': 'Portrait of Grace',
                'category': categories[1],
                'series': series_list[2],
                'medium': 'oil',
                'description': 'Intimate portrait study focusing on expression and light.',
                'inspiration': 'The quiet strength I see in everyday people.',
                'technique_notes': 'Careful attention to skin tones and lighting.',
                'dimensions_width': 12.0,
                'dimensions_height': 16.0,
                'year_created': 2022,
                'original_price': 650.00,
                'story': 'This portrait represents the dignity found in ordinary moments.',
            },
            {
                'title': 'Flowers in Blue Vase',
                'category': categories[2],
                'series': None,
                'medium': 'watercolor',
                'description': 'Delicate still life of spring flowers in a ceramic vase.',
                'inspiration': 'The fleeting beauty of spring blooms.',
                'technique_notes': 'Layered transparent washes for luminosity.',
                'dimensions_width': 14.0,
                'dimensions_height': 18.0,
                'year_created': 2023,
                'original_price': 380.00,
                'story': 'Painted from flowers in my garden during peak spring.',
            },
            {
                'title': 'Abstract Flow',
                'category': categories[3],
                'series': None,
                'medium': 'mixed',
                'description': 'Abstract composition exploring color and movement.',
                'inspiration': 'The rhythm of music translated to visual form.',
                'technique_notes': 'Combined watercolor and acrylic techniques.',
                'dimensions_width': 18.0,
                'dimensions_height': 24.0,
                'year_created': 2023,
                'original_price': 520.00,
                'story': 'This piece emerged from a meditation on color and sound.',
            },
        ]
        
        # Create artworks
        created_count = 0
        for i in range(min(count, len(sample_artworks))):
            artwork_data = sample_artworks[i]
            
            # Check if artwork already exists
            if not Artwork.objects.filter(title=artwork_data['title']).exists():
                artwork = Artwork.objects.create(**artwork_data)
                
                # Add some tags
                if i < len(tags) - 2:
                    artwork.tags.add(tags[i], tags[i+1])
                
                created_count += 1
                self.stdout.write(f'Created artwork: {artwork.title}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} sample artworks!')
        )
        
        if created_count > 0:
            self.stdout.write('You can now test the admin interface at /admin/artwork/artwork/')
        else:
            self.stdout.write('Sample artworks already exist. Use --count to create more.')
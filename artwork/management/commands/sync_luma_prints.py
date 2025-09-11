from django.core.management.base import BaseCommand
from django.utils import timezone
from artwork.models import Artwork
from orders.luma_prints_api import create_luma_prints_product, update_luma_prints_product


class Command(BaseCommand):
    help = 'Sync print artworks with LumaPrints catalog - create/update products'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-missing',
            action='store_true',
            help='Create LumaPrints products for print artworks that don\'t have product IDs',
        )
        parser.add_argument(
            '--update-existing',
            action='store_true',
            help='Update existing LumaPrints products with latest artwork data',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update all print artworks regardless of current state',
        )
        parser.add_argument(
            '--artwork-id',
            type=int,
            help='Process only specific artwork by ID',
        )
        parser.add_argument(
            '--cleanup-orphaned',
            action='store_true',
            help='Remove LumaPrints product IDs from non-print artworks',
        )

    def handle(self, *args, **options):
        self.stdout.write("Syncing print artworks with LumaPrints catalog...")
        
        # Handle cleanup of orphaned LumaPrints IDs first
        if options['cleanup_orphaned']:
            self._cleanup_orphaned_ids()
        
        # Get print artworks to process
        if options['artwork_id']:
            artworks = Artwork.objects.filter(id=options['artwork_id'], type='print', is_active=True)
            if not artworks.exists():
                self.stdout.write(
                    self.style.ERROR(f'No active print artwork found with ID {options["artwork_id"]}')
                )
                return
        else:
            artworks = Artwork.objects.filter(type='print', is_active=True).order_by('-created_at')
        
        total_count = artworks.count()
        created_count = 0
        updated_count = 0
        error_count = 0
        
        self.stdout.write(f"Found {total_count} print artworks to process")
        
        for artwork in artworks:
            try:
                has_luma_id = bool(artwork.lumaprints_product_id)
                should_create = (not has_luma_id and options['create_missing']) or options['force']
                should_update = (has_luma_id and options['update_existing']) or options['force']
                
                if should_create and not has_luma_id:
                    # Create new product
                    result = self._create_product(artwork)
                    if result['status'] == 'success':
                        created_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'✓ Created product for "{artwork.title}" - ID: {result.get("product_id")}'
                            )
                        )
                    else:
                        error_count += 1
                        self.stdout.write(
                            self.style.ERROR(
                                f'✗ Failed to create product for "{artwork.title}": {result.get("message")}'
                            )
                        )
                
                elif should_update and has_luma_id:
                    # Update existing product
                    result = self._update_product(artwork)
                    if result['status'] == 'success':
                        updated_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'✓ Updated product for "{artwork.title}" - ID: {result.get("product_id")}'
                            )
                        )
                    else:
                        error_count += 1
                        self.stdout.write(
                            self.style.ERROR(
                                f'✗ Failed to update product for "{artwork.title}": {result.get("message")}'
                            )
                        )
                
                else:
                    # Skip - no action needed
                    action = "has product ID" if has_luma_id else "missing product ID"
                    self.stdout.write(f'- Skipped "{artwork.title}" ({action})')
                    
            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f'✗ Unexpected error for "{artwork.title}": {str(e)}')
                )
        
        # Summary
        self.stdout.write("\n" + "="*50)
        self.stdout.write(f"Sync completed:")
        self.stdout.write(f"  Total artworks processed: {total_count}")
        self.stdout.write(self.style.SUCCESS(f"  Products created: {created_count}"))
        self.stdout.write(self.style.SUCCESS(f"  Products updated: {updated_count}"))
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f"  Errors: {error_count}"))
        else:
            self.stdout.write("  No errors")
    
    def _create_product(self, artwork):
        """Create LumaPrints product for artwork"""
        try:
            # Ensure we have a valid image URL
            if not artwork.main_image_url:
                return {'status': 'error', 'message': 'No main image URL found'}
            
            # Get signed URL for the image
            image_url = artwork.get_simple_signed_url()
            if not image_url:
                return {'status': 'error', 'message': 'Failed to generate signed image URL'}
            
            # Create product
            return create_luma_prints_product(artwork, image_url)
            
        except Exception as e:
            return {'status': 'error', 'message': f'Unexpected error: {str(e)}'}
    
    def _update_product(self, artwork):
        """Update LumaPrints product for artwork"""
        try:
            # Ensure we have a valid image URL
            if not artwork.main_image_url:
                return {'status': 'error', 'message': 'No main image URL found'}
            
            # Get signed URL for the image
            image_url = artwork.get_simple_signed_url()
            if not image_url:
                return {'status': 'error', 'message': 'Failed to generate signed image URL'}
            
            # Update product
            return update_luma_prints_product(artwork, image_url)
            
        except Exception as e:
            return {'status': 'error', 'message': f'Unexpected error: {str(e)}'}
    
    def _cleanup_orphaned_ids(self):
        """Clean up LumaPrints product IDs from non-print artworks"""
        self.stdout.write("Cleaning up orphaned LumaPrints product IDs...")
        
        # Find non-print artworks that still have LumaPrints product IDs
        orphaned_artworks = Artwork.objects.filter(
            lumaprints_product_id__isnull=False
        ).exclude(
            lumaprints_product_id=''
        ).exclude(
            type='print'
        )
        
        orphaned_count = orphaned_artworks.count()
        
        if orphaned_count == 0:
            self.stdout.write("No orphaned LumaPrints product IDs found")
            return
        
        self.stdout.write(f"Found {orphaned_count} artworks with orphaned LumaPrints product IDs")
        
        for artwork in orphaned_artworks:
            try:
                # Try to delete the product from LumaPrints first
                from orders.luma_prints_api import delete_luma_prints_product
                result = delete_luma_prints_product(artwork)
                
                # Clear the product ID regardless of delete result
                old_product_id = artwork.lumaprints_product_id
                artwork.lumaprints_product_id = ''
                artwork.save(update_fields=['lumaprints_product_id'])
                
                if result['status'] == 'success':
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Cleaned up "{artwork.title}" (ID: {old_product_id})')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'⚠ Cleared ID for "{artwork.title}" but LumaPrints delete failed: {result.get("message")}')
                    )
                    
            except Exception as e:
                # Clear the ID even if delete fails
                artwork.lumaprints_product_id = ''
                artwork.save(update_fields=['lumaprints_product_id'])
                self.stdout.write(
                    self.style.WARNING(f'⚠ Cleared ID for "{artwork.title}" but error occurred: {str(e)}')
                )
        
        self.stdout.write(f"Cleanup complete: {orphaned_count} orphaned IDs processed\n")
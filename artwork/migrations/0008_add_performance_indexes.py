# Generated for performance optimization

from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('artwork', '0007_auto_20250815_1937'),
    ]

    operations = [
        # Add indexes for frequently queried fields
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_artwork_artwork_created_at ON artwork_artwork(created_at);",
            reverse_sql="DROP INDEX IF EXISTS idx_artwork_artwork_created_at;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_artwork_artwork_type ON artwork_artwork(type);",
            reverse_sql="DROP INDEX IF EXISTS idx_artwork_artwork_type;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_artwork_artwork_medium ON artwork_artwork(medium);",
            reverse_sql="DROP INDEX IF EXISTS idx_artwork_artwork_medium;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_artwork_artwork_original_available ON artwork_artwork(original_available);",
            reverse_sql="DROP INDEX IF EXISTS idx_artwork_artwork_original_available;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_artwork_artwork_is_featured ON artwork_artwork(is_featured);",
            reverse_sql="DROP INDEX IF EXISTS idx_artwork_artwork_is_featured;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_artwork_artwork_is_active ON artwork_artwork(is_active);",
            reverse_sql="DROP INDEX IF EXISTS idx_artwork_artwork_is_active;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_artwork_artwork_display_order ON artwork_artwork(display_order);",
            reverse_sql="DROP INDEX IF EXISTS idx_artwork_artwork_display_order;"
        ),
        # Composite index for common filtering patterns
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_artwork_type_active ON artwork_artwork(type, is_active);",
            reverse_sql="DROP INDEX IF EXISTS idx_artwork_type_active;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_artwork_featured_active ON artwork_artwork(is_featured, is_active);",
            reverse_sql="DROP INDEX IF EXISTS idx_artwork_featured_active;"
        ),
    ]
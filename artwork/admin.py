from django.contrib import admin
from django.contrib import messages
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Artwork, Category, Series, Tag, PrintOption, ArtworkView, ArtworkInquiry
from .forms import ArtworkForm


class PrintOptionInline(admin.TabularInline):
    """Inline editing for print options"""
    model = PrintOption
    extra = 1
    fields = ('size', 'material', 'price', 'is_available', 'display_order', 'description')
    ordering = ['display_order', 'price']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Admin interface for Tags"""
    list_display = ['name', 'slug', 'color_preview', 'is_active', 'artwork_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active']
    
    def color_preview(self, obj):
        return format_html(
            '<div style="width: 20px; height: 20px; background-color: {}; border: 1px solid #ccc; border-radius: 3px;"></div>',
            obj.color
        )
    color_preview.short_description = 'Color'
    
    def artwork_count(self, obj):
        return obj.artworks.count()
    artwork_count.short_description = 'Artworks'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin interface for Categories"""
    list_display = ['name', 'slug', 'is_active', 'display_order', 'artwork_count', 'series_count']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active', 'display_order']
    ordering = ['display_order', 'name']
    
    def artwork_count(self, obj):
        return obj.artworks.count()
    artwork_count.short_description = 'Artworks'
    
    def series_count(self, obj):
        return obj.series.count()
    series_count.short_description = 'Series'


@admin.register(Series)
class SeriesAdmin(admin.ModelAdmin):
    """Admin interface for Series"""
    list_display = ['name', 'category', 'slug', 'is_active', 'display_order', 'artwork_count']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'category__name']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active', 'display_order']
    ordering = ['category__name', 'display_order', 'name']
    
    def artwork_count(self, obj):
        return obj.artworks.count()
    artwork_count.short_description = 'Artworks'


@admin.register(Artwork)
class ArtworkAdmin(admin.ModelAdmin):
    """Comprehensive admin interface for Artworks"""
    form = ArtworkForm
    inlines = [PrintOptionInline]
    
    class Media:
        css = {
            'all': ('admin/css/artwork-admin.css',)
        }
        js = ('admin/js/artwork-admin.js',)
    
    def get_form(self, request, obj=None, **kwargs):
        """Override form to ensure image fields are never required"""
        form = super().get_form(request, obj, **kwargs)
        
        # Ensure all image file fields are marked as not required
        image_fields = ['main_image_file', 'frame1_image_file', 'frame2_image_file', 'frame3_image_file', 'frame4_image_file']
        for field_name in image_fields:
            if field_name in form.base_fields:
                form.base_fields[field_name].required = False
                form.base_fields[field_name].widget.attrs.update({
                    'required': False,
                    'data-required': 'false',
                    'class': 'form-file-input',
                    'accept': '.jpg,.jpeg,.png,.webp'
                })
        
        return form
    
    list_display = [
        'image_preview', 'title', 'category', 'series', 'medium', 
        'type', 'price_display', 'is_featured', 'is_active', 'views', 'created_at'
    ]
    list_display_links = ['image_preview', 'title']
    list_filter = [
        'category', 'series', 'medium', 'type', 'is_featured', 
        'is_active', 'year_created'
    ]
    search_fields = ['title', 'description', 'tags__name', 'category__name', 'series__name']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['type', 'is_featured', 'is_active']
    ordering = ['-is_featured', 'display_order', '-created_at']
    
    filter_horizontal = ['tags']
    
    readonly_fields = ['slug', 'views', 'favorites', 'created_at', 'updated_at', 'image_previews']
    
    # Remove old availability-based actions since we now use type field
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                ('title', 'slug'),
                ('category', 'series'),
                ('medium', 'year_created'),
                ('dimensions_width', 'dimensions_height'),
                'display_order',
            )
        }),
        ('Content', {
            'fields': (
                'description',
                'inspiration', 
                'technique_notes',
                'story',
            )
        }),
        ('Pricing & Type', {
            'fields': (
                ('type', 'original_price'),
                'edition_info',
            )
        }),
        ('Images', {
            'fields': (
                'image_previews',
                'main_image_file',
                'frame1_image_file',
                'frame2_image_file', 
                'frame3_image_file',
                'frame4_image_file',
            ),
            'description': 'Upload new images to update the artwork gallery. Current images are shown above.'
        }),
        ('SEO & Metadata', {
            'fields': (
                'meta_description',
                'alt_text',
                'lumaprints_product_id',
            ),
            'classes': ('collapse',)
        }),
        ('Organization', {
            'fields': (
                'tags',
                ('is_featured', 'is_active'),
            )
        }),
        ('Statistics', {
            'fields': (
                ('views', 'favorites'),
                ('created_at', 'updated_at'),
            ),
            'classes': ('collapse',)
        })
    )
    
    def image_preview(self, obj):
        """Small image preview for list view"""
        if obj.main_image_url:
            try:
                thumb_url = obj.get_image('thumbnail')
                return format_html(
                    '<img src="{}" alt="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />',
                    thumb_url, obj.alt_text or obj.title
                )
            except:
                return format_html('<div style="width: 50px; height: 50px; background: #f3f4f6; border-radius: 4px; display: flex; align-items: center; justify-content: center; font-size: 10px;">No Image</div>')
        return format_html('<div style="width: 50px; height: 50px; background: #f3f4f6; border-radius: 4px; display: flex; align-items: center; justify-content: center; font-size: 10px;">No Image</div>')
    
    image_preview.short_description = 'Preview'
    
    def image_previews(self, obj):
        """Show all current images in the form"""
        if not obj.pk:
            return "Save the artwork first to see image previews."
        
        html = '<div style="display: flex; flex-wrap: wrap; gap: 10px; margin: 10px 0;">'
        
        # Main image
        try:
            main_url = obj.get_image('medium')
            if main_url:
                html += f'''
                <div style="text-align: center;">
                    <img src="{main_url}" alt="Main Image" style="width: 150px; height: 150px; object-fit: cover; border: 2px solid #e5e7eb; border-radius: 8px;" />
                    <div style="margin-top: 5px; font-size: 12px; color: #6b7280;">Main Image</div>
                </div>
                '''
        except:
            html += '''
            <div style="text-align: center;">
                <div style="width: 150px; height: 150px; background: #f3f4f6; border: 2px solid #e5e7eb; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: #9ca3af;">No Main Image</div>
                <div style="margin-top: 5px; font-size: 12px; color: #6b7280;">Main Image</div>
            </div>
            '''
        
        # Frame images
        for i in range(1, 5):
            try:
                frame_url = obj.get_frame_image(i, 'medium')
                if frame_url:
                    html += f'''
                    <div style="text-align: center;">
                        <img src="{frame_url}" alt="Frame {i}" style="width: 150px; height: 150px; object-fit: cover; border: 2px solid #e5e7eb; border-radius: 8px;" />
                        <div style="margin-top: 5px; font-size: 12px; color: #6b7280;">Frame {i}</div>
                    </div>
                    '''
                else:
                    html += f'''
                    <div style="text-align: center;">
                        <div style="width: 150px; height: 150px; background: #f9fafb; border: 2px dashed #d1d5db; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: #9ca3af;">No Frame {i}</div>
                        <div style="margin-top: 5px; font-size: 12px; color: #6b7280;">Frame {i}</div>
                    </div>
                    '''
            except:
                html += f'''
                <div style="text-align: center;">
                    <div style="width: 150px; height: 150px; background: #f9fafb; border: 2px dashed #d1d5db; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: #9ca3af;">No Frame {i}</div>
                    <div style="margin-top: 5px; font-size: 12px; color: #6b7280;">Frame {i}</div>
                </div>
                '''
        
        html += '</div>'
        return mark_safe(html)
    
    image_previews.short_description = 'Current Images'
    
    def price_display(self, obj):
        if obj.original_price:
            return f"${obj.original_price:,.0f}"
        return "Price on request"
    price_display.short_description = 'Price'
    
    def save_model(self, request, obj, form, change):
        """Handle all form field updates and image uploads"""
        from .services import artwork_image_service
        
        # FIRST: Save all the regular form fields using the form's save method
        # This ensures all field updates (title, description, tags, etc.) are preserved
        if hasattr(form, 'save'):
            # Let the form handle its own save logic which includes all field updates
            obj = form.save(commit=False)
        
        # SECOND: Process image uploads and update image URLs
        image_fields = [
            ('main_image_file', 'main_image_url'),
            ('frame1_image_file', 'frame1_image_url'),
            ('frame2_image_file', 'frame2_image_url'),
            ('frame3_image_file', 'frame3_image_url'),
            ('frame4_image_file', 'frame4_image_url'),
        ]
        
        for field_name, url_field in image_fields:
            uploaded_file = form.cleaned_data.get(field_name)
            if uploaded_file:
                try:
                    # Process and upload image
                    image_url = artwork_image_service.process_image_upload(
                        obj, field_name, uploaded_file
                    )
                    
                    if image_url:
                        setattr(obj, url_field, image_url)
                        messages.success(
                            request, 
                            f"Successfully uploaded {field_name.replace('_file', '').replace('_', ' ')}"
                        )
                    else:
                        messages.warning(
                            request,
                            f"Failed to upload {field_name.replace('_file', '').replace('_', ' ')}"
                        )
                        
                except Exception as e:
                    messages.error(
                        request,
                        f"Error uploading {field_name.replace('_file', '').replace('_', ' ')}: {str(e)}"
                    )
        
        # THIRD: Save the model with all updates (regular fields + image URLs)
        obj.save()
        
        # FOURTH: Handle many-to-many relationships (like tags)
        if hasattr(form, 'save_m2m'):
            form.save_m2m()
        
        # Log the update for debugging
        if change:
            print(f"Updated artwork: {obj.title} - Form fields saved and images processed")
        else:
            print(f"Created artwork: {obj.title} - All fields saved and images processed")


@admin.register(ArtworkView)
class ArtworkViewAdmin(admin.ModelAdmin):
    """Admin interface for Artwork Views (Analytics)"""
    list_display = ['artwork', 'ip_address', 'timestamp', 'referrer_display']
    list_filter = ['timestamp', 'artwork__category']
    search_fields = ['artwork__title', 'ip_address', 'referrer']
    readonly_fields = ['artwork', 'ip_address', 'user_agent', 'referrer', 'timestamp']
    ordering = ['-timestamp']
    
    def has_add_permission(self, request):
        return False  # Views are created automatically
    
    def referrer_display(self, obj):
        if obj.referrer:
            return obj.referrer[:50] + "..." if len(obj.referrer) > 50 else obj.referrer
        return "Direct"
    referrer_display.short_description = 'Referrer'


@admin.register(ArtworkInquiry)
class ArtworkInquiryAdmin(admin.ModelAdmin):
    """Admin interface for Artwork Inquiries"""
    list_display = ['artwork', 'name', 'email', 'inquiry_type', 'is_responded', 'created_at']
    list_filter = ['inquiry_type', 'is_responded', 'created_at', 'artwork__category']
    search_fields = ['artwork__title', 'name', 'email', 'message']
    readonly_fields = ['artwork', 'name', 'email', 'phone', 'message', 'inquiry_type', 'created_at']
    
    fieldsets = (
        ('Inquiry Details', {
            'fields': (
                'artwork',
                ('name', 'email'),
                'phone',
                'inquiry_type',
                'message',
                'created_at',
            )
        }),
        ('Response', {
            'fields': (
                'is_responded',
                'responded_at',
                'response_notes',
            )
        })
    )
    
    def save_model(self, request, obj, form, change):
        """Auto-set responded_at when marking as responded"""
        if obj.is_responded and not obj.responded_at:
            from django.utils import timezone
            obj.responded_at = timezone.now()
        super().save_model(request, obj, form, change)

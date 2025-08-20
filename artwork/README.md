# Artwork Admin Interface

The artwork admin interface has been completely updated to provide a comprehensive and user-friendly experience for managing artwork data.

## Features

### 🎨 **Comprehensive Artwork Management**
- **Complete artwork details**: Title, category, series, medium, dimensions, year
- **Rich content fields**: Description, inspiration, technique notes, personal story
- **Pricing & availability**: Original pricing, print availability, status tracking
- **SEO optimization**: Meta descriptions, alt text, structured data

### 🖼️ **Advanced Image Management**
- **5-image system**: Main image + 4 frame variants
- **Visual previews**: See all current images in the admin
- **Upload validation**: File type, size, and format validation
- **Image processing**: Automatic optimization and resizing
- **Supabase integration**: Ready for cloud storage

### 🏷️ **Organization Tools**
- **Categories & Series**: Hierarchical organization
- **Dynamic filtering**: Series automatically filters by category
- **Tag system**: Flexible tagging with color coding
- **Featured content**: Mark artworks as featured
- **Display ordering**: Custom sort order

### 💰 **Print Options Management**
- **Inline editing**: Manage print options directly in artwork form
- **Multiple sizes**: 8x10, 11x14, 16x20, 24x30 standard sizes
- **Material options**: Fine art paper, canvas, etc.
- **Pricing per option**: Individual pricing for each print variant
- **Availability tracking**: Enable/disable specific print options

### 📊 **Analytics & Insights**
- **View tracking**: Monitor artwork page views
- **Inquiry management**: Handle customer inquiries
- **Performance metrics**: Views, favorites, engagement

## Admin Interface Structure

### **Artwork List View**
- **Image previews**: Thumbnail preview of each artwork
- **Key information**: Title, category, series, medium, status, price
- **Quick editing**: Edit status, featured flag, and active status inline
- **Advanced filtering**: Filter by category, series, medium, status, year
- **Search functionality**: Search titles, descriptions, tags, categories

### **Artwork Edit Form**

#### **Basic Information Section**
- Title (auto-generates slug)
- Category and Series (dynamic filtering)
- Medium, Year Created
- Dimensions (width × height in inches)
- Status and Display Order

#### **Content Section**
- Description (main artwork description)
- Inspiration (what inspired the piece)
- Technique Notes (technical creation details)
- Story (personal story behind the artwork)

#### **Pricing & Availability Section**
- Original Available (checkbox)
- Original Price (required if available)
- Prints Available (checkbox)
- Edition Info (limited edition details)

#### **Images Section**
- **Current Images Preview**: Visual grid showing all 5 images
- **Upload Fields**: Separate upload for main + 4 frame images
- **Format Support**: JPG, PNG, WebP up to 10MB each
- **Auto-processing**: Automatic optimization and validation

#### **SEO & Metadata Section** (Collapsible)
- Meta Description (160 character limit)
- Alt Text (auto-generated if empty)
- Luma Prints Product ID

#### **Organization Section**
- Tags (checkbox grid with color coding)
- Featured Flag
- Active Status

#### **Statistics Section** (Collapsible, Read-only)
- View count
- Favorites count
- Created/Updated timestamps

### **Print Options (Inline)**
- Size (8x10, 11x14, etc.)
- Material (Fine Art Paper, Canvas, etc.)
- Price per print
- Availability toggle
- Display order
- Description

## How to Use

### **Creating New Artwork**

1. **Navigate to Admin**: Go to `/admin/artwork/artwork/`
2. **Click "Add Artwork"**
3. **Fill Basic Information**:
   - Enter title (slug auto-generates)
   - Select category (series will filter automatically)
   - Choose medium and enter year
   - Add dimensions in inches

4. **Add Content**:
   - Write compelling description
   - Share inspiration story
   - Include technique notes
   - Add personal story

5. **Set Pricing**:
   - Check "Original Available" if selling original
   - Enter price (required if available)
   - Check "Prints Available" if offering prints

6. **Upload Images**:
   - Upload main artwork image
   - Add up to 4 frame variants
   - All images auto-optimize

7. **Add Print Options** (if prints available):
   - Click "Add another Print Option"
   - Set size, material, price
   - Repeat for all available options

8. **Organize**:
   - Select relevant tags
   - Mark as featured if applicable
   - Set active status

9. **Save**: Images process automatically

### **Editing Existing Artwork**

1. **Find artwork** in list view (use search/filters)
2. **Click artwork title** to edit
3. **Review current images** in preview section
4. **Upload new images** to replace existing ones
5. **Update any other fields** as needed
6. **Save changes**

### **Managing Categories & Series**

#### **Categories**
- Go to `/admin/artwork/category/`
- Create logical groupings (Landscapes, Portraits, etc.)
- Set display order for homepage/gallery sorting
- Add descriptions for SEO

#### **Series**
- Go to `/admin/artwork/series/`
- Create series within categories
- Use for related artwork groupings
- Helps with organization and navigation

#### **Tags**
- Go to `/admin/artwork/tag/`
- Create descriptive tags (watercolor, peaceful, etc.)
- Set colors for visual distinction
- Use for filtering and discovery

## Validation & Error Handling

### **Automatic Validation**
- **Image files**: Type, size, format validation
- **Required fields**: Title, category, dimensions, year
- **Price validation**: Required if original available
- **Alt text**: Auto-generated if not provided

### **Form Enhancement**
- **Real-time validation**: Errors shown immediately
- **Dynamic filtering**: Series updates based on category
- **Auto-slug generation**: URL-friendly slugs from titles
- **Price requirement**: Price field becomes required when original available

## Technical Features

### **Image Processing**
- **Format conversion**: Converts to WebP for optimization
- **Resize handling**: Automatic resizing if too large
- **EXIF rotation**: Auto-rotates based on camera orientation
- **Validation**: File type, size, and format checking

### **URL Generation**
- **Supabase URLs**: Generates `supabase://` URLs for storage
- **Fallback support**: Handles existing public URLs
- **Transformation**: Dynamic image sizing and optimization

### **Admin Enhancements**
- **Custom CSS**: Professional styling and layout
- **JavaScript**: Dynamic form behavior and validation
- **Media files**: Enhanced file upload interfaces
- **Error handling**: Graceful error display and recovery

## Sample Data

To test the interface with sample data:

```bash
python manage.py create_sample_artwork --count 5
```

This creates:
- Sample categories (Landscapes, Portraits, etc.)
- Related series (Mountain Views, Ocean Scenes, etc.)
- Sample tags with colors
- 5 complete artworks with all fields populated

## Best Practices

### **Image Management**
- **Consistent sizing**: Use similar aspect ratios for gallery consistency
- **High quality**: Upload high-resolution originals (system will optimize)
- **Frame variants**: Show artwork in different settings/frames
- **Alt text**: Write descriptive alt text for accessibility

### **Content Writing**
- **Descriptions**: Write engaging, detailed descriptions
- **Stories**: Share personal connections and inspiration
- **Technique notes**: Include interesting technical details
- **SEO**: Use relevant keywords naturally

### **Organization**
- **Categories**: Keep broad, logical categories
- **Series**: Group related works for easier browsing
- **Tags**: Use consistent, descriptive tags
- **Featured**: Highlight your best works

### **Pricing**
- **Research**: Price competitively based on size, medium, complexity
- **Print tiers**: Offer multiple print sizes and materials
- **Availability**: Keep status updated (available, sold, etc.)

The artwork admin interface is now ready for professional art portfolio management with comprehensive features for content, images, pricing, and organization.
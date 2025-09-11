# LumaPrints Integration Setup

This document explains how to configure LumaPrints integration for automatic print fulfillment.

## Environment Variables

Add these variables to your `.env` file:

```bash
# LumaPrints API Configuration
LUMA_PRINTS_API_KEY=your_luma_prints_api_key_here
LUMA_PRINTS_BASE_URL=https://api.lumaprints.com/v1
LUMA_PRINTS_TEST_MODE=True  # Set to False for production
LUMA_PRINTS_WEBHOOK_SECRET=your_webhook_secret_here
```

## How It Works

### Complete Lifecycle Management

The integration automatically handles all artwork operations:

#### 1. **Create Print Artwork**
When you create a new artwork with `type = 'print'`:
1. **Artwork Saved**: Django saves the artwork to the database
2. **Image Processing**: System generates a signed URL for the main image  
3. **LumaPrints API Call**: Automatically creates a product in LumaPrints with:
   - Artwork title as product name
   - Description from artwork
   - Main image as print source
   - Standard print options (8x10, 11x14, 16x20, 24x30)
   - Pricing: $45, $65, $95, $150 respectively
4. **Product ID Storage**: LumaPrints product ID is saved to `artwork.lumaprints_product_id`

#### 2. **Edit Print Artwork**
When you edit a print artwork with key changes:
- **Monitored Fields**: title, description, main_image_url, type, is_active
- **Auto-Update**: Changes automatically sync to LumaPrints product
- **Background Processing**: Updates happen without blocking the UI

#### 3. **Convert Artwork Type**
When you change artwork type:
- **Original → Print**: Creates new LumaPrints product
- **Print → Original**: Deletes LumaPrints product and clears ID
- **Seamless Conversion**: No manual intervention required

#### 4. **Delete Print Artwork**
When you delete a print artwork:
- **LumaPrints Cleanup**: Automatically deletes the product from LumaPrints
- **Background Processing**: Deletion happens without blocking the operation

### Error Handling

- If LumaPrints API fails, artwork creation still succeeds
- Errors are logged but don't break the workflow
- Admin can retry with management command later

## Management Commands

### Sync Print Artworks

```bash
# Create LumaPrints products for artworks that don't have them
python manage.py sync_luma_prints --create-missing

# Update existing LumaPrints products with latest artwork data
python manage.py sync_luma_prints --update-existing

# Force update all print artworks
python manage.py sync_luma_prints --force

# Process specific artwork by ID
python manage.py sync_luma_prints --artwork-id 123 --create-missing

# Clean up orphaned LumaPrints product IDs (from type changes)
python manage.py sync_luma_prints --cleanup-orphaned
```

## Testing

### Full Lifecycle Testing

1. **Set Test Mode**: Ensure `LUMA_PRINTS_TEST_MODE=True` in your environment

2. **Create Print Artwork**: 
   - Use Django admin or artwork form to create artwork with `type='print'`
   - Check console for: `✓ Created LumaPrints product for 'Title' - ID: xxx`
   - Verify `lumaprints_product_id` is populated in artwork

3. **Edit Print Artwork**:
   - Change title, description, or main image
   - Check console for: `✓ Updated LumaPrints product for 'Title' - ID: xxx`
   - Verify changes sync to LumaPrints

4. **Convert Artwork Type**:
   - Change `type` from 'print' to 'original'
   - Check console for: `✓ Deleted LumaPrints product for 'Title' (type changed to original)`
   - Verify `lumaprints_product_id` is cleared
   - Change back to 'print' to test creation

5. **Delete Print Artwork**:
   - Delete a print artwork from admin
   - Check console for: `✓ Deleted LumaPrints product for 'Title'`

6. **Run Cleanup**:
   - `python manage.py sync_luma_prints --cleanup-orphaned`
   - Verifies no orphaned product IDs remain

## Print Options

The integration automatically creates these print options for each artwork:

| Size | Material | Finish | Price |
|------|----------|--------|-------|
| 8x10 | Fine Art Paper | Matte | $45 |
| 11x14 | Fine Art Paper | Matte | $65 |
| 16x20 | Fine Art Paper | Matte | $95 |
| 24x30 | Fine Art Paper | Matte | $150 |

## Order Fulfillment

When customers purchase prints:

1. **Order Created**: Django creates order with print items
2. **LumaPrints Order**: System automatically sends order to LumaPrints via API
3. **Status Updates**: Webhooks update order status (processing, shipped, delivered)
4. **Customer Notifications**: Email updates sent based on status changes

## Troubleshooting

### Common Issues

**"Failed to create product: Authentication failed"**
- Check `LUMA_PRINTS_API_KEY` is correct
- Verify API key has proper permissions

**"Failed to generate signed image URL"**
- Ensure artwork has `main_image_url` 
- Check Supabase configuration and access permissions

**"Product created but no product_id returned"**
- Check LumaPrints API response format
- Verify test mode settings match expectations

### Debug Mode

For additional debugging, you can add temporary print statements or use Django's logging framework to track the integration flow.

## Production Deployment

Before going live:

1. Set `LUMA_PRINTS_TEST_MODE=False`
2. Use production LumaPrints API credentials
3. Test end-to-end workflow with real orders
4. Configure webhook endpoints for status updates
5. Test print quality and fulfillment times

## Support

For LumaPrints API issues, consult their documentation or contact their support team. For integration issues with this Django implementation, check the error logs and management command output for detailed troubleshooting information.
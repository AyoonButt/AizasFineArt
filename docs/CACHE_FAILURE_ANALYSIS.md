# Image Cache Failure Analysis Report

## 🎯 Root Causes Identified

### 1. **Database Constraint Issue**
- **Problem**: `_cached_image_url` field has NOT NULL constraint but `refresh_url_cache()` sets it to empty string
- **Evidence**: `IntegrityError: NOT NULL constraint failed: artwork_artwork._cached_image_url`
- **Impact**: Database errors prevent cache updates from saving

### 2. **Flawed Cache Refresh Logic**
- **Problem**: `refresh_url_cache()` method only CLEARS cache, doesn't REGENERATE URLs
- **Current behavior**:
  ```python
  def refresh_url_cache(self):
      self._cached_image_url = ''  # CLEARS but doesn't regenerate
      self._cached_thumbnail_url = ''
      self._cached_frame_urls = {}
      self._url_cache_expires = None
  ```
- **Impact**: Templates get empty URLs until next method call

### 3. **Supabase Transform API Issues**
- **Problem**: Image transformations fail with format validation errors
- **Evidence**: `body/transform/format must be equal to one of the allowed values`
- **Impact**: `get_image()` falls back to simple signed URLs, losing transformations

### 4. **Silent Background Failures**
- **Problem**: Background refresh threads fail silently without logging or user feedback
- **Impact**: Users see broken images with no indication of the problem

### 5. **Template Dependency on Cached URLs**
- **Problem**: Templates use `{{ artwork.image_url }}` which depends on cached values
- **Impact**: When cache is cleared/expired, templates display empty images

## 🔍 Test Results Summary

### ✅ What's Working:
- Supabase connection and authentication
- Basic signed URL generation (`get_simple_signed_url()`)
- Management command can refresh URLs when forced
- Database queries for artworks with supabase:// URLs

### ❌ What's Failing:
- Cache refresh doesn't regenerate URLs immediately
- Database constraints prevent NULL cached URLs
- Image transformations fail due to format validation
- Background refresh threads fail silently
- Templates show empty images during cache refresh

### ⚠️ Warnings:
- Cache expires in 37.3 minutes (normal)
- Transformation errors fall back to simple URLs (functional but not optimal)

## 📊 HTTP Request Analysis
From the logs, we can see:
- ✅ `POST /storage/v1/object/list/art-storage` → 200 OK (listing works)
- ✅ `POST /storage/v1/object/sign/art-storage/artwork/file.jpg` → 200 OK (signing works)
- ❌ `POST /storage/v1/object/sign/art-storage/artwork/file.jpg` → 400 Bad Request (transformations fail)

## 💡 Recommended Solutions

### Immediate Fixes:
1. **Fix Database Constraint**: Allow NULL values or use empty string default
2. **Fix refresh_url_cache()**: Immediately regenerate URLs after clearing cache
3. **Fix Supabase Transformations**: Update format parameter to valid values
4. **Add Error Logging**: Replace silent failures with proper error logging

### Long-term Solutions:
1. **On-Demand URL Generation**: Eliminate cache dependency entirely
2. **Fallback Chain**: Multiple URL generation strategies
3. **Client-side Retry Logic**: Handle failures gracefully in templates
4. **Monitoring**: Track URL generation success/failure rates

## 🚨 Critical Issue Priority:
1. **HIGH**: Database constraint preventing saves
2. **HIGH**: refresh_url_cache() not regenerating URLs  
3. **MEDIUM**: Supabase transformation format errors
4. **MEDIUM**: Silent background failures
5. **LOW**: Template error handling improvements
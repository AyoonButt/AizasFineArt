# 🧪 Tests Directory

This directory contains all test files and testing utilities for the Aiza's Fine Art project.

## 📋 Test Categories

### Cache System Tests
- `test_cache_targeted.py` - Targeted cache refresh mechanism tests
- `test_cache_issue_analysis.py` - Cache failure analysis and diagnostics
- `test_image_cache_diagnosis.py` - Image cache system diagnostics
- `test_nonce_cache_system.py` - Nonce-based cache system tests (deprecated)
- `test_unique_expiry_system.py` - **Main cache system test** - Tests the production unique expiry system
- `test_production_ready.py` - **Production validation** - Final system verification

### Just-In-Time Refresh Tests
- `test_jit_refresh.py` - Just-in-time refresh with short timeouts
- `test_quick_jit.py` - Quick cache logic validation

### Frame and Performance Tests
- `test_frame_preloading.py` - Frame image preloading system tests
- `verify_cache_fixes.py` - Cache fix verification

### Build and Development Tests
- `test-build.js` - JavaScript build testing
- `webpack.test.js` - Webpack configuration testing
- `test-minimal.css` - Minimal CSS for testing
- `test-output/` - Build test output directory

### Application Tests
- `test_artwork_detail.py` - Artwork detail page testing
- `test_minimal.py` - Minimal application testing

## 🚀 How to Run Tests

### Cache System Tests (Recommended)
```bash
# Test the production-ready enhanced cache system
python3 tests/test_production_ready.py

# Comprehensive cache system validation
python3 tests/test_unique_expiry_system.py

# Quick cache logic verification
python3 tests/test_quick_jit.py
```

### Diagnostic Tests
```bash
# Diagnose cache issues
python3 tests/test_cache_issue_analysis.py

# Verify cache fixes
python3 tests/verify_cache_fixes.py
```

### Build Tests
```bash
# Test JavaScript build
node tests/test-build.js

# Test webpack configuration
node tests/webpack.test.js
```

## 📊 Test Results Interpretation

### ✅ Success Indicators
- URLs are unique on each refresh
- Cache hits work correctly
- URL accessibility validation passes
- Graceful error handling

### ⚠️ Warning Signs
- Identical URLs generated on refresh
- Cache misses when hits expected
- URL accessibility failures
- Exception handling not working

### ❌ Failure Modes
- No URLs generated
- Supabase connection failures
- Database save errors
- System-wide cache failures

## 🔧 Development Notes

### Key Test Files for Cache System
1. **`test_production_ready.py`** - Main production validation
2. **`test_unique_expiry_system.py`** - Comprehensive system testing
3. **`test_cache_targeted.py`** - Specific cache behavior testing

### Test Environment Setup
- Tests require valid Supabase credentials
- Django settings must be properly configured
- Database connection required for cache tests

### Historical Context
- `test_nonce_cache_system.py` tests the deprecated nonce approach
- Unique expiry system replaced the nonce approach due to Supabase limitations
- Cache system evolved from simple time-based to two-tier validation

## 📝 Adding New Tests

When adding new tests:
1. Follow the naming convention: `test_<component>_<purpose>.py`
2. Include proper error handling and cleanup
3. Add descriptive docstrings and comments
4. Update this README with test descriptions
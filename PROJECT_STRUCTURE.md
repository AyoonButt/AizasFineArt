# 📁 Project Structure

This document outlines the organized structure of the Aiza's Fine Art project.

## 🎯 Main Application
```
/
├── manage.py                 # Django management script
├── aizasfineart/            # Main Django project directory
├── artwork/                 # Artwork application
├── orders/                  # Orders application
├── api/                     # API endpoints
├── utils/                   # Utility modules (e.g., supabase_client.py)
├── static/                  # Static assets (CSS, JS, images)
├── templates/               # Django templates
├── requirements.txt         # Python dependencies
├── package.json            # Node.js dependencies
├── webpack.config.js       # Webpack configuration
└── tailwind.config.js      # Tailwind CSS configuration
```

## 🧪 Tests Directory
```
tests/
├── README.md                        # Test documentation
├── test_production_ready.py         # ⭐ Main production validation
├── test_unique_expiry_system.py     # ⭐ Comprehensive cache testing
├── test_cache_targeted.py           # Cache-specific tests
├── test_quick_jit.py               # Quick cache validation
├── test_nonce_cache_system.py      # Historical nonce tests
├── test_jit_refresh.py             # JIT refresh tests
├── test_cache_issue_analysis.py    # Cache diagnostics
├── test_image_cache_diagnosis.py   # Image cache diagnostics
├── test_frame_preloading.py        # Frame image tests
├── verify_cache_fixes.py           # Cache fix verification
├── test_artwork_detail.py          # Artwork page tests
├── test_minimal.py                 # Minimal app tests
├── performance_test.py             # Performance benchmarks
├── database_performance_test.py    # Database performance
├── simple_test_server.py           # Test server utility
├── test-build.js                   # JavaScript build tests
├── webpack.test.js                 # Webpack tests
├── test-minimal.css                # Test CSS
└── test-output/                    # Test build output
```

## 📚 Documentation Directory
```
docs/
├── README_DOCS.md                   # Documentation overview
├── README.md                        # Main project documentation
├── CLAUDE.md                        # ⭐ Development audit trail
├── DEVELOPER_GUIDE.md               # Developer setup guide
├── PERFORMANCE_IMPROVEMENTS.md      # ⭐ Performance optimization log
├── SUPABASE_SETUP.md               # Storage configuration
├── CHECKOUT_SETUP.md               # Payment system setup
├── GOOGLE_OAUTH_SETUP.md           # OAuth configuration
├── LUMA_PRINTS_SETUP.md            # Print service setup
├── BUILD_PERFORMANCE_IMPROVEMENTS.md # Build optimizations
├── FRONTEND_FIXES_COMPLETED.md     # Frontend improvements
├── BUILD_ISSUES_REPORT.md          # Build issue history
└── CACHE_FAILURE_ANALYSIS.md       # Historical cache analysis
```

## 🔧 Configuration Files
```
/
├── .gitignore                # Git ignore rules
├── .claude/                  # Claude AI configuration
│   └── settings.local.json
├── Dockerfile               # Docker configuration
├── package.json            # Node.js dependencies
├── requirements.txt        # Python dependencies
├── tailwind.config.js      # Tailwind CSS configuration
├── webpack.config.js       # Webpack bundling
└── webpack-stats.json      # Webpack output statistics
```

## 📊 Key Features by Directory

### `/tests/` - Testing Infrastructure
- **Production validation**: `test_production_ready.py`
- **Cache system verification**: `test_unique_expiry_system.py`
- **Performance benchmarks**: `performance_test.py`
- **Build testing**: `test-build.js`, `webpack.test.js`

### `/docs/` - Documentation
- **Development history**: `CLAUDE.md` (comprehensive audit trail)
- **Setup guides**: Supabase, OAuth, checkout, prints
- **Performance tracking**: Optimization logs and improvements
- **Architecture documentation**: Developer guides and README

### Main Application
- **Enhanced cache system**: `utils/supabase_client.py`, `artwork/models.py`
- **React components**: `static/src/js/react/`
- **Django applications**: `artwork/`, `orders/`, `api/`
- **Frontend assets**: `static/src/css/`, `static/src/js/`

## 🎯 Quick Navigation

### For Developers
1. **Start here**: `docs/DEVELOPER_GUIDE.md`
2. **Test cache system**: `tests/test_production_ready.py`
3. **View development history**: `docs/CLAUDE.md`

### For Testing
1. **Run main tests**: `python3 tests/test_production_ready.py`
2. **Cache diagnostics**: `python3 tests/test_unique_expiry_system.py`
3. **Performance tests**: `python3 tests/performance_test.py`

### For Documentation
1. **Project overview**: `docs/README.md`
2. **Performance improvements**: `docs/PERFORMANCE_IMPROVEMENTS.md`
3. **Service setup**: `docs/SUPABASE_SETUP.md`

## 📈 Recent Improvements

### ✅ Cache System Enhancement
- **Unique expiry-based refresh**: Solves JWT token expiration issues
- **Two-tier validation**: Time-based + accessibility checks
- **Production-ready**: Clean error handling and logging

### ✅ Project Organization
- **Separated concerns**: Tests and docs in dedicated directories
- **Clear documentation**: README files for each directory
- **Improved navigation**: Easy access to key files and resources

### ✅ Testing Infrastructure
- **Comprehensive test suite**: From unit tests to integration tests
- **Production validation**: Ensures system reliability
- **Performance monitoring**: Tracks optimization improvements
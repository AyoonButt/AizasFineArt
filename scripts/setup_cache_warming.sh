#!/bin/bash

# Enhanced setup script to configure automatic cache warming for featured artworks
# This ensures optimal performance for the homepage featured section with better error handling

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"

echo "🔥 Setting up enhanced automatic cache warming for featured artworks..."
echo "Project directory: $PROJECT_DIR"

# Verify Django management command exists
if ! cd "$PROJECT_DIR" && python3 manage.py help warm_featured_cache > /dev/null 2>&1; then
    echo "❌ Error: warm_featured_cache management command not found"
    echo "Make sure you're in the correct Django project directory"
    exit 1
fi

# Create enhanced cron job with better error handling and logging
CRON_JOB_FEATURED="0 * * * * cd $PROJECT_DIR && python3 manage.py warm_featured_cache >> /var/log/artwork_cache_warm.log 2>&1"
CRON_JOB_ALL="0 6 * * * cd $PROJECT_DIR && python3 manage.py warm_all_cache >> /var/log/artwork_cache_warm.log 2>&1"

# Check if cron jobs already exist
EXISTING_CRON=$(crontab -l 2>/dev/null || echo "")

if echo "$EXISTING_CRON" | grep -q "warm_featured_cache"; then
    echo "✓ Featured cache warming cron job already exists"
else
    echo "Adding featured cache warming cron job..."
    (echo "$EXISTING_CRON"; echo "$CRON_JOB_FEATURED") | crontab -
    echo "✓ Cron job added: Featured cache will be warmed every hour"
fi

if echo "$EXISTING_CRON" | grep -q "warm_all_cache"; then
    echo "✓ Full cache warming cron job already exists"
else
    echo "Adding full cache warming cron job..."
    (crontab -l 2>/dev/null; echo "$CRON_JOB_ALL") | crontab -
    echo "✓ Cron job added: Full cache will be warmed daily at 6 AM"
fi

# Create log directory with proper permissions
LOG_DIR="/var/log"
LOG_FILE="/var/log/artwork_cache_warm.log"

if [ -w "$LOG_DIR" ]; then
    touch "$LOG_FILE"
    chmod 644 "$LOG_FILE" 2>/dev/null || true
    echo "✓ Log file configured: $LOG_FILE"
else
    # Fallback to project directory for logging if /var/log is not writable
    LOG_FILE="$PROJECT_DIR/cache_warming.log"
    touch "$LOG_FILE"
    echo "⚠️  Using project directory for logs: $LOG_FILE"
    
    # Update cron jobs to use project directory for logs
    NEW_CRON=$(crontab -l 2>/dev/null | sed "s|/var/log/artwork_cache_warm.log|$LOG_FILE|g")
    echo "$NEW_CRON" | crontab -
fi

# Test the cache warming command
echo ""
echo "🧪 Testing cache warming command..."
cd "$PROJECT_DIR"
if python3 manage.py warm_featured_cache --help > /dev/null 2>&1; then
    echo "✓ Cache warming command is working"
    
    # Run a quick test (dry run)
    echo "Running quick test..."
    python3 manage.py warm_featured_cache | head -5
else
    echo "❌ Error: Cache warming command failed"
    exit 1
fi

echo ""
echo "✅ Enhanced cache warming setup complete!"
echo ""
echo "📋 Configuration Summary:"
echo "  • Featured artworks: Every hour (0 * * * *)"
echo "  • All artworks: Daily at 6 AM (0 6 * * *)"
echo "  • Log location: $LOG_FILE"
echo ""
echo "🔧 Manual Commands:"
echo "  • Featured cache: python3 manage.py warm_featured_cache"
echo "  • All cache: python3 manage.py warm_all_cache"
echo "  • Refresh URLs: python3 manage.py refresh_image_urls"
echo ""
echo "📊 Monitor Cron Jobs:"
echo "  • View cron jobs: crontab -l"
echo "  • View logs: tail -f $LOG_FILE"
echo "  • Check last run: ls -la $LOG_FILE"
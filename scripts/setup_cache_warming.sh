#!/bin/bash

# Setup script to configure automatic cache warming for featured artworks
# This ensures optimal performance for the homepage featured section

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"

echo "Setting up automatic cache warming for featured artworks..."

# Create cron job to warm cache every hour
CRON_JOB="0 * * * * cd $PROJECT_DIR && python3 manage.py warm_featured_cache >> /var/log/artwork_cache_warm.log 2>&1"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "warm_featured_cache"; then
    echo "Cache warming cron job already exists."
else
    echo "Adding cache warming cron job..."
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    echo "✓ Cron job added: Cache will be warmed every hour"
fi

# Create log directory if it doesn't exist
sudo mkdir -p /var/log
sudo touch /var/log/artwork_cache_warm.log
sudo chmod 644 /var/log/artwork_cache_warm.log

echo "✓ Cache warming setup complete!"
echo ""
echo "Manual cache warming: python3 manage.py warm_featured_cache"
echo "Log location: /var/log/artwork_cache_warm.log"
echo "Cron schedule: Every hour (0 * * * *)"
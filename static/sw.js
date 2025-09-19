// Service Worker for Aiza's Fine Art - Caching & Performance
const CACHE_NAME = 'aizas-art-v1';
const STATIC_CACHE = 'static-v1';
const IMAGE_CACHE = 'images-v1';

// Cache strategies
const CACHE_STRATEGIES = {
    NETWORK_FIRST: 'network-first',
    CACHE_FIRST: 'cache-first',
    STALE_WHILE_REVALIDATE: 'stale-while-revalidate'
};

// Cache configuration
const CACHE_CONFIG = {
    // Static assets - cache first
    static: {
        strategy: CACHE_STRATEGIES.CACHE_FIRST,
        maxAge: 7 * 24 * 60 * 60 * 1000, // 7 days
        patterns: [
            /\.css$/,
            /\.js$/,
            /\.woff2?$/,
            /\.png$/,
            /\.ico$/
        ]
    },
    
    // Images - cache first with long expiry
    images: {
        strategy: CACHE_STRATEGIES.CACHE_FIRST,
        maxAge: 30 * 24 * 60 * 60 * 1000, // 30 days
        patterns: [
            /\.jpg$/,
            /\.jpeg$/,
            /\.png$/,
            /\.webp$/,
            /\.avif$/
        ]
    },
    
    // HTML pages - stale while revalidate
    pages: {
        strategy: CACHE_STRATEGIES.STALE_WHILE_REVALIDATE,
        maxAge: 24 * 60 * 60 * 1000, // 1 day
        patterns: [
            /\/gallery\//,
            /\/shop\//,
            /\/art\//,
            /\/portfolio\//
        ]
    },
    
    // API responses - network first
    api: {
        strategy: CACHE_STRATEGIES.NETWORK_FIRST,
        maxAge: 5 * 60 * 1000, // 5 minutes
        patterns: [
            /\/api\//
        ]
    }
};

// Install event - cache essential resources
self.addEventListener('install', event => {
    event.waitUntil(
        Promise.all([
            caches.open(STATIC_CACHE).then(cache => {
                return cache.addAll([
                    '/static/dist/css/main.css',
                    '/static/src/js/loading-optimizer.js',
                    '/static/src/js/lazy-loader.js',
                    '/static/src/js/performance-monitor.js'
                ]);
            }),
            self.skipWaiting()
        ])
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
    event.waitUntil(
        Promise.all([
            caches.keys().then(cacheNames => {
                return Promise.all(
                    cacheNames.map(cacheName => {
                        if (!cacheName.includes('v1')) {
                            return caches.delete(cacheName);
                        }
                    })
                );
            }),
            self.clients.claim()
        ])
    );
});

// Fetch event - implement caching strategies
self.addEventListener('fetch', event => {
    const request = event.request;
    
    // Skip non-GET requests
    if (request.method !== 'GET') {
        return;
    }
    
    // Skip chrome-extension and other non-http requests
    if (!request.url.startsWith('http')) {
        return;
    }
    
    // Determine cache strategy
    const strategy = getCacheStrategy(request.url);
    
    event.respondWith(
        handleRequest(request, strategy)
    );
});

// Determine appropriate cache strategy
function getCacheStrategy(url) {
    for (const [type, config] of Object.entries(CACHE_CONFIG)) {
        for (const pattern of config.patterns) {
            if (pattern.test(url)) {
                return config;
            }
        }
    }
    
    // Default to stale while revalidate for unknown resources
    return CACHE_CONFIG.pages;
}

// Handle request based on strategy
async function handleRequest(request, strategy) {
    const cacheName = getCacheName(request.url);
    
    switch (strategy.strategy) {
        case CACHE_STRATEGIES.CACHE_FIRST:
            return cacheFirst(request, cacheName, strategy);
        
        case CACHE_STRATEGIES.NETWORK_FIRST:
            return networkFirst(request, cacheName, strategy);
        
        case CACHE_STRATEGIES.STALE_WHILE_REVALIDATE:
            return staleWhileRevalidate(request, cacheName, strategy);
        
        default:
            return fetch(request);
    }
}

// Get appropriate cache name
function getCacheName(url) {
    if (CACHE_CONFIG.images.patterns.some(pattern => pattern.test(url))) {
        return IMAGE_CACHE;
    }
    if (CACHE_CONFIG.static.patterns.some(pattern => pattern.test(url))) {
        return STATIC_CACHE;
    }
    return CACHE_NAME;
}

// Cache first strategy
async function cacheFirst(request, cacheName, strategy) {
    try {
        const cache = await caches.open(cacheName);
        const cached = await cache.match(request);
        
        if (cached && !isExpired(cached, strategy.maxAge)) {
            return cached;
        }
        
        const response = await fetch(request);
        
        if (response.status === 200) {
            await cache.put(request, response.clone());
        }
        
        return response;
        
    } catch (error) {
        console.warn('Cache first failed:', error);
        const cache = await caches.open(cacheName);
        return await cache.match(request) || new Response('Offline', { status: 503 });
    }
}

// Network first strategy
async function networkFirst(request, cacheName, strategy) {
    try {
        const response = await fetch(request);
        
        if (response.status === 200) {
            const cache = await caches.open(cacheName);
            await cache.put(request, response.clone());
        }
        
        return response;
        
    } catch (error) {
        console.warn('Network first failed, trying cache:', error);
        const cache = await caches.open(cacheName);
        const cached = await cache.match(request);
        
        if (cached) {
            return cached;
        }
        
        throw error;
    }
}

// Stale while revalidate strategy
async function staleWhileRevalidate(request, cacheName, strategy) {
    const cache = await caches.open(cacheName);
    const cached = await cache.match(request);
    
    // Start fetch in background
    const fetchPromise = fetch(request).then(response => {
        if (response.status === 200) {
            cache.put(request, response.clone());
        }
        return response;
    }).catch(error => {
        console.warn('Background fetch failed:', error);
        return null;
    });
    
    // Return cached version immediately if available
    if (cached && !isExpired(cached, strategy.maxAge)) {
        return cached;
    }
    
    // Wait for network if no cache or expired
    return await fetchPromise || cached || new Response('Offline', { status: 503 });
}

// Check if cached response is expired
function isExpired(response, maxAge) {
    if (!maxAge) return false;
    
    const cached = new Date(response.headers.get('date'));
    const now = new Date();
    
    return (now - cached) > maxAge;
}

// Background sync for image preloading
self.addEventListener('message', event => {
    if (event.data && event.data.type === 'PRELOAD_IMAGES') {
        event.waitUntil(
            preloadImages(event.data.urls)
        );
    }
    
    if (event.data && event.data.type === 'CLEAR_CACHE') {
        event.waitUntil(
            clearExpiredCache()
        );
    }
    
    if (event.data && event.data.type === 'WARM_CACHE') {
        event.waitUntil(
            warmCacheFromAPI().then(result => {
                if (event.ports && event.ports[0]) {
                    event.ports[0].postMessage(result);
                }
            })
        );
    }
    
    if (event.data && event.data.type === 'CACHE_STATS') {
        event.waitUntil(
            getCacheStats().then(stats => {
                if (event.ports && event.ports[0]) {
                    event.ports[0].postMessage(stats);
                }
            })
        );
    }
});

// Preload images
async function preloadImages(urls) {
    const cache = await caches.open(IMAGE_CACHE);
    
    const preloadPromises = urls.map(async (url) => {
        try {
            const response = await fetch(url, { 
                mode: 'cors',
                credentials: 'omit'
            });
            
            if (response.status === 200) {
                await cache.put(url, response);
            }
        } catch (error) {
            console.warn('Preload failed for:', url, error);
        }
    });
    
    await Promise.all(preloadPromises);
}

// Clear expired cache entries
async function clearExpiredCache() {
    const cacheNames = await caches.keys();
    
    for (const cacheName of cacheNames) {
        const cache = await caches.open(cacheName);
        const keys = await cache.keys();
        
        for (const request of keys) {
            const response = await cache.match(request);
            if (response && isExpired(response, 7 * 24 * 60 * 60 * 1000)) {
                await cache.delete(request);
            }
        }
    }
}

// Warm cache by fetching featured artwork images from API
async function warmCacheFromAPI() {
    try {
        // Fetch featured artworks from API
        const response = await fetch('/api/artworks/?is_featured=true&limit=5', {
            mode: 'cors',
            credentials: 'same-origin'
        });
        
        if (!response.ok) {
            throw new Error(`API request failed: ${response.status}`);
        }
        
        const data = await response.json();
        const imageUrls = [];
        
        // Extract image URLs from artwork data
        if (data.results && Array.isArray(data.results)) {
            data.results.forEach(artwork => {
                if (artwork.image_url) {
                    imageUrls.push(artwork.image_url);
                }
                if (artwork.thumbnail_url) {
                    imageUrls.push(artwork.thumbnail_url);
                }
            });
        }
        
        // Preload the images
        if (imageUrls.length > 0) {
            await preloadImages(imageUrls);
            return {
                success: true,
                message: `Warmed cache for ${imageUrls.length} images`,
                count: imageUrls.length
            };
        } else {
            return {
                success: true,
                message: 'No images found to cache',
                count: 0
            };
        }
        
    } catch (error) {
        console.error('Cache warming failed:', error);
        return {
            success: false,
            message: error.message,
            count: 0
        };
    }
}

// Get cache statistics
async function getCacheStats() {
    try {
        const stats = {
            caches: {},
            totalSize: 0,
            totalEntries: 0,
            lastUpdated: new Date().toISOString()
        };
        
        const cacheNames = await caches.keys();
        
        for (const cacheName of cacheNames) {
            const cache = await caches.open(cacheName);
            const keys = await cache.keys();
            
            let cacheSize = 0;
            let expiredCount = 0;
            
            for (const request of keys) {
                const response = await cache.match(request);
                if (response) {
                    // Estimate size (not exact, but gives an idea)
                    const clone = response.clone();
                    const buffer = await clone.arrayBuffer();
                    cacheSize += buffer.byteLength;
                    
                    // Check if expired
                    if (isExpired(response, 30 * 24 * 60 * 60 * 1000)) {
                        expiredCount++;
                    }
                }
            }
            
            stats.caches[cacheName] = {
                entries: keys.length,
                sizeBytes: cacheSize,
                sizeMB: Math.round(cacheSize / 1024 / 1024 * 100) / 100,
                expiredEntries: expiredCount
            };
            
            stats.totalSize += cacheSize;
            stats.totalEntries += keys.length;
        }
        
        stats.totalSizeMB = Math.round(stats.totalSize / 1024 / 1024 * 100) / 100;
        
        return stats;
        
    } catch (error) {
        console.error('Failed to get cache stats:', error);
        return {
            error: error.message,
            lastUpdated: new Date().toISOString()
        };
    }
}
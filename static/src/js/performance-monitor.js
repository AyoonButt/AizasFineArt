// Performance Monitoring for Aiza's Fine Art
// Tracks loading speeds and user experience metrics

class PerformanceMonitor {
    constructor() {
        this.metrics = {
            pageLoad: 0,
            firstPaint: 0,
            firstContentfulPaint: 0,
            largestContentfulPaint: 0,
            cumulativeLayoutShift: 0,
            totalBlockingTime: 0,
            imageLoadTimes: [],
            masonryLayoutTime: 0
        };
        
        this.init();
    }
    
    init() {
        // Only run if performance API is available
        if (!('performance' in window)) return;
        
        this.measurePageLoad();
        this.measurePaintTimings();
        this.measureLCP();
        this.measureCLS();
        this.trackImageLoading();
        this.trackMasonryPerformance();
        
        // Report metrics after page is fully loaded
        window.addEventListener('load', () => {
            setTimeout(() => this.reportMetrics(), 1000);
        });
    }
    
    measurePageLoad() {
        window.addEventListener('load', () => {
            const navigation = performance.getEntriesByType('navigation')[0];
            if (navigation) {
                this.metrics.pageLoad = navigation.loadEventEnd - navigation.fetchStart;
            }
        });
    }
    
    measurePaintTimings() {
        const paintEntries = performance.getEntriesByType('paint');
        paintEntries.forEach(entry => {
            if (entry.name === 'first-paint') {
                this.metrics.firstPaint = entry.startTime;
            } else if (entry.name === 'first-contentful-paint') {
                this.metrics.firstContentfulPaint = entry.startTime;
            }
        });
    }
    
    measureLCP() {
        if ('PerformanceObserver' in window) {
            const observer = new PerformanceObserver((list) => {
                const entries = list.getEntries();
                const lastEntry = entries[entries.length - 1];
                this.metrics.largestContentfulPaint = lastEntry.startTime;
            });
            
            try {
                observer.observe({ entryTypes: ['largest-contentful-paint'] });
            } catch (e) {
                console.log('LCP measurement not supported');
            }
        }
    }
    
    measureCLS() {
        if ('PerformanceObserver' in window) {
            let clsScore = 0;
            const observer = new PerformanceObserver((list) => {
                for (const entry of list.getEntries()) {
                    if (!entry.hadRecentInput) {
                        clsScore += entry.value;
                    }
                }
                this.metrics.cumulativeLayoutShift = clsScore;
            });
            
            try {
                observer.observe({ entryTypes: ['layout-shift'] });
            } catch (e) {
                console.log('CLS measurement not supported');
            }
        }
    }
    
    trackImageLoading() {
        const observer = new PerformanceObserver((list) => {
            list.getEntries().forEach(entry => {
                if (entry.name.includes('.jpg') || entry.name.includes('.jpeg') || 
                    entry.name.includes('.png') || entry.name.includes('.webp')) {
                    this.metrics.imageLoadTimes.push({
                        url: entry.name,
                        duration: entry.duration,
                        size: entry.transferSize || 0
                    });
                }
            });
        });
        
        try {
            observer.observe({ entryTypes: ['resource'] });
        } catch (e) {
            console.log('Resource timing not supported');
        }
    }
    
    trackMasonryPerformance() {
        // Hook into masonry layout timing
        const originalConsoleLog = console.log;
        console.log = (...args) => {
            const message = args.join(' ');
            
            // Look for masonry completion messages
            if (message.includes('masonry layout complete')) {
                const match = message.match(/(\d+)px/);
                if (match) {
                    // Estimate layout time based on container height
                    const containerHeight = parseInt(match[1]);
                    this.metrics.masonryLayoutTime = performance.now() - this.pageStartTime;
                }
            }
            
            originalConsoleLog.apply(console, args);
        };
        
        this.pageStartTime = performance.now();
    }
    
    getWebVitalsGrade() {
        const scores = {
            lcp: this.metrics.largestContentfulPaint <= 2500 ? 'good' : 
                 this.metrics.largestContentfulPaint <= 4000 ? 'needs-improvement' : 'poor',
            cls: this.metrics.cumulativeLayoutShift <= 0.1 ? 'good' :
                 this.metrics.cumulativeLayoutShift <= 0.25 ? 'needs-improvement' : 'poor',
            fcp: this.metrics.firstContentfulPaint <= 1800 ? 'good' :
                 this.metrics.firstContentfulPaint <= 3000 ? 'needs-improvement' : 'poor'
        };
        
        return scores;
    }
    
    reportMetrics() {
        const vitals = this.getWebVitalsGrade();
        const avgImageLoadTime = this.metrics.imageLoadTimes.length > 0 ?
            this.metrics.imageLoadTimes.reduce((sum, img) => sum + img.duration, 0) / this.metrics.imageLoadTimes.length : 0;
        
        const report = {
            timestamp: new Date().toISOString(),
            url: window.location.href,
            userAgent: navigator.userAgent,
            connection: navigator.connection ? {
                effectiveType: navigator.connection.effectiveType,
                downlink: navigator.connection.downlink,
                rtt: navigator.connection.rtt
            } : null,
            metrics: this.metrics,
            webVitals: vitals,
            averageImageLoadTime: avgImageLoadTime,
            totalImages: this.metrics.imageLoadTimes.length
        };
        
        // Log to console in development
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            console.group('🚀 Performance Report');
            console.log('Page Load Time:', this.formatTime(this.metrics.pageLoad));
            console.log('First Contentful Paint:', this.formatTime(this.metrics.firstContentfulPaint), `(${vitals.fcp})`);
            console.log('Largest Contentful Paint:', this.formatTime(this.metrics.largestContentfulPaint), `(${vitals.lcp})`);
            console.log('Cumulative Layout Shift:', this.metrics.cumulativeLayoutShift.toFixed(4), `(${vitals.cls})`);
            console.log('Average Image Load Time:', this.formatTime(avgImageLoadTime));
            console.log('Images Loaded:', this.metrics.imageLoadTimes.length);
            console.log('Masonry Layout Time:', this.formatTime(this.metrics.masonryLayoutTime));
            console.groupEnd();
        }
        
        // Store for analytics (can be sent to monitoring service)
        this.storeMetrics(report);
        
        return report;
    }
    
    formatTime(ms) {
        return `${Math.round(ms)}ms`;
    }
    
    storeMetrics(report) {
        // Store in localStorage for debugging
        try {
            localStorage.setItem('performance-metrics', JSON.stringify(report));
        } catch (e) {
            console.warn('Could not store performance metrics');
        }
    }
    
    getStoredMetrics() {
        try {
            const stored = localStorage.getItem('performance-metrics');
            return stored ? JSON.parse(stored) : null;
        } catch (e) {
            return null;
        }
    }
}

// Auto-initialize
document.addEventListener('DOMContentLoaded', () => {
    window.performanceMonitor = new PerformanceMonitor();
});

// Export for manual use
window.PerformanceMonitor = PerformanceMonitor;
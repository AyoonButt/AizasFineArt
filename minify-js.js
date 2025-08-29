const fs = require('fs');
const path = require('path');

function minifyJS(code) {
    // Basic minification - remove comments and extra whitespace
    return code
        // Remove single-line comments
        .replace(/\/\/.*$/gm, '')
        // Remove multi-line comments
        .replace(/\/\*[\s\S]*?\*\//g, '')
        // Remove extra whitespace and newlines
        .replace(/\s+/g, ' ')
        // Remove space around operators and punctuation
        .replace(/\s*([{}();,=+\-*/])\s*/g, '$1')
        // Remove trailing spaces
        .replace(/^\s+|\s+$/gm, '')
        // Remove empty lines
        .replace(/\n\s*\n/g, '\n')
        .trim();
}

function minifyJSFiles() {
    const jsDir = 'static/dist/js';
    const files = fs.readdirSync(jsDir).filter(file => file.endsWith('.js'));
    
    console.log(`Minifying ${files.length} JavaScript files...`);
    
    files.forEach(file => {
        const filePath = path.join(jsDir, file);
        const originalCode = fs.readFileSync(filePath, 'utf8');
        const minifiedCode = minifyJS(originalCode);
        
        const originalSize = Buffer.byteLength(originalCode, 'utf8');
        const minifiedSize = Buffer.byteLength(minifiedCode, 'utf8');
        const savings = Math.round(((originalSize - minifiedSize) / originalSize) * 100);
        
        fs.writeFileSync(filePath, minifiedCode);
        
        console.log(`${file}: ${formatBytes(originalSize)} → ${formatBytes(minifiedSize)} (${savings}% reduction)`);
    });
}

function formatBytes(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

// Run minification
minifyJSFiles();
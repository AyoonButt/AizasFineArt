const path = require('path');

// Test if we can require React components
try {
  console.log('Testing Node environment...');
  console.log('Current directory:', __dirname);
  console.log('Node version:', process.version);
  
  // Test babel-loader
  const babel = require('@babel/core');
  console.log('Babel version:', babel.version);
  
  // Test webpack
  const webpack = require('webpack');
  console.log('Webpack version:', webpack.version);
  
  console.log('✅ All core dependencies loaded successfully');
} catch (error) {
  console.error('❌ Error loading dependencies:', error.message);
}
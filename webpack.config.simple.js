const path = require('path');
const BundleTracker = require('webpack-bundle-tracker');

module.exports = {
  context: __dirname,
  
  entry: {
    // Single main entry point to avoid complexity
    main: './static/src/js/react/index.js',
  },

  output: {
    path: path.resolve('./static/dist/js/'),
    filename: '[name].bundle.js',
    publicPath: '/static/dist/js/',
    clean: false, // Don't clean to avoid conflicts
  },

  module: {
    rules: [
      {
        test: /\.jsx?$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: [
              ['@babel/preset-env', {
                targets: 'defaults'
              }],
              '@babel/preset-react'
            ]
          }
        }
      }
    ]
  },

  plugins: [
    new BundleTracker({
      path: __dirname,
      filename: 'webpack-stats.json'
    })
  ],

  resolve: {
    extensions: ['.js', '.jsx'],
    alias: {
      '@': path.resolve(__dirname, 'static/src/js/react'),
      '@components': path.resolve(__dirname, 'static/src/js/react/components'),
    }
  },

  // Disable code splitting for simplicity
  optimization: {
    splitChunks: false
  },

  // Speed up build
  devtool: false,
  
  // External dependencies to avoid bundling
  externals: {
    'react': 'React',
    'react-dom': 'ReactDOM'
  },

  // Performance settings
  performance: {
    hints: false
  }
};
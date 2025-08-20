const path = require('path');
const BundleTracker = require('webpack-bundle-tracker');

module.exports = {
  context: __dirname,
  
  entry: {
    // Main React entry points
    main: './static/src/js/react/index.js',
    // Component-specific bundles for better code splitting
    gallery: './static/src/js/react/components/Gallery/index.js',
    forms: './static/src/js/react/components/Forms/index.js',
  },

  output: {
    path: path.resolve('./static/dist/js/'),
    filename: '[name]-[contenthash].js',
    chunkFilename: '[name]-[contenthash].js',
    publicPath: '/static/dist/js/',
    clean: true,
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
                targets: {
                  browsers: ['last 2 versions']
                }
              }],
              ['@babel/preset-react', {
                runtime: 'automatic' // Use new JSX transform
              }]
            ]
          }
        }
      },
      {
        test: /\.css$/,
        use: [
          'style-loader',
          'css-loader',
          {
            loader: 'postcss-loader',
            options: {
              postcssOptions: {
                plugins: [
                  require('tailwindcss'),
                  require('autoprefixer'),
                ]
              }
            }
          }
        ]
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
      '@hooks': path.resolve(__dirname, 'static/src/js/react/hooks'),
      '@utils': path.resolve(__dirname, 'static/src/js/react/utils'),
      '@services': path.resolve(__dirname, 'static/src/js/react/services'),
    }
  },

  optimization: {
    splitChunks: {
      chunks: 'all',
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          chunks: 'all',
          enforce: true
        }
      }
    }
  },

  devtool: process.env.NODE_ENV === 'development' ? 'eval-source-map' : 'source-map',

  // Development server configuration
  devServer: {
    host: '0.0.0.0',
    port: 3000,
    hot: true,
    headers: {
      "Access-Control-Allow-Origin": "*",
    },
    allowedHosts: 'all',
  },

  externals: {
    // Keep GSAP external since we're loading it via CDN
    'gsap': 'gsap'
  }
};
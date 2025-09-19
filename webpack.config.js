const path = require('path');
const BundleTracker = require('webpack-bundle-tracker');

module.exports = (env, argv) => {
  const isProduction = argv.mode === 'production';
  
  return {
    context: __dirname,
    
    entry: {
      // Single main entry point to avoid complexity
      main: './static/src/js/react/index.js',
    },

    output: {
      path: path.resolve('./static/dist/js/'),
      filename: isProduction ? '[name].[contenthash:8].bundle.js' : '[name].bundle.js',
      publicPath: '/static/dist/js/',
      clean: false, // Don't clean to avoid conflicts
    },

    // Enable caching for faster builds
    cache: {
      type: 'filesystem',
      cacheDirectory: path.resolve(__dirname, '.webpack-cache'),
      buildDependencies: {
        config: [__filename],
      },
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
              ],
              cacheDirectory: true, // Enable Babel caching
            }
          }
        }
      ]
    },

    plugins: [
      new BundleTracker({
        path: __dirname,
        filename: 'webpack-stats.json',
        logTime: true,
        indent: 2
      })
    ],

    resolve: {
      extensions: ['.js', '.jsx'],
      alias: {
        '@': path.resolve(__dirname, 'static/src/js/react'),
        '@components': path.resolve(__dirname, 'static/src/js/react/components'),
      }
    },

    // Optimization settings
    optimization: {
      splitChunks: isProduction ? {
        chunks: 'all',
        cacheGroups: {
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name: 'vendors',
            chunks: 'all',
          },
        },
      } : false,
      minimize: isProduction,
    },

    // Development vs Production settings
    devtool: isProduction ? false : 'eval-cheap-module-source-map',
    
    // Bundle React directly instead of external loading
    // externals: {
    //   'react': 'React',
    //   'react-dom': 'ReactDOM'
    // },

    // Performance and timeout settings
    performance: {
      hints: false,
      maxAssetSize: 1000000, // 1MB
      maxEntrypointSize: 1000000, // 1MB
    },

    // Infrastructure logging for debugging
    infrastructureLogging: {
      level: 'warn',
    },

    // Stats configuration for better error reporting
    stats: {
      errorDetails: true,
      warnings: false,
    }
  };
};
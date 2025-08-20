const path = require('path');

module.exports = {
  mode: 'development',
  
  entry: {
    main: './static/src/js/react/index.js',
  },

  output: {
    path: path.resolve('./static/dist/js/'),
    filename: '[name].bundle.js',
    publicPath: '/static/dist/js/',
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
              '@babel/preset-env',
              '@babel/preset-react'
            ]
          }
        }
      }
    ]
  },

  resolve: {
    extensions: ['.js', '.jsx'],
    alias: {
      '@': path.resolve(__dirname, 'static/src/js/react'),
      '@components': path.resolve(__dirname, 'static/src/js/react/components'),
    }
  },

  externals: {
    'react': 'React',
    'react-dom': 'ReactDOM',
    'framer-motion': 'FramerMotion',
    'axios': 'axios'
  }
};
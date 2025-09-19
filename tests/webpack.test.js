const path = require('path');

module.exports = {
  entry: './static/src/js/react/components/Orders/OrderTracking.jsx',
  mode: 'development',
  output: {
    path: path.resolve('./test-output/'),
    filename: 'test.js',
  },
  module: {
    rules: [
      {
        test: /\.jsx?$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-react']
          }
        }
      }
    ]
  },
  resolve: {
    extensions: ['.js', '.jsx'],
  },
  externals: {
    'react': 'React',
    'react-dom': 'ReactDOM'
  }
};
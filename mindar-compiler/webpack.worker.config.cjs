const path = require('path');

module.exports = {
  entry: './src/image-target/compiler.worker.js',
  output: {
    filename: 'compiler.worker.cjs',
    path: path.resolve(__dirname),
    libraryTarget: 'commonjs2'
  },
  target: 'node',
  mode: 'production',
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: [['@babel/preset-env', { targets: { node: '18' } }]]
          }
        }
      }
    ]
  },
  resolve: {
    extensions: ['.js'],
    alias: {
      '@': path.resolve(__dirname, 'src/image-target')
    }
  }
};
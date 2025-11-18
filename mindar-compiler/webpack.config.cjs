const path = require('path');

module.exports = {
  entry: './compiler.patched.js',
  output: {
    filename: 'compiler.bundled.cjs',
    path: path.resolve(__dirname),
    libraryTarget: 'commonjs2'
  },
  target: 'node',
  mode: 'production'
};
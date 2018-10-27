const path = require('path');

module.exports = {
  entry: './daiseihai/assets/javascript/main.js',
  devtool: 'source-map',
  output: {
    path: path.resolve(__dirname, 'daiseihai/static/'),
    filename: 'bundle.js',
    sourceMapFilename: "bundle.js.map"
  }
};

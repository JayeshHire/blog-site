const path = require('path');

module.exports = {
  // mode: "development",
  entry: './main.js',
  output: {
    filename: 'bundle.js',
    path: path.resolve(__dirname, 'dist'), // Output directory for the bundled file
  }
  // Add loaders and plugins as needed for your project (e.g., Babel for ES6+)
};
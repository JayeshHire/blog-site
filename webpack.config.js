const path = require('path');

module.exports = (env) => {
  const pkg = env.package ;

  return {
    mode: "development",
    entry: `./static/scripts/packages/${pkg}/`,
    output: {
      filename: 'bundle.js',
      path: path.resolve(__dirname, `dist/${pkg}`),
    }
  } ;
} ;

// {
//   mode: "development",
//   entry: './static/scripts/main.js',
//   output: {
//     filename: 'bundle.js',
//     path: path.resolve(__dirname, 'dist/editor'), // Output directory for the bundled file
//   }
//   // Add loaders and plugins as needed for your project (e.g., Babel for ES6+)
// };
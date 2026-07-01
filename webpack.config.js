const path = require('path');

// React / ReactDOM / PropTypes are provided by Dash on the page as globals, so we
// externalize them instead of bundling. Univer imports `react-dom/client` for its
// own isolated root; React 18's global `ReactDOM` UMD exposes `createRoot`, so we
// map that specifier to the same global. Everything else (Univer, rxjs) is bundled.
const externals = {
  react: 'React',
  'react-dom': 'ReactDOM',
  'react-dom/client': 'ReactDOM',
  'prop-types': 'PropTypes',
};

module.exports = (env, argv) => {
  const mode = (argv && argv.mode) || 'production';
  return {
    mode,
    entry: './src/lib/index.js',
    output: {
      path: path.resolve(__dirname, 'dash_univer'),
      filename: 'dash_univer.js',
      library: 'dash_univer',
      libraryTarget: 'window',
      // Dash serves a fixed list of JS files (_js_dist); it can't fetch webpack's
      // on-demand async chunks. Inline them into the single main bundle instead.
      asyncChunks: false,
    },
    externals,
    // Univer is multi-megabyte by nature; the size warning is expected and noisy.
    performance: {hints: false},
    module: {
      rules: [
        {
          test: /\.jsx?$/,
          exclude: /node_modules/,
          use: 'babel-loader',
        },
        {
          test: /\.css$/,
          use: ['style-loader', 'css-loader'],
        },
      ],
    },
    resolve: {
      extensions: ['.js', '.jsx'],
    },
  };
};

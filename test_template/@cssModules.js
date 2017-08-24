    {
        test: /\.scss/,
        exclude: /node_modules/,
        loader: extractCss.extract({
            use: [
                `css-loader?importLoaders=1${isProd ? '' : '&sourceMap'}`,
                `postcss-loader${isProd ? '' : '?sourceMap'}`,
                `resolve-url-loader${isProd ? '' : '?sourceMap'}`,
                `sass-loader${isProd ? '' : '?sourceMap'}`,
            ].join('!'),
        }),
    },
    new webpack.LoaderOptionsPlugin({
        options: {
            postcss: function postcss() {
                const result = [
                    pxtorem({
                        rootValue: 10,
                        unitPrecision: 2,
                        propWhiteList: [],
                        selectorBlackList: [
                            /^html$/,
                            '.old_', // used in unsupported browsers alert
                        ],
                        mediaQuery: false,
                        minPixelValue: 5,
                    }),
                    autoprefixer({
                        diff: false,
                        browsers: ['> 1%', 'last 50 versions', 'Firefox ESR', 'Opera 12.1'],
                    }),
                ];

                if (isProd) {
                    result.push(csso({
                        restructure: false,
                        sourceMap: !isProd,
                        debug: !isProd,
                    }));
                }

                return result;
            },
            htmlLoader: {
                root: path.resolve(__dirname),
                attrs: ['img:src', 'source:src'],
                xhtml: true,
                interpolate: true,
            },
        },
    }),
"use strict";
const path = require("path");
const webpack = require("webpack");
const autoprefixer = require("autoprefixer");
const bundletracker = require("webpack-bundle-tracker");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");

module.exports = (env, argv) => {
    const mode = argv.mode || "development";
    const dev_mode = mode === "development";

    const config = {
        entry: "./assets/src/js/index.js",
        output: {
            filename: "[name]-[contenthash].js",
            path: path.resolve(__dirname, "assets", "webpack_bundles"),
            publicPath: "auto",
            clean: true,
        },
        plugins: [
            new webpack.ProvidePlugin({
                $: "jquery",
                jQuery: "jquery",
            }),
            new bundletracker({
                path: __dirname,
                filename: "webpack-stats.json",
            }),
            new MiniCssExtractPlugin({
                filename: "[name].css",
                chunkFilename: "[id].css",
            }),
        ],
        module: {
            rules: [
                {
                    test: /\.(woff|woff2|eot|ttf|otf)$/i,
                    type: "asset/resource",
                },
                {
                    test: /\.(sa|sc|c)ss$/,
                    use: [
                        {
                            loader: dev_mode
                                ? "style-loader"
                                : MiniCssExtractPlugin.loader,
                        },
                        {
                            loader: "css-loader",
                        },
                        {
                            loader: "postcss-loader",
                            options: {
                                postcssOptions: {
                                    plugins: [autoprefixer],
                                },
                            },
                        },
                        {
                            loader: "sass-loader",
                        },
                    ],
                },
            ],
        },
        devtool: mode === "development" ? "eval-source-map" : false,
    };
    return config;
};

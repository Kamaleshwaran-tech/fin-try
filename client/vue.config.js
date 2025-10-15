const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: true,
  publicPath: process.env.NODE_ENV === 'production' ? './' : '/',
  productionSourceMap: false,
  devServer: {
    port: 8080,
    proxy: {
      // Proxy API calls to Flask backend in development to avoid CORS
      '^/(extract|analyze|visualize)': {
        target: process.env.VUE_APP_API_BASE_URL || 'http://localhost:8000',
        changeOrigin: true,
        ws: false,
      },
    },
  },
})

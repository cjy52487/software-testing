const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    host: '0.0.0.0',
    port: 8080,
    allowedHosts: 'all',
    hot: true,
    open: false,
    client: {
      webSocketURL: 'auto://0.0.0.0:0/ws'
    },
    // ========== 重点：添加以下代理配置 ==========
    proxy: {
      '/api': {
        target: 'http://localhost:5000',  // 指向你的后端地址
        changeOrigin: true,               // 解决跨域问题
        pathRewrite: {
          '^/api': '/api'                 // 保持/api路径不变
        }
      }
    }
    // ==========================================
  }
})
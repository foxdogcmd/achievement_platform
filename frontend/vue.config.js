const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: true,
  
  // 开发服务器配置
  devServer: {
    port: 8080,
    host: '0.0.0.0', // 允许局域网访问
    open: true,
    // 代理配置，解决跨域问题
    proxy: {
      '/api': {
        target: 'http://121.194.211.93:5000',
        changeOrigin: true,
        secure: false
      }
    }
  },
  
  // 生产环境配置：使用绝对路径，避免嵌套路由下静态资源相对路径解析错误
  publicPath: process.env.NODE_ENV === 'production' ? '/' : '/',
  outputDir: 'dist',
  assetsDir: 'static',
  
  // CSS配置
  css: {
    loaderOptions: {
      sass: {
        additionalData: `@import "@/styles/variables.scss";`
      }
    }
  },
  
  // 链式操作配置
  chainWebpack: config => {
    // 设置别名
    config.resolve.alias
      .set('@', require('path').resolve(__dirname, 'src'))
      .set('components', require('path').resolve(__dirname, 'src/components'))
      .set('views', require('path').resolve(__dirname, 'src/views'))
      .set('utils', require('path').resolve(__dirname, 'src/utils'))
      .set('api', require('path').resolve(__dirname, 'src/api'))
  }
})
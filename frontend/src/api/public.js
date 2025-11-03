import axios from 'axios'

// 创建公共API的axios实例，不需要认证
const publicRequest = axios.create({
  baseURL: process.env.NODE_ENV === 'development' ? '/api' : '/api',
  timeout: 10000
})

// 公共API响应拦截器（简化版，不处理认证相关错误）
publicRequest.interceptors.response.use(
  response => {
    return response
  },
  error => {
    console.error('公共API请求失败:', error)
    return Promise.reject(error)
  }
)

// 获取公共成果列表
export function getPublicAchievements(params) {
  return publicRequest({
    url: '/public/achievements',
    method: 'get',
    params
  })
}

// 获取公共统计数据
export function getPublicStatistics() {
  return publicRequest({
    url: '/public/statistics',
    method: 'get'
  })
}

// 获取公共班级列表
export function getPublicClasses() {
  return publicRequest({
    url: '/public/classes',
    method: 'get'
  })
}

// 获取公共系统配置
export function getPublicConfig() {
  return publicRequest({
    url: '/public/config',
    method: 'get'
  })
}
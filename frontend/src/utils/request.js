import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { getToken } from './auth'
import router from '@/router'

// 后端服务地址（统一前端请求入口）
export const API_BASE = 'http://121.194.211.93:5000/api'

// 创建axios实例
const service = axios.create({
  baseURL: API_BASE,
  timeout: 10000
})

// 请求拦截器
service.interceptors.request.use(
  config => {
    // 添加token到请求头
    const token = getToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  response => {
    return response
  },
  async error => {
    const { response } = error
    
    if (response) {
      const { status, data } = response
      
      switch (status) {
        case 401: {
          // Token过期或无效
          const userStore = useUserStore()
          
          // 尝试刷新token
          try {
            await userStore.refreshAccessToken()
            // 重新发送原请求
            return service.request(error.config)
          } catch (refreshError) {
            // 刷新失败，跳转到登录页
            ElMessage.error('登录已过期，请重新登录')
            userStore.logout()
            router.push('/login')
            return Promise.reject(refreshError)
          }
        }
          
        case 403:
          ElMessage.error(data.message || '权限不足')
          break
          
        case 404:
          ElMessage.error(data.message || '请求的资源不存在')
          break
          
        case 422:
          ElMessage.error(data.message || '请求参数错误')
          break
          
        case 500:
          ElMessage.error(data.message || '服务器内部错误')
          break
          
        default:
          ElMessage.error(data.message || `请求失败 (${status})`)
      }
    } else {
      // 网络错误
      ElMessage.error('网络连接失败，请检查网络设置')
    }
    
    return Promise.reject(error)
  }
)

export default service
import request from '@/utils/request'

/**
 * 用户登录
 */
export function login(data) {
  return request({
    url: '/auth/login',
    method: 'post',
    data
  })
}

/**
 * 用户注册
 */
export function register(data) {
  return request({
    url: '/auth/register',
    method: 'post',
    data
  })
}

/**
 * 刷新访问令牌
 */
export function refreshToken() {
  const refreshTokenValue = localStorage.getItem('refresh_token')
  return request({
    url: '/auth/refresh',
    method: 'post',
    headers: {
      Authorization: `Bearer ${refreshTokenValue}`
    }
  })
}

/**
 * 获取用户信息
 */
export function getUserProfile() {
  return request({
    url: '/auth/profile',
    method: 'get'
  })
}

/**
 * 更新用户个人信息（仅姓名）
 */
export function updateUserProfile(data) {
  return request({
    url: '/auth/profile',
    method: 'put',
    data
  })
}

/**
 * 修改密码
 */
export function changePassword(data) {
  return request({
    url: '/auth/change_password',
    method: 'put',
    data
  })
}

/**
 * 解析 CAS 注册令牌
 */
export function getCasTokenInfo(token) {
  return request({
    url: '/auth/cas/token_info',
    method: 'get',
    params: { token }
  })
}
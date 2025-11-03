import { defineStore } from 'pinia'
import request from '@/utils/request'
import { getPublicConfig } from '@/api/public'
import { useUserStore } from '@/stores/user'

// 获取系统配置的API函数
const getSystemConfig = () => {
  return request({
    url: '/config',
    method: 'get'
  })
}

export const useConfigStore = defineStore('config', {
  state: () => ({
    config: {
      system_name: '学生成果登记与管理系统',
      max_file_size: 10,
      achievement_types: [
        { value: 'paper', label: '论文' },
        { value: 'competition', label: '竞赛' },
        { value: 'project', label: '项目' },
        { value: 'honor', label: '荣誉' }
      ],
      achievement_levels: [
        { value: 'school', label: '校级' },
        { value: 'province', label: '省部级' },
        { value: 'national', label: '国家级' }
      ],
      default_password: 'student123'
    },
    loaded: false,
    lastUpdated: null
  }),

  getters: {
    // 获取成果类型选项
    achievementTypeOptions: (state) => {
      return state.config.achievement_types.map(type => ({
        label: type.label,
        value: type.value
      }))
    },

    // 获取获奖级别选项
    achievementLevelOptions: (state) => {
      return state.config.achievement_levels.map(level => ({
        label: level.label,
        value: level.value
      }))
    },

    // 根据值获取类型标签
    getTypeLabel: (state) => {
      return (value) => {
        const type = state.config.achievement_types.find(t => t.value === value)
        return type ? type.label : value
      }
    },

    // 根据值获取级别标签
    getLevelLabel: (state) => {
      return (value) => {
        const level = state.config.achievement_levels.find(l => l.value === value)
        if (level) return level.label
        const fallback = { school: '校级', province: '省部级', national: '国家级' }
        return fallback[value] || value
      }
    },

    // 获取系统名称
    systemName: (state) => state.config.system_name,

    // 获取文件上传限制
    maxFileSize: (state) => state.config.max_file_size,

    // 获取默认密码
    defaultPassword: (state) => state.config.default_password
  },

  actions: {
    // 加载系统配置
    async loadConfig(force = false) {
      // 如果已加载且不是强制刷新，则跳过
      if (this.loaded && !force) return
      
      try {
        const userStore = useUserStore()
        let response
        if (userStore.isLoggedIn) {
          response = await getSystemConfig()
        } else {
          // 未登录使用公共配置接口，避免401拦截导致跳转登录
          response = await getPublicConfig()
        }
        this.config = response.data.config
        this.loaded = true
        this.lastUpdated = Date.now()
      } catch (error) {
        console.error('加载系统配置失败:', error)
        // 使用默认配置，标记为已加载以避免重复请求
        this.loaded = true
        this.lastUpdated = Date.now()
      }
    },

    // 更新配置
    updateConfig(newConfig) {
      this.config = { ...this.config, ...newConfig }
    },

    // 强制刷新配置
    async refreshConfig() {
      await this.loadConfig(true)
    },

    // 检查配置是否需要刷新（超过5分钟自动刷新）
    shouldRefresh() {
      if (!this.lastUpdated) return true
      const fiveMinutes = 5 * 60 * 1000
      return Date.now() - this.lastUpdated > fiveMinutes
    },

    // 智能加载配置（根据时间自动判断是否需要刷新）
    async smartLoadConfig() {
      if (!this.loaded || this.shouldRefresh()) {
        await this.refreshConfig()
      }
    },

    // 重置配置
    resetConfig() {
      this.loaded = false
      this.lastUpdated = null
      this.config = {
        system_name: '学生成果登记与管理系统',
        max_file_size: 10,
        achievement_types: [
          { value: 'paper', label: '论文' },
          { value: 'competition', label: '竞赛' },
          { value: 'project', label: '项目' },
          { value: 'honor', label: '荣誉' }
        ],
        achievement_levels: [
          { value: 'school', label: '校级' },
          { value: 'province', label: '省部级' },
          { value: 'national', label: '国家级' }
        ],
        default_password: 'student123'
      }
    }
  }
})
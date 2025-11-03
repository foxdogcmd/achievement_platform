<template>
  <div class="admin-dashboard">
    <div class="welcome-card">
      <h2>欢迎，{{ userStore.userName }}管理员！</h2>
      <p>这里是系统管理控制台，您可以管理用户、配置系统、监控数据。</p>
    </div>
    
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card users">
          <div class="stat-content">
            <div class="stat-number">{{ statistics.total_users || 0 }}</div>
            <div class="stat-label">总用户数</div>
          </div>
          <el-icon class="stat-icon"><User /></el-icon>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card achievements">
          <div class="stat-content">
            <div class="stat-number">{{ statistics.total_achievements || 0 }}</div>
            <div class="stat-label">总成果数</div>
          </div>
          <el-icon class="stat-icon"><Trophy /></el-icon>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card classes">
          <div class="stat-content">
            <div class="stat-number">{{ statistics.total_classes || 0 }}</div>
            <div class="stat-label">班级数量</div>
          </div>
          <el-icon class="stat-icon"><School /></el-icon>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card pending">
          <div class="stat-content">
            <div class="stat-number">{{ statistics.pending_achievements || 0 }}</div>
            <div class="stat-label">待审核成果</div>
          </div>
          <el-icon class="stat-icon"><Clock /></el-icon>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" class="chart-row">
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <span>用户角色分布</span>
          </template>
          <div ref="userChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <span>成果状态分布</span>
          </template>
          <div ref="achievementChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" class="recent-section">
      <el-col :span="12">
        <el-card class="recent-card">
          <template #header>
            <div class="card-header">
              <span>最新用户</span>
              <el-button type="primary" size="small" @click="$router.push('/admin/users')">
                查看全部
              </el-button>
            </div>
          </template>
          <div v-if="recentUsers.length === 0" class="empty-state">
            <el-icon size="48"><User /></el-icon>
            <p>暂无新用户</p>
          </div>
          <div v-else class="recent-list">
            <div 
              v-for="user in recentUsers" 
              :key="user.user_id" 
              class="recent-item"
            >
              <div class="item-info">
                <div class="item-title">{{ user.name }}</div>
                <div class="item-meta">
                  <el-tag :type="getRoleTagType(user.role)" size="small">
                    {{ getRoleDisplay(user.role) }}
                  </el-tag>
                  <span class="item-time">{{ user.username }}</span>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="recent-card">
          <template #header>
            <div class="card-header">
              <span>最新成果</span>
              <el-button type="primary" size="small" @click="$router.push('/admin/monitor')">
                查看全部
              </el-button>
            </div>
          </template>
          <div v-if="recentAchievements.length === 0" class="empty-state">
            <el-icon size="48"><Trophy /></el-icon>
            <p>暂无新成果</p>
          </div>
          <div v-else class="recent-list">
            <div 
              v-for="achievement in recentAchievements" 
              :key="achievement.achievement_id" 
              class="recent-item"
            >
              <div class="item-info">
                <div class="item-title">{{ achievement.title }}</div>
                <div class="item-meta">
                  <el-tag :type="getTypeTagType(achievement.type)" size="small">
                    {{ getTypeDisplay(achievement.type) }}
                  </el-tag>
                  <span class="item-time">{{ formatTime(achievement.created_at) }}</span>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-card class="quick-actions">
      <template #header>
        <span>快速操作</span>
      </template>
      <el-row :gutter="20">
        <el-col :span="3">
          <el-button type="primary" @click="$router.push('/admin/users')" block size="large">
            <el-icon><User /></el-icon>
            用户管理
          </el-button>
        </el-col>
        <el-col :span="3">
          <el-button @click="$router.push('/admin/config')" block size="large">
            <el-icon><Setting /></el-icon>
            系统配置
          </el-button>
        </el-col>
        <el-col :span="3">
          <el-button @click="$router.push('/display')" block size="large" type="success">
            <el-icon><DataBoard /></el-icon>
            成果展示
          </el-button>
        </el-col>
        <el-col :span="3">
          <el-button @click="$router.push('/admin/monitor')" block size="large">
            <el-icon><Monitor /></el-icon>
            数据监控
          </el-button>
        </el-col>
        <el-col :span="3">
          <el-button @click="refreshData" block size="large">
            <el-icon><Refresh /></el-icon>
            刷新数据
          </el-button>
        </el-col>
        <el-col :span="3">
          <el-button @click="exportAllData" block size="large">
            <el-icon><Download /></el-icon>
            导出数据
          </el-button>
        </el-col>
        <el-col :span="6">
          <el-button @click="showSystemInfo" block size="large">
            <el-icon><InfoFilled /></el-icon>
            系统信息
          </el-button>
        </el-col>
      </el-row>
    </el-card>
    
    <!-- 系统信息对话框 -->
    <el-dialog
      v-model="systemInfoVisible"
      title="系统信息"
      width="600px"
    >
      <el-descriptions :column="2" border>
        <el-descriptions-item label="系统版本">v1.0.0</el-descriptions-item>
        <el-descriptions-item label="数据库">PostgreSQL</el-descriptions-item>
        <el-descriptions-item label="后端框架">Flask</el-descriptions-item>
        <el-descriptions-item label="前端框架">Vue 3</el-descriptions-item>
        <el-descriptions-item label="UI组件">Element Plus</el-descriptions-item>
        <el-descriptions-item label="部署环境">开发环境</el-descriptions-item>
        <el-descriptions-item label="最后更新" :span="2">{{ new Date().toLocaleString('zh-CN') }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { useUserStore } from '@/stores/user'
import { useConfigStore } from '@/stores/config'
import { getAdminStatistics, getAllUsers, getAllAchievements, exportData } from '@/api/admin'
import { ElMessage } from 'element-plus'
import { 
  User, 
  Trophy, 
  School,
  Clock,
  Setting,
  Monitor,
  Refresh,
  Download,
  InfoFilled,
  DataBoard
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'

const userStore = useUserStore()
const configStore = useConfigStore()

// 数据
const statistics = reactive({
  total_users: 0,
  total_achievements: 0,
  total_classes: 0,
  pending_achievements: 0,
  by_role: {},
  by_status: {}
})

const recentUsers = ref([])
const recentAchievements = ref([])
const systemInfoVisible = ref(false)

// 图表引用
const userChartRef = ref()
const achievementChartRef = ref()
let userChart = null
let achievementChart = null

// 角色和类型映射
const roleMap = {
  'student': '学生',
  'team_leader': '队长',
  'admin': '管理员'
}

// 获取统计数据
const fetchStatistics = async () => {
  try {
    const response = await getAdminStatistics()
    Object.assign(statistics, response.data.statistics)
    
    // 更新图表
    await nextTick()
    updateCharts()
  } catch (error) {
    ElMessage.error('获取统计数据失败')
  }
}

// 获取最新用户
const fetchRecentUsers = async () => {
  try {
    const response = await getAllUsers({ page: 1, per_page: 5, sort_by: 'created_at', sort_order: 'desc' })
    recentUsers.value = response.data.users || []
  } catch (error) {
    console.error('获取最新用户失败:', error)
  }
}

// 获取最新成果
const fetchRecentAchievements = async () => {
  try {
    const response = await getAllAchievements({ page: 1, per_page: 5, sort_by: 'created_at', sort_order: 'desc' })
    recentAchievements.value = response.data.achievements || []
  } catch (error) {
    console.error('获取最新成果失败:', error)
  }
}

// 更新图表
const updateCharts = () => {
  updateUserChart()
  updateAchievementChart()
}

// 更新用户角色分布图表
const updateUserChart = () => {
  if (!userChart) {
    userChart = echarts.init(userChartRef.value)
  }
  
  const data = Object.entries(statistics.by_role).map(([key, value]) => ({
    name: roleMap[key] || key,
    value
  }))
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    series: [{
      name: '用户角色',
      type: 'pie',
      radius: '70%',
      data,
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }]
  }
  
  userChart.setOption(option)
}

// 更新成果状态分布图表
const updateAchievementChart = () => {
  if (!achievementChart) {
    achievementChart = echarts.init(achievementChartRef.value)
  }
  
  const statusData = [
    { name: '待审核', value: statistics.pending_achievements },
    { name: '已通过', value: statistics.by_status?.approved || 0 },
    { name: '已退回', value: statistics.by_status?.returned || 0 },
    { name: '已拒绝', value: statistics.by_status?.rejected || 0 }
  ]
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    series: [{
      name: '成果状态',
      type: 'pie',
      radius: '70%',
      data: statusData,
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }]
  }
  
  achievementChart.setOption(option)
}

// 刷新数据
const refreshData = async () => {
  await Promise.all([
    fetchStatistics(),
    fetchRecentUsers(),
    fetchRecentAchievements()
  ])
  ElMessage.success('数据已刷新')
}

// 导出所有数据
const exportAllData = async () => {
  try {
    const response = await exportData({ type: 'all', format: 'excel' })
    // 处理文件下载
    const blob = new Blob([response.data])
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `系统数据导出_${new Date().toISOString().split('T')[0]}.xlsx`
    link.click()
    window.URL.revokeObjectURL(url)
    ElMessage.success('数据导出成功')
  } catch (error) {
    ElMessage.error('导出数据失败')
  }
}

// 显示系统信息
const showSystemInfo = () => {
  systemInfoVisible.value = true
}

// 获取角色显示文本
const getRoleDisplay = (role) => roleMap[role] || role

// 获取类型显示文本
const getTypeDisplay = (type) => configStore.getTypeLabel(type)

// 获取角色标签类型
const getRoleTagType = (role) => {
  const roleColors = {
    'student': '',
    'team_leader': 'success',
    'admin': 'danger'
  }
  return roleColors[role] || ''
}

// 获取类型标签类型
const getTypeTagType = (type) => {
  const typeColors = {
    'paper': '',
    'competition': 'success',
    'project': 'warning',
    'honor': 'danger'
  }
  return typeColors[type] || ''
}

// 格式化时间
const formatTime = (dateTime) => {
  if (!dateTime) return '-'
  const date = new Date(dateTime)
  const now = new Date()
  const diff = now - date
  
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  return date.toLocaleDateString('zh-CN')
}

// 组件挂载时获取数据
onMounted(async () => {
  await configStore.smartLoadConfig()
  refreshData()
})
</script>

<style lang="scss" scoped>
.admin-dashboard {
  .welcome-card {
    background: var(--bg-primary);
    color: var(--text-primary);
    border: 1px solid var(--border-color);
    padding: 30px;
    border-radius: 8px;
    margin-bottom: 20px;
    box-shadow: 0 4px 16px var(--shadow-light);
    transition: background-color 0.3s ease, color 0.3s ease, box-shadow 0.3s ease;
    
    h2 {
      margin: 0 0 10px 0;
      color: var(--text-primary);
    }
    
    p {
      margin: 0;
      color: var(--text-secondary);
    }
  }
  
  .stats-row {
    margin-bottom: 20px;
  }
  
  .stat-card {
    position: relative;
    overflow: hidden;
    
    .stat-content {
      text-align: center;
      position: relative;
      z-index: 2;
      
      .stat-number {
        font-size: 36px;
        font-weight: bold;
        margin-bottom: 8px;
      }
      
      .stat-label {
        font-size: 14px;
        opacity: 0.8;
      }
    }
    
    .stat-icon {
      position: absolute;
      right: 20px;
      top: 50%;
      transform: translateY(-50%);
      font-size: 40px;
      opacity: 0.3;
    }
    
    &.users {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
    }
    
    &.achievements {
      background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
      color: white;
    }
    
    &.classes {
      background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
      color: white;
    }
    
    &.pending {
      background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
      color: white;
    }
  }
  
  .chart-row {
    margin-bottom: 20px;
  }
  
  .chart-card {
    .chart-container {
      height: 300px;
      width: 100%;
      background: var(--bg-primary);
      border: 1px solid var(--border-color);
      border-radius: 8px;
    }
  }
  
  .recent-section {
    margin-bottom: 20px;
  }
  
  .recent-card {
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    
    .empty-state {
      text-align: center;
      padding: 40px 20px;
      color: var(--text-secondary);
      
      .el-icon {
        margin-bottom: 16px;
        color: var(--text-tertiary);
      }
      
      p {
        margin: 0;
        font-size: 14px;
        color: var(--text-secondary);
      }
    }
    
    .recent-list {
      .recent-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 12px 0;
        border-bottom: 1px solid var(--border-color);
        
        &:last-child {
          border-bottom: none;
        }
        
        .item-info {
          flex: 1;
          
          .item-title {
            font-weight: 500;
            color: var(--text-primary);
            margin-bottom: 4px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
          }
          
          .item-meta {
            display: flex;
            align-items: center;
            gap: 8px;
            
            .item-time {
              font-size: 12px;
              color: var(--text-secondary);
            }
          }
        }
      }
    }
  }
  
  .quick-actions {
    .el-button {
      height: 60px;
      font-size: 16px;
    }
  }
}
</style>
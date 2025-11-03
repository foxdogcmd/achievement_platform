<template>
  <div class="leader-dashboard">
    <div class="welcome-card">
      <h2>欢迎，{{ userStore.userName }}队长！</h2>
      <p>这里是队长管理控制台，您可以审核成果、管理团队数据。</p>
    </div>
    
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card pending">
          <div class="stat-content">
            <div class="stat-number">{{ statistics.pending || 0 }}</div>
            <div class="stat-label">待审核</div>
          </div>
          <el-icon class="stat-icon"><Clock /></el-icon>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card total">
          <div class="stat-content">
            <div class="stat-number">{{ statistics.total || 0 }}</div>
            <div class="stat-label">本队总成果</div>
          </div>
          <el-icon class="stat-icon"><Trophy /></el-icon>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card approved">
          <div class="stat-content">
            <div class="stat-number">{{ statistics.approved || 0 }}</div>
            <div class="stat-label">已通过</div>
          </div>
          <el-icon class="stat-icon"><Check /></el-icon>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card returned">
          <div class="stat-content">
            <div class="stat-number">{{ statistics.returned || 0 }}</div>
            <div class="stat-label">已退回</div>
          </div>
          <el-icon class="stat-icon"><RefreshLeft /></el-icon>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" class="chart-row">
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <span>本队成果类型分布</span>
          </template>
          <div ref="typeChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <span>审核状态分布</span>
          </template>
          <div ref="statusChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" class="recent-section">
      <el-col :span="12">
        <el-card class="recent-card">
          <template #header>
            <div class="card-header">
              <span>待审核成果</span>
              <el-button type="primary" size="small" @click="$router.push('/leader/audit')">
                查看全部
              </el-button>
            </div>
          </template>
          <div v-if="recentPending.length === 0" class="empty-state">
            <el-icon size="48"><DocumentChecked /></el-icon>
            <p>暂无待审核成果</p>
          </div>
          <div v-else class="recent-list">
            <div 
              v-for="item in recentPending" 
              :key="item.achievement_id" 
              class="recent-item"
              @click="quickAudit(item)"
            >
              <div class="item-info">
                <div class="item-title">{{ item.title }}</div>
                <div class="item-meta">
                  <el-tag :type="getTypeTagType(item.type)" size="small">
                    {{ getTypeDisplay(item.type) }}
                  </el-tag>
                  <span class="item-time">{{ formatTime(item.created_at) }}</span>
                </div>
              </div>
              <el-icon class="item-arrow"><ArrowRight /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="recent-card">
          <template #header>
            <div class="card-header">
              <span>最近审核记录</span>
              <el-button type="primary" size="small" @click="$router.push('/leader/manage')">
                查看全部
              </el-button>
            </div>
          </template>
          <div v-if="recentAudits.length === 0" class="empty-state">
            <el-icon size="48"><List /></el-icon>
            <p>暂无审核记录</p>
          </div>
          <div v-else class="recent-list">
            <div 
              v-for="item in recentAudits" 
              :key="item.log_id" 
              class="recent-item"
            >
              <div class="item-info">
                <div class="item-title">{{ item.achievement_title }}</div>
                <div class="item-meta">
                  <el-tag :type="getActionTagType(item.action)" size="small">
                    {{ getActionDisplay(item.action) }}
                  </el-tag>
                  <span class="item-time">{{ formatTime(item.audit_time) }}</span>
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
        <el-col :span="4">
          <el-button type="primary" @click="$router.push('/leader/audit')" block size="large">
            <el-icon><DocumentChecked /></el-icon>
            成果审核
          </el-button>
        </el-col>
        <el-col :span="4">
          <el-button @click="$router.push('/leader/manage')" block size="large">
            <el-icon><Setting /></el-icon>
            成果管理
          </el-button>
        </el-col>
        <el-col :span="4">
          <el-button @click="$router.push('/display')" block size="large" type="success">
            <el-icon><DataBoard /></el-icon>
            成果展示
          </el-button>
        </el-col>
        <el-col :span="4">
          <el-button @click="refreshData" block size="large">
            <el-icon><Refresh /></el-icon>
            刷新数据
          </el-button>
        </el-col>
        <el-col :span="4">
          <el-button @click="exportReport" block size="large">
            <el-icon><Download /></el-icon>
            导出报表
          </el-button>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useConfigStore } from '@/stores/config'
import { getLeaderStatistics, getPendingAchievements, getAuditLogs, exportAchievements } from '@/api/leader'
import { ElMessage } from 'element-plus'
import { 
  Clock, 
  Trophy, 
  Check, 
  RefreshLeft,
  DocumentChecked,
  List,
  ArrowRight,
  Setting,
  Refresh,
  Download,
  DataBoard
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'

const router = useRouter()
const userStore = useUserStore()
const configStore = useConfigStore()

// 数据
const statistics = reactive({
  pending: 0,
  total: 0,
  approved: 0,
  returned: 0,
  rejected: 0,
  by_type: {},
  by_status: {}
})

const recentPending = ref([])
const recentAudits = ref([])

// 图表引用
const typeChartRef = ref()
const statusChartRef = ref()
let typeChart = null
let statusChart = null

// 状态映射
const actionMap = {
  'approve': '通过',
  'return': '退回',
  'reject': '拒绝'
}

// 获取统计数据
const fetchStatistics = async () => {
  try {
    const response = await getLeaderStatistics()
    Object.assign(statistics, response.data.statistics)
    
    // 更新图表
    await nextTick()
    updateCharts()
  } catch (error) {
    ElMessage.error('获取统计数据失败')
  }
}

// 获取待审核成果
const fetchRecentPending = async () => {
  try {
    const response = await getPendingAchievements({ page: 1, per_page: 5 })
    recentPending.value = response.data.achievements || []
  } catch (error) {
    console.error('获取待审核成果失败:', error)
  }
}

// 获取最近审核记录
const fetchRecentAudits = async () => {
  try {
    const response = await getAuditLogs({ page: 1, per_page: 5 })
    recentAudits.value = response.data.logs || []
  } catch (error) {
    console.error('获取审核记录失败:', error)
  }
}

// 更新图表
const updateCharts = () => {
  updateTypeChart()
  updateStatusChart()
}

// 更新类型分布图表
const updateTypeChart = () => {
  if (!typeChart) {
    typeChart = echarts.init(typeChartRef.value)
  }
  
  const data = Object.entries(statistics.by_type).map(([key, value]) => ({
    name: configStore.getTypeLabel(key),
    value
  }))
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    series: [{
      name: '成果类型',
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
  
  typeChart.setOption(option)
}

// 更新状态分布图表
const updateStatusChart = () => {
  if (!statusChart) {
    statusChart = echarts.init(statusChartRef.value)
  }
  
  const statusData = [
    { name: '待审核', value: statistics.pending },
    { name: '已通过', value: statistics.approved },
    { name: '已退回', value: statistics.returned },
    { name: '已拒绝', value: statistics.rejected }
  ]
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    series: [{
      name: '审核状态',
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
  
  statusChart.setOption(option)
}

// 快速审核
const quickAudit = (item) => {
  router.push(`/leader/audit?id=${item.achievement_id}`)
}

// 刷新数据
const refreshData = async () => {
  await Promise.all([
    fetchStatistics(),
    fetchRecentPending(),
    fetchRecentAudits()
  ])
  ElMessage.success('数据已刷新')
}

// 导出报表
const exportReport = async () => {
  try {
    const response = await exportAchievements({ format: 'excel' })
    // 处理文件下载
    const blob = new Blob([response.data])
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `成果报表_${new Date().toISOString().split('T')[0]}.xlsx`
    link.click()
    window.URL.revokeObjectURL(url)
    ElMessage.success('报表导出成功')
  } catch (error) {
    ElMessage.error('导出报表失败')
  }
}

// 获取类型显示文本
const getTypeDisplay = (type) => configStore.getTypeLabel(type)

// 获取操作显示文本
const getActionDisplay = (action) => actionMap[action] || action

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

// 获取操作标签类型
const getActionTagType = (action) => {
  const actionColors = {
    'approve': 'success',
    'return': 'warning',
    'reject': 'danger'
  }
  return actionColors[action] || ''
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
.leader-dashboard {
  .welcome-card {
    background: var(--bg-primary);
    padding: 30px;
    border-radius: 8px;
    margin-bottom: 20px;
    border: 1px solid var(--border-color);
    box-shadow: 0 2px 4px var(--shadow-light);
    
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
    
    &.pending {
      background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
      color: white;
    }
    
    &.total {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
    }
    
    &.approved {
      background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
      color: white;
    }
    
    &.returned {
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
      color: #909399;
      
      .el-icon {
        margin-bottom: 16px;
        color: #c0c4cc;
      }
      
      p {
        margin: 0;
        font-size: 14px;
      }
    }
    
    .recent-list {
      .recent-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 12px 0;
        border-bottom: 1px solid #f0f0f0;
        cursor: pointer;
        transition: background-color 0.3s;
        
        &:hover {
          background-color: #f5f7fa;
        }
        
        &:last-child {
          border-bottom: none;
        }
        
        .item-info {
          flex: 1;
          
          .item-title {
            font-weight: 500;
            color: #303133;
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
              color: #909399;
            }
          }
        }
        
        .item-arrow {
          color: #c0c4cc;
          font-size: 16px;
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
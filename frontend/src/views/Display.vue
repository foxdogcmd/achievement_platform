<template>
  <div class="display-container" :class="{ 'dark-mode': isDarkMode }">
    <!-- 主题切换按钮 -->
    <ThemeToggle />
    
    <!-- 页面头部 -->
    <div class="header">
      <h1 class="title">成果展示</h1>
      <p class="subtitle">优秀学生成果展示平台</p>
    </div>
    
    <!-- 主要内容区域 -->
    <div class="main-content">
      <!-- 筛选条件 -->
      <el-card class="filter-card" shadow="never">
        <div class="filter-section">
          <el-row :gutter="16">
            <el-col :span="6">
              <el-select v-model="filters.type" placeholder="成果类型" clearable @change="fetchAchievements">
                <el-option label="全部类型" value="" />
                <el-option 
                  v-for="type in achievementTypes" 
                  :key="type.value" 
                  :label="type.label" 
                  :value="type.value" 
                />
              </el-select>
            </el-col>
            <el-col :span="6">
              <el-select v-model="filters.level" placeholder="获奖级别" clearable @change="fetchAchievements">
                <el-option label="全部级别" value="" />
                <el-option 
                  v-for="level in achievementLevels" 
                  :key="level.value" 
                  :label="level.label" 
                  :value="level.value" 
                />
              </el-select>
            </el-col>
            <el-col :span="6">
              <el-select v-model="filters.class_id" placeholder="所属班级" clearable @change="fetchAchievements">
                <el-option label="全部班级" value="" />
                <el-option 
                  v-for="cls in classes" 
                  :key="cls.class_id" 
                  :label="cls.class_name" 
                  :value="cls.class_id" 
                />
              </el-select>
            </el-col>
            <el-col :span="6">
              <el-select v-model="filters.year" placeholder="获奖年份" clearable @change="fetchAchievements">
                <el-option label="全部年份" value="" />
                <el-option 
                  v-for="year in availableYears" 
                  :key="year" 
                  :label="year + '年'" 
                  :value="year" 
                />
              </el-select>
            </el-col>
          </el-row>
        </div>
      </el-card>
      
      <!-- 视图切换标签 -->
      <el-card class="content-card" shadow="never">
        <el-tabs v-model="activeTab" @tab-change="handleTabChange">
          <!-- 列表视图 -->
          <el-tab-pane label="列表视图" name="list">
            <div v-loading="loading" class="list-view">
              <div v-if="achievements.length === 0" class="empty-state">
                <el-empty description="暂无公开成果数据" />
              </div>
              <div v-else class="achievement-grid">
                <div 
                  v-for="achievement in achievements" 
                  :key="achievement.achievement_id"
                  class="achievement-card"
                >
                  <el-card shadow="hover" class="achievement-item" @click="viewDetail(achievement)">
                    <div class="achievement-header">
                      <h3 class="achievement-title">{{ achievement.title }}</h3>
                      <div class="achievement-tags">
                        <el-tag :type="getTypeTagType(achievement.type)" size="small">
                          {{ getTypeDisplay(achievement.type) }}
                        </el-tag>
                        <el-tag :type="getLevelTagType(achievement.level)" size="small">
                          {{ getLevelDisplay(achievement.level) }}
                        </el-tag>
                      </div>
                    </div>
                    <div class="achievement-info">
                      <div class="info-item">
                        <el-icon><Calendar /></el-icon>
                        <span>{{ formatDate(achievement.award_date) }}</span>
                      </div>
                      <div class="info-item">
                        <el-icon><School /></el-icon>
                        <span>{{ achievement.class_name }}</span>
                      </div>
                      <div v-if="achievement.supervisor" class="info-item">
                        <el-icon><User /></el-icon>
                        <span>指导教师：{{ achievement.supervisor }}</span>
                      </div>
                      <div v-if="achievement.members && achievement.members.length > 0" class="info-item">
                        <el-icon><UserFilled /></el-icon>
                        <span>成员：{{ achievement.members.join('、') }}</span>
                      </div>
                    </div>
                  </el-card>
                </div>
              </div>
              
              <!-- 分页 -->
              <div v-if="pagination.total > 0" class="pagination-wrapper">
                <el-pagination
                  v-model:current-page="pagination.page"
                  v-model:page-size="pagination.per_page"
                  :page-sizes="[12, 24, 48]"
                  :total="pagination.total"
                  layout="total, sizes, prev, pager, next, jumper"
                  @size-change="handleSizeChange"
                  @current-change="handleCurrentChange"
                />
              </div>
            </div>
          </el-tab-pane>
          
          <!-- 图表视图 -->
          <el-tab-pane label="图表视图" name="chart">
            <div v-loading="statisticsLoading" class="chart-view">
              <div v-if="!statistics.total_count" class="empty-state">
                <el-empty description="暂无统计数据" />
              </div>
              <div v-else class="charts-container">
                <!-- 统计概览 -->
                <el-row :gutter="16" class="stats-overview">
                  <el-col :span="6">
                    <el-card shadow="hover" class="stat-card">
                      <div class="stat-content">
                        <div class="stat-number">{{ statistics.total_count }}</div>
                        <div class="stat-label">总成果数</div>
                      </div>
                    </el-card>
                  </el-col>
                  <el-col :span="6">
                    <el-card shadow="hover" class="stat-card">
                      <div class="stat-content">
                        <div class="stat-number">{{ statistics.by_type?.length || 0 }}</div>
                        <div class="stat-label">成果类型</div>
                      </div>
                    </el-card>
                  </el-col>
                  <el-col :span="6">
                    <el-card shadow="hover" class="stat-card">
                      <div class="stat-content">
                        <div class="stat-number">{{ statistics.by_year?.length || 0 }}</div>
                        <div class="stat-label">涉及年份</div>
                      </div>
                    </el-card>
                  </el-col>
                  <el-col :span="6">
                    <el-card shadow="hover" class="stat-card">
                      <div class="stat-content">
                        <div class="stat-number">{{ statistics.by_class?.length || 0 }}</div>
                        <div class="stat-label">参与班级</div>
                      </div>
                    </el-card>
                  </el-col>
                </el-row>
                
                <!-- 图表区域 -->
                <el-row :gutter="16" class="charts-row">
                  <!-- 类型分布饼图 -->
                  <el-col :span="8">
                    <el-card shadow="hover" class="chart-card">
                      <template #header>
                        <div class="chart-header">
                          <span>成果类型分布</span>
                        </div>
                      </template>
                      <div ref="typeChartRef" class="chart-container"></div>
                    </el-card>
                  </el-col>
                  
                  <!-- 级别分布饼图 -->
                  <el-col :span="8">
                    <el-card shadow="hover" class="chart-card">
                      <template #header>
                        <div class="chart-header">
                          <span>获奖级别分布</span>
                        </div>
                      </template>
                      <div ref="levelChartRef" class="chart-container"></div>
                    </el-card>
                  </el-col>
                  
                  <!-- 年度趋势折线图 -->
                  <el-col :span="8">
                    <el-card shadow="hover" class="chart-card">
                      <template #header>
                        <div class="chart-header">
                          <span>年度趋势</span>
                        </div>
                      </template>
                      <div ref="yearChartRef" class="chart-container"></div>
                    </el-card>
                  </el-col>
                </el-row>
                
                <!-- 班级对比柱状图 -->
                <el-row :gutter="16">
                  <el-col :span="24">
                    <el-card shadow="hover" class="chart-card">
                      <template #header>
                        <div class="chart-header">
                          <span>班级成果对比（前10名）</span>
                        </div>
                      </template>
                      <div ref="classChartRef" class="chart-container-large"></div>
                    </el-card>
                  </el-col>
                </el-row>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </el-card>
    </div>
    
    <!-- 成果详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="成果详情"
      width="800px"
      :before-close="closeDetailDialog"
    >
      <div v-if="currentAchievement" class="achievement-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="成果名称" :span="2">
            {{ currentAchievement.title }}
          </el-descriptions-item>
          <el-descriptions-item label="类型">
            <el-tag :type="getTypeTagType(currentAchievement.type)">
              {{ getTypeDisplay(currentAchievement.type) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="级别">
            <el-tag :type="getLevelTagType(currentAchievement.level)">
              {{ getLevelDisplay(currentAchievement.level) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="获奖时间">
            {{ formatDate(currentAchievement.award_date) }}
          </el-descriptions-item>
          <el-descriptions-item label="所属班级">
            {{ currentAchievement.class_name || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="指导教师">
            {{ currentAchievement.supervisor || '无' }}
          </el-descriptions-item>
          <el-descriptions-item v-if="currentAchievement.members && currentAchievement.members.length" label="团队成员" :span="2">
            {{ currentAchievement.members.join('、') }}
          </el-descriptions-item>
          <el-descriptions-item v-if="currentAchievement.description" label="简介/描述" :span="2">
            {{ currentAchievement.description }}
          </el-descriptions-item>
          <el-descriptions-item v-if="currentAchievement.remarks" label="备注" :span="2">
            {{ currentAchievement.remarks }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="closeDetailDialog">关闭</el-button>
        </span>
      </template>
    </el-dialog>
  
    <!-- 返回按钮 -->
    <div class="back-button">
      <el-button type="primary" size="large" @click="goBack">
        <el-icon><ArrowLeft /></el-icon>
        返回首页
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, nextTick, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useThemeStore } from '@/stores/theme'
import { useConfigStore } from '@/stores/config'
import { storeToRefs } from 'pinia'
import { ElMessage } from 'element-plus'
import {
  Calendar,
  School,
  User,
  UserFilled,
  ArrowLeft
} from '@element-plus/icons-vue'
import ThemeToggle from '@/components/ThemeToggle.vue'
import { getPublicAchievements, getPublicStatistics, getPublicClasses, getPublicConfig } from '@/api/public'
import * as echarts from 'echarts'

const router = useRouter()
const themeStore = useThemeStore()
const configStore = useConfigStore()
const { isDarkMode } = storeToRefs(themeStore)

// 数据状态
const loading = ref(false)
const statisticsLoading = ref(false)
const activeTab = ref('list')
const achievements = ref([])
const currentAchievement = ref(null)
const detailDialogVisible = ref(false)
const statistics = ref({})
const classes = ref([])
const availableYears = ref([])
const systemConfig = ref({})

// 使用configStore的计算属性
const achievementTypes = computed(() => configStore.achievementTypeOptions)
const achievementLevels = computed(() => configStore.achievementLevelOptions)

// 筛选条件
const filters = reactive({
  type: '',
  level: '',
  class_id: '',
  year: ''
})

// 分页
const pagination = reactive({
  page: 1,
  per_page: 12,
  total: 0
})

// 图表引用
const typeChartRef = ref(null)
const levelChartRef = ref(null)
const yearChartRef = ref(null)
const classChartRef = ref(null)

// 图表实例
let typeChart = null
let levelChart = null
let yearChart = null
let classChart = null

// 类型和级别映射
// 获取显示文本
const getTypeDisplay = (type) => {
  return configStore.getTypeLabel(type)
}

const getLevelDisplay = (level) => {
  return configStore.getLevelLabel(level)
}

// 获取标签类型
const getTypeTagType = (type) => {
  const typeColors = {
    'paper': '',
    'competition': 'success',
    'project': 'warning',
    'honor': 'danger'
  }
  return typeColors[type] || ''
}

const getLevelTagType = (level) => {
  const levelColors = {
    'school': '',
    'province': 'warning',
    'national': 'danger'
  }
  return levelColors[level] || ''
}

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}

// 获取成果列表
const fetchAchievements = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      per_page: pagination.per_page,
      ...filters
    }
    
    // 移除空值
    Object.keys(params).forEach(key => {
      if (params[key] === '' || params[key] === null || params[key] === undefined) {
        delete params[key]
      }
    })
    
    const response = await getPublicAchievements(params)
    achievements.value = response.data.achievements
    pagination.total = response.data.total
  } catch (error) {
    console.error('获取成果列表失败:', error)
    ElMessage.error('获取成果列表失败')
  } finally {
    loading.value = false
  }
}

// 查看详情
const viewDetail = (row) => {
  currentAchievement.value = row
  detailDialogVisible.value = true
}

// 关闭详情对话框
const closeDetailDialog = () => {
  detailDialogVisible.value = false
  currentAchievement.value = null
}

// 获取统计数据
const fetchStatistics = async () => {
  statisticsLoading.value = true
  try {
    const response = await getPublicStatistics()
    statistics.value = response.data
    
    // 生成可用年份列表
    if (response.data.by_year && response.data.by_year.length > 0) {
      availableYears.value = response.data.by_year
        .map(item => item.year)
        .sort((a, b) => b - a)
    }
    
    // 如果当前在图表视图，渲染图表
    if (activeTab.value === 'chart') {
      await nextTick()
      renderCharts()
    }
  } catch (error) {
    console.error('获取统计数据失败:', error)
    ElMessage.error('获取统计数据失败')
  } finally {
    statisticsLoading.value = false
  }
}

// 获取班级列表
const fetchClasses = async () => {
  try {
    const response = await getPublicClasses()
    classes.value = response.data.classes
  } catch (error) {
    console.error('获取班级列表失败:', error)
  }
}

// 获取系统配置
const fetchSystemConfig = async () => {
  try {
    const response = await getPublicConfig()
    systemConfig.value = response.data.config
  } catch (error) {
    console.error('获取系统配置失败:', error)
  }
}

// 分页处理
const handleSizeChange = (size) => {
  pagination.per_page = size
  pagination.page = 1
  fetchAchievements()
}

const handleCurrentChange = (page) => {
  pagination.page = page
  fetchAchievements()
}

// 标签页切换
const handleTabChange = async (tabName) => {
  if (tabName === 'chart' && Object.keys(statistics.value).length === 0) {
    await fetchStatistics()
  } else if (tabName === 'chart') {
    await nextTick()
    renderCharts()
  }
}

// 渲染图表
const renderCharts = () => {
  renderTypeChart()
  renderLevelChart()
  renderYearChart()
  renderClassChart()
}

// 渲染类型分布饼图
const renderTypeChart = () => {
  if (!typeChartRef.value || !statistics.value.by_type) return
  
  if (typeChart) {
    typeChart.dispose()
  }
  
  typeChart = echarts.init(typeChartRef.value)
  
  const data = statistics.value.by_type.map(item => ({
    name: getTypeDisplay(item.type),
    value: item.count
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
      data: data,
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

// 渲染级别分布饼图
const renderLevelChart = () => {
  if (!levelChartRef.value || !statistics.value.by_level) return
  
  if (levelChart) {
    levelChart.dispose()
  }
  
  levelChart = echarts.init(levelChartRef.value)
  
  const data = statistics.value.by_level.map(item => ({
    name: getLevelDisplay(item.level),
    value: item.count
  }))
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    series: [{
      name: '获奖级别',
      type: 'pie',
      radius: '70%',
      data: data,
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }]
  }
  
  levelChart.setOption(option)
}

// 渲染年度趋势折线图
const renderYearChart = () => {
  if (!yearChartRef.value || !statistics.value.by_year) return
  
  if (yearChart) {
    yearChart.dispose()
  }
  
  yearChart = echarts.init(yearChartRef.value)
  
  const sortedData = statistics.value.by_year.sort((a, b) => a.year - b.year)
  const years = sortedData.map(item => item.year)
  const counts = sortedData.map(item => item.count)
  
  const option = {
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      data: years
    },
    yAxis: {
      type: 'value'
    },
    series: [{
      name: '成果数量',
      type: 'line',
      data: counts,
      smooth: true,
      itemStyle: {
        color: '#409EFF'
      },
      areaStyle: {
        color: 'rgba(64, 158, 255, 0.1)'
      }
    }]
  }
  
  yearChart.setOption(option)
}

// 渲染班级对比柱状图
const renderClassChart = () => {
  if (!classChartRef.value || !statistics.value.by_class) return
  
  if (classChart) {
    classChart.dispose()
  }
  
  classChart = echarts.init(classChartRef.value)
  
  const data = statistics.value.by_class
  const classNames = data.map(item => item.class_name)
  const counts = data.map(item => item.count)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    xAxis: {
      type: 'category',
      data: classNames,
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: {
      type: 'value'
    },
    series: [{
      name: '成果数量',
      type: 'bar',
      data: counts,
      itemStyle: {
        color: '#67C23A'
      }
    }]
  }
  
  classChart.setOption(option)
}

// 返回首页
const goBack = () => {
  router.push('/')
}

// 监听主题变化，重新渲染图表
watch(isDarkMode, () => {
  if (activeTab.value === 'chart') {
    setTimeout(() => {
      renderCharts()
    }, 100)
  }
})

// 组件挂载时获取数据
onMounted(async () => {
  await configStore.smartLoadConfig()
  await fetchSystemConfig()
  await fetchClasses()
  await fetchAchievements()
})

// 组件卸载时销毁图表
onUnmounted(() => {
  if (typeChart) typeChart.dispose()
  if (levelChart) levelChart.dispose()
  if (yearChart) yearChart.dispose()
  if (classChart) classChart.dispose()
})
</script>

<style scoped>
.display-container {
  min-height: 100vh;
  background: url('~@/assets/back.jpg') center center/cover no-repeat;
  padding: 20px;
  transition: all 0.3s ease;
}

.dark-mode .display-container {
  filter: brightness(0.8);
}

.header {
  text-align: center;
  color: white;
  margin-bottom: 30px;
}

.title {
  font-size: 3rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  text-shadow: 3px 3px 8px rgba(0, 0, 0, 0.8), 0 0 12px rgba(0, 0, 0, 0.6);
}

.subtitle {
  font-size: 1.25rem;
  font-weight: 500;
  opacity: 1;
  text-shadow: 2px 2px 6px rgba(0, 0, 0, 0.8), 0 0 8px rgba(0, 0, 0, 0.6);
}

.main-content {
  max-width: 1400px;
  width: 100%;
  margin: 0 auto;
}

.filter-card {
  margin-bottom: 20px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.dark-mode .filter-card {
  background: rgba(26, 26, 26, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.filter-section {
  padding: 20px;
}

.content-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.dark-mode .content-card {
  background: rgba(26, 26, 26, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.list-view {
  padding: 20px;
}

.achievement-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.achievement-card {
  transition: all 0.3s ease;
  cursor: pointer;
}

.achievement-card:hover {
  transform: translateY(-5px);
}

.achievement-item {
  height: 100%;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(5px);
}

.dark-mode .achievement-item {
  background: rgba(45, 45, 45, 0.9);
}

.achievement-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
  gap: 15px;
}

.achievement-title {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
  margin: 0;
  line-height: 1.4;
  flex: 1;
}

.dark-mode .achievement-title {
  color: #e4e7ed;
}

.achievement-tags {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.achievement-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #606266;
}

.dark-mode .info-item {
  color: #909399;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  padding: 20px 0;
}

.chart-view {
  padding: 20px;
}

.stats-overview {
  margin-bottom: 30px;
}

.stat-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  text-align: center;
  border: none;
}

.stat-content {
  padding: 10px;
}

.stat-number {
  font-size: 32px;
  font-weight: bold;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  opacity: 0.9;
}

.charts-row {
  margin-bottom: 20px;
}

.chart-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.dark-mode .chart-card {
  background: rgba(45, 45, 45, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.chart-header {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
  text-align: center;
}

.dark-mode .chart-header {
  color: #e4e7ed;
}

.chart-container {
  width: 100%;
  height: 300px;
}

.chart-container-large {
  width: 100%;
  height: 400px;
}

.back-button {
  position: fixed;
  bottom: 30px;
  right: 30px;
  z-index: 1000;
}

.back-button .el-button {
  background: rgba(64, 158, 255, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.3);
  backdrop-filter: blur(10px);
  box-shadow: 0 8px 32px rgba(64, 158, 255, 0.3);
  transition: all 0.3s ease;
}

.back-button .el-button:hover {
  background: rgba(64, 158, 255, 1);
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(64, 158, 255, 0.4);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .display-container {
    padding: 10px;
  }
  
  .title {
    font-size: 2rem;
  }
  
  .achievement-grid {
    grid-template-columns: 1fr;
  }
  
  .achievement-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .achievement-tags {
    align-self: flex-start;
  }
  
  .back-button {
    bottom: 20px;
    right: 20px;
  }
  
  .chart-container,
  .chart-container-large {
    height: 250px;
  }
}

@media (max-width: 480px) {
  .filter-section .el-row {
    flex-direction: column;
  }
  
  .filter-section .el-col {
    width: 100%;
    margin-bottom: 10px;
  }
}

/* 动画效果 */
.achievement-card {
  animation: fadeInUp 0.6s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.chart-card {
  animation: fadeIn 0.8s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

/* Element Plus 组件样式覆盖 */
.el-tabs__item {
  font-weight: 500;
}

.el-tabs__item.is-active {
  color: #409eff;
}

.el-select {
  width: 100%;
}

.el-pagination {
  justify-content: center;
}

.el-tag {
  font-weight: 500;
}

.el-card {
  border-radius: 12px;
}

.el-loading-spinner {
  margin-top: -25px;
}

/* 暗色模式下的 Element Plus 组件覆盖 */
.dark-mode :deep(.el-select__wrapper) {
  background-color: rgba(45, 45, 45, 0.95);
  border-color: rgba(255, 255, 255, 0.12);
  color: #e4e7ed;
}

.dark-mode :deep(.el-select__placeholder) {
  color: #bfc2c7;
}

.dark-mode :deep(.el-input__inner) {
  background-color: transparent;
  color: #e4e7ed;
}

.dark-mode :deep(.el-dialog) {
  background-color: rgba(45, 45, 45, 0.96);
  border: 1px solid rgba(255, 255, 255, 0.12);
}

.dark-mode :deep(.el-dialog__title) {
  color: #e4e7ed;
}

.dark-mode :deep(.el-dialog__body),
.dark-mode :deep(.el-dialog__footer) {
  color: #e4e7ed;
}

.dark-mode :deep(.el-descriptions__table.is-bordered) {
  border-color: rgba(255, 255, 255, 0.12);
}

.dark-mode :deep(.el-descriptions__cell) {
  background-color: rgba(40, 40, 40, 0.9);
  color: #e4e7ed;
}

.dark-mode :deep(.el-descriptions__label) {
  background-color: rgba(50, 50, 50, 0.9);
  color: #e4e7ed;
}
</style>
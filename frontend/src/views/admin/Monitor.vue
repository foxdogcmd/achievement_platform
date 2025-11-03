<template>
  <div class="monitor-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>成果总览</span>
          <div class="header-actions">
            <el-button @click="batchSetPublic" :disabled="selectedAchievements.length === 0">
              <el-icon><View /></el-icon>
              批量公开
            </el-button>
            <el-button type="primary" @click="exportAllData">
              <el-icon><Download /></el-icon>
              导出数据
            </el-button>
          </div>
        </div>
      </template>
      
      <!-- 筛选条件 -->
      <div class="filter-section">
        <el-row :gutter="20">
          <el-col :span="4">
            <el-select v-model="filters.status" placeholder="状态筛选" clearable @change="fetchAchievements">
              <el-option label="全部状态" value="" />
              <el-option label="待审核" value="pending" />
              <el-option label="已通过" value="approved" />
              <el-option label="已退回" value="returned" />
              <el-option label="已拒绝" value="rejected" />
            </el-select>
          </el-col>
          <el-col :span="4">
            <el-select v-model="filters.type" placeholder="类型筛选" clearable @change="fetchAchievements">
              <el-option label="全部类型" value="" />
              <el-option 
                v-for="option in configStore.achievementTypeOptions" 
                :key="option.value" 
                :label="option.label" 
                :value="option.value" 
              />
            </el-select>
          </el-col>
          <el-col :span="4">
            <el-select v-model="filters.level" placeholder="级别筛选" clearable @change="fetchAchievements">
              <el-option label="全部级别" value="" />
              <el-option 
                v-for="option in configStore.achievementLevelOptions" 
                :key="option.value" 
                :label="option.label" 
                :value="option.value" 
              />
            </el-select>
          </el-col>
          <el-col :span="4">
            <el-select v-model="filters.class_id" placeholder="班级筛选" clearable @change="fetchAchievements">
              <el-option label="全部班级" value="" />
              <el-option 
                v-for="cls in classes" 
                :key="cls.class_id" 
                :label="cls.class_name" 
                :value="cls.class_id" 
              />
            </el-select>
          </el-col>
          <el-col :span="8">
            <el-input
              v-model="filters.keyword"
              placeholder="搜索成果名称或提交人"
              clearable
              @keyup.enter="fetchAchievements"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </el-col>
        </el-row>
        <el-row :gutter="20" style="margin-top: 12px;">
          <el-col :span="8">
            <el-date-picker
              v-model="filters.date_range"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              @change="fetchAchievements"
              style="width: 100%;"
            />
          </el-col>
          <el-col :span="8">
            <el-button @click="fetchAchievements" :loading="loading">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
            <el-button @click="resetFilters">
              <el-icon><Delete /></el-icon>
              重置
            </el-button>
          </el-col>
        </el-row>
      </div>
      
      <!-- 成果列表 -->
      <el-table
        :data="achievements"
        v-loading="loading"
        stripe
        style="width: 100%"
        @sort-change="handleSortChange"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="title" label="成果名称" min-width="200" show-overflow-tooltip />
        <el-table-column prop="type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getTypeTagType(row.type)">{{ getTypeDisplay(row.type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="level" label="级别" width="100">
          <template #default="{ row }">
            <el-tag :type="getLevelTagType(row.level)">{{ getLevelDisplay(row.level) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="submitter_name" label="提交人" width="120" />
        <el-table-column prop="leader_name" label="审核队长" width="120" />
        <el-table-column prop="class_name" label="所属班级" width="120" />
        <el-table-column prop="award_date" label="获奖时间" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)">{{ getStatusDisplay(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_public" label="公开状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_public ? 'success' : 'info'">
              {{ row.is_public ? '已公开' : '未公开' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="提交时间" width="160" sortable="custom">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button size="small" @click="viewDetail(row)">
                <el-icon><View /></el-icon>
                查看
              </el-button>
              <el-button 
                size="small" 
                :type="row.is_public ? 'warning' : 'success'"
                @click="togglePublicStatus(row)"
              >
                {{ row.is_public ? '取消公开' : '设为公开' }}
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.per_page"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="fetchAchievements"
          @current-change="fetchAchievements"
        />
      </div>
    </el-card>
    
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
            {{ currentAchievement.award_date }}
          </el-descriptions-item>
          <el-descriptions-item label="指导教师">
            {{ currentAchievement.supervisor || '无' }}
          </el-descriptions-item>
          <el-descriptions-item label="提交人">
            {{ currentAchievement.submitter_name }}
          </el-descriptions-item>
          <el-descriptions-item label="审核队长">
            {{ currentAchievement.leader_name || '未分配' }}
          </el-descriptions-item>
          <el-descriptions-item label="所属班级">
            {{ currentAchievement.class_name }}
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusTagType(currentAchievement.status)">
              {{ getStatusDisplay(currentAchievement.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="公开状态">
            <el-tag :type="currentAchievement.is_public ? 'success' : 'info'">
              {{ currentAchievement.is_public ? '已公开' : '未公开' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="成员名单" :span="2">
            <el-tag v-for="member in currentAchievement.members" :key="member" class="member-tag">
              {{ member }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="成果描述" :span="2">
            {{ currentAchievement.description || '无描述' }}
          </el-descriptions-item>
          <el-descriptions-item label="备注" :span="2">
            {{ currentAchievement.remarks || '无备注' }}
          </el-descriptions-item>
        </el-descriptions>
        
        <!-- 佐证材料 -->
        <div class="evidence-section">
          <h4>佐证材料</h4>
          <div v-if="!currentAchievement.evidence_files || currentAchievement.evidence_files.length === 0" class="no-files">
            <p>暂无佐证材料</p>
          </div>
          <div v-else class="file-list">
            <div v-for="file in currentAchievement.evidence_files" :key="file" class="file-item">
              <div class="file-info">
                <el-icon class="file-icon">
                  <Document v-if="!isImageFile(file)" />
                  <Picture v-else />
                </el-icon>
                <span class="file-name">{{ getFileName(file) }}</span>
                <span class="file-type">{{ getFileType(file) }}</span>
              </div>
              <div class="file-actions">
                <el-button 
                  v-if="isImageFile(file)" 
                  size="small" 
                  @click="previewImage(file)"
                >
                  <el-icon><View /></el-icon>
                  预览
                </el-button>
                <el-button size="small" type="primary" @click="downloadFile(file)">
                  <el-icon><Download /></el-icon>
                  下载
                </el-button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>
    
    <!-- 图片预览弹窗 -->
    <el-dialog
      v-model="imagePreviewVisible"
      title="图片预览"
      width="80%"
      :before-close="closeImagePreview"
      class="image-preview-dialog"
    >
      <div class="image-preview-container">
        <el-image
          v-if="currentPreviewImage"
          :src="getFileUrl(currentPreviewImage)"
          fit="contain"
          style="width: 100%; height: 100%;"
          preview-teleported
        />
      </div>
      
      <template #footer>
        <div class="image-preview-footer">
          <span class="image-info">
            {{ currentPreviewImage ? getFileName(currentPreviewImage) : '未知文件' }}
          </span>
          <div class="preview-actions">
            <el-button 
              v-if="currentPreviewImage" 
              @click="downloadFile(currentPreviewImage)"
            >
              <el-icon><Download /></el-icon>
              下载
            </el-button>
            <el-button @click="closeImagePreview">关闭</el-button>
          </div>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search,
  Refresh,
  Delete,
  View,
  Download,
  Document,
  Picture
} from '@element-plus/icons-vue'
import { 
  getAllAchievements, 
  updateAchievementPublic, 
  batchOperateAchievements,
  exportData,
  getAllClasses
} from '@/api/admin'
import { useConfigStore } from '@/stores/config'

// 配置store
const configStore = useConfigStore()

// 数据
const loading = ref(false)
const achievements = ref([])
const selectedAchievements = ref([])
const classes = ref([])
const currentAchievement = ref(null)
const detailDialogVisible = ref(false)

// 图片预览相关
const imagePreviewVisible = ref(false)
const currentPreviewImage = ref(null)

// 筛选条件
const filters = reactive({
  status: '',
  type: '',
  level: '',
  class_id: '',
  keyword: '',
  date_range: null
})

// 分页
const pagination = reactive({
  page: 1,
  per_page: 10,
  total: 0
})

// 排序
const sortConfig = reactive({
  prop: '',
  order: ''
})

const statusMap = {
  'pending': '待审核',
  'approved': '已通过',
  'returned': '已退回',
  'rejected': '已拒绝'
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
    
    // 处理日期范围
    if (filters.date_range && filters.date_range.length === 2) {
      params.start_date = filters.date_range[0].toISOString().split('T')[0]
      params.end_date = filters.date_range[1].toISOString().split('T')[0]
    }
    
    if (sortConfig.prop) {
      params.sort_by = sortConfig.prop
      params.sort_order = sortConfig.order === 'ascending' ? 'asc' : 'desc'
    }
    
    const response = await getAllAchievements(params)
    achievements.value = response.data.achievements
    pagination.total = response.data.total
  } catch (error) {
    ElMessage.error('获取成果列表失败')
  } finally {
    loading.value = false
  }
}

// 获取班级列表
const fetchClasses = async () => {
  try {
    const response = await getAllClasses()
    classes.value = response.data.classes
  } catch (error) {
    console.error('获取班级列表失败:', error)
  }
}

// 重置筛选条件
const resetFilters = () => {
  Object.assign(filters, {
    status: '',
    type: '',
    level: '',
    class_id: '',
    keyword: '',
    date_range: null
  })
  pagination.page = 1
  fetchAchievements()
}

// 排序处理
const handleSortChange = ({ prop, order }) => {
  sortConfig.prop = prop
  sortConfig.order = order
  fetchAchievements()
}

// 选择处理
const handleSelectionChange = (selection) => {
  selectedAchievements.value = selection
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

// 切换公开状态
const togglePublicStatus = async (row) => {
  try {
    await updateAchievementPublic(row.achievement_id, !row.is_public)
    ElMessage.success(`成果已${row.is_public ? '取消公开' : '设为公开'}`)
    fetchAchievements()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

// 批量设置公开
const batchSetPublic = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要将选中的 ${selectedAchievements.value.length} 个成果设置为公开展示吗？`,
      '批量操作确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const achievementIds = selectedAchievements.value.map(item => item.achievement_id)
    await batchOperateAchievements({
      achievement_ids: achievementIds,
      operation: 'set_public',
      value: true
    })
    
    ElMessage.success('批量设置成功')
    fetchAchievements()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量操作失败')
    }
  }
}

// 导出数据
const exportAllData = async () => {
  try {
    const response = await exportData({ type: 'achievements', format: 'excel' })
    // 处理文件下载
    const blob = new Blob([response.data])
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `成果数据导出_${new Date().toISOString().split('T')[0]}.xlsx`
    link.click()
    window.URL.revokeObjectURL(url)
    ElMessage.success('数据导出成功')
  } catch (error) {
    ElMessage.error('导出数据失败')
  }
}

// 文件相关方法
const getFileName = (filePath) => {
  if (!filePath) return '未知文件'
  return filePath.split('/').pop()
}

const getFileType = (filePath) => {
  const ext = filePath.split('.').pop().toLowerCase()
  const typeMap = {
    'pdf': 'PDF文档',
    'jpg': '图片',
    'jpeg': '图片', 
    'png': '图片',
    'gif': '图片'
  }
  return typeMap[ext] || '未知类型'
}

const isImageFile = (filePath) => {
  const ext = filePath.split('.').pop().toLowerCase()
  return ['jpg', 'jpeg', 'png', 'gif'].includes(ext)
}

const getFileUrl = (filePath) => {
  if (filePath.startsWith('/')) {
    return `http://localhost:5000${filePath}`
  }
  return filePath
}

const previewImage = (filePath) => {
  currentPreviewImage.value = filePath
  imagePreviewVisible.value = true
}

const closeImagePreview = () => {
  imagePreviewVisible.value = false
  currentPreviewImage.value = null
}

const downloadFile = (filePath) => {
  const link = document.createElement('a')
  link.href = getFileUrl(filePath)
  link.download = getFileName(filePath)
  link.target = '_blank'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

// 获取显示文本
const getTypeDisplay = (type) => configStore.getTypeLabel(type)
const getLevelDisplay = (level) => configStore.getLevelLabel(level)
const getStatusDisplay = (status) => statusMap[status] || status

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

const getStatusTagType = (status) => {
  const statusColors = {
    'pending': 'warning',
    'approved': 'success',
    'returned': 'info',
    'rejected': 'danger'
  }
  return statusColors[status] || ''
}

// 格式化日期时间
const formatDateTime = (dateTime) => {
  if (!dateTime) return '-'
  return new Date(dateTime).toLocaleString('zh-CN')
}

// 组件挂载时获取数据
onMounted(async () => {
  await configStore.smartLoadConfig()
  fetchAchievements()
  fetchClasses()
})
</script>

<style lang="scss" scoped>
.monitor-page {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    .header-actions {
      display: flex;
      gap: 12px;
      align-items: center;
    }
  }
  
  .filter-section {
    margin-bottom: 20px;
    padding: 20px;
    background: #f8f9fa;
    border-radius: 6px;
  }
  
  .pagination-wrapper {
    margin-top: 20px;
    text-align: right;
  }
  
  .action-buttons {
    display: flex;
    gap: 8px;
    flex-wrap: nowrap;
    
    .el-button {
      flex-shrink: 0;
    }
  }
  
  .achievement-detail {
    .member-tag {
      margin-right: 8px;
      margin-bottom: 4px;
    }
    
    .evidence-section {
      margin-top: 20px;
      
      h4 {
        margin-bottom: 12px;
        color: #303133;
      }
      
      .no-files {
        text-align: center;
        padding: 40px 20px;
        color: #909399;
        background: #f5f7fa;
        border-radius: 6px;
        
        p {
          margin: 0;
          font-size: 14px;
        }
      }
      
      .file-list {
        .file-item {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 12px 16px;
          background: #f5f7fa;
          border-radius: 6px;
          margin-bottom: 12px;
          border: 1px solid #e4e7ed;
          transition: all 0.3s;
          
          &:hover {
            background: #ecf5ff;
            border-color: #409eff;
          }
          
          .file-info {
            display: flex;
            align-items: center;
            flex: 1;
            
            .file-icon {
              margin-right: 12px;
              color: #409eff;
              font-size: 20px;
            }
            
            .file-name {
              font-weight: 500;
              color: #303133;
              margin-right: 12px;
            }
            
            .file-type {
              font-size: 12px;
              color: #909399;
              background: #e4e7ed;
              padding: 2px 8px;
              border-radius: 12px;
            }
          }
          
          .file-actions {
            display: flex;
            gap: 8px;
          }
        }
      }
    }
  }
  
  // 图片预览弹窗样式
  :deep(.image-preview-dialog) {
    .el-dialog__body {
      padding: 20px;
      text-align: center;
      max-height: 80vh;
      overflow: hidden;
    }
    
    .image-preview-container {
      display: flex;
      justify-content: center;
      align-items: center;
      width: 100%;
      height: 60vh;
      max-height: 600px;
      min-height: 300px;
      background: #f5f5f5;
      border-radius: 8px;
      overflow: hidden;
      
      .el-image {
        width: 100% !important;
        height: 100% !important;
        
        .el-image__inner {
          width: 100% !important;
          height: 100% !important;
          object-fit: contain !important;
        }
      }
    }
    
    .image-preview-footer {
      display: flex;
      justify-content: space-between;
      align-items: center;
      
      .image-info {
        color: #606266;
        font-size: 14px;
      }
      
      .preview-actions {
        display: flex;
        gap: 12px;
      }
    }
  }
}
</style>
<template>
  <div class="audit-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>成果审核</span>
          <div class="header-actions">
            <el-select v-model="filters.status" placeholder="状态筛选" clearable @change="fetchAchievements">
              <el-option label="全部状态" value="" />
              <el-option label="待审核" value="pending" />
              <el-option label="已通过" value="approved" />
              <el-option label="已退回" value="returned" />
              <el-option label="已拒绝" value="rejected" />
            </el-select>
            <el-button @click="fetchAchievements" :loading="loading">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </div>
      </template>
      
      <!-- 待审核成果列表 -->
      <el-table
        :data="achievements"
        v-loading="loading"
        stripe
        style="width: 100%"
        @sort-change="handleSortChange"
      >
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
        <el-table-column prop="award_date" label="获奖时间" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)">{{ getStatusDisplay(row.status) }}</el-tag>
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
                v-if="row.status === 'pending'"
                size="small"
                type="primary"
                @click="openAuditDialog(row)"
              >
                <el-icon><DocumentChecked /></el-icon>
                审核
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
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusTagType(currentAchievement.status)">
              {{ getStatusDisplay(currentAchievement.status) }}
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
    
    <!-- 审核对话框 -->
    <el-dialog
      v-model="auditDialogVisible"
      title="成果审核"
      width="600px"
      :before-close="closeAuditDialog"
    >
      <div v-if="currentAuditAchievement" class="audit-form">
        <div class="achievement-info">
          <h4>{{ currentAuditAchievement.title }}</h4>
          <p>提交人：{{ currentAuditAchievement.submitter_name }}</p>
          <p>提交时间：{{ formatDateTime(currentAuditAchievement.created_at) }}</p>
        </div>
        
        <el-form :model="auditForm" :rules="auditRules" ref="auditFormRef" label-width="100px">
          <el-form-item label="审核结果" prop="action">
            <el-radio-group v-model="auditForm.action">
              <el-radio value="approve">
                <el-icon><Check /></el-icon>
                通过
              </el-radio>
              <el-radio value="return">
                <el-icon><RefreshLeft /></el-icon>
                退回
              </el-radio>
              <el-radio value="reject">
                <el-icon><Close /></el-icon>
                拒绝
              </el-radio>
            </el-radio-group>
          </el-form-item>
          
          <el-form-item 
            label="审核意见" 
            prop="comment"
            :rules="auditForm.action !== 'approve' ? [{ required: true, message: '请填写审核意见', trigger: 'blur' }] : []"
          >
            <el-input
              v-model="auditForm.comment"
              type="textarea"
              :rows="4"
              :placeholder="getCommentPlaceholder()"
              maxlength="500"
              show-word-limit
            />
          </el-form-item>
        </el-form>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="closeAuditDialog">取消</el-button>
          <el-button type="primary" @click="submitAudit" :loading="auditing">
            提交审核
          </el-button>
        </div>
      </template>
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
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Refresh,
  View,
  DocumentChecked,
  Document,
  Picture,
  Download,
  Check,
  RefreshLeft,
  Close
} from '@element-plus/icons-vue'
import { getPendingAchievements, auditAchievement as auditAchievementApi } from '@/api/leader'
import { useConfigStore } from '@/stores/config'

const route = useRoute()

// 配置store
const configStore = useConfigStore()

// 数据
const loading = ref(false)
const auditing = ref(false)
const achievements = ref([])
const currentAchievement = ref(null)
const currentAuditAchievement = ref(null)
const detailDialogVisible = ref(false)
const auditDialogVisible = ref(false)

// 图片预览相关
const imagePreviewVisible = ref(false)
const currentPreviewImage = ref(null)

// 筛选条件
const filters = reactive({
  status: ''
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

// 审核表单
const auditForm = reactive({
  action: '',
  comment: ''
})

const auditFormRef = ref()

const auditRules = {
  action: [
    { required: true, message: '请选择审核结果', trigger: 'change' }
  ]
}

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
    
    if (sortConfig.prop) {
      params.sort_by = sortConfig.prop
      params.sort_order = sortConfig.order === 'ascending' ? 'asc' : 'desc'
    }
    
    const response = await getPendingAchievements(params)
    achievements.value = response.data.achievements
    pagination.total = response.data.total
  } catch (error) {
    ElMessage.error('获取成果列表失败')
  } finally {
    loading.value = false
  }
}

// 排序处理
const handleSortChange = ({ prop, order }) => {
  sortConfig.prop = prop
  sortConfig.order = order
  fetchAchievements()
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

// 打开审核对话框
const openAuditDialog = (row) => {
  currentAuditAchievement.value = row
  auditForm.action = ''
  auditForm.comment = ''
  auditDialogVisible.value = true
}

// 关闭审核对话框
const closeAuditDialog = () => {
  auditDialogVisible.value = false
  currentAuditAchievement.value = null
  auditForm.action = ''
  auditForm.comment = ''
}

// 获取审核意见占位符
const getCommentPlaceholder = () => {
  switch (auditForm.action) {
    case 'return':
      return '请说明需要修改的地方...'
    case 'reject':
      return '请说明拒绝的原因...'
    default:
      return '请填写审核意见（选填）'
  }
}

// 提交审核
const submitAudit = async () => {
  if (!auditFormRef.value) return
  
  await auditFormRef.value.validate(async (valid) => {
    if (valid) {
      auditing.value = true
      try {
        await auditAchievementApi(currentAuditAchievement.value.achievement_id, auditForm)
        ElMessage.success('审核提交成功')
        closeAuditDialog()
        fetchAchievements()
      } catch (error) {
        ElMessage.error(error.response?.data?.message || '审核失败')
      } finally {
        auditing.value = false
      }
    }
  })
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
  // 如果有指定的成果ID，直接跳转到审核
  if (route.query.id) {
    // 这里可以根据ID获取特定成果并打开审核对话框
  }
  fetchAchievements()
})
</script>

<style lang="scss" scoped>
.audit-page {
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
  
  .audit-form {
    .achievement-info {
      padding: 16px;
      background: #f5f7fa;
      border-radius: 6px;
      margin-bottom: 20px;
      
      h4 {
        margin: 0 0 8px 0;
        color: #303133;
      }
      
      p {
        margin: 4px 0;
        color: #606266;
        font-size: 14px;
      }
    }
    
    .el-radio {
      margin-right: 20px;
      margin-bottom: 12px;
      
      .el-icon {
        margin-right: 4px;
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
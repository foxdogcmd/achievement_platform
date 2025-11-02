<template>
  <div class="achievements-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>我的成果</span>
          <el-button type="primary" @click="$router.push('/student/achievements/create')">
            <el-icon><Plus /></el-icon>
            添加成果
          </el-button>
        </div>
      </template>
      
      <!-- 筛选条件 -->
      <div class="filter-section">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-select v-model="filters.status" placeholder="状态筛选" clearable @change="fetchAchievements">
              <el-option label="全部状态" value="" />
              <el-option label="待审核" value="pending" />
              <el-option label="已通过" value="approved" />
              <el-option label="已退回" value="returned" />
              <el-option label="已拒绝" value="rejected" />
            </el-select>
          </el-col>
          <el-col :span="6">
            <el-select v-model="filters.type" placeholder="类型筛选" clearable @change="fetchAchievements">
              <el-option label="全部类型" value="" />
              <el-option label="论文" value="paper" />
              <el-option label="竞赛" value="competition" />
              <el-option label="项目" value="project" />
              <el-option label="荣誉" value="honor" />
            </el-select>
          </el-col>
          <el-col :span="6">
            <el-input
              v-model="filters.keyword"
              placeholder="搜索成果名称"
              clearable
              @keyup.enter="fetchAchievements"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </el-col>
          <el-col :span="6">
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
        <el-table-column prop="award_date" label="获奖时间" width="120" sortable="custom" />
        <el-table-column prop="leader_name" label="所属队长" width="120" />
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
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button size="small" @click="viewDetail(row)">
                <el-icon><View /></el-icon>
                查看
              </el-button>
              <el-button
                v-if="canEdit(row)"
                size="small"
                type="primary"
                @click="editAchievement(row)"
              >
                <el-icon><Edit /></el-icon>
                编辑
              </el-button>
              <el-button
                v-if="canDelete(row)"
                size="small"
                type="danger"
                @click="deleteAchievement(row)"
              >
                <el-icon><Delete /></el-icon>
                删除
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
    
    <!-- 详情对话框 -->
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
          <el-descriptions-item label="所属队长">
            {{ currentAchievement.leader_name }}
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
          <el-descriptions-item label="提交时间">
            {{ formatDateTime(currentAchievement.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="更新时间">
            {{ formatDateTime(currentAchievement.updated_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="审核意见" :span="2" v-if="currentAchievement.status !== 'pending'">
            {{ currentAchievement.comment  }}
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
            :preview-src-list="getImagePreviewList()"
            :initial-index="currentImageIndex"
            fit="contain"
            style="width: 100%; height: 100%;"
            preview-teleported
          />
        </div>
       
       <template #footer>
          <div class="image-preview-footer">
            <span class="image-info">
              {{ currentPreviewImage ? getFileName(currentPreviewImage) : '未知文件' }} 
              ({{ currentImageIndex + 1 }} / {{ getImagePreviewList().length }})
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
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus,
  Search,
  Refresh,
  Delete,
  View,
  Edit,
  Document,
  Picture,
  Download
} from '@element-plus/icons-vue'
import { getMyAchievements, deleteAchievement as deleteAchievementApi } from '@/api/student'

const router = useRouter()

// 数据
const loading = ref(false)
const achievements = ref([])
const currentAchievement = ref(null)
const detailDialogVisible = ref(false)

// 图片预览相关
const imagePreviewVisible = ref(false)
const currentPreviewImage = ref(null)
const currentImageIndex = ref(0)

// 筛选条件
const filters = reactive({
  status: '',
  type: '',
  keyword: ''
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

// 类型映射
const typeMap = {
  'paper': '论文',
  'competition': '竞赛',
  'project': '项目',
  'honor': '荣誉'
}

const levelMap = {
  'school': '校级',
  'province': '省部级',
  'national': '国家级'
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
    
    const response = await getMyAchievements(params)
    achievements.value = response.data.achievements
    pagination.total = response.data.total
  } catch (error) {
    ElMessage.error('获取成果列表失败')
  } finally {
    loading.value = false
  }
}

// 重置筛选条件
const resetFilters = () => {
  Object.assign(filters, {
    status: '',
    type: '',
    keyword: ''
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

// 编辑成果
const editAchievement = (row) => {
  // 跳转到创建页面，并传递编辑的成果ID
  router.push({
    path: '/student/achievements/create',
    query: { edit: row.achievement_id }
  })
}

// 删除成果
const deleteAchievement = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除成果"${row.title}"吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await deleteAchievementApi(row.achievement_id)
    ElMessage.success('删除成功')
    fetchAchievements()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.message || '删除失败')
    }
  }
}

// 判断是否可以编辑
const canEdit = (row) => {
  return ['pending', 'returned'].includes(row.status)
}

// 判断是否可以删除
const canDelete = (row) => {
  return row.status === 'pending'
}

// 获取类型显示文本
const getTypeDisplay = (type) => typeMap[type] || type

// 获取级别显示文本
const getLevelDisplay = (level) => levelMap[level] || level

// 获取状态显示文本
const getStatusDisplay = (status) => statusMap[status] || status

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

// 获取级别标签类型
const getLevelTagType = (level) => {
  const levelColors = {
    'school': '',
    'province': 'warning',
    'national': 'danger'
  }
  return levelColors[level] || ''
}

// 获取状态标签类型
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

// 获取文件名
const getFileName = (filePath) => {
  if (!filePath) return '未知文件'
  return filePath.split('/').pop()
}

// 获取文件类型
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

// 判断是否为图片文件
const isImageFile = (filePath) => {
  const ext = filePath.split('.').pop().toLowerCase()
  return ['jpg', 'jpeg', 'png', 'gif'].includes(ext)
}

// 注释：PDF预览功能已移除，只保留图片预览

// 获取文件完整URL
const getFileUrl = (filePath) => {
  // 如果是相对路径，添加基础URL
  if (filePath.startsWith('/')) {
    return `http://localhost:5000${filePath}`
  }
  return filePath
}

// 预览图片
const previewImage = (filePath) => {
  if (!isImageFile(filePath)) return
  
  const imageFiles = currentAchievement.value.evidence_files.filter(file => isImageFile(file))
  const imageIndex = imageFiles.findIndex(file => file === filePath)
  
  currentPreviewImage.value = filePath
  currentImageIndex.value = imageIndex >= 0 ? imageIndex : 0
  imagePreviewVisible.value = true
}

// 关闭图片预览
const closeImagePreview = () => {
  imagePreviewVisible.value = false
  currentPreviewImage.value = null
  currentImageIndex.value = 0
}

// 获取图片预览列表
const getImagePreviewList = () => {
  if (!currentAchievement.value?.evidence_files) return []
  
  return currentAchievement.value.evidence_files
    .filter(file => isImageFile(file))
    .map(file => getFileUrl(file))
}

// 下载文件
const downloadFile = (filePath) => {
  const link = document.createElement('a')
  link.href = getFileUrl(filePath)
  link.download = getFileName(filePath)
  link.target = '_blank'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

// 组件挂载时获取数据
onMounted(() => {
  fetchAchievements()
})
</script>

<style lang="scss" scoped>
.achievements-page {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
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
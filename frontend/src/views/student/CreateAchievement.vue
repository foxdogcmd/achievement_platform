<template>
  <div class="create-achievement-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>{{ isEdit ? '编辑成果' : '添加成果' }}</span>
          <el-button @click="$router.back()" type="info" plain>
            <el-icon><ArrowLeft /></el-icon>
            返回
          </el-button>
        </div>
      </template>
      
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="120px"
        class="achievement-form"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="成果名称" prop="title">
              <el-input
                v-model="form.title"
                placeholder="请输入成果名称"
                maxlength="200"
                show-word-limit
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="成果类型" prop="type">
              <el-select v-model="form.type" placeholder="请选择成果类型" style="width: 100%">
                <el-option 
                  v-for="option in configStore.achievementTypeOptions" 
                  :key="option.value"
                  :label="option.label" 
                  :value="option.value" 
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="获奖级别" prop="level">
              <el-select v-model="form.level" placeholder="请选择获奖级别" style="width: 100%">
                <el-option 
                  v-for="option in configStore.achievementLevelOptions" 
                  :key="option.value"
                  :label="option.label" 
                  :value="option.value" 
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="获奖时间" prop="award_date">
              <el-date-picker
                v-model="form.award_date"
                type="date"
                placeholder="请选择获奖时间"
                style="width: 100%"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="指导教师" prop="supervisor">
              <el-input
                v-model="form.supervisor"
                placeholder="请输入指导教师姓名，多个教师用逗号分隔"
                maxlength="100"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="所属队长" prop="leader_id">
              <el-select
                v-model="form.leader_id"
                placeholder="请选择所属队长"
                style="width: 100%"
                filterable
              >
                <el-option
                  v-for="leader in leaders"
                  :key="leader.user_id"
                  :label="leader.name"
                  :value="leader.user_id"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="成员名单" prop="members">
          <el-input
            v-model="membersText"
            type="textarea"
            :rows="3"
            placeholder="请输入成员姓名，每行一个或用逗号分隔"
            maxlength="500"
            show-word-limit
          />
          <div class="form-tip">
            提示：请输入参与该成果的所有成员姓名，包括您自己
          </div>
        </el-form-item>
        
        <el-form-item label="成果描述">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="4"
            placeholder="请详细描述该成果的内容、意义和价值（选填）"
            maxlength="1000"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item label="佐证材料" prop="evidence_files">
          <el-upload
            ref="uploadRef"
            class="upload-demo"
            drag
            :action="uploadAction"
            :headers="uploadHeaders"
            :on-success="handleUploadSuccess"
            :on-error="handleUploadError"
            :on-remove="handleRemove"
            :file-list="fileList"
            :before-upload="beforeUpload"
            multiple
            accept=".pdf,.jpg,.jpeg,.png"
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              将文件拖到此处，或<em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                支持 PDF、JPG、PNG 格式，单个文件不超过 10MB，总大小不超过 50MB
              </div>
            </template>
          </el-upload>
        </el-form-item>
        
      <el-form-item>
          <el-button type="primary" @click="submitForm" :loading="submitting" size="large">
            <el-icon><Check /></el-icon>
            {{ (isEdit && (currentStatus === 'draft' || currentStatus === 'returned')) ? '提交审核' : (isEdit ? '更新成果' : '提交审核') }}
          </el-button>
          <el-button
            v-if="!isEdit || (isEdit && (currentStatus === 'draft' || currentStatus === 'returned'))"
            @click="saveDraft"
            :loading="saving"
            size="large"
          >
            <el-icon><Document /></el-icon>
            保存草稿
          </el-button>
          <el-button @click="resetForm" size="large">
            <el-icon><Refresh /></el-icon>
            重置表单
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  ArrowLeft, 
  Check, 
  Document, 
  Refresh, 
  UploadFilled 
} from '@element-plus/icons-vue'
import { createAchievement, updateAchievement, getMyAchievements, getLeaders, saveDraftAchievement, updateDraftAchievement } from '@/api/student'
import { getToken } from '@/utils/auth'
import { API_BASE } from '@/utils/request'
import { useConfigStore } from '@/stores/config'

const router = useRouter()
const route = useRoute()
const configStore = useConfigStore()

// 判断是否为编辑模式
const isEdit = computed(() => !!route.query.edit)
const editId = computed(() => route.query.edit)
// 当前编辑成果的状态（用于控制按钮显示与文案）
const currentStatus = ref('')

// 表单引用
const formRef = ref()
const uploadRef = ref()

// 加载状态
const submitting = ref(false)
const saving = ref(false)

// 队长列表
const leaders = ref([])

// 文件列表
const fileList = ref([])

// 表单数据
const form = reactive({
  title: '',
  type: '',
  level: '',
  award_date: '',
  supervisor: '',
  leader_id: '',
  members: [],
  description: '',
  evidence_files: []
})

// 成员名单文本
const membersText = ref('')

// 表单验证规则
const rules = {
  title: [
    { required: true, message: '请输入成果名称', trigger: 'blur' },
    { min: 2, max: 200, message: '成果名称长度在 2 到 200 个字符', trigger: 'blur' }
  ],
  type: [
    { required: true, message: '请选择成果类型', trigger: 'change' }
  ],
  level: [
    { required: true, message: '请选择获奖级别', trigger: 'change' }
  ],
  award_date: [
    { required: true, message: '请选择获奖时间', trigger: 'change' }
  ],
  leader_id: [
    { required: true, message: '请选择所属队长', trigger: 'change' }
  ]
}

// 上传配置
// 统一走后端端口，避免生产环境 80 端口未代理导致 405
const uploadAction = computed(() => `${API_BASE}/upload`)
const uploadHeaders = computed(() => ({
  'Authorization': `Bearer ${getToken()}`
}))

// 获取队长列表
const fetchLeaders = async () => {
  try {
    const response = await getLeaders()
    leaders.value = response.data.leaders
  } catch (error) {
    ElMessage.error('获取队长列表失败')
  }
}

// 加载编辑数据
const loadEditData = async () => {
  if (!isEdit.value) return
  
  try {
    const response = await getMyAchievements({ achievement_id: editId.value })
    const achievement = response.data.achievements[0]
    
    if (achievement) {
      // 记录当前状态
      currentStatus.value = achievement.status
      // 填充表单数据
      Object.assign(form, {
        title: achievement.title,
        type: achievement.type,
        level: achievement.level,
        award_date: achievement.award_date,
        supervisor: achievement.supervisor || '',
        leader_id: achievement.leader_id,
        description: achievement.description || '',
        evidence_files: achievement.evidence_files || []
      })
      
      // 填充成员名单
      if (achievement.members && achievement.members.length > 0) {
        membersText.value = achievement.members.join('\n')
      }
      
      // 设置文件列表显示
      if (achievement.evidence_files && achievement.evidence_files.length > 0) {
        const fileBase = API_BASE.replace(/\/api$/, '')
        fileList.value = achievement.evidence_files.map((filePath, index) => ({
          name: filePath.split('/').pop(),
          url: filePath.startsWith('http') ? filePath : `${fileBase}${filePath}`,
          uid: index
        }))
      }
    }
  } catch (error) {
    ElMessage.error('加载成果数据失败')
    router.back()
  }
}

// 处理成员名单
const processMembers = () => {
  if (!membersText.value.trim()) {
    form.members = []
    return
  }
  
  // 支持换行符和逗号分隔
  const members = membersText.value
    .split(/[,，\n]/)
    .map(name => name.trim())
    .filter(name => name.length > 0)
  
  form.members = members
}

// 文件上传前检查
const beforeUpload = (file) => {
  const isValidType = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png'].includes(file.type)
  const isLt10M = file.size / 1024 / 1024 < 10
  
  if (!isValidType) {
    ElMessage.error('只能上传 PDF、JPG、PNG 格式的文件!')
    return false
  }
  if (!isLt10M) {
    ElMessage.error('单个文件大小不能超过 10MB!')
    return false
  }
  
  // 检查总文件大小
  const totalSize = fileList.value.reduce((total, file) => total + file.size, 0) + file.size
  if (totalSize / 1024 / 1024 > 50) {
    ElMessage.error('所有文件总大小不能超过 50MB!')
    return false
  }
  
  return true
}

// 文件上传成功
const handleUploadSuccess = (response) => {
  if (response.success) {
    form.evidence_files.push(response.data.file_path)
    ElMessage.success('文件上传成功')
  } else {
    ElMessage.error(response.message || '文件上传失败')
  }
}

// 文件上传失败
const handleUploadError = () => {
  ElMessage.error('文件上传失败，请重试')
}

// 移除文件
const handleRemove = (file) => {
  // 从evidence_files中移除对应的文件路径
  const index = form.evidence_files.findIndex(path => path.includes(file.name))
  if (index > -1) {
    form.evidence_files.splice(index, 1)
  }
}

// 提交表单
const submitForm = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      processMembers()
      
      submitting.value = true
      try {
        if (isEdit.value) {
          // 编辑模式：直接更新（并将状态改为pending以供审核）
          await updateAchievement(editId.value, {
            ...form,
            is_draft: false
          })
          const submitEditingDraft = currentStatus.value === 'draft' || currentStatus.value === 'returned'
          ElMessage.success(submitEditingDraft ? '成果提交成功，等待队长审核' : '成果更新成功')
        } else {
          // 创建模式：创建新成果（直接提交审核，不作为草稿）
          await createAchievement({
            ...form,
            is_draft: false
          })
          ElMessage.success('成果提交成功，等待队长审核')
        }
        router.push('/student/achievements')
      } catch (error) {
        ElMessage.error(error.response?.data?.message || (isEdit.value ? '更新失败' : '提交失败'))
      } finally {
        submitting.value = false
      }
    }
  })
}

// 保存草稿
const saveDraft = async () => {
  processMembers()
  
  saving.value = true
  try {
    const draftData = {
      title: form.title,
      type: form.type,
      level: form.level,
      award_date: form.award_date,
      supervisor: form.supervisor,
      leader_id: form.leader_id,
      members: form.members,
      description: form.description,
      evidence_files: form.evidence_files,
      is_draft: true
    }
    
    if (isEdit.value) {
      // 更新现有草稿
      await updateDraftAchievement(editId.value, draftData)
      ElMessage.success('草稿更新成功')
    } else {
      // 创建新草稿
      await saveDraftAchievement(draftData)
      ElMessage.success('草稿保存成功')
    }
    
    // 可选：保存到本地存储作为备份
    saveDraftToLocal(draftData)
    
    // 返回成就列表
    setTimeout(() => {
      router.push('/student/achievements')
    }, 1000)
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '保存草稿失败')
    console.error('保存草稿失败:', error)
  } finally {
    saving.value = false
  }
}

// 保存草稿到本地存储（作为备份）
const saveDraftToLocal = (data) => {
  try {
    const localDrafts = JSON.parse(localStorage.getItem('achievementDrafts') || '{}')
    const draftKey = isEdit.value ? `draft_${editId.value}` : `draft_${Date.now()}`
    localDrafts[draftKey] = {
      ...data,
      savedAt: new Date().toISOString()
    }
    localStorage.setItem('achievementDrafts', JSON.stringify(localDrafts))
  } catch (error) {
    console.warn('本地草稿保存失败:', error)
  }
}

// 重置表单
const resetForm = async () => {
  try {
    await ElMessageBox.confirm('确定要重置表单吗？所有已填写的内容将被清空。', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    formRef.value?.resetFields()
    membersText.value = ''
    form.members = []
    form.evidence_files = []
    fileList.value = []
    uploadRef.value?.clearFiles()
    
    ElMessage.success('表单已重置')
  } catch {
    // 用户取消
  }
}

// 组件挂载时获取数据
onMounted(async () => {
  try {
    // 使用智能加载，自动判断是否需要刷新配置
    await configStore.smartLoadConfig()
  } catch (error) {
    console.error('配置加载失败，使用默认配置:', error)
  }
  
  await fetchLeaders()
  if (isEdit.value) {
    await loadEditData()
  }
})
</script>

<style lang="scss" scoped>
.create-achievement-page {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .achievement-form {
    max-width: 1000px;
    margin: 0 auto;
    
    .form-tip {
      font-size: 12px;
      color: #909399;
      margin-top: 5px;
    }
    
    .upload-demo {
      width: 100%;
      
      :deep(.el-upload-dragger) {
        width: 100%;
      }
    }
    
    .el-form-item {
      margin-bottom: 24px;
    }
    
    .el-button {
      margin-right: 12px;
      
      &:last-child {
        margin-right: 0;
      }
    }
  }
}
</style>
<template>
  <div class="register-container" :class="{ 'dark-mode': isDarkMode }">
    <div class="register-card">
      <div class="register-header">
        <h2>用户注册</h2>
        <p class="subtitle">请填写以下信息完成注册</p>
      </div>

      <el-form ref="formRef" :model="form" :rules="rules" label-width="92px" class="register-form">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入学号/工号" @blur="trim('username')" />
        </el-form-item>

        <el-form-item label="姓名" prop="name">
          <el-input v-model="form.name" placeholder="请输入姓名" @blur="trim('name')" />
        </el-form-item>

        <el-form-item label="角色">
          <el-select v-model="form.role" disabled>
            <el-option label="学生" value="student" />
          </el-select>
          <span class="role-tip">注册默认创建学生账号，如需队长/管理员请联系管理员</span>
        </el-form-item>

        <el-form-item label="班级" prop="class_id">
          <el-select v-model="form.class_id" filterable placeholder="请选择班级">
            <el-option v-for="cls in classOptions" :key="cls.class_id" :label="`${cls.class_name}（${cls.college}）`" :value="cls.class_id" />
          </el-select>
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="至少6位" show-password />
        </el-form-item>

        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="form.confirmPassword" type="password" placeholder="再次输入密码" show-password />
        </el-form-item>

        <div class="actions">
          <el-button type="primary" :loading="submitting" @click="handleSubmit">注册</el-button>
          <el-button link @click="goLogin">已有账号？去登录</el-button>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { useThemeStore } from '@/stores/theme'
import { storeToRefs } from 'pinia'
import { getPublicClasses } from '@/api/public'

const router = useRouter()
const userStore = useUserStore()
const themeStore = useThemeStore()
const { isDarkMode } = storeToRefs(themeStore)

const formRef = ref(null)
const submitting = ref(false)
const classOptions = ref([])

const form = reactive({
  username: '',
  name: '',
  role: 'student',
  class_id: '',
  password: '',
  confirmPassword: ''
})

const rules = {
  username: [
    { required: true, message: '请输入学号/工号', trigger: 'blur' },
    { min: 3, message: '用户名至少3个字符', trigger: 'blur' }
  ],
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' }
  ],
  class_id: [
    { required: true, message: '请选择班级', trigger: 'change' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== form.password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

const trim = (field) => {
  if (typeof form[field] === 'string') {
    form[field] = form[field].trim()
  }
}

const fetchClasses = async () => {
  try {
    const { data } = await getPublicClasses()
    classOptions.value = data.classes || []
  } catch (error) {
    ElMessage.error('获取班级列表失败，请稍后重试')
  }
}

onMounted(() => {
  fetchClasses()
})

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    submitting.value = true
    try {
      const payload = {
        username: form.username,
        name: form.name,
        role: form.role,
        class_id: form.class_id,
        password: form.password
      }
      const result = await userStore.register(payload)
      if (result.success) {
        ElMessage.success('注册成功，请登录')
        router.push('/login')
      } else {
        ElMessage.error(result.message || '注册失败')
      }
    } catch (error) {
      ElMessage.error('注册失败，请稍后重试')
    } finally {
      submitting.value = false
    }
  })
}

const goLogin = () => {
  router.push('/login')
}
</script>

<style lang="scss" scoped>
.register-container {
  min-height: 100vh;
  background: url('~@/assets/back.jpg') center center/cover no-repeat;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  position: relative;
  transition: all 0.3s ease;

  &.dark-mode {
    filter: brightness(0.4);

    &::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0, 0, 0, 0.5);
      pointer-events: none;
    }
  }
}

.register-card {
  width: 560px;
  max-width: 92vw;
  background: rgba(255, 255, 255, 0.92);
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.15);
  padding: 24px;
  backdrop-filter: blur(6px);
}

.register-header {
  margin-bottom: 12px;
  h2 {
    margin: 0;
    font-size: 22px;
    font-weight: 600;
  }
  .subtitle {
    margin-top: 6px;
    color: #666;
    font-size: 14px;
  }
}

.register-form {
  .el-select, .el-input {
    width: 100%;
  }
}

.role-tip {
  margin-left: 10px;
  color: #888;
  font-size: 13px;
}

.actions {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 12px;
}
</style>
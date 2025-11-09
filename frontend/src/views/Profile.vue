<template>
  <div class="profile-page">
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>个人信息</span>
            </div>
          </template>

          <el-form :model="profileForm" :rules="profileRules" ref="profileFormRef" label-width="100px">
            <el-form-item label="用户名">
              <el-input v-model="profileForm.username" disabled />
            </el-form-item>

            <el-form-item label="角色">
              <el-input :value="roleDisplay" disabled />
            </el-form-item>

            <el-form-item label="所属班级">
              <el-input :value="userStore.user?.class_name || '—'" disabled />
            </el-form-item>

            <el-form-item label="姓名" prop="name">
              <el-input v-model="profileForm.name" placeholder="请输入姓名" />
            </el-form-item>

            <el-form-item>
              <el-button type="primary" :loading="savingProfile" @click="saveProfile">保存</el-button>
              <el-button @click="resetProfile">重置</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>修改密码</span>
            </div>
          </template>

          <el-form :model="passwordForm" :rules="passwordRules" ref="passwordFormRef" label-width="100px">
            <el-form-item label="旧密码" prop="old_password">
              <el-input v-model="passwordForm.old_password" type="password" show-password placeholder="请输入旧密码" />
            </el-form-item>

            <el-form-item label="新密码" prop="new_password">
              <el-input v-model="passwordForm.new_password" type="password" show-password placeholder="请输入新密码（至少6位）" />
            </el-form-item>

            <el-form-item label="确认新密码" prop="confirm_password">
              <el-input v-model="passwordForm.confirm_password" type="password" show-password placeholder="请再次输入新密码" />
            </el-form-item>

            <el-form-item>
              <el-button type="warning" :loading="savingPassword" @click="savePassword">修改密码</el-button>
              <el-button @click="resetPassword">重置</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { updateUserProfile, changePassword } from '@/api/auth'

const userStore = useUserStore()

// 个人信息表单
const profileFormRef = ref(null)
const profileForm = ref({
  username: '',
  name: ''
})
const savingProfile = ref(false)

const roleDisplay = computed(() => {
  const role = userStore.user?.role
  if (role === 'student') return '学生'
  if (role === 'team_leader') return '队长'
  if (role === 'admin') return '管理员'
  return role || '—'
})

const profileRules = {
  name: [
    { required: true, message: '姓名不能为空', trigger: 'blur' },
    { min: 2, max: 30, message: '姓名长度应为2-30字符', trigger: 'blur' }
  ]
}

const resetProfile = () => {
  profileForm.value.username = userStore.user?.username || ''
  profileForm.value.name = userStore.user?.name || ''
}

const saveProfile = async () => {
  try {
    await profileFormRef.value.validate()
    savingProfile.value = true
    const resp = await updateUserProfile({ name: profileForm.value.name })
    // 同步用户信息
    userStore.updateUser(resp.data.user)
    ElMessage.success('个人信息更新成功')
  } catch (e) {
    const msg = e?.response?.data?.message || '更新失败'
    ElMessage.error(msg)
  } finally {
    savingProfile.value = false
  }
}

// 修改密码表单
const passwordFormRef = ref(null)
const passwordForm = ref({
  old_password: '',
  new_password: '',
  confirm_password: ''
})
const savingPassword = ref(false)

const passwordRules = {
  old_password: [{ required: true, message: '请填写旧密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请填写新密码', trigger: 'blur' },
    { min: 6, message: '新密码至少6位', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请填写确认密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== passwordForm.value.new_password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

const resetPassword = () => {
  passwordForm.value.old_password = ''
  passwordForm.value.new_password = ''
  passwordForm.value.confirm_password = ''
}

const savePassword = async () => {
  try {
    await passwordFormRef.value.validate()
    savingPassword.value = true
    await changePassword({
      old_password: passwordForm.value.old_password,
      new_password: passwordForm.value.new_password
    })
    ElMessage.success('密码修改成功')
    resetPassword()
  } catch (e) {
    const msg = e?.response?.data?.message || '修改失败'
    ElMessage.error(msg)
  } finally {
    savingPassword.value = false
  }
}

onMounted(() => {
  resetProfile()
})
</script>

<style lang="scss" scoped>
.profile-page {
  .card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-weight: 500;
  }
}
</style>
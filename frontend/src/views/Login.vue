<template>
  <div class="login-container" :class="{ 'dark-mode': isDarkMode }">
    <!-- 夜间模式切换按钮 -->
    <ThemeToggle />

    <div class="form-control" :class="{ 'dark': isDarkMode }">
      <!-- 返回按钮 -->
      <button class="back-btn" @click="goBack" title="返回上一页">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
          <path d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z"/>
        </svg>
        返回
      </button>
      
      <div class="login-header">
        <h2 class="title">信息网络安全学院</h2>
        <h3 class="subtitle">学生成果登记与管理系统</h3>
      </div>
      
      <div class="input-field">
         <input 
           v-model="loginForm.username"
           required 
           class="input" 
           type="text"
           @blur="validateField('username')"
         />
         <label class="label">请输入学号/工号</label>
       </div>
       
       <div class="input-field">
         <input 
           v-model="loginForm.password"
           required 
           class="input" 
           type="password"
           @blur="validateField('password')"
           @keyup.enter="handleLogin"
         />
         <label class="label">请输入密码</label>
       </div>
      
      <button 
        class="submit-btn" 
        :disabled="loading"
        @click="handleLogin"
      >
        {{ loading ? '登录中...' : '登录' }}
      </button>
      
  <div class="login-footer">
        <p>请使用学号/工号和密码登录系统</p>
        <p class="register-tip">
          还没有账号？
          <a href="#" @click.prevent="goRegister">去注册</a>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { useThemeStore } from '@/stores/theme'
import { storeToRefs } from 'pinia'
import ThemeToggle from '@/components/ThemeToggle.vue'

const router = useRouter()
const userStore = useUserStore()
const themeStore = useThemeStore()

const { isDarkMode } = storeToRefs(themeStore)

const loading = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const errors = reactive({
  username: '',
  password: ''
})

// 表单验证
const validateField = (field) => {
  errors[field] = ''
  
  if (field === 'username') {
    if (!loginForm.username.trim()) {
      errors.username = '请输入学号/工号'
    }
  }
  
  if (field === 'password') {
    if (!loginForm.password) {
      errors.password = '请输入密码'
    } else if (loginForm.password.length < 6) {
      errors.password = '密码长度不能少于6位'
    }
  }
}

// 验证整个表单
const validateForm = () => {
  validateField('username')
  validateField('password')
  
  return !errors.username && !errors.password && loginForm.username && loginForm.password
}

const handleLogin = async () => {
  if (!validateForm()) {
    ElMessage.error('请填写完整的登录信息')
    return
  }
  
  loading.value = true
  
  try {
    const result = await userStore.login(loginForm)
    
    if (result.success) {
      ElMessage.success('登录成功')
      
      // 根据用户角色跳转到对应页面
      const roleRoutes = {
        'student': '/student',
        'team_leader': '/leader',
        'admin': '/admin'
      }
      
      router.push(roleRoutes[result.user.role] || '/dashboard')
    } else {
      ElMessage.error(result.message)
    }
  } catch (error) {
    ElMessage.error('登录失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 返回上一页功能
const goBack = () => {
  router.replace('/')
}

// 跳转注册页
const goRegister = () => {
  router.push('/register')
}
</script>

<style lang="scss" scoped>
.login-container {
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

.register-tip {
  margin-top: 8px;
  font-size: 14px;
}



.form-control {
  margin: 20px;
  background-color: #ffffff;
  box-shadow: 0 15px 25px rgba(0, 0, 0, 0.6);
  width: 400px;
  display: flex;
  justify-content: center;
  flex-direction: column;
  gap: 10px;
  padding: 25px;
  border-radius: 16px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  position: relative;
  z-index: 10;
  transition: all 0.3s ease;
  
  &.dark {
    background-color: rgba(30, 30, 30, 0.95);
    color: #ffffff;
    box-shadow: 0 15px 25px rgba(0, 0, 0, 0.8);
  }
}

.back-btn {
  position: absolute;
  top: 15px;
  left: 15px;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  color: #666;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(5px);
  
  svg {
    width: 16px;
    height: 16px;
  }
  
  &:hover {
    background: rgba(255, 255, 255, 1);
    color: #2d79f3;
    border-color: #2d79f3;
    transform: translateX(-2px);
  }
  
  .form-control.dark & {
    background: rgba(50, 50, 50, 0.9);
    color: #ccc;
    border-color: rgba(255, 255, 255, 0.2);
    
    &:hover {
      background: rgba(70, 70, 70, 1);
      color: #4a9eff;
      border-color: #4a9eff;
    }
  }
}

.login-header {
  text-align: center;
  margin-bottom: 20px;
  
  .title {
    font-size: 24px;
    font-weight: 700;
    margin-bottom: 8px;
    color: #333;
    text-shadow: 2px 2px 6px rgba(0, 0, 0, 0.3);
    
    .form-control.dark & {
      color: #ffffff;
      text-shadow: 2px 2px 6px rgba(0, 0, 0, 0.8);
    }
  }
  
  .subtitle {
    font-size: 16px;
    font-weight: 500;
    color: #666;
    text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.3);
    
    .form-control.dark & {
      color: #cccccc;
      text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.8);
    }
  }
}

.input-field {
  position: relative;
  width: 100%;
  margin-bottom: 20px;
}

.input {
  margin-top: 15px;
  width: 100%;
  outline: none;
  border-radius: 8px;
  height: 45px;
  border: 1.5px solid #ecedec;
  background: transparent;
  padding-left: 10px;
  font-size: 16px;
  transition: all 0.3s ease;
  
  .form-control.dark & {
    border-color: #555;
    background: rgba(255, 255, 255, 0.1);
    color: #ffffff;
    
    &::placeholder {
      color: #aaa;
    }
  }
  
  &:focus {
    border: 1.5px solid #2d79f3;
    
    .form-control.dark & {
      border-color: #4a9eff;
    }
  }
}

.input-field .label {
  position: absolute;
  top: 25px;
  left: 15px;
  color: #ccc;
  transition: all 0.3s ease;
  pointer-events: none;
  z-index: 2;
  background: transparent;
  
  .form-control.dark & {
    color: #aaa;
  }
}

.input-field .input:focus ~ .label,
.input-field .input:valid ~ .label {
  top: 5px;
  left: 5px;
  font-size: 12px;
  color: #2d79f3;
  background-color: #ffffff;
  padding-left: 5px;
  padding-right: 5px;
  
  .form-control.dark & {
    color: #4a9eff;
    background-color: rgba(30, 30, 30, 0.95);
  }
}



.submit-btn {
  margin-top: 30px;
  height: 55px;
  border-radius: 11px;
  border: 0;
  outline: none;
  color: #ffffff;
  font-size: 18px;
  font-weight: 700;
  background: linear-gradient(180deg, #4a9eff 0%, #2d79f3 50%, #1e5bb8 100%);
  box-shadow: 0px 0px 0px 0px #4a9eff, 0px 0px 0px 0px rgba(74, 158, 255, 0.3);
  transition: all 0.3s cubic-bezier(0.15, 0.83, 0.66, 1);
  cursor: pointer;
  
  &:hover:not(:disabled) {
    box-shadow: 0px 0px 0px 2px #4a9eff, 0px 0px 0px 4px rgba(74, 158, 255, 0.3);
    transform: translateY(-2px);
  }
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
  }
  
  .form-control.dark & {
    background: linear-gradient(180deg, #5ba3ff 0%, #3d85f5 50%, #2668c7 100%);
    
    &:hover:not(:disabled) {
      box-shadow: 0px 0px 0px 2px #5ba3ff, 0px 0px 0px 4px rgba(91, 163, 255, 0.3);
    }
  }
}

.login-footer {
  text-align: center;
  margin-top: 20px;
  
  p {
    color: #666;
    font-size: 14px;
    margin: 0;
    
    .form-control.dark & {
      color: #aaa;
    }
  }
}

@media (max-width: 768px) {
  .form-control {
    width: 90%;
    max-width: 350px;
    padding: 20px;
  }
  
  .mode-toggle {
    top: 15px;
    right: 15px;
    
    .toggle-btn {
      width: 40px;
      height: 40px;
      font-size: 16px;
    }
  }
}
</style>
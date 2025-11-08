<template>
  <div class="home-container" :class="{ 'dark-mode': isDarkMode }">
    <!-- 主题切换按钮 -->
    <ThemeToggle />
    
    <!-- 加载动画 -->
    <div v-if="showLoading" class="loading-overlay">
      <div class="bg">
        <div class="loader"></div>
      </div>
    </div>

    <!-- 主要内容 -->
    <div v-else class="main-content">
      <div class="header">
        <h1 class="title">信息网络安全学院</h1>
        <h2 class="subtitle">学生成果登记与管理系统</h2>
      </div>
      
      <div class="cards">
        <div class="card login-card" @click="goToLogin">
          <div class="card-icon">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
            </svg>
          </div>
          <p class="card-title">登录</p>
          <p class="card-description">进入系统管理</p>
        </div>
        
        <div class="card display-card" @click="goToDisplay">
          <div class="card-icon">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
            </svg>
          </div>
          <p class="card-title">展示</p>
          <p class="card-description">查看成果展示</p>
        </div>
      </div>
      
      <div class="footer">
        <p>&copy; 2024 信息网络安全学院 学生成果管理系统</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useThemeStore } from '@/stores/theme'
import { storeToRefs } from 'pinia'
import ThemeToggle from '@/components/ThemeToggle.vue'

const router = useRouter()
const themeStore = useThemeStore()
const { isDarkMode } = storeToRefs(themeStore)

const showLoading = ref(true)

onMounted(() => {
  // 显示加载动画0.5秒
  setTimeout(() => {
    showLoading.value = false
  }, 500)
})

const goToLogin = () => {
  router.push('/login')
}

const goToDisplay = () => {
  router.push('/display')
}
</script>

<style scoped>
.home-container {
  min-height: 100vh;
  position: relative;
  background: url('~@/assets/back.jpg') center center/cover no-repeat;
  overflow: hidden;
}

/* 加载动画样式 */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

.bg {
  padding: 20px;
  border-radius: 10px;
  background-color: var(--base-color);
  --base-color: #1e3a8a;
}

.loader {
  width: 60px;
  height: 40px;
  position: relative;
  display: inline-block;
  background-color: var(--base-color);
}

.loader::before {
  content: '';
  left: 0;
  top: 0;
  position: absolute;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background-color: #FFF;
  background-image: radial-gradient(circle 8px at 18px 18px, var(--base-color) 100%, transparent 0), radial-gradient(circle 4px at 18px 0px, var(--base-color) 100%, transparent 0), radial-gradient(circle 4px at 0px 18px, var(--base-color) 100%, transparent 0), radial-gradient(circle 4px at 36px 18px, var(--base-color) 100%, transparent 0), radial-gradient(circle 4px at 18px 36px, var(--base-color) 100%, transparent 0), radial-gradient(circle 4px at 30px 5px, var(--base-color) 100%, transparent 0), radial-gradient(circle 4px at 30px 5px, var(--base-color) 100%, transparent 0), radial-gradient(circle 4px at 30px 30px, var(--base-color) 100%, transparent 0), radial-gradient(circle 4px at 5px 30px, var(--base-color) 100%, transparent 0), radial-gradient(circle 4px at 5px 5px, var(--base-color) 100%, transparent 0);
  background-repeat: no-repeat;
  box-sizing: border-box;
  animation: rotationBack 3s linear infinite;
}

.loader::after {
  content: '';
  left: 35px;
  top: 15px;
  position: absolute;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background-color: #FFF;
  background-image: radial-gradient(circle 5px at 12px 12px, var(--base-color) 100%, transparent 0), radial-gradient(circle 2.5px at 12px 0px, var(--base-color) 100%, transparent 0), radial-gradient(circle 2.5px at 0px 12px, var(--base-color) 100%, transparent 0), radial-gradient(circle 2.5px at 24px 12px, var(--base-color) 100%, transparent 0), radial-gradient(circle 2.5px at 12px 24px, var(--base-color) 100%, transparent 0), radial-gradient(circle 2.5px at 20px 3px, var(--base-color) 100%, transparent 0), radial-gradient(circle 2.5px at 20px 3px, var(--base-color) 100%, transparent 0), radial-gradient(circle 2.5px at 20px 20px, var(--base-color) 100%, transparent 0), radial-gradient(circle 2.5px at 3px 20px, var(--base-color) 100%, transparent 0), radial-gradient(circle 2.5px at 3px 3px, var(--base-color) 100%, transparent 0);
  background-repeat: no-repeat;
  box-sizing: border-box;
  animation: rotationBack 4s linear infinite reverse;
}

@keyframes rotationBack {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(-360deg);
  }
}

/* 主要内容样式 */
.main-content {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 2rem;
  animation: fadeIn 0.8s ease-in-out;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(5px);
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.header {
  text-align: center;
  margin-bottom: 3rem;
  color: #ffffff;
  text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.8), 0 0 10px rgba(0, 0, 0, 0.6);
}

.title {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.subtitle {
  font-size: 1.5rem;
  font-weight: 500;
  opacity: 1;
  color: #ffffff;
  text-shadow: 2px 2px 6px rgba(0, 0, 0, 0.8), 0 0 8px rgba(0, 0, 0, 0.6);
}

.cards {
  display: flex;
  gap: 2rem;
  margin-bottom: 3rem;
}

.card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 200px;
  height: 160px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  border: 2px solid rgba(255, 255, 255, 0.3);
  backdrop-filter: blur(10px);
}

.card:hover {
  transform: translateY(-8px);
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.3);
  background: rgba(255, 255, 255, 0.95);
}

.login-card {
  border-color: #3b82f6;
  color: #3b82f6;
}

.login-card:hover {
  border-color: #2563eb;
  color: #2563eb;
  background: #f8faff;
}

.display-card {
  border-color: #06b6d4;
  color: #06b6d4;
}

.display-card:hover {
  border-color: #0891b2;
  color: #0891b2;
  background: #f0fdff;
}

.card-icon {
  width: 48px;
  height: 48px;
  margin-bottom: 1rem;
  opacity: 0.9;
}

.card-icon svg {
  width: 100%;
  height: 100%;
}

.card-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.card-description {
  font-size: 0.875rem;
  opacity: 0.8;
  text-align: center;
}

.footer {
  color: #ffffff;
  text-align: center;
  opacity: 0.95;
  font-size: 0.875rem;
  font-weight: 500;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8), 0 0 6px rgba(0, 0, 0, 0.6);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .title {
    font-size: 2rem;
  }
  
  .subtitle {
    font-size: 1.25rem;
  }
  
  .cards {
    flex-direction: column;
    gap: 1.5rem;
  }
  
  .card {
    width: 280px;
  }
}
</style>
<template>
  <div class="layout-container" :class="{ 'dark-mode': isDarkMode }">
    <!-- 主题切换按钮 -->
    <ThemeToggle />
    
    <el-container>
      <!-- 顶部导航 -->
      <el-header class="layout-header">
        <div class="header-left">
          <h2>信息网络安全学院学生成果管理系统</h2>
        </div>
        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <el-icon><User /></el-icon>
              {{ userStore.userName }}
              <el-icon class="el-icon--right"><arrow-down /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人信息</el-dropdown-item>
                <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-container>
        <!-- 侧边栏 -->
        <el-aside class="layout-aside" width="200px">
          <el-menu
            :default-active="$route.path"
            class="sidebar-menu"
            router
            unique-opened
          >
            <!-- 学生菜单 -->
            <template v-if="userStore.userRole === 'student'">
              <el-menu-item index="/student">
                <el-icon><House /></el-icon>
                <span>控制台</span>
              </el-menu-item>
              <el-menu-item index="/student/achievements">
                <el-icon><Document /></el-icon>
                <span>我的成果</span>
              </el-menu-item>
              <el-menu-item index="/student/achievements/create">
                <el-icon><Plus /></el-icon>
                <span>添加成果</span>
              </el-menu-item>
            </template>

            <!-- 队长菜单 -->
            <template v-if="userStore.userRole === 'team_leader'">
              <el-menu-item index="/leader">
                <el-icon><House /></el-icon>
                <span>控制台</span>
              </el-menu-item>
              <el-menu-item index="/leader/audit">
                <el-icon><Check /></el-icon>
                <span>成果审核</span>
              </el-menu-item>
              <el-menu-item index="/leader/manage">
                <el-icon><Setting /></el-icon>
                <span>成果管理</span>
              </el-menu-item>
            </template>

            <!-- 管理员菜单 -->
            <template v-if="userStore.userRole === 'admin'">
              <el-menu-item index="/admin">
                <el-icon><House /></el-icon>
                <span>控制台</span>
              </el-menu-item>
              <el-menu-item index="/admin/users">
                <el-icon><User /></el-icon>
                <span>用户管理</span>
              </el-menu-item>
              <el-menu-item index="/admin/config">
                <el-icon><School /></el-icon>
                <span>系统配置</span>
              </el-menu-item>
              <el-menu-item index="/display">
                <el-icon><DataBoard /></el-icon>
                <span>成果展示</span>
              </el-menu-item>
              <el-menu-item index="/admin/monitor">
                <el-icon><Document /></el-icon>
                <span>数据监控</span>
              </el-menu-item>
            </template>
          </el-menu>
        </el-aside>

        <!-- 主内容区 -->
        <el-main class="layout-main">
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { useThemeStore } from '@/stores/theme'
import { storeToRefs } from 'pinia'
import ThemeToggle from '@/components/ThemeToggle.vue'
import { 
  User, 
  ArrowDown, 
  House, 
  Document, 
  Plus, 
  Check, 
  Setting,
  School,
  DataBoard
} from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()
const themeStore = useThemeStore()
const { isDarkMode } = storeToRefs(themeStore)

const handleCommand = async (command) => {
  switch (command) {
    case 'profile':
      // 跳转到个人信息页面
      break
    case 'logout':
      try {
        await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        
        userStore.logout()
        ElMessage.success('已退出登录')
        router.push('/login')
      } catch {
        // 用户取消
      }
      break
  }
}
</script>

<style lang="scss" scoped>
.layout-container {
  height: 100vh;
  background-color: var(--bg-secondary);
  transition: background-color 0.3s ease;
  overflow: hidden;
}

.layout-header {
  background: var(--bg-primary);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  transition: all 0.3s ease;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  
  .header-left h2 {
    margin: 0;
    color: var(--text-primary);
    font-size: 18px;
    font-weight: 500;
  }
  
  .header-right {
    .user-info {
      display: flex;
      align-items: center;
      cursor: pointer;
      color: var(--text-secondary);
      transition: color 0.3s ease;
      
      &:hover {
        color: var(--primary-color);
      }
      
      .el-icon {
        margin: 0 4px;
      }
    }
  }
}

.layout-aside {
  background: var(--bg-primary);
  border-right: 1px solid var(--border-color);
  transition: all 0.3s ease;
  position: fixed;
  top: 60px;
  left: 0;
  bottom: 0;
  z-index: 99;
  overflow-y: auto;
  
  .sidebar-menu {
    border-right: none;
    height: 100%;
    background: var(--bg-primary);
  }
}

.layout-main {
  background: var(--bg-secondary);
  padding: 20px;
  transition: background-color 0.3s ease;
  margin-left: 200px;
  margin-top: 60px;
  height: calc(100vh - 60px);
  overflow-y: auto;
}

// 暗色主题下的特殊样式
.dark-mode {
  :deep(.el-container) {
    background-color: var(--bg-secondary);
  }
  
  :deep(.el-menu) {
    background-color: var(--bg-primary);
    
    .el-menu-item {
      color: var(--text-secondary);
      
      &:hover {
        background-color: var(--bg-tertiary);
        color: var(--primary-color);
      }
      
      &.is-active {
        background-color: var(--primary-light);
        color: var(--primary-color);
      }
    }
  }
  
  :deep(.el-dropdown-menu) {
    background-color: var(--bg-primary);
    border-color: var(--border-color);
    
    .el-dropdown-menu__item {
      color: var(--text-primary);
      
      &:hover {
        background-color: var(--bg-tertiary);
        color: var(--primary-color);
      }
    }
  }

  // 输入计数（例如 0 / 200）在暗色模式下的颜色
  :deep(.el-input__count),
  :deep(.el-input__count-inner) {
    color: var(--text-secondary);
    background: transparent;
  }
  
  // 修复各种组件的夜间模式样式
  :deep(.el-card) {
    background-color: var(--bg-primary);
    border-color: var(--border-color);
    color: var(--text-primary);
    
    .el-card__header {
      background-color: var(--bg-primary);
      border-bottom-color: var(--border-color);
      color: var(--text-primary);
    }
    
    .el-card__body {
      background-color: var(--bg-primary);
      color: var(--text-primary);
    }
  }
  
  :deep(.el-table) {
    background-color: var(--bg-primary);
    color: var(--text-primary);
    
    .el-table__header {
      background-color: var(--bg-secondary) !important;
      color: var(--text-primary) !important;
      
      th {
        background-color: var(--bg-secondary) !important;
        color: var(--text-primary) !important;
        border-bottom-color: var(--border-color) !important;
      }
      
      .el-table__cell {
        background-color: var(--bg-secondary) !important;
        color: var(--text-primary) !important;
        
        .cell {
          color: var(--text-primary) !important;
        }
      }
    }
    
    // 额外的表头样式覆盖
    thead {
      background-color: var(--bg-secondary) !important;
      
      th {
        background-color: var(--bg-secondary) !important;
        color: var(--text-primary) !important;
        
        .cell {
          color: var(--text-primary) !important;
        }
      }
    }
    
    .el-table__body {
      background-color: var(--bg-primary);
      
      tr {
        background-color: var(--bg-primary);
        
        // 条纹效果 - 偶数行
        &.el-table__row--striped {
          background-color: var(--bg-secondary);
          
          td {
            background-color: var(--bg-secondary);
          }
        }
        
        // 悬停效果
        &:hover {
          background-color: var(--bg-tertiary) !important;
          
          td {
            background-color: var(--bg-tertiary) !important;
          }
        }
        
        td {
          border-bottom-color: var(--border-color);
          color: var(--text-primary);
          background-color: inherit;
        }
      }
    }
    
    // 确保条纹表格的样式正确
    &.el-table--striped {
      .el-table__body {
        tr.el-table__row--striped {
          background-color: var(--bg-secondary);
          
          td {
            background-color: var(--bg-secondary);
          }
          
          &:hover {
            background-color: var(--bg-tertiary) !important;
            
            td {
              background-color: var(--bg-tertiary) !important;
            }
          }
        }
      }
    }
  }
  
  :deep(.el-input) {
    .el-input__wrapper {
      background-color: var(--bg-primary);
      border-color: var(--border-color);
      color: var(--text-primary);
      
      &:hover {
        border-color: var(--primary-color);
      }
      
      &.is-focus {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 1px var(--primary-color);
      }
    }
    
    .el-input__inner {
      color: var(--text-primary);
      
      &::placeholder {
        color: var(--text-tertiary);
      }
    }
  }
  
  :deep(.el-textarea) {
    .el-textarea__inner {
      background-color: var(--bg-primary);
      border-color: var(--border-color);
      color: var(--text-primary);
      
      &:hover {
        border-color: var(--primary-color);
      }
      
      &:focus {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 1px var(--primary-color);
      }
      
      &::placeholder {
        color: var(--text-tertiary);
      }
    }
  }
  
  :deep(.el-select) {
    .el-select__wrapper {
      background-color: var(--bg-primary);
      border-color: var(--border-color);
      color: var(--text-primary);
      
      &:hover {
        border-color: var(--primary-color);
      }
      
      &.is-focus {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 1px var(--primary-color);
      }
    }

    .el-select__placeholder {
      color: var(--text-tertiary);
    }

    .el-select__selection {
      color: var(--text-primary);
    }
  }
  
  :deep(.el-button--default) {
    background-color: var(--bg-primary);
    border-color: var(--border-color);
    color: var(--text-primary);
    
    &:hover {
      border-color: var(--primary-color);
      color: var(--primary-color);
    }
  }
  
  :deep(.el-button--primary) {
    background-color: var(--primary-color);
    border-color: var(--primary-color);
    
    &:hover {
      background-color: var(--primary-hover);
      border-color: var(--primary-hover);
    }
  }
  
  :deep(.el-form-item__label) {
    color: var(--text-primary);
  }
  
  :deep(.el-upload) {
    .el-upload-dragger {
      background-color: var(--bg-secondary);
      border-color: var(--border-color);
      color: var(--text-secondary);
      
      &:hover {
        border-color: var(--primary-color);
      }
    }
  }
  
  :deep(.el-pagination) {
    .el-pagination__total,
    .el-pagination__goto,
    .el-pagination__classifier {
      color: var(--text-primary);
    }
    
    .btn-prev,
    .btn-next {
      background-color: var(--bg-primary);
      color: var(--text-primary);
      
      &:hover {
        color: var(--primary-color);
      }
    }
    
    .el-pager li {
      background-color: var(--bg-primary);
      color: var(--text-primary);
      
      &:hover {
        color: var(--primary-color);
      }
      
      &.is-active {
        background-color: var(--primary-color);
        color: white;
      }
    }
  }
  
  :deep(.el-tag--success) {
    background-color: rgba(16, 185, 129, 0.1);
    border-color: rgba(16, 185, 129, 0.2);
    color: #10b981;
  }
  
  :deep(.el-tag--danger) {
    background-color: rgba(239, 68, 68, 0.1);
    border-color: rgba(239, 68, 68, 0.2);
    color: #ef4444;
  }
  
  :deep(.el-tag--warning) {
    background-color: rgba(245, 158, 11, 0.1);
    border-color: rgba(245, 158, 11, 0.2);
    color: #f59e0b;
  }
  
  :deep(.el-tag--info) {
    background-color: rgba(6, 182, 212, 0.1);
    border-color: rgba(6, 182, 212, 0.2);
    color: #06b6d4;
  }

  // info 按钮（返回等），plain 变体与普通变体在暗色模式下的样式
  :deep(.el-button--info) {
    background-color: var(--info-color);
    border-color: var(--info-color);
    color: #fff;

    &:hover {
      filter: brightness(1.1);
    }
  }

  :deep(.el-button--info.is-plain) {
    background-color: var(--bg-primary);
    border-color: var(--border-color);
    color: var(--text-primary);

    &:hover {
      border-color: var(--primary-color);
      color: var(--primary-color);
      background-color: var(--bg-tertiary);
    }
  }

  // 兜底：无修饰类的按钮在暗色模式下不显白
  :deep(.el-button) {
    background-color: var(--bg-primary);
    border-color: var(--border-color);
    color: var(--text-primary);

    &:hover {
      border-color: var(--primary-color);
      color: var(--primary-color);
    }
  }

  // 页面内的筛选区容器在暗色模式下不显白
  :deep(.filter-section) {
    background-color: var(--bg-secondary) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 6px !important;
    color: var(--text-primary) !important;
    padding: 16px !important;
    
    // 筛选区内的所有输入组件
    .el-input__wrapper {
      background-color: var(--bg-primary) !important;
      border-color: var(--border-color) !important;
      color: var(--text-primary) !important;
      
      &:hover {
        border-color: var(--primary-color) !important;
      }
      
      &.is-focus {
        border-color: var(--primary-color) !important;
        box-shadow: 0 0 0 1px var(--primary-color) !important;
      }
    }
    
    .el-input__inner {
      color: var(--text-primary) !important;
      background-color: transparent !important;
      
      &::placeholder {
        color: var(--text-tertiary) !important;
      }
    }
    
    // 选择器组件
    .el-select__wrapper {
      background-color: var(--bg-primary) !important;
      border-color: var(--border-color) !important;
      color: var(--text-primary) !important;
      
      &:hover {
        border-color: var(--primary-color) !important;
      }
      
      &.is-focus {
        border-color: var(--primary-color) !important;
        box-shadow: 0 0 0 1px var(--primary-color) !important;
      }
    }
    
    .el-select__placeholder {
      color: var(--text-tertiary) !important;
    }
    
    .el-select__selection {
      color: var(--text-primary) !important;
    }
    
    // 日期选择器
    .el-range-editor {
      background-color: var(--bg-primary) !important;
      border-color: var(--border-color) !important;
      
      &:hover {
        border-color: var(--primary-color) !important;
      }
      
      &.is-focus {
        border-color: var(--primary-color) !important;
        box-shadow: 0 0 0 1px var(--primary-color) !important;
      }
    }
    
    .el-range-input {
      color: var(--text-primary) !important;
      background-color: transparent !important;
      
      &::placeholder {
        color: var(--text-tertiary) !important;
      }
    }
    
    .el-range-separator {
      color: var(--text-secondary) !important;
    }
    
    // 按钮
    .el-button {
      background-color: var(--bg-primary) !important;
      border-color: var(--border-color) !important;
      color: var(--text-primary) !important;
      
      &:hover {
        border-color: var(--primary-color) !important;
        color: var(--primary-color) !important;
      }
    }
    
    // 图标
    .el-icon {
      color: var(--text-secondary) !important;
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .layout-aside {
    transform: translateX(-100%);
    transition: transform 0.3s ease;
    
    &.mobile-open {
      transform: translateX(0);
    }
  }
  
  .layout-main {
    margin-left: 0;
  }
}
</style>
import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'
import NProgress from 'nprogress'

// 路由配置
const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    meta: { 
      title: '首页',
      requiresAuth: false 
    }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { 
      title: '登录',
      requiresAuth: false 
    }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
    meta: {
      title: '注册',
      requiresAuth: false
    }
  },
  {
    path: '/display',
    name: 'Display',
    component: () => import('@/views/Display.vue'),
    meta: { 
      title: '成果展示',
      requiresAuth: false 
    }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Layout.vue'),
    meta: { 
      title: '控制台',
      requiresAuth: true 
    },
    children: [
      // 学生路由
      {
        path: '/student',
        name: 'StudentDashboard',
        component: () => import('@/views/student/Dashboard.vue'),
        meta: { 
          title: '学生控制台',
          requiresAuth: true,
          roles: ['student']
        }
      },
      {
        path: '/student/achievements',
        name: 'StudentAchievements',
        component: () => import('@/views/student/Achievements.vue'),
        meta: { 
          title: '我的成果',
          requiresAuth: true,
          roles: ['student']
        }
      },
      {
        path: '/student/achievements/create',
        name: 'CreateAchievement',
        component: () => import('@/views/student/CreateAchievement.vue'),
        meta: { 
          title: '添加成果',
          requiresAuth: true,
          roles: ['student']
        }
      },
      
      // 队长路由
      {
        path: '/leader',
        name: 'LeaderDashboard',
        component: () => import('@/views/leader/Dashboard.vue'),
        meta: { 
          title: '队长控制台',
          requiresAuth: true,
          roles: ['team_leader']
        }
      },
      {
        path: '/leader/audit',
        name: 'AuditAchievements',
        component: () => import('@/views/leader/Audit.vue'),
        meta: { 
          title: '成果审核',
          requiresAuth: true,
          roles: ['team_leader']
        }
      },
      {
        path: '/leader/manage',
        name: 'ManageAchievements',
        component: () => import('@/views/leader/Manage.vue'),
        meta: { 
          title: '成果管理',
          requiresAuth: true,
          roles: ['team_leader']
        }
      },
      
      // 管理员路由
      {
        path: '/admin',
        name: 'AdminDashboard',
        component: () => import('@/views/admin/Dashboard.vue'),
        meta: { 
          title: '管理员控制台',
          requiresAuth: true,
          roles: ['admin']
        }
      },
      {
        path: '/admin/users',
        name: 'UserManagement',
        component: () => import('@/views/admin/Users.vue'),
        meta: { 
          title: '用户管理',
          requiresAuth: true,
          roles: ['admin']
        }
      },
      {
        path: '/admin/config',
        name: 'SystemConfig',
        component: () => import('@/views/admin/Config.vue'),
        meta: { 
          title: '系统配置',
          requiresAuth: true,
          roles: ['admin']
        }
      },
      {
        path: '/admin/monitor',
        name: 'DataMonitor',
        component: () => import('@/views/admin/Monitor.vue'),
        meta: { 
          title: '数据监控',
          requiresAuth: true,
          roles: ['admin']
        }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue'),
    meta: { title: '页面不存在' }
  }
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  NProgress.start()
  
  const userStore = useUserStore()
  
  // 设置页面标题
  document.title = to.meta.title ? `${to.meta.title} - 成果管理系统` : '成果管理系统'
  
  // 检查是否需要认证
  if (to.meta.requiresAuth) {
    if (!userStore.isLoggedIn) {
      // 尝试从本地存储恢复用户信息
      await userStore.checkAuth()
      
      if (!userStore.isLoggedIn) {
        next('/login')
        return
      }
    }
    
    // 检查角色权限
    if (to.meta.roles && !to.meta.roles.includes(userStore.user.role)) {
      // 根据用户角色重定向到对应的首页
      const roleRoutes = {
        'student': '/student',
        'team_leader': '/leader',
        'admin': '/admin'
      }
      next(roleRoutes[userStore.user.role] || '/login')
      return
    }
  }
  
  next()
})

router.afterEach(() => {
  NProgress.done()
})

export default router
# 信息网络安全学院学生成果登记与管理系统 - 项目结构

## 项目概述
基于Vue 3前端 + Flask后端 + PostgreSQL数据库的现代化学生成果管理系统，采用前后端分离架构，支持完整的成果登记、审核、管理和统计功能。

## 目录结构
```
获奖记录平台/
├── backend/                    # Flask后端服务
│   ├── app/
│   │   ├── __init__.py        # Flask应用初始化和蓝图注册
│   │   ├── config.py          # 应用配置文件
│   │   ├── models/            # 数据库模型层
│   │   │   ├── __init__.py
│   │   │   ├── user.py        # 用户模型（学生、队长、管理员）
│   │   │   ├── achievement.py # 成果模型
│   │   │   ├── class_model.py # 班级模型
│   │   │   ├── audit_log.py   # 审核日志模型
│   │   │   └── system_config.py # 系统配置模型
│   │   ├── routes/            # API路由控制器
│   │   │   ├── __init__.py
│   │   │   ├── auth.py        # 认证相关API
│   │   │   ├── student.py     # 学生功能API
│   │   │   ├── leader.py      # 队长功能API
│   │   │   ├── admin.py       # 管理员功能API
│   │   │   ├── config.py      # 系统配置API
│   │   │   └── upload.py      # 文件上传API
│   │   └── utils/             # 工具函数
│   │       ├── __init__.py
│   │       ├── auth.py        # 认证工具
│   │       ├── file_handler.py # 文件处理
│   │       └── validators.py   # 数据验证
│   ├── uploads/               # 文件上传存储目录
│   ├── requirements.txt       # Python依赖包
│   └── run.py                 # 应用启动入口
├── frontend/                  # Vue 3前端应用
│   ├── src/
│   │   ├── api/               # API接口封装
│   │   │   ├── auth.js        # 认证API
│   │   │   ├── student.js     # 学生API
│   │   │   ├── leader.js      # 队长API
│   │   │   └── admin.js       # 管理员API
│   │   ├── components/        # 公共组件
│   │   │   ├── Layout.vue     # 布局组件
│   │   │   └── common/        # 通用组件
│   │   ├── views/             # 页面组件
│   │   │   ├── Login.vue      # 登录页面
│   │   │   ├── Layout.vue     # 主布局页面
│   │   │   ├── student/       # 学生端页面
│   │   │   │   ├── Dashboard.vue        # 学生控制台
│   │   │   │   ├── Achievements.vue     # 我的成果
│   │   │   │   └── CreateAchievement.vue # 添加成果
│   │   │   ├── leader/        # 队长端页面
│   │   │   │   ├── Dashboard.vue # 队长控制台
│   │   │   │   ├── Audit.vue     # 成果审核
│   │   │   │   └── Manage.vue    # 成果管理
│   │   │   └── admin/         # 管理员端页面
│   │   │       ├── Dashboard.vue # 管理员控制台
│   │   │       ├── Users.vue     # 用户管理
│   │   │       ├── Config.vue    # 系统配置
│   │   │       └── Monitor.vue   # 数据监控
│   │   ├── router/            # Vue Router路由配置
│   │   │   └── index.js       # 路由定义和守卫
│   │   ├── stores/            # Pinia状态管理
│   │   │   ├── user.js        # 用户状态
│   │   │   └── config.js      # 系统配置状态
│   │   ├── utils/             # 工具函数
│   │   │   ├── request.js     # HTTP请求封装
│   │   │   ├── auth.js        # 认证工具
│   │   │   └── format.js      # 格式化工具
│   │   ├── styles/            # 样式文件
│   │   │   └── global.scss    # 全局样式
│   │   ├── App.vue            # 根组件
│   │   └── main.js            # 应用入口
│   ├── public/                # 静态资源
│   │   └── index.html         # HTML模板
│   ├── package.json           # 前端依赖配置
│   └── vue.config.js          # Vue CLI配置
├── scripts/                   # 部署和初始化脚本
│   ├── init_database.py       # 数据库初始化脚本
│   ├── start_backend.bat      # 后端启动脚本
│   └── start_frontend.bat     # 前端启动脚本
├── docs/                      # 项目文档
├── README.md                  # 项目说明文档
├── project_structure.md       # 项目结构文档
└── 信息网络安全学院学生成果登记与管理系统项目管理手册.md # 项目管理手册
```

## 技术栈详情

### 前端技术栈
- **框架**: Vue 3 (Composition API)
- **UI组件库**: Element Plus
- **状态管理**: Pinia
- **路由管理**: Vue Router 4
- **HTTP客户端**: Axios
- **图表库**: ECharts
- **构建工具**: Vue CLI
- **样式预处理**: Sass/SCSS

### 后端技术栈
- **Web框架**: Flask 2.3.3
- **数据库**: PostgreSQL 12+
- **ORM**: SQLAlchemy
- **认证**: Flask-JWT-Extended
- **文件处理**: Werkzeug
- **数据验证**: Marshmallow
- **CORS**: Flask-CORS

### 数据库设计
- **用户表**: 支持多角色用户管理
- **班级表**: 班级信息和学生归属
- **成果表**: 成果信息和状态管理
- **审核日志表**: 完整的审核历史记录
- **系统配置表**: 动态系统配置管理

### 核心功能模块
1. **认证授权**: JWT令牌认证，角色权限控制
2. **成果管理**: 完整的成果生命周期管理
3. **审核流程**: 三级审核流程（通过/退回/拒绝）
4. **文件上传**: 支持多种格式的佐证材料上传
5. **数据统计**: 多维度数据统计和图表展示
6. **系统配置**: 动态配置管理，支持实时更新
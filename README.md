# Husky CRM

一个轻量级 Salesforce-like CRM 系统，基于 Python FastAPI + Vue 3 构建，单租户部署，使用 SQLite 数据库。

## 功能模块

| 模块 | 说明 |
|------|------|
| **仪表盘** | 首页数据概览 |
| **账户管理** | 客户/公司信息管理，支持分页、搜索、筛选 |
| **联系人管理** | 联系人信息管理，支持挂靠到账户 |
| **产品管理** | 产品目录管理，含分类和定价 |
| **销售机会** | 机会管道（Kanban 看板），支持阶段拖拽和产品明细 |
| **销售区域** | 层级化 Territory 管理，支持区域成员、账户关联、产品目录和管道筛选 |
| **自定义对象** | 动态对象引擎，通过 UI 创建自定义数据表和字段（13种字段类型） |
| **工作流** | 条件-动作引擎，支持多条件评估和自动操作 |
| **报表** | 可配置报表和仪表盘，支持图表展示 |

## 技术栈

| 层 | 技术 |
|---|---|
| **后端框架** | Python FastAPI (async) |
| **ORM** | SQLAlchemy 2.0 + Alembic |
| **数据库** | SQLite (aiosqlite) |
| **认证** | JWT (python-jose + passlib, bcrypt) |
| **前端框架** | Vue 3 + TypeScript (Composition API) |
| **UI 组件库** | Element Plus |
| **前端路由** | Vue Router 4 |
| **HTTP 客户端** | Axios |
| **构建工具** | Vite |
| **测试 (API)** | pytest + pytest-asyncio + httpx |
| **测试 (UAT)** | pytest + Playwright |

## 快速开始

### 前置条件

- Python 3.11+
- Node.js 18+
- SQLite 3

### 1. 启动后端

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

### 2. 启动前端

```bash
cd frontend
npm install
npm run dev
```

### 3. 初始化演示数据

```bash
python DEMO.py
```

然后在菜单中选择需要的操作：
- **1** — 创建数据库表结构
- **2** — 创建管理员账号 (admin / admin123)
- **3** — 创建销售阶段
- **4** — 加载测试数据 (TEST.sql)

或者一键完成全部初始化：

```bash
python DEMO.py <<< $'1\n2\n3\n4\n0'
```

### 4. 访问系统

打开浏览器访问 **http://localhost:5173**

默认登录：**admin** / **admin123**

## 项目结构

```
spsf/
├── README.md                       # 本文件
├── DEMO.py                         # 演示数据初始化脚本（交互式菜单）
├── TEST.sql                        # 测试数据 SQL 文件
├── TEST.md                         # 测试指南
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI 入口 + 路由注册
│   │   ├── config.py               # 系统配置
│   │   ├── database.py             # SQLAlchemy 引擎和会话
│   │   ├── models/                 # SQLAlchemy 数据模型
│   │   │   ├── auth.py             # 用户模型
│   │   │   ├── crm.py              # 账户、联系人、机会、产品、阶段
│   │   │   ├── territory.py        # 销售区域、成员、账户/产品关联
│   │   │   ├── custom_object.py    # 自定义对象元数据
│   │   │   ├── workflow.py         # 工作流规则
│   │   │   └── report.py           # 报表与仪表盘
│   │   ├── schemas/                # Pydantic 请求/响应模型
│   │   ├── api/                    # 路由处理器
│   │   │   ├── auth.py             # 登录/注册/刷新
│   │   │   ├── accounts.py         # 账户 CRUD
│   │   │   ├── contacts.py         # 联系人 CRUD
│   │   │   ├── products.py         # 产品 CRUD
│   │   │   ├── opportunities.py    # 机会 CRUD + 管道 + 产品明细
│   │   │   ├── territories.py      # 区域 CRUD + 树 + 成员 + 账户 + 产品 + 管道
│   │   │   ├── custom_objects.py   # 自定义对象引擎
│   │   │   ├── workflows.py        # 工作流管理
│   │   │   └── reports.py          # 报表 + 仪表盘
│   │   ├── services/               # 业务逻辑层
│   │   │   ├── custom_object_service.py  # 动态 DDL 服务
│   │   │   ├── workflow_service.py       # 条件评估器 + 动作执行器
│   │   │   └── report_service.py         # 报表执行引擎
│   │   ├── core/                   # 基础设施
│   │   │   ├── security.py         # JWT 生成/验证、密码哈希
│   │   │   └── deps.py             # 依赖注入
│   │   └── utils/
│   │       └── dynamic_ddl.py      # 动态建表/改表工具
│   ├── requirements.txt
│   └── huskycrm.db                 # SQLite 数据库文件
├── frontend/
│   ├── src/
│   │   ├── main.ts                 # Vue 应用入口
│   │   ├── App.vue                 # 根组件
│   │   ├── api/                    # API 客户端（Axios）
│   │   │   ├── client.ts           # Axios 实例 + JWT 拦截器
│   │   │   ├── auth.ts
│   │   │   ├── accounts.ts
│   │   │   ├── contacts.ts
│   │   │   ├── products.ts
│   │   │   ├── opportunities.ts
│   │   │   ├── territories.ts
│   │   │   ├── customObjects.ts
│   │   │   ├── workflows.ts
│   │   │   └── reports.ts
│   │   ├── types/                  # TypeScript 类型定义
│   │   │   ├── auth.ts
│   │   │   ├── crm.ts
│   │   │   ├── territory.ts
│   │   │   └── customObject.ts
│   │   ├── components/             # 通用组件
│   │   │   ├── layout/             # 布局组件（AppLayout, Sidebar, Header, NavTabs）
│   │   │   ├── record/             # 记录组件（RecordHeader, RecordSection, HighlightsPanel, RecordTabs, RelatedList）
│   │   │   ├── dynamic-form/       # 自定义对象动态表单
│   │   │   └── common/             # 通用小部件
│   │   ├── views/                  # 页面视图
│   │   │   ├── accounts/
│   │   │   ├── contacts/
│   │   │   ├── products/
│   │   │   ├── opportunities/
│   │   │   ├── territories/
│   │   │   ├── custom-objects/
│   │   │   ├── workflows/
│   │   │   └── reports/
│   │   ├── stores/                 # Pinia 状态管理
│   │   │   └── authStore.ts
│   │   ├── router/                 # Vue Router
│   │   │   └── index.ts
│   │   └── styles/                 # 样式
│   │       └── salesforce-theme.css
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
├── scripts/
│   └── seed_data.py                # API 方式的数据导入脚本
└── TEST/
    ├── Unittest/                   # API 单元测试（pytest + httpx）
    │   ├── conftest.py
    │   ├── test_auth.py            # 10 个测试
    │   ├── test_accounts.py        # 13 个测试
    │   ├── test_contacts.py        # 8 个测试
    │   ├── test_opportunities.py   # 8 个测试
    │   ├── test_custom_objects.py  # 17 个测试
    │   ├── test_workflows.py       # 14 个测试
    │   ├── test_reports.py         # 13 个测试
    │   ├── TestPlan.md
    │   └── TestReport.md
    └── UAT/                        # 端到端测试（Playwright）
        ├── conftest.py
        ├── test_login_flow.py
        ├── test_account_flow.py
        ├── test_contact_flow.py
        ├── test_pipeline_flow.py
        ├── test_custom_object_flow.py
        ├── test_workflow_report_flow.py
        ├── TestPlan.md
        └── TestReport.md
```

## API 概览

| 端点 | 说明 |
|------|------|
| `POST /api/auth/register` | 用户注册 |
| `POST /api/auth/login` | 登录，返回 JWT |
| `POST /api/auth/refresh` | 刷新 Token |
| `GET /api/auth/me` | 获取当前用户信息 |
| `GET /api/auth/users` | 用户列表 |
| `GET/POST /api/accounts` | 账户列表/创建 |
| `GET/PUT/DEL /api/accounts/{id}` | 账户详情/更新/删除 |
| `GET/POST /api/contacts` | 联系人列表/创建 |
| `GET/PUT/DEL /api/contacts/{id}` | 联系人详情/更新/删除 |
| `GET/POST /api/products` | 产品列表/创建 |
| `GET/PUT/DEL /api/products/{id}` | 产品详情/更新/删除 |
| `GET/POST /api/opportunities` | 机会列表/创建 |
| `GET/PUT/DEL /api/opportunities/{id}` | 机会详情/更新/删除 |
| `GET /api/opportunities/stages` | 销售阶段列表 |
| `GET /api/opportunities/pipeline` | 管道看板数据 |
| `GET/POST/DEL /api/opportunities/{id}/line-items` | 机会产品明细 |
| `GET/POST /api/territories` | 区域列表/创建 |
| `GET/PUT/DEL /api/territories/{id}` | 区域详情/更新/删除 |
| `GET /api/territories/tree` | 区域树形结构 |
| `GET/POST/DEL /api/territories/{id}/members` | 区域成员管理 |
| `GET/POST/DEL /api/territories/{id}/accounts` | 区域账户关联 |
| `GET/POST/PUT/DEL /api/territories/{id}/products` | 区域产品目录 |
| `GET /api/territories/{id}/pipeline` | 区域管道数据 |
| `GET/POST /api/custom-objects` | 自定义对象列表/创建 |
| `GET/PUT/DEL /api/custom-objects/{id}` | 对象定义管理 |
| `POST /api/custom-objects/{id}/fields` | 添加字段（动态 ALTER TABLE） |
| `GET/POST /api/custom-objects/{id}/records` | 自定义记录列表/创建 |
| `GET/PUT/DEL /api/custom-objects/{id}/records/{rid}` | 记录详情/更新/删除 |
| `GET/POST /api/workflows` | 工作流列表/创建 |
| `GET/PUT/DEL /api/workflows/{id}` | 工作流管理 |
| `GET/POST /api/reports` | 报表列表/创建 |
| `GET/PUT/DEL /api/reports/{id}` | 报表管理 |
| `POST /api/reports/{id}/run` | 执行报表 |
| `GET/POST /api/dashboards` | 仪表盘列表/创建 |
| `GET/PUT/DEL /api/dashboards/{id}` | 仪表盘管理 |

## 运行测试

### API 单元测试

```bash
cd backend
source venv/bin/activate
python -m pytest TEST/Unittest/ -v
```

81 个测试用例，覆盖认证、CRUD、分页搜索、错误路径、自定义对象引擎、工作流条件评估、报表执行等。

### UAT 端到端测试

需要同时启动后端和前端：

```bash
# 终端 1：启动后端
cd backend && source venv/bin/activate
python -m uvicorn app.main:app --reload --port 8000

# 终端 2：启动前端
cd frontend && npm run dev

# 终端 3：运行测试
cd backend && source venv/bin/activate
python -m pytest TEST/UAT/ -v --headed
```

30 个测试场景，覆盖登录、账户/联系人 CRUD、机会管道、自定义对象、工作流、报表等完整业务流程。

## 关键设计

### 自定义对象引擎

采用 **动态 DDL** 方案而非 EAV 或 JSON 字段：

| 方案 | 优点 | 缺点 |
|---|---|---|
| **动态 DDL** (已选) | 真正 SQL 类型和索引，查询性能最优 | 需动态执行 SQL，做注入防护 |
| EAV | 完全动态 | 查询性能极差，无法高效过滤/排序 |
| JSON 字段 | 实现简单 | 无法对单个字段建索引，类型不严格 |

SQL 注入通过白名单机制防护：所有字段名和类型需匹配预定义的 API 名称和类型列表。

### 销售区域管理

层级化结构通过 `parent_id` 自引用实现，支持：
- 用户分配到区域（manager / member）
- 账户多区域关联（多对多）
- 产品区域目录（含区域专属价格）
- 按区域查看管道

### 前端样式

高度还原 Salesforce 风格：Inter + Noto Sans SC 字体、#1589ee 主题色、紧凑间距、自定义侧边栏和导航标签。

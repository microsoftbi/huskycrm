# Husky CRM — 测试指南

## 目录结构

```
TEST/
├── Unittest/                          # API 单元测试（pytest + httpx）
│   ├── conftest.py                    # 共享 fixtures（内存 DB、auth headers）
│   ├── test_auth.py                   # 认证模块（注册/登录/刷新/me）
│   ├── test_accounts.py               # 账户 CRUD
│   ├── test_contacts.py               # 联系人 CRUD
│   ├── test_opportunities.py          # 机会 + 管道看板
│   ├── test_custom_objects.py         # 自定义对象引擎（动态建表/字段/记录）
│   ├── test_workflows.py              # 工作流引擎（条件评估器 + CRUD）
│   ├── test_reports.py                # 报表 + 仪表盘
│   ├── TestPlan.md                    # 单元测试计划
│   └── TestReport.md                  # 单元测试报告
│
├── UAT/                               # UAT 端到端测试（Playwright）
│   ├── conftest.py                    # Playwright fixtures、auth 注入
│   ├── test_login_flow.py             # 登录流程（4 场景）
│   ├── test_account_flow.py           # 账户 CRUD 流程（6 场景）
│   ├── test_contact_flow.py           # 联系人 CRUD 流程（4 场景）
│   ├── test_pipeline_flow.py          # 机会 + 管道看板（3 场景）
│   ├── test_custom_object_flow.py     # 自定义对象引擎（5 场景）
│   ├── test_workflow_report_flow.py   # 工作流 + 报表（8 场景）
│   ├── TestPlan.md                    # UAT 测试计划
│   └── TestReport.md                  # UAT 测试报告
│
└── ../
```

---

## 单元测试（API 级）

### 简介

单元测试直接测试后端 API 端点，使用内存 SQLite 数据库，每次测试自动建表和清理。无需启动外部服务。

- **测试框架**：pytest + pytest-asyncio
- **HTTP 客户端**：httpx.AsyncClient（直连 FastAPI，无需网络）
- **数据库**：`sqlite+aiosqlite://` 内存模式
- **数据隔离**：每个测试独立建表，测试后自动清理

### 运行方式

```bash
# 1. 激活虚拟环境
cd backend && source venv/bin/activate

# 2. 运行全部测试
python -m pytest TEST/Unittest/ -v

# 3. 运行单个测试文件
python -m pytest TEST/Unittest/test_auth.py -v

# 4. 运行单个测试用例
python -m pytest TEST/Unittest/test_auth.py::TestRegister::test_register_success -v

# 5. 显示详细错误信息
python -m pytest TEST/Unittest/ -v --tb=long

# 6. 运行并显示覆盖率（需安装 pytest-cov）
python -m pytest TEST/Unittest/ --cov=app
```

### 预期结果

```
============================= 81 passed in 35.82s ==============================
```

### 测试内容

| 测试文件 | 数量 | 覆盖内容 |
|---|---|---|
| `test_auth.py` | 10 | 注册、登录、刷新、获取用户、错误路径 |
| `test_accounts.py` | 13 | 账户 CRUD、分页、搜索、错误路径 |
| `test_contacts.py` | 8 | 联系人 CRUD、账户筛选、搜索 |
| `test_opportunities.py` | 8 | 机会 CRUD、阶段移动、管道数据 |
| `test_custom_objects.py` | 17 | 动态建表、字段管理、记录 CRUD、通用 API |
| `test_workflows.py` | 14 | 条件评估器（纯函数）、工作流 CRUD |
| `test_reports.py` | 13 | 报表 CRUD、执行、仪表盘 CRUD、组件管理 |

---

## UAT 测试（端到端）

### 简介

UAT 测试使用 Playwright 模拟真实用户在浏览器中的操作，验证完整的端到端流程。需要后端和前端同时运行。

- **测试框架**：pytest + Playwright
- **浏览器**：Chromium（Headless / Headed 模式）
- **后端**：http://localhost:8000
- **前端**：http://localhost:5173

### 前置条件

```bash
# 1. 安装 Playwright
cd backend && source venv/bin/activate
pip install pytest-playwright
playwright install chromium

# 2. 启动后端（终端 1）
cd backend && source venv/bin/activate
uvicorn app.main:app --reload --port 8000

# 3. 启动前端（终端 2）
cd frontend
npm run dev
```

### 运行方式

```bash
# 1. 激活虚拟环境（新终端）
cd backend && source venv/bin/activate

# 2. 运行全部 UAT 测试（无界面模式）
python -m pytest TEST/UAT/ -v

# 3. 运行全部 UAT 测试（有浏览器界面，调试用）
python -m pytest TEST/UAT/ -v --headed

# 4. 运行单个测试文件
python -m pytest TEST/UAT/test_login_flow.py -v --headed

# 5. 失败时保留截图
python -m pytest TEST/UAT/ --screenshot=only-on-failure

# 6. 慢速模式（查看每一步操作）
python -m pytest TEST/UAT/ --headed --slowmo 500
```

### 预期结果

```
============================= 30 passed in 105.66s ==============================
```

### 测试场景

| 测试文件 | 场景数 | 覆盖内容 |
|---|---|---|
| `test_login_flow.py` | 4 | 正常登录、密码错误、注册登录、退出 |
| `test_account_flow.py` | 6 | 列表、新建、编辑、删除、搜索、空校验 |
| `test_contact_flow.py` | 4 | 新建、编辑、删除 |
| `test_pipeline_flow.py` | 3 | 新建机会、看板显示、摘要统计 |
| `test_custom_object_flow.py` | 5 | 动态对象、记录 CRUD、通用 API、添加字段、删除 |
| `test_workflow_report_flow.py` | 8 | 工作流 CRUD、条件测试、报表执行、筛选、生命周期 |

---

## 对比

| 维度 | 单元测试 | UAT 测试 |
|---|---|---|
| **目的** | 验证 API 正确性 | 验证用户操作流程 |
| **运行速度** | 快（~36s） | 慢（~106s） |
| **需要前端** | 否 | 是 |
| **需要浏览器** | 否 | 是 |
| **测试数量** | 81 | 30 |
| **错误定位** | 精确到行 | 定位到用户操作步骤 |
| **覆盖范围** | 边界条件、错误路径 | 完整业务流程 |

---

## 常见问题

### Q: 单元测试报 `ModuleNotFoundError: No module named 'app'`

**原因**：pytest 找不到 backend 目录的 Python 模块。

**解决**：确保从项目根目录运行，`pytest.ini` 中已配置 `pythonpath = backend`。如果仍有问题：
```bash
cd backend && source venv/bin/activate
PYTHONPATH=$PYTHONPATH:.. python -m pytest TEST/Unittest/
```

### Q: UAT 测试报连接被拒绝

**原因**：后端或前端服务未启动。

**解决**：确保两个服务都在运行：
```bash
curl http://localhost:8000/api/health   # 检查后端
curl http://localhost:5173              # 检查前端
```

### Q: Playwright 报浏览器未安装

**原因**：未安装 Chromium 浏览器引擎。

**解决**：
```bash
playwright install chromium
```

### Q: 测试数据残留

**原因**：测试之间数据未清理干净。

**解决**：单元测试使用内存数据库，每次自动重建。如果使用文件数据库，手动删除：
```bash
rm -f backend/huskycrm.db
```

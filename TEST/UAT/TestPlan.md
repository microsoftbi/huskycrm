# SPSF CRM — UAT 测试计划

## 1. 概述

本文档定义了 SPSF CRM 系统的用户验收测试（User Acceptance Testing）策略。UAT 测试使用 Playwright 模拟真实用户操作，验证完整的端到端业务流程。

### 测试目标
- 验证所有用户核心流程从头到尾的正确性
- 验证前端交互（表单、表格、拖拽）在真实浏览器中正常工作
- 捕获 API 级测试无法发现的 UI/UX 问题
- 确保错误提示、状态变化等用户体验符合预期

### 测试工具

| 工具 | 用途 |
|---|---|
| **Playwright** | 浏览器自动化，模拟用户操作 |
| **Chromium** | 测试浏览器（Playwright 内置） |
| **pytest** | 测试框架（与现有 API 测试一致） |
| **pytest-playwright** | Playwright + pytest 集成插件 |

### 测试环境

| 项目 | 配置 |
|---|---|
| 前端 URL | `http://localhost:5173` |
| 后端 URL | `http://localhost:8000` |
| 浏览器 | Chromium（Headless 或 UI 模式） |
| 数据库 | 独立测试数据库（不影响开发数据） |
| 测试账号 | 自动注册（每个测试用例独立） |

---

## 2. 测试架构

```
TEST/UAT/
├── conftest.py              # Playwright fixtures
├── TestPlan.md              # 本文档
├── test_login_flow.py       # 登录流程 UAT
├── test_account_flow.py     # 账户 CRUD 流程
├── test_contact_flow.py     # 联系人 CRUD 流程
├── test_pipeline_flow.py    # 管道看板拖拽
└── test_custom_object_flow.py # 自定义对象流程
```

### 与 API 测试的关系

```
API 测试（TEST/Unittest/）          UAT 测试（TEST/UAT/）
┌──────────────────────────┐     ┌──────────────────────────┐
│ 测试边界条件和错误路径     │     │ 测试用户核心操作流程      │
│ 81 个测试，35s 完成      │     │ ~20 个场景，5-10min     │
│ 不渲染浏览器             │     │ 真实浏览器渲染           │
│ 直接调用 HTTP API        │     │ 通过 UI 操作调用 API     │
│ 覆盖: 401/404/422 等    │     │ 覆盖: 交互/状态/提示等   │
└──────────────────────────┘     └──────────────────────────┘
          互补                       互补
```

### 数据管理策略

- 每个测试用例 **自动注册** 独立用户
- 每个测试用例创建自己的测试数据
- 测试结束后不清理数据库（由下次启动覆盖或重置）
- 后端使用独立端口（8000），前端使用独立端口（5173）

---

## 3. 测试场景清单

### 3.1 登录流程 — 4 个场景

| ID | 场景 | 操作步骤 | 预期结果 | 优先级 |
|---|---|---|---|---|
| UAT-LOGIN-01 | **正常登录** | 1. 打开首页<br>2. 输入用户名/密码<br>3. 点击"登录" | 跳转到仪表盘页面，显示"仪表盘"标题 | P0 |
| UAT-LOGIN-02 | **密码错误** | 1. 输入错误密码<br>2. 点击"登录" | 显示错误提示信息，停留在登录页 | P0 |
| UAT-LOGIN-03 | **切换到注册** | 1. 点击"注册" tab<br>2. 输入用户名/邮箱/密码<br>3. 点击"注册" | 注册成功，自动登录并跳转到仪表盘 | P1 |
| UAT-LOGIN-04 | **退出登录** | 1. 已登录状态<br>2. 点击右上角头像<br>3. 点击"退出登录" | 跳转到登录页，清除 token | P0 |

### 3.2 账户管理流程 — 6 个场景

| ID | 场景 | 操作步骤 | 预期结果 | 优先级 |
|---|---|---|---|---|
| UAT-ACC-01 | **查看账户列表** | 1. 点击侧边栏"账户"<br>2. 浏览列表 | 显示账户表格，包含名称/行业/电话等列 | P0 |
| UAT-ACC-02 | **新建账户** | 1. 点击"新建账户"按钮<br>2. 填写名称/行业/电话等<br>3. 点击"保存" | 跳转到新账户详情页，显示提交的数据 | P0 |
| UAT-ACC-03 | **编辑账户** | 1. 打开一个账户详情<br>2. 点击"编辑"按钮<br>3. 修改字段<br>4. 点击"保存" | 详情页显示更新后的数据 | P0 |
| UAT-ACC-04 | **删除账户** | 1. 打开一个账户详情<br>2. 点击"删除"按钮<br>3. 在确认弹窗中点"删除" | 跳转回列表页，该账户不再出现 | P0 |
| UAT-ACC-05 | **搜索账户** | 1. 在搜索框输入名称<br>2. 按回车搜索 | 列表只显示匹配的记录 | P1 |
| UAT-ACC-06 | **空表单提交** | 1. 不填名称直接点"保存" | 表单校验显示"请输入账户名称" | P1 |

### 3.3 联系人管理流程 — 4 个场景

| ID | 场景 | 操作步骤 | 预期结果 | 优先级 |
|---|---|---|---|---|
| UAT-CON-01 | **新建联系人** | 1. 点击"新建联系人"<br>2. 填写姓名/邮箱/电话<br>3. 点击"保存" | 跳转到联系人详情页 | P0 |
| UAT-CON-02 | **关联账户** | 1. 新建联系人时选择关联账户<br>2. 保存 | 联系人详情页显示关联的账户信息 | P1 |
| UAT-CON-03 | **编辑联系人** | 1. 打开联系人详情<br>2. 编辑字段<br>3. 保存 | 详情页显示更新后的数据 | P0 |
| UAT-CON-04 | **删除联系人** | 1. 打开联系人详情<br>2. 点击删除<br>3. 确认 | 跳转回列表，该联系人已删除 | P0 |

### 3.4 销售机会 + 管道看板 — 4 个场景

| ID | 场景 | 操作步骤 | 预期结果 | 优先级 |
|---|---|---|---|---|
| UAT-OPP-01 | **新建机会** | 1. 进入机会列表<br>2. 点击"新建机会"<br>3. 填写名称/金额/阶段等<br>4. 保存 | 跳转到机会详情页 | P0 |
| UAT-OPP-02 | **管道看板** | 1. 点击"管道看板"<br>2. 浏览各列 | 显示 7 个阶段列，机会卡片在对应列中 | P0 |
| UAT-OPP-03 | **拖拽移动阶段** | 1. 在管道看板中<br>2. 拖拽一个机会卡片到下一列<br>3. 松开鼠标 | 卡片移动到目标列，阶段已更新 | P0 |
| UAT-OPP-04 | **管道摘要统计** | 1. 打开管道看板 | 顶部显示管道总额/机会总数等统计卡片 | P1 |

### 3.5 自定义对象流程 — 3 个场景

| ID | 场景 | 操作步骤 | 预期结果 | 优先级 |
|---|---|---|---|---|
| UAT-CUS-01 | **创建自定义对象** | 1. 进入自定义对象管理<br>2. 创建新对象（如"发票"）<br>3. 添加字段（文本/数字/选项）<br>4. 保存 | 对象出现在列表中，包含定义的字段 | P0 |
| UAT-CUS-02 | **动态记录 CRUD** | 1. 打开自定义对象记录列表<br>2. 新建一条记录<br>3. 填写动态表单<br>4. 保存 | 记录显示在列表中 | P0 |
| UAT-CUS-03 | **通用 API 验证** | 1. 通过 /by-name/ 端点访问<br>2. 创建和查询记录 | 返回正确数据 | P2 |

### 3.6 工作流 + 报表 — 2 个场景

| ID | 场景 | 操作步骤 | 预期结果 | 优先级 |
|---|---|---|---|---|
| UAT-WF-01 | **创建工作流** | 1. 进入工作流管理<br>2. 创建工作流规则<br>3. 设置条件和动作<br>4. 保存 | 规则出现在列表中 | P1 |
| UAT-REP-01 | **运行报表** | 1. 进入报表管理<br>2. 创建新报表<br>3. 选择对象和字段<br>4. 运行 | 显示报表结果表格 | P1 |

---

## 4. Playwright 技术方案

### 依赖安装

```bash
# 安装 Playwright Python + 浏览器
cd backend && source venv/bin/activate
pip install pytest-playwright
playwright install chromium

# 或
pip install playwright
python -m playwright install chromium
```

### conftest.py 设计

```python
import pytest
from playwright.sync_api import sync_playwright

BASE_URL = "http://localhost:5173"

@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()

@pytest.fixture
def page(browser):
    context = browser.new_context()
    page = context.new_page()
    yield page
    context.close()

@pytest.fixture
def logged_in_page(page):
    """注册用户并登录，返回已登录的 page 对象"""
    # 注册
    page.goto(f"{BASE_URL}/login")
    page.click("text=注册")
    page.fill("[placeholder='请输入用户名']", f"test_{uuid4().hex[:8]}")
    page.fill("[placeholder='请输入邮箱']", f"test@example.com")
    page.fill("[placeholder='请输入密码']", "test123")
    page.click("button:has-text('注册')")
    page.wait_for_url(f"{BASE_URL}/")
    return page
```

### 元素定位策略（针对 Element Plus）

| 操作 | 定位方式 | 示例 |
|---|---|---|
| 按钮点击 | `page.click("button:has-text('保存')")` | 根据按钮文字 |
| 输入框填写 | `page.fill("[placeholder='请输入名称']", "Acme")` | 根据 placeholder |
| 表格行 | `page.locator(".el-table__row")` | Element Plus 表格行 |
| 弹窗确认 | `page.click(".el-message-box .el-button--primary")` | 确认弹窗 |
| 下拉选择 | `page.click(".el-select")` → 点选项 | Element Plus Select |
| Tab 切换 | `page.click(".el-tabs__item:has-text('注册')")` | Tab 标签 |
| 拖拽 | `source.drag_to(target)` | Playwright 原生 API |

---

## 5. 测试执行

### 运行命令

```bash
# 1. 启动后端
cd backend && source venv/bin/activate && uvicorn app.main:app --port 8000

# 2. 启动前端（另一个终端）
cd frontend && npm run dev

# 3. 运行 UAT 测试
cd backend && source venv/bin/activate
pytest TEST/UAT/ -v --headed  # 有界面模式（开发调试用）
pytest TEST/UAT/ -v           # 无界面模式（CI 用）

# 只运行特定文件
pytest TEST/UAT/test_login_flow.py -v

# 生成 HTML 报告
pytest TEST/UAT/ --html=report.html
```

### CI 集成

```yaml
# .github/workflows/uat.yml
- name: Install dependencies
  run: |
    pip install pytest-playwright
    playwright install chromium

- name: Start services
  run: |
    uvicorn app.main:app --port 8000 &
    cd frontend && npm run dev &

- name: Run UAT tests
  run: pytest TEST/UAT/ --tracing=retain-on-failure
```

---

## 6. 测试用例模板

```python
# TEST/UAT/test_login_flow.py
import pytest
from playwright.sync_api import Page, expect
from faker import Faker

fake = Faker()

BASE_URL = "http://localhost:5173"


class TestLoginFlow:
    """登录流程 UAT 测试"""

    def test_login_success(self, page: Page):
        """UAT-LOGIN-01: 正常登录"""
        # 1. 先注册用户（通过 API 快速创建）
        import requests
        user = {
            "username": fake.user_name(),
            "email": fake.email(),
            "password": "test123",
        }
        requests.post("http://localhost:8000/api/auth/register", json=user)

        # 2. 打开登录页
        page.goto(f"{BASE_URL}/login")
        expect(page).to_have_title("SPSF CRM")

        # 3. 输入凭据
        page.fill("[placeholder='请输入用户名']", user["username"])
        page.fill("[placeholder='请输入密码']", user["password"])

        # 4. 点击登录
        page.click("button:has-text('登录')")

        # 5. 验证跳转到仪表盘
        page.wait_for_url(f"{BASE_URL}/")
        expect(page.locator("text=仪表盘")).to_be_visible()
        expect(page.locator("text=SPSF CRM")).to_be_visible()

    def test_wrong_password(self, page: Page):
        """UAT-LOGIN-02: 密码错误"""
        page.goto(f"{BASE_URL}/login")
        page.fill("[placeholder='请输入用户名']", "nonexistent")
        page.fill("[placeholder='请输入密码']", "wrong")
        page.click("button:has-text('登录')")
        # 验证错误提示（Element Plus 的 ElMessage）
        expect(page.locator(".el-message--error")).to_be_visible()
```

---

## 7. 风险与缓解

| 风险 | 影响 | 缓解措施 |
|---|---|---|
| 前端端口占用 | 无法启动测试 | 自动检测端口，使用备用端口 |
| 测试数据污染 | 用例间互相影响 | 每个用例注册独立用户 |
| 网络延迟/API 慢 | 测试不稳定 | Playwright 自动等待 + 超时配置 |
| 浏览器版本兼容 | 环境差异 | `playwright install chromium` 固定版本 |
| 拖拽操作不稳定 | 测试偶尔失败 | 添加重试机制（pytest-rerunfailures） |

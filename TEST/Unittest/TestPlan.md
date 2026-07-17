# SPSF CRM — 单元测试计划

## 1. 概述

本文档描述了 SPSF CRM 系统的单元测试策略、范围和方法。测试覆盖所有后端 API 端点和服务层逻辑，使用内存 SQLite 数据库确保隔离性。

### 测试目标
- 验证所有 REST API 端点的正确性
- 验证核心业务逻辑（条件评估器等）
- 验证动态 DDL 引擎的正确性和安全性
- 确保错误路径被正确处理（404、400、401、422 等）

### 测试工具
| 工具 | 用途 |
|---|---|
| pytest 8.x | 测试框架 |
| pytest-asyncio | 异步测试支持 |
| httpx | HTTP 异步测试客户端 |
| ASGITransport | FastAPI 应用直连（无需网络） |

---

## 2. 测试架构

```
TEST/Unittest/
├── conftest.py              # 共享 fixtures（DB、client、auth）
├── test_auth.py             # 认证模块测试
├── test_accounts.py         # 账户 CRUD 测试
├── test_contacts.py         # 联系人 CRUD 测试
├── test_opportunities.py    # 机会与管道测试
├── test_custom_objects.py   # 自定义对象引擎测试
├── test_workflows.py        # 工作流引擎测试
└── test_reports.py          # 报表与仪表盘测试
```

### 测试数据库
- 使用 `sqlite+aiosqlite://` 内存数据库
- 每次测试前自动创建所有表（`setup_database` fixture）
- 每次测试后自动删除所有表（包括动态创建的 `obj_*` 表）
- 测试之间完全隔离

### 认证机制
- 所有需要认证的测试使用 `auth_headers` fixture
- 该 fixture 自动注册测试用户并获取 JWT token
- 测试无需手动处理 token

---

## 3. 测试用例清单

### 3.1 认证模块 (`test_auth.py`) — 9 个测试

| 测试类 | 测试方法 | 验证内容 |
|---|---|---|
| `TestRegister` | `test_register_success` | 注册成功返回 201，包含用户信息 |
| `TestRegister` | `test_register_duplicate_username` | 重复用户名返回 400 |
| `TestRegister` | `test_register_duplicate_email` | 重复邮箱返回 400 |
| `TestLogin` | `test_login_success` | 登录成功返回 JWT token |
| `TestLogin` | `test_login_wrong_password` | 错误密码返回 401 |
| `TestLogin` | `test_login_nonexistent_user` | 不存在用户返回 401 |
| `TestRefresh` | `test_refresh_success` | 刷新 token 成功 |
| `TestRefresh` | `test_refresh_invalid_token` | 无效 refresh token 返回 401 |
| `TestMe` | `test_get_me` | 获取当前用户信息 |
| `TestMe` | `test_get_me_unauthorized` | 未认证请求返回 403 |

### 3.2 账户模块 (`test_accounts.py`) — 12 个测试

| 测试类 | 测试方法 | 验证内容 |
|---|---|---|
| `TestListAccounts` | `test_list_empty` | 空列表返回 total=0 |
| `TestListAccounts` | `test_list_with_data` | 创建后列表包含两条记录 |
| `TestListAccounts` | `test_search` | 按名称搜索过滤 |
| `TestListAccounts` | `test_pagination` | 分页返回正确数量和总数 |
| `TestCreateAccount` | `test_create_minimal` | 最小字段创建成功 |
| `TestCreateAccount` | `test_create_full` | 全字段创建成功 |
| `TestCreateAccount` | `test_create_missing_name` | 缺少必填字段返回 422 |
| `TestGetAccount` | `test_get_by_id` | 按 ID 获取账户 |
| `TestGetAccount` | `test_get_not_found` | 不存在的 ID 返回 404 |
| `TestUpdateAccount` | `test_update` | 更新账户字段 |
| `TestUpdateAccount` | `test_update_not_found` | 更新不存在账户返回 404 |
| `TestDeleteAccount` | `test_delete` | 删除账户后 404 |
| `TestDeleteAccount` | `test_delete_not_found` | 删除不存在返回 404 |

### 3.3 联系人模块 (`test_contacts.py`) — 8 个测试

| 测试类 | 测试方法 | 验证内容 |
|---|---|---|
| `TestCreateContact` | `test_create_minimal` | 最小字段创建成功 |
| `TestCreateContact` | `test_create_full` | 全字段创建（含账户关联） |
| `TestCreateContact` | `test_create_missing_name` | 缺姓/名返回 422 |
| `TestListContacts` | `test_list_with_account_filter` | 按账户 ID 筛选 |
| `TestListContacts` | `test_search_contacts` | 按姓名/邮箱搜索 |
| `TestUpdateContact` | `test_update` | 更新联系人字段 |
| `TestDeleteContact` | `test_delete` | 删除后返回 404 |

### 3.4 销售机会模块 (`test_opportunities.py`) — 9 个测试

| 测试类 | 测试方法 | 验证内容 |
|---|---|---|
| `TestStages` | `test_stages_seeded` | 7 个默认阶段正确创建 |
| `TestCreateOpportunity` | `test_create_success` | 创建机会成功 |
| `TestCreateOpportunity` | `test_create_invalid_stage` | 无效阶段返回 400 |
| `TestListOpportunities` | `test_list_and_search` | 列表、搜索、按阶段筛选 |
| `TestUpdateOpportunity` | `test_move_stage` | 移动到不同阶段 |
| `TestUpdateOpportunity` | `test_update_not_found` | 更新不存在返回 404 |
| `TestDeleteOpportunity` | `test_delete` | 删除后返回 204 |
| `TestPipeline` | `test_pipeline_structure` | 管道数据结构完整，金额汇总正确 |

### 3.5 自定义对象引擎 (`test_custom_objects.py`) — 17 个测试

| 测试类 | 测试方法 | 验证内容 |
|---|---|---|
| `TestCreateCustomObject` | `test_create_with_fields` | 创建带字段的自定义对象，验证 picklist 值 |
| `TestCreateCustomObject` | `test_create_duplicate_api_name` | 重复 api_name 返回 400 |
| `TestCreateCustomObject` | `test_create_without_fields` | 无字段创建成功 |
| `TestListAndGetObjects` | `test_list_objects` | 列出所有自定义对象 |
| `TestListAndGetObjects` | `test_get_object_by_id` | 按 ID 获取对象定义 |
| `TestListAndGetObjects` | `test_get_not_found` | 不存在返回 404 |
| `TestAddField` | `test_add_field` | 动态添加字段并验证 |
| `TestAddField` | `test_add_duplicate_field` | 重复字段返回 400 |
| `TestRecordCRUD` | `test_create_record` | 创建记录，验证字段值 |
| `TestRecordCRUD` | `test_create_record_missing_required` | 缺必填字段返回 400 |
| `TestRecordCRUD` | `test_list_records` | 列表返回分页数据 |
| `TestRecordCRUD` | `test_update_record` | 更新记录字段值 |
| `TestRecordCRUD` | `test_delete_record` | 删除后返回 404 |
| `TestUniversalAPI` | `test_create_record_by_name` | 通过 API name 创建记录 |
| `TestUniversalAPI` | `test_list_records_by_name` | 通过 API name 列表查询 |
| `TestDeleteCustomObject` | `test_delete_object` | 删除对象（含动态表）后返回 404 |

### 3.6 工作流引擎 (`test_workflows.py`) — 13 个测试

| 测试类 | 测试方法 | 验证内容 |
|---|---|---|
| `TestConditionEvaluator` | `test_eq_operator` | 等于操作符 |
| `TestConditionEvaluator` | `test_gt_operator` | 大于操作符 |
| `TestConditionEvaluator` | `test_contains_operator` | 包含操作符 |
| `TestConditionEvaluator` | `test_multiple_conditions_anded` | 多条件 AND 逻辑 |
| `TestConditionEvaluator` | `test_empty_conditions_always_true` | 空条件始终为真 |
| `TestConditionEvaluator` | `test_is_empty_operator` | 为空操作符 |
| `TestConditionEvaluator` | `test_missing_field_treated_as_none` | 缺失字段视为空 |
| `TestWorkflowCRUD` | `test_create_workflow` | 创建工作流（含动作） |
| `TestWorkflowCRUD` | `test_list_workflows` | 列表返回所有规则 |
| `TestWorkflowCRUD` | `test_get_workflow` | 按 ID 获取 |
| `TestWorkflowCRUD` | `test_update_workflow` | 更新名称和状态 |
| `TestWorkflowCRUD` | `test_delete_workflow` | 删除后 404 |
| `TestWorkflowTest` | `test_workflow_condition_match` | 测试条件匹配 |
| `TestWorkflowTest` | `test_workflow_condition_no_match` | 测试条件不匹配 |

### 3.7 拜访事件 (`test_events.py`) — 30 个测试

| 测试类 | 测试方法 | 验证内容 |
|---|---|---|
| `TestListEvents` | `test_list_empty` | 空列表返回 total=0 |
| `TestListEvents` | `test_list_with_data` | 创建后列表包含两条记录 |
| `TestListEvents` | `test_search_by_subject` | 按主题搜索过滤 |
| `TestListEvents` | `test_filter_by_status` | 按状态筛选 |
| `TestListEvents` | `test_filter_by_type` | 按类型筛选 |
| `TestCreateEvent` | `test_create_minimal` | 最小字段创建成功 |
| `TestCreateEvent` | `test_create_full` | 全字段创建成功 |
| `TestCreateEvent` | `test_create_with_what_id` | 关联账户创建成功 |
| `TestCreateEvent` | `test_create_missing_subject` | 缺少必填主题返回 422 |
| `TestCreateEvent` | `test_create_missing_start_datetime` | 缺少必填时间返回 422 |
| `TestGetEvent` | `test_get_by_id` | 按 ID 获取事件 |
| `TestGetEvent` | `test_get_not_found` | 不存在返回 404 |
| `TestUpdateEvent` | `test_update` | 更新事件字段 |
| `TestUpdateEvent` | `test_update_not_found` | 更新不存在返回 404 |
| `TestDeleteEvent` | `test_delete` | 删除后返回 204 |
| `TestDeleteEvent` | `test_delete_not_found` | 删除不存在返回 404 |
| `TestCheckInOut` | `test_check_in` | 签到成功，状态变为 in_progress |
| `TestCheckInOut` | `test_check_in_with_location` | 签到带位置信息 |
| `TestCheckInOut` | `test_check_in_not_planned` | 已签到事件不能重复签到 |
| `TestCheckInOut` | `test_check_out` | 签退成功，状态变为 completed |
| `TestCheckInOut` | `test_check_out_without_check_in` | 未签到不能签退 |
| `TestCheckInOut` | `test_check_in_not_found` | 签到不存在的事件返回 404 |
| `TestCheckInOut` | `test_check_out_not_found` | 签退不存在的事件返回 404 |
| `TestTaskCRUD` | `test_create_task` | 创建任务成功 |
| `TestTaskCRUD` | `test_list_tasks` | 列表返回所有任务 |
| `TestTaskCRUD` | `test_update_task` | 更新任务状态 |
| `TestTaskCRUD` | `test_delete_task` | 删除任务 |
| `TestTaskCRUD` | `test_task_update_not_found` | 更新不存在任务返回 404 |
| `TestTaskCRUD` | `test_task_delete_not_found` | 删除不存在任务返回 404 |
| `TestEventHistory` | `test_account_event_history` | 按账户获取拜访历史 |
| `TestEventHistory` | `test_opportunity_event_history` | 按商机获取拜访历史 |
| `TestEventHistory` | `test_contact_event_history` | 按联系人获取拜访历史 |

### 3.8 个人信息 (`test_profile.py`) — 11 个测试

| 测试类 | 测试方法 | 验证内容 |
|---|---|---|
| `TestUpdateProfile` | `test_update_display_name` | 更新显示名称 |
| `TestUpdateProfile` | `test_update_email` | 更新邮箱 |
| `TestUpdateProfile` | `test_update_both` | 同时更新多个字段 |
| `TestUpdateProfile` | `test_update_empty_body` | 空请求体返回 400 |
| `TestUpdateProfile` | `test_update_unauthorized` | 未认证返回 403 |
| `TestChangePassword` | `test_change_password_success` | 修改密码成功后可用新密码登录 |
| `TestChangePassword` | `test_change_password_wrong_current` | 旧密码错误返回 400 |
| `TestChangePassword` | `test_change_password_mismatch` | 两次密码不一致返回 400 |
| `TestChangePassword` | `test_change_password_too_short` | 密码太短返回 400 |
| `TestChangePassword` | `test_change_password_unauthorized` | 未认证返回 403 |
| `TestMyTerritories` | `test_my_territories_empty` | 空区域返回空列表 |
| `TestMyTerritories` | `test_my_territories_structure` | 响应结构包含所有字段 |
| `TestMyTerritories` | `test_my_territories_unauthorized` | 未认证返回 403 |

### 3.9 报表与仪表盘 (`test_reports.py`) — 13 个测试

| 测试类 | 测试方法 | 验证内容 |
|---|---|---|
| `TestReportCRUD` | `test_create_report` | 创建报表定义 |
| `TestReportCRUD` | `test_list_reports` | 列表返回 |
| `TestReportCRUD` | `test_get_report` | 按 ID 获取 |
| `TestReportCRUD` | `test_update_report` | 更新报表配置 |
| `TestReportCRUD` | `test_delete_report` | 删除报表 |
| `TestRunReport` | `test_run_account_report` | 执行账户报表 |
| `TestRunReport` | `test_run_report_with_filter` | 带筛选条件的报表 |
| `TestDashboardCRUD` | `test_create_dashboard` | 创建仪表盘 |
| `TestDashboardCRUD` | `test_list_dashboards` | 列表 |
| `TestDashboardCRUD` | `test_get_dashboard_with_components` | 获取含组件的仪表盘 |
| `TestDashboardCRUD` | `test_delete_dashboard` | 删除仪表盘 |
| `TestDashboardComponent` | `test_add_component` | 添加仪表盘组件 |
| `TestDashboardComponent` | `test_delete_component` | 删除仪表盘组件 |

---

## 4. 测试统计

| 模块 | 文件 | 测试数 |
|---|---|---|
| 认证 | `test_auth.py` | 10 |
| 账户 | `test_accounts.py` | 12 |
| 联系人 | `test_contacts.py` | 8 |
| 销售机会 | `test_opportunities.py` | 9 |
| 自定义对象 | `test_custom_objects.py` | 17 |
| 工作流 | `test_workflows.py` | 13 |
| 报表 | `test_reports.py` | 13 |
| 拜访事件 | `test_events.py` | 30 |
| 个人信息 | `test_profile.py` | 11 |
| **合计** | | **124** |

---

## 4. Fixture 体系

| Fixture | 作用域 | 用途 |
|---|---|---|
| `event_loop` | session | 创建测试事件循环 |
| `setup_database` | function (autouse) | 每次测试前建表，测试后删表 |
| `client` | function | 提供 Async HTTP 客户端 |
| `user_token` | function | 注册用户并返回 token |
| `auth_headers` | function | 提供 Authorization 请求头 |
| `seeded_stages` | function | 初始化 7 个销售阶段 |

---

## 5. 测试策略

### 正常路径测试
每个 API 端点的成功路径都被覆盖（200/201 响应）。

### 错误路径测试
- 404: 请求不存在的资源
- 400: 无效请求（重复、缺少必填）
- 401: 未授权或密码错误
- 422: 请求体验证失败
- 403: 未提供认证信息

### 边界测试
- 空列表
- 搜索/筛选
- 分页

### 核心逻辑单元测试
工作流条件评估器（`ConditionEvaluator`）被作为纯函数单独测试，覆盖所有操作符。

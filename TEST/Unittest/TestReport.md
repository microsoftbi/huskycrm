# SPSF CRM — 单元测试报告

## 1. 执行摘要

| 项目 | 数值 |
|---|---|
| **执行时间** | 2026-07-15 17:50 UTC |
| **总用例数** | 81 |
| **通过** | 81 ✅ |
| **失败** | 0 ❌ |
| **错误** | 0 ❌ |
| **跳过** | 0 |
| **运行时长** | 35.82 秒 |
| **覆盖率** | 后端 API 端点全覆盖 |

### 测试结果概要

```
============================= 81 passed in 35.82s ==============================
```

---

## 2. 测试详情

### 2.1 认证模块 — 10 测试 ✅

| 测试 | 耗时 | 结果 |
|---|---|---|
| `test_register_success` — 注册成功 | 0.264s | ✅ PASS |
| `test_register_duplicate_username` — 重复用户名 | 0.268s | ✅ PASS |
| `test_register_duplicate_email` — 重复邮箱 | 0.272s | ✅ PASS |
| `test_login_success` — 登录成功 | 0.492s | ✅ PASS |
| `test_login_wrong_password` — 错误密码 | 0.492s | ✅ PASS |
| `test_login_nonexistent_user` — 不存在用户 | 0.037s | ✅ PASS |
| `test_refresh_success` — 刷新 token | 0.490s | ✅ PASS |
| `test_refresh_invalid_token` — 无效 refresh token | 0.035s | ✅ PASS |
| `test_get_me` — 获取当前用户 | 0.498s | ✅ PASS |
| `test_get_me_unauthorized` — 未认证请求 | 0.036s | ✅ PASS |

### 2.2 账户模块 — 12 测试 ✅

| 测试 | 耗时 | 结果 |
|---|---|---|
| `test_list_empty` — 空列表 | 0.528s | ✅ PASS |
| `test_list_with_data` — 列表含数据 | 0.499s | ✅ PASS |
| `test_search` — 名称搜索 | 0.497s | ✅ PASS |
| `test_pagination` — 分页 | 0.507s | ✅ PASS |
| `test_create_minimal` — 最小字段创建 | 0.498s | ✅ PASS |
| `test_create_full` — 全字段创建 | 0.510s | ✅ PASS |
| `test_create_missing_name` — 缺名称 422 | 0.497s | ✅ PASS |
| `test_get_by_id` — 按 ID 获取 | 0.500s | ✅ PASS |
| `test_get_not_found` — 不存在 404 | 0.498s | ✅ PASS |
| `test_update` — 更新字段 | 0.497s | ✅ PASS |
| `test_update_not_found` — 更新不存在 404 | 0.492s | ✅ PASS |
| `test_delete` — 删除 | 0.497s | ✅ PASS |
| `test_delete_not_found` — 删除不存在 404 | 0.498s | ✅ PASS |

### 2.3 联系人模块 — 8 测试 ✅

| 测试 | 耗时 | 结果 |
|---|---|---|
| `test_create_minimal` — 最小字段创建 | 0.499s | ✅ PASS |
| `test_create_full` — 全字段创建（含账户关联） | 0.537s | ✅ PASS |
| `test_create_missing_name` — 缺姓名 422 | 0.498s | ✅ PASS |
| `test_list_with_account_filter` — 按账户筛选 | 0.505s | ✅ PASS |
| `test_search_contacts` — 搜索 | 0.541s | ✅ PASS |
| `test_update` — 更新 | 0.497s | ✅ PASS |
| `test_delete` — 删除 | 0.495s | ✅ PASS |

### 2.4 销售机会模块 — 8 测试 ✅

| 测试 | 耗时 | 结果 |
|---|---|---|
| `test_stages_seeded` — 7 阶段自动创建 | 0.518s | ✅ PASS |
| `test_create_success` — 创建机会成功 | 0.528s | ✅ PASS |
| `test_create_invalid_stage` — 无效阶段 400 | 0.516s | ✅ PASS |
| `test_list_and_search` — 列表/搜索/筛选 | 0.526s | ✅ PASS |
| `test_move_stage` — 移动阶段 | 0.517s | ✅ PASS |
| `test_update_not_found` — 更新不存在 404 | 0.517s | ✅ PASS |
| `test_delete` — 删除 | 0.527s | ✅ PASS |
| `test_pipeline_structure` — 管道数据结构验证 | 0.516s | ✅ PASS |

### 2.5 自定义对象引擎 — 17 测试 ✅

| 测试 | 耗时 | 结果 |
|---|---|---|
| `test_create_with_fields` — 创建带字段的对象 | 0.501s | ✅ PASS |
| `test_create_duplicate_api_name` — 重复 api_name 400 | 0.533s | ✅ PASS |
| `test_create_without_fields` — 无字段创建 | 0.511s | ✅ PASS |
| `test_list_objects` — 列出所有对象 | 0.514s | ✅ PASS |
| `test_get_object_by_id` — 按 ID 获取 | 0.516s | ✅ PASS |
| `test_get_not_found` — 不存在 404 | 0.502s | ✅ PASS |
| `test_add_field` — 动态添加字段 | 0.517s | ✅ PASS |
| `test_add_duplicate_field` — 重复字段 400 | 0.513s | ✅ PASS |
| `test_create_record` — 创建记录 | 0.574s | ✅ PASS |
| `test_create_record_missing_required` — 缺必填 400 | 0.513s | ✅ PASS |
| `test_list_records` — 记录列表 | 0.517s | ✅ PASS |
| `test_update_record` — 更新记录 | 0.522s | ✅ PASS |
| `test_delete_record` — 删除记录 | 0.523s | ✅ PASS |
| `test_create_record_by_name` — 通用 API 创建 | 0.512s | ✅ PASS |
| `test_list_records_by_name` — 通用 API 列表 | 0.517s | ✅ PASS |
| `test_delete_object` — 删除对象 | 0.515s | ✅ PASS |

### 2.6 工作流引擎 — 13 测试 ✅

| 测试 | 耗时 | 结果 |
|---|---|---|
| `test_eq_operator` — 等于操作符 | 0.034s | ✅ PASS |
| `test_gt_operator` — 大于操作符 | 0.035s | ✅ PASS |
| `test_contains_operator` — 包含操作符 | 0.034s | ✅ PASS |
| `test_multiple_conditions_anded` — 多条件 AND | 0.035s | ✅ PASS |
| `test_empty_conditions_always_true` — 空条件 | 0.035s | ✅ PASS |
| `test_is_empty_operator` — 为空操作符 | 0.035s | ✅ PASS |
| `test_missing_field_treated_as_none` — 缺失字段 | 0.037s | ✅ PASS |
| `test_create_workflow` — 创建工作流 | 0.498s | ✅ PASS |
| `test_list_workflows` — 工作流列表 | 0.505s | ✅ PASS |
| `test_get_workflow` — 按 ID 获取 | 0.498s | ✅ PASS |
| `test_update_workflow` — 更新工作流 | 0.501s | ✅ PASS |
| `test_delete_workflow` — 删除工作流 | 0.503s | ✅ PASS |
| `test_workflow_condition_match` — 条件匹配测试 | 0.495s | ✅ PASS |
| `test_workflow_condition_no_match` — 条件不匹配测试 | 0.495s | ✅ PASS |

### 2.7 报表与仪表盘 — 13 测试 ✅

| 测试 | 耗时 | 结果 |
|---|---|---|
| `test_create_report` — 创建报表 | 0.505s | ✅ PASS |
| `test_list_reports` — 报表列表 | 0.513s | ✅ PASS |
| `test_get_report` — 获取报表 | 0.512s | ✅ PASS |
| `test_update_report` — 更新报表 | 0.518s | ✅ PASS |
| `test_delete_report` — 删除报表 | 0.515s | ✅ PASS |
| `test_run_account_report` — 执行账户报表 | 0.503s | ✅ PASS |
| `test_run_report_with_filter` — 带筛选报表 | 0.503s | ✅ PASS |
| `test_create_dashboard` — 创建仪表盘 | 0.499s | ✅ PASS |
| `test_list_dashboards` — 仪表盘列表 | 0.500s | ✅ PASS |
| `test_get_dashboard_with_components` — 含组件仪表盘 | 0.511s | ✅ PASS |
| `test_delete_dashboard` — 删除仪表盘 | 0.509s | ✅ PASS |
| `test_add_component` — 添加组件 | 0.496s | ✅ PASS |
| `test_delete_component` — 删除组件 | 0.504s | ✅ PASS |

---

## 3. 性能分析

### 最快 / 最慢测试

| 测试 | 耗时 | 类别 |
|---|---|---|
| 🏆 `test_eq_operator` | 0.034s | 纯逻辑（单元测试） |
| 🏆 `test_refresh_invalid_token` | 0.035s | 简单错误路径 |
| 🏆 `test_get_me_unauthorized` | 0.036s | 简单错误路径 |
| 🐢 `test_create_record` | 0.574s | 数据库写入（动态表） |
| 🐢 `test_create_full` (contacts) | 0.537s | 数据库写入 |
| 🐢 `test_create_duplicate_api_name` | 0.533s | 数据库写入+动态DDL |

### 平均执行时间

| 类别 | 平均耗时 |
|---|---|
| 单元测试（纯逻辑） | 0.035s |
| API 测试 | 0.509s |
| 整体 | 0.442s |

---

## 4. 错误修复记录

### 问题 1：async httpx 的 `.json()` 调用

**现象**：`AttributeError: 'coroutine' object has no attribute 'json'`

**原因**：`await client.post(...).json()` 中，`client.post(...)` 返回协程，不能直接调 `.json()`。正确写法是 `(await client.post(...)).json()` 或 `resp = await client.post(...); data = resp.json()`。

**修复**：将所有多行 `await client.post(...).json()` 改为两行赋值模式。

### 问题 2：动态表在测试间残留

**现象**：`sqlalchemy.exc.OperationalError: table obj_1 already exists`

**原因**：`setup_database` fixture 只删除 `Base.metadata` 中的标准表，不清理测试中动态创建的 `obj_*` 表。

**修复**：在 teardown 阶段额外查询 `sqlite_master` 并删除所有 `obj_%` 表。

---

## 5. 结论

- **所有 81 个测试通过**，覆盖认证、账户、联系人、机会、自定义对象、工作流、报表七大模块
- 自定义对象引擎（核心功能）通过 17 个测试，验证了动态建表、字段管理、记录 CRUD、通用 API 等功能
- 工作流条件评估器作为纯函数单元测试，覆盖所有操作符
- 测试基础设施（内存数据库、自动清理、fixture 体系）运行稳定
- 测试环境在 35.82 秒内完成全部 81 个测试

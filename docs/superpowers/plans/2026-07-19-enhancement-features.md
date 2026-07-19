# Enhancement Features Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement 4 CRM enhancement features: activity timeline, notification center, global search, and CSV import/export.

**Architecture:** Backend in FastAPI + SQLAlchemy async with SQLite; frontend in Vue 3 + TypeScript + Element Plus. The audit log uses SQLAlchemy event listeners for automatic recording. Global search uses SQLite FTS5 for full-text search. Notifications use polling (30s). Import uses a two-phase upload→confirm flow.

**Tech Stack:** Python 3.11+, FastAPI, SQLAlchemy 2.0 async, SQLite (aiosqlite), Vue 3, TypeScript, Element Plus, Axios

## Global Constraints

- All new model IDs use GUID format with prefix via `generate_id()` from `app/utils/id_gen.py` (e.g. `aud_`, `not_`, `imp_`)
- Backend test files go in `TEST/Unittest/` alongside existing tests
- Frontend API clients follow the pattern in `frontend/src/api/` (Axios instance from `client.ts`)
- All new Pydantic schemas use `from_attributes = True` in `class Config`
- All new API endpoints require auth via `get_current_user` dependency
- Use `require_permission("read")` for read endpoints, etc.
- All new frontend types go in `frontend/src/types/`
- Follow existing naming conventions: kebab-case for Vue files, camelCase for TS/JS, snake_case for Python

---

## File Structure

### Phase 1: Activity Timeline

**Backend — Create:**
- `backend/app/models/audit_log.py` — AuditLog model
- `backend/app/schemas/audit_log.py` — AuditLogIn, TimelineEntry schemas
- `backend/app/services/audit_service.py` — SQLAlchemy event listener setup + contextvar middleware
- `backend/app/api/audit_logs.py` — `/api/audit-logs` and `/api/timeline` endpoints

**Backend — Modify:**
- `backend/app/database.py` — Import AuditLog model, call `setup_audit_listeners()`
- `backend/app/main.py` — Register audit_logs router
- `backend/app/core/deps.py` — Add `set_current_user` middleware for contextvar

**Frontend — Create:**
- `frontend/src/types/auditLog.ts` — AuditLog, TimelineEntry types
- `frontend/src/api/auditLogs.ts` — API client
- `frontend/src/components/activity/Timeline.vue` — Reusable timeline component

**Frontend — Modify:**
- `frontend/src/views/accounts/AccountDetail.vue` — Add "活动" tab
- `frontend/src/views/contacts/ContactDetail.vue` — Add "活动" tab
- `frontend/src/views/opportunities/OpportunityDetail.vue` — Add "活动" tab

### Phase 2: Notification Center

**Backend — Create:**
- `backend/app/models/notification.py` — Notification model
- `backend/app/schemas/notification.py` — Notification schemas
- `backend/app/api/notifications.py` — Notification API endpoints
- `backend/app/services/notification_service.py` — Helper functions for creating notifications

**Backend — Modify:**
- `backend/app/database.py` — Import Notification model
- `backend/app/main.py` — Register notifications router
- `backend/app/api/territories.py` — Add system notifications on territory member/account assignment
- `backend/app/services/workflow_service.py` — Create notifications when workflow action is "send_notification"

**Frontend — Create:**
- `frontend/src/types/notification.ts` — Notification types
- `frontend/src/api/notifications.ts` — API client
- `frontend/src/composables/useNotifications.ts` — Polling composable
- `frontend/src/components/notification/NotificationBell.vue` — Bell icon + badge
- `frontend/src/components/notification/NotificationDropdown.vue` — Dropdown panel
- `frontend/src/views/admin/NotificationList.vue` — Full notification list page

**Frontend — Modify:**
- `frontend/src/components/layout/Header.vue` — Add NotificationBell
- `frontend/src/router/index.ts` — Add notification list route

### Phase 3: Global Search

**Backend — Create:**
- `backend/app/services/search_service.py` — FTS5 index management + triggers
- `backend/app/api/search.py` — `/api/search` endpoint

**Backend — Modify:**
- `backend/app/database.py` — Create FTS5 virtual table, seed triggers
- `backend/app/main.py` — Register search router

**Frontend — Create:**
- `frontend/src/types/search.ts` — SearchResult types
- `frontend/src/api/search.ts` — API client
- `frontend/src/components/search/GlobalSearch.vue` — Search input + dropdown panel

**Frontend — Modify:**
- `frontend/src/components/layout/Header.vue` — Replace search input with GlobalSearch component

### Phase 4: Import / Export

**Backend — Create:**
- `backend/app/models/import_job.py` — ImportJob model
- `backend/app/schemas/import_export.py` — Import/export schemas
- `backend/app/services/csv_service.py` — CSV parsing, field mapping, validation
- `backend/app/api/import_export.py` — Import/export endpoints

**Backend — Modify:**
- `backend/app/database.py` — Import ImportJob model
- `backend/app/main.py` — Register import_export router

**Frontend — Create:**
- `frontend/src/types/importJob.ts` — ImportJob types
- `frontend/src/api/importExport.ts` — API client
- `frontend/src/components/import/ImportWizard.vue` — 3-step import dialog

**Frontend — Modify:**
- `frontend/src/views/accounts/AccountList.vue` — Add import/export buttons
- `frontend/src/views/contacts/ContactList.vue` — Add import/export buttons
- `frontend/src/views/products/ProductList.vue` — Add import/export buttons
- `frontend/src/views/opportunities/OpportunityList.vue` — Add import/export buttons
- `frontend/src/views/custom-objects/ObjectRecords.vue` — Add export button

---

## Phase 1: Activity Timeline (Change History)

### Task 1.1: Create AuditLog model

**Files:**
- Create: `backend/app/models/audit_log.py`

**Interfaces:**
- Produces: `AuditLog` model class with columns `id`, `object_type`, `object_id`, `field_name`, `old_value`, `new_value`, `action`, `user_id`, `created_at`

- [ ] **Step 1: Create the model file**

```python
# backend/app/models/audit_log.py
from sqlalchemy import Column, String, DateTime, func
from app.database import Base
from app.utils.id_gen import generate_id


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: generate_id("aud_"))
    object_type = Column(String(80), nullable=False, index=True)
    object_id = Column(String(36), nullable=False, index=True)
    field_name = Column(String(80), nullable=True)
    old_value = Column(String, nullable=True)
    new_value = Column(String, nullable=True)
    action = Column(String(20), nullable=False)  # "create" | "update" | "delete"
    user_id = Column(String(36), nullable=False, index=True)
    created_at = Column(DateTime, default=func.now())
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/models/audit_log.py
git commit -m "feat: add AuditLog model for change history tracking"
```

### Task 1.2: Create AuditLog schemas

**Files:**
- Create: `backend/app/schemas/audit_log.py`

**Interfaces:**
- Produces: `AuditLogOut`, `TimelineEntry`, `TimelineResponse` schemas

- [ ] **Step 1: Create the schema file**

```python
# backend/app/schemas/audit_log.py
from pydantic import BaseModel
from datetime import datetime


class AuditLogOut(BaseModel):
    id: str
    object_type: str
    object_id: str
    field_name: str | None = None
    old_value: str | None = None
    new_value: str | None = None
    action: str
    user_id: str
    created_at: datetime | None = None

    class Config:
        from_attributes = True


class TimelineEntry(BaseModel):
    type: str  # "audit" | "event" | "task"
    action: str | None = None
    field_name: str | None = None
    old_value: str | None = None
    new_value: str | None = None
    subject: str | None = None
    status: str | None = None
    result: str | None = None
    user_id: str | None = None
    user_display_name: str | None = None
    created_at: datetime | None = None
    reference_id: str | None = None
    reference_type: str | None = None
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/schemas/audit_log.py
git commit -m "feat: add AuditLog schemas and TimelineEntry type"
```

### Task 1.3: Implement audit service with SQLAlchemy event listeners

**Files:**
- Create: `backend/app/services/audit_service.py`

**Interfaces:**
- Produces: `setup_audit_listeners()` function that attaches event handlers to all models
- Consumes: `AuditLog` model, `get_current_user_id()` from contextvar

- [ ] **Step 1: Create the audit service with contextvar support**

```python
# backend/app/services/audit_service.py
import contextvars
from sqlalchemy import event
from sqlalchemy.orm import Mapper
from sqlalchemy.orm.attributes import get_history
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.auth import User
from app.models.audit_log import AuditLog

# Context variable to hold current user ID for audit logging
current_user_id: contextvars.ContextVar[str | None] = contextvars.ContextVar("current_user_id", default=None)

# Models to audit (all core CRM models)
AUDIT_MODELS = [
    "Account", "Contact", "Opportunity", "Product",
    "Event", "Task",
    "Territory", "TerritoryMember", "TerritoryAccount", "TerritoryProduct",
    "CustomObjectDef", "CustomFieldDef",
    "WorkflowRule", "WorkflowAction",
    "Report", "Dashboard", "DashboardComponent",
]

# Fields to exclude from audit logging
EXCLUDED_FIELDS = {"password_hash", "updated_at", "created_at"}

_audit_listeners_attached = False


def setup_audit_listeners():
    """Attach SQLAlchemy event listeners to all audited models."""
    global _audit_listeners_attached
    if _audit_listeners_attached:
        return
    _audit_listeners_attached = True

    # We attach listeners dynamically — models are imported at database.py
    # This is called from init_db() after all models are imported


def attach_listeners(model_class):
    """Attach after_insert/after_update/after_delete listeners to a model class."""
    @event.listens_for(model_class, "after_insert")
    def receive_after_insert(mapper: Mapper, connection, target):
        _record_audit(connection, target, "create")

    @event.listens_for(model_class, "after_update")
    def receive_after_update(mapper: Mapper, connection, target):
        _record_audit(connection, target, "update")

    @event.listens_for(model_class, "after_delete")
    def receive_after_delete(mapper: Mapper, connection, target):
        _record_audit(connection, target, "delete")


def _record_audit(connection, target, action: str):
    """Record an audit log entry for the given target object and action."""
    object_type = target.__class__.__name__
    object_id = str(target.id)
    user_id = current_user_id.get() or "system"

    if action == "create":
        connection.execute(
            AuditLog.__table__.insert().values(
                object_type=object_type,
                object_id=object_id,
                field_name=None,
                old_value=None,
                new_value=None,
                action="create",
                user_id=user_id,
            )
        )
    elif action == "delete":
        connection.execute(
            AuditLog.__table__.insert().values(
                object_type=object_type,
                object_id=object_id,
                field_name=None,
                old_value=None,
                new_value=None,
                action="delete",
                user_id=user_id,
            )
        )
    elif action == "update":
        # Check each column for changes
        for col in target.__table__.columns:
            field_name = col.name
            if field_name in EXCLUDED_FIELDS or field_name == "id":
                continue

            hist = get_history(target, field_name)
            if hist.has_changes():
                old_val = str(hist.deleted[0]) if hist.deleted else None
                new_val = str(hist.added[0]) if hist.added else None
                connection.execute(
                    AuditLog.__table__.insert().values(
                        object_type=object_type,
                        object_id=object_id,
                        field_name=field_name,
                        old_value=old_val,
                        new_value=new_val,
                        action="update",
                        user_id=user_id,
                    )
                )
```

- [ ] **Step 2: Add middleware to set current_user_id contextvar**

In `backend/app/core/deps.py`, add the contextvar middleware:

```python
# Add to existing deps.py
from app.services.audit_service import current_user_id

# ... existing get_current_user function ...

# In main.py, we'll add a middleware that sets current_user_id
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/services/audit_service.py
git commit -m "feat: implement audit log service with SQLAlchemy event listeners"
```

### Task 1.4: Wire audit service into database.py and main.py

**Files:**
- Modify: `backend/app/database.py` — Import AuditLog model, call `setup_audit_listeners()` and `attach_listeners()` for each model
- Modify: `backend/app/main.py` — Register audit_logs router, add middleware for current_user_id

- [ ] **Step 1: Update database.py**

Edit `backend/app/database.py` to add the AuditLog model import and call `setup_audit_listeners()`:

In the `init_db()` function, after all model imports, add:
```python
from app.models.audit_log import AuditLog  # noqa: F401
from app.services.audit_service import setup_audit_listeners, attach_listeners

# ... existing imports ...

async def init_db():
    """Create all tables."""
    from app.models.auth import User  # noqa: F401
    from app.models.crm import Account, Contact, Stage, Opportunity, Product, OpportunityProduct  # noqa: F401
    from app.models.custom_object import CustomObjectDef, CustomFieldDef  # noqa: F401
    from app.models.workflow import WorkflowRule, WorkflowAction, WorkflowExecutionLog  # noqa: F401
    from app.models.report import Report, Dashboard, DashboardComponent  # noqa: F401
    from app.models.territory import Territory, TerritoryMember, TerritoryAccount, TerritoryProduct  # noqa: F401
    from app.models.event import Event, Task  # noqa: F401
    from app.models.profile import Profile  # noqa: F401
    from app.models.audit_log import AuditLog  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await seed_default_profiles()

    # Attach audit listeners to all models
    setup_audit_listeners()
    for model_cls in [User, Account, Contact, Opportunity, Product, Event, Task,
                      Territory, TerritoryMember, TerritoryAccount, TerritoryProduct,
                      CustomObjectDef, CustomFieldDef,
                      WorkflowRule, WorkflowAction,
                      Report, Dashboard, DashboardComponent]:
        attach_listeners(model_cls)
```

- [ ] **Step 2: Update main.py**

Edit `backend/app/main.py`:
```python
# Add to the imports section
from app.api import (
    auth, accounts, contacts, opportunities, custom_objects, workflows, reports,
    products, territories, events, profiles, audit_logs,
)
from app.services.audit_service import current_user_id
from app.core.deps import get_current_user

# Add after the CORSMiddleware setup:
@app.middleware("http")
async def set_audit_user(request, call_next):
    """Set current user ID in audit contextvar for automatic audit logging."""
    # Set default first
    token = current_user_id.set("system")
    try:
        # Try to get the current user from the request
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            from app.core.security import decode_token
            token_str = auth_header.split(" ")[1]
            payload = decode_token(token_str)
            if payload and payload.get("sub"):
                current_user_id.set(payload["sub"])
        response = await call_next(request)
        return response
    finally:
        current_user_id.reset(token)

# Also include the router:
app.include_router(audit_logs.router)
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/database.py backend/app/main.py
git commit -m "feat: wire audit log service into database and main app"
```

### Task 1.5: Create audit log API endpoints

**Files:**
- Create: `backend/app/api/audit_logs.py`

- [ ] **Step 1: Create the API file**

```python
# backend/app/api/audit_logs.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.audit_log import AuditLog
from app.models.auth import User
from app.models.event import Event, Task
from app.schemas.audit_log import TimelineEntry
from app.core.deps import get_current_user
from app.core.permissions import require_permission

router = APIRouter(prefix="/api", tags=["audit-logs"])


@router.get("/audit-logs/{object_type}/{object_id}", response_model=list[TimelineEntry])
async def get_audit_logs(
    object_type: str,
    object_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("read")),
):
    """Get change history for a specific record."""
    # Map common object type names to model class names
    type_map = {
        "account": "Account", "contact": "Contact", "opportunity": "Opportunity",
        "product": "Product", "event": "Event", "task": "Task",
        "territory": "Territory",
    }
    model_type = type_map.get(object_type.lower(), object_type)

    query = (
        select(AuditLog)
        .where(AuditLog.object_type == model_type, AuditLog.object_id == object_id)
        .order_by(AuditLog.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(query)
    logs = result.scalars().all()

    entries = []
    for log in logs:
        # Get user display name
        user_result = await db.execute(select(User).where(User.id == log.user_id))
        user = user_result.scalar_one_or_none()

        entries.append(TimelineEntry(
            type="audit",
            action=log.action,
            field_name=log.field_name,
            old_value=log.old_value,
            new_value=log.new_value,
            user_id=log.user_id,
            user_display_name=user.display_name if user else "System",
            created_at=log.created_at,
        ))

    return entries


@router.get("/timeline/{object_type}/{object_id}", response_model=list[TimelineEntry])
async def get_timeline(
    object_type: str,
    object_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("read")),
):
    """Get merged timeline: audit logs + related events + tasks."""
    type_map = {
        "account": "Account", "contact": "Contact", "opportunity": "Opportunity",
    }
    model_type = type_map.get(object_type.lower(), object_type)

    # 1. Get audit logs
    audit_query = (
        select(AuditLog)
        .where(AuditLog.object_type == model_type, AuditLog.object_id == object_id)
        .order_by(AuditLog.created_at.desc())
        .limit(50)
    )
    audit_result = await db.execute(audit_query)
    audit_logs = audit_result.scalars().all()

    entries = []
    for log in audit_logs:
        user_result = await db.execute(select(User).where(User.id == log.user_id))
        user = user_result.scalar_one_or_none()
        entries.append(TimelineEntry(
            type="audit",
            action=log.action,
            field_name=log.field_name,
            old_value=log.old_value,
            new_value=log.new_value,
            user_id=log.user_id,
            user_display_name=user.display_name if user else "System",
            created_at=log.created_at,
        ))

    # 2. Get related events (by what_id)
    if object_type.lower() in ("account", "contact", "opportunity"):
        what_type_map = {"account": "Account", "contact": "Contact", "opportunity": "Opportunity"}
        what_type = what_type_map[object_type.lower()]
        event_query = (
            select(Event)
            .where(Event.what_id == object_id, Event.what_type == what_type)
            .order_by(Event.actual_start_time.desc())
            .limit(20)
        )
        event_result = await db.execute(event_query)
        events = event_result.scalars().all()

        for ev in events:
            user_result = await db.execute(select(User).where(User.id == ev.owner_id))
            user = user_result.scalar_one_or_none()
            entries.append(TimelineEntry(
                type="event",
                subject=ev.subject,
                status=ev.status,
                result=ev.result,
                user_id=ev.owner_id,
                user_display_name=user.display_name if user else None,
                created_at=ev.actual_start_time or ev.created_at,
                reference_id=ev.id,
                reference_type="event",
            ))

            # 3. Get tasks for each event
            task_query = select(Task).where(Task.event_id == ev.id).order_by(Task.created_at.desc())
            task_result = await db.execute(task_query)
            tasks = task_result.scalars().all()
            for t in tasks:
                entries.append(TimelineEntry(
                    type="task",
                    subject=t.subject,
                    status="completed" if t.is_completed else "pending",
                    created_at=t.completed_at or t.created_at,
                    reference_id=t.id,
                    reference_type="task",
                ))

    # Sort all entries by created_at desc
    entries.sort(key=lambda e: e.created_at or "", reverse=True)

    # Paginate
    start = (page - 1) * page_size
    return entries[start:start + page_size]
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/api/audit_logs.py
git commit -m "feat: add audit log and timeline API endpoints"
```

### Task 1.6: Create frontend types and API client for audit logs

**Files:**
- Create: `frontend/src/types/auditLog.ts`
- Create: `frontend/src/api/auditLogs.ts`

- [ ] **Step 1: Create types file**

```typescript
// frontend/src/types/auditLog.ts
export interface TimelineEntry {
  type: 'audit' | 'event' | 'task'
  action?: string
  field_name?: string
  old_value?: string
  new_value?: string
  subject?: string
  status?: string
  result?: string
  user_id?: string
  user_display_name?: string
  created_at?: string
  reference_id?: string
  reference_type?: string
}
```

- [ ] **Step 2: Create API client**

```typescript
// frontend/src/api/auditLogs.ts
import apiClient from './client'
import type { TimelineEntry } from '../types/auditLog'

export const auditLogsApi = {
  getTimeline(objectType: string, objectId: string, page = 1) {
    return apiClient.get<TimelineEntry[]>(`/timeline/${objectType}/${objectId}`, { params: { page } })
  },
}
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/types/auditLog.ts frontend/src/api/auditLogs.ts
git commit -m "feat: add frontend types and API client for timeline"
```

### Task 1.7: Create Timeline.vue component

**Files:**
- Create: `frontend/src/components/activity/Timeline.vue`

- [ ] **Step 1: Create the Timeline component**

```vue
<!-- frontend/src/components/activity/Timeline.vue -->
<template>
  <div class="timeline" v-loading="loading">
    <div v-if="entries.length === 0" class="timeline-empty">
      <el-empty description="暂无活动记录" :image-size="60" />
    </div>
    <div v-else class="timeline-list">
      <!-- Date group header -->
      <template v-for="(group, gIdx) in groupedEntries" :key="gIdx">
        <div class="timeline-date-header">{{ group.date }}</div>
        <div
          v-for="(entry, eIdx) in group.entries"
          :key="`${gIdx}-${eIdx}`"
          class="timeline-item"
          :class="`timeline-type-${entry.type}`"
        >
          <div class="timeline-dot">
            <el-icon v-if="entry.type === 'audit'" :size="12"><edit-pen /></el-icon>
            <el-icon v-else-if="entry.type === 'event'" :size="12"><phone /></el-icon>
            <el-icon v-else :size="12"><check /></el-icon>
          </div>
          <div class="timeline-content">
            <div class="timeline-header">
              <span class="timeline-user">{{ entry.user_display_name || 'System' }}</span>
              <span class="timeline-time">{{ formatTime(entry.created_at) }}</span>
            </div>
            <div class="timeline-body">
              <!-- Audit entries -->
              <template v-if="entry.type === 'audit'">
                <span v-if="entry.action === 'create'">创建了此记录</span>
                <span v-else-if="entry.action === 'delete'">删除了此记录</span>
                <span v-else-if="entry.action === 'update' && entry.field_name">
                  更新了 <strong>{{ fieldLabel(entry.field_name) }}</strong>
                  <span class="timeline-change" v-if="entry.old_value !== null">
                    {{ entry.old_value || '(空)' }} → {{ entry.new_value || '(空)' }}
                  </span>
                </span>
              </template>
              <!-- Event entries -->
              <template v-else-if="entry.type === 'event'">
                <span>完成了拜访 <strong>{{ entry.subject }}</strong></span>
                <el-tag v-if="entry.result" :type="resultType(entry.result)" size="small" class="timeline-tag">
                  {{ resultLabel(entry.result) }}
                </el-tag>
              </template>
              <!-- Task entries -->
              <template v-else>
                <span>完成任务 <strong>{{ entry.subject }}</strong></span>
              </template>
            </div>
          </div>
        </div>
      </template>

      <div v-if="hasMore" class="timeline-load-more">
        <el-button text type="primary" :loading="loadingMore" @click="$emit('load-more')">
          加载更多
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { EditPen, Phone, Check } from '@element-plus/icons-vue'
import type { TimelineEntry } from '../../types/auditLog'

const props = defineProps<{
  entries: TimelineEntry[]
  loading: boolean
  loadingMore?: boolean
  hasMore?: boolean
}>()

defineEmits<{
  'load-more': []
}>()

const FIELD_LABELS: Record<string, string> = {
  name: '名称', industry: '行业', phone: '电话', email: '邮箱',
  website: '网站', billing_street: '街道', billing_city: '城市',
  billing_state: '省份', billing_postal_code: '邮编', billing_country: '国家',
  description: '描述', first_name: '姓', last_name: '名', mobile: '手机',
  title: '职位', department: '部门', amount: '金额', stage_id: '销售阶段',
  close_date: '预计关闭日期', probability: '成功率', product_code: '产品编码',
  standard_price: '标准价格', cost: '成本', category: '分类', is_active: '是否启用',
  subject: '主题', type: '类型', status: '状态',
}

function fieldLabel(field: string): string {
  return FIELD_LABELS[field] || field
}

function formatTime(dateStr?: string): string {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

function formatDate(dateStr?: string): string {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  const today = new Date()
  const yesterday = new Date(today)
  yesterday.setDate(yesterday.getDate() - 1)

  if (d.toDateString() === today.toDateString()) return '今天'
  if (d.toDateString() === yesterday.toDateString()) return '昨天'
  return d.toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })
}

function resultType(result: string): string {
  const map: Record<string, string> = { success: 'success', neutral: 'info', failure: 'danger', no_show: 'warning' }
  return map[result] || 'info'
}

function resultLabel(result: string): string {
  const map: Record<string, string> = { success: '成功', neutral: '一般', failure: '失败', no_show: '未到' }
  return map[result] || result
}

const groupedEntries = computed(() => {
  const groups: { date: string; entries: TimelineEntry[] }[] = []
  let currentDate = ''
  let currentGroup: TimelineEntry[] = []

  for (const entry of [...props.entries].sort((a, b) => {
    return new Date(b.created_at || 0).getTime() - new Date(a.created_at || 0).getTime()
  })) {
    const date = formatDate(entry.created_at)
    if (date !== currentDate) {
      if (currentGroup.length > 0) {
        groups.push({ date: currentDate, entries: currentGroup })
      }
      currentDate = date
      currentGroup = [entry]
    } else {
      currentGroup.push(entry)
    }
  }
  if (currentGroup.length > 0) {
    groups.push({ date: currentDate, entries: currentGroup })
  }
  return groups
})
</script>

<style scoped>
.timeline { padding: 8px 0; }
.timeline-empty { padding: 40px 0; }
.timeline-list { position: relative; }
.timeline-date-header {
  font-size: 13px;
  font-weight: 600;
  color: #514f4d;
  padding: 12px 0 8px;
  border-bottom: 1px solid #e4e7ed;
  margin-bottom: 8px;
}
.timeline-item {
  display: flex;
  gap: 10px;
  padding: 8px 0;
  position: relative;
}
.timeline-dot {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-top: 2px;
}
.timeline-type-audit .timeline-dot { background: #e8f0fe; color: #1589ee; }
.timeline-type-event .timeline-dot { background: #e8f5e9; color: #67c23a; }
.timeline-type-task .timeline-dot { background: #fff3e0; color: #e6a23c; }
.timeline-content { flex: 1; min-width: 0; }
.timeline-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 2px;
}
.timeline-user { font-size: 12px; font-weight: 600; color: #333; }
.timeline-time { font-size: 11px; color: #909399; }
.timeline-body { font-size: 13px; color: #606266; line-height: 1.5; }
.timeline-change {
  display: block;
  font-size: 12px;
  color: #909399;
  background: #f5f7fa;
  padding: 4px 8px;
  border-radius: 3px;
  margin-top: 2px;
  word-break: break-all;
}
.timeline-tag { margin-left: 6px; }
.timeline-load-more { text-align: center; padding: 12px 0; }
</style>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/components/activity/Timeline.vue
git commit -m "feat: add Timeline.vue component for activity timeline display"
```

### Task 1.8: Add activity tab to detail pages

**Files:**
- Modify: `frontend/src/views/accounts/AccountDetail.vue`
- Modify: `frontend/src/views/contacts/ContactDetail.vue`
- Modify: `frontend/src/views/opportunities/OpportunityDetail.vue`

- [ ] **Step 1: Add activity tab to AccountDetail.vue**

In the script section, add:
```typescript
import { auditLogsApi } from '../../api/auditLogs'
import type { TimelineEntry } from '../../types/auditLog'
import Timeline from '../../components/activity/Timeline.vue'

// Add state
const timelineEntries = ref<TimelineEntry[]>([])
const timelineLoading = ref(false)
const timelinePage = ref(1)
const timelineHasMore = ref(true)

// Add to tabs computed
const tabs = computed(() => [
  { key: 'details', label: '详细信息' },
  { key: 'contacts', label: '联系人', count: contactsTotal.value },
  { key: 'activity', label: '活动' },
])

// Add load function
async function loadTimeline() {
  if (!account.value?.id) return
  timelineLoading.value = true
  try {
    const { data } = await auditLogsApi.getTimeline('account', account.value.id, timelinePage.value)
    if (timelinePage.value === 1) {
      timelineEntries.value = data
    } else {
      timelineEntries.value.push(...data)
    }
    timelineHasMore.value = data.length >= 20
  } catch {
    // silent
  } finally {
    timelineLoading.value = false
  }
}

function loadMoreTimeline() {
  timelinePage.value++
  loadTimeline()
}

// Call loadTimeline after account loads
watch(() => account.value?.id, (id) => {
  if (id) {
    timelinePage.value = 1
    loadTimeline()
  }
})
```

In the template, add the activity tab panel:
```vue
<template #panel-activity>
  <Timeline
    :entries="timelineEntries"
    :loading="timelineLoading"
    :has-more="timelineHasMore"
    @load-more="loadMoreTimeline"
  />
</template>
```

- [ ] **Step 2: Apply same pattern to ContactDetail.vue and OpportunityDetail.vue**

The changes are identical except:
- ContactDetail: `objectType = 'contact'`
- OpportunityDetail: `objectType = 'opportunity'`

- [ ] **Step 3: Commit**

```bash
git add frontend/src/views/accounts/AccountDetail.vue frontend/src/views/contacts/ContactDetail.vue frontend/src/views/opportunities/OpportunityDetail.vue
git commit -m "feat: add activity timeline tab to account, contact, and opportunity detail pages"
```

### Task 1.9: Phase 1 tests

**Files:**
- Create: `TEST/Unittest/test_audit_log.py`

- [ ] **Step 1: Write and run tests**

```python
# TEST/Unittest/test_audit_log.py
import pytest
from app.models.audit_log import AuditLog
from app.models.crm import Account
from app.services.audit_service import current_user_id


@pytest.mark.asyncio
async def test_audit_log_created_on_account_create(db_session):
    """Verify an audit log entry is created when a new account is inserted."""
    # Set current user context
    token = current_user_id.set("test_user")
    try:
        account = Account(name="Test Account", industry="Tech")
        db_session.add(account)
        await db_session.commit()
        await db_session.refresh(account)
    finally:
        current_user_id.reset(token)

    # Query audit log
    result = await db_session.execute(
        __import__("sqlalchemy").select(AuditLog).where(
            AuditLog.object_type == "Account",
            AuditLog.object_id == account.id,
        )
    )
    logs = result.scalars().all()
    assert len(logs) >= 1
    create_log = [l for l in logs if l.action == "create"]
    assert len(create_log) == 1
    assert create_log[0].user_id == "test_user"


@pytest.mark.asyncio
async def test_audit_log_recorded_on_update(db_session):
    token = current_user_id.set("test_user")
    try:
        account = Account(name="Original", industry="Tech")
        db_session.add(account)
        await db_session.commit()
        await db_session.refresh(account)

        account.name = "Updated"
        await db_session.commit()
    finally:
        current_user_id.reset(token)

    result = await db_session.execute(
        __import__("sqlalchemy").select(AuditLog).where(
            AuditLog.object_type == "Account",
            AuditLog.object_id == account.id,
            AuditLog.action == "update",
        )
    )
    logs = result.scalars().all()
    name_updates = [l for l in logs if l.field_name == "name"]
    assert len(name_updates) >= 1
    assert "Original" in name_updates[0].old_value
    assert "Updated" in name_updates[0].new_value
```

Run: `cd backend && python -m pytest TEST/Unittest/test_audit_log.py -v`
Expected: PASS

- [ ] **Step 2: Run all existing tests to verify no regressions**

Run: `cd backend && python -m pytest TEST/Unittest/ -v`
Expected: All existing tests + new tests pass

- [ ] **Step 3: Commit**

```bash
git add TEST/Unittest/test_audit_log.py
git commit -m "test: add audit log unit tests"
```

---

## Phase 2: Notification Center

### Task 2.1: Create Notification model

**Files:**
- Create: `backend/app/models/notification.py`

- [ ] **Step 1: Create the model**

```python
# backend/app/models/notification.py
from sqlalchemy import Column, String, Boolean, DateTime, func
from app.database import Base
from app.utils.id_gen import generate_id


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String(36), primary_key=True, default=lambda: generate_id("not_"))
    user_id = Column(String(36), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    message = Column(String, nullable=True)
    notification_type = Column(String(50), nullable=False)  # "workflow" | "system"
    reference_type = Column(String(80), nullable=True)
    reference_id = Column(String(36), nullable=True)
    is_read = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=func.now())
```

- [ ] **Step 2: Update database.py**

Add `from app.models.notification import Notification  # noqa: F401` to the imports in `init_db()`.

- [ ] **Step 3: Commit**

```bash
git add backend/app/models/notification.py backend/app/database.py
git commit -m "feat: add Notification model"
```

### Task 2.2: Create Notification schemas

**Files:**
- Create: `backend/app/schemas/notification.py`

- [ ] **Step 1: Create schemas**

```python
# backend/app/schemas/notification.py
from pydantic import BaseModel
from datetime import datetime


class NotificationOut(BaseModel):
    id: str
    user_id: str
    title: str
    message: str | None = None
    notification_type: str
    reference_type: str | None = None
    reference_id: str | None = None
    is_read: bool = False
    created_at: datetime | None = None

    class Config:
        from_attributes = True


class UnreadCountOut(BaseModel):
    count: int
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/schemas/notification.py
git commit -m "feat: add Notification schemas"
```

### Task 2.3: Create Notification API endpoints

**Files:**
- Create: `backend/app/api/notifications.py`

- [ ] **Step 1: Create the API**

```python
# backend/app/api/notifications.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update as sa_update
from app.database import get_db
from app.models.notification import Notification
from app.models.auth import User
from app.schemas.notification import NotificationOut, UnreadCountOut
from app.core.deps import get_current_user
from app.core.permissions import require_permission

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("", response_model=dict)
async def list_notifications(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("read")),
):
    """List notifications for the current user."""
    query = (
        select(Notification)
        .where(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(query)
    items = result.scalars().all()

    count_result = await db.execute(
        select(func.count(Notification.id)).where(Notification.user_id == current_user.id)
    )
    total = count_result.scalar() or 0

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [NotificationOut.model_validate(n).model_dump() for n in items],
    }


@router.get("/unread-count", response_model=UnreadCountOut)
async def get_unread_count(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get the count of unread notifications for the current user."""
    result = await db.execute(
        select(func.count(Notification.id)).where(
            Notification.user_id == current_user.id,
            Notification.is_read == False,
        )
    )
    return UnreadCountOut(count=result.scalar() or 0)


@router.put("/{notification_id}/read", response_model=NotificationOut)
async def mark_as_read(
    notification_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("edit")),
):
    """Mark a single notification as read."""
    result = await db.execute(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == current_user.id,
        )
    )
    notification = result.scalar_one_or_none()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    notification.is_read = True
    await db.commit()
    await db.refresh(notification)
    return notification


@router.put("/read-all", status_code=200)
async def mark_all_as_read(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("edit")),
):
    """Mark all notifications as read."""
    await db.execute(
        sa_update(Notification)
        .where(Notification.user_id == current_user.id, Notification.is_read == False)
        .values(is_read=True)
    )
    await db.commit()
    return {"message": "All notifications marked as read"}
```

- [ ] **Step 2: Register router in main.py**

Add `from app.api import ... notifications` and `app.include_router(notifications.router)`.

- [ ] **Step 3: Commit**

```bash
git add backend/app/api/notifications.py backend/app/main.py
git commit -m "feat: add notification API endpoints"
```

### Task 2.4: Create notification service helper

**Files:**
- Create: `backend/app/services/notification_service.py`

- [ ] **Step 1: Create the service**

```python
# backend/app/services/notification_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.notification import Notification


async def create_notification(
    db: AsyncSession,
    user_id: str,
    title: str,
    message: str | None = None,
    notification_type: str = "system",
    reference_type: str | None = None,
    reference_id: str | None = None,
) -> Notification:
    """Create a notification for a user."""
    notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        notification_type=notification_type,
        reference_type=reference_type,
        reference_id=reference_id,
    )
    db.add(notification)
    await db.commit()
    await db.refresh(notification)
    return notification
```

- [ ] **Step 2: Wire system notifications into territory assignment**

In `backend/app/api/territories.py`, add imports:
```python
from app.services.notification_service import create_notification
```

After adding a territory member:
```python
# After adding member successfully
user_result = await db.execute(select(User).where(User.id == payload.user_id))
added_user = user_result.scalar_one_or_none()
if added_user:
    territory = await db.get(Territory, territory_id)
    await create_notification(
        db,
        user_id=payload.user_id,
        title="区域分配",
        message=f"您已被分配到区域「{territory.name}」",
        reference_type="territory",
        reference_id=territory_id,
    )
```

- [ ] **Step 3: Wire workflow notifications**

In `backend/app/services/workflow_service.py`, update the `send_notification` action:
```python
elif action.action_type == "send_notification":
    message = config.get("message", "Notification triggered")
    target_user_id = config.get("user_id")
    if target_user_id:
        from app.services.notification_service import create_notification
        await create_notification(
            db,
            user_id=target_user_id,
            title=config.get("title", "工作流通知"),
            message=message,
            notification_type="workflow",
            reference_type=object_type,
            reference_id=str(record.get("id", "")),
        )
    results.append(f"Notification: {message}")
```

- [ ] **Step 4: Commit**

```bash
git add backend/app/services/notification_service.py backend/app/api/territories.py backend/app/services/workflow_service.py
git commit -m "feat: add notification service and wire into territories and workflows"
```

### Task 2.5: Create frontend notification types and API client

**Files:**
- Create: `frontend/src/types/notification.ts`
- Create: `frontend/src/api/notifications.ts`

- [ ] **Step 1: Create types**

```typescript
// frontend/src/types/notification.ts
export interface Notification {
  id: string
  user_id: string
  title: string
  message: string | null
  notification_type: 'workflow' | 'system'
  reference_type: string | null
  reference_id: string | null
  is_read: boolean
  created_at: string | null
}

export interface NotificationListResponse {
  total: number
  page: number
  page_size: number
  items: Notification[]
}

export interface UnreadCountResponse {
  count: number
}
```

- [ ] **Step 2: Create API client**

```typescript
// frontend/src/api/notifications.ts
import apiClient from './client'
import type { Notification, NotificationListResponse, UnreadCountResponse } from '../types/notification'

export const notificationsApi = {
  list(page = 1, pageSize = 20) {
    return apiClient.get<NotificationListResponse>('/notifications', { params: { page, page_size: pageSize } })
  },
  unreadCount() {
    return apiClient.get<UnreadCountResponse>('/notifications/unread-count')
  },
  markRead(id: string) {
    return apiClient.put<Notification>(`/notifications/${id}/read`)
  },
  markAllRead() {
    return apiClient.put('/notifications/read-all')
  },
}
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/types/notification.ts frontend/src/api/notifications.ts
git commit -m "feat: add frontend notification types and API client"
```

### Task 2.6: Create useNotifications composable

**Files:**
- Create: `frontend/src/composables/useNotifications.ts`

- [ ] **Step 1: Create the composable**

```typescript
// frontend/src/composables/useNotifications.ts
import { ref, onMounted, onUnmounted } from 'vue'
import { notificationsApi } from '../api/notifications'
import type { Notification } from '../types/notification'

export function useNotifications() {
  const unreadCount = ref(0)
  const recentNotifications = ref<Notification[]>([])
  let pollTimer: number | null = null

  async function fetchUnreadCount() {
    try {
      const { data } = await notificationsApi.unreadCount()
      unreadCount.value = data.count
    } catch {
      // silent
    }
  }

  async function fetchRecent() {
    try {
      const { data } = await notificationsApi.list(1, 10)
      recentNotifications.value = data.items
    } catch {
      // silent
    }
  }

  async function markAsRead(id: string) {
    try {
      await notificationsApi.markRead(id)
      await fetchUnreadCount()
      await fetchRecent()
    } catch {
      // silent
    }
  }

  async function markAllRead() {
    try {
      await notificationsApi.markAllRead()
      unreadCount.value = 0
      recentNotifications.value = recentNotifications.value.map(n => ({ ...n, is_read: true }))
    } catch {
      // silent
    }
  }

  function startPolling() {
    fetchUnreadCount()
    pollTimer = window.setInterval(fetchUnreadCount, 30000)
  }

  function stopPolling() {
    if (pollTimer !== null) {
      clearInterval(pollTimer)
      pollTimer = null
    }
  }

  onMounted(startPolling)
  onUnmounted(stopPolling)

  return {
    unreadCount,
    recentNotifications,
    fetchUnreadCount,
    fetchRecent,
    markAsRead,
    markAllRead,
  }
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/composables/useNotifications.ts
git commit -m "feat: add useNotifications composable with polling"
```

### Task 2.7: Create NotificationBell and NotificationDropdown components

**Files:**
- Create: `frontend/src/components/notification/NotificationBell.vue`
- Create: `frontend/src/components/notification/NotificationDropdown.vue`

- [ ] **Step 1: Create NotificationBell.vue**

```vue
<!-- frontend/src/components/notification/NotificationBell.vue -->
<template>
  <el-popover
    placement="bottom-end"
    :width="360"
    trigger="click"
    :popper-style="{ padding: '0' }"
    @show="handleShow"
  >
    <template #reference>
      <el-badge :value="unreadCount" :hidden="unreadCount === 0" :max="99" class="notif-badge">
        <el-button size="small" circle class="notif-button">
          <el-icon :size="18"><bell /></el-icon>
        </el-button>
      </el-badge>
    </template>
    <NotificationDropdown />
  </el-popover>
</template>

<script setup lang="ts">
import { Bell } from '@element-plus/icons-vue'
import { useNotifications } from '../../composables/useNotifications'
import NotificationDropdown from './NotificationDropdown.vue'

const { unreadCount, fetchRecent } = useNotifications()

function handleShow() {
  fetchRecent()
}
</script>

<style scoped>
.notif-badge { line-height: 1; }
.notif-button { border: none; background: transparent; }
.notif-button:hover { background: #f4f6f9; }
</style>
```

- [ ] **Step 2: Create NotificationDropdown.vue**

```vue
<!-- frontend/src/components/notification/NotificationDropdown.vue -->
<template>
  <div class="notif-dropdown">
    <div class="notif-header">
      <span class="notif-title">通知</span>
      <el-button v-if="hasUnread" text size="small" @click="handleMarkAllRead">
        全部标记已读
      </el-button>
    </div>
    <div class="notif-list" v-loading="loading">
      <div v-if="items.length === 0" class="notif-empty">暂无通知</div>
      <div
        v-for="item in items"
        :key="item.id"
        class="notif-item"
        :class="{ 'notif-unread': !item.is_read }"
        @click="handleClick(item)"
      >
        <div class="notif-item-dot" v-if="!item.is_read" />
        <div class="notif-item-content">
          <div class="notif-item-title">{{ item.title }}</div>
          <div class="notif-item-message" v-if="item.message">{{ item.message }}</div>
          <div class="notif-item-time">{{ formatTime(item.created_at) }}</div>
        </div>
        <el-tag v-if="item.notification_type === 'workflow'" size="small" type="warning">工作流</el-tag>
      </div>
    </div>
    <div class="notif-footer">
      <router-link to="/admin/notifications" class="notif-footer-link">查看全部通知</router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useNotifications } from '../../composables/useNotifications'

const router = useRouter()
const { recentNotifications: items, markAsRead, markAllRead } = useNotifications()

const loading = computed(() => false)
const hasUnread = computed(() => items.value.some(n => !n.is_read))

function formatTime(dateStr: string | null): string {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - d.getTime()
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  return d.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}

async function handleClick(item: any) {
  if (!item.is_read) {
    await markAsRead(item.id)
  }
  if (item.reference_type && item.reference_id) {
    const routes: Record<string, string> = {
      account: `/accounts/${item.reference_id}`,
      contact: `/contacts/${item.reference_id}`,
      opportunity: `/opportunities/${item.reference_id}`,
      territory: `/admin/territories`,
    }
    const path = routes[item.reference_type]
    if (path) router.push(path)
  }
}

function handleMarkAllRead() {
  markAllRead()
}
</script>

<style scoped>
.notif-dropdown { font-size: 13px; }
.notif-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 10px 14px; border-bottom: 1px solid #ebeef5;
}
.notif-title { font-weight: 600; color: #333; }
.notif-list { max-height: 360px; overflow-y: auto; }
.notif-empty { padding: 30px; text-align: center; color: #909399; }
.notif-item {
  display: flex; align-items: flex-start; gap: 8px;
  padding: 10px 14px; cursor: pointer; transition: background 0.1s;
  border-bottom: 1px solid #f2f2f2;
}
.notif-item:hover { background: #f5f7fa; }
.notif-unread { background: #f0f7ff; }
.notif-item-dot {
  width: 8px; height: 8px; border-radius: 50%;
  background: #1589ee; flex-shrink: 0; margin-top: 5px;
}
.notif-item-content { flex: 1; min-width: 0; }
.notif-item-title { font-weight: 500; color: #333; margin-bottom: 2px; }
.notif-item-message { font-size: 12px; color: #909399; margin-bottom: 2px; }
.notif-item-time { font-size: 11px; color: #c0c4cc; }
.notif-footer {
  padding: 8px 14px; text-align: center; border-top: 1px solid #ebeef5;
}
.notif-footer-link { color: #1589ee; text-decoration: none; font-size: 12px; }
</style>
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/notification/NotificationBell.vue frontend/src/components/notification/NotificationDropdown.vue
git commit -m "feat: add NotificationBell and NotificationDropdown components"
```

### Task 2.8: Integrate NotificationBell into Header

**Files:**
- Modify: `frontend/src/components/layout/Header.vue`

- [ ] **Step 1: Add NotificationBell to Header.vue**

In the template, add the bell before the user dropdown:
```vue
<!-- After the +新建 button and settings button, before user dropdown -->
<NotificationBell />
```

In the script:
```typescript
// Add import
import NotificationBell from '../notification/NotificationBell.vue'
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/components/layout/Header.vue
git commit -m "feat: integrate NotificationBell into header"
```

### Task 2.9: Create NotificationList page and route

**Files:**
- Create: `frontend/src/views/admin/NotificationList.vue`
- Modify: `frontend/src/router/index.ts`

- [ ] **Step 1: Create the notification list page**

```vue
<!-- frontend/src/views/admin/NotificationList.vue -->
<template>
  <div class="notification-list" v-loading="loading">
    <div class="nl-header">
      <h3 class="nl-title">通知列表</h3>
      <el-button v-if="hasUnread" size="small" @click="handleMarkAllRead">全部标记已读</el-button>
    </div>

    <el-table :data="notifications" border style="width:100%" @row-click="handleRowClick">
      <el-table-column label="状态" width="60" align="center">
        <template #default="{ row }">
          <el-icon v-if="!row.is_read" color="#1589ee" size="12"><circle-check /></el-icon>
        </template>
      </el-table-column>
      <el-table-column label="类型" width="80" align="center">
        <template #default="{ row }">
          <el-tag v-if="row.notification_type === 'workflow'" size="small" type="warning">工作流</el-tag>
          <el-tag v-else size="small" type="info">系统</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="标题" prop="title" min-width="200" />
      <el-table-column label="内容" prop="message" min-width="250" show-overflow-tooltip />
      <el-table-column label="时间" width="160">
        <template #default="{ row }">
          {{ row.created_at ? new Date(row.created_at).toLocaleString('zh-CN') : '-' }}
        </template>
      </el-table-column>
    </el-table>

    <div class="nl-pagination" v-if="total > pageSize">
      <el-pagination
        v-model:current-page="page"
        :page-size="pageSize"
        :total="total"
        layout="prev, pager, next"
        @current-change="loadNotifications"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { CircleCheck } from '@element-plus/icons-vue'
import { notificationsApi } from '../../api/notifications'
import { useNotifications } from '../../composables/useNotifications'
import type { Notification } from '../../types/notification'

const router = useRouter()
const { markAsRead, markAllRead, unreadCount } = useNotifications()
const notifications = ref<Notification[]>([])
const loading = ref(false)
const page = ref(1)
const pageSize = 20
const total = ref(0)
const hasUnread = computed(() => unreadCount.value > 0)

async function loadNotifications() {
  loading.value = true
  try {
    const { data } = await notificationsApi.list(page.value, pageSize)
    notifications.value = data.items
    total.value = data.total
  } catch {
    // silent
  } finally {
    loading.value = false
  }
}

async function handleRowClick(row: Notification) {
  if (!row.is_read) {
    await markAsRead(row.id)
    row.is_read = true
  }
  if (row.reference_type && row.reference_id) {
    const routes: Record<string, string> = {
      account: `/accounts/${row.reference_id}`,
      contact: `/contacts/${row.reference_id}`,
      opportunity: `/opportunities/${row.reference_id}`,
      territory: `/admin/territories`,
    }
    const path = routes[row.reference_type]
    if (path) router.push(path)
  }
}

function handleMarkAllRead() {
  markAllRead()
  notifications.value.forEach(n => { n.is_read = true })
}

onMounted(loadNotifications)
</script>

<style scoped>
.notification-list { padding: 16px; }
.nl-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 16px;
}
.nl-title { margin: 0; font-size: 16px; color: #333; }
.nl-pagination { margin-top: 16px; text-align: center; }
</style>
```

- [ ] **Step 2: Add route**

In `frontend/src/router/index.ts`, add route:
```typescript
{
  path: 'admin/notifications',
  name: 'NotificationList',
  component: () => import('../views/admin/NotificationList.vue'),
},
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/views/admin/NotificationList.vue frontend/src/router/index.ts
git commit -m "feat: add notification list page and route"
```

### Task 2.10: Phase 2 tests

- [ ] **Step 1: Write notification tests**

```python
# TEST/Unittest/test_notifications.py
import pytest
from app.models.notification import Notification


@pytest.mark.asyncio
async def test_create_notification(db_session):
    from app.services.notification_service import create_notification
    notif = await create_notification(
        db_session,
        user_id="test_user",
        title="Test Notification",
        message="This is a test",
        notification_type="system",
    )
    assert notif.id is not None
    assert notif.title == "Test Notification"
    assert notif.is_read is False


@pytest.mark.asyncio
async def test_unread_count(db_session):
    from app.services.notification_service import create_notification
    await create_notification(db_session, user_id="user_a", title="N1")
    await create_notification(db_session, user_id="user_a", title="N2")
    await create_notification(db_session, user_id="user_b", title="N3")

    # Mark one as read
    result = await db_session.execute(
        __import__("sqlalchemy").select(Notification).where(Notification.user_id == "user_a")
    )
    notifs = result.scalars().all()
    notifs[0].is_read = True
    await db_session.commit()

    # Check unread count for user_a
    from sqlalchemy import select, func
    result = await db_session.execute(
        select(func.count(Notification.id)).where(
            Notification.user_id == "user_a",
            Notification.is_read == False,
        )
    )
    assert result.scalar() == 1
```

Run: `cd backend && python -m pytest TEST/Unittest/test_notifications.py -v`
Expected: PASS

- [ ] **Step 2: Run all tests**

Run: `cd backend && python -m pytest TEST/Unittest/ -v`
Expected: All pass

- [ ] **Step 3: Commit**

```bash
git add TEST/Unittest/test_notifications.py
git commit -m "test: add notification unit tests"
```

---

## Phase 3: Global Search

### Task 3.1: Create search service with FTS5 setup

**Files:**
- Create: `backend/app/services/search_service.py`

- [ ] **Step 1: Create the search service**

```python
# backend/app/services/search_service.py
"""
Search service using SQLite FTS5 for full-text search across all objects.
"""
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, AsyncConnection


FTS5_TABLE = "search_idx"

# SQL to create the FTS5 virtual table
CREATE_FTS5_SQL = f"""
CREATE VIRTUAL TABLE IF NOT EXISTS {FTS5_TABLE} USING fts5(
    object_type, object_id, name, content,
    tokenize='unicode61'
);
"""

# Triggers for core objects
TRIGGERS = {
    "accounts": {
        "table": "accounts",
        "object_type": "account",
        "name_col": "name",
        "content_cols": "name || ' ' || COALESCE(industry, '') || ' ' || COALESCE(email, '')",
        "id_col": "id",
    },
    "contacts": {
        "table": "contacts",
        "object_type": "contact",
        "name_col": "first_name || ' ' || last_name",
        "content_cols": "first_name || ' ' || last_name || ' ' || COALESCE(email, '')",
        "id_col": "id",
    },
    "opportunities": {
        "table": "opportunities",
        "object_type": "opportunity",
        "name_col": "name",
        "content_cols": "name || ' ' || COALESCE(description, '')",
        "id_col": "id",
    },
    "products": {
        "table": "products",
        "object_type": "product",
        "name_col": "name",
        "content_cols": "name || ' ' || COALESCE(product_code, '') || ' ' || COALESCE(description, '')",
        "id_col": "id",
    },
    "events": {
        "table": "events",
        "object_type": "event",
        "name_col": "subject",
        "content_cols": "subject || ' ' || COALESCE(purpose, '')",
        "id_col": "id",
    },
}


async def setup_fts5(conn: AsyncConnection):
    """Create the FTS5 table and triggers."""
    await conn.execute(text(CREATE_FTS5_SQL))

    for key, cfg in TRIGGERS.items():
        # Insert trigger
        await conn.execute(text(f"""
            CREATE TRIGGER IF NOT EXISTS trg_{key}_fts_insert AFTER INSERT ON {cfg['table']}
            BEGIN
                INSERT INTO {FTS5_TABLE} (object_type, object_id, name, content)
                VALUES ('{cfg['object_type']}', NEW.{cfg['id_col']}, {cfg['name_col']}, {cfg['content_cols']});
            END;
        """))
        # Update trigger
        await conn.execute(text(f"""
            CREATE TRIGGER IF NOT EXISTS trg_{key}_fts_update AFTER UPDATE ON {cfg['table']}
            BEGIN
                UPDATE {FTS5_TABLE} SET
                    name = {cfg['name_col']},
                    content = {cfg['content_cols']}
                WHERE object_id = NEW.{cfg['id_col']} AND object_type = '{cfg['object_type']}';
            END;
        """))
        # Delete trigger
        await conn.execute(text(f"""
            CREATE TRIGGER IF NOT EXISTS trg_{key}_fts_delete AFTER DELETE ON {cfg['table']}
            BEGIN
                DELETE FROM {FTS5_TABLE} WHERE object_id = OLD.{cfg['id_col']} AND object_type = '{cfg['object_type']};
            END;
        """))


async def search_all(db: AsyncSession, query: str, limit: int = 5) -> dict:
    """Search across all indexed objects and return grouped results."""
    if not query or len(query.strip()) < 1:
        return {}

    search_term = query.strip()
    results = {
        "accounts": [],
        "contacts": [],
        "opportunities": [],
        "products": [],
        "events": [],
        "custom_objects": {},
    }

    # Search using FTS5
    fts_query = f"\"{search_term}\" OR {search_term}*"
    sql = text(f"""
        SELECT object_type, object_id, name, content
        FROM {FTS5_TABLE}
        WHERE {FTS5_TABLE} MATCH :q
        ORDER BY rank
        LIMIT :lim
    """)
    try:
        result = await db.execute(sql, {"q": fts_query, "lim": limit * 10})
        rows = result.fetchall()
    except Exception:
        # Fallback to LIKE search if FTS5 fails
        return await _search_like_fallback(db, search_term, limit)

    # Group by object_type
    for row in rows:
        obj_type = row[0]
        obj_id = row[1]
        name = row[2]

        if obj_type == "account" and len(results["accounts"]) < limit:
            results["accounts"].append({"id": obj_id, "name": name})
        elif obj_type == "contact" and len(results["contacts"]) < limit:
            results["contacts"].append({"id": obj_id, "name": name})
        elif obj_type == "opportunity" and len(results["opportunities"]) < limit:
            results["opportunities"].append({"id": obj_id, "name": name})
        elif obj_type == "product" and len(results["products"]) < limit:
            results["products"].append({"id": obj_id, "name": name})
        elif obj_type == "event" and len(results["events"]) < limit:
            results["events"].append({"id": obj_id, "name": name})

    return results


async def _search_like_fallback(db: AsyncSession, query: str, limit: int) -> dict:
    """Fallback to LIKE search for all objects."""
    from sqlalchemy import select, or_
    from app.models.crm import Account, Contact, Opportunity, Product
    from app.models.event import Event

    results = {"accounts": [], "contacts": [], "opportunities": [], "products": [], "events": [], "custom_objects": {}}
    q = f"%{query}%"

    # Accounts
    result = await db.execute(select(Account).where(Account.name.ilike(q)).limit(limit))
    for a in result.scalars().all():
        results["accounts"].append({"id": a.id, "name": a.name})

    # Contacts
    result = await db.execute(
        select(Contact).where(or_(Contact.first_name.ilike(q), Contact.last_name.ilike(q), Contact.email.ilike(q))).limit(limit)
    )
    for c in result.scalars().all():
        results["contacts"].append({"id": c.id, "name": f"{c.first_name} {c.last_name}"})

    # Opportunities
    result = await db.execute(select(Opportunity).where(Opportunity.name.ilike(q)).limit(limit))
    for o in result.scalars().all():
        results["opportunities"].append({"id": o.id, "name": o.name})

    # Products
    result = await db.execute(select(Product).where(Product.name.ilike(q)).limit(limit))
    for p in result.scalars().all():
        results["products"].append({"id": p.id, "name": p.name})

    # Events
    result = await db.execute(select(Event).where(Event.subject.ilike(q)).limit(limit))
    for e in result.scalars().all():
        results["events"].append({"id": e.id, "name": e.subject})

    return results
```

- [ ] **Step 2: Update database.py to create FTS5 table**

In `init_db()`, after table creation:
```python
from app.services.search_service import setup_fts5

async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)
    await setup_fts5(conn)

# ... seed_default_profiles, attach_listeners, etc.
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/services/search_service.py backend/app/database.py
git commit -m "feat: add FTS5 search service with triggers"
```

### Task 3.2: Create search API endpoint

**Files:**
- Create: `backend/app/api/search.py`

- [ ] **Step 1: Create the search endpoint**

```python
# backend/app/api/search.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.auth import User
from app.core.deps import get_current_user
from app.core.permissions import require_permission
from app.services.search_service import search_all

router = APIRouter(prefix="/api/search", tags=["search"])


@router.get("")
async def search(
    q: str = Query("", min_length=1, max_length=255),
    limit: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("read")),
):
    """Unified search across all objects."""
    return await search_all(db, q, limit)
```

- [ ] **Step 2: Register router in main.py**

Add `from app.api import ... search` and `app.include_router(search.router)`.

- [ ] **Step 3: Commit**

```bash
git add backend/app/api/search.py backend/app/main.py
git commit -m "feat: add global search API endpoint"
```

### Task 3.3: Create frontend search types and API client

**Files:**
- Create: `frontend/src/types/search.ts`
- Create: `frontend/src/api/search.ts`

- [ ] **Step 1: Create types**

```typescript
// frontend/src/types/search.ts
export interface SearchResult {
  id: string
  name: string
}

export interface SearchResults {
  accounts: SearchResult[]
  contacts: SearchResult[]
  opportunities: SearchResult[]
  products: SearchResult[]
  events: SearchResult[]
  custom_objects: Record<string, SearchResult[]>
}
```

- [ ] **Step 2: Create API client**

```typescript
// frontend/src/api/search.ts
import apiClient from './client'
import type { SearchResults } from '../types/search'

export const searchApi = {
  search(q: string, limit = 5) {
    return apiClient.get<SearchResults>('/search', { params: { q, limit } })
  },
}
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/types/search.ts frontend/src/api/search.ts
git commit -m "feat: add frontend search types and API client"
```

### Task 3.4: Create GlobalSearch component

**Files:**
- Create: `frontend/src/components/search/GlobalSearch.vue`

- [ ] **Step 1: Create the component**

```vue
<!-- frontend/src/components/search/GlobalSearch.vue -->
<template>
  <div class="global-search" ref="searchRef">
    <el-input
      v-model="query"
      placeholder="搜索账户、联系人、商机..."
      size="small"
      clearable
      :prefix-icon="SearchIcon"
      @input="handleInput"
      @keyup.enter="handleEnter"
      @focus="showPanel = true"
      @keydown.escape="showPanel = false"
    />

    <Transition name="search-fade">
      <div v-if="showPanel && query.length > 0" class="search-panel">
        <div v-if="loading" class="search-loading">
          <el-icon class="is-loading" :size="20"><loading /></el-icon>
        </div>
        <template v-else>
          <div v-if="hasResults" class="search-results">
            <div v-for="(items, type) in groupedResults" :key="type">
              <div v-if="items.length > 0" class="search-group">
                <div class="search-group-label">{{ groupLabel(type) }}</div>
                <div
                  v-for="item in items"
                  :key="item.id"
                  class="search-item"
                  @click="navigateTo(type, item.id)"
                >
                  <el-icon :size="14" class="search-item-icon">
                    <component :is="iconFor(type)" />
                  </el-icon>
                  <span class="search-item-name">{{ item.name }}</span>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="search-no-results">未找到相关结果</div>
        </template>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { Search as SearchIcon, Loading } from '@element-plus/icons-vue'
import { OfficeBuilding, User, TrendCharts, Box, Phone } from '@element-plus/icons-vue'
import { searchApi } from '../../api/search'
import type { SearchResults } from '../../types/search'

const router = useRouter()
const query = ref('')
const loading = ref(false)
const showPanel = ref(false)
const results = ref<SearchResults>({ accounts: [], contacts: [], opportunities: [], products: [], events: [], custom_objects: {} })
const searchRef = ref<HTMLElement | null>(null)
let debounceTimer: number | null = null

const ICONS: Record<string, any> = {
  accounts: OfficeBuilding,
  contacts: User,
  opportunities: TrendCharts,
  products: Box,
  events: Phone,
}

const GROUP_LABELS: Record<string, string> = {
  accounts: '账户',
  contacts: '联系人',
  opportunities: '销售机会',
  products: '产品',
  events: '拜访',
}

const groupedResults = computed(() => results.value)

const hasResults = computed(() => {
  for (const key of Object.keys(results.value)) {
    if (key === 'custom_objects') {
      for (const val of Object.values((results.value as any).custom_objects)) {
        if (Array.isArray(val) && val.length > 0) return true
      }
    } else {
      if ((results.value as any)[key]?.length > 0) return true
    }
  }
  return false
})

function iconFor(type: string): any {
  return ICONS[type] || OfficeBuilding
}

function groupLabel(type: string): string {
  return GROUP_LABELS[type] || type
}

function handleInput() {
  if (debounceTimer) clearTimeout(debounceTimer)
  if (!query.value.trim()) {
    showPanel.value = false
    return
  }
  debounceTimer = window.setTimeout(doSearch, 300)
}

async function doSearch() {
  const q = query.value.trim()
  if (!q) return
  loading.value = true
  try {
    const { data } = await searchApi.search(q)
    results.value = data
  } catch {
    // silent
  } finally {
    loading.value = false
  }
}

function handleEnter() {
  if (query.value.trim()) {
    showPanel.value = false
    router.push(`/accounts?search=${encodeURIComponent(query.value.trim())}`)
  }
}

function navigateTo(type: string, id: string) {
  showPanel.value = false
  query.value = ''
  const routes: Record<string, string> = {
    accounts: `/accounts/${id}`,
    contacts: `/contacts/${id}`,
    opportunities: `/opportunities/${id}`,
    products: `/products/${id}`,
    events: `/events/${id}`,
  }
  const path = routes[type]
  if (path) router.push(path)
}

// Keyboard shortcut: Ctrl+K
function handleKeydown(e: KeyboardEvent) {
  if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
    e.preventDefault()
    const input = searchRef.value?.querySelector('input')
    input?.focus()
  }
}

// Click outside to close
function handleClickOutside(e: MouseEvent) {
  if (searchRef.value && !searchRef.value.contains(e.target as Node)) {
    showPanel.value = false
  }
}

onMounted(() => {
  document.addEventListener('keydown', handleKeydown)
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.global-search { position: relative; width: 100%; }
.search-panel {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  margin-top: 4px;
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  z-index: 2000;
  max-height: 400px;
  overflow-y: auto;
}
.search-loading { padding: 20px; text-align: center; }
.search-no-results { padding: 30px; text-align: center; color: #909399; }
.search-group { padding: 4px 0; }
.search-group-label {
  font-size: 11px; font-weight: 700; color: #909399;
  text-transform: uppercase; padding: 4px 12px; letter-spacing: 0.5px;
}
.search-item {
  display: flex; align-items: center; gap: 8px;
  padding: 6px 12px; cursor: pointer; font-size: 13px;
  transition: background 0.1s;
}
.search-item:hover { background: #f0f7ff; }
.search-item-icon { color: #706e6b; flex-shrink: 0; }
.search-item-name { color: #333; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.search-fade-enter-active, .search-fade-leave-active { transition: opacity 0.15s; }
.search-fade-enter-from, .search-fade-leave-to { opacity: 0; }
</style>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/components/search/GlobalSearch.vue
git commit -m "feat: add GlobalSearch component with dropdown panel"
```

### Task 3.5: Integrate GlobalSearch into Header

**Files:**
- Modify: `frontend/src/components/layout/Header.vue`

- [ ] **Step 1: Replace the old search input**

In the template, replace the existing `.sf-header-center` section:
```vue
<!-- Center: Global Search -->
<div class="sf-header-center">
  <GlobalSearch />
</div>
```

In the script:
```typescript
// Remove: searchQuery, handleSearch
// Add import:
import GlobalSearch from '../search/GlobalSearch.vue'
```

Remove the old `searchQuery`, `handleSearch`, and the `Search as SearchIcon` import (since GlobalSearch handles it internally).

- [ ] **Step 2: Commit**

```bash
git add frontend/src/components/layout/Header.vue
git commit -m "feat: integrate GlobalSearch into header"
```

### Task 3.6: Phase 3 tests

- [ ] **Step 1: Write search tests**

```python
# TEST/Unittest/test_search.py
import pytest
from app.models.crm import Account


@pytest.mark.asyncio
async def test_search_like_fallback(db_session):
    """Test the LIKE search fallback works."""
    from app.services.search_service import _search_like_fallback

    # Create a test account
    account = Account(name="SearchTest Corp", industry="Tech")
    db_session.add(account)
    await db_session.commit()

    # Search for it
    results = await _search_like_fallback(db_session, "SearchTest", 5)
    assert len(results["accounts"]) >= 1
    assert results["accounts"][0]["name"] == "SearchTest Corp"
```

Run: `cd backend && python -m pytest TEST/Unittest/test_search.py -v`
Expected: PASS

- [ ] **Step 2: Run all tests**

Run: `cd backend && python -m pytest TEST/Unittest/ -v`
Expected: All pass

- [ ] **Step 3: Commit**

```bash
git add TEST/Unittest/test_search.py
git commit -m "test: add search unit tests"
```

---

## Phase 4: Import / Export

### Task 4.1: Create ImportJob model

**Files:**
- Create: `backend/app/models/import_job.py`

- [ ] **Step 1: Create the model**

```python
# backend/app/models/import_job.py
from sqlalchemy import Column, String, Integer, DateTime, func
from app.database import Base
from app.utils.id_gen import generate_id


class ImportJob(Base):
    __tablename__ = "import_jobs"

    id = Column(String(36), primary_key=True, default=lambda: generate_id("imp_"))
    object_type = Column(String(80), nullable=False)
    filename = Column(String(255), nullable=False)
    total_rows = Column(Integer, default=0)
    success_rows = Column(Integer, default=0)
    error_rows = Column(Integer, default=0)
    errors = Column(String, nullable=True)
    status = Column(String(20), default="pending")  # pending | processing | completed | failed
    created_by = Column(String(36), nullable=False)
    created_at = Column(DateTime, default=func.now())
```

- [ ] **Step 2: Update database.py**

Add `from app.models.import_job import ImportJob  # noqa: F401` to `init_db()`.

- [ ] **Step 3: Commit**

```bash
git add backend/app/models/import_job.py backend/app/database.py
git commit -m "feat: add ImportJob model"
```

### Task 4.2: Create import/export schemas

**Files:**
- Create: `backend/app/schemas/import_export.py`

- [ ] **Step 1: Create schemas**

```python
# backend/app/schemas/import_export.py
from pydantic import BaseModel
from datetime import datetime


class ImportPreviewResponse(BaseModel):
    preview_id: str
    columns: list[str]
    mapping_suggestions: dict[str, str | None]
    available_fields: list[dict]
    preview_rows: list[list[str]]


class ImportConfirmRequest(BaseModel):
    preview_id: str
    mapping: dict[str, str]  # CSV column -> field name


class ImportResultResponse(BaseModel):
    success_rows: int
    error_rows: int
    errors: list[dict] = []


class ImportJobOut(BaseModel):
    id: str
    object_type: str
    filename: str
    total_rows: int
    success_rows: int
    error_rows: int
    errors: str | None = None
    status: str
    created_by: str
    created_at: datetime | None = None

    class Config:
        from_attributes = True
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/schemas/import_export.py
git commit -m "feat: add import/export schemas"
```

### Task 4.3: Create CSV service

**Files:**
- Create: `backend/app/services/csv_service.py`

- [ ] **Step 1: Create the CSV service**

```python
# backend/app/services/csv_service.py
"""
CSV parsing and field mapping service for import/export.
"""
import csv
import io
import json
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.crm import Account, Contact, Product, Opportunity


# Object field definitions: {api_name: {label, type, required}}
OBJECT_FIELDS = {
    "account": {
        "name": {"label": "名称", "type": "text", "required": True},
        "industry": {"label": "行业", "type": "text", "required": False},
        "phone": {"label": "电话", "type": "text", "required": False},
        "website": {"label": "网站", "type": "text", "required": False},
        "email": {"label": "邮箱", "type": "text", "required": False},
        "billing_street": {"label": "街道", "type": "text", "required": False},
        "billing_city": {"label": "城市", "type": "text", "required": False},
        "billing_state": {"label": "省份", "type": "text", "required": False},
        "billing_postal_code": {"label": "邮编", "type": "text", "required": False},
        "billing_country": {"label": "国家", "type": "text", "required": False},
        "description": {"label": "描述", "type": "text", "required": False},
    },
    "contact": {
        "first_name": {"label": "名", "type": "text", "required": True},
        "last_name": {"label": "姓", "type": "text", "required": True},
        "email": {"label": "邮箱", "type": "text", "required": False},
        "phone": {"label": "电话", "type": "text", "required": False},
        "mobile": {"label": "手机", "type": "text", "required": False},
        "title": {"label": "职位", "type": "text", "required": False},
        "department": {"label": "部门", "type": "text", "required": False},
    },
    "product": {
        "name": {"label": "产品名称", "type": "text", "required": True},
        "product_code": {"label": "产品编码", "type": "text", "required": False},
        "category": {"label": "分类", "type": "text", "required": False},
        "standard_price": {"label": "标准价格", "type": "number", "required": True},
        "cost": {"label": "成本", "type": "number", "required": False},
        "description": {"label": "描述", "type": "text", "required": False},
        "is_active": {"label": "是否启用", "type": "boolean", "required": False},
    },
    "opportunity": {
        "name": {"label": "机会名称", "type": "text", "required": True},
        "amount": {"label": "金额", "type": "number", "required": False},
        "close_date": {"label": "预计关闭日期", "type": "date", "required": False},
        "description": {"label": "描述", "type": "text", "required": False},
    },
}

# Model class mapping for import
IMPORT_MODELS = {
    "account": Account,
    "contact": Contact,
    "product": Product,
    "opportunity": Opportunity,
}

# Auto-mapping: common Chinese column names -> field names
AUTO_MAP = {
    "名称": "name", "姓名": "name", "账户名称": "name",
    "行业": "industry", "电话": "phone", "网站": "website",
    "邮箱": "email", "街道": "billing_street", "城市": "billing_city",
    "省份": "billing_state", "邮编": "billing_postal_code", "国家": "billing_country",
    "描述": "description", "名": "first_name", "姓": "last_name",
    "手机": "mobile", "职位": "title", "部门": "department",
    "产品名称": "name", "产品编码": "product_code", "分类": "category",
    "标准价格": "standard_price", "成本": "cost",
    "机会名称": "name", "金额": "amount", "预计关闭日期": "close_date",
    "是否启用": "is_active",
}

# Store preview data in memory (keyed by preview_id)
_preview_store: dict[str, dict] = {}


def parse_csv(content: bytes) -> tuple[list[str], list[list[str]]]:
    """Parse CSV content and return (headers, rows)."""
    text = content.decode("utf-8-sig")
    reader = csv.reader(io.StringIO(text))
    rows = list(reader)
    if not rows:
        raise ValueError("Empty CSV file")
    headers = [h.strip() for h in rows[0]]
    data_rows = [[cell.strip() for cell in row] for row in rows[1:] if any(cell.strip() for cell in row)]
    return headers, data_rows


def auto_map_fields(headers: list[str], object_type: str) -> dict[str, str | None]:
    """Auto-map CSV column headers to field names."""
    fields = OBJECT_FIELDS.get(object_type, {})
    mapping = {}
    for header in headers:
        # Try exact match
        if header in AUTO_MAP:
            field = AUTO_MAP[header]
            if field in fields:
                mapping[header] = field
                continue
        # Try label match
        for field_name, field_def in fields.items():
            if field_def["label"] == header:
                mapping[header] = field_name
                break
        else:
            mapping[header] = None
    return mapping


def create_preview(headers: list[str], rows: list[list[str]], object_type: str) -> dict:
    """Create a preview and store it for later confirmation."""
    mapping = auto_map_fields(headers, object_type)
    fields = OBJECT_FIELDS.get(object_type, {})
    available = [{"name": k, "label": v["label"], "type": v["type"], "required": v["required"]}
                 for k, v in fields.items()]

    preview_id = str(uuid.uuid4())[:8]
    _preview_store[preview_id] = {
        "object_type": object_type,
        "headers": headers,
        "rows": rows,
        "mapping": mapping,
    }

    return {
        "preview_id": preview_id,
        "columns": headers,
        "mapping_suggestions": mapping,
        "available_fields": available,
        "preview_rows": rows[:10],
    }


async def confirm_import(db: AsyncSession, preview_id: str, mapping: dict[str, str], user_id: str) -> dict:
    """Execute the import with confirmed field mapping."""
    preview = _preview_store.get(preview_id)
    if not preview:
        raise ValueError("Preview not found or expired")

    object_type = preview["object_type"]
    headers = preview["headers"]
    rows = preview["rows"]
    model_class = IMPORT_MODELS.get(object_type)
    if not model_class:
        raise ValueError(f"Unknown object type: {object_type}")

    fields = OBJECT_FIELDS.get(object_type, {})
    success_rows = 0
    error_rows = 0
    errors = []

    for row_idx, row in enumerate(rows):
        try:
            record_data = {}
            for col_idx, header in enumerate(headers):
                field_name = mapping.get(header)
                if field_name and col_idx < len(row):
                    value = row[col_idx].strip()
                    if value:
                        field_def = fields.get(field_name, {})
                        if field_def.get("type") == "number":
                            try:
                                value = float(value)
                            except ValueError:
                                pass
                        elif field_def.get("type") == "boolean":
                            value = value.lower() in ("true", "yes", "是", "1", "active")
                        record_data[field_name] = value

            # Check required fields
            missing = [f for f_name, f_def in fields.items()
                       if f_def.get("required") and f_name not in record_data]
            if missing:
                raise ValueError(f"Missing required fields: {', '.join(missing)}")

            record = model_class(**record_data)
            db.add(record)
            success_rows += 1
        except Exception as e:
            error_rows += 1
            errors.append({"row": row_idx + 2, "error": str(e)})

    if success_rows > 0:
        await db.commit()

    # Clean up preview
    _preview_store.pop(preview_id, None)

    return {
        "success_rows": success_rows,
        "error_rows": error_rows,
        "errors": errors,
    }


def generate_csv(object_type: str, records: list[dict]) -> str:
    """Generate CSV content from a list of record dicts."""
    fields = OBJECT_FIELDS.get(object_type, {})
    if not fields:
        fields = {k: {"label": k} for k in (records[0].keys() if records else [])}

    output = io.StringIO()
    writer = csv.writer(output)

    # Header row
    headers = [f["label"] for f in fields.values()]
    writer.writerow(headers)

    # Data rows
    for record in records:
        row = [str(record.get(f_name, "") or "") for f_name in fields.keys()]
        writer.writerow(row)

    return output.getvalue()
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/services/csv_service.py
git commit -m "feat: add CSV import/export service with field mapping"
```

### Task 4.4: Create import/export API endpoints

**Files:**
- Create: `backend/app/api/import_export.py`

- [ ] **Step 1: Create the API**

```python
# backend/app/api/import_export.py
import json
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.auth import User
from app.models.import_job import ImportJob
from app.models.crm import Account, Contact, Product, Opportunity
from app.schemas.import_export import (
    ImportPreviewResponse, ImportConfirmRequest, ImportResultResponse, ImportJobOut,
)
from app.core.deps import get_current_user
from app.core.permissions import require_permission
from app.services.csv_service import parse_csv, create_preview, confirm_import, generate_csv
from app.services.audit_service import current_user_id

router = APIRouter(prefix="/api/import", tags=["import"])

# Export models
EXPORT_MODELS = {
    "account": Account,
    "contact": Contact,
    "product": Product,
    "opportunity": Opportunity,
}

# ── Import ─────────────────────────────────────────────────────────────

@router.post("/upload", response_model=ImportPreviewResponse)
async def upload_csv(
    file: UploadFile = File(...),
    object_type: str = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("create")),
):
    """Upload a CSV file, parse it, and return preview data."""
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    content = await file.read()
    try:
        headers, rows = parse_csv(content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if object_type not in ("account", "contact", "product", "opportunity"):
        raise HTTPException(status_code=400, detail=f"Unsupported object type: {object_type}")

    return ImportPreviewResponse(**create_preview(headers, rows, object_type))


@router.post("/confirm", response_model=ImportResultResponse)
async def confirm_import_endpoint(
    payload: ImportConfirmRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("create")),
):
    """Confirm and execute the import."""
    token = current_user_id.set(current_user.id)
    try:
        result = await confirm_import(db, payload.preview_id, payload.mapping, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        current_user_id.reset(token)

    # Save import job record
    job = ImportJob(
        object_type="account",
        filename="import.csv",
        total_rows=result["success_rows"] + result["error_rows"],
        success_rows=result["success_rows"],
        error_rows=result["error_rows"],
        errors=json.dumps(result["errors"]) if result["errors"] else None,
        status="completed" if result["error_rows"] == 0 else "completed",
        created_by=current_user.id,
    )
    db.add(job)
    await db.commit()

    return ImportResultResponse(**result)


@router.get("/jobs", response_model=dict)
async def list_import_jobs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("read")),
):
    """List import history."""
    query = (
        select(ImportJob)
        .order_by(ImportJob.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(query)
    items = result.scalars().all()

    count_result = await db.execute(select(func.count(ImportJob.id)))
    total = count_result.scalar() or 0

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [ImportJobOut.model_validate(j).model_dump() for j in items],
    }


# ── Export ─────────────────────────────────────────────────────────────

@router.get("/export/{object_type}")
async def export_csv(
    object_type: str,
    q: str = Query("", max_length=255),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: User = Depends(require_permission("read")),
):
    """Export records as CSV."""
    model_class = EXPORT_MODELS.get(object_type)
    if not model_class:
        # Check if it's a custom object
        from app.models.custom_object import CustomObjectDef
        result = await db.execute(
            select(CustomObjectDef).where(CustomObjectDef.api_name == object_type)
        )
        obj_def = result.scalar_one_or_none()
        if obj_def:
            from app.services.custom_object_service import list_records
            records = await list_records(db, obj_def, page=1, page_size=10000)
            # Build CSV from dynamic records
            if records["items"]:
                csv_content = generate_csv(object_type, records["items"])
            else:
                csv_content = "No data"
            return PlainTextResponse(csv_content, media_type="text/csv",
                                     headers={"Content-Disposition": f"attachment; filename={object_type}.csv"})

        raise HTTPException(status_code=404, detail=f"Unknown object type: {object_type}")

    # Build query
    query = select(model_class)
    if q:
        if hasattr(model_class, "name"):
            query = query.where(model_class.name.ilike(f"%{q}%"))
    query = query.order_by(model_class.created_at.desc())

    result = await db.execute(query)
    records = result.scalars().all()

    csv_content = generate_csv(object_type, [vars(r) for r in records])
    return PlainTextResponse(csv_content, media_type="text/csv",
                             headers={"Content-Disposition": f"attachment; filename={object_type}.csv"})
```

- [ ] **Step 2: Register router in main.py**

Add `from app.api import ... import_export` and `app.include_router(import_export.router)`.

- [ ] **Step 3: Commit**

```bash
git add backend/app/api/import_export.py backend/app/main.py
git commit -m "feat: add import/export API endpoints"
```

### Task 4.5: Create frontend import types and API client

**Files:**
- Create: `frontend/src/types/importJob.ts`
- Create: `frontend/src/api/importExport.ts`

- [ ] **Step 1: Create types**

```typescript
// frontend/src/types/importJob.ts
export interface ImportPreview {
  preview_id: string
  columns: string[]
  mapping_suggestions: Record<string, string | null>
  available_fields: { name: string; label: string; type: string; required: boolean }[]
  preview_rows: string[][]
}

export interface ImportConfirmRequest {
  preview_id: string
  mapping: Record<string, string>
}

export interface ImportResult {
  success_rows: number
  error_rows: number
  errors: { row: number; error: string }[]
}

export interface ImportJob {
  id: string
  object_type: string
  filename: string
  total_rows: number
  success_rows: number
  error_rows: number
  errors: string | null
  status: string
  created_by: string
  created_at: string | null
}
```

- [ ] **Step 2: Create API client**

```typescript
// frontend/src/api/importExport.ts
import apiClient from './client'
import type { ImportPreview, ImportConfirmRequest, ImportResult, ImportJob } from '../types/importJob'

export const importExportApi = {
  upload(file: File, objectType: string) {
    const formData = new FormData()
    formData.append('file', file)
    return apiClient.post<ImportPreview>('/import/upload', formData, {
      params: { object_type: objectType },
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  confirm(data: ImportConfirmRequest) {
    return apiClient.post<ImportResult>('/import/confirm', data)
  },
  listJobs(page = 1) {
    return apiClient.get<{ total: number; page: number; page_size: number; items: ImportJob[] }>(
      '/import/jobs', { params: { page } }
    )
  },
  exportCsv(objectType: string, search = '') {
    return apiClient.get(`/import/export/${objectType}`, {
      params: { q: search },
      responseType: 'blob',
    })
  },
}
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/types/importJob.ts frontend/src/api/importExport.ts
git commit -m "feat: add frontend import types and API client"
```

### Task 4.6: Create ImportWizard component

**Files:**
- Create: `frontend/src/components/import/ImportWizard.vue`

- [ ] **Step 1: Create the import wizard dialog**

```vue
<!-- frontend/src/components/import/ImportWizard.vue -->
<template>
  <el-dialog v-model="visible" title="导入数据" width="700px" :close-on-click-modal="false">
    <el-steps :active="step" align-center finish-status="success" style="margin-bottom: 24px">
      <el-step title="选择文件" />
      <el-step title="字段映射" />
      <el-step title="导入结果" />
    </el-steps>

    <!-- Step 1: File Upload -->
    <div v-if="step === 0" class="iw-step">
      <el-upload
        drag
        accept=".csv"
        :auto-upload="false"
        :show-file-list="false"
        :on-change="handleFileChange"
      >
        <el-icon :size="40" class="iw-upload-icon"><upload-filled /></el-icon>
        <div class="iw-upload-text">将 CSV 文件拖到此处，或点击选择文件</div>
        <template #tip>
          <div class="el-upload__tip">仅支持 CSV 格式，第一行为列标题</div>
        </template>
      </el-upload>
      <div v-if="selectedFile" class="iw-file-info">
        已选择: {{ selectedFile.name }}
      </div>
    </div>

    <!-- Step 2: Field Mapping -->
    <div v-if="step === 1 && preview" class="iw-step">
      <h4 class="iw-section-title">预览数据（前10行）</h4>
      <el-table :data="previewRows" border size="small" max-height="200">
        <el-table-column
          v-for="col in preview.columns"
          :key="col"
          :label="col"
          :prop="col"
          min-width="120"
        />
      </el-table>

      <h4 class="iw-section-title" style="margin-top: 16px">字段映射</h4>
      <div class="iw-mapping">
        <div v-for="col in preview.columns" :key="col" class="iw-mapping-row">
          <span class="iw-mapping-csv">{{ col }}</span>
          <el-icon class="iw-mapping-arrow"><arrow-right /></el-icon>
          <el-select
            v-model="mapping[col]"
            placeholder="选择字段"
            size="small"
            style="width: 200px"
            :class="{ 'iw-mapping-warning': !mapping[col] }"
          >
            <el-option
              v-for="field in preview.available_fields"
              :key="field.name"
              :label="`${field.label}${field.required ? ' *' : ''}`"
              :value="field.name"
            />
            <el-option label="(不导入)" value="" />
          </el-select>
        </div>
      </div>
    </div>

    <!-- Step 3: Result -->
    <div v-if="step === 2 && result" class="iw-step">
      <el-result
        :icon="result.error_rows > 0 ? 'warning' : 'success'"
        :title="result.error_rows > 0 ? '导入完成，有错误' : '导入成功'"
        :sub-title="`成功 ${result.success_rows} 行，失败 ${result.error_rows} 行`"
      >
        <template #extra>
          <div v-if="result.errors.length > 0" class="iw-errors">
            <h4>错误详情</h4>
            <div v-for="err in result.errors" :key="err.row" class="iw-error-item">
              第 {{ err.row }} 行: {{ err.error }}
            </div>
          </div>
        </template>
      </el-result>
    </div>

    <template #footer>
      <el-button v-if="step > 0 && step < 2" @click="step--">上一步</el-button>
      <el-button v-if="step < 2" type="primary" :loading="loading" @click="handleNext">
        {{ step === 0 ? '下一步' : '开始导入' }}
      </el-button>
      <el-button v-else type="primary" @click="close">完成</el-button>
      <el-button v-if="step === 0" @click="close">取消</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { UploadFilled, ArrowRight } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { importExportApi } from '../../api/importExport'
import type { ImportPreview, ImportResult } from '../../types/importJob'

const props = defineProps<{
  objectType: string
}>()

const emit = defineEmits<{
  'done': []
}>()

const visible = ref(false)
const step = ref(0)
const loading = ref(false)
const selectedFile = ref<File | null>(null)
const preview = ref<ImportPreview | null>(null)
const mapping = ref<Record<string, string>>({})
const result = ref<ImportResult | null>(null)

const previewRows = computed(() => {
  if (!preview.value) return []
  return preview.value.preview_rows.map(row => {
    const obj: Record<string, string> = {}
    preview.value!.columns.forEach((col, idx) => {
      obj[col] = row[idx] || ''
    })
    return obj
  })
})

function open() {
  visible.value = true
  step.value = 0
  selectedFile.value = null
  preview.value = null
  result.value = null
}

function close() {
  visible.value = false
  emit('done')
}

function handleFileChange(file: any) {
  selectedFile.value = file.raw
}

async function handleNext() {
  if (step.value === 0) {
    if (!selectedFile.value) {
      ElMessage.warning('请选择文件')
      return
    }
    loading.value = true
    try {
      const { data } = await importExportApi.upload(selectedFile.value, props.objectType)
      preview.value = data
      // Initialize mapping with suggestions
      mapping.value = {}
      for (const [col, field] of Object.entries(data.mapping_suggestions)) {
        mapping.value[col] = field || ''
      }
      step.value = 1
    } catch (e: any) {
      ElMessage.error(e?.response?.data?.detail || '导入失败')
    } finally {
      loading.value = false
    }
  } else if (step.value === 1) {
    loading.value = true
    try {
      if (!preview.value) return
      const { data } = await importExportApi.confirm({
        preview_id: preview.value.preview_id,
        mapping: mapping.value,
      })
      result.value = data
      step.value = 2
    } catch (e: any) {
      ElMessage.error(e?.response?.data?.detail || '导入失败')
    } finally {
      loading.value = false
    }
  }
}

defineExpose({ open })
</script>

<style scoped>
.iw-step { min-height: 200px; }
.iw-upload-icon { margin-bottom: 8px; }
.iw-upload-text { font-size: 14px; color: #606266; margin-bottom: 8px; }
.iw-file-info { margin-top: 12px; padding: 8px; background: #f5f7fa; border-radius: 4px; font-size: 13px; }
.iw-section-title { font-size: 14px; font-weight: 600; color: #333; margin: 0 0 8px; }
.iw-mapping { display: flex; flex-direction: column; gap: 8px; }
.iw-mapping-row {
  display: flex; align-items: center; gap: 8px;
  padding: 6px 8px; background: #fafafa; border-radius: 4px;
}
.iw-mapping-csv { font-size: 13px; font-weight: 500; min-width: 120px; color: #333; }
.iw-mapping-arrow { color: #c0c4cc; }
.iw-mapping-warning :deep(.el-select__wrapper) { background: #fff3e0; }
.iw-errors { max-height: 200px; overflow-y: auto; margin-top: 8px; }
.iw-error-item { font-size: 12px; color: #f56c6c; padding: 2px 0; }
</style>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/components/import/ImportWizard.vue
git commit -m "feat: add ImportWizard component with 3-step dialog"
```

### Task 4.7: Add import/export buttons to list pages

**Files:**
- Modify: `frontend/src/views/accounts/AccountList.vue`
- Modify: `frontend/src/views/contacts/ContactList.vue`
- Modify: `frontend/src/views/products/ProductList.vue`
- Modify: `frontend/src/views/opportunities/OpportunityList.vue`
- Modify: `frontend/src/views/custom-objects/ObjectRecords.vue`

- [ ] **Step 1: For each list page, add import/export buttons**

Let's take AccountList.vue as an example. In the template, add after the search/new button row:
```vue
<!-- Add import/export buttons -->
<el-button size="small" @click="handleImport">📥 导入</el-button>
<el-button size="small" @click="handleExport">📤 导出</el-button>

<!-- Add ImportWizard -->
<ImportWizard ref="importWizard" object-type="account" @done="fetchAccounts" />
```

In the script:
```typescript
import { importExportApi } from '../../api/importExport'
import ImportWizard from '../../components/import/ImportWizard.vue'

const importWizard = ref<InstanceType<typeof ImportWizard> | null>(null)

function handleImport() {
  importWizard.value?.open()
}

async function handleExport() {
  try {
    const { data } = await importExportApi.exportCsv('account', searchQuery.value)
    const url = window.URL.createObjectURL(new Blob([data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'accounts.csv')
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch {
    ElMessage.error('导出失败')
  }
}
```

Repeat for:
- ContactList: `object-type="contact"`, filename `contacts.csv`
- ProductList: `object-type="product"`, filename `products.csv`
- OpportunityList: `object-type="opportunity"`, filename `opportunities.csv`
- ObjectRecords: export only (no import), uses `object-type` from route params

- [ ] **Step 2: Commit**

```bash
git add frontend/src/views/accounts/AccountList.vue frontend/src/views/contacts/ContactList.vue frontend/src/views/products/ProductList.vue frontend/src/views/opportunities/OpportunityList.vue frontend/src/views/custom-objects/ObjectRecords.vue
git commit -m "feat: add import/export buttons to list pages"
```

### Task 4.8: Phase 4 tests

- [ ] **Step 1: Write CSV import/export tests**

```python
# TEST/Unittest/test_import_export.py
import pytest
import io
import csv
from app.services.csv_service import parse_csv, auto_map_fields, OBJECT_FIELDS


def test_parse_csv():
    content = "名称,行业,电话\n测试公司,Tech,13800138000\n"
    headers, rows = parse_csv(content.encode("utf-8"))
    assert headers == ["名称", "行业", "电话"]
    assert len(rows) == 1
    assert rows[0] == ["测试公司", "Tech", "13800138000"]


def test_auto_map_fields():
    mapping = auto_map_fields(["名称", "行业", "电话"], "account")
    assert mapping["名称"] == "name"
    assert mapping["行业"] == "industry"
    assert mapping["电话"] == "phone"


@pytest.mark.asyncio
async def test_import_account(db_session):
    from app.services.csv_service import create_preview, confirm_import
    from app.models.crm import Account
    from sqlalchemy import select

    # Create a preview
    headers = ["名称", "行业"]
    rows = [["导入测试公司", "Tech"], ["导入测试公司2", "Finance"]]
    preview = create_preview(headers, rows, "account")
    preview_id = preview["preview_id"]

    # Confirm import
    mapping = {"名称": "name", "行业": "industry"}
    result = await confirm_import(db_session, preview_id, mapping, "test_user")

    assert result["success_rows"] == 2
    assert result["error_rows"] == 0

    # Verify records were created
    db_result = await db_session.execute(select(Account).where(Account.name.ilike("导入测试%")))
    accounts = db_result.scalars().all()
    assert len(accounts) == 2


def test_generate_csv():
    from app.services.csv_service import generate_csv
    records = [{"name": "Test", "industry": "Tech"}]
    csv_content = generate_csv("account", records)
    assert "名称" in csv_content
    assert "Test" in csv_content
```

Run: `cd backend && python -m pytest TEST/Unittest/test_import_export.py -v`
Expected: PASS

- [ ] **Step 2: Run all tests**

Run: `cd backend && python -m pytest TEST/Unittest/ -v`
Expected: All pass

- [ ] **Step 3: Commit**

```bash
git add TEST/Unittest/test_import_export.py
git commit -m "test: add import/export unit tests"
```

---

## Self-Review Checklist

- [ ] **Spec coverage:** Every requirement from the spec (4 features, 3 new tables, FTS5, 15+ API endpoints, ~12 new frontend components/pages) has tasks covering it
- [ ] **Placeholder scan:** No TBD, TODO, or placeholder patterns in the plan. Every step has actual code.
- [ ] **Type consistency:** ImportJob API endpoint uses `ImportJobOut` schema; confirm endpoint uses `ImportResultResponse`; frontend types match backend schemas. No signature mismatches between tasks.
- [ ] **Test coverage:** Each phase has at least 1 test file with 3-5 test cases
- [ ] **Edge cases:** CSV parsing handles UTF-8 BOM, empty rows, missing fields. Search falls back to LIKE if FTS5 fails. Notifications handle missing user gracefully.
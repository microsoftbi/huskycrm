# Husky CRM Enhancement Features Design

> 日期: 2026-07-19
> 状态: Draft

## Overview

This document covers the design for 4 enhancement features for Husky CRM:

1. **Activity Timeline / Change History** — Automatic audit logging of all CRUD operations, displayed as a timeline on record detail pages, merged with related events and tasks.
2. **Notification Center** — In-app notification system with bell icon, unread badge, and notification list.
3. **Global Search** — Full-text search across all objects (accounts, contacts, opportunities, products, events, custom objects) via a dropdown panel.
4. **Import / Export** — CSV import with preview and field mapping for core objects; CSV export for all objects.

## Architecture Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Audit log mechanism | SQLAlchemy event listeners | Automatic, zero changes to existing API code |
| Full-text search | SQLite FTS5 | Better performance and relevance ranking than LIKE |
| Notification delivery | Polling (30s interval) | Simple, consistent with existing REST architecture |
| Import strategy | Two-phase (upload → preview → confirm) | Allows field mapping verification before commit |

## Data Model Changes

### 1. `audit_logs` Table

```python
class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: str             # GUID (prefix: "aud_")
    object_type: str    # Object type name, e.g. "account", "contact", "opportunity"
    object_id: str      # ID of the record that changed
    field_name: str | None  # Changed field name; None for create/delete
    old_value: str | None   # Old value (stringified)
    new_value: str | None   # New value (stringified)
    action: str         # "create" | "update" | "delete"
    user_id: str        # Who performed the action
    created_at: datetime
```

**Recording rules:**
- `create`: One row with `action=create`, `field_name=None`, `old_value=None`, `new_value=None`
- `update`: One row per changed field, with `old_value` and `new_value`
- `delete`: One row with `action=delete`, `field_name=None`

**Event listener approach:**
- A single `audit_listen()` function attached to `after_insert` / `after_update` / `after_delete` events on all models
- Uses `inspect` to detect which columns changed
- Accesses current user via `contextvars` — a middleware stores `request.state.current_user` into a context variable so the event listener can read it without touching the request object
- Sensitive fields (password_hash) are excluded from audit logging by a configurable ignore list

### 2. `notifications` Table

```python
class Notification(Base):
    __tablename__ = "notifications"
    id: str                  # GUID (prefix: "not_")
    user_id: str             # Recipient user ID
    title: str               # Notification title
    message: str             # Notification body text
    notification_type: str   # "workflow" | "system"
    reference_type: str | None   # Related object type, e.g. "account"
    reference_id: str | None     # Related object ID
    is_read: bool            # Default False
    created_at: datetime
```

**Notification triggers:**
- **Workflow notifications**: When a workflow rule's action type is "notification", create a notification for the configured recipient(s)
- **System notifications**: When a user is assigned to a territory / account / etc., create a notification

### 3. `import_jobs` Table

```python
class ImportJob(Base):
    __tablename__ = "import_jobs"
    id: str                  # GUID (prefix: "imp_")
    object_type: str         # One of: "account", "contact", "product", "opportunity"
    filename: str            # Original CSV filename
    total_rows: int          # Total rows in CSV
    success_rows: int        # Rows successfully imported
    error_rows: int          # Rows with errors
    errors: str | None       # JSON string: array of {row, error_message}
    status: str              # "pending" | "processing" | "completed" | "failed"
    created_by: str          # User who ran the import
    created_at: datetime
```

### 4. FTS5 Search Index

SQLite FTS5 virtual table, created at database initialization:

```sql
CREATE VIRTUAL TABLE IF NOT EXISTS search_idx USING fts5(
    object_type, object_id, name, content, tokenize='unicode61'
);
```

**Triggers:** On INSERT/UPDATE/DELETE of searchable objects, sync to `search_idx`.

**Searchable objects and fields:**

| Object Type | Fields Indexed |
|-------------|---------------|
| `account` | name |
| `contact` | first_name, last_name, email |
| `opportunity` | name |
| `product` | name, product_code |
| `event` | subject |
| `custom_object_*` | name (dynamic) |

**Scope:** All objects share one FTS5 index for simplicity. Custom objects are handled dynamically — when a custom object definition is created, its records are also indexed.

## API Endpoints

### Import / Export

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/import/upload` | Upload CSV, parse, return preview + field mapping suggestions |
| `POST` | `/api/import/confirm` | Confirm import with finalized field mapping, write to DB |
| `GET` | `/api/import/jobs` | List import history |
| `GET` | `/api/export/{object_type}` | Export CSV, supports `?q=search&filters=...` |

**Import flow:**
1. User selects CSV file → upload via `POST /api/import/upload`
2. Backend parses CSV header, auto-maps columns to fields (e.g., `名称` → `name`), returns:
   ```json
   {
     "preview_id": "preview_uuid",
     "columns": ["名称", "行业", "电话"],
     "mapping_suggestions": {"名称": "name", "行业": "industry", "电话": "phone"},
     "available_fields": [...],
     "preview_rows": [...first 10 rows...]
   }
   ```
3. Frontend shows preview table, user adjusts field mapping if needed
4. User confirms → `POST /api/import/confirm` with `{preview_id, mapping: {...}}`
5. Backend validates and inserts, returns `{success_rows, error_rows, errors: [...]}`
6. Frontend shows result summary

### Activity Timeline

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/audit-logs/{object_type}/{object_id}` | Get change history for a record |
| `GET` | `/api/timeline/{object_type}/{object_id}` | Merged timeline: audit logs + events + tasks |

**`/api/timeline` response:**
```json
[
  {
    "type": "audit",
    "action": "update",
    "field_name": "phone",
    "old_value": "13800138000",
    "new_value": "13900139000",
    "user": {"id": "...", "display_name": "张三"},
    "created_at": "2026-07-19T09:30:00Z"
  },
  {
    "type": "event",
    "event_id": "...",
    "subject": "需求沟通",
    "status": "completed",
    "result": "success",
    "user": {"id": "...", "display_name": "李四"},
    "created_at": "2026-07-18T14:00:00Z"
  }
]
```

### Notification Center

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/notifications?page=&limit=` | List notifications for current user |
| `GET` | `/api/notifications/unread-count` | Get unread count (for polling badge) |
| `PUT` | `/api/notifications/{id}/read` | Mark single notification as read |
| `PUT` | `/api/notifications/read-all` | Mark all as read |

### Global Search

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/search?q=keyword&limit=` | Unified search across all objects |

**Response:**
```json
{
  "accounts": [{"id": "...", "name": "华为技术有限公司", ...}],
  "contacts": [{"id": "...", "first_name": "张三", "account_name": "华为"}],
  "opportunities": [{"id": "...", "name": "华为云服务采购", "amount": 500000}],
  "products": [{"id": "...", "name": "企业版软件"}],
  "events": [{"id": "...", "subject": "华为拜访"}],
  "custom_objects": {
    "培训课程": [{"id": "...", "name": "销售技巧培训"}],
    "项目": [{"id": "...", "name": "CRM二期"}]
  }
}
```

## Frontend Changes

### New Files

```
frontend/src/
├── api/
│   ├── auditLogs.ts          # Audit log API client
│   ├── notifications.ts      # Notification API client
│   ├── search.ts             # Search API client
│   └── importExport.ts       # Import/export API client
├── types/
│   ├── auditLog.ts           # AuditLog, TimelineEntry types
│   ├── notification.ts       # Notification types
│   └── importJob.ts          # ImportJob types
├── components/
│   ├── activity/
│   │   └── Timeline.vue      # Reusable timeline component
│   ├── notification/
│   │   ├── NotificationBell.vue   # Bell icon + unread badge
│   │   └── NotificationDropdown.vue  # Dropdown panel
│   └── search/
│       └── GlobalSearch.vue   # Search input + dropdown panel
├── views/
│   └── admin/
│       └── NotificationList.vue  # Full notification list page
└── composables/
    └── useNotifications.ts   # Notification polling and state
```

### Modified Files

| File | Changes |
|------|---------|
| `frontend/src/components/layout/Header.vue` | Add GlobalSearch, NotificationBell; wire up search and notification |
| `frontend/src/views/accounts/AccountDetail.vue` | Add "活动" tab with Timeline component |
| `frontend/src/views/contacts/ContactDetail.vue` | Add "活动" tab with Timeline component |
| `frontend/src/views/opportunities/OpportunityDetail.vue` | Add "活动" tab with Timeline component |
| `frontend/src/views/accounts/AccountList.vue` | Add import/export buttons |
| `frontend/src/views/contacts/ContactList.vue` | Add import/export buttons |
| `frontend/src/views/products/ProductList.vue` | Add import/export buttons |
| `frontend/src/views/opportunities/OpportunityList.vue` | Add import/export buttons |
| `frontend/src/views/custom-objects/ObjectRecords.vue` | Add export button |
| `frontend/src/router/index.ts` | Add notification list route |
| `frontend/src/components/layout/Sidebar.vue` | Add notification link if needed |

### UI Details

**Import Dialog (3-step wizard):**
- Step 1: File upload + object type selector
- Step 2: Preview table (first 10 rows) + field mapping dropdowns
- Step 3: Confirmation + result summary (success/error counts)

**Timeline Component:**
- Left-side vertical timeline line with dots
- Each entry: icon (audit/event/task), user name, action description, timestamp
- Audit entries show old→new value changes
- Supports "load more" pagination

**Notification Bell:**
- Integrates with `useNotifications` composable that polls `/api/notifications/unread-count` every 30s
- Dropdown: 10 most recent notifications, unread in bold, click to mark read + navigate
- "全部标记已读" link at bottom
- "查看全部通知" → navigate to `/admin/notifications`

**Global Search:**
- Search input in Header, placeholder text updated to "搜索账户、联系人、商机..."
- Debounced input (300ms) triggers `/api/search`
- Dropdown panel shows results grouped by object type
- Max 5 results per type, "查看更多" link if more
- Click navigates to detail page
- Ctrl+K key shortcut to focus search

## Implementation Order

### Phase 1: Activity Timeline (Change History)
1. Create `audit_logs` model + schema
2. Implement `app/models/audit.py` with SQLAlchemy event listeners
3. Create `/api/audit-logs` and `/api/timeline` endpoints
4. Create frontend Timeline component
5. Add "活动" tab to AccountDetail, ContactDetail, OpportunityDetail

### Phase 2: Notification Center
1. Create `notifications` model + schema
2. Create notification API endpoints
3. Create frontend `NotificationBell`, `NotificationDropdown`, `useNotifications`
4. Wire system notifications into key operations (territory assignment, account assignment)
5. Create `NotificationList.vue` page

### Phase 3: Global Search
1. Create FTS5 virtual table + triggers
2. Create `/api/search` endpoint
3. Create `GlobalSearch.vue` component
4. Integrate into Header.vue

### Phase 4: Import / Export
1. Create `import_jobs` model + schema
2. Implement CSV parser + field mapping logic
3. Create import/export API endpoints
4. Create import wizard dialog
5. Add import/export buttons to list pages

## Files to Create (Backend)

```
backend/app/
├── models/
│   ├── audit_log.py          # AuditLog model
│   └── notification.py       # Notification model
├── schemas/
│   ├── audit_log.py          # Pydantic schemas
│   ├── notification.py       # Pydantic schemas
│   └── import_export.py      # Pydantic schemas for import
├── api/
│   ├── audit_logs.py         # Timeline API endpoints
│   ├── notifications.py      # Notification API endpoints
│   ├── search.py             # Global search endpoint
│   └── import_export.py      # Import/export endpoints
└── services/
    ├── audit_service.py      # SQLAlchemy event listener setup
    ├── csv_service.py        # CSV parsing and field mapping
    └── search_service.py     # FTS5 index management
```

## Files to Modify (Backend)

| File | Changes |
|------|---------|
| `backend/app/main.py` | Register new routers (audit_logs, notifications, search, import_export) |
| `backend/app/database.py` | Import new models, create FTS5 table, seed triggers |
| `backend/app/api/territories.py` | Add system notifications on territory member/account assignment |
| `backend/app/services/workflow_service.py` | Create notifications when workflow action is "notification" |
| `backend/app/models/__init__.py` | Export new models |
# Technical Concept Document

> **Deloitte ProjectOps** — Tax Compliance Calendar & Deadline Tracking

## Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Layer                              │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Bootstrap 5 + Jinja2 Templates (Server-Rendered)       │    │
│  │  Optional: HTMX/Alpine.js for enhanced UX (Phase 2)     │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Application Layer                            │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Flask Application (Blueprints)                         │    │
│  │  ├── auth/      (login, logout, session)                │    │
│  │  ├── main/      (dashboard, calendar)                   │    │
│  │  ├── tasks/     (task CRUD, status, evidence)           │    │
│  │  ├── admin/     (entities, users, templates, import)    │    │
│  │  └── api/       (REST endpoints for async ops)          │    │
│  └─────────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Services Layer                                         │    │
│  │  ├── TaskService      (lifecycle, status transitions)   │    │
│  │  ├── ImportService    (Excel parsing, validation)       │    │
│  │  ├── AuditService     (immutable logging)               │    │
│  │  └── NotificationSvc  (reminders - Phase 2)             │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Data Layer                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  SQLAlchemy ORM + Alembic Migrations                    │    │
│  │  PostgreSQL (Production) / SQLite (Development)         │    │
│  └─────────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  File Storage (Evidence)                                │    │
│  │  Local filesystem (MVP) → Azure Blob/S3 (Production)    │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Background Jobs (Phase 2)                     │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  APScheduler / Celery + Redis                           │    │
│  │  ├── Due-soon status evaluation (daily)                 │    │
│  │  ├── Overdue marking (daily)                            │    │
│  │  ├── Reminder notifications                             │    │
│  │  └── Recurring task generation                          │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

### Authentication Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│  User    │────▶│  Login   │────▶│  Flask   │
│          │     │  Form    │     │  Login   │
└──────────┘     └──────────┘     └──────────┘
                                       │
                 MVP: Local Auth ◀─────┤
                 (Flask-Login)         │
                                       ▼
                 Phase 2: ────▶  ┌──────────┐
                 OIDC/Entra ID   │  Entra   │
                                 │  ID      │
                                 └──────────┘
```

### Data Model (Entity Relationship)

```
┌─────────────────┐       ┌─────────────────┐
│     users       │       │    entities     │
├─────────────────┤       ├─────────────────┤
│ id              │       │ id              │
│ email           │       │ name            │
│ name            │       │ country         │
│ password_hash   │       │ group_id        │
│ role            │       │ active          │
│ is_active       │       └────────┬────────┘
│ created_at      │                │
│ last_login      │                │
└────────┬────────┘                │
         │                         │
         │    ┌────────────────────┼────────────────────┐
         │    │                    │                    │
         ▼    ▼                    ▼                    │
┌─────────────────┐       ┌─────────────────┐          │
│     tasks       │◀──────│ task_templates  │          │
├─────────────────┤       ├─────────────────┤          │
│ id              │       │ id              │          │
│ template_id  ───┼──────▶│ tax_type_id  ───┼──┐       │
│ entity_id    ───┼───────┼─────────────────┼──┼───────┘
│ year            │       │ keyword         │  │
│ due_date        │       │ description     │  │
│ status          │       │ default_recur   │  │
│ owner_id     ───┼───┐   │ default_due     │  │
│ reviewer_id  ───┼───┤   └─────────────────┘  │
│ submitted_at    │   │                        │
│ completed_at    │   │   ┌─────────────────┐  │
└────────┬────────┘   │   │   tax_types     │◀─┘
         │            │   ├─────────────────┤
         │            │   │ id              │
         │            │   │ name            │
         │            │   │ code            │
         ▼            │   └─────────────────┘
┌─────────────────┐   │
│  task_evidence  │   │
├─────────────────┤   │
│ id              │   │
│ task_id         │   │
│ type            │   │
│ file_path/url   │   │
│ uploaded_by  ───┼───┘
│ uploaded_at     │
└─────────────────┘

┌─────────────────┐       ┌─────────────────┐
│    comments     │       │   audit_log     │
├─────────────────┤       ├─────────────────┤
│ id              │       │ id              │
│ task_id         │       │ timestamp       │
│ reference_id    │       │ user_id         │
│ text            │       │ action          │
│ created_by      │       │ object_type     │
│ created_at      │       │ object_id       │
│ resolved        │       │ old_value       │
└─────────────────┘       │ new_value       │
                          │ ip_address      │
┌─────────────────┐       └─────────────────┘
│ references_     │
│ applications    │
├─────────────────┤
│ id              │
│ law             │
│ paragraph       │
│ purpose         │
│ explanation     │
│ source          │
└─────────────────┘
```

---

## Feature Roadmap

### MVP (Phase 1) — Target: 6-10 Core Screens

| Priority | Feature | Description | Status |
|----------|---------|-------------|--------|
| 1 | **Authentication** | Local Flask-Login (email/password) | 🟡 Existing |
| 2 | **User Management** | Admin CRUD for users, role assignment | 🔴 To Build |
| 3 | **Entity Management** | CRUD for legal entities/Gesellschaften | 🔴 To Build |
| 4 | **Tax Types** | Manage tax type catalog (KSt, USt, GewSt, etc.) | 🔴 To Build |
| 5 | **Excel Import** | Import YEAR/Anträge/Kommentare sheets | 🔴 To Build |
| 6 | **Task Templates** | Generated from Excel, editable | 🔴 To Build |
| 7 | **Task List** | Filterable list with status badges | 🔴 To Build |
| 8 | **Task Detail** | Status change, evidence, comments, audit | 🔴 To Build |
| 9 | **Calendar View** | Month view, color-coded by status | 🔴 To Build |
| 10 | **Dashboard** | KPIs, filters, "My Tasks" panel | 🔴 To Build |
| 11 | **Basic Reports** | Export filtered tasks to Excel | 🔴 To Build |

### Phase 2 — Enhanced Functionality

| Feature | Description |
|---------|-------------|
| **OIDC/Entra ID** | SSO integration with Azure AD |
| **Recurrence Rules** | RRULE-based automatic task generation |
| **Reminder System** | Email/Teams notifications before due dates |
| **Four-Eyes Enforcement** | Cannot complete without reviewer approval |
| **Advanced Reports** | Compliance heatmaps, drilldowns, aging reports |
| **Template Builder UI** | Create templates without Excel import |
| **Batch Operations** | Reassign, change due dates in bulk |
| **File Virus Scanning** | Integrate with antivirus for uploads |

### Phase 3 — Enterprise Features

| Feature | Description |
|---------|-------------|
| **Multi-Tenant** | Support multiple client organizations |
| **API Gateway** | REST API for external integrations |
| **SAP Integration** | Pull/push data from SAP systems |
| **Power BI Connector** | Export data for BI dashboards |
| **Mobile App** | Progressive Web App or native |

---

## Status Definitions & Color Mapping

| Status | Description | Deloitte CSS Variable | Trigger |
|--------|-------------|----------------------|---------|
| **Draft** | Task created, not started | `--dtt-cool-gray-6` | Initial state |
| **Due Soon** | Within N days of due date | `--dtt-warning-orange` | Automatic (N=7) |
| **Overdue** | Past due date, not completed | `--dtt-danger-red` | Automatic |
| **Submitted** | Preparer submitted deliverable | `--dtt-sec-blue-4` | Manual action |
| **In Review** | Reviewer is checking | `--dtt-sec-teal-6` | Manual action |
| **Completed** | Finalized, evidence locked | `--dtt-sec-green-5` | Manual action |

### State Transition Diagram

```
                    ┌─────────────────────────────────────┐
                    │                                     │
                    ▼                                     │
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│  Draft  │────▶│Submitted│────▶│In Review│────▶│Completed│
└─────────┘     └─────────┘     └────┬────┘     └─────────┘
                    ▲                │
                    │                │
                    └────────────────┘
                    (Rework Required)

System Overlays (automatic, non-blocking):
- Due Soon: applied when due_date - today <= N days
- Overdue: applied when due_date < today AND status != Completed
```

---

## Non-Functional Requirements

### Security
- RBAC with fine-grained permissions
- Secure file upload handling (path sanitization, size limits)
- CSRF protection on all forms
- Password hashing with Werkzeug

### Auditability
- Immutable audit log for all changes
- Evidence snapshots (files cannot be deleted after completion)
- User action tracking with IP and timestamp

### Performance
- Database indexes on: `due_date`, `status`, `entity_id`, `owner_id`
- Pagination for task lists (50 items default)
- Lazy loading for large evidence files

### Data Retention
- Configurable retention periods
- Export before deletion
- Soft delete for tasks (archive, don't destroy)

### Compliance
- GDPR: minimal PII, access controls, export capability
- Audit trail for regulatory inspection
- Role-based data visibility

# Progress Tracker

> Development progress for Deloitte TaxOps Calendar

## Current Status: ✅ MVP Complete with Multi-Reviewer

**Last Updated:** 2025-12-28 (Session 3)

---

## Existing Features (From Template)

### ✅ Completed (Inherited)

- [x] Flask application factory pattern
- [x] SQLAlchemy integration with SQLite
- [x] User model with password hashing
- [x] Flask-Login authentication
- [x] Admin role decorator (`@admin_required`)
- [x] AuditLog model for activity tracking
- [x] Bootstrap 5 base template with Deloitte branding
- [x] Complete Deloitte 2024 color palette CSS variables
- [x] Internationalization (DE/EN) with session storage
- [x] Login/logout functionality
- [x] Flash message system
- [x] Error pages (404, 500)
- [x] Responsive navbar with language switcher
- [x] Admin dashboard (basic)
- [x] Admin users list (read-only)
- [x] CLI commands (`flask initdb`, `flask createadmin`)

---

## MVP Checklist

### Phase 1: Foundation ✅

- [x] Memory Bank documentation created
- [x] Install Flask-Migrate for Alembic
- [x] Install openpyxl for Excel processing
- [x] Install python-dateutil for date handling
- [x] Initialize migrations (`flask db init`)
- [ ] Restructure to blueprints (deferred)

### Phase 2: Core Models ✅

- [x] Entity model (with self-referential groups)
- [x] TaxType model
- [x] TaskTemplate model
- [x] Task model with status enum
- [x] TaskEvidence model (file + link types)
- [x] Comment model
- [x] ReferenceApplication model (Anträge)
- [x] TaskPreset model (predefined task templates)
- [x] **TaskReviewer model (multi-reviewer support)**
- [x] UserRole enum (admin, manager, reviewer, preparer, readonly)
- [x] TaskStatus enum (draft, submitted, in_review, approved, completed, rejected)
- [x] Entity-User access association table
- [x] Create migration for all models
- [x] Apply migration (`flask db upgrade`)

### Phase 3: User & Entity Management ✅

- [x] User CRUD (admin) - create/edit forms
- [x] Extended user roles (manager, reviewer, preparer, readonly)
- [x] Entity CRUD (admin) - full CRUD with parent selection
- [x] TaxType CRUD (admin) - full CRUD
- [ ] User-Entity permission scoping (deferred)

### Phase 4: Task Presets ✅

- [x] TaskPreset model for predefined tasks
- [x] JSON data files (steuerarten_aufgaben.json, Antraege.json)
- [x] Admin preset management (list, create, edit, delete)
- [x] `flask loadpresets` CLI command
- [x] Preset selection in task creation form
- [x] Auto-fill form from preset data

### Phase 5: Task Management ✅

- [x] Task list view with filters
- [x] Task detail view with tabs (overview, evidence, comments, audit)
- [x] Status change functionality
- [x] Status badge CSS classes (Deloitte colors)
- [x] Evidence upload (file upload with unique names)
- [x] Evidence link addition
- [x] Evidence preview modal (PDF, images, text)
- [x] Evidence download
- [x] Comment thread (add/delete)
- [x] Audit log display (color-coded by action type)

### Phase 6: Multi-Reviewer Approval ✅

- [x] TaskReviewer model with approval tracking
- [x] Multi-select reviewer field in task form
- [x] Individual reviewer approval/rejection
- [x] Approval progress bar
- [x] Auto-transition to approved when all approve
- [x] Auto-transition to rejected if any rejects
- [x] Reviewer-specific action buttons
- [x] Per-reviewer approval timestamps and notes

### Phase 7: Calendar & Dashboard ✅

- [x] Calendar month view
- [x] Calendar year view
- [x] Calendar status colors
- [x] Task preview popovers on hover
- [x] Task click opens detail
- [x] Dashboard KPI cards
- [x] "My Tasks" panel
- [x] Due soon / Overdue automatic marking (via Task properties)

### Phase 8: Reports & Export

- [ ] Task list Excel export
- [ ] Status summary report
- [ ] Basic filtering for exports

---

## Phase 2 Backlog (Post-MVP)

### Authentication & Security
- [ ] OIDC/Entra ID integration
- [ ] Role mapping from Azure AD groups
- [ ] Virus scanning for uploads

### Advanced Features
- [ ] RRULE recurrence rules
- [ ] Automatic recurring task generation
- [ ] Email reminders
- [ ] Teams notifications
- [ ] Batch operations (reassign, change due dates)

### Advanced Reports
- [ ] Compliance heatmap (entity × month)
- [ ] Overdue aging report
- [ ] On-time rate by tax type
- [ ] Workload by owner report

### Template Management
- [ ] Template builder UI (no Excel needed)
- [ ] Template versioning

---

## Session Log

### 2025-12-28 — Session 1: Initial Setup

**Completed:**
- Reviewed existing Flask template codebase
- Created Memory Bank documentation structure
- Installed new dependencies (flask-migrate, openpyxl, python-dateutil)
- Created all TaxOps Calendar models
- Added enums: TaskStatus, UserRole, EvidenceType, RecurrenceType
- Extended User model with new roles and relationships
- Initialized Alembic migrations
- Generated and applied first migration

### 2025-12-28 — Session 2: Core Features

**Completed:**
- Entity CRUD admin interface
- TaxType CRUD admin interface  
- User CRUD admin interface
- Main dashboard with KPI cards
- Task list view with filters
- Task detail view with 4 tabs
- Status change functionality
- Calendar month view
- Updated navigation
- Seed command with sample data

### 2025-12-28 — Session 3: Advanced Features

**Completed:**
- **Evidence Upload System:**
  - File upload route with secure filename handling
  - Link addition route
  - File preview modal (PDF, images, text inline)
  - Download route with proper MIME types
  - Evidence deletion

- **Comments System:**
  - Add comment route
  - Delete comment route (owner/admin only)
  - User avatars and timestamps

- **Audit Log Enhancement:**
  - Color-coded action badges
  - Icons for different action types
  - Entity-scoped logging for evidence/comments

- **UI Improvements:**
  - Navbar with "TaxOps Calendar" app name
  - Green separator between logo and title
  - Calendar preview popovers on month/year views
  - Task list preview column with hover popovers

- **Task Presets System:**
  - TaskPreset model
  - Admin management interface
  - JSON data import (loadpresets command)
  - Preset selection in task form

- **Multi-Reviewer Approval System:**
  - TaskReviewer model with approval tracking
  - Multi-select reviewer field
  - Individual approval/rejection workflow
  - Approval progress bars
  - Auto-transition logic
  - Updated permission checks

- **Documentation:**
  - Updated Memory Bank docs
  - Comprehensive README.md for GitHub

---

## Known Issues

| Issue | Severity | Status |
|-------|----------|--------|
| None currently | — | — |

---

## Files Modified (Session 3)

### Models
- `models.py` — Added TaskReviewer model, Task multi-reviewer methods

### Routes (app.py)
- `task_upload_evidence` — File upload handler
- `task_add_link` — Link addition handler
- `task_preview_evidence` — Inline file preview
- `task_download_evidence` — File download
- `task_delete_evidence` — Evidence deletion
- `task_add_comment` — Comment creation
- `task_delete_comment` — Comment deletion
- `task_reviewer_action` — Individual reviewer approve/reject
- Updated `task_create` / `task_edit` for multi-reviewer

### Templates
- `templates/tasks/form.html` — Multi-select reviewers
- `templates/tasks/detail.html` — Evidence upload, comments, multi-reviewer display
- `templates/tasks/list.html` — Preview column with popovers
- `templates/calendar.html` — Task preview popovers
- `templates/calendar_year.html` — Task preview popovers
- `templates/base.html` — App name in navbar
- `templates/admin/presets.html` — Task preset management
- `templates/admin/preset_form.html` — Preset create/edit

### Migrations
- `f34a3101bc19_add_taskreviewer_many_to_many_table_for_.py`

---

## Notes

- Using Alembic for database migrations (Flask-Migrate wrapper)
- Local Flask-Login auth for MVP, OIDC planned for Phase 2
- PostgreSQL recommended for production, SQLite for development
- Evidence files stored locally in uploads/ folder
- Multi-reviewer requires ALL reviewers to approve before task is approved
- ANY reviewer rejection immediately rejects the entire task

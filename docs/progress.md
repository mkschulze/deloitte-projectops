# Progress Tracker

> Development progress for Deloitte TaxOps Calendar

## Current Status: ✅ MVP Complete + Phases A-J (Notifications, Bulk Ops, Exports, iCal, Email, Charts, Entity Scoping, Recurring Tasks, Archival, Template Builder UI)

**Last Updated:** 2025-12-31 (Session 7)  
**Version:** 1.2.0

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
- [x] **Team model (user grouping)**
- [x] UserRole enum (admin, manager, reviewer, preparer, readonly)
- [x] TaskStatus enum (draft, submitted, in_review, approved, completed, rejected)
- [x] Entity-User access association table
- [x] team_members association table
- [x] Create migration for all models
- [x] Apply migration (`flask db upgrade`)

### Phase 3: User & Entity Management ✅

- [x] User CRUD (admin) - create/edit forms
- [x] Extended user roles (manager, reviewer, preparer, readonly)
- [x] Entity CRUD (admin) - full CRUD with parent selection
- [x] TaxType CRUD (admin) - full CRUD
- [x] **Team Management (admin) - full CRUD with member assignment**
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

### Phase 6b: Team Management ✅

- [x] Team model with name, description, color, manager
- [x] team_members many-to-many association table
- [x] Task.owner_team_id for team-based ownership
- [x] Task.reviewer_team_id for team-based review
- [x] Team admin CRUD (list, create, edit, delete)
- [x] Multi-select member assignment
- [x] Team selection in task create/edit forms
- [x] Team display in task detail view
- [x] is_reviewer() checks team membership
- [x] Navigation link in admin menu

### Phase 7: Calendar & Dashboard ✅

- [x] Calendar month view
- [x] Calendar year view
- [x] Calendar status colors
- [x] Task preview popovers on hover
- [x] Task click opens detail
- [x] Dashboard KPI cards
- [x] "My Tasks" panel
- [x] Due soon / Overdue automatic marking (via Task properties)

### Phase 8: Reports & Export ✅

- [x] Task list Excel export
- [x] Task PDF export (weasyprint)
- [x] Status summary report (multi-sheet Excel)
- [x] Filtering preserved in exports

---

## Phase 2 Backlog (Post-MVP) — Feature Roadmap

### Phase A: In-App Notifications (WebSocket) ✅
- [x] Flask-SocketIO + eventlet dependencies
- [x] Notification model with NotificationType enum
- [x] NotificationService with helper methods
- [x] WebSocket events (connect, disconnect, emit)
- [x] Notification API routes
- [x] Notification triggers in task/comment routes
- [x] Navbar notification bell with dropdown
- [x] Real-time WebSocket JavaScript client
- [x] Translations (DE/EN)
- [x] Database migration

### Phase B: Bulk Operations ✅
- [x] Bulk selection UI (checkboxes in task list)
- [x] "Select all" toggle
- [x] Bulk status change
- [x] Bulk reassign owner
- [x] Bulk delete (hard delete with related records)
- [x] Confirmation modals
- [x] Loading spinners during operations
- [x] Success/error handling

### Phase C: Excel/PDF Export ✅
- [x] Task list Excel export with filters
- [x] Task detail PDF export (weasyprint)
- [x] Status summary report (Excel with charts)
- [x] Export buttons in UI (dropdown in task list, button in task detail)
- [x] Deloitte branding in exports (colors, logo)

### Phase D: Calendar Sync (iCal) ✅
- [x] iCal feed endpoint per user (`/calendar/feed/<token>.ics`)
- [x] Task deadlines as calendar events with alarms
- [x] Secure token-based subscription URL generation
- [x] User settings for calendar sync (subscription page)
- [x] Instructions for Outlook, Google Calendar, Apple Calendar
- [x] Token regeneration for security

### Phase E: E-Mail Notifications ✅
- [x] Email service abstraction (SMTP/SendGrid/SES providers)
- [x] Email configuration in config.py
- [x] HTML email templates with Deloitte branding (inline CSS)
- [x] Task assignment email notification
- [x] Status change email notification
- [x] Due reminder email (via CLI command)
- [x] New comment email notification
- [x] User email preferences (profile_notifications.html)
- [x] Master toggle + per-notification-type settings
- [x] CLI command: `flask send_due_reminders --days=7`
- [x] Database migration for User email preferences

### Phase F: Dashboard Extensions (Chart.js) ✅
- [x] Chart.js integration (CDN)
- [x] Tasks by status doughnut chart (pie chart with cutout)
- [x] Tasks by month stacked bar chart (with year selector)
- [x] Team workload horizontal bar chart
- [x] API endpoints for chart data
- [x] Responsive chart containers

### Phase G: Entity Scoping ✅
- [x] UserEntity model with access levels (view, edit, manage)
- [x] EntityAccessLevel enum
- [x] Entity-based task filtering in dashboard and task list
- [x] Entity hierarchy access inheritance (inherit_to_children flag)
- [x] User.get_accessible_entities() and get_accessible_entity_ids() methods
- [x] User.can_access_entity() and get_entity_access_level() methods
- [x] Admin UI: User entity permissions (/admin/users/<id>/entities)
- [x] Admin UI: Entity user permissions (/admin/entities/<id>/users)
- [x] Links in admin users and entities lists
- [x] Auto-access for admins and managers (bypass permissions)
- [x] Database migration for user_entity table

### Phase H: Recurring Tasks (RRULE) ✅
- [x] TaskPreset extended with recurrence fields (is_recurring, frequency, rrule, day_offset, end_date)
- [x] Task model extended with preset_id and is_recurring_instance
- [x] RECURRENCE_FREQUENCIES constant (monthly, quarterly, semi_annual, annual, custom)
- [x] RecurrenceService with get_period_dates(), generate_tasks_from_preset(), parse_rrule()
- [x] CLI command: `flask generate-recurring-tasks --year --preset-id --entity-id --dry-run --force`
- [x] Admin preset form with recurrence configuration UI
- [x] Frequency selector, day offset, RRULE input, default entity/owner
- [x] Task detail shows recurring badge with preset reference
- [x] Database migration for recurrence fields

### Phase I: Archival & Soft-Delete ✅
- [x] Soft-delete for tasks (is_archived, archived_at, archived_by_id, archive_reason)
- [x] Task model extended with archive() and restore() methods
- [x] Archive/Restore routes (single and bulk)
- [x] Archived tasks hidden from dashboard, task list, calendar views
- [x] Archive view page with filters and pagination (/tasks/archive)
- [x] Archive button in task detail with reason modal
- [x] Restore button for archived tasks (admin/manager only)
- [x] Bulk archive functionality in task list
- [x] Bulk restore functionality in archive view
- [x] Navigation dropdown for tasks with archive link
- [x] Archived banner on task detail page
- [x] Translations for archive features (DE/EN)
- [x] Database migration for archive fields

### 🆕 Projektmanagement-Modul (Jira-ähnlich)

> **Detaillierter Plan:** [docs/projectManagementModule.md](projectManagementModule.md)

#### Phase PM-0: Infrastruktur
- [ ] Blueprint-Refactoring (extensions.py, modules/)
- [ ] ModuleRegistry Pattern
- [ ] Module & UserModule Models
- [ ] Dynamische Navigation
- [ ] Admin Modul-Verwaltung

#### Phase PM-1: Projekt-Basis
- [ ] Project Model mit Key (TAX, AUD)
- [ ] ProjectMember für Mitgliedschaft
- [ ] Projekt-CRUD Routes & Templates

#### Phase PM-2: Issue-Management
- [ ] Issue Model mit Auto-Key (TAX-1, TAX-2)
- [ ] IssueType: Epic, Story, Task, Bug, Sub-Task
- [ ] IssueStatus: Open, In Progress, In Test, Done
- [ ] Issue-CRUD mit Markdown-Editor

#### Phase PM-3: Kanban Board
- [ ] Board & BoardColumn Models
- [ ] SortableJS Drag & Drop
- [ ] Move-API für Status-Änderungen
- [ ] WebSocket Real-time Updates

#### Phase PM-4: Backlog
- [ ] Priorisierte Issue-Liste
- [ ] Drag & Drop Ranking
- [ ] Bulk-Aktionen

#### Phase PM-5: Sprint-Management
- [ ] Sprint Model (name, goal, dates)
- [ ] Sprint starten/beenden
- [ ] Sprint-Board

#### Phase PM-6 bis PM-10: Erweitert
- [ ] Kommentare, Attachments, Links
- [ ] Epics & Progress-Tracking
- [ ] Suche & Filter
- [ ] Charts (Burndown, Velocity)
- [ ] Konfigurierbare Workflows

### Phase J: Template Builder UI ✅
**Full Form Builder (Option C) implementation**

#### C1: Enhanced Preset Form ✅
- [x] Live preview panel showing task card with current form values
- [x] Recurrence wizard with visual calendar date preview
- [x] Tax type search dropdown with filtering
- [x] Due date calculator showing next occurrences

#### C2: Visual Category Tree ✅
- [x] 3 views: Tree (grouped by tax type), Card (grid), Table (classic)
- [x] Drag & drop reordering (SortableJS)
- [x] Bulk selection with floating action bar
- [x] Quick edit slide-out panel
- [x] JSON export (includes custom fields)
- [x] View persistence in localStorage

#### C3: Custom Fields ✅
- [x] PresetCustomField model (name, labels, type, required, options, conditions)
- [x] TaskCustomFieldValue model for storing values
- [x] CustomFieldType enum (text, textarea, number, date, select, checkbox)
- [x] Custom Fields UI section in preset form
- [x] Modal dialog for field creation/editing
- [x] API endpoints for CRUD operations
- [x] Template variables support ({{year}}, {{entity}}, etc.)

#### C4: Import/Export Enhancement ✅
- [x] Enhanced JSON export includes custom fields
- [x] JSON import handles enhanced format with custom fields
- [x] Import counts imported fields in message
- [x] Conditional visibility fields (condition_field, condition_operator, condition_value)

### Future Considerations
- [ ] OIDC/Entra ID integration
- [ ] Role mapping from Azure AD groups
- [ ] Virus scanning for uploads
- [ ] MS Teams notifications

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

### 2025-12-28 — Session 4: Team Management

**Completed:**
- **Team Model & Database:**
  - Created Team model with name, description, color, manager
  - Created team_members association table (many-to-many)
  - Added owner_team_id and reviewer_team_id to Task model
  - Generated and applied migration

- **Admin Team Management:**
  - Team list view with color indicators
  - Team create/edit form with multi-select members
  - Team soft-delete (deactivation)
  - Added Teams link to admin navigation menu

- **Task-Team Integration:**
  - Task form with owner team and reviewer team selection
  - Task detail shows team assignments
  - is_reviewer() checks team membership for access control

### 2025-12-31 — Session 6: Recurring Tasks (Phase H)

**Completed:**
- **TaskPreset Model Extended:**
  - Added is_recurring, recurrence_frequency, recurrence_rrule fields
  - Added recurrence_day_offset (day of period when task is due)
  - Added recurrence_end_date for optional end date
  - Added last_generated_date for tracking
  - Added default_owner_id and default_entity_id with relationships
  - RECURRENCE_FREQUENCIES constant with labels (DE/EN)

- **Task Model Extended:**
  - Added preset_id foreign key to task_preset
  - Added is_recurring_instance boolean flag
  - Added preset relationship with backref 'generated_tasks'

- **RecurrenceService:**
  - get_period_dates(frequency, year, day_offset) - generates period labels and due dates
  - generate_tasks_from_preset(preset, year, entities, owner_id, force) - creates task instances
  - generate_all_recurring_tasks(year, dry_run) - batch generation from all presets
  - parse_rrule(rrule_string, start_date, count) - RRULE parsing via python-dateutil

- **CLI Command:**
  - `flask generate-recurring-tasks` with --year, --preset-id, --entity-id, --dry-run, --force options
  - Dry-run shows what would be created without changes
  - Supports single preset or all recurring presets

- **Admin UI:**
  - Preset form extended with recurrence settings card
  - Toggle to enable recurring generation
  - Frequency dropdown (monthly, quarterly, semi-annual, annual, custom RRULE)
  - Day offset input, RRULE field for custom patterns
  - Default entity and owner selection
  - End date picker
  - Shows last generated date and task count

- **Task Detail:**
  - Shows "Recurring" badge for is_recurring_instance tasks
  - Links to source preset on hover

- **Database Migration:**
  - c3d4e5f6g7h8_add_recurring_task_fields.py applied

---

## Known Issues

| Issue | Severity | Status |
|-------|----------|--------|
| None currently | — | — |

---

## Files Modified (Session 3 & 4)

### Models
- `models.py` — Added TaskReviewer model, Task multi-reviewer methods, Team model, team_members table, Task team fields

### Routes (app.py)
- `task_upload_evidence` — File upload handler
- `task_add_link` — Link addition handler
- `task_preview_evidence` — Inline file preview
- `task_download_evidence` — File download
- `task_delete_evidence` — Evidence deletion
- `task_add_comment` — Comment creation
- `task_delete_comment` — Comment deletion
- `task_reviewer_action` — Individual reviewer approve/reject
- `admin_teams` — Team list view
- `admin_team_new` — Team creation
- `admin_team_edit` — Team editing with member management
- `admin_team_delete` — Team soft-delete
- Updated `task_create` / `task_edit` for multi-reviewer and teams

### Templates
- `templates/tasks/form.html` — Multi-select reviewers, team selection
- `templates/tasks/detail.html` — Evidence upload, comments, multi-reviewer display, team display
- `templates/tasks/list.html` — Preview column with popovers
- `templates/calendar.html` — Task preview popovers
- `templates/calendar_year.html` — Task preview popovers
- `templates/base.html` — App name in navbar, Teams link in admin menu
- `templates/admin/presets.html` — Task preset management
- `templates/admin/preset_form.html` — Preset create/edit
- `templates/admin/teams.html` — Team list view (NEW)
- `templates/admin/team_form.html` — Team create/edit form (NEW)

### Migrations
- `f34a3101bc19_add_taskreviewer_many_to_many_table_for_.py`
- `76a36e71cb1c_add_team_model_and_task_team_assignments.py` (NEW)

### Translations
- `translations.py` — Added team-related translations

---

## Notes

- Using Alembic for database migrations (Flask-Migrate wrapper)
- Local Flask-Login auth for MVP, OIDC planned for Phase 2
- PostgreSQL recommended for production, SQLite for development
- Evidence files stored locally in uploads/ folder
- Multi-reviewer requires ALL reviewers to approve before task is approved
- ANY reviewer rejection immediately rejects the entire task

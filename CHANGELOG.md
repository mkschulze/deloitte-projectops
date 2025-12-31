# Changelog

All notable changes to the Deloitte TaxOps Calendar will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.2.1] - 2025-12-31

### 🎨 UI/UX Improvements

#### Changed
- **Task List**: Added stats cards (Total, Overdue, Due Soon, Completed) with color-coded borders
- **Task List**: Dark table header for better visual hierarchy
- **Dashboard**: Dark card headers for all charts with Deloitte green icons
- **Dashboard**: "My Tasks" section with dark header styling
- **Task Detail**: Fixed button wrapping issue with `flex-nowrap` and `text-nowrap`
- **Task Detail**: Changed "Wiederherstellen" to "Aktivieren" (shorter, fits inline)
- **User Management**: Added German translations for roles (Prüfer, Bearbeiter, Nur Lesen)

#### Fixed
- Button layout issue on task detail page where long text caused vertical stacking

---

## [1.2.0] - 2025-12-31

### 🛠️ Phase J: Template Builder UI (Full Form Builder)

This release adds comprehensive template/preset management with enhanced UI, custom fields, and improved import/export.

#### Added
- **C1: Enhanced Preset Form**
  - Live preview panel showing task card with current form values
  - Recurrence wizard with visual calendar date preview
  - Tax type search dropdown with filtering
  - Due date calculator showing next occurrences

- **C2: Visual Category Tree**
  - 3 views: Tree (grouped by tax type), Card (grid), Table (classic)
  - Drag & drop reordering with SortableJS
  - Bulk selection with floating action bar
  - Quick edit slide-out panel
  - View toggle with persistence in localStorage

- **C3: Custom Fields**
  - `PresetCustomField` model (name, labels, type, required, options, conditions)
  - `TaskCustomFieldValue` model for storing field values on tasks
  - `CustomFieldType` enum (text, textarea, number, date, select, checkbox)
  - Custom Fields UI section in preset form
  - Modal dialog for field creation/editing
  - API endpoints: `GET/POST /api/preset-fields`, `PUT/DELETE /api/preset-fields/<id>`
  - Template variables support: `{{year}}`, `{{entity}}`, `{{quarter}}`, etc.
  - Conditional visibility (show field based on other field values)

- **C4: Import/Export Enhancement**
  - Enhanced JSON export includes custom fields
  - JSON import handles enhanced format with custom fields
  - Import counts imported fields in success message

- **Deloitte Color Scheme Enhancement**
  - Page headers with Deloitte gradient
  - View toggle buttons with proper colors
  - Filter cards with styled inputs
  - Enhanced table view with dark green header
  - Action buttons with hover states

#### Fixed
- Added missing `make_response` import for export route
- Fixed `User.display_name` to `User.name` in preset routes
- Fixed checkbox styling in preset list
- Fixed search input minimum width
- Fixed card text overflow handling
- Fixed view toggle icon visibility when active

---

## [1.1.0] - 2025-12-31

### 🗄️ Phase I: Archival & Soft-Delete

This release adds comprehensive archival functionality for task lifecycle management.

#### Added
- **Soft-delete for tasks** - Tasks can now be archived instead of permanently deleted
  - `is_archived`, `archived_at`, `archived_by_id`, `archive_reason` fields
  - `Task.archive(user, reason)` and `Task.restore()` methods
- **Archive routes** - Single and bulk archive/restore operations
  - `POST /tasks/<id>/archive` - Archive single task with optional reason
  - `POST /tasks/<id>/restore` - Restore archived task
  - `POST /api/tasks/bulk-archive` - Bulk archive selected tasks
  - `POST /api/tasks/bulk-restore` - Bulk restore selected tasks
- **Archive view page** (`/tasks/archive`) with filters and pagination
- **Archive UI components**
  - Archive button with reason modal in task detail
  - Restore button for archived tasks (admin/manager only)
  - Bulk archive functionality in task list
  - Bulk restore functionality in archive view
  - Navigation dropdown for tasks with archive link
  - Archived banner on task detail page
- **Translations** for archive features (German and English)
- **Database migration** for archive fields

#### Changed
- Dashboard, task list, and calendar views now exclude archived tasks
- Tasks navigation changed from single link to dropdown menu

#### Fixed
- Status badge translations in popovers now show localized labels instead of raw status keys

---

## [1.0.0] - 2025-12-31

### 🎉 Initial Release

First production-ready release of the Deloitte TaxOps Calendar with complete MVP features and Phase A-H enhancements.

### Core Features (MVP)

#### Task Management
- Full CRUD operations for tax compliance tasks
- Multi-stage approval workflow (Draft → Submitted → In Review → Approved → Completed)
- Task status tracking with visual indicators
- Due date management with overdue/due-soon warnings
- Task filtering and search functionality

#### Evidence Management
- File upload support (PDF, Office documents, images)
- External link references
- Inline preview for PDFs and images
- Secure file download

#### Comments System
- Discussion threads on tasks
- User avatars and timestamps
- Owner/admin-only comment deletion

#### Multi-Reviewer Approval
- Assign multiple reviewers to tasks
- Individual reviewer approve/reject actions
- Progress bar showing approval status
- Auto-transition when all reviewers approve
- Immediate rejection if any reviewer rejects

#### Team Management
- Create and manage user teams
- Team-based task ownership and review
- Multi-select member assignment
- Color-coded team indicators

#### Calendar Views
- Month view with task indicators
- Year overview with status colors
- Hover previews with task details
- Quick navigation to task details

#### Admin Panel
- User management with role assignment
- Entity management with hierarchy support
- Tax type management
- Task preset management (templates)
- Audit logging

### Phase A: In-App Notifications
- Real-time WebSocket notifications via Flask-SocketIO
- Notification bell with unread count in navbar
- Dropdown notification list
- Mark as read / Mark all as read
- Notification triggers for task assignments, status changes, comments

### Phase B: Bulk Operations
- Select multiple tasks with checkboxes
- Select all toggle
- Bulk status change
- Bulk owner reassignment
- Bulk delete with confirmation

### Phase C: Excel/PDF Export
- Task list Excel export with filters
- Individual task PDF export with Deloitte branding
- Status summary Excel report with multiple sheets
- Deloitte color scheme in exports

### Phase D: Calendar Sync (iCal)
- Personal iCal feed URL per user
- Secure token-based subscription
- Task deadlines as calendar events
- Reminder alarms (1 week, 1 day before)
- Token regeneration for security
- Instructions for Outlook, Google Calendar, Apple Calendar

### Phase E: Email Notifications
- SMTP email service (configurable provider)
- HTML email templates with Deloitte branding
- Task assignment notifications
- Status change notifications
- Due reminder emails (CLI command)
- Comment notifications
- User email preferences (master toggle + per-type settings)
- CLI: `flask send_due_reminders --days=7`

### Phase F: Dashboard Charts
- Tasks by status (doughnut chart)
- Tasks by month (stacked bar chart with year selector)
- Team workload (horizontal bar chart)
- Chart.js integration via CDN
- Responsive chart containers

### Phase G: Entity Scoping
- Entity access permissions (view, edit, manage)
- Entity hierarchy inheritance
- User-entity permission management
- Entity-user permission management
- Access level enforcement in queries
- Admin/Manager bypass for all entities

### Phase H: Recurring Tasks (RRULE)
- TaskPreset recurrence configuration
- Frequency options: Monthly, Quarterly, Semi-Annual, Annual, Custom RRULE
- Day offset for due date calculation
- Default entity and owner assignment
- CLI: `flask generate-recurring-tasks --year --dry-run`
- Recurring task badge in task detail
- RRULE parsing via python-dateutil

### Internationalization
- German (default) and English language support
- Language toggle in navigation
- Session-based language storage
- Bilingual form labels and validation messages

### Technical

#### Dependencies
- Flask 2.x
- Flask-SQLAlchemy
- Flask-Migrate (Alembic)
- Flask-Login
- Flask-WTF
- Flask-SocketIO + eventlet
- openpyxl
- WeasyPrint
- python-dateutil
- icalendar

#### Database
- SQLite (development)
- PostgreSQL compatible (production)

#### Security
- Password hashing (Werkzeug)
- CSRF protection
- Role-based access control
- Secure file uploads
- Token-based calendar feeds

---

## [Unreleased]

### Planned for Future Releases

#### Projektmanagement-Modul (Jira-ähnlich)
- Blueprint-Refactoring for modular architecture
- Project model with issue keys (TAX-1, TAX-2)
- Issue types: Epic, Story, Task, Bug, Sub-Task
- Kanban board with drag & drop
- Backlog and Sprint management

#### Future Considerations
- OIDC/Entra ID SSO integration
- MS Teams notifications
- Virus scanning for uploads
- Template builder UI
- Advanced compliance reports

---

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 1.1.0 | 2025-12-31 | Phase I: Archival & Soft-Delete |
| 1.0.0 | 2025-12-31 | Initial production release with MVP + Phase A-H |

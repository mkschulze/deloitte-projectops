# Changelog

All notable changes to the Deloitte TaxOps Calendar will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

#### Phase I: Archival & Soft-Delete
- Soft-delete for tasks (is_archived flag)
- Archive view for completed tasks
- Retention policy settings
- Bulk archive by date range
- Restore from archive

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
| 1.0.0 | 2025-12-31 | Initial production release with MVP + Phase A-H |

# 🚀 Deloitte ProjectOps

> **Enterprise Project & Task Management Platform** — A centralized platform for managing projects, tasks, and deadlines across teams and organizations with multi-tenant support.

![Version](https://img.shields.io/badge/version-1.19.0-blue)
![Tests](https://img.shields.io/badge/Tests-536%20passed-brightgreen?logo=pytest)
![Coverage](https://img.shields.io/badge/Coverage-43%25-yellow?logo=codecov)
![Flask](https://img.shields.io/badge/Flask-3.x-green?logo=flask)
![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple?logo=bootstrap)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.x-orange)
![License](https://img.shields.io/badge/License-Proprietary-red)

---

## 🎯 Purpose

The **Deloitte ProjectOps** is a web application designed to centralize project and task management for enterprises. It provides a single platform to:

- **Plan** projects with flexible methodologies (Scrum, Kanban, Waterfall, Custom)
- **Assign** tasks to responsible owners and multiple reviewers
- **Track** progress against due dates with visual status indicators
- **Review** submitted work through a structured multi-reviewer approval process
- **Document** compliance with file uploads and audit trails

---

## ✨ Features

### Core Functionality

| Feature | Description |
|---------|-------------|
| 📊 **Dashboard** | KPI cards, Chart.js visualizations (status pie, monthly bar, team workload) |
| 📋 **Task Management** | Full CRUD with status workflow, bulk operations, filters, and search |
| 📅 **Calendar Views** | Month and year views with color-coded task indicators and previews |
| 👥 **Multi-Reviewer Approval** | Assign multiple reviewers who must all approve before completion |
| 👨‍👩‍👧‍👦 **Team Management** | Create teams, assign tasks to teams, team-based access control |
| 📎 **Evidence Management** | Upload files (PDF, Office, images) and add links as evidence |
| 💬 **Comments** | Discussion threads on tasks with user avatars |
| 📝 **Audit Logging** | Complete activity history for compliance |
| 🏢 **Entity Management** | Manage legal entities with hierarchies and user permissions |
| 🔐 **Role-Based Access** | Admin, Manager, Reviewer, Preparer, Read-only roles |
| 🌍 **Internationalization** | German (default) and English language support |

### Project Management Module

| Feature | Description |
|---------|-------------|
| 📁 **Multi-Methodology** | Scrum, Kanban, Waterfall, or Custom workflows |
| 🏃 **Iterations/Sprints** | Time-boxed iterations with burndown charts |
| 📋 **Kanban Boards** | Drag-and-drop issue management with WIP limits |
| 🎯 **Issue Tracking** | Full lifecycle management with custom workflows |
| 🔀 **Workflow Transitions** | Configurable status transitions per methodology |
| 📊 **Reports & Analytics** | Velocity, burndown, cumulative flow diagrams |
| 🏷️ **Labels & Priorities** | Customizable categorization |
| ⏱️ **Work Logging** | Time tracking with estimates vs actuals |

### Multi-Tenancy & Enterprise Features

| Feature | Description |
|---------|-------------|
| 🏢 **Multi-Tenant Architecture** | Complete client separation with tenant-specific data |
| 👔 **Per-Tenant Roles** | Admin, Manager, Member, Viewer roles per tenant |
| 🔑 **API Keys** | Per-tenant API access for integrations |
| 📤 **Compliance Export** | Full JSON/Excel export for audits (10+ sheets) |
| 🔔 **Real-time Notifications** | WebSocket notifications via Flask-SocketIO |
| ⚡ **Bulk Operations** | Select multiple tasks for status change, reassignment, deletion |
| 📆 **Calendar Sync (iCal)** | Subscribe to personal calendar feed in Outlook/Google/Apple |
| 📧 **Email Notifications** | Task assignment, status change, comment, due reminder emails |

### Multi-Stage Approval Workflow

```
┌─────────┐     ┌───────────┐     ┌───────────┐     ┌──────────┐     ┌───────────┐
│  Draft  │────▶│ Submitted │────▶│ In Review │────▶│ Approved │────▶│ Completed │
└─────────┘     └───────────┘     └─────┬─────┘     └──────────┘     └───────────┘
                                        │
                           All Reviewers Must Approve
                                        │
                      ┌─────────────────┴─────────────────┐
                      │  If ANY Reviewer Rejects → Rework │
                      └───────────────────────────────────┘
```

### Task Presets

Pre-defined task templates for common tax compliance tasks:
- **Aufgaben** (Tasks): USt-Voranmeldung, Lohnsteuer-Anmeldung, etc.
- **Anträge** (Applications): Fristverlängerungen, Steuerbefreiungen, etc.

---

## 🖼️ Screenshots

### Dashboard
- KPI cards with real-time statistics
- "My Tasks" panel for quick access
- Overdue warnings

### Calendar View
- Month/Year navigation
- Color-coded status indicators
- Hover previews with task details

### Task Detail
- Tabbed interface (Overview, Evidence, Comments, Audit Log)
- Multi-reviewer approval panel with progress bar
- File upload with preview modal

---

## 🛠️ Tech Stack

### Backend
| Component | Technology |
|-----------|------------|
| Framework | Flask 3.x |
| ORM | SQLAlchemy + Flask-SQLAlchemy |
| Migrations | Alembic (Flask-Migrate) |
| Authentication | Flask-Login |
| Real-time | Flask-SocketIO + eventlet |
| Excel Processing | openpyxl |
| PDF Export | WeasyPrint |
| Calendar | icalendar + python-dateutil |

### Frontend
| Component | Technology |
|-----------|------------|
| CSS Framework | Bootstrap 5.3 |
| Icons | Bootstrap Icons + Deloitte Icons |
| Charts | Chart.js 4.x |
| Templating | Jinja2 |
| JavaScript | Vanilla JS + Socket.IO Client |

### Database
| Environment | Database |
|-------------|----------|
| Development | SQLite |
| Production | PostgreSQL (recommended) |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- Pipenv (`pip install pipenv`)
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/mkschulze/deloitte-projectops.git
cd deloitte-projectops

# Install dependencies
pipenv install

# Activate virtual environment
pipenv shell

# Create .env file
cat > .env << EOF
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-super-secret-key-change-in-production
EOF

# Initialize database
flask initdb

# Create admin user
flask createadmin

# Load sample data (optional)
flask seed

# Run development server
flask run
```

### Access the Application

Open http://127.0.0.1:5000 in your browser.

**Test Credentials (from seed command):**

| Email | Password | Role |
|-------|----------|------|
| admin@deloitte.de | password | Admin |
| manager@deloitte.de | password | Manager |
| reviewer@deloitte.de | password | Reviewer |
| preparer@deloitte.de | password | Preparer |

---

## 📁 Project Structure

```
deloitte-projectops/
├── app.py                  # Main application (~3900 lines)
├── models.py               # SQLAlchemy models (~850 lines)
├── services.py             # Business logic services (~650 lines)
├── config.py               # Configuration classes
├── translations.py         # i18n dictionary (DE/EN)
├── init_db.py              # Database initialization
├── Pipfile                 # Dependencies
├── requirements.txt        # Pip requirements (generated)
│
├── instance/               # Instance-specific files
│   └── app.db              # SQLite database
│
├── migrations/             # Alembic migrations
│   └── versions/           # Migration scripts
│
├── static/                 # Static assets
│   ├── Deloitte-Master-Logo/
│   ├── Deloitte Special Case Web Icons/
│   └── favicon/
│
├── templates/              # Jinja2 templates
│   ├── base.html           # Master layout
│   ├── dashboard.html      # Main dashboard with charts
│   ├── calendar.html       # Month calendar
│   ├── calendar_year.html  # Year calendar
│   ├── tasks/              # Task templates
│   ├── admin/              # Admin templates
│   └── errors/             # Error pages
│
├── uploads/                # User uploads (evidence files)
│   └── task_*/             # Per-task folders
│
└── docs/                   # Memory Bank documentation
    ├── technicalConcept.md
    ├── techContext.md
    ├── systemPatterns.md
    ├── productContext.md
    ├── progress.md
    └── activeContext.md
```

---

## 🗄️ Database Models

### Core Models

| Model | Purpose |
|-------|---------|
| `Tenant` | Multi-tenant client separation |
| `TenantMembership` | Per-tenant roles and access |
| `User` | User accounts with roles and permissions |
| `Project` | Projects with methodology configuration |
| `Issue` | Issue/task tracking with workflows |
| `Sprint` | Iterations/phases for time-boxed work |
| `Entity` | Legal entities/subsidiaries (Gesellschaften) |
| `Task` | Calendar items with status |
| `TaskReviewer` | Multi-reviewer assignments with approval tracking |
| `Team` | Team groupings with members |
| `Comment` | Discussion threads |
| `AuditLog` | Activity logging |

### Task Status Flow

| Status | Color | Description |
|--------|-------|-------------|
| `draft` | Gray | Task created, not started |
| `submitted` | Blue | Submitted for review |
| `in_review` | Teal | Under reviewer examination |
| `approved` | Green | All reviewers approved |
| `completed` | Green | Task finished |
| `rejected` | Red | Returned for rework |

---

## 🔐 Role-Based Access Control

| Role | Permissions |
|------|-------------|
| **Admin** | Full access to all features and settings |
| **Manager** | Can assign tasks, view all entities, run reports |
| **Reviewer** | Can review and approve/reject tasks |
| **Preparer** | Can work on assigned tasks, upload evidence |
| **Read-only** | View-only access to task status and evidence |

---

## 🌐 API Routes

### Main Routes

| Route | Method | Description |
|-------|--------|-------------|
| `/` | GET | Landing page |
| `/dashboard` | GET | Main dashboard |
| `/tasks` | GET | Task list with filters |
| `/tasks/<id>` | GET | Task detail |
| `/tasks/new` | GET, POST | Create task |
| `/tasks/<id>/edit` | GET, POST | Edit task |
| `/tasks/<id>/status` | POST | Change status |
| `/tasks/<id>/reviewer-action` | POST | Reviewer approve/reject |
| `/calendar` | GET | Month calendar |
| `/calendar/year` | GET | Year calendar |

### Admin Routes

| Route | Method | Description |
|-------|--------|-------------|
| `/admin` | GET | Admin dashboard |
| `/admin/entities` | GET | Entity list |
| `/admin/tax-types` | GET | Tax types |
| `/admin/users` | GET | User management |
| `/admin/presets` | GET | Task presets |

---

## 🧪 Development

### Database Migrations

```bash
# Create migration after model changes
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade

# Rollback one version
flask db downgrade
```

### CLI Commands

```bash
flask initdb                # Initialize database tables
flask createadmin           # Create admin user interactively
flask seed                  # Load sample data
flask loadpresets           # Load task presets from JSON
flask send_due_reminders    # Send due reminder emails (--days=7)
flask generate-recurring-tasks  # Generate tasks from presets (--year, --dry-run)
```

---

## 📋 Roadmap

### ✅ Completed (v1.12.0)

- [x] Multi-tenant architecture with client separation
- [x] Project Management Module (Scrum, Kanban, Waterfall, Custom)
- [x] Methodology-agnostic terminology
- [x] Configurable workflow transitions
- [x] Kanban boards with drag-and-drop
- [x] Sprint/Iteration management with reports
- [x] User authentication with Flask-Login
- [x] Task CRUD with multi-stage workflow
- [x] Multi-reviewer approval system
- [x] Team management and assignment
- [x] Calendar views (month/year)
- [x] Evidence upload and preview
- [x] Real-time WebSocket notifications
- [x] Internationalization (DE/EN)
- [x] Compliance export (JSON/Excel)

### 🔜 Planned (Future Releases)

- [ ] OIDC/Entra ID SSO integration
- [ ] MS Teams notifications
- [ ] Advanced analytics dashboard
- [ ] Template builder UI
- [ ] Mobile-responsive improvements

---

## 🎨 Deloitte Branding

The application uses the official **Deloitte 2024 Color Palette**:

| Color | CSS Variable | Usage |
|-------|--------------|-------|
| Deloitte Green | `--dtt-green` | Primary, success states |
| Danger Red | `--dtt-danger-red` | Overdue, errors |
| Warning Orange | `--dtt-warning-orange` | Due soon |
| Blue | `--dtt-sec-blue-4` | Submitted status |
| Teal | `--dtt-sec-teal-6` | In review status |

---

## 📄 License

This project is proprietary software developed for Deloitte. All rights reserved.

---

## 👥 Contributors

- Deloitte Tax & Legal Technology Team

---

## 📞 Support

For questions or support, contact the Deloitte ProjectOps team.

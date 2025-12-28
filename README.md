# 📅 Deloitte TaxOps Calendar

> **Tax Compliance Calendar & Deadline Tracking** — A centralized platform for managing tax compliance deadlines across entities and tax types.

![Flask](https://img.shields.io/badge/Flask-2.x-green?logo=flask)
![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple?logo=bootstrap)
![License](https://img.shields.io/badge/License-Proprietary-red)

---

## 🎯 Purpose

The **Deloitte TaxOps Calendar** is a web application designed to centralize tax compliance deadline management for enterprises. It provides a single platform to:

- **Plan** annual tax compliance calendars with all relevant deadlines
- **Assign** tasks to responsible owners and multiple reviewers
- **Track** progress against due dates with visual status indicators
- **Review** submitted work through a structured multi-reviewer approval process
- **Evidence** compliance with document uploads and audit trails

---

## ✨ Features

### Core Functionality

| Feature | Description |
|---------|-------------|
| 📊 **Dashboard** | KPI cards showing overdue, due soon, in review, and completed tasks |
| 📋 **Task Management** | Full CRUD with status workflow, filters, and search |
| 📅 **Calendar Views** | Month and year views with color-coded task indicators |
| 👥 **Multi-Reviewer Approval** | Assign multiple reviewers who must all approve before completion |
| 📎 **Evidence Management** | Upload files (PDF, Office, images) and add links as evidence |
| 💬 **Comments** | Discussion threads on tasks with user avatars |
| 📝 **Audit Logging** | Complete activity history for compliance |
| 🏢 **Entity Management** | Manage legal entities/subsidiaries with hierarchies |
| 🔐 **Role-Based Access** | Admin, Manager, Reviewer, Preparer, Read-only roles |
| 🌍 **Internationalization** | German (default) and English language support |

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
| Framework | Flask 2.x |
| ORM | SQLAlchemy + Flask-SQLAlchemy |
| Migrations | Alembic (Flask-Migrate) |
| Authentication | Flask-Login |
| Excel Processing | openpyxl |

### Frontend
| Component | Technology |
|-----------|------------|
| CSS Framework | Bootstrap 5.3 |
| Icons | Bootstrap Icons + Deloitte Icons |
| Templating | Jinja2 |
| JavaScript | Vanilla JS |

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
git clone https://github.com/deloitte/deloitte-taxops-calendar.git
cd deloitte-taxops-calendar

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
deloitte-taxops-calendar/
├── app.py                  # Main application (~1700 lines)
├── models.py               # SQLAlchemy models (7 models + enums)
├── config.py               # Configuration classes
├── translations.py         # i18n dictionary (DE/EN)
├── init_db.py              # Database initialization
├── Pipfile                 # Dependencies
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
│   ├── dashboard.html      # Main dashboard
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
| `User` | User accounts with roles and permissions |
| `Entity` | Legal entities/subsidiaries (Gesellschaften) |
| `TaxType` | Tax categories (KSt, USt, GewSt, etc.) |
| `TaskTemplate` | Reusable task definitions |
| `Task` | Individual calendar items with status |
| `TaskReviewer` | Multi-reviewer assignments with approval tracking |
| `TaskEvidence` | File uploads and links |
| `Comment` | Discussion threads |
| `TaskPreset` | Pre-defined task templates |
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
flask initdb      # Initialize database tables
flask createadmin # Create admin user interactively
flask seed        # Load sample data
flask loadpresets # Load task presets from JSON
```

---

## 📋 Roadmap

### ✅ Completed (MVP)

- [x] User authentication with Flask-Login
- [x] Entity and Tax Type management
- [x] Task CRUD with multi-stage workflow
- [x] Multi-reviewer approval system
- [x] Calendar views (month/year)
- [x] Evidence upload and preview
- [x] Comments and audit logging
- [x] Task presets from JSON
- [x] Internationalization (DE/EN)

### 🔜 Planned (Phase 2)

- [ ] OIDC/Entra ID SSO integration
- [ ] Email/Teams notifications
- [ ] Excel import/export
- [ ] Advanced reports and dashboards
- [ ] RRULE-based recurring tasks
- [ ] API for external integrations

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

For questions or support, contact the Deloitte TaxOps team.

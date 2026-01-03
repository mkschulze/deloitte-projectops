# Active Context

> Current session state for Deloitte ProjectOps development
> 
> **Purpose:** This file captures the active working context so development can continue seamlessly after context resets.

---

## Session Information

**Date:** 2026-01-03 (Session 14)  
**Last Action:** PM-11 Methodology-Agnostic Terminology abgeschlossen  
**Status:** MVP Complete + Phase A-J + PM-0 bis PM-11 + UI Redesign
**Version:** 1.12.0

---

## Current State

### ✅ What Was Accomplished (Session 14)

1. **PM-11: Methodology-Agnostic Terminology** (Complete)

   #### Neutrale URL-Pfade
   - `/sprints/` → `/iterations/` (neutral für alle Methodologien)
   - `/issues/` → `/items/` (neutral für alle Methodologien)
   - Template-Ordner umbenannt: `issues/` → `items/`, `sprints/` → `iterations/`
   - Alle `url_for()` Aufrufe und Route-Endpunkte aktualisiert
   
   #### Dynamische Terminologie
   - METHODOLOGY_CONFIG erweitert mit `issue` / `issue_plural` Keys
   - Alle 4 Methodologien haben vollständige Terminologie (DE/EN):
     - Scrum: Issue/Issues
     - Kanban: Aufgabe/Aufgaben (DE), Item/Items (EN)
     - Waterfall: Aktivität/Aktivitäten (DE), Activity/Activities (EN)
     - Custom: Eintrag/Einträge (DE), Item/Items (EN)
   
   #### Templates aktualisiert
   - Projektübersicht: "Neues Issue" → "Neue Aktivität" (Waterfall)
   - Projektübersicht: "Alle Issues" → "Alle Aktivitäten"
   - Projektübersicht: "Issue-Typen" → "Aktivität-Typen"
   - Iteration-Report: Burndown → Fortschrittsdiagramm, Velocity → Durchsatz
   - Item-Formular: Dynamische Placeholders und Tipps
   - Iteration-Formular: Timeline-Vorschau mit existierenden Iterationen

### ✅ Previously Completed (Session 13)

1. **PM-10: Workflow Transitions** (Complete)
   - Tab-Navigation in Workflow Settings
   - Interaktive Transition-Matrix
   - Frontend/Backend Validation

---

## Project State

### Database Tables

```
user                  ✅ Extended with roles, email preferences, calendar token
audit_log             ✅ With action types
entity                ✅ With group hierarchy
tax_type              ✅ Tax categories
task_template         ✅ Reusable templates
task                  ✅ Core tasks with status, teams, preset_id, is_recurring_instance
task_reviewer         ✅ Multi-reviewer tracking
task_evidence         ✅ Files and links
comment               ✅ Discussion threads
task_preset           ✅ Extended with recurrence fields
reference_application ✅ Anträge library
entity_user_access    ✅ Association table
team                  ✅ User grouping
team_members          ✅ Team-User many-to-many
notification          ✅ In-app notifications
user_entity           ✅ Entity access with levels
```

### Key Models

| Model | Purpose |
|-------|---------|
| `User` | User accounts with roles, preferences |
| `Task` | Core task with workflow, teams, recurrence |
| `TaskPreset` | Predefined templates with recurrence config |
| `Team` | User grouping with members |
| `TaskReviewer` | Multi-reviewer approval tracking |
| `Notification` | In-app notification system |
| `UserEntity` | Entity access permissions |

### Routes (app.py ~1850 lines)

| Category | Routes | Description |
|----------|--------|-------------|
| Auth | 3 | login, logout, set_language |
| Dashboard | 1 | Main dashboard |
| Tasks | 12 | CRUD, status, evidence, comments |
| Calendar | 3 | Month, year, week views |
| Admin | 19 | Users, entities, tax types, teams, presets |
| CLI | 4 | initdb, createadmin, seed, loadpresets |

---

## Multi-Reviewer Workflow

### How It Works

1. **Assignment:** When creating/editing a task, select multiple reviewers via multi-select dropdown
2. **Tracking:** Each reviewer has their own `TaskReviewer` record with approval status
3. **Review:** When task is "in_review", each reviewer sees their own approval panel
4. **Approval:** Clicking "Approve" marks that reviewer as approved with timestamp
5. **Rejection:** Clicking "Reject" immediately rejects the entire task
6. **Completion:** When ALL reviewers approve, task auto-transitions to "approved"

### Key Methods (Task model)

```python
task.set_reviewers([user_ids])      # Assign multiple reviewers
task.is_reviewer(user)               # Check if user is a reviewer
task.get_reviewer_status(user)       # Get TaskReviewer record
task.approve_by_reviewer(user, note) # Mark user as approved
task.reject_by_reviewer(user, note)  # Mark user as rejected
task.all_reviewers_approved()        # Check if all approved
task.any_reviewer_rejected()         # Check if any rejected
task.get_approval_count()            # Returns (approved, total) tuple
```

---

## Team Management

### How It Works

1. **Create Teams:** Admins can create teams with name, description, color, and optional manager
2. **Assign Members:** Multi-select users to add as team members
3. **Task Assignment:** Tasks can be assigned to:
   - Individual owner (owner_id) OR owner team (owner_team_id)
   - Individual reviewers (TaskReviewer) AND/OR reviewer team (reviewer_team_id)
4. **Access Control:** `is_reviewer()` checks both direct assignment AND team membership

### Key Methods (Task model)

```python
task.owner_team              # Get owner Team object
task.reviewer_team           # Get reviewer Team object
task.is_reviewer(user)       # Check direct OR team membership
task.is_reviewer_via_team(user)  # Check team membership only
task.get_owner_display()     # Returns user or team name
task.is_assigned_to_user(user)   # Check any assignment
task.get_all_assigned_users()    # All users via direct + teams
```

### Key Methods (Team model)

```python
team.add_member(user)        # Add user to team
team.remove_member(user)     # Remove user from team
team.is_member(user)         # Check membership
team.get_member_count()      # Count members
```

---

## File Structure

```
deloitte-projectops-calendar/
├── app.py                  # ~3100 lines - All routes + CLI commands
├── models.py               # ~850 lines - All models
├── services.py             # ~650 lines - Business logic services
├── config.py               # Configuration
├── translations.py         # i18n (DE/EN)
│
├── templates/
│   ├── base.html           # Master layout with navbar + notification bell
│   ├── dashboard.html      # KPI cards, my tasks, Chart.js charts
│   ├── calendar.html       # Month view with popovers
│   ├── calendar_year.html  # Year view with popovers
│   ├── profile_notifications.html  # Email preferences
│   ├── calendar_sync.html  # iCal subscription instructions
│   ├── tasks/
│   │   ├── list.html       # Filterable list with bulk ops, preview
│   │   ├── detail.html     # Tabs, evidence, comments, recurring badge
│   │   └── form.html       # Create/edit with multi-reviewer
│   └── admin/
│       ├── presets.html    # Preset management
│       ├── preset_form.html # With recurrence settings
│       ├── teams.html      # Team management
│       └── team_form.html  # Team create/edit
│
├── uploads/                # Evidence files
│   └── task_*/             # Per-task folders
│
├── data/                   # JSON data files
│   ├── steuerarten_aufgaben.json
│   └── Antraege.json
│
└── docs/                   # Memory Bank
    ├── progress.md         # Development checklist
    ├── activeContext.md    # Current session state
    ├── technicalConcept.md # Architecture
    ├── techContext.md      # Tech stack
    ├── systemPatterns.md   # Design patterns
    └── productContext.md   # Product requirements
```

---

## Test Credentials

| Email | Password | Role |
|-------|----------|------|
| admin@deloitte.de | password | admin |
| manager@deloitte.de | password | manager |
| reviewer@deloitte.de | password | reviewer |
| preparer@deloitte.de | password | preparer |

---

## CLI Commands

| Command | Purpose |
|---------|---------|
| `flask initdb` | Initialize database tables |
| `flask createadmin` | Create admin user |
| `flask seed` | Seed sample data |
| `flask loadpresets` | Load presets from JSON files |
| `flask send_due_reminders --days=7` | Send reminder emails |
| `flask generate-recurring-tasks --year --dry-run` | Generate tasks from presets |

---

## App URLs

| URL | Purpose |
|-----|---------|
| `/` | Landing page |
| `/login` | Login form |
| `/dashboard` | Main dashboard with KPIs + charts |
| `/tasks` | Task list with filters + bulk operations |
| `/tasks/new` | Create new task |
| `/tasks/<id>` | Task detail (tabs: overview, evidence, comments, audit) |
| `/tasks/<id>/edit` | Edit task |
| `/calendar` | Month calendar |
| `/calendar/year` | Year calendar |
| `/calendar/feed/<token>.ics` | iCal feed (subscriptions) |
| `/profile/notifications` | Email preferences |
| `/profile/calendar-sync` | Calendar sync settings |
| `/admin` | Admin dashboard |
| `/admin/entities` | Entity management |
| `/admin/entities/<id>/users` | Entity user permissions |
| `/admin/users/<id>/entities` | User entity permissions |
| `/admin/tax-types` | Tax type management |
| `/admin/teams` | Team management |
| `/admin/presets` | Task preset management (with recurrence) |

---

## Next Steps (If Continuing Development)

### Remaining Project Management Phases
1. **Phase PM-4:** Backlog (Priorisierte Issue-Liste, Drag & Drop Ranking)
2. **Phase PM-5:** Sprint-Management (Sprint starten/beenden, Sprint-Board)
3. **Phase PM-6:** Kommentare, Attachments, Links
4. **Phase PM-7:** Epics & Progress-Tracking
5. **Phase PM-8:** Suche & Filter (erweitert)
6. **Phase PM-9:** Charts (Burndown, Velocity, Cumulative Flow)
7. **Phase PM-10:** Konfigurierbare Workflows (Workflow-Designer)

### Future Considerations
1. OIDC/Entra ID SSO integration
2. MS Teams notifications via webhooks
3. Virus scanning for uploads
4. WebSocket Real-time Updates für Board

---

## Blockers

None currently. All Phase A-J + PM-0/PM-1/PM-2/PM-3 features are complete and functional.

---

## Technical Notes

- **MIME Type Detection:** Use `mimetypes.guess_type()` for file uploads
- **Jinja2 Limitation:** `startswith()` doesn't work in templates, use string slicing: `mime[:6] == 'image/'`
- **SQLite FK Constraints:** Must provide constraint names explicitly in migrations
- **Multi-Reviewer Query:** For SQL queries checking reviewer access, need subquery join on `task_reviewer` table
- **SortableJS:** CDN für Kanban Board Drag & Drop (Version 1.15.0)
- **marked.js:** CDN für Markdown-Rendering in Issue-Beschreibungen

---

*Last updated: 2026-01-02 Session 9*

# Active Context

> Current session state for Deloitte TaxOps Calendar development
> 
> **Purpose:** This file captures the active working context so development can continue seamlessly after context resets.

---

## Session Information

**Date:** 2025-12-31 (Session 7)  
**Last Action:** Implemented Phase I — Archival & Soft-Delete  
**Status:** MVP Complete + Phase A-I — All core features + notifications, bulk ops, exports, calendar sync, email, charts, entity scoping, recurring tasks, archival

---

## Current State

### ✅ What Was Accomplished (Session 7)

1. **Phase I: Archival & Soft-Delete** (Complete)
   - **Task Model Extended:**
     - `is_archived` — Boolean flag for soft-delete (indexed)
     - `archived_at` — DateTime when task was archived
     - `archived_by_id` — Foreign key to user who archived
     - `archive_reason` — Optional text explaining why archived
     - `archive(user, reason)` — Method to archive a task
     - `restore()` — Method to restore from archive
     - `archived_by` — Relationship to User
   
   - **Routes Added (app.py):**
     - `POST /tasks/<id>/archive` — Archive single task with reason modal
     - `POST /tasks/<id>/restore` — Restore single task from archive
     - `GET /tasks/archive` — View archived tasks with filters & pagination
     - `POST /api/tasks/bulk-archive` — Bulk archive multiple tasks
     - `POST /api/tasks/bulk-restore` — Bulk restore multiple tasks
   
   - **Views Updated:**
     - Dashboard, task list, calendar views exclude archived tasks
     - Task detail shows archived banner with info
     - Archive button in task detail (for admin/manager/owner)
     - Restore button for archived tasks (admin/manager only)
   
   - **UI Components:**
     - Archive modal with reason input
     - Archive view page (templates/tasks/archive.html)
     - Bulk archive button in task list
     - Bulk restore in archive view
     - Navigation dropdown with archive link
   
   - **Database Migration:**
     - `b4301e4eea63_add_archive_fields_to_task_model.py` applied

### ✅ Previously Completed (Sessions 1-6)

- **Phase A:** In-App Notifications (WebSocket + Flask-SocketIO)
- **Phase B:** Bulk Operations (select all, bulk status, reassign, delete)
- **Phase C:** Excel/PDF Export (task list, detail, status summary)
- **Phase D:** Calendar Sync (iCal feed with secure tokens)
- **Phase E:** Email Notifications (SMTP/SendGrid, templates, preferences)
- **Phase F:** Dashboard Charts (Chart.js — status pie, monthly bar, team workload)
- **Phase G:** Entity Scoping (access levels, hierarchy inheritance)
- **Phase H:** Recurring Tasks (RRULE)
- **MVP:** Full task lifecycle, evidence, comments, multi-reviewer, teams
     - RRULE input field for custom patterns
     - Default entity and owner selection
     - End date picker
     - Shows last generated date and task count
   
   - **Task Detail:**
     - "Wiederkehrend/Recurring" badge for generated tasks
     - Tooltip shows source preset name
   
   - **Database Migration:**
     - `c3d4e5f6g7h8_add_recurring_task_fields.py` applied

### ✅ Previously Completed (Sessions 1-5)

- **Phase A:** In-App Notifications (WebSocket + Flask-SocketIO)
- **Phase B:** Bulk Operations (select all, bulk status, reassign, delete)
- **Phase C:** Excel/PDF Export (task list, detail, status summary)
- **Phase D:** Calendar Sync (iCal feed with secure tokens)
- **Phase E:** Email Notifications (SMTP/SendGrid, templates, preferences)
- **Phase F:** Dashboard Charts (Chart.js — status pie, monthly bar, team workload)
- **Phase G:** Entity Scoping (access levels, hierarchy inheritance)
- **MVP:** Full task lifecycle, evidence, comments, multi-reviewer, teams

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
deloitte-taxops-calendar/
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

### Remaining Phases
1. **Phase I:** Archival & Soft-Delete (is_archived flag, archive view, retention)

### Future Considerations
1. OIDC/Entra ID SSO integration
2. MS Teams notifications via webhooks
3. Virus scanning for uploads
4. Template builder UI

---

## Blockers

None currently. All Phase A-H features are complete and functional.

---

## Technical Notes

- **MIME Type Detection:** Use `mimetypes.guess_type()` for file uploads
- **Jinja2 Limitation:** `startswith()` doesn't work in templates, use string slicing: `mime[:6] == 'image/'`
- **SQLite FK Constraints:** Must provide constraint names explicitly in migrations
- **Multi-Reviewer Query:** For SQL queries checking reviewer access, need subquery join on `task_reviewer` table

---

*Last updated: 2025-12-28 Session 4*

# Active Context

> Current session state for Deloitte TaxOps Calendar development
> 
> **Purpose:** This file captures the active working context so development can continue seamlessly after context resets.

---

## Session Information

**Date:** 2025-12-28 (Session 4)  
**Last Action:** Implemented Team Management System  
**Status:** MVP Complete with Teams — All core features + team-based user management

---

## Current State

### ✅ What Was Accomplished

1. **Team Management System** (Session 4 - Complete)
   - `Team` model with name, description, color, manager
   - `team_members` many-to-many association table
   - Task fields: `owner_team_id`, `reviewer_team_id`
   - Admin CRUD for teams with multi-select member assignment
   - Team selection in task create/edit forms
   - Team display in task detail view
   - `is_reviewer()` checks team membership for access control
   - Navigation link in admin menu

2. **Evidence Upload System** (Complete)
   - File upload with secure unique filenames
   - Link addition for external references
   - Preview modal for PDF, images, and text files
   - Download with proper MIME types
   - Delete functionality

3. **Comments System** (Complete)
   - Add/delete comments
   - User avatars and timestamps
   - Owner/admin-only deletion

4. **Task Presets** (Complete)
   - TaskPreset model with categories (aufgabe/antrag)
   - Admin CRUD interface
   - JSON import via `flask loadpresets`
   - Preset selection in task creation

5. **Multi-Reviewer Approval** (Complete)
   - `TaskReviewer` model with approval tracking
   - Multi-select field for reviewer assignment
   - Individual reviewer approve/reject actions
   - Progress bar showing approval status
   - Auto-transition: all approve → approved status
   - Auto-transition: any reject → rejected status

6. **UI Enhancements** (Complete)
   - Navbar with "TaxOps Calendar" app name
   - Calendar preview popovers on month/year views
   - Task list preview column with hover details
   - Color-coded audit log badges

7. **Documentation** (Complete)
   - Comprehensive README.md for GitHub
   - Updated Memory Bank documentation

---

## Project State

### Database Tables

```
user                  ✅ Extended with roles
audit_log             ✅ With action types
entity                ✅ With group hierarchy
tax_type              ✅ Tax categories
task_template         ✅ Reusable templates
task                  ✅ Core tasks with status + team fields
task_reviewer         ✅ Multi-reviewer tracking
task_evidence         ✅ Files and links
comment               ✅ Discussion threads
task_preset           ✅ Predefined task templates
reference_application ✅ Anträge library
entity_user_access    ✅ Association table
team                  ✅ NEW - User grouping
team_members          ✅ NEW - Team-User many-to-many
```

### Key Models

| Model | Lines | Purpose |
|-------|-------|---------|
| `User` | ~50 | User accounts with roles |
| `Task` | ~280 | Core task with workflow + team methods |
| `Team` | ~50 | User grouping with members |
| `TaskReviewer` | ~60 | Multi-reviewer approval tracking |
| `TaskEvidence` | ~30 | File/link attachments |
| `Comment` | ~20 | Discussion threads |
| `TaskPreset` | ~30 | Predefined task templates |

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
├── app.py                  # ~1735 lines - All routes
├── models.py               # ~650 lines - All models
├── config.py               # Configuration
├── translations.py         # i18n (DE/EN)
│
├── templates/
│   ├── base.html           # Master layout with navbar
│   ├── dashboard.html      # KPI cards, my tasks
│   ├── calendar.html       # Month view with popovers
│   ├── calendar_year.html  # Year view with popovers
│   ├── tasks/
│   │   ├── list.html       # Filterable list with preview
│   │   ├── detail.html     # Tabs, evidence, comments, reviewers
│   │   └── form.html       # Create/edit with multi-reviewer
│   └── admin/
│       ├── presets.html    # Preset management
│       └── preset_form.html
│
├── uploads/                # Evidence files
│   └── task_*/             # Per-task folders
│
├── data/                   # JSON data files
│   ├── steuerarten_aufgaben.json
│   └── Antraege.json
│
└── docs/                   # Memory Bank
    ├── progress.md         # This checklist
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

## App URLs

| URL | Purpose |
|-----|---------|
| `/` | Landing page |
| `/login` | Login form |
| `/dashboard` | Main dashboard with KPIs |
| `/tasks` | Task list with filters |
| `/tasks/new` | Create new task |
| `/tasks/<id>` | Task detail (tabs: overview, evidence, comments, audit) |
| `/tasks/<id>/edit` | Edit task |
| `/tasks/<id>/status` | Change task status |
| `/tasks/<id>/reviewer-action` | Individual reviewer approve/reject |
| `/calendar` | Month calendar |
| `/calendar/year` | Year calendar |
| `/admin` | Admin dashboard |
| `/admin/entities` | Entity management |
| `/admin/tax-types` | Tax type management |
| `/admin/teams` | Team management (NEW) |
| `/admin/teams/new` | Create team (NEW) |
| `/admin/teams/<id>` | Edit team (NEW) |
| `/admin/users` | User management |
| `/admin/presets` | Task preset management |

---

## Next Steps (If Continuing Development)

### Immediate Priorities
1. **Excel Export:** Add download button to task list
2. **Batch Operations:** Select multiple tasks for reassignment
3. **Email Notifications:** Reminder emails for due soon tasks

### Phase 2 Features
1. OIDC/Entra ID SSO integration
2. Teams notifications via webhooks
3. RRULE-based recurring task generation
4. Advanced compliance reports

---

## Blockers

None currently. MVP is complete and functional.

---

## Technical Notes

- **MIME Type Detection:** Use `mimetypes.guess_type()` for file uploads
- **Jinja2 Limitation:** `startswith()` doesn't work in templates, use string slicing: `mime[:6] == 'image/'`
- **SQLite FK Constraints:** Must provide constraint names explicitly in migrations
- **Multi-Reviewer Query:** For SQL queries checking reviewer access, need subquery join on `task_reviewer` table

---

*Last updated: 2025-12-28 Session 4*

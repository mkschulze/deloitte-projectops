# Active Context

> Current session state for Deloitte ProjectOps development
> 
> **Purpose:** This file captures the active working context so development can continue seamlessly after context resets.

---

## Session Information

**Date:** 2026-01-03 (Session 15)  
**Last Action:** Multi-Tenancy v1.12.0 + Release Automation + GitHub Rename  
**Status:** MVP Complete + Phase A-J + PM-0 bis PM-11 + Multi-Tenancy + Release Automation
**Version:** 1.12.0

---

## Current State

### ✅ What Was Accomplished (Session 15)

1. **Multi-Tenancy v1.12.0** (Complete)

   #### Tenant Infrastructure
   - `Tenant` model with slug, name, logo (base64), is_active, is_archived
   - `TenantMembership` model with per-tenant roles (admin, manager, member, viewer)
   - `TenantApiKey` model for API access per tenant
   - `tenant_id` column on all major tables (Task, Entity, Project, Issue, Sprint, Team)
   - Tenant middleware for context switching
   
   #### Super-Admin Tenant Management (`/admin/tenants/`)
   - Modern Deloitte-styled UI with gradient headers
   - Tenant list with active/archived filters and stats
   - Tenant detail page with member list, API keys, quick actions
   - Full CRUD: create, edit, archive, restore, delete
   - "Enter Tenant" to switch context as Super-Admin
   
   #### Tenant Selection (`/select-tenant`)
   - Users with multiple memberships can switch between clients
   - Modern card-based UI with Deloitte branding
   - Super-Admin section to access Tenant Management
   
   #### Compliance Export
   - JSON export of tenant data
   - Excel export with 10 sheets (Mandant, Mitglieder, Projekte, Issues, etc.)
   - Timestamped filenames for audit trail

2. **Release Automation Script** (Complete)
   - `scripts/release.py` for automated releases
   - Version updates in all files (VERSION, config.py, README.md, docs/)
   - CHANGELOG.md section generation
   - Memory Bank prompt generation for AI updates
   - Git commit and tag creation
   - Push to remote
   - `scripts/update_memory_bank.py` for AI-powered doc updates

3. **GitHub Repository Rename** (Complete)
   - Renamed from `deloitte-taxops-calendar` to `deloitte-projectops`
   - Updated all documentation URLs
   - Created v1.12.0 tag

4. **Landing Page Update** (Complete)
   - New branding: ProjectOps with rocket icon
   - Features: Projects, Kanban, Iterations, Multi-Tenancy
   - Updated hero section and feature cards

### ✅ Previously Completed (Session 14)

1. **PM-11: Methodology-Agnostic Terminology** (Complete)
   - Neutral URL paths: `/sprints/` → `/iterations/`, `/issues/` → `/items/`
   - Dynamic terminology per methodology
   - METHODOLOGY_CONFIG with issue/issue_plural keys

---

## Project State

### Database Tables

```
# Multi-Tenancy
tenant                ✅ Client/organization separation
tenant_membership     ✅ Per-tenant user roles
tenant_api_key        ✅ API access per tenant

# Core
user                  ✅ Extended with roles, email preferences, calendar token
audit_log             ✅ With action types
entity                ✅ With group hierarchy + tenant_id
category              ✅ Task categories (renamed from tax_type)
task_template         ✅ Reusable templates
task                  ✅ Core tasks with status, teams, preset_id + tenant_id
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
| `Tenant` | Multi-tenant client separation |
| `TenantMembership` | Per-tenant user roles (admin, manager, member, viewer) |
| `TenantApiKey` | API access tokens per tenant |
| `User` | User accounts with roles, preferences |
| `Project` | Projects with methodology configuration |
| `Issue` | Issue/task tracking with workflows |
| `Sprint` | Iterations/phases for time-boxed work |
| `Task` | Calendar tasks with workflow, teams, recurrence |
| `Team` | User grouping with members |
| `Entity` | Legal entities with tenant scoping |
| `Notification` | In-app notification system |

### Routes (app.py ~3900 lines)

| Category | Routes | Description |
|----------|--------|-------------|
| Auth | 3 | login, logout, set_language |
| Dashboard | 1 | Main dashboard |
| Tasks | 12 | CRUD, status, evidence, comments |
| Calendar | 3 | Month, year, week views |
| Admin | 25+ | Users, entities, categories, teams, presets, tenants |
| Tenants | 8 | CRUD, members, API keys, compliance export |
| CLI | 6 | initdb, createadmin, seed, loadpresets, due reminders, recurring tasks |

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
deloitte-projectops/
├── app.py                  # ~3900 lines - All routes + CLI commands
├── models.py               # ~1200 lines - All models incl. Multi-Tenancy
├── services.py             # ~650 lines - Business logic services
├── config.py               # Configuration
├── translations.py         # i18n (DE/EN)
│
├── admin/                  # Admin blueprints
│   └── tenants.py          # Tenant management routes
│
├── middleware/             # Request middleware
│   └── tenant.py           # Tenant context middleware
│
├── modules/                # Feature modules
│   ├── projects/           # Project management module
│   └── tasks/              # Tasks module
│
├── scripts/                # Automation scripts
│   ├── release.py          # Release automation
│   ├── update_memory_bank.py  # AI-powered doc updates
│   └── create_full_demo_data.py
│
├── templates/
│   ├── base.html           # Master layout with tenant switcher
│   ├── select_tenant.html  # Tenant selection page
│   ├── index.html          # Landing page (ProjectOps branding)
│   ├── admin/
│   │   └── tenants/        # Tenant management UI
│   └── ...
│
├── migrations/versions/
│   ├── mt001_add_multi_tenancy.py
│   └── ...
│
└── docs/                   # Memory Bank
    ├── progress.md
    ├── activeContext.md
    ├── multiTenancyDesign.md  # NEW: Multi-tenancy architecture
    └── ...
```

---

## Test Credentials

| Email | Password | Role |
|-------|----------|------|
| admin@deloitte.de | password | admin (Super-Admin) |
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
| `/` | Landing page (ProjectOps branding) |
| `/login` | Login form |
| `/select-tenant` | Tenant selection for multi-tenant users |
| `/dashboard` | Main dashboard with KPIs + charts |
| `/tasks` | Task list with filters + bulk operations |
| `/calendar` | Month calendar |
| `/calendar/year` | Year calendar |
| `/projects` | Project Management module |
| `/projects/<key>/board` | Kanban board |
| `/projects/<key>/iterations` | Iterations/Sprints |
| `/admin` | Admin dashboard |
| `/admin/tenants` | **NEW:** Tenant management (Super-Admin) |
| `/admin/tenants/<id>` | Tenant detail with members, API keys |
| `/admin/tenants/<id>/export` | Compliance export (JSON/Excel) |
| `/admin/entities` | Entity management |
| `/admin/categories` | Category management (renamed from tax-types) |
| `/admin/teams` | Team management |

---

## Next Steps (If Continuing Development)

### Future Considerations
1. OIDC/Entra ID SSO integration
2. MS Teams notifications via webhooks
3. Advanced analytics dashboard
4. Template builder UI
5. Mobile-responsive improvements

---

## Blockers

None currently. All features through v1.12.0 are complete and functional.

---

## Technical Notes

- **Multi-Tenancy:** All queries must be scoped by `tenant_id` for data isolation
- **Tenant Middleware:** `middleware/tenant.py` handles tenant context from session
- **Release Script:** `python scripts/release.py` automates version bumps, tags, and docs
- **Memory Bank Updates:** Use generated prompt in `scripts/memory_bank_update_prompt.txt`
- **SortableJS:** CDN für Kanban Board Drag & Drop (Version 1.15.0)
- **marked.js:** CDN für Markdown-Rendering in Issue-Beschreibungen

---

*Last updated: 2026-01-03 Session 15*

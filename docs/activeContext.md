# Active Context

> Current session state for Deloitte ProjectOps development
> 
> **Purpose:** This file captures the active working context so development can continue seamlessly after context resets.

---

## Session Information

**Date:** 2026-01-03 (Session 18)  
**Last Action:** Phase 3 Service Layer Tests v1.18.0  
**Status:** MVP Complete + Phase A-J + PM-0 bis PM-11 + Multi-Tenancy + Unit Tests
**Version:** 1.18.0

---

## Current State

### ✅ What Was Accomplished (Session 18)

1. **Phase 3 Service Layer Tests v1.18.0** (Complete)

   #### New Test File: `test_phase3_services.py` (62 tests)
   - **TestNotificationServiceCreate** (4 tests) - basic, with message, entity reference, actor
   - **TestNotificationServiceNotifyUsers** (4 tests) - single, multiple, deduplication, skip None
   - **TestNotificationServiceGetUnread** (3 tests) - zero, with notifications, excludes read
   - **TestExportServiceExcel** (6 tests) - empty, bytes, German/English, multiple tasks, XLSX format
   - **TestCalendarServiceToken** (5 tests) - returns string, length, uniqueness, different users, hex chars
   - **TestCalendarServiceIcal** (7 tests) - empty feed, with task, title, skip no due date, languages, user name
   - **TestEmailServiceInit** (3 tests) - without app, with app, init_app method
   - **TestEmailServiceIsEnabled** (3 tests) - false without app, false by default, true when configured
   - **TestEmailServiceProvider** (4 tests) - default smtp, without app, sendgrid, ses
   - **TestEmailServiceSendEmail** (3 tests) - disabled logs, generates text, via SMTP
   - **TestRecurrenceServicePeriodDates** (16 tests) - monthly, quarterly, semi-annual, annual frequencies
   - **TestRecurrenceServiceEdgeCases** (4 tests) - February handling, leap year, negative/zero offset

   #### Coverage Improvement
   - **services.py**: 16% → 37% (+21 percentage points)
   - **Total tests**: 548 → 598 (+50 net, 62 new tests)
   - Phase 3 target was +12%, achieved **+21%** - exceeded goal

   #### Bug Fix
   - Fixed `CalendarService.generate_ical_feed()` calling `.date()` on date object
   - Added `date` import to services.py
   - Now handles both `date` and `datetime` objects correctly

2. **Separated Memory Bank Check Script v1.17.0** (Previous Session)

2. **Release Script Enhancement v1.16.2** (Complete)

   #### 3-Phase Memory Bank Workflow
   - PHASE 1: Script displays COMPLETE content of all 7 Memory Bank files
   - PHASE 2: Pauses for manual updates with specific instructions
   - PHASE 3: Verifies all updates were made before allowing release
   - Forces AI to actually read each file before updating
   - Blocks release if any required file is missing version update

2. **Release Script Enhancement v1.16.1** (Complete)

   #### Extra Strong Memory Bank Verification
   - Individual file confirmation for each of 7 Memory Bank files
   - Final phrase confirmation: "I have read and updated all memory bank files"
   - Blocks release if any confirmation fails
   - Prevents AI from auto-confirming without actually reading each file

2. **Test Coverage Phase 2 v1.16.0** (Complete)

   #### Phase 2 Implementation
   - Added 69 comprehensive middleware and module tests
   - Total tests: 467 → 536 (+69)
   - middleware/tenant.py coverage: 28% → 98% (+70%)
   - modules/core/__init__.py: 89% → 100%
   - modules/__init__.py: 54% → 88% (+34%)

2. **Test Coverage Phase 1 v1.15.0** (Complete)

   #### Phase 1 Implementation
   - Created `.coveragerc` to exclude scripts/, migrations/, tests/, demo files
   - Added 43 new tests for User, Team, TaskReviewer, UserEntity models
   - Total tests: 424 → 467 (+43)
   - models.py coverage: 63% → 70% (+7%)
   
   #### New Test File: `test_phase1_models.py`
   - TestUserTenantMethods (13 tests)
   - TestUserCalendarToken (3 tests)
   - TestUserTeamMethods (1 test)
   - TestTeamModel (13 tests)
   - TestTaskReviewerModel (6 tests)
   - TestUserEntityModel (5 tests)
   - TestEntityAccessLevelEnum (2 tests)
   
   #### Infrastructure Updates
   - Updated conftest.py cleanup to include team_members, Entity, Task tables
   - Added entity and task fixtures for Task model testing

2. **Test Coverage Expansion v1.14.0** (Complete)

   #### Test Suite Expansion
   - Expanded from 125 to 424 tests (+299 tests)
   - Code coverage increased from 34% to 43% (+9%)
   
   #### New Test Files
   - `test_task_model.py` - 56 tests for Task, User, Tenant, Notification models
   - `test_project_methods.py` - 42 tests for Project model getters
   - `test_all_services.py` - 36 tests for all service classes
   - `test_middleware_advanced.py` - 18 tests for middleware functions
   - `test_middleware.py` - 35 tests for tenant middleware
   - `test_models_advanced.py` - Extended model tests
   - `test_project_models_advanced.py` - Project model edge cases
   - `test_services_advanced.py` - Service method testing
   - `test_modules.py` - Module system tests
   
   #### Infrastructure Improvements
   - Fixed database isolation issues in `conftest.py`
   - Added autouse `clean_db_tables` fixture for proper test cleanup
   - Resolved intermittent test failures from database state leaking
   
   #### Test Coverage Plan
   - Created `docs/testCoveragePlan.md` with roadmap to 100% coverage
   - 5-phase implementation plan with time estimates
   - Target: ~920 tests for full coverage

### ✅ Previously Completed (Session 15)

1. **Unit Test Infrastructure v1.13.0** (Complete)
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

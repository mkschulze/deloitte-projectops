# Active Context

> Current session state for Deloitte ProjectOps development
> 
> **Purpose:** This file captures the active working context so development can continue seamlessly after context resets.

---

## Session Information

**Date:** 2026-01-10 (Session 28)  
**Last Action:** Security Fixes Released (T13, T14, T17, T19, T20)  
**Status:** MVP Complete + Phase A-J + PM-0 bis PM-11 + Multi-Tenancy + Unit Tests + Security Hardening + ZAP Remediation Complete
**Version:** 1.21.7

---

## Current State

### 🔄 What Is In Progress (Session 28)

#### ZAP Penetration Test Remediation - Updated Plan

A new ZAP scan was run on 2026-01-10 (on neutral brand version at port 5000). The JSON report is at `docs/pentest/2026-01-10-ZAP-Report-.json`. The full remediation plan is at `docs/pentest/ZAP_DOM_XSS_NOTES.md`.

**🚨 NEW CRITICAL FINDING: Persistent XSS (121 instances)**

ZAP successfully stored and reflected `javascript:alert(1);` payloads via:
- Evidence link URLs (`url` parameter)
- Evidence link titles (`link_title` parameter)
- Comments/notes (`text`, `note`, `reason` parameters)
- Task/entity names (`name`, `title`, `name_de` parameters)

**Key Findings on http://127.0.0.1:5000:**

| Severity | Finding | Count | Status |
|----------|---------|-------|--------|
| 🔴 HIGH | **Persistent XSS** | 121 | 🆕 **NEW - Critical** |
| 🔴 HIGH | SQL Injection | 22 | Likely false positive (verify) |
| 🟠 MEDIUM | CSP Header Not Set | 5 | ⏳ Pending (T7) |
| 🟠 MEDIUM | Session ID in URL (Socket.IO) | 5 | 📋 Accept risk |
| 🟠 MEDIUM | SRI Missing (CDN scripts) | 5 | ✅ Partial (T9 - DOMPurify) |
| 🟡 LOW | Application Error Disclosure (500s) | 6 | ✅ Fixed (T1-T6) |
| 🟡 LOW | Server Header Leak | 1 | ⏳ Pending (T8) |

#### Remediation Progress

**✅ Completed (v1.21.7):**
- T1-T6: Added tenant guards to prevent 500 errors
- T10: SQLi verified as false positive (ORM-only usage)
- T13: URL scheme validation (`validate_external_url()` in `routes/tasks.py`)
- T14: Template href safety (defense-in-depth in `templates/tasks/detail.html`)
- T15: Template audit completed (found issues → fixed via T13/T14)
- T17: DOMPurify for markdown with SRI (`modules/projects/templates/projects/items/detail.html`)
- T19: Notification HTML escaping (`escapeHtml()` in `templates/base.html`)
- T20: Open Redirect validation (`is_safe_redirect()` in `routes/auth.py`, `routes/main.py`)

**⏳ Pending (Lower Priority):**

| Task | Description | Priority |
|------|-------------|----------|
| T7 | CSP empty nonce - check `/admin/entities/*/delete` responses | High |
| T8 | Server header leak - verify middleware covers static/errors | High |
| T9 | Add SRI to remaining CDN scripts (Chart.js, SortableJS) | Medium |
| T11 | Document accepted risks (Socket.IO sid, X-Content-Type-Options) | Low |
| T12 | Database cleanup - run `reset_and_create_demo_data.py` | Low |
| T16 | Server-side sanitization for text fields (deferred - Jinja2 auto-escapes) | Low |

#### Files Modified for Security Fixes (v1.21.7)

1. **routes/tasks.py** - `evidence_link()`, `add_comment()`, `update_status()`, `archive_task()`
2. **templates/tasks/detail.html** - Evidence link rendering, comment display
3. **templates/tasks/includes/** - Any evidence/comment includes
4. **services.py** - `create_notification()` for any HTML in notifications

---

### Previous Session Context (Session 27)

#### Files Modified (Session 27)

1. **routes/main.py**
   - Added `if not g.tenant:` guard to `/notifications` route
   - Returns redirect to tenant selection instead of 500

2. **routes/tasks.py**
   - Added 8 tenant guards across task routes
   - `/tasks`, `/tasks/archive`, `/tasks/<id>/status`, `/tasks/<id>/archive`, etc.
   - Returns 302/403/404 instead of 500

3. **modules/projects/routes.py**
   - Enhanced `project_access_required` decorator
   - Checks `g.tenant` and project tenant match
   - Returns 404 for cross-tenant access attempts

4. **admin/tenants.py**
   - Wrapped `openpyxl` import in try/except
   - Returns flash message + redirect if package missing (not 500)

5. **app.py** (from earlier session)
   - Moved `load_tenant_context`, `inject_tenant_context`, `inject_globals` registration into `create_app()`
   - Changed `inject_globals()` to use `current_app.config` instead of module-level `app`
   - Fixed function definition order (helpers before factory)

---

### 🔄 Test Fixes (Blocked - Resume After ZAP)

9 tests still failing due to tenant context issues in test fixtures.

**Root Cause:** Test fixtures use wrong session key and missing tenant setup.

**Fixes Needed:**

1. **Replace `sess['tenant_id']` → `sess['current_tenant_id']`** (12 occurrences in 6 files):
   - `tests/integration/test_presets_routes.py` (lines 57, 77)
   - `tests/integration/test_admin_routes.py` (lines 44, 64)
   - `tests/integration/test_tasks_routes.py` (lines 46, 577)
   - `tests/unit/test_app.py` (lines 39, 59)
   - `tests/integration/test_routes.py` (lines 67, 90)
   - `tests/integration/test_main_routes.py` (lines 43, 64)

2. **Add tenant context to blueprint fixtures** (`test_blueprints.py`):
   - Create `Tenant` + `TenantMembership` in `bp_logged_in_admin` / `bp_logged_in_user`
   - Set `session['current_tenant_id']` after login POST
   - Change `role='user'` → `role='preparer'` (valid UserRole)

3. **Fix test expectation** (`test_api_routes.py`):
   - `test_bulk_permanent_delete_skips_non_archived` expects 200
   - API returns 400 when any task is not archived (fail-fast)
   - Change assertion to expect 400 + error message

---

### ✅ What Was Accomplished (Session 26)

1. **Project Structure Cleanup** (Complete)

   #### Files Reorganized
   - `admin/PENTEST/` → `docs/pentest/` (security reports with docs)
   - `.rules` → repo root (better visibility, editor-agnostic)
   - `scripts/memory-bank/` created (organized memory bank scripts)

   #### Files Deleted (Deprecated)
   - `create_demo_data.py` (replaced by `scripts/demo-data/`)
   - `create_zap_user.py` (replaced by `scripts/demo-data/`)

   #### Generated Artifacts Cleaned
   - `htmlcov/`, `.coverage`, `.pytest_cache/`
   - `__pycache__/`, `*.pyc`, `.DS_Store`

   #### New Structure
   ```
   scripts/
   ├── create_modules.py
   ├── demo-data/
   ├── memory-bank/
   └── release.py
   ```

2. **Future Refactoring Plan: v2.0.0** (Documented)

   #### Application Package Pattern
   Currently, core Python files (`extensions.py`, `models.py`, `services.py`, 
   `translations.py`) are in the project root. Best practice for larger Flask 
   apps is to use an application package structure.

   #### Planned Target Structure
   ```
   deloitte-projectops/
   ├── projectops/              # Application package
   │   ├── __init__.py          # create_app() factory
   │   ├── extensions.py
   │   ├── models.py
   │   ├── services.py
   │   ├── translations.py
   │   ├── config.py
   │   ├── routes/
   │   ├── admin/
   │   ├── middleware/
   │   └── modules/
   ├── run.py                   # Entry point
   └── ...
   ```

   #### Benefits
   - Clean separation of app code from project config
   - Standard imports: `from projectops.models import User`
   - Better for packaging/deployment

   #### Decision
   - **Deferred to v2.0.0** - significant refactor (2-3 hours)
   - All imports across codebase would need updating
   - Requires full test coverage to catch breaks

3. **Kanban Board CSRF Fix v1.21.5** (Complete)

   #### WSGI Middleware Implementation
   - Created `ServerHeaderMiddleware` class in app.py
   - Intercepts WSGI `start_response` to filter headers
   - Removes Werkzeug-set `Server` header
   - Adds neutral `Server: ProjectOps` header
   - Applied via `app.wsgi_app = ServerHeaderMiddleware(app.wsgi_app)`

   #### Security Finding (ZAP Penetration Test)
   - **Issue:** Server version information disclosure
   - **Before:** `Server: Werkzeug/3.1.4 Python/3.14.2`
   - **After:** `Server: ProjectOps`
   - **Risk:** Low (information disclosure)

   #### ZAP Scan Analysis
   - Analyzed report from `/admin/PENTEST/2026-01-05-ZAP-Report-.json`
   - Found ZAP only tested 6 endpoints (57% auth failures)
   - Most findings were on unauthenticated endpoints only
   - External CDN findings (googleapis, jsdelivr) not in scope

   #### Files Modified
   - `app.py` - Added `ServerHeaderMiddleware` class, removed redundant header from `after_request`

   #### Verification
   - Tested via Flask test client: `Server header: ProjectOps` ✅

2. **Kanban Board CSRF Fix v1.21.5** (Complete)

   #### Problem
   - Kanban-Karten ließen sich nicht per Drag & Drop verschieben
   - Symptom: Keine Fehlermeldung im UI, aber POST-Requests scheiterten
   - Root Cause: `fetch()` Requests ohne `X-CSRFToken` Header → 400 Response

   #### Diagnose-Prozess
   1. Zunächst CSP/SortableJS-Blockade vermutet → nicht zutreffend (CDN in CSP erlaubt)
   2. Workflow-Transitions geprüft → `can_transition_to()` korrekt (leere Liste = alle erlaubt)
   3. **CSRF-Token fehlt** → identifiziert durch Vergleich mit `backlog.html` (Session 25 Fix)

   #### Lösung
   - `X-CSRFToken` Header zu allen Board-Fetch-Requests hinzugefügt
   - Pattern: `if (window.csrfToken) { headers['X-CSRFToken'] = window.csrfToken; }`

   #### Files Modified
   - `modules/projects/templates/projects/board.html` - CSRF für Move + Quick Create
   - `modules/projects/templates/projects/sprints/board.html` - CSRF für Sprint Move
   - `modules/projects/templates/projects/iterations/board.html` - CSRF für Iteration Move
   - `modules/projects/templates/projects/settings/issue_statuses.html` - CSRF für Workflow Save

   #### Zusätzliche Änderungen
   - CSS: `cursor: grab` statt `pointer` für besseres Drag-Feedback
   - Verbesserte Click/Drag-Erkennung mit Zeit- und Distanz-Schwellwerten

   #### Lesson Learned
   > **Bei JEDEM neuen `fetch()` mit POST/PUT/DELETE immer `X-CSRFToken` Header prüfen!**
   > Dies war bereits das zweite Mal (nach Backlog in Session 25), dass fehlendes CSRF-Token 
   > JavaScript-Features stillschweigend blockierte. Dokumentiert in `docs/systemPatterns.md`.

   #### Verification
   - Kanban Drag & Drop funktioniert ✅
   - Network Tab: POST `/board/move` → 200 OK ✅

### ✅ What Was Accomplished (Session 25)

1. **Demo Data & Module System v1.21.3** (Complete)
   - Module creation in demo script (core + projects)
   - UserModule assignments for non-admin users
   - current_tenant_id set for all users

2. **AJAX CSRF Token Fixes v1.21.2** (Complete)

   #### Backlog Reorder Fix
   - Added `X-CSRFToken` header to drag & drop fetch requests
   - Changed SortableJS from `onEnd` to `onUpdate` to prevent false triggers on page load
   - Added JSON response validation before parsing
   - Added try/except with proper rollback and logging in `backlog_reorder()` route

   #### Estimation Story Points Fix
   - Added `X-CSRFToken` header to Story Point assignment fetch
   - Added `Accept: application/json` header for proper content negotiation
   - Added response content-type validation before JSON parsing

   #### CSP Update
   - Added `https://cdn.jsdelivr.net https://cdn.socket.io` to `connect-src` for source maps

   #### Files Modified
   - `modules/projects/templates/projects/backlog.html` - CSRF token in fetch
   - `modules/projects/templates/projects/estimation.html` - CSRF token in fetch
   - `modules/projects/routes.py` - Enhanced error handling in backlog_reorder()
   - `app.py` - Updated CSP connect-src directive

### ✅ What Was Accomplished (Session 23)

1. **Test Coverage Continued Expansion v1.20.4** (Complete)

   #### New Test Files Created
   - **`tests/unit/test_app.py`** - 23 tests for app.py
     - TestGetFileIcon: all file extension icon mappings (PDF, Word, Excel, images, etc.)
     - TestLegacyRouteAliases: index, login, logout endpoint aliases
     - TestContextProcessors: inject_globals with t(), app_name, helpers
     - TestLogAction: audit log creation with old/new values
     - TestWebSocketEvents: emit_notification functions
     - 19 passed, 4 xfailed

   - **`tests/integration/test_auth_routes.py`** - 31 tests for auth routes
     - TestLoginPage, TestLogout, TestSelectTenant
     - TestSwitchTenant, TestApiSwitchTenant
     - TestAuditLogging
     - 25 passed, 6 xfailed

   #### Extended Test Files
   - **`tests/integration/test_api_routes.py`** - +9 tests (46 total)
     - TestDashboardChartUserRestrictions: preparer user access to charts
     - TestDashboardTeamChart, TestDashboardTrendsChart
     - TestDashboardProjectDistribution, TestPresetsApi

   - **`tests/integration/test_admin_routes.py`** - +18 tests (59 total)
     - TestUserModulePermissions: save and remove module assignments
     - TestUserEntitySave, TestEntityUserSave: entity permission CRUD
     - TestCategoryCreateEdit, TestModuleToggleExtended, TestTeamValidation

   - **`tests/integration/test_tasks_routes.py`** - +16 evidence tests
     - TestTaskEvidence: file upload, link add, delete, not found handling
     - TestTaskReviewerAction: reviewer-specific actions

   #### Bug Fixes
   - **api_switch_tenant response**: Fixed `tenant.display_name` → `tenant.slug`

   #### Coverage Improvements

   | File | Before | After | Improvement |
   |------|--------|-------|-------------|
   | routes/auth.py | 57% | 100% | +43% |
   | routes/admin.py | 70% | 97% | +27% |
   | routes/api.py | 70% | 88% | +18% |
   | app.py | 64% | 78% | +14% |
   | routes/tasks.py | 62% | 69% | +7% |

   #### Test Results
   - **892 tests passed**, 12 skipped, 113 xfailed
   - **Overall Coverage: 68%** (up from 65%)

### ✅ What Was Accomplished (Session 22)

1. **Test Coverage Major Expansion v1.20.3** (Complete)

   #### New Test Files Created
   - **`tests/integration/test_admin_tenants_routes.py`** - 32 tests for admin tenants
     - TestTenantList, TestTenantCreate, TestTenantDetail, TestTenantEdit
     - TestTenantArchive, TestTenantMemberManagement, TestApiKeyManagement
     - 23 passed, 9 xfailed (template context processor)

   - **`tests/unit/test_services_coverage.py`** - 41 tests for services.py
     - NotificationService, CalendarService, ExportService
     - EmailService, RecurrenceService, WorkflowService, ApprovalService
     - All 41 passed

   - **`tests/integration/test_projects_routes.py`** - 36 tests for projects module
     - TestProject* (list, create, detail, edit, archive, members)
     - TestIssue* (list, create, detail, edit, delete)
     - TestBoard, TestBacklog, TestSprint*, TestIssueComments/Worklog
     - TestProjectSettings, TestProjectAPI, TestEstimation
     - 15 passed, 21 xfailed (template context processor + 1 API bug)

   #### Bug Fixes
   - **Dashboard Endpoint Bug**: Fixed `url_for('dashboard')` → `url_for('main.dashboard')`
     - templates/base.html (2 occurrences)
     - templates/profile_notifications.html (2 occurrences)
     - templates/calendar_subscription.html
     - admin/tenants.py
     - middleware/tenant.py (3 occurrences)
     - modules/projects/routes.py (2 occurrences)

   #### Coverage Improvements

   | File | Before | After | Improvement |
   |------|--------|-------|-------------|
   | admin/tenants.py | 17% | 63% | +46% |
   | modules/projects/routes.py | 19% | 42% | +23% |
   | services.py | 52% | 65% | +13% |

   #### Test Results
   - **814 tests passed**, 12 skipped, 97 xfailed
   - **Overall Coverage: 65%** (up from 46%)

### ✅ What Was Accomplished (Session 21)

1. **Test Coverage Improvements v1.20.2** (Complete)

   #### New Presets Blueprint (`routes/presets.py`) - 13 routes
   - Admin CRUD: `/admin/presets`, `/admin/presets/new`, `/admin/presets/<id>`, `/admin/presets/<id>/delete`
   - API endpoints: `/api/presets/<id>` PATCH, `/api/presets/bulk-toggle-active`, `/api/presets/bulk-delete`
   - Custom field CRUD: `/api/preset-fields` POST, `/api/preset-fields/<id>` GET/PUT/DELETE
   - Import/Export: `/admin/presets/export`, `/admin/presets/template`, `/admin/presets/seed`

   #### Extended Existing Blueprints
   - **admin_bp** (+6 routes): user_modules, user_entities, entity_users (GET/POST each)
   - **api_bp** (+8 routes): dashboard team-chart/velocity/trends/distribution, notifications list/count/read/mark-all
   - **tasks_bp** (+3 routes): export/excel, export/summary, export/pdf

   #### Final Stats
   - **97 routes migrated** across 6 blueprints (was 67 in v1.19.0)
   - **641 tests passed** (was 626)
   - Phase 4b route migration complete

### ✅ What Was Accomplished (Session 19)

1. **Phase 4 Blueprint Refactoring v1.19.0** (Complete)

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

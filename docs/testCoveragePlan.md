# Test Coverage Plan: Road to 100%

**Created:** 3. Januar 2026  
**Current Status:** 44% coverage (424 tests passing, 12 skipped)  
**Target:** 100% coverage (~920 tests estimated)

---

## Current Coverage Analysis

| File | Coverage | Lines Missed | Priority |
|------|----------|--------------|----------|
| `app.py` | 17% | 1,793 | High |
| `services.py` | 15% | 758 | High |
| `modules/projects/routes.py` | 19% | 1,337 | High |
| `admin/tenants.py` | 17% | 396 | Medium |
| `middleware/tenant.py` | 28% | 93 | Medium |
| `models.py` | 71% | ~200 | Low |
| `config.py` | 78% | ~30 | Low |

**Total statements missed:** 5,284 out of 9,332

---

## Implementation Phases

### Phase 1: Quick Wins (+5% coverage)
**Time Estimate:** 2-3 hours  
**Target Coverage:** 49%

#### Tasks:
1. **Create `.coveragerc` file** to exclude non-essential files:
   - `scripts/` directory
   - `migrations/` directory
   - `create_demo_data.py`
   - `init_db.py`

2. **Complete Model Method Tests:**
   - Finish testing all `Project` model getters
   - Test remaining `Task` model methods
   - Test `User` preference methods
   - Test `Notification` status methods

3. **Config Tests:**
   - Test all configuration classes
   - Test environment variable loading

---

### Phase 2: Middleware & Module Core (+8% coverage)
**Time Estimate:** 3-4 hours  
**Target Coverage:** 57%

#### Tasks:
1. **Middleware Testing (`middleware/tenant.py`):**
   - Mock `current_user` and Flask's `g` object
   - Test `require_tenant` decorator with various scenarios
   - Test `get_current_tenant()` function
   - Test tenant context switching

2. **Module Core (`modules/core/`):**
   - Test module registration system
   - Test permission checking utilities
   - Test module initialization

3. **Test Utilities:**
   - Create reusable mock fixtures for `current_user`
   - Create tenant context test helpers

---

### Phase 3: Service Layer Deep Dive (+12% coverage)
**Time Estimate:** 6-8 hours  
**Target Coverage:** 69%

#### Tasks:
1. **NotificationService (Full Coverage):**
   - Test `create_notification()` with all parameters
   - Test `send_bulk_notifications()`
   - Test notification preferences integration
   - Test email notification triggering

2. **ExportService (Full Coverage):**
   - Test `export_tasks_to_excel()` with mock data
   - Test `export_tasks_to_csv()`
   - Test column mapping and formatting
   - Test file generation and cleanup

3. **CalendarService (Full Coverage):**
   - Test `generate_ical()` 
   - Test `get_calendar_events()`
   - Test recurring event generation
   - Test timezone handling

4. **EmailService (Full Coverage):**
   - Mock SMTP connections
   - Test email template rendering
   - Test send failures and retries
   - Test attachment handling

5. **RecurrenceService (Full Coverage):**
   - Test all recurrence patterns (daily, weekly, monthly)
   - Test `generate_next_occurrence()`
   - Test edge cases (leap years, month ends)

#### Required Packages:
```
pytest-mock
responses (for HTTP mocking)
freezegun (for date/time mocking)
```

---

### Phase 4: Route Handlers (+25% coverage)
**Time Estimate:** 12-16 hours  
**Target Coverage:** 94%

#### Architecture Decision Required:
**Option A: Refactor to Blueprints** (Recommended)
- Move routes from `app.py` into Flask Blueprints
- Enables proper integration testing with `test_client`
- Cleaner separation of concerns
- Estimated refactoring time: 4-6 hours

**Option B: Mock-Heavy Unit Testing**
- Keep current architecture
- Use extensive mocking for request context
- More brittle tests, harder to maintain
- No refactoring time needed

#### Tasks (Assuming Option A):
1. **Create Blueprint Structure:**
   ```
   routes/
   ├── __init__.py
   ├── auth.py
   ├── dashboard.py
   ├── tasks.py
   ├── projects.py
   └── api.py
   ```

2. **Test Categories:**
   - **Authentication Routes:** login, logout, session management
   - **Dashboard Routes:** data aggregation, widget rendering
   - **Task Routes:** CRUD operations, status changes, assignments
   - **Project Routes:** CRUD, membership, settings
   - **API Routes:** JSON endpoints, filtering, pagination

3. **Integration Test Pattern:**
   ```python
   def test_task_create(client, auth_user, test_tenant):
       response = client.post('/tasks/create', data={...})
       assert response.status_code == 302
       assert Task.query.count() == 1
   ```

---

### Phase 5: Admin Module (+6% coverage)
**Time Estimate:** 4-6 hours  
**Target Coverage:** 100%

#### Tasks:
1. **Tenant Management (`admin/tenants.py`):**
   - Test tenant CRUD operations
   - Test tenant settings management
   - Test member invitations
   - Test role assignments

2. **Admin Dashboard:**
   - Test statistics aggregation
   - Test user management views
   - Test system configuration

3. **Permission Testing:**
   - Test admin-only route protection
   - Test cross-tenant isolation
   - Test superuser capabilities

---

## Test File Structure

```
tests/
├── conftest.py                    # Shared fixtures
├── unit/
│   ├── test_models.py            # ✅ Exists
│   ├── test_task_model.py        # ✅ Exists  
│   ├── test_project_methods.py   # ✅ Exists
│   ├── test_all_services.py      # ✅ Exists
│   ├── test_middleware_advanced.py # ✅ Exists
│   ├── test_notification_service.py # Phase 3
│   ├── test_export_service.py    # Phase 3
│   ├── test_calendar_service.py  # Phase 3
│   ├── test_email_service.py     # Phase 3
│   ├── test_recurrence_service.py # Phase 3
│   └── test_config.py            # Phase 1
├── integration/
│   ├── test_auth_routes.py       # Phase 4
│   ├── test_task_routes.py       # Phase 4
│   ├── test_project_routes.py    # Phase 4
│   ├── test_dashboard_routes.py  # Phase 4
│   └── test_api_routes.py        # Phase 4
└── admin/
    ├── test_tenant_management.py # Phase 5
    └── test_admin_dashboard.py   # Phase 5
```

---

## Milestones

| Milestone | Tests | Coverage | Hours |
|-----------|-------|----------|-------|
| Phase 1 Complete | ~470 | 49% | 2-3 |
| Phase 2 Complete | ~520 | 57% | 5-7 |
| Phase 3 Complete | ~620 | 69% | 11-15 |
| Phase 4 Complete | ~870 | 94% | 23-31 |
| Phase 5 Complete | ~920 | 100% | 27-37 |

---

## Key Dependencies

### Python Packages Needed:
```
pytest>=9.0.0
pytest-cov>=7.0.0
pytest-flask>=1.3.0
pytest-mock>=3.12.0
responses>=0.24.0
freezegun>=1.2.0
```

### Infrastructure Requirements:
- Test database (SQLite in-memory)
- Mock SMTP server for email tests
- Fixture data generators

---

## Risk Factors

1. **Route Architecture:** Routes defined outside `create_app()` prevent easy integration testing
   - Mitigation: Blueprint refactoring in Phase 4

2. **External Dependencies:** Email, calendar integrations
   - Mitigation: Comprehensive mocking strategy

3. **Test Isolation:** Database state leaking between tests
   - Mitigation: ✅ Fixed with `clean_db_tables` fixture

4. **Time Investment:** 27-37 hours is significant
   - Mitigation: Prioritize by business value (Phase 3 services first)

---

## Quick Reference: Current Test Count

```
tests/unit/test_models.py           - 89 tests
tests/unit/test_task_model.py       - 56 tests  
tests/unit/test_project_methods.py  - 42 tests
tests/unit/test_all_services.py     - 36 tests
tests/unit/test_middleware_advanced.py - 18 tests
tests/unit/test_middleware.py       - 35 tests
tests/unit/test_services.py         - 79 tests
tests/unit/test_translations.py     - 57 tests
-------------------------------------------
Total:                              424 tests
```

---

## Next Actions

1. [ ] Create `.coveragerc` to exclude non-essential directories
2. [ ] Install additional testing packages (pytest-mock, freezegun)
3. [ ] Begin Phase 1: Complete remaining model tests
4. [ ] Review route architecture for Blueprint decision

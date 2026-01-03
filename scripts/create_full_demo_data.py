#!/usr/bin/env python3
"""
Create Complete Demo Data for Multi-Tenancy

Creates demo data for all tenants:
- Projects with Issues
- Tasks from TaskPresets  
- Teams, Entities, Tax Types

Run with: python scripts/create_full_demo_data.py
"""
import sys
import os
import random
from datetime import datetime, date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import (
    Tenant, TenantMembership, User, Team, Entity, TaxType, 
    Task, TaskPreset, Notification
)
from modules.projects.models import (
    Project, ProjectMember, Issue, IssueType, IssueStatus, Sprint,
    create_default_issue_types, create_default_issue_statuses
)


# =============================================================================
# DEMO DATA DEFINITIONS
# =============================================================================

DEMO_PROJECTS = {
    'deloitte_germany': [
        {
            'key': 'TAX',
            'name': 'Steuerliche Compliance',
            'name_en': 'Tax Compliance',
            'description': 'Steuerliche Pflichten und Fristen für alle Gesellschaften',
            'category': 'Tax',
            'icon': 'bi-calculator',
            'color': '#86BC25'
        },
        {
            'key': 'AUD',
            'name': 'Jahresabschlussprüfung 2025',
            'name_en': 'Annual Audit 2025',
            'description': 'Vorbereitung und Durchführung der Jahresabschlussprüfung',
            'category': 'Audit',
            'icon': 'bi-clipboard-check',
            'color': '#0076A8'
        },
        {
            'key': 'DIG',
            'name': 'Digitalisierung Initiative',
            'name_en': 'Digitalization Initiative',
            'description': 'Interne Digitalisierungsprojekte',
            'category': 'Internal',
            'icon': 'bi-gear',
            'color': '#DA291C'
        }
    ],
    'demo_client': [
        {
            'key': 'DEMO',
            'name': 'Demo Projekt',
            'name_en': 'Demo Project',
            'description': 'Beispielprojekt für Demonstrationszwecke',
            'category': 'Demo',
            'icon': 'bi-star',
            'color': '#6B3FA0'
        },
        {
            'key': 'TEST',
            'name': 'Test & QA',
            'name_en': 'Test & QA',
            'description': 'Quality Assurance und Testing',
            'category': 'Testing',
            'icon': 'bi-bug',
            'color': '#FF6B35'
        }
    ]
}

DEMO_ISSUES = [
    # Epics
    {'type': 'Epic', 'summary': 'Q1 2026 Compliance', 'priority': 2, 'labels': ['Q1-2026', 'Compliance']},
    {'type': 'Epic', 'summary': 'Digitalisierung Phase 1', 'priority': 2, 'labels': ['Digital', 'Phase-1']},
    {'type': 'Epic', 'summary': 'Prozessoptimierung', 'priority': 3, 'labels': ['Optimierung']},
    # Stories
    {'type': 'Story', 'summary': 'USt-Voranmeldung Januar', 'priority': 1, 'story_points': 5, 'labels': ['USt', 'Monatlich'], 'due_days': 10},
    {'type': 'Story', 'summary': 'Lohnsteuer-Anmeldung Februar', 'priority': 2, 'story_points': 3, 'labels': ['LohnSt', 'Monatlich'], 'due_days': 15},
    {'type': 'Story', 'summary': 'Jahresabschluss-Unterlagen sammeln', 'priority': 2, 'story_points': 8, 'labels': ['Jahresabschluss'], 'due_days': 30},
    {'type': 'Story', 'summary': 'Dokumenten-Scanner Integration', 'priority': 3, 'story_points': 5, 'labels': ['Integration'], 'due_days': 45},
    {'type': 'Story', 'summary': 'Reporting Dashboard erstellen', 'priority': 2, 'story_points': 8, 'labels': ['Dashboard', 'Reporting'], 'due_days': 21},
    {'type': 'Story', 'summary': 'API-Anbindung Finanzamt', 'priority': 1, 'story_points': 13, 'labels': ['API', 'Finanzamt'], 'due_days': 60},
    {'type': 'Story', 'summary': 'Mitarbeiter-Schulung planen', 'priority': 3, 'story_points': 3, 'labels': ['Schulung'], 'due_days': 25},
    # Tasks
    {'type': 'Task', 'summary': 'Belegprüfung Januar', 'priority': 2, 'story_points': 2, 'due_days': 5},
    {'type': 'Task', 'summary': 'Kontenabstimmung durchführen', 'priority': 2, 'story_points': 3, 'due_days': 7},
    {'type': 'Task', 'summary': 'Quartalsbericht erstellen', 'priority': 1, 'story_points': 5, 'due_days': 14},
    {'type': 'Task', 'summary': 'Team-Meeting organisieren', 'priority': 4, 'story_points': 1, 'due_days': 3},
    {'type': 'Task', 'summary': 'Dokumentation aktualisieren', 'priority': 3, 'story_points': 2, 'due_days': 10},
    {'type': 'Task', 'summary': 'Systemkonfiguration prüfen', 'priority': 2, 'story_points': 3, 'due_days': 8},
    {'type': 'Task', 'summary': 'Backup-Strategie überprüfen', 'priority': 2, 'story_points': 2, 'due_days': 12},
    {'type': 'Task', 'summary': 'Kundenfeedback auswerten', 'priority': 3, 'story_points': 3, 'due_days': 18},
    # Subtasks
    {'type': 'Subtask', 'summary': 'Eingangsrechnungen prüfen', 'priority': 3, 'story_points': 1, 'due_days': 2},
    {'type': 'Subtask', 'summary': 'Ausgangsrechnungen prüfen', 'priority': 3, 'story_points': 1, 'due_days': 2},
    {'type': 'Subtask', 'summary': 'Reisekostenabrechnungen kontrollieren', 'priority': 3, 'story_points': 1, 'due_days': 4},
    {'type': 'Subtask', 'summary': 'Bankabstimmung durchführen', 'priority': 2, 'story_points': 2, 'due_days': 3},
    # Bugs
    {'type': 'Bug', 'summary': 'Berechnungsfehler im Formular', 'priority': 1, 'labels': ['Bug', 'Urgent'], 'due_days': 1},
    {'type': 'Bug', 'summary': 'Formatierung in Export fehlerhaft', 'priority': 3, 'labels': ['Bug'], 'due_days': 7},
    {'type': 'Bug', 'summary': 'Performance-Problem bei großen Datenmengen', 'priority': 2, 'labels': ['Bug', 'Performance'], 'due_days': 5},
    {'type': 'Bug', 'summary': 'Druckvorschau zeigt falsche Daten', 'priority': 2, 'labels': ['Bug'], 'due_days': 6},
]

DEMO_ENTITIES = {
    'deloitte_germany': [
        {'name': 'Deloitte GmbH', 'code': 'DEL-DE'},
        {'name': 'Deloitte Holding AG', 'code': 'DEL-HLD'},
        {'name': 'Deloitte Consulting GmbH', 'code': 'DEL-CON'},
    ],
    'demo_client': [
        {'name': 'Demo Holding AG', 'code': 'DEMO-HLD'},
        {'name': 'Demo Services GmbH', 'code': 'DEMO-SVC'},
    ]
}

DEMO_TAX_TYPES = [
    {'code': 'USt', 'name': 'Umsatzsteuer', 'name_en': 'VAT'},
    {'code': 'KSt', 'name': 'Körperschaftsteuer', 'name_en': 'Corporate Tax'},
    {'code': 'GewSt', 'name': 'Gewerbesteuer', 'name_en': 'Trade Tax'},
    {'code': 'LohnSt', 'name': 'Lohnsteuer', 'name_en': 'Payroll Tax'},
    {'code': 'ErbSt', 'name': 'Erbschaftsteuer', 'name_en': 'Inheritance Tax'},
]

DEMO_TEAMS = {
    'deloitte_germany': [
        {'name': 'Tax Compliance Team', 'name_en': 'Tax Compliance Team'},
        {'name': 'Audit Team', 'name_en': 'Audit Team'},
        {'name': 'Digital Transformation', 'name_en': 'Digital Transformation'},
    ],
    'demo_client': [
        {'name': 'Demo Team', 'name_en': 'Demo Team'},
    ]
}


# =============================================================================
# MAIN FUNCTIONS
# =============================================================================

def get_or_create_issue_types_for_project(project):
    """Ensure default issue types exist for a project"""
    types = IssueType.query.filter_by(project_id=project.id).all()
    if not types:
        # Create default types for this project
        default_types = [
            ('Epic', 'bi-lightning-charge', '#6B3FA0', 0, True, False),
            ('Story', 'bi-bookmark', '#0076A8', 1, True, False),
            ('Task', 'bi-check2-square', '#86BC25', 2, True, False),
            ('Bug', 'bi-bug', '#DA291C', 2, False, False),
            ('Subtask', 'bi-list-task', '#62B5E5', 3, False, True),
        ]
        for name, icon, color, level, can_children, is_subtask in default_types:
            issue_type = IssueType(
                project_id=project.id,
                name=name,
                icon=icon,
                color=color,
                hierarchy_level=level,
                can_have_children=can_children,
                is_subtask=is_subtask
            )
            db.session.add(issue_type)
        db.session.commit()
        types = IssueType.query.filter_by(project_id=project.id).all()
    return {t.name: t for t in types}


def get_or_create_issue_statuses_for_project(project):
    """Ensure default issue statuses exist for a project"""
    statuses = IssueStatus.query.filter_by(project_id=project.id).all()
    if not statuses:
        default_statuses = [
            ('To Do', 'todo', 1),
            ('In Progress', 'in_progress', 2),
            ('In Review', 'in_progress', 3),
            ('Done', 'done', 4),
        ]
        for name, category, order in default_statuses:
            status = IssueStatus(
                project_id=project.id,
                name=name,
                category=category,
                sort_order=order
            )
            db.session.add(status)
        db.session.commit()
        statuses = IssueStatus.query.filter_by(project_id=project.id).all()
    return {s.name: s for s in statuses}


def create_demo_data_for_tenant(tenant, admin_user):
    """Create all demo data for a specific tenant"""
    print(f"\n{'='*60}")
    print(f"Creating demo data for: {tenant.name} ({tenant.slug})")
    print(f"{'='*60}")
    
    # Get all tenant members
    members = [m.user for m in tenant.memberships]
    if not members:
        members = [admin_user]
    
    # Check if this is the first tenant (already has data from migration)
    is_first_tenant = tenant.id == 1
    
    # 1. Get or Create Entities
    print("\n📁 Getting/Creating Entities...")
    if is_first_tenant:
        # Use existing entities for first tenant
        entities = Entity.query.filter(
            (Entity.tenant_id == tenant.id) | (Entity.tenant_id.is_(None))
        ).all()
        if entities:
            print(f"  ℹ Using {len(entities)} existing entities")
        else:
            entities = []
    else:
        entities_data = DEMO_ENTITIES.get(tenant.slug, [{'name': f'{tenant.name} Default Entity', 'code': tenant.slug.upper()[:6]}])
        entities = []
        for data in entities_data:
            entity = Entity.query.filter_by(name=data['name'], tenant_id=tenant.id).first()
            if not entity:
                entity = Entity(name=data['name'], tenant_id=tenant.id)
                db.session.add(entity)
                print(f"  ✓ Created entity: {data['name']}")
            entities.append(entity)
        db.session.commit()
    
    # 2. Get or Create Tax Types
    print("\n📋 Getting/Creating Tax Types...")
    if is_first_tenant:
        # Use existing tax types for first tenant
        tax_types = TaxType.query.filter(
            (TaxType.tenant_id == tenant.id) | (TaxType.tenant_id.is_(None))
        ).all()
        if tax_types:
            print(f"  ℹ Using {len(tax_types)} existing tax types")
        else:
            tax_types = []
    else:
        tax_types = []
        for data in DEMO_TAX_TYPES:
            tt = TaxType.query.filter_by(code=data['code'], tenant_id=tenant.id).first()
            if not tt:
                # Check if code exists globally (old constraint)
                existing = TaxType.query.filter_by(code=data['code']).first()
                if existing:
                    print(f"  ⚠ Skipping {data['code']} (exists globally)")
                    continue
                tt = TaxType(
                    code=data['code'],
                    name=data['name'],
                    name_en=data['name_en'],
                    tenant_id=tenant.id
                )
                db.session.add(tt)
                print(f"  ✓ Created tax type: {data['code']}")
            tax_types.append(tt)
        db.session.commit()
    
    # 3. Get or Create Teams
    print("\n👥 Getting/Creating Teams...")
    if is_first_tenant:
        # Use existing teams for first tenant
        teams = Team.query.filter(
            (Team.tenant_id == tenant.id) | (Team.tenant_id.is_(None))
        ).all()
        if teams:
            print(f"  ℹ Using {len(teams)} existing teams")
        else:
            teams = []
    else:
        teams_data = DEMO_TEAMS.get(tenant.slug, [{'name': f'{tenant.name} Team', 'name_en': f'{tenant.name} Team'}])
        teams = []
        for data in teams_data:
            team = Team.query.filter_by(name=data['name'], tenant_id=tenant.id).first()
            if not team:
                team = Team(
                    name=data['name'],
                    name_en=data['name_en'],
                    tenant_id=tenant.id
                )
                db.session.add(team)
                print(f"  ✓ Created team: {data['name']}")
            teams.append(team)
        db.session.commit()
    
    # 4. Get or Create Projects
    print("\n🗂️ Getting/Creating Projects...")
    if is_first_tenant:
        # Use existing projects for first tenant
        projects = Project.query.filter(
            (Project.tenant_id == tenant.id) | (Project.tenant_id.is_(None))
        ).all()
        if projects:
            print(f"  ℹ Using {len(projects)} existing projects")
        else:
            projects = []
    else:
        projects_data = DEMO_PROJECTS.get(tenant.slug, [
            {'key': 'PRJ', 'name': f'{tenant.name} Project', 'name_en': f'{tenant.name} Project', 
             'category': 'General', 'icon': 'bi-folder', 'color': '#0076A8'}
        ])
        projects = []
        for data in projects_data:
            project = Project.query.filter_by(key=data['key'], tenant_id=tenant.id).first()
            if not project:
                # Check if key exists globally (old constraint)
                existing = Project.query.filter_by(key=data['key']).first()
                if existing:
                    print(f"  ⚠ Skipping project {data['key']} (exists globally)")
                    continue
                project = Project(
                    key=data['key'],
                    name=data['name'],
                    name_en=data.get('name_en', data['name']),
                    description=data.get('description', ''),
                    category=data.get('category', 'General'),
                    icon=data.get('icon', 'bi-folder'),
                    color=data.get('color', '#0076A8'),
                    lead_id=admin_user.id,
                    created_by_id=admin_user.id,
                    tenant_id=tenant.id
                )
                db.session.add(project)
                db.session.flush()
                
                # Add admin as project member
                member = ProjectMember(
                    project_id=project.id,
                    user_id=admin_user.id,
                    role='admin',
                    added_by_id=admin_user.id
                )
                db.session.add(member)
                print(f"  ✓ Created project: {data['key']} - {data['name']}")
            projects.append(project)
        db.session.commit()
    
    # 5. Create Issues for each project
    print("\n📝 Creating Issues...")
    for project in projects:
        # Get or create issue types and statuses for THIS project
        issue_types = get_or_create_issue_types_for_project(project)
        issue_statuses = get_or_create_issue_statuses_for_project(project)
        status_list = list(issue_statuses.values())
        
        if not issue_types or not status_list:
            print(f"  ⚠ Skipping {project.key} - no types or statuses")
            continue
        
        # Check if project already has issues
        existing_count = Issue.query.filter_by(project_id=project.id).count()
        if existing_count >= 10:
            print(f"  • Project {project.key} already has {existing_count} issues")
            continue
        
        issue_count = 0
        # Get next issue number for this project
        max_issue = db.session.query(db.func.max(Issue.id)).filter_by(project_id=project.id).scalar() or 0
        next_number = max_issue + 1
        
        for i, issue_data in enumerate(DEMO_ISSUES):
            type_name = issue_data.get('type', 'Task')
            issue_type = issue_types.get(type_name)
            if not issue_type:
                continue
            
            # Random status
            status = random.choice(status_list)
            
            # Due date
            due_days = issue_data.get('due_days', random.randint(7, 60))
            due_date = date.today() + timedelta(days=due_days)
            
            # Random assignee from members
            assignee = random.choice(members) if members else admin_user
            
            # Labels as list
            labels = issue_data.get('labels', [])
            if isinstance(labels, str):
                labels = [l.strip() for l in labels.split(',') if l.strip()]
            
            # Generate key (PROJECT-NUMBER)
            issue_key = f"{project.key}-{next_number + i}"
            
            issue = Issue(
                project_id=project.id,
                key=issue_key,
                type_id=issue_type.id,
                status_id=status.id,
                summary=issue_data['summary'],
                description=f"Demo-Issue für {project.name}\n\nDies ist eine automatisch generierte Demo-Issue für Testzwecke.",
                priority=issue_data.get('priority', 3),
                story_points=issue_data.get('story_points'),
                labels=labels,
                due_date=due_date,
                assignee_id=assignee.id,
                reporter_id=admin_user.id,
                tenant_id=tenant.id
            )
            db.session.add(issue)
            issue_count += 1
        
        db.session.commit()
        print(f"  ✓ Created {issue_count} issues for project {project.key}")
    
    # 6. Create Sprints and assign issues
    print("\n🏃 Creating Sprints and assigning Issues...")
    for project in projects:
        existing_sprints = Sprint.query.filter_by(project_id=project.id).count()
        if existing_sprints >= 3:
            print(f"  • Project {project.key} already has {existing_sprints} sprints")
            continue
        
        # Create 4 sprints: 2 past, current, future
        sprints_data = [
            {'name': 'Sprint 1 - Grundlagen', 'goal': 'Grundlegende Infrastruktur aufbauen', 'start': -42, 'end': -28, 'state': 'completed'},
            {'name': 'Sprint 2 - Core Features', 'goal': 'Kernfunktionalitäten implementieren', 'start': -28, 'end': -14, 'state': 'completed'},
            {'name': 'Sprint 3 - Aktuell', 'goal': 'Aktuelle Aufgaben abarbeiten und Bugs fixen', 'start': -7, 'end': 7, 'state': 'active'},
            {'name': 'Sprint 4 - Nächste Iteration', 'goal': 'Erweiterungen und Optimierungen', 'start': 14, 'end': 28, 'state': 'planning'},
        ]
        
        created_sprints = []
        for s_data in sprints_data:
            sprint = Sprint(
                project_id=project.id,
                name=s_data['name'],
                goal=s_data['goal'],
                start_date=date.today() + timedelta(days=s_data['start']),
                end_date=date.today() + timedelta(days=s_data['end']),
                state=s_data['state'],
                tenant_id=tenant.id
            )
            db.session.add(sprint)
            created_sprints.append(sprint)
        
        db.session.commit()
        print(f"  ✓ Created {len(created_sprints)} sprints for {project.key}")
        
        # Assign issues to sprints
        project_issues = Issue.query.filter_by(project_id=project.id).all()
        if project_issues and created_sprints:
            # Distribute issues across sprints
            active_sprint = next((s for s in created_sprints if s.state == 'active'), None)
            planning_sprint = next((s for s in created_sprints if s.state == 'planning'), None)
            completed_sprints = [s for s in created_sprints if s.state == 'completed']
            
            for i, issue in enumerate(project_issues):
                # Skip Epics from sprints
                if issue.issue_type and issue.issue_type.name == 'Epic':
                    continue
                
                # Assign to different sprints based on status
                if issue.status and issue.status.category == 'done':
                    # Done issues go to completed sprints
                    if completed_sprints:
                        issue.sprint_id = completed_sprints[i % len(completed_sprints)].id
                elif issue.status and issue.status.category == 'in_progress':
                    # In progress issues go to active sprint
                    if active_sprint:
                        issue.sprint_id = active_sprint.id
                else:
                    # Todo issues go to planning or active sprint
                    if i % 2 == 0 and active_sprint:
                        issue.sprint_id = active_sprint.id
                    elif planning_sprint:
                        issue.sprint_id = planning_sprint.id
            
            db.session.commit()
            assigned_count = sum(1 for issue in project_issues if issue.sprint_id)
            print(f"  ✓ Assigned {assigned_count} issues to sprints for {project.key}")
    
    # 7. Create Tasks from TaskPresets
    print("\n✅ Creating Tasks...")
    presets = TaskPreset.query.filter_by(tenant_id=tenant.id).limit(15).all()
    if not presets:
        # Use global presets if tenant has none
        presets = TaskPreset.query.filter_by(tenant_id=None).limit(15).all()
    
    if presets and entities:
        task_count = 0
        for i, preset in enumerate(presets):
            entity = entities[i % len(entities)]
            assignee = members[i % len(members)] if members else admin_user
            
            # Vary status and dates
            statuses = ['draft', 'in_progress', 'in_review', 'completed']
            status = statuses[i % len(statuses)]
            
            if status == 'completed':
                due = date.today() - timedelta(days=random.randint(10, 60))
            else:
                due = date.today() + timedelta(days=random.randint(5, 90))
            
            task = Task(
                title=preset.title_de or preset.title or f"Aufgabe {i+1}",
                description=preset.description_de or preset.description or "",
                due_date=due,
                status=status,
                entity_id=entity.id,
                owner_id=assignee.id,
                year=due.year,
                preset_id=preset.id,
                tenant_id=tenant.id
            )
            db.session.add(task)
            task_count += 1
        
        db.session.commit()
        print(f"  ✓ Created {task_count} tasks")
    else:
        print("  ⚠️ No presets available for task creation")
    
    print(f"\n✅ Demo data complete for {tenant.name}")


def main():
    """Main function to create demo data for all tenants"""
    with app.app_context():
        print("="*60)
        print("Creating Full Demo Data for All Tenants")
        print("="*60)
        
        # Get admin user
        admin_user = User.query.filter_by(email='admin@example.com').first()
        if not admin_user:
            admin_user = User.query.filter(User.role == 'admin').first()
        if not admin_user:
            admin_user = User.query.first()
        
        if not admin_user:
            print("❌ No users found. Please create users first.")
            return
        
        print(f"👤 Using admin: {admin_user.name} ({admin_user.email})")
        
        # Get all active tenants
        tenants = Tenant.query.filter_by(is_active=True, is_archived=False).all()
        
        if not tenants:
            print("❌ No active tenants found. Run create_demo_tenants.py first.")
            return
        
        print(f"📋 Found {len(tenants)} active tenants")
        
        # Create demo data for each tenant
        for tenant in tenants:
            try:
                create_demo_data_for_tenant(tenant, admin_user)
            except Exception as e:
                print(f"❌ Error creating data for {tenant.name}: {e}")
                db.session.rollback()
                continue
        
        # Final summary
        print("\n" + "="*60)
        print("📊 SUMMARY")
        print("="*60)
        
        for tenant in tenants:
            project_count = Project.query.filter_by(tenant_id=tenant.id).count()
            issue_count = Issue.query.filter_by(tenant_id=tenant.id).count()
            sprint_count = Sprint.query.filter_by(tenant_id=tenant.id).count()
            task_count = Task.query.filter_by(tenant_id=tenant.id).count()
            entity_count = Entity.query.filter_by(tenant_id=tenant.id).count()
            team_count = Team.query.filter_by(tenant_id=tenant.id).count()
            
            print(f"\n{tenant.name} ({tenant.slug}):")
            print(f"  • {project_count} Projects")
            print(f"  • {issue_count} Issues (Items)")
            print(f"  • {sprint_count} Sprints (Iterations)")
            print(f"  • {task_count} Tasks")
            print(f"  • {entity_count} Entities")
            print(f"  • {team_count} Teams")
        
        print("\n✅ All demo data created successfully!")
        print("🔗 Access: http://127.0.0.1:5000")


if __name__ == '__main__':
    main()

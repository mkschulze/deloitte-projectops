#!/usr/bin/env python
"""
Create sample issues for testing the Projects module.
Run with: python scripts/create_sample_issues.py
"""
import sys
import os
from datetime import datetime, timedelta
import random

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from extensions import db
from modules.projects.models import Project, Issue, IssueType, IssueStatus, ProjectMember
from modules.projects.routes import create_default_issue_types, create_default_issue_statuses
from models import User


# Sample issues organized by category
SAMPLE_ISSUES = [
    # Epics
    {
        'type': 'Epic',
        'summary': 'Q1 Steuerliche Compliance',
        'summary_en': 'Q1 Tax Compliance',
        'description': 'Alle steuerlichen Pflichten für Q1 2026 sicherstellen',
        'priority': 2,
        'story_points': None,
        'labels': ['Q1-2026', 'Compliance'],
    },
    {
        'type': 'Epic',
        'summary': 'Digitalisierung Dokumentenmanagement',
        'summary_en': 'Document Management Digitalization',
        'description': 'Einführung eines digitalen Dokumentenmanagementsystems',
        'priority': 2,
        'story_points': None,
        'labels': ['Digital', 'Initiative'],
    },
    
    # Stories
    {
        'type': 'Story',
        'summary': 'USt-Voranmeldung Januar einreichen',
        'summary_en': 'Submit VAT return for January',
        'description': 'USt-Voranmeldung für Januar 2026 vorbereiten und fristgerecht einreichen.\n\n**Akzeptanzkriterien:**\n- Alle Belege geprüft\n- Abstimmung mit Buchhaltung erfolgt\n- Fristgerechte Übermittlung an Finanzamt',
        'priority': 1,
        'story_points': 5,
        'labels': ['USt', 'Monatlich'],
        'due_days': 10,
    },
    {
        'type': 'Story',
        'summary': 'Lohnsteuer-Anmeldung Februar',
        'summary_en': 'Payroll tax registration February',
        'description': 'Lohnsteuer-Anmeldung für Februar vorbereiten und einreichen.',
        'priority': 2,
        'story_points': 3,
        'labels': ['LohnSt', 'Monatlich'],
        'due_days': 15,
    },
    {
        'type': 'Story',
        'summary': 'Jahresabschluss-Unterlagen sammeln',
        'summary_en': 'Collect annual report documents',
        'description': 'Alle relevanten Unterlagen für den Jahresabschluss 2025 zusammenstellen.',
        'priority': 2,
        'story_points': 8,
        'labels': ['Jahresabschluss', '2025'],
        'due_days': 30,
    },
    {
        'type': 'Story',
        'summary': 'Dokumenten-Scanner integrieren',
        'summary_en': 'Integrate document scanner',
        'description': 'Scanner-Software mit dem neuen DMS verbinden für automatische Dokumentenerfassung.',
        'priority': 3,
        'story_points': 5,
        'labels': ['Digital', 'Integration'],
        'due_days': 45,
    },
    {
        'type': 'Story',
        'summary': 'Mitarbeiter-Schulung DMS',
        'summary_en': 'Employee training DMS',
        'description': 'Schulungsunterlagen erstellen und Mitarbeiter im neuen Dokumentenmanagementsystem schulen.',
        'priority': 3,
        'story_points': 8,
        'labels': ['Schulung', 'DMS'],
        'due_days': 60,
    },
    
    # Tasks
    {
        'type': 'Task',
        'summary': 'Belegprüfung Januar durchführen',
        'summary_en': 'Perform document review January',
        'description': 'Alle Eingangs- und Ausgangsrechnungen für Januar prüfen und kontieren.',
        'priority': 2,
        'story_points': 3,
        'labels': ['Buchhaltung'],
        'due_days': 5,
        'status': 'In Bearbeitung',
    },
    {
        'type': 'Task',
        'summary': 'Elster-Zertifikat erneuern',
        'summary_en': 'Renew Elster certificate',
        'description': 'Das Elster-Zertifikat läuft am 31.01.2026 ab und muss erneuert werden.',
        'priority': 1,
        'story_points': 1,
        'labels': ['Admin', 'Elster'],
        'due_days': 3,
        'status': 'Erledigt',
    },
    {
        'type': 'Task',
        'summary': 'Kontenabstimmung Dezember',
        'summary_en': 'Account reconciliation December',
        'description': 'Abstimmung aller Sachkonten für Dezember 2025.',
        'priority': 2,
        'story_points': 5,
        'labels': ['Buchhaltung', 'Abstimmung'],
        'due_days': -2,  # Overdue
        'status': 'In Bearbeitung',
    },
    {
        'type': 'Task',
        'summary': 'DMS-Testinstallation aufsetzen',
        'summary_en': 'Set up DMS test installation',
        'description': 'Testumgebung für das neue Dokumentenmanagementsystem aufsetzen.',
        'priority': 3,
        'story_points': 3,
        'labels': ['DMS', 'IT'],
        'due_days': 20,
    },
    {
        'type': 'Task',
        'summary': 'Archiv-Struktur definieren',
        'summary_en': 'Define archive structure',
        'description': 'Ordnerstruktur und Namenskonventionen für das digitale Archiv festlegen.',
        'priority': 3,
        'story_points': 2,
        'labels': ['DMS', 'Organisation'],
        'due_days': 25,
        'status': 'Erledigt',
    },
    {
        'type': 'Task',
        'summary': 'Altdaten-Migration planen',
        'summary_en': 'Plan legacy data migration',
        'description': 'Migrationskonzept für bestehende Dokumente ins neue DMS erstellen.',
        'priority': 4,
        'story_points': 5,
        'labels': ['DMS', 'Migration'],
        'due_days': 40,
    },
    
    # Bugs
    {
        'type': 'Bug',
        'summary': 'Falscher Steuersatz bei EU-Lieferungen',
        'summary_en': 'Wrong tax rate for EU deliveries',
        'description': '**Problem:** Bei innergemeinschaftlichen Lieferungen wird der Standard-Steuersatz statt 0% angezeigt.\n\n**Schritte zur Reproduktion:**\n1. Neue Rechnung erstellen\n2. EU-Kunde auswählen\n3. Position hinzufügen\n\n**Erwartet:** Steuersatz 0%\n**Tatsächlich:** Steuersatz 19%',
        'priority': 1,
        'story_points': 2,
        'labels': ['Bug', 'Kritisch', 'Buchhaltung'],
        'due_days': 1,
    },
    {
        'type': 'Bug',
        'summary': 'PDF-Export zeigt falsches Datum',
        'summary_en': 'PDF export shows wrong date',
        'description': 'Beim PDF-Export von Berichten wird das falsche Datum im Header angezeigt.',
        'priority': 3,
        'story_points': 1,
        'labels': ['Bug', 'PDF'],
        'due_days': 14,
    },
    {
        'type': 'Bug',
        'summary': 'Langsame Ladezeit bei großen Konten',
        'summary_en': 'Slow loading for large accounts',
        'description': 'Konten mit mehr als 1000 Buchungen laden sehr langsam (>10 Sekunden).',
        'priority': 2,
        'story_points': 3,
        'labels': ['Bug', 'Performance'],
        'due_days': 21,
        'status': 'In Bearbeitung',
    },
    
    # Sub-Tasks (without parent for now)
    {
        'type': 'Sub-Task',
        'summary': 'Eingangsrechnungen prüfen',
        'summary_en': 'Review incoming invoices',
        'description': 'Alle Eingangsrechnungen auf Vollständigkeit und Richtigkeit prüfen.',
        'priority': 3,
        'story_points': 1,
        'labels': [],
        'status': 'Erledigt',
    },
    {
        'type': 'Sub-Task',
        'summary': 'Ausgangsrechnungen prüfen',
        'summary_en': 'Review outgoing invoices',
        'description': 'Alle Ausgangsrechnungen auf Vollständigkeit und Richtigkeit prüfen.',
        'priority': 3,
        'story_points': 1,
        'labels': [],
        'status': 'Erledigt',
    },
    {
        'type': 'Sub-Task',
        'summary': 'Kassenbuch abstimmen',
        'summary_en': 'Reconcile cash book',
        'description': 'Kassenbuch mit Bankkontoauszügen abgleichen.',
        'priority': 3,
        'story_points': 1,
        'labels': [],
        'status': 'In Bearbeitung',
    },
]


def create_sample_issues():
    """Create sample issues for the first project."""
    with app.app_context():
        # Find a project (prefer TAX)
        project = Project.query.filter_by(key='TAX').first()
        if not project:
            project = Project.query.first()
        
        if not project:
            print("ERROR: No projects found. Run 'python scripts/create_sample_projects.py' first.")
            return False
        
        print(f"Creating issues for project: {project.key} - {project.name}")
        print("-" * 60)
        
        # Ensure issue types and statuses exist
        issue_types = IssueType.query.filter_by(project_id=project.id).all()
        if not issue_types:
            print("Creating default issue types...")
            create_default_issue_types(project)
            db.session.commit()
            issue_types = IssueType.query.filter_by(project_id=project.id).all()
        
        issue_statuses = IssueStatus.query.filter_by(project_id=project.id).all()
        if not issue_statuses:
            print("Creating default issue statuses...")
            create_default_issue_statuses(project)
            db.session.commit()
            issue_statuses = IssueStatus.query.filter_by(project_id=project.id).all()
        
        # Build lookup dicts
        type_map = {t.name: t for t in issue_types}
        status_map = {s.name: s for s in issue_statuses}
        
        print(f"Available types: {list(type_map.keys())}")
        print(f"Available statuses: {list(status_map.keys())}")
        print("-" * 60)
        
        # Get project members for random assignment
        members = ProjectMember.query.filter_by(project_id=project.id).all()
        member_users = [m.user for m in members] if members else []
        
        # Get all users if no members
        if not member_users:
            member_users = User.query.filter_by(is_active=True).limit(5).all()
        
        print(f"Available assignees: {[u.name for u in member_users]}")
        print("-" * 60)
        
        # Check existing issues
        existing_count = Issue.query.filter_by(project_id=project.id).count()
        if existing_count > 5:
            print(f"Project already has {existing_count} issues. Skipping creation.")
            print("To recreate, delete existing issues first.")
            return True
        
        created = 0
        today = datetime.now().date()
        
        for i, data in enumerate(SAMPLE_ISSUES):
            # Find issue type
            issue_type = type_map.get(data['type'])
            if not issue_type:
                # Try English name or fallback
                for t in issue_types:
                    if data['type'].lower() in t.name.lower() or data['type'].lower() in (t.name_en or '').lower():
                        issue_type = t
                        break
            
            if not issue_type:
                print(f"  SKIP: Type '{data['type']}' not found")
                continue
            
            # Find status (default to first/initial status)
            status_name = data.get('status', 'Offen')
            issue_status = status_map.get(status_name)
            if not issue_status:
                for s in issue_statuses:
                    if status_name.lower() in s.name.lower() or status_name.lower() in (s.name_en or '').lower():
                        issue_status = s
                        break
            
            if not issue_status:
                issue_status = next((s for s in issue_statuses if s.is_initial), issue_statuses[0])
            
            # Calculate due date
            due_date = None
            if 'due_days' in data:
                due_date = today + timedelta(days=data['due_days'])
            
            # Random assignee (70% chance to assign)
            assignee = None
            if member_users and random.random() < 0.7:
                assignee = random.choice(member_users)
            
            # Generate issue key
            issue_number = project.issue_counter + 1
            issue_key = f"{project.key}-{issue_number}"
            
            # Create issue
            issue = Issue(
                project_id=project.id,
                key=issue_key,
                type_id=issue_type.id,
                status_id=issue_status.id,
                summary=data['summary'],
                description=data.get('description', ''),
                priority=data.get('priority', 3),
                story_points=data.get('story_points'),
                labels=data.get('labels', []),
                due_date=due_date,
                assignee_id=assignee.id if assignee else None,
                reporter_id=member_users[0].id if member_users else None,
                backlog_position=i + 1,
            )
            
            db.session.add(issue)
            project.issue_counter = issue_number
            created += 1
            
            status_indicator = "✓" if issue_status.is_final else "○"
            assignee_name = assignee.name if assignee else "Unassigned"
            print(f"  {status_indicator} {issue_key}: {data['summary'][:40]}... [{issue_type.name}] -> {assignee_name}")
        
        db.session.commit()
        
        print("-" * 60)
        print(f"Created {created} issues in project {project.key}")
        print(f"Total issues now: {Issue.query.filter_by(project_id=project.id).count()}")
        
        return True


if __name__ == '__main__':
    success = create_sample_issues()
    sys.exit(0 if success else 1)

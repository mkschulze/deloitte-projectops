#!/usr/bin/env python3
"""Create sample sprints for testing"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from extensions import db
from modules.projects.models import Project, Sprint, Issue
from datetime import datetime, timedelta

app = create_app()
with app.app_context():
    # Get TAX project
    project = Project.query.filter_by(key='TAX').first()
    if not project:
        print("TAX Projekt nicht gefunden!")
        exit(1)
    
    print(f"Projekt: {project.name} (ID: {project.id})")
    
    # Delete existing sprints
    existing = Sprint.query.filter_by(project_id=project.id).count()
    if existing > 0:
        Sprint.query.filter_by(project_id=project.id).delete()
        Issue.query.filter_by(project_id=project.id).update({'sprint_id': None})
        db.session.commit()
        print(f"{existing} existierende Sprints gelöscht.")
    
    # Create sprints
    today = datetime.now().date()
    
    sprints_data = [
        {
            'name': 'Sprint 1 - Grundlagen',
            'goal': 'Basis-Infrastruktur und erste Steuerarten implementieren',
            'start_date': today - timedelta(days=28),
            'end_date': today - timedelta(days=15),
            'state': 'closed',
            'started_at': datetime.now() - timedelta(days=28),
            'completed_at': datetime.now() - timedelta(days=15)
        },
        {
            'name': 'Sprint 2 - Erweiterung',
            'goal': 'Weitere Steuerarten und Benutzer-Workflows',
            'start_date': today - timedelta(days=14),
            'end_date': today + timedelta(days=0),
            'state': 'active',
            'started_at': datetime.now() - timedelta(days=14),
            'completed_at': None
        },
        {
            'name': 'Sprint 3 - Optimierung',
            'goal': 'Performance-Verbesserungen und Bug-Fixes',
            'start_date': today + timedelta(days=1),
            'end_date': today + timedelta(days=14),
            'state': 'future',
            'started_at': None,
            'completed_at': None
        },
        {
            'name': 'Sprint 4 - Release',
            'goal': 'Finale Tests und Go-Live Vorbereitung',
            'start_date': today + timedelta(days=15),
            'end_date': today + timedelta(days=28),
            'state': 'future',
            'started_at': None,
            'completed_at': None
        }
    ]
    
    created_sprints = []
    for data in sprints_data:
        sprint = Sprint(
            project_id=project.id,
            name=data['name'],
            goal=data['goal'],
            start_date=data['start_date'],
            end_date=data['end_date'],
            state=data['state'],
            started_at=data['started_at'],
            completed_at=data['completed_at']
        )
        db.session.add(sprint)
        created_sprints.append(sprint)
    
    db.session.commit()
    print(f"\n{len(created_sprints)} Sprints erstellt:")
    for s in created_sprints:
        print(f"  - {s.name} [{s.state}]")
    
    # Assign issues to sprints
    issues = Issue.query.filter_by(project_id=project.id, is_archived=False).all()
    
    if issues:
        active_sprint = next((s for s in created_sprints if s.state == 'active'), None)
        closed_sprint = next((s for s in created_sprints if s.state == 'closed'), None)
        future_sprint = next((s for s in created_sprints if s.state == 'future'), None)
        
        assigned_count = 0
        for i, issue in enumerate(issues):
            if i < 4 and closed_sprint:
                issue.sprint_id = closed_sprint.id
                assigned_count += 1
            elif i < 12 and active_sprint:
                issue.sprint_id = active_sprint.id
                assigned_count += 1
            elif i < 15 and future_sprint:
                issue.sprint_id = future_sprint.id
                assigned_count += 1
        
        db.session.commit()
        print(f"\n{assigned_count} Issues den Sprints zugewiesen:")
        print(f"  - Sprint 1 (closed): {Issue.query.filter_by(sprint_id=closed_sprint.id).count()} Issues")
        print(f"  - Sprint 2 (active): {Issue.query.filter_by(sprint_id=active_sprint.id).count()} Issues")
        print(f"  - Sprint 3 (future): {Issue.query.filter_by(sprint_id=future_sprint.id).count()} Issues")
        print(f"  - Backlog: {Issue.query.filter_by(project_id=project.id, sprint_id=None, is_archived=False).count()} Issues")
    
    print("\n✅ Beispieldaten für Sprints erstellt!")

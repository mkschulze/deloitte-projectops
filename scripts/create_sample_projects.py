#!/usr/bin/env python
"""
Create sample projects for testing the Projects module.
Run with: python scripts/create_sample_projects.py
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from extensions import db
from modules.projects.models import Project, ProjectMember
from models import User


SAMPLE_PROJECTS = [
    {
        'key': 'TAX',
        'name': 'Steuerliche Compliance',
        'name_en': 'Tax Compliance',
        'description': 'Steuerliche Pflichten und Fristen für alle Gesellschaften',
        'description_en': 'Tax obligations and deadlines for all entities',
        'category': 'Tax',
        'icon': 'bi-calculator',
        'color': '#86BC25'
    },
    {
        'key': 'AUD',
        'name': 'Jahresabschlussprüfung',
        'name_en': 'Annual Audit',
        'description': 'Vorbereitung und Durchführung der Jahresabschlussprüfung',
        'description_en': 'Preparation and execution of annual audit',
        'category': 'Audit',
        'icon': 'bi-clipboard-check',
        'color': '#0076A8'
    },
    {
        'key': 'INT',
        'name': 'Interne Projekte',
        'name_en': 'Internal Projects',
        'description': 'Interne Verbesserungsprojekte und Initiativen',
        'description_en': 'Internal improvement projects and initiatives',
        'category': 'Internal',
        'icon': 'bi-gear',
        'color': '#DA291C'
    }
]


def create_sample_projects():
    """Create sample projects if they don't exist."""
    with app.app_context():
        # Get admin user (by role, not username)
        admin = User.query.filter_by(role='admin').first()
        if not admin:
            admin = User.query.first()
        
        if not admin:
            print("ERROR: No users found in database. Run 'flask createadmin' first.")
            return False
        
        print(f"Using user: {admin.name} ({admin.email})")
        print(f"Existing projects: {Project.query.count()}")
        print("-" * 40)
        
        created = 0
        for data in SAMPLE_PROJECTS:
            # Skip if already exists
            existing = Project.query.filter_by(key=data['key']).first()
            if existing:
                print(f"  SKIP: {data['key']} already exists")
                continue
            
            # Create project
            project = Project(
                key=data['key'],
                name=data['name'],
                name_en=data['name_en'],
                description=data['description'],
                description_en=data['description_en'],
                category=data['category'],
                icon=data['icon'],
                color=data['color'],
                lead_id=admin.id,
                created_by_id=admin.id
            )
            db.session.add(project)
            db.session.flush()
            
            # Add admin as project admin
            member = ProjectMember(
                project_id=project.id,
                user_id=admin.id,
                role='admin',
                added_by_id=admin.id
            )
            db.session.add(member)
            
            created += 1
            print(f"  CREATE: {data['key']} - {data['name']}")
        
        db.session.commit()
        
        print("-" * 40)
        print(f"Created: {created} new projects")
        print(f"Total projects: {Project.query.count()}")
        return True


if __name__ == '__main__':
    success = create_sample_projects()
    sys.exit(0 if success else 1)

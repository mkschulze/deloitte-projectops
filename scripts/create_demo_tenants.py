#!/usr/bin/env python3
"""
Create Demo Tenants Script

Creates sample tenants with demo data for testing multi-tenancy.
Run with: python scripts/create_demo_tenants.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from app import app, db
from models import (
    Tenant, TenantMembership, User, Team, Entity, TaxType, 
    Task, TaskPreset
)


def create_demo_tenants():
    """Create demo tenants with sample data"""
    
    with app.app_context():
        print("=" * 60)
        print("Creating Demo Tenants for Multi-Tenancy Testing")
        print("=" * 60)
        
        # Get or create super-admin user
        admin_user = User.query.filter_by(email='admin@example.com').first()
        if not admin_user:
            admin_user = User.query.filter(User.role == 'admin').first()
        if not admin_user:
            admin_user = User.query.first()
        if not admin_user:
            print("\n⚠️  No users found. Please run init_db.py first.")
            return
        
        # Make sure admin is super-admin
        if not admin_user.is_superadmin:
            admin_user.is_superadmin = True
            db.session.commit()
            print("✓ Set admin@deloitte.de as Super-Admin")
        
        # =========================================================
        # TENANT 1: Deloitte Germany
        # =========================================================
        print("\n" + "-" * 40)
        print("Creating Tenant: Deloitte Germany")
        print("-" * 40)
        
        tenant1 = Tenant.query.filter_by(slug='deloitte_germany').first()
        if not tenant1:
            tenant1 = Tenant(
                slug='deloitte_germany',
                name='Deloitte Deutschland',
                is_active=True,
                created_by_id=admin_user.id
            )
            db.session.add(tenant1)
            db.session.commit()
            print("✓ Created tenant: Deloitte Deutschland")
        else:
            print("• Tenant already exists: Deloitte Deutschland")
        
        # Add admin to tenant 1
        membership1 = TenantMembership.query.filter_by(
            tenant_id=tenant1.id, user_id=admin_user.id
        ).first()
        if not membership1:
            membership1 = TenantMembership(
                tenant_id=tenant1.id,
                user_id=admin_user.id,
                role='admin'
            )
            db.session.add(membership1)
            db.session.commit()
            print("✓ Added admin as tenant admin")
        
        # Update existing data to belong to tenant 1
        updated_teams = Team.query.filter_by(tenant_id=None).update({'tenant_id': tenant1.id})
        updated_entities = Entity.query.filter_by(tenant_id=None).update({'tenant_id': tenant1.id})
        updated_tax_types = TaxType.query.filter_by(tenant_id=None).update({'tenant_id': tenant1.id})
        updated_tasks = Task.query.filter_by(tenant_id=None).update({'tenant_id': tenant1.id})
        updated_presets = TaskPreset.query.filter_by(tenant_id=None).update({'tenant_id': tenant1.id})
        db.session.commit()
        
        if any([updated_teams, updated_entities, updated_tax_types, updated_tasks, updated_presets]):
            print(f"✓ Migrated existing data to tenant 1:")
            print(f"  - {updated_teams} Teams")
            print(f"  - {updated_entities} Entities")
            print(f"  - {updated_tax_types} Tax Types")
            print(f"  - {updated_tasks} Tasks")
            print(f"  - {updated_presets} Task Presets")
        
        # Add existing users to tenant 1
        all_users = User.query.all()
        for user in all_users:
            if not TenantMembership.query.filter_by(tenant_id=tenant1.id, user_id=user.id).first():
                role = 'admin' if user.role in ['admin', 'Admin'] else 'member'
                membership = TenantMembership(
                    tenant_id=tenant1.id,
                    user_id=user.id,
                    role=role
                )
                db.session.add(membership)
        db.session.commit()
        print(f"✓ Added {len(all_users)} users to tenant 1")
        
        # =========================================================
        # TENANT 2: Demo Client
        # =========================================================
        print("\n" + "-" * 40)
        print("Creating Tenant: Demo Client GmbH")
        print("-" * 40)
        
        tenant2 = Tenant.query.filter_by(slug='demo_client').first()
        if not tenant2:
            tenant2 = Tenant(
                slug='demo_client',
                name='Demo Client GmbH',
                is_active=True,
                created_by_id=admin_user.id
            )
            db.session.add(tenant2)
            db.session.commit()
            print("✓ Created tenant: Demo Client GmbH")
        else:
            print("• Tenant already exists: Demo Client GmbH")
        
        # Add admin to tenant 2
        membership2 = TenantMembership.query.filter_by(
            tenant_id=tenant2.id, user_id=admin_user.id
        ).first()
        if not membership2:
            membership2 = TenantMembership(
                tenant_id=tenant2.id,
                user_id=admin_user.id,
                role='admin'
            )
            db.session.add(membership2)
            db.session.commit()
            print("✓ Added admin as tenant admin")
        
        # Create sample entity for tenant 2
        demo_entity = Entity.query.filter_by(name='Demo Holding AG', tenant_id=tenant2.id).first()
        if not demo_entity:
            demo_entity = Entity(
                name='Demo Holding AG',
                tenant_id=tenant2.id
            )
            db.session.add(demo_entity)
            db.session.commit()
            print("✓ Created demo entity: Demo Holding AG")
        
        # Create sample tax types for tenant 2
        demo_tax_types = [
            ('USt', 'Umsatzsteuer', 'VAT'),
            ('KSt', 'Körperschaftsteuer', 'Corporate Tax'),
            ('GewSt', 'Gewerbesteuer', 'Trade Tax'),
        ]
        for code, name_de, name_en in demo_tax_types:
            existing = TaxType.query.filter_by(code=code, tenant_id=tenant2.id).first()
            if not existing:
                tax_type = TaxType(
                    code=code,
                    name=name_de,
                    name_en=name_en,
                    tenant_id=tenant2.id
                )
                db.session.add(tax_type)
        db.session.commit()
        print("✓ Created demo tax types")
        
        # Create sample team for tenant 2
        demo_team = Team.query.filter_by(name='Demo Tax Team', tenant_id=tenant2.id).first()
        if not demo_team:
            demo_team = Team(
                name='Demo Tax Team',
                name_en='Demo Tax Team',
                description='Demo team for testing',
                tenant_id=tenant2.id
            )
            db.session.add(demo_team)
            db.session.commit()
            print("✓ Created demo team")
        
        # =========================================================
        # TENANT 3: Inactive/Archived Demo
        # =========================================================
        print("\n" + "-" * 40)
        print("Creating Tenant: Archived Client (for testing)")
        print("-" * 40)
        
        tenant3 = Tenant.query.filter_by(slug='archived_client').first()
        if not tenant3:
            tenant3 = Tenant(
                slug='archived_client',
                name='Archivierter Mandant',
                is_active=False,
                is_archived=True,
                archived_at=datetime.utcnow(),
                archived_by_id=admin_user.id,
                created_by_id=admin_user.id
            )
            db.session.add(tenant3)
            db.session.commit()
            print("✓ Created archived tenant for testing")
        else:
            print("• Archived tenant already exists")
        
        # Set admin's default tenant
        admin_user.current_tenant_id = tenant1.id
        db.session.commit()
        
        # =========================================================
        # Summary
        # =========================================================
        print("\n" + "=" * 60)
        print("✅ Demo Tenants Created Successfully!")
        print("=" * 60)
        
        tenants = Tenant.query.all()
        print(f"\nTotal Tenants: {len(tenants)}")
        for t in tenants:
            member_count = len(t.members)
            status = "🟢 Active" if t.is_active and not t.is_archived else "🔴 Archived" if t.is_archived else "🟡 Inactive"
            print(f"  • {t.name} ({t.slug}) - {status} - {member_count} members")
        
        print("\n👤 Super-Admin: admin@example.com")
        print("   Can access all tenants and manage them.")
        print("\n🔗 Access: http://127.0.0.1:5000/admin/tenants")


if __name__ == '__main__':
    create_demo_tenants()

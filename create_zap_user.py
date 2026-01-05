#!/usr/bin/env python3
"""
Create a pentest user for ZAP scanning.
This user is exempt from rate limiting.
"""
from app import create_app
from extensions import db
from models import User, Tenant

app = create_app()

with app.app_context():
    # Check if pentest user already exists
    existing = User.query.filter_by(email='pentest@zap.local').first()
    if existing:
        print(f"✅ ZAP Pentest user already exists: {existing.email}")
    else:
        # Get default tenant
        tenant = Tenant.query.first()
        if not tenant:
            print("❌ No tenant found! Create a tenant first.")
            exit(1)
        
        # Create pentest user
        user = User(
            email='pentest@zap.local',
            name='ZAP Pentest',
            role='admin',  # Admin to scan all pages
            current_tenant_id=tenant.id,
            is_active=True
        )
        user.set_password('ZapTest2026!')
        
        db.session.add(user)
        db.session.commit()
        
        print("=" * 50)
        print("🔐 ZAP PENTEST USER CREATED")
        print("=" * 50)
        print(f"Email:    pentest@zap.local")
        print(f"Password: ZapTest2026!")
        print(f"Role:     admin")
        print(f"Tenant:   {tenant.name}")
        print("=" * 50)
        print("⚠️  This user is exempt from rate limiting!")
        print("⚠️  Delete after pen testing is complete.")
        print("=" * 50)

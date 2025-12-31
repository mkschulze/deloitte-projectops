#!/usr/bin/env python3
"""Create demo tasks based on TaskPreset templates."""

from app import app, db
from models import TaskPreset, Task, Entity, User, TaxType
from datetime import date, timedelta
import random

def create_demo_tasks():
    with app.app_context():
        # Get existing data
        presets = TaskPreset.query.limit(25).all()
        entities = Entity.query.all()
        users = User.query.all()
        
        print(f"Found {len(presets)} presets, {len(entities)} entities, {len(users)} users")
        
        if not presets or not entities or not users:
            print("Error: Missing required data (presets, entities, or users)")
            return
        
        # Create demo tasks
        created_count = 0
        
        for i, preset in enumerate(presets):
            # Rotate through entities and users
            entity = entities[i % len(entities)]
            user = users[i % len(users)]
            
            # Vary due dates: some past, some current, some future
            if i % 5 == 0:
                due = date(2024, random.randint(6, 12), random.randint(1, 28))  # Past
                status = 'completed'
            elif i % 5 == 1:
                due = date(2025, 1, random.randint(1, 28))  # Current month
                status = 'in_review'
            elif i % 5 == 2:
                due = date(2025, random.randint(2, 6), random.randint(1, 28))  # Near future
                status = 'in_progress'
            elif i % 5 == 3:
                due = date(2025, random.randint(7, 12), random.randint(1, 28))  # Later this year
                status = 'draft'
            else:
                due = date(2026, random.randint(1, 6), random.randint(1, 28))  # Next year
                status = 'draft'
            
            # Get tax_type_id from the preset's tax_type code
            tax_type_id = None
            if preset.tax_type:
                tt = TaxType.query.filter_by(code=preset.tax_type).first()
                if tt:
                    tax_type_id = tt.id
            
            task = Task(
                title=preset.title_de or preset.title or f"Aufgabe {i+1}",
                description=preset.description or preset.description_de or "",
                due_date=due,
                status=status,
                entity_id=entity.id,
                owner_id=user.id,
                year=due.year,
                preset_id=preset.id
            )
            db.session.add(task)
            created_count += 1
            print(f"Created: {task.title[:50]}... (Status: {status}, Due: {due})")
        
        db.session.commit()
        print(f"\n✅ Successfully created {created_count} demo tasks!")

if __name__ == "__main__":
    create_demo_tasks()

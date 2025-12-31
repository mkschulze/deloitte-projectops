"""
Deloitte Flask App Template - Database Initialization
Run: python init_db.py
"""
from app import app
from extensions import db
from models import User, TaxType, Entity, Team


def init_database():
    """Initialize database with tables and default admin user"""
    with app.app_context():
        # Create all tables
        db.create_all()
        print('✓ Database tables created')
        
        # Check if admin exists
        admin = User.query.filter_by(email='admin@example.com').first()
        if not admin:
            admin = User(
                email='admin@example.com',
                name='Administrator',
                role='admin',
                is_active=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print('✓ Admin user created: admin@example.com / admin123')
        else:
            print('• Admin user already exists')
        
        # Create demo user
        user = User.query.filter_by(email='user@example.com').first()
        if not user:
            user = User(
                email='user@example.com',
                name='Demo User',
                role='user',
                is_active=True
            )
            user.set_password('user123')
            db.session.add(user)
            db.session.commit()
            print('✓ Demo user created: user@example.com / user123')
        else:
            print('• Demo user already exists')
        
        # Create default tax types with multilingual names
        tax_types_data = [
            {'code': 'EST', 'name': 'Einkommensteuer', 'name_de': 'Einkommensteuer', 'name_en': 'Income Tax', 
             'description': 'Einkommensteuer für natürliche Personen', 'description_de': 'Einkommensteuer für natürliche Personen', 'description_en': 'Income tax for natural persons'},
            {'code': 'KOST', 'name': 'Körperschaftsteuer', 'name_de': 'Körperschaftsteuer', 'name_en': 'Corporate Tax',
             'description': 'Körperschaftsteuer für juristische Personen', 'description_de': 'Körperschaftsteuer für juristische Personen', 'description_en': 'Corporate tax for legal entities'},
            {'code': 'GEWST', 'name': 'Gewerbesteuer', 'name_de': 'Gewerbesteuer', 'name_en': 'Trade Tax',
             'description': 'Gewerbesteuer für Gewerbebetriebe', 'description_de': 'Gewerbesteuer für Gewerbebetriebe', 'description_en': 'Trade tax for businesses'},
            {'code': 'UST', 'name': 'Umsatzsteuer', 'name_de': 'Umsatzsteuer', 'name_en': 'VAT',
             'description': 'Umsatzsteuer / Mehrwertsteuer', 'description_de': 'Umsatzsteuer / Mehrwertsteuer', 'description_en': 'Value Added Tax'},
            {'code': 'LST', 'name': 'Lohnsteuer', 'name_de': 'Lohnsteuer', 'name_en': 'Payroll Tax',
             'description': 'Lohnsteuer für Arbeitnehmer', 'description_de': 'Lohnsteuer für Arbeitnehmer', 'description_en': 'Payroll tax for employees'},
            {'code': 'KAPEST', 'name': 'Kapitalertragsteuer', 'name_de': 'Kapitalertragsteuer', 'name_en': 'Capital Gains Tax',
             'description': 'Steuer auf Kapitalerträge', 'description_de': 'Steuer auf Kapitalerträge', 'description_en': 'Tax on capital gains'},
            {'code': 'OTHER', 'name': 'Sonstige', 'name_de': 'Sonstige', 'name_en': 'Other',
             'description': 'Sonstige Steuerarten', 'description_de': 'Sonstige Steuerarten', 'description_en': 'Other tax types'},
        ]
        
        for tt_data in tax_types_data:
            existing = TaxType.query.filter_by(code=tt_data['code']).first()
            if not existing:
                tax_type = TaxType(**tt_data, is_active=True)
                db.session.add(tax_type)
        db.session.commit()
        print('✓ Default tax types created')
        
        # Create default entities with multilingual names
        entities_data = [
            {'name': 'Hauptgesellschaft GmbH', 'name_de': 'Hauptgesellschaft GmbH', 'name_en': 'Main Company Ltd', 'is_active': True},
            {'name': 'Tochtergesellschaft 1 GmbH', 'name_de': 'Tochtergesellschaft 1 GmbH', 'name_en': 'Subsidiary 1 Ltd', 'is_active': True},
            {'name': 'Tochtergesellschaft 2 GmbH', 'name_de': 'Tochtergesellschaft 2 GmbH', 'name_en': 'Subsidiary 2 Ltd', 'is_active': True},
        ]
        
        for ent_data in entities_data:
            existing = Entity.query.filter_by(name=ent_data['name']).first()
            if not existing:
                entity = Entity(**ent_data)
                db.session.add(entity)
        db.session.commit()
        print('✓ Default entities created')
        
        # Create default teams with multilingual names
        teams_data = [
            {'name': 'Steuerabteilung', 'name_de': 'Steuerabteilung', 'name_en': 'Tax Department', 
             'description': 'Hauptverantwortlich für Steuererklärungen', 'description_de': 'Hauptverantwortlich für Steuererklärungen', 'description_en': 'Main responsibility for tax returns', 'is_active': True},
            {'name': 'Buchhaltung', 'name_de': 'Buchhaltung', 'name_en': 'Accounting',
             'description': 'Finanzbuchhaltung und Jahresabschluss', 'description_de': 'Finanzbuchhaltung und Jahresabschluss', 'description_en': 'Financial accounting and annual statements', 'is_active': True},
            {'name': 'Controlling', 'name_de': 'Controlling', 'name_en': 'Controlling',
             'description': 'Planung und Kostenrechnung', 'description_de': 'Planung und Kostenrechnung', 'description_en': 'Planning and cost accounting', 'is_active': True},
        ]
        
        for team_data in teams_data:
            existing = Team.query.filter_by(name=team_data['name']).first()
            if not existing:
                team = Team(**team_data)
                db.session.add(team)
        db.session.commit()
        print('✓ Default teams created')
        
        print('\n🚀 Database initialized successfully!')
        print('   Run: flask run --debug')


if __name__ == '__main__':
    init_database()

"""
Projects Module
Jira-like project management with Kanban boards, sprints, and issue tracking.
"""
from flask import Blueprint, url_for
from modules import BaseModule, ModuleRegistry


@ModuleRegistry.register
class ProjectsModule(BaseModule):
    """Project Management - Jira-like Issue Tracking"""
    
    code = 'projects'
    name_de = 'Projektmanagement'
    name_en = 'Project Management'
    description_de = 'Jira-ähnliche Projektverwaltung mit Kanban-Boards und Sprints'
    description_en = 'Jira-like project management with Kanban boards and sprints'
    icon = 'bi-kanban'
    nav_order = 20
    is_core = False  # Optional module
    
    _blueprint = None
    
    @classmethod
    def get_blueprint(cls):
        """Get or create the projects blueprint"""
        if cls._blueprint is None:
            cls._blueprint = Blueprint(
                'projects',
                __name__,
                template_folder='templates',
                url_prefix='/projects'
            )
            # Routes will be registered in PM-1
            # from .routes import register_routes
            # register_routes(cls._blueprint)
        return cls._blueprint
    
    @classmethod
    def get_nav_items(cls, user, lang='de'):
        """Navigation items for Projects module"""
        t = lambda de, en: de if lang == 'de' else en
        
        items = [
            {
                'label': t('Projekte', 'Projects'),
                'url': '/projects',
                'icon': 'bi-kanban',
                'children': [
                    {'label': t('Alle Projekte', 'All Projects'), 'url': '/projects'},
                    {'label': t('Neues Projekt', 'New Project'), 'url': '/projects/new'},
                ]
            },
        ]
        
        return items
    
    @classmethod
    def init_app(cls, app):
        """Initialize projects module"""
        bp = cls.get_blueprint()
        if bp:
            app.register_blueprint(bp)

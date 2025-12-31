"""
Project Management Module - Routes
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify
from flask_login import login_required, current_user

from extensions import db
from models import User
from translations import get_translation as t
from .models import Project, ProjectMember, ProjectRole

# Create blueprint
bp = Blueprint('projects', __name__, template_folder='templates', url_prefix='/projects')


def project_access_required(f):
    """Decorator to check project access"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        project_id = kwargs.get('project_id')
        if project_id:
            project = Project.query.get_or_404(project_id)
            if not project.is_member(current_user):
                flash('Kein Zugriff auf dieses Projekt.' if session.get('lang', 'de') == 'de' else 'No access to this project.', 'danger')
                return redirect(url_for('projects.project_list'))
            kwargs['project'] = project
        return f(*args, **kwargs)
    return decorated_function


def projects_module_required(f):
    """Decorator to check if user has access to projects module"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from models import Module, UserModule
        
        # Admins always have access
        if current_user.role == 'admin':
            return f(*args, **kwargs)
        
        # Check if projects module is active
        module = Module.query.filter_by(code='projects', is_active=True).first()
        if not module:
            flash('Projektmanagement-Modul ist nicht aktiv.' if session.get('lang', 'de') == 'de' else 'Project management module is not active.', 'warning')
            return redirect(url_for('dashboard'))
        
        # Check if user has module assignment
        user_module = UserModule.query.filter_by(user_id=current_user.id, module_id=module.id).first()
        if not user_module:
            flash('Sie haben keinen Zugriff auf das Projektmanagement-Modul.' if session.get('lang', 'de') == 'de' else 'You do not have access to the project management module.', 'warning')
            return redirect(url_for('dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function


# ============================================================================
# PROJECT LIST & DASHBOARD
# ============================================================================

@bp.route('/')
@login_required
@projects_module_required
def project_list():
    """List all projects the user has access to"""
    lang = session.get('lang', 'de')
    
    # Get projects based on role
    if current_user.role == 'admin':
        projects = Project.query.filter_by(is_archived=False).order_by(Project.name).all()
    else:
        # Get projects where user is a member
        member_project_ids = [m.project_id for m in current_user.project_memberships]
        projects = Project.query.filter(
            Project.id.in_(member_project_ids),
            Project.is_archived == False
        ).order_by(Project.name).all()
    
    return render_template('projects/list.html', projects=projects, lang=lang)


# ============================================================================
# PROJECT CRUD
# ============================================================================

@bp.route('/new', methods=['GET', 'POST'])
@login_required
@projects_module_required
def project_new():
    """Create a new project"""
    lang = session.get('lang', 'de')
    
    # Only admins and managers can create projects
    if current_user.role not in ['admin', 'manager']:
        flash('Keine Berechtigung zum Erstellen von Projekten.' if lang == 'de' else 'No permission to create projects.', 'danger')
        return redirect(url_for('projects.project_list'))
    
    if request.method == 'POST':
        key = request.form.get('key', '').upper().strip()
        name = request.form.get('name', '').strip()
        name_en = request.form.get('name_en', '').strip()
        description = request.form.get('description', '').strip()
        description_en = request.form.get('description_en', '').strip()
        lead_id = request.form.get('lead_id', type=int)
        category = request.form.get('category', '').strip()
        icon = request.form.get('icon', 'bi-folder').strip()
        color = request.form.get('color', '#86BC25').strip()
        
        # Validation
        if not key or not name:
            flash('Projektschlüssel und Name sind erforderlich.' if lang == 'de' else 'Project key and name are required.', 'danger')
            return redirect(url_for('projects.project_new'))
        
        if len(key) > 10:
            flash('Projektschlüssel darf maximal 10 Zeichen lang sein.' if lang == 'de' else 'Project key must be at most 10 characters.', 'danger')
            return redirect(url_for('projects.project_new'))
        
        # Check if key already exists
        if Project.query.filter_by(key=key).first():
            flash('Projektschlüssel existiert bereits.' if lang == 'de' else 'Project key already exists.', 'danger')
            return redirect(url_for('projects.project_new'))
        
        project = Project(
            key=key,
            name=name,
            name_en=name_en or None,
            description=description or None,
            description_en=description_en or None,
            lead_id=lead_id,
            category=category or None,
            icon=icon,
            color=color,
            created_by_id=current_user.id
        )
        db.session.add(project)
        db.session.flush()  # Get project ID
        
        # Add creator as admin member
        member = ProjectMember(
            project_id=project.id,
            user_id=current_user.id,
            role='admin',
            added_by_id=current_user.id
        )
        db.session.add(member)
        
        # Add lead as member if different from creator
        if lead_id and lead_id != current_user.id:
            lead_member = ProjectMember(
                project_id=project.id,
                user_id=lead_id,
                role='lead',
                added_by_id=current_user.id
            )
            db.session.add(lead_member)
        
        db.session.commit()
        
        flash(f'Projekt {project.key} erstellt.' if lang == 'de' else f'Project {project.key} created.', 'success')
        return redirect(url_for('projects.project_detail', project_id=project.id))
    
    # GET request
    users = User.query.filter_by(is_active=True).order_by(User.name).all()
    return render_template('projects/form.html', project=None, users=users, lang=lang)


@bp.route('/<int:project_id>')
@login_required
@projects_module_required
@project_access_required
def project_detail(project_id, project=None):
    """Project detail/dashboard view"""
    lang = session.get('lang', 'de')
    
    if project is None:
        project = Project.query.get_or_404(project_id)
    
    # Get member list
    members = ProjectMember.query.filter_by(project_id=project_id).all()
    
    return render_template('projects/detail.html', project=project, members=members, lang=lang)


@bp.route('/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
@projects_module_required
@project_access_required
def project_edit(project_id, project=None):
    """Edit project settings"""
    lang = session.get('lang', 'de')
    
    if project is None:
        project = Project.query.get_or_404(project_id)
    
    # Check edit permission
    if not project.can_user_edit(current_user):
        flash('Keine Berechtigung zum Bearbeiten.' if lang == 'de' else 'No permission to edit.', 'danger')
        return redirect(url_for('projects.project_detail', project_id=project_id))
    
    if request.method == 'POST':
        project.name = request.form.get('name', '').strip()
        project.name_en = request.form.get('name_en', '').strip() or None
        project.description = request.form.get('description', '').strip() or None
        project.description_en = request.form.get('description_en', '').strip() or None
        project.lead_id = request.form.get('lead_id', type=int)
        project.category = request.form.get('category', '').strip() or None
        project.icon = request.form.get('icon', 'bi-folder').strip()
        project.color = request.form.get('color', '#86BC25').strip()
        
        db.session.commit()
        
        flash('Projekt aktualisiert.' if lang == 'de' else 'Project updated.', 'success')
        return redirect(url_for('projects.project_detail', project_id=project_id))
    
    users = User.query.filter_by(is_active=True).order_by(User.name).all()
    return render_template('projects/form.html', project=project, users=users, lang=lang)


@bp.route('/<int:project_id>/archive', methods=['POST'])
@login_required
@projects_module_required
@project_access_required
def project_archive(project_id, project=None):
    """Archive a project"""
    lang = session.get('lang', 'de')
    
    if project is None:
        project = Project.query.get_or_404(project_id)
    
    # Only admins can archive
    if project.get_member_role(current_user) != 'admin':
        flash('Keine Berechtigung zum Archivieren.' if lang == 'de' else 'No permission to archive.', 'danger')
        return redirect(url_for('projects.project_detail', project_id=project_id))
    
    from datetime import datetime
    project.is_archived = True
    project.archived_at = datetime.utcnow()
    db.session.commit()
    
    flash(f'Projekt {project.key} archiviert.' if lang == 'de' else f'Project {project.key} archived.', 'success')
    return redirect(url_for('projects.project_list'))


# ============================================================================
# PROJECT MEMBERS
# ============================================================================

@bp.route('/<int:project_id>/members')
@login_required
@projects_module_required
@project_access_required
def project_members(project_id, project=None):
    """Manage project members"""
    lang = session.get('lang', 'de')
    
    if project is None:
        project = Project.query.get_or_404(project_id)
    
    members = ProjectMember.query.filter_by(project_id=project_id).all()
    member_user_ids = [m.user_id for m in members]
    available_users = User.query.filter(
        User.is_active == True,
        ~User.id.in_(member_user_ids)
    ).order_by(User.name).all()
    
    can_edit = project.can_user_edit(current_user)
    
    return render_template('projects/members.html', 
                          project=project, 
                          members=members, 
                          available_users=available_users,
                          can_edit=can_edit,
                          lang=lang)


@bp.route('/<int:project_id>/members/add', methods=['POST'])
@login_required
@projects_module_required
@project_access_required
def project_member_add(project_id, project=None):
    """Add a member to the project"""
    lang = session.get('lang', 'de')
    
    if project is None:
        project = Project.query.get_or_404(project_id)
    
    if not project.can_user_edit(current_user):
        flash('Keine Berechtigung.' if lang == 'de' else 'No permission.', 'danger')
        return redirect(url_for('projects.project_members', project_id=project_id))
    
    user_id = request.form.get('user_id', type=int)
    role = request.form.get('role', 'member')
    
    if not user_id:
        flash('Benutzer erforderlich.' if lang == 'de' else 'User required.', 'danger')
        return redirect(url_for('projects.project_members', project_id=project_id))
    
    # Check if already member
    existing = ProjectMember.query.filter_by(project_id=project_id, user_id=user_id).first()
    if existing:
        flash('Benutzer ist bereits Mitglied.' if lang == 'de' else 'User is already a member.', 'warning')
        return redirect(url_for('projects.project_members', project_id=project_id))
    
    member = ProjectMember(
        project_id=project_id,
        user_id=user_id,
        role=role,
        added_by_id=current_user.id
    )
    db.session.add(member)
    db.session.commit()
    
    flash('Mitglied hinzugefügt.' if lang == 'de' else 'Member added.', 'success')
    return redirect(url_for('projects.project_members', project_id=project_id))


@bp.route('/<int:project_id>/members/<int:member_id>/remove', methods=['POST'])
@login_required
@projects_module_required
@project_access_required
def project_member_remove(project_id, member_id, project=None):
    """Remove a member from the project"""
    lang = session.get('lang', 'de')
    
    if project is None:
        project = Project.query.get_or_404(project_id)
    
    if not project.can_user_edit(current_user):
        flash('Keine Berechtigung.' if lang == 'de' else 'No permission.', 'danger')
        return redirect(url_for('projects.project_members', project_id=project_id))
    
    member = ProjectMember.query.get_or_404(member_id)
    
    # Can't remove last admin
    admin_count = ProjectMember.query.filter_by(project_id=project_id, role='admin').count()
    if member.role == 'admin' and admin_count <= 1:
        flash('Kann letzten Administrator nicht entfernen.' if lang == 'de' else 'Cannot remove last administrator.', 'danger')
        return redirect(url_for('projects.project_members', project_id=project_id))
    
    db.session.delete(member)
    db.session.commit()
    
    flash('Mitglied entfernt.' if lang == 'de' else 'Member removed.', 'success')
    return redirect(url_for('projects.project_members', project_id=project_id))


@bp.route('/<int:project_id>/members/<int:member_id>/role', methods=['POST'])
@login_required
@projects_module_required
@project_access_required
def project_member_role(project_id, member_id, project=None):
    """Change member role"""
    lang = session.get('lang', 'de')
    
    if project is None:
        project = Project.query.get_or_404(project_id)
    
    if not project.can_user_edit(current_user):
        flash('Keine Berechtigung.' if lang == 'de' else 'No permission.', 'danger')
        return redirect(url_for('projects.project_members', project_id=project_id))
    
    member = ProjectMember.query.get_or_404(member_id)
    new_role = request.form.get('role', 'member')
    
    # Can't demote last admin
    if member.role == 'admin' and new_role != 'admin':
        admin_count = ProjectMember.query.filter_by(project_id=project_id, role='admin').count()
        if admin_count <= 1:
            flash('Kann letzten Administrator nicht herabstufen.' if lang == 'de' else 'Cannot demote last administrator.', 'danger')
            return redirect(url_for('projects.project_members', project_id=project_id))
    
    member.role = new_role
    db.session.commit()
    
    flash('Rolle aktualisiert.' if lang == 'de' else 'Role updated.', 'success')
    return redirect(url_for('projects.project_members', project_id=project_id))


def register_routes(blueprint):
    """Register all routes - called from module __init__"""
    pass  # Routes are already registered via decorators

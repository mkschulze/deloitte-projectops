"""
Deloitte TaxOps Calendar
Tax Compliance Calendar & Deadline Tracking for enterprises.
"""
import json
import os
from datetime import datetime
from functools import wraps
from io import BytesIO

from flask import Flask, render_template, redirect, url_for, flash, request, session, send_file, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_migrate import Migrate

from config import config
from models import db, User, AuditLog, Entity, TaxType, TaskTemplate, Task, TaskEvidence, Comment, ReferenceApplication, UserRole, TaskPreset, TaskReviewer, Team
from translations import get_translation as t

# Flask-Migrate instance
migrate = Migrate()


# ============================================================================
# APP INITIALIZATION
# ============================================================================

def create_app(config_name='default'):
    """Application factory"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Login manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = 'Bitte melden Sie sich an.'
    login_manager.login_message_category = 'warning'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    return app


app = create_app()


# ============================================================================
# CONTEXT PROCESSORS
# ============================================================================

@app.context_processor
def inject_globals():
    """Inject global variables into all templates"""
    lang = session.get('lang', app.config.get('DEFAULT_LANGUAGE', 'de'))
    return {
        'app_name': app.config.get('APP_NAME', 'MyApp'),
        'app_version': app.config.get('APP_VERSION', '1.0.0'),
        'current_year': datetime.now().year,
        'lang': lang,
        't': lambda key: t(key, lang),
        'get_file_icon': get_file_icon
    }


def get_file_icon(filename):
    """Return Bootstrap icon class based on file extension"""
    if not filename or '.' not in filename:
        return 'bi-file-earmark'
    ext = filename.rsplit('.', 1)[1].lower()
    icons = {
        'pdf': 'bi-file-earmark-pdf text-danger',
        'doc': 'bi-file-earmark-word text-primary',
        'docx': 'bi-file-earmark-word text-primary',
        'xls': 'bi-file-earmark-excel text-success',
        'xlsx': 'bi-file-earmark-excel text-success',
        'csv': 'bi-file-earmark-spreadsheet text-success',
        'txt': 'bi-file-earmark-text',
        'png': 'bi-file-earmark-image text-info',
        'jpg': 'bi-file-earmark-image text-info',
        'jpeg': 'bi-file-earmark-image text-info',
        'gif': 'bi-file-earmark-image text-info',
        'zip': 'bi-file-earmark-zip text-warning',
    }
    return icons.get(ext, 'bi-file-earmark')


# ============================================================================
# DECORATORS
# ============================================================================

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin():
            flash('Keine Berechtigung für diese Aktion.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


def log_action(action, entity_type=None, entity_id=None, entity_name=None, old_value=None, new_value=None):
    """Log an action to the audit log"""
    log = AuditLog(
        user_id=current_user.id if current_user.is_authenticated else None,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        entity_name=entity_name,
        old_value=old_value,
        new_value=new_value,
        ip_address=request.remote_addr,
        user_agent=str(request.user_agent)[:500] if request.user_agent else None
    )
    db.session.add(log)
    db.session.commit()


# ============================================================================
# AUTH ROUTES
# ============================================================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                flash('Ihr Konto ist deaktiviert.', 'danger')
                return render_template('login.html')
            
            login_user(user, remember=remember)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            log_action('LOGIN', 'User', user.id, user.email)
            
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        
        flash('Ungültige Anmeldedaten.', 'danger')
    
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    """Logout user"""
    log_action('LOGOUT', 'User', current_user.id, current_user.email)
    logout_user()
    flash('Sie wurden abgemeldet.', 'success')
    return redirect(url_for('index'))


# ============================================================================
# MAIN ROUTES
# ============================================================================

@app.route('/')
def index():
    """Home page - redirect to dashboard if logged in"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard with task overview"""
    from datetime import date, timedelta
    
    # Get user's tasks
    if current_user.is_admin() or current_user.is_manager():
        # Admins and managers see all tasks
        base_query = Task.query
    else:
        # Others see only their tasks
        base_query = Task.query.filter(
            (Task.owner_id == current_user.id) | (Task.reviewer_id == current_user.id)
        )
    
    today = date.today()
    soon = today + timedelta(days=7)
    
    stats = {
        'total': base_query.count(),
        'overdue': base_query.filter(Task.due_date < today, Task.status != 'completed').count(),
        'due_soon': base_query.filter(Task.due_date >= today, Task.due_date <= soon, Task.status != 'completed').count(),
        'in_review': base_query.filter_by(status='in_review').count(),
        'completed': base_query.filter_by(status='completed').count(),
    }
    
    # My upcoming tasks
    my_tasks = base_query.filter(
        Task.status != 'completed'
    ).order_by(Task.due_date).limit(10).all()
    
    # Overdue tasks
    overdue_tasks = base_query.filter(
        Task.due_date < today,
        Task.status != 'completed'
    ).order_by(Task.due_date).limit(5).all()
    
    return render_template('dashboard.html', 
                         stats=stats, 
                         my_tasks=my_tasks, 
                         overdue_tasks=overdue_tasks,
                         today=today)


@app.route('/tasks')
@login_required
def task_list():
    """Task list with filters"""
    from datetime import date
    
    # Get filter parameters
    status_filter = request.args.get('status', '')
    entity_filter = request.args.get('entity', type=int)
    tax_type_filter = request.args.get('tax_type', type=int)
    year_filter = request.args.get('year', type=int, default=date.today().year)
    
    # Base query
    query = Task.query
    
    # Apply role-based filtering
    if not (current_user.is_admin() or current_user.is_manager()):
        query = query.filter(
            (Task.owner_id == current_user.id) | (Task.reviewer_id == current_user.id)
        )
    
    # Apply filters
    if status_filter:
        if status_filter == 'overdue':
            query = query.filter(Task.due_date < date.today(), Task.status != 'completed')
        elif status_filter == 'due_soon':
            from datetime import timedelta
            soon = date.today() + timedelta(days=7)
            query = query.filter(Task.due_date >= date.today(), Task.due_date <= soon, Task.status != 'completed')
        else:
            query = query.filter_by(status=status_filter)
    
    if entity_filter:
        query = query.filter_by(entity_id=entity_filter)
    
    if tax_type_filter:
        query = query.join(TaskTemplate).filter(TaskTemplate.tax_type_id == tax_type_filter)
    
    if year_filter:
        query = query.filter_by(year=year_filter)
    
    # Order by due date
    tasks = query.order_by(Task.due_date).all()
    
    # Get filter options
    entities = Entity.query.filter_by(is_active=True).order_by(Entity.name).all()
    tax_types = TaxType.query.filter_by(is_active=True).order_by(TaxType.code).all()
    years = db.session.query(Task.year).distinct().order_by(Task.year.desc()).all()
    years = [y[0] for y in years]
    
    return render_template('tasks/list.html', 
                         tasks=tasks, 
                         entities=entities,
                         tax_types=tax_types,
                         years=years,
                         current_filters={
                             'status': status_filter,
                             'entity': entity_filter,
                             'tax_type': tax_type_filter,
                             'year': year_filter
                         })


@app.route('/tasks/<int:task_id>')
@login_required
def task_detail(task_id):
    """Task detail view"""
    task = Task.query.get_or_404(task_id)
    
    # Check access (admin, manager, owner, or any assigned reviewer)
    if not (current_user.is_admin() or current_user.is_manager() or 
            task.owner_id == current_user.id or task.is_reviewer(current_user)):
        flash('Keine Berechtigung.', 'danger')
        return redirect(url_for('task_list'))
    
    # Get audit log for this task
    audit_logs = AuditLog.query.filter_by(
        entity_type='Task', 
        entity_id=task.id
    ).order_by(AuditLog.timestamp.desc()).all()
    
    return render_template('tasks/detail.html', task=task, audit_logs=audit_logs)


@app.route('/tasks/new', methods=['GET', 'POST'])
@login_required
def task_create():
    """Create a new task"""
    from datetime import date
    
    if request.method == 'POST':
        # Get form data
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        entity_id = request.form.get('entity_id', type=int)
        template_id = request.form.get('template_id', type=int) or None
        due_date_str = request.form.get('due_date', '')
        year = request.form.get('year', type=int, default=date.today().year)
        period = request.form.get('period', '').strip()
        owner_id = request.form.get('owner_id', type=int) or None
        owner_team_id = request.form.get('owner_team_id', type=int) or None
        reviewer_ids = request.form.getlist('reviewer_ids', type=int)
        reviewer_team_id = request.form.get('reviewer_team_id', type=int) or None
        
        # Validate required fields
        errors = []
        if not title:
            errors.append('Titel ist erforderlich.')
        if not entity_id:
            errors.append('Gesellschaft ist erforderlich.')
        if not due_date_str:
            errors.append('Fälligkeitsdatum ist erforderlich.')
        
        if errors:
            for error in errors:
                flash(error, 'danger')
        else:
            try:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
                
                task = Task(
                    title=title,
                    description=description,
                    entity_id=entity_id,
                    template_id=template_id,
                    due_date=due_date,
                    year=year,
                    period=period,
                    owner_id=owner_id,
                    owner_team_id=owner_team_id,
                    reviewer_team_id=reviewer_team_id,
                    status='draft'
                )
                db.session.add(task)
                db.session.flush()  # Get task ID for reviewers
                
                # Add multiple reviewers
                if reviewer_ids:
                    task.set_reviewers(reviewer_ids)
                
                db.session.commit()
                
                log_action('CREATE', 'Task', task.id, task.title)
                flash('Aufgabe erfolgreich erstellt.', 'success')
                return redirect(url_for('task_detail', task_id=task.id))
                
            except ValueError:
                flash('Ungültiges Datumsformat.', 'danger')
    
    # GET request - show form
    entities = Entity.query.filter_by(is_active=True).order_by(Entity.name).all()
    templates = TaskTemplate.query.filter_by(is_active=True).order_by(TaskTemplate.keyword).all()
    users = User.query.filter_by(is_active=True).order_by(User.name).all()
    teams = Team.query.filter_by(is_active=True).order_by(Team.name).all()
    presets = TaskPreset.query.filter_by(is_active=True).order_by(TaskPreset.category, TaskPreset.title).all()
    
    return render_template('tasks/form.html',
                         task=None,
                         entities=entities,
                         templates=templates,
                         users=users,
                         teams=teams,
                         presets=presets,
                         current_year=date.today().year)


@app.route('/tasks/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required
def task_edit(task_id):
    """Edit an existing task"""
    from datetime import date
    
    task = Task.query.get_or_404(task_id)
    
    # Check permission
    if not (current_user.is_admin() or current_user.is_manager() or task.owner_id == current_user.id):
        flash('Keine Berechtigung.', 'danger')
        return redirect(url_for('task_detail', task_id=task_id))
    
    if request.method == 'POST':
        old_values = f"title={task.title}, due_date={task.due_date}"
        
        task.title = request.form.get('title', '').strip()
        task.description = request.form.get('description', '').strip()
        task.entity_id = request.form.get('entity_id', type=int)
        task.template_id = request.form.get('template_id', type=int) or None
        task.year = request.form.get('year', type=int, default=date.today().year)
        task.period = request.form.get('period', '').strip()
        task.owner_id = request.form.get('owner_id', type=int) or None
        task.owner_team_id = request.form.get('owner_team_id', type=int) or None
        task.reviewer_team_id = request.form.get('reviewer_team_id', type=int) or None
        
        # Handle multiple reviewers
        reviewer_ids = request.form.getlist('reviewer_ids', type=int)
        task.set_reviewers(reviewer_ids)
        
        due_date_str = request.form.get('due_date', '')
        if due_date_str:
            try:
                task.due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Ungültiges Datumsformat.', 'danger')
                return redirect(url_for('task_edit', task_id=task_id))
        
        db.session.commit()
        
        new_values = f"title={task.title}, due_date={task.due_date}"
        log_action('UPDATE', 'Task', task.id, task.title, old_values, new_values)
        
        flash('Aufgabe erfolgreich aktualisiert.', 'success')
        return redirect(url_for('task_detail', task_id=task_id))
    
    # GET request
    entities = Entity.query.filter_by(is_active=True).order_by(Entity.name).all()
    templates = TaskTemplate.query.filter_by(is_active=True).order_by(TaskTemplate.keyword).all()
    users = User.query.filter_by(is_active=True).order_by(User.name).all()
    teams = Team.query.filter_by(is_active=True).order_by(Team.name).all()
    
    return render_template('tasks/form.html',
                         task=task,
                         entities=entities,
                         templates=templates,
                         users=users,
                         teams=teams,
                         current_year=date.today().year)


@app.route('/tasks/<int:task_id>/status', methods=['POST'])
@login_required
def task_change_status(task_id):
    """Change task status with multi-stage approval workflow"""
    task = Task.query.get_or_404(task_id)
    new_status = request.form.get('status')
    note = request.form.get('note', '').strip()
    
    # Check if transition is allowed
    if not task.can_transition_to(new_status, current_user):
        flash('Diese Statusänderung ist nicht erlaubt.', 'danger')
        return redirect(url_for('task_detail', task_id=task_id))
    
    try:
        old_status = task.transition_to(new_status, current_user, note)
        db.session.commit()
        log_action('STATUS_CHANGE', 'Task', task.id, task.title, old_status, new_status)
        
        # Status-specific messages
        status_messages = {
            'submitted': 'Aufgabe eingereicht. Wartet auf Prüfung.',
            'in_review': 'Aufgabe wird geprüft.',
            'approved': 'Aufgabe genehmigt. Kann abgeschlossen werden.',
            'completed': 'Aufgabe erfolgreich abgeschlossen.',
            'rejected': 'Aufgabe zur Überarbeitung zurückgewiesen.',
            'draft': 'Aufgabe zurück in Bearbeitung.',
        }
        flash(status_messages.get(new_status, f'Status geändert: {old_status} → {new_status}'), 'success')
        
    except ValueError as e:
        flash(str(e), 'danger')
    
    return redirect(url_for('task_detail', task_id=task_id))


@app.route('/tasks/<int:task_id>/reviewer-action', methods=['POST'])
@login_required
def task_reviewer_action(task_id):
    """Handle individual reviewer approval/rejection"""
    task = Task.query.get_or_404(task_id)
    action = request.form.get('action')
    note = request.form.get('note', '').strip()
    
    # Check if user is a reviewer for this task
    if not task.is_reviewer(current_user):
        flash('Sie sind kein Prüfer für diese Aufgabe.', 'danger')
        return redirect(url_for('task_detail', task_id=task_id))
    
    # Check if task is in review
    if task.status != 'in_review':
        flash('Die Aufgabe muss sich in Prüfung befinden.', 'danger')
        return redirect(url_for('task_detail', task_id=task_id))
    
    if action == 'approve':
        task.approve_by_reviewer(current_user, note)
        db.session.commit()
        log_action('REVIEWER_APPROVE', 'Task', task.id, task.title, 
                   f'Reviewer: {current_user.name}', note or 'No note')
        
        # Check if all reviewers have approved
        if task.all_reviewers_approved():
            # Auto-transition to approved
            old_status = task.status
            task.status = 'approved'
            task.approved_by_id = current_user.id
            task.approved_at = datetime.utcnow()
            db.session.commit()
            log_action('STATUS_CHANGE', 'Task', task.id, task.title, old_status, 'approved')
            flash('Alle Prüfer haben genehmigt. Aufgabe ist nun genehmigt.', 'success')
        else:
            remaining = task.reviewers.count() - task.get_approval_count()
            flash(f'Ihre Genehmigung wurde gespeichert. Noch {remaining} Prüfer ausstehend.', 'success')
    
    elif action == 'reject':
        task.reject_by_reviewer(current_user, note)
        db.session.commit()
        log_action('REVIEWER_REJECT', 'Task', task.id, task.title, 
                   f'Reviewer: {current_user.name}', note or 'No note')
        
        # Auto-transition to rejected if any reviewer rejects
        old_status = task.status
        task.status = 'rejected'
        task.rejected_by_id = current_user.id
        task.rejected_at = datetime.utcnow()
        task.rejection_reason = note
        db.session.commit()
        log_action('STATUS_CHANGE', 'Task', task.id, task.title, old_status, 'rejected')
        flash('Aufgabe wurde von Ihnen abgelehnt und zur Überarbeitung zurückgewiesen.', 'warning')
    
    return redirect(url_for('task_detail', task_id=task_id))


# ============================================================================
# TASK EVIDENCE (File Upload & Links)
# ============================================================================

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config.get('ALLOWED_EXTENSIONS', set())


@app.route('/tasks/<int:task_id>/evidence/upload', methods=['POST'])
@login_required
def task_upload_evidence(task_id):
    """Upload file evidence to a task"""
    import os
    import uuid
    from werkzeug.utils import secure_filename
    
    task = Task.query.get_or_404(task_id)
    
    # Check permission (admin, manager, owner, or any assigned reviewer)
    if not (current_user.is_admin() or current_user.is_manager() or 
            current_user.id == task.owner_id or task.is_reviewer(current_user)):
        flash('Keine Berechtigung zum Hochladen.', 'danger')
        return redirect(url_for('task_detail', task_id=task_id))
    
    if 'file' not in request.files:
        flash('Keine Datei ausgewählt.', 'warning')
        return redirect(url_for('task_detail', task_id=task_id))
    
    file = request.files['file']
    if file.filename == '':
        flash('Keine Datei ausgewählt.', 'warning')
        return redirect(url_for('task_detail', task_id=task_id))
    
    if file and allowed_file(file.filename):
        # Secure the filename and make it unique
        original_filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{original_filename}"
        
        # Create task-specific folder
        upload_folder = os.path.join(app.config['UPLOAD_FOLDER'], f'task_{task_id}')
        os.makedirs(upload_folder, exist_ok=True)
        
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Create evidence record
        evidence = TaskEvidence(
            task_id=task_id,
            evidence_type='file',
            filename=original_filename,
            file_path=file_path,
            file_size=file_size,
            mime_type=file.content_type,
            uploaded_by_id=current_user.id
        )
        db.session.add(evidence)
        db.session.commit()
        
        log_action('UPLOAD', 'Task', task_id, task.title, None, f'Datei: {original_filename}')
        flash(f'Datei "{original_filename}" erfolgreich hochgeladen.', 'success')
    else:
        allowed = ', '.join(app.config.get('ALLOWED_EXTENSIONS', []))
        flash(f'Dateityp nicht erlaubt. Erlaubte Formate: {allowed}', 'danger')
    
    return redirect(url_for('task_detail', task_id=task_id) + '#evidence')


@app.route('/tasks/<int:task_id>/evidence/link', methods=['POST'])
@login_required
def task_add_link(task_id):
    """Add link evidence to a task"""
    task = Task.query.get_or_404(task_id)
    
    # Check permission (admin, manager, owner, or any assigned reviewer)
    if not (current_user.is_admin() or current_user.is_manager() or 
            current_user.id == task.owner_id or task.is_reviewer(current_user)):
        flash('Keine Berechtigung.', 'danger')
        return redirect(url_for('task_detail', task_id=task_id))
    
    url = request.form.get('url', '').strip()
    link_title = request.form.get('link_title', '').strip()
    
    if not url:
        flash('URL ist erforderlich.', 'warning')
        return redirect(url_for('task_detail', task_id=task_id))
    
    # Basic URL validation
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    evidence = TaskEvidence(
        task_id=task_id,
        evidence_type='link',
        url=url,
        link_title=link_title or url[:100],
        uploaded_by_id=current_user.id
    )
    db.session.add(evidence)
    db.session.commit()
    
    log_action('LINK_ADD', 'Task', task_id, task.title, None, f'Link: {link_title or url[:50]}')
    flash('Link erfolgreich hinzugefügt.', 'success')
    
    return redirect(url_for('task_detail', task_id=task_id) + '#evidence')


@app.route('/tasks/<int:task_id>/evidence/<int:evidence_id>/download')
@login_required
def task_download_evidence(task_id, evidence_id):
    """Download file evidence"""
    import os
    
    evidence = TaskEvidence.query.filter_by(id=evidence_id, task_id=task_id).first_or_404()
    
    if evidence.evidence_type != 'file':
        flash('Nur Dateien können heruntergeladen werden.', 'warning')
        return redirect(url_for('task_detail', task_id=task_id))
    
    if not os.path.exists(evidence.file_path):
        flash('Datei nicht gefunden.', 'danger')
        return redirect(url_for('task_detail', task_id=task_id))
    
    return send_file(evidence.file_path, as_attachment=True, download_name=evidence.filename)


@app.route('/tasks/<int:task_id>/evidence/<int:evidence_id>/preview')
@login_required
def task_preview_evidence(task_id, evidence_id):
    """Preview file evidence inline (for images, PDFs, text files)"""
    import os
    
    evidence = TaskEvidence.query.filter_by(id=evidence_id, task_id=task_id).first_or_404()
    
    if evidence.evidence_type != 'file':
        flash('Nur Dateien können angezeigt werden.', 'warning')
        return redirect(url_for('task_detail', task_id=task_id))
    
    if not os.path.exists(evidence.file_path):
        flash('Datei nicht gefunden.', 'danger')
        return redirect(url_for('task_detail', task_id=task_id))
    
    # Determine mimetype for inline display
    mimetype = evidence.mime_type or 'application/octet-stream'
    
    return send_file(evidence.file_path, mimetype=mimetype, as_attachment=False, download_name=evidence.filename)


@app.route('/tasks/<int:task_id>/evidence/<int:evidence_id>/delete', methods=['POST'])
@login_required
def task_delete_evidence(task_id, evidence_id):
    """Delete evidence from a task"""
    import os
    
    evidence = TaskEvidence.query.filter_by(id=evidence_id, task_id=task_id).first_or_404()
    task = Task.query.get_or_404(task_id)
    
    # Check permission - only uploader, owner, or admin can delete
    if not (current_user.is_admin() or current_user.id == evidence.uploaded_by_id or 
            current_user.id == task.owner_id):
        flash('Keine Berechtigung zum Löschen.', 'danger')
        return redirect(url_for('task_detail', task_id=task_id))
    
    # Delete file if exists
    if evidence.evidence_type == 'file' and evidence.file_path:
        if os.path.exists(evidence.file_path):
            os.remove(evidence.file_path)
    
    description = evidence.filename or evidence.url
    db.session.delete(evidence)
    db.session.commit()
    
    log_action('EVIDENCE_DELETE', 'Task', task_id, task.title, f'Nachweis: {description[:50]}', None)
    flash('Nachweis gelöscht.', 'success')
    
    return redirect(url_for('task_detail', task_id=task_id) + '#evidence')


# ============================================================================
# TASK COMMENTS
# ============================================================================

@app.route('/tasks/<int:task_id>/comments', methods=['POST'])
@login_required
def task_add_comment(task_id):
    """Add a comment to a task"""
    task = Task.query.get_or_404(task_id)
    
    text = request.form.get('text', '').strip()
    
    if not text:
        flash('Kommentar darf nicht leer sein.', 'warning')
        return redirect(url_for('task_detail', task_id=task_id) + '#comments')
    
    comment = Comment(
        task_id=task_id,
        text=text,
        created_by_id=current_user.id
    )
    db.session.add(comment)
    db.session.commit()
    
    log_action('COMMENT', 'Task', task_id, task.title, None, text[:100] + ('...' if len(text) > 100 else ''))
    flash('Kommentar hinzugefügt.', 'success')
    
    return redirect(url_for('task_detail', task_id=task_id) + '#comments')


@app.route('/tasks/<int:task_id>/comments/<int:comment_id>/delete', methods=['POST'])
@login_required
def task_delete_comment(task_id, comment_id):
    """Delete a comment from a task"""
    comment = Comment.query.filter_by(id=comment_id, task_id=task_id).first_or_404()
    task = Task.query.get_or_404(task_id)
    
    # Check permission - only comment author, task owner, or admin can delete
    if not (current_user.is_admin() or current_user.id == comment.created_by_id or 
            current_user.id == task.owner_id):
        flash('Keine Berechtigung zum Löschen.', 'danger')
        return redirect(url_for('task_detail', task_id=task_id))
    
    # Save text before deletion for audit log
    comment_text = comment.text[:50] + ('...' if len(comment.text) > 50 else '')
    
    db.session.delete(comment)
    db.session.commit()
    
    log_action('COMMENT_DELETE', 'Task', task_id, task.title, comment_text, None)
    flash('Kommentar gelöscht.', 'success')
    
    return redirect(url_for('task_detail', task_id=task_id) + '#comments')


@app.route('/set-language/<lang>')
def set_language(lang):
    """Change language"""
    if lang in app.config.get('SUPPORTED_LANGUAGES', ['de', 'en']):
        session['lang'] = lang
    return redirect(request.referrer or url_for('index'))


@app.route('/calendar')
@login_required
def calendar_view():
    """Calendar month view of tasks"""
    from datetime import date, timedelta
    import calendar
    
    # Get year and month from query params, default to current
    year = request.args.get('year', type=int, default=date.today().year)
    month = request.args.get('month', type=int, default=date.today().month)
    
    # Validate month/year
    if month < 1:
        month = 12
        year -= 1
    elif month > 12:
        month = 1
        year += 1
    
    # Get first and last day of month
    first_day = date(year, month, 1)
    if month == 12:
        last_day = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        last_day = date(year, month + 1, 1) - timedelta(days=1)
    
    # Build calendar structure
    cal = calendar.Calendar(firstweekday=0)  # Monday first
    month_days = cal.monthdayscalendar(year, month)
    
    # Get tasks for this month
    query = Task.query.filter(
        Task.due_date >= first_day,
        Task.due_date <= last_day
    )
    
    # Apply role-based filtering
    if not (current_user.is_admin() or current_user.is_manager()):
        query = query.filter(
            (Task.owner_id == current_user.id) | (Task.reviewer_id == current_user.id)
        )
    
    tasks = query.order_by(Task.due_date).all()
    
    # Group tasks by day
    tasks_by_day = {}
    for task in tasks:
        day = task.due_date.day
        if day not in tasks_by_day:
            tasks_by_day[day] = []
        tasks_by_day[day].append(task)
    
    # Calculate prev/next month
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1
    
    return render_template('calendar.html',
                         year=year,
                         month=month,
                         month_name=calendar.month_name[month],
                         month_days=month_days,
                         tasks_by_day=tasks_by_day,
                         today=date.today(),
                         prev_month=prev_month,
                         prev_year=prev_year,
                         next_month=next_month,
                         next_year=next_year)


@app.route('/calendar/year')
@login_required
def calendar_year_view():
    """Calendar year view of tasks"""
    from datetime import date, timedelta
    import calendar
    
    year = request.args.get('year', type=int, default=date.today().year)
    
    # Get all tasks for the year
    first_day = date(year, 1, 1)
    last_day = date(year, 12, 31)
    
    query = Task.query.filter(
        Task.due_date >= first_day,
        Task.due_date <= last_day
    )
    
    if not (current_user.is_admin() or current_user.is_manager()):
        query = query.filter(
            (Task.owner_id == current_user.id) | (Task.reviewer_id == current_user.id)
        )
    
    tasks = query.order_by(Task.due_date).all()
    
    # Group tasks by month
    tasks_by_month = {m: [] for m in range(1, 13)}
    for task in tasks:
        tasks_by_month[task.due_date.month].append(task)
    
    # Count by status per month
    month_stats = {}
    for m in range(1, 13):
        month_tasks = tasks_by_month[m]
        month_stats[m] = {
            'total': len(month_tasks),
            'completed': sum(1 for t in month_tasks if t.status == 'completed'),
            'overdue': sum(1 for t in month_tasks if t.is_overdue),
            'in_review': sum(1 for t in month_tasks if t.status == 'in_review'),
        }
    
    # German month names
    month_names = ['', 'Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 
                   'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember']
    
    return render_template('calendar_year.html',
                         year=year,
                         month_names=month_names,
                         tasks_by_month=tasks_by_month,
                         month_stats=month_stats,
                         today=date.today())


@app.route('/calendar/week')
@login_required
def calendar_week_view():
    """Calendar week view of tasks"""
    from datetime import date, timedelta
    import calendar
    
    today = date.today()
    year = request.args.get('year', type=int, default=today.year)
    week = request.args.get('week', type=int, default=today.isocalendar()[1])
    
    # Validate week number
    if week < 1:
        week = 52
        year -= 1
    elif week > 52:
        week = 1
        year += 1
    
    # Get first day of the week (Monday)
    # ISO week: week 1 is the week containing Jan 4th
    jan4 = date(year, 1, 4)
    week_start = jan4 - timedelta(days=jan4.weekday()) + timedelta(weeks=week - 1)
    week_end = week_start + timedelta(days=6)
    
    # Get tasks for this week
    query = Task.query.filter(
        Task.due_date >= week_start,
        Task.due_date <= week_end
    )
    
    if not (current_user.is_admin() or current_user.is_manager()):
        query = query.filter(
            (Task.owner_id == current_user.id) | (Task.reviewer_id == current_user.id)
        )
    
    tasks = query.order_by(Task.due_date, Task.id).all()
    
    # Build days of the week
    week_days = []
    for i in range(7):
        day_date = week_start + timedelta(days=i)
        day_tasks = [t for t in tasks if t.due_date == day_date]
        week_days.append({
            'date': day_date,
            'weekday': ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag'][i],
            'weekday_short': ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So'][i],
            'tasks': day_tasks,
            'is_today': day_date == today,
            'is_weekend': i >= 5
        })
    
    # Prev/next week
    prev_week = week - 1 if week > 1 else 52
    prev_year = year if week > 1 else year - 1
    next_week = week + 1 if week < 52 else 1
    next_year = year if week < 52 else year + 1
    
    return render_template('calendar_week.html',
                         year=year,
                         week=week,
                         week_start=week_start,
                         week_end=week_end,
                         week_days=week_days,
                         today=today,
                         prev_week=prev_week,
                         prev_year=prev_year,
                         next_week=next_week,
                         next_year=next_year)


# ============================================================================
# ADMIN ROUTES
# ============================================================================

@app.route('/admin')
@admin_required
def admin_dashboard():
    """Admin dashboard"""
    from datetime import date
    stats = {
        'users': User.query.count(),
        'active_users': User.query.filter_by(is_active=True).count(),
        'entities': Entity.query.filter_by(is_active=True).count(),
        'tax_types': TaxType.query.filter_by(is_active=True).count(),
        'tasks_total': Task.query.count(),
        'tasks_overdue': Task.query.filter(Task.due_date < date.today(), Task.status != 'completed').count(),
        'tasks_completed': Task.query.filter_by(status='completed').count(),
        'presets': TaskPreset.query.filter_by(is_active=True).count(),
    }
    return render_template('admin/dashboard.html', stats=stats)


@app.route('/admin/users')
@admin_required
def admin_users():
    """User management"""
    users = User.query.order_by(User.name).all()
    return render_template('admin/users.html', users=users)


@app.route('/admin/users/new', methods=['GET', 'POST'])
@admin_required
def admin_user_new():
    """Create new user"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        name = request.form.get('name', '').strip()
        role = request.form.get('role', 'preparer')
        password = request.form.get('password', '')
        
        if User.query.filter_by(email=email).first():
            flash('E-Mail-Adresse bereits vorhanden.', 'danger')
        elif not email or not name or not password:
            flash('Bitte füllen Sie alle Pflichtfelder aus.', 'warning')
        else:
            user = User(email=email, name=name, role=role, is_active=True)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            log_action('CREATE', 'User', user.id, user.email)
            flash(f'Benutzer {name} wurde erstellt.', 'success')
            return redirect(url_for('admin_users'))
    
    return render_template('admin/user_form.html', user=None, roles=UserRole)


@app.route('/admin/users/<int:user_id>', methods=['GET', 'POST'])
@admin_required
def admin_user_edit(user_id):
    """Edit user"""
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        user.name = request.form.get('name', '').strip()
        user.role = request.form.get('role', 'preparer')
        user.is_active = request.form.get('is_active') == 'on'
        
        new_password = request.form.get('password', '')
        if new_password:
            user.set_password(new_password)
        
        db.session.commit()
        log_action('UPDATE', 'User', user.id, user.email)
        flash(f'Benutzer {user.name} wurde aktualisiert.', 'success')
        return redirect(url_for('admin_users'))
    
    return render_template('admin/user_form.html', user=user, roles=UserRole)


# ============================================================================
# ENTITY MANAGEMENT
# ============================================================================

@app.route('/admin/entities')
@admin_required
def admin_entities():
    """Entity management"""
    entities = Entity.query.order_by(Entity.name).all()
    return render_template('admin/entities.html', entities=entities)


@app.route('/admin/entities/new', methods=['GET', 'POST'])
@admin_required
def admin_entity_new():
    """Create new entity"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        short_name = request.form.get('short_name', '').strip()
        country = request.form.get('country', 'DE').strip().upper()
        group_id = request.form.get('group_id', type=int)
        
        if not name:
            flash('Name ist erforderlich.', 'warning')
        else:
            entity = Entity(
                name=name, 
                short_name=short_name or None,
                country=country, 
                group_id=group_id if group_id else None,
                is_active=True
            )
            db.session.add(entity)
            db.session.commit()
            log_action('CREATE', 'Entity', entity.id, entity.name)
            flash(f'Gesellschaft {name} wurde erstellt.', 'success')
            return redirect(url_for('admin_entities'))
    
    parent_entities = Entity.query.filter_by(is_active=True).order_by(Entity.name).all()
    return render_template('admin/entity_form.html', entity=None, parent_entities=parent_entities)


@app.route('/admin/entities/<int:entity_id>', methods=['GET', 'POST'])
@admin_required
def admin_entity_edit(entity_id):
    """Edit entity"""
    entity = Entity.query.get_or_404(entity_id)
    
    if request.method == 'POST':
        entity.name = request.form.get('name', '').strip()
        entity.short_name = request.form.get('short_name', '').strip() or None
        entity.country = request.form.get('country', 'DE').strip().upper()
        group_id = request.form.get('group_id', type=int)
        entity.group_id = group_id if group_id and group_id != entity.id else None
        entity.is_active = request.form.get('is_active') == 'on'
        
        db.session.commit()
        log_action('UPDATE', 'Entity', entity.id, entity.name)
        flash(f'Gesellschaft {entity.name} wurde aktualisiert.', 'success')
        return redirect(url_for('admin_entities'))
    
    parent_entities = Entity.query.filter(Entity.id != entity_id, Entity.is_active == True).order_by(Entity.name).all()
    return render_template('admin/entity_form.html', entity=entity, parent_entities=parent_entities)


@app.route('/admin/entities/<int:entity_id>/delete', methods=['POST'])
@admin_required
def admin_entity_delete(entity_id):
    """Delete entity (soft delete)"""
    entity = Entity.query.get_or_404(entity_id)
    entity.is_active = False
    db.session.commit()
    log_action('DELETE', 'Entity', entity.id, entity.name)
    flash(f'Gesellschaft {entity.name} wurde deaktiviert.', 'success')
    return redirect(url_for('admin_entities'))


# ============================================================================
# TAX TYPE MANAGEMENT
# ============================================================================

@app.route('/admin/tax-types')
@admin_required
def admin_tax_types():
    """Tax type management"""
    tax_types = TaxType.query.order_by(TaxType.code).all()
    return render_template('admin/tax_types.html', tax_types=tax_types)


@app.route('/admin/tax-types/new', methods=['GET', 'POST'])
@admin_required
def admin_tax_type_new():
    """Create new tax type"""
    if request.method == 'POST':
        code = request.form.get('code', '').strip().upper()
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        
        if TaxType.query.filter_by(code=code).first():
            flash('Code bereits vorhanden.', 'danger')
        elif not code or not name:
            flash('Code und Name sind erforderlich.', 'warning')
        else:
            tax_type = TaxType(code=code, name=name, description=description or None, is_active=True)
            db.session.add(tax_type)
            db.session.commit()
            log_action('CREATE', 'TaxType', tax_type.id, tax_type.code)
            flash(f'Steuerart {code} wurde erstellt.', 'success')
            return redirect(url_for('admin_tax_types'))
    
    return render_template('admin/tax_type_form.html', tax_type=None)


@app.route('/admin/tax-types/<int:tax_type_id>', methods=['GET', 'POST'])
@admin_required
def admin_tax_type_edit(tax_type_id):
    """Edit tax type"""
    tax_type = TaxType.query.get_or_404(tax_type_id)
    
    if request.method == 'POST':
        tax_type.name = request.form.get('name', '').strip()
        tax_type.description = request.form.get('description', '').strip() or None
        tax_type.is_active = request.form.get('is_active') == 'on'
        
        db.session.commit()
        log_action('UPDATE', 'TaxType', tax_type.id, tax_type.code)
        flash(f'Steuerart {tax_type.code} wurde aktualisiert.', 'success')
        return redirect(url_for('admin_tax_types'))
    
    return render_template('admin/tax_type_form.html', tax_type=tax_type)


# ============================================================================
# TEAM MANAGEMENT
# ============================================================================

@app.route('/admin/teams')
@admin_required
def admin_teams():
    """Team management - list all teams"""
    teams = Team.query.order_by(Team.name).all()
    return render_template('admin/teams.html', teams=teams)


@app.route('/admin/teams/new', methods=['GET', 'POST'])
@admin_required
def admin_team_new():
    """Create new team"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        color = request.form.get('color', '#86BC25').strip()
        manager_id = request.form.get('manager_id', type=int)
        member_ids = request.form.getlist('members', type=int)
        
        if Team.query.filter_by(name=name).first():
            flash('Teamname bereits vorhanden.', 'danger')
        elif not name:
            flash('Teamname ist erforderlich.', 'warning')
        else:
            team = Team(
                name=name,
                description=description or None,
                color=color,
                manager_id=manager_id if manager_id else None,
                is_active=True
            )
            db.session.add(team)
            db.session.flush()  # Get team.id
            
            # Add members
            for user_id in member_ids:
                user = User.query.get(user_id)
                if user:
                    team.add_member(user)
            
            db.session.commit()
            log_action('CREATE', 'Team', team.id, team.name)
            flash(f'Team "{name}" wurde erstellt.', 'success')
            return redirect(url_for('admin_teams'))
    
    users = User.query.filter_by(is_active=True).order_by(User.name).all()
    return render_template('admin/team_form.html', team=None, users=users)


@app.route('/admin/teams/<int:team_id>', methods=['GET', 'POST'])
@admin_required
def admin_team_edit(team_id):
    """Edit team"""
    team = Team.query.get_or_404(team_id)
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        
        # Check for duplicate name (excluding current team)
        existing = Team.query.filter(Team.name == name, Team.id != team_id).first()
        if existing:
            flash('Teamname bereits vorhanden.', 'danger')
        elif not name:
            flash('Teamname ist erforderlich.', 'warning')
        else:
            team.name = name
            team.description = request.form.get('description', '').strip() or None
            team.color = request.form.get('color', '#86BC25').strip()
            team.manager_id = request.form.get('manager_id', type=int) or None
            team.is_active = request.form.get('is_active') == 'on'
            
            # Update members - get current and new member lists
            new_member_ids = set(request.form.getlist('members', type=int))
            current_member_ids = set(m.id for m in team.members.all())
            
            # Remove members no longer selected
            for user_id in current_member_ids - new_member_ids:
                user = User.query.get(user_id)
                if user:
                    team.remove_member(user)
            
            # Add new members
            for user_id in new_member_ids - current_member_ids:
                user = User.query.get(user_id)
                if user:
                    team.add_member(user)
            
            db.session.commit()
            log_action('UPDATE', 'Team', team.id, team.name)
            flash(f'Team "{team.name}" wurde aktualisiert.', 'success')
            return redirect(url_for('admin_teams'))
    
    users = User.query.filter_by(is_active=True).order_by(User.name).all()
    return render_template('admin/team_form.html', team=team, users=users)


@app.route('/admin/teams/<int:team_id>/delete', methods=['POST'])
@admin_required
def admin_team_delete(team_id):
    """Delete team (soft delete)"""
    team = Team.query.get_or_404(team_id)
    team.is_active = False
    db.session.commit()
    log_action('DELETE', 'Team', team.id, team.name)
    flash(f'Team "{team.name}" wurde deaktiviert.', 'success')
    return redirect(url_for('admin_teams'))


# ============================================================================
# ADMIN: TASK PRESETS (Aufgabenvorlagen)
# ============================================================================

@app.route('/admin/presets')
@admin_required
def admin_presets():
    """Task preset management"""
    category_filter = request.args.get('category', '')
    search = request.args.get('search', '').strip()
    
    query = TaskPreset.query
    if category_filter:
        query = query.filter(TaskPreset.category == category_filter)
    if search:
        query = query.filter(TaskPreset.title.ilike(f'%{search}%') | 
                            TaskPreset.tax_type.ilike(f'%{search}%') |
                            TaskPreset.law_reference.ilike(f'%{search}%'))
    
    presets = query.order_by(TaskPreset.category, TaskPreset.tax_type, TaskPreset.title).all()
    
    # Get unique tax types for filter
    tax_types = db.session.query(TaskPreset.tax_type).filter(TaskPreset.tax_type.isnot(None)).distinct().all()
    tax_types = sorted([t[0] for t in tax_types if t[0]])
    
    return render_template('admin/presets.html', 
                           presets=presets, 
                           category_filter=category_filter,
                           search=search,
                           tax_types=tax_types)


@app.route('/admin/presets/new', methods=['GET', 'POST'])
@admin_required
def admin_preset_new():
    """Create new task preset"""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        category = request.form.get('category', 'aufgabe')
        tax_type = request.form.get('tax_type', '').strip() or None
        law_reference = request.form.get('law_reference', '').strip() or None
        description = request.form.get('description', '').strip() or None
        
        if not title:
            flash('Titel ist erforderlich.', 'warning')
        else:
            preset = TaskPreset(
                title=title,
                category=category,
                tax_type=tax_type,
                law_reference=law_reference,
                description=description,
                source='manual',
                is_active=True
            )
            db.session.add(preset)
            db.session.commit()
            log_action('CREATE', 'TaskPreset', preset.id, preset.title[:50])
            flash('Aufgabenvorlage wurde erstellt.', 'success')
            return redirect(url_for('admin_presets'))
    
    return render_template('admin/preset_form.html', preset=None)


@app.route('/admin/presets/<int:preset_id>', methods=['GET', 'POST'])
@admin_required
def admin_preset_edit(preset_id):
    """Edit task preset"""
    preset = TaskPreset.query.get_or_404(preset_id)
    
    if request.method == 'POST':
        preset.title = request.form.get('title', '').strip()
        preset.category = request.form.get('category', 'aufgabe')
        preset.tax_type = request.form.get('tax_type', '').strip() or None
        preset.law_reference = request.form.get('law_reference', '').strip() or None
        preset.description = request.form.get('description', '').strip() or None
        preset.is_active = request.form.get('is_active') == 'on'
        
        db.session.commit()
        log_action('UPDATE', 'TaskPreset', preset.id, preset.title[:50])
        flash('Aufgabenvorlage wurde aktualisiert.', 'success')
        return redirect(url_for('admin_presets'))
    
    return render_template('admin/preset_form.html', preset=preset)


@app.route('/admin/presets/<int:preset_id>/delete', methods=['POST'])
@admin_required
def admin_preset_delete(preset_id):
    """Delete task preset"""
    preset = TaskPreset.query.get_or_404(preset_id)
    title = preset.title
    db.session.delete(preset)
    db.session.commit()
    log_action('DELETE', 'TaskPreset', preset_id, title[:50])
    flash('Aufgabenvorlage wurde gelöscht.', 'success')
    return redirect(url_for('admin_presets'))


@app.route('/admin/presets/import', methods=['POST'])
@admin_required
def admin_preset_import():
    """Import task presets from JSON or Excel file"""
    import json as json_module
    
    if 'file' not in request.files:
        flash('Keine Datei ausgewählt.', 'warning')
        return redirect(url_for('admin_presets'))
    
    file = request.files['file']
    if file.filename == '':
        flash('Keine Datei ausgewählt.', 'warning')
        return redirect(url_for('admin_presets'))
    
    filename = file.filename.lower()
    imported = 0
    skipped = 0
    
    try:
        if filename.endswith('.json'):
            data = json_module.load(file)
            
            # Handle Antraege.json format
            if 'sheets' in data:
                for sheet_name, records in data['sheets'].items():
                    for record in records:
                        title = record.get('Zweck des Antrags') or record.get('title')
                        if not title:
                            skipped += 1
                            continue
                        existing = TaskPreset.query.filter_by(title=title, category='antrag').first()
                        if existing:
                            skipped += 1
                            continue
                        preset = TaskPreset(
                            category='antrag',
                            title=title,
                            law_reference=record.get('§ Paragraph') or record.get('law_reference'),
                            tax_type=record.get('Gesetz') or record.get('tax_type'),
                            description=record.get('Erläuterung') or record.get('description'),
                            source='json',
                            is_active=True
                        )
                        db.session.add(preset)
                        imported += 1
            
            # Handle steuerarten_aufgaben.json format
            elif 'records' in data:
                for record in data['records']:
                    title = record.get('aufgabe') or record.get('title')
                    if not title:
                        skipped += 1
                        continue
                    existing = TaskPreset.query.filter_by(title=title, category='aufgabe').first()
                    if existing:
                        skipped += 1
                        continue
                    preset = TaskPreset(
                        category='aufgabe',
                        title=title,
                        tax_type=record.get('steuerart') or record.get('tax_type'),
                        description=record.get('description'),
                        source='json',
                        is_active=True
                    )
                    db.session.add(preset)
                    imported += 1
        
        elif filename.endswith('.xlsx') or filename.endswith('.xls'):
            import openpyxl
            wb = openpyxl.load_workbook(file)
            ws = wb.active
            
            # Find header row
            header_row = None
            headers = {}
            for row_idx, row in enumerate(ws.iter_rows(min_row=1, max_row=10, values_only=True), 1):
                for col_idx, cell in enumerate(row):
                    if cell:
                        cell_lower = str(cell).lower()
                        if 'titel' in cell_lower or 'aufgabe' in cell_lower or 'zweck' in cell_lower:
                            header_row = row_idx
                            for i, h in enumerate(row):
                                if h:
                                    headers[str(h).lower().strip()] = i
                            break
                if header_row:
                    break
            
            if not header_row:
                flash('Keine gültige Kopfzeile gefunden.', 'danger')
                return redirect(url_for('admin_presets'))
            
            # Find title column
            title_col = None
            for key in ['titel', 'aufgabe', 'zweck des antrags', 'zweck']:
                if key in headers:
                    title_col = headers[key]
                    break
            
            if title_col is None:
                flash('Spalte "Titel" oder "Aufgabe" nicht gefunden.', 'danger')
                return redirect(url_for('admin_presets'))
            
            category_col = headers.get('kategorie') or headers.get('category')
            tax_type_col = headers.get('steuerart') or headers.get('tax_type') or headers.get('gesetz')
            law_ref_col = headers.get('§ paragraph') or headers.get('paragraph') or headers.get('law_reference')
            desc_col = headers.get('beschreibung') or headers.get('description') or headers.get('erläuterung')
            
            for row in ws.iter_rows(min_row=header_row + 1, values_only=True):
                title = row[title_col] if title_col < len(row) else None
                if not title or not str(title).strip():
                    skipped += 1
                    continue
                
                title = str(title).strip()
                category = 'aufgabe'
                if category_col is not None and category_col < len(row) and row[category_col]:
                    if 'antrag' in str(row[category_col]).lower():
                        category = 'antrag'
                
                existing = TaskPreset.query.filter_by(title=title, category=category).first()
                if existing:
                    skipped += 1
                    continue
                
                preset = TaskPreset(
                    category=category,
                    title=title,
                    tax_type=str(row[tax_type_col]).strip() if tax_type_col is not None and tax_type_col < len(row) and row[tax_type_col] else None,
                    law_reference=str(row[law_ref_col]).strip() if law_ref_col is not None and law_ref_col < len(row) and row[law_ref_col] else None,
                    description=str(row[desc_col]).strip() if desc_col is not None and desc_col < len(row) and row[desc_col] else None,
                    source='excel',
                    is_active=True
                )
                db.session.add(preset)
                imported += 1
        else:
            flash('Ungültiges Dateiformat. Erlaubt: .json, .xlsx', 'danger')
            return redirect(url_for('admin_presets'))
        
        db.session.commit()
        log_action('IMPORT', 'TaskPreset', None, f'{imported} imported, {skipped} skipped')
        flash(f'{imported} Vorlagen importiert, {skipped} übersprungen.', 'success')
    
    except Exception as e:
        db.session.rollback()
        flash(f'Fehler beim Import: {str(e)}', 'danger')
    
    return redirect(url_for('admin_presets'))


@app.route('/admin/presets/template')
@admin_required
def admin_preset_template():
    """Download Excel template for import"""
    from io import BytesIO
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Aufgabenvorlagen"
    
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="000000", end_color="000000", fill_type="solid")
    thin_border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
    
    headers = ['Kategorie', 'Titel', 'Steuerart', '§ Paragraph', 'Beschreibung']
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.border = thin_border
        cell.alignment = Alignment(horizontal='center')
    
    examples = [
        ['aufgabe', 'USt-Voranmeldung einreichen', 'Umsatzsteuer', '', 'Monatliche USt-Voranmeldung'],
        ['aufgabe', 'Körperschaftsteuererklärung erstellen', 'Körperschaftsteuer', '', 'Jährliche KSt-Erklärung'],
        ['antrag', 'Unbeschränkte Einkommensteuerpflicht', 'EStG', '§1 (3) EStG', 'Antrag für ausländische Mitarbeiter'],
    ]
    
    for row_idx, example in enumerate(examples, 2):
        for col_idx, value in enumerate(example, 1):
            cell = ws.cell(row=row_idx, column=col_idx, value=value)
            cell.border = thin_border
    
    ws.column_dimensions['A'].width = 12
    ws.column_dimensions['B'].width = 45
    ws.column_dimensions['C'].width = 25
    ws.column_dimensions['D'].width = 20
    ws.column_dimensions['E'].width = 50
    
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     as_attachment=True, download_name='Aufgabenvorlagen_Vorlage.xlsx')


@app.route('/admin/presets/seed', methods=['POST'])
@admin_required
def admin_preset_seed():
    """Seed presets from JSON files in data folder"""
    import json as json_module
    import os as os_module
    
    data_dir = os_module.path.join(os_module.path.dirname(__file__), 'data')
    imported = 0
    skipped = 0
    
    antraege_path = os_module.path.join(data_dir, 'Antraege.json')
    if os_module.path.exists(antraege_path):
        with open(antraege_path, 'r', encoding='utf-8') as f:
            data = json_module.load(f)
            if 'sheets' in data:
                for sheet_name, records in data['sheets'].items():
                    for record in records:
                        title = record.get('Zweck des Antrags')
                        if not title:
                            continue
                        existing = TaskPreset.query.filter_by(title=title, category='antrag').first()
                        if existing:
                            skipped += 1
                            continue
                        preset = TaskPreset(category='antrag', title=title, law_reference=record.get('§ Paragraph'),
                                          tax_type=record.get('Gesetz'), description=record.get('Erläuterung'),
                                          source='json', is_active=True)
                        db.session.add(preset)
                        imported += 1
    
    aufgaben_path = os_module.path.join(data_dir, 'steuerarten_aufgaben.json')
    if os_module.path.exists(aufgaben_path):
        with open(aufgaben_path, 'r', encoding='utf-8') as f:
            data = json_module.load(f)
            if 'records' in data:
                for record in data['records']:
                    title = record.get('aufgabe')
                    if not title:
                        continue
                    existing = TaskPreset.query.filter_by(title=title, category='aufgabe').first()
                    if existing:
                        skipped += 1
                        continue
                    preset = TaskPreset(category='aufgabe', title=title, tax_type=record.get('steuerart'),
                                      source='json', is_active=True)
                    db.session.add(preset)
                    imported += 1
    
    db.session.commit()
    log_action('SEED', 'TaskPreset', None, f'{imported} seeded, {skipped} skipped')
    flash(f'{imported} Vorlagen aus JSON-Dateien importiert, {skipped} übersprungen.', 'success')
    return redirect(url_for('admin_presets'))


@app.route('/api/presets')
@login_required
def api_presets():
    """API endpoint for fetching presets"""
    category = request.args.get('category', '')
    search = request.args.get('search', '').strip()
    
    query = TaskPreset.query.filter(TaskPreset.is_active == True)
    if category:
        query = query.filter(TaskPreset.category == category)
    if search:
        query = query.filter(TaskPreset.title.ilike(f'%{search}%'))
    
    presets = query.order_by(TaskPreset.title).limit(50).all()
    return jsonify([p.to_dict() for p in presets])


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found_error(error):
    """404 error handler"""
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """500 error handler"""
    db.session.rollback()
    return render_template('errors/500.html'), 500


# ============================================================================
# CLI COMMANDS
# ============================================================================

@app.cli.command()
def initdb():
    """Initialize the database"""
    db.create_all()
    print('Database initialized.')


@app.cli.command()
def createadmin():
    """Create admin user"""
    admin = User(
        email='admin@example.com',
        name='Administrator',
        role='admin',
        is_active=True
    )
    admin.set_password('admin123')
    db.session.add(admin)
    db.session.commit()
    print('Admin user created: admin@example.com / admin123')


@app.cli.command()
def seed():
    """Seed database with sample data for development"""
    from datetime import date, timedelta
    
    # Create sample users
    users_data = [
        {'email': 'manager@example.com', 'name': 'Max Manager', 'role': 'manager'},
        {'email': 'reviewer@example.com', 'name': 'Rita Reviewer', 'role': 'reviewer'},
        {'email': 'preparer@example.com', 'name': 'Peter Preparer', 'role': 'preparer'},
        {'email': 'readonly@example.com', 'name': 'Rolf Readonly', 'role': 'readonly'},
    ]
    
    for u in users_data:
        if not User.query.filter_by(email=u['email']).first():
            user = User(email=u['email'], name=u['name'], role=u['role'], is_active=True)
            user.set_password('password123')
            db.session.add(user)
    
    db.session.commit()
    print(f'Created {len(users_data)} sample users')
    
    # Create sample tax types
    tax_types_data = [
        {'code': 'KSt', 'name': 'Körperschaftsteuer', 'description': 'Corporate income tax'},
        {'code': 'USt', 'name': 'Umsatzsteuer', 'description': 'Value added tax (VAT)'},
        {'code': 'GewSt', 'name': 'Gewerbesteuer', 'description': 'Trade tax'},
        {'code': 'LSt', 'name': 'Lohnsteuer', 'description': 'Wage tax'},
        {'code': 'ESt', 'name': 'Einkommensteuer', 'description': 'Income tax'},
        {'code': 'ErbSt', 'name': 'Erbschaftsteuer', 'description': 'Inheritance tax'},
        {'code': 'GrSt', 'name': 'Grundsteuer', 'description': 'Property tax'},
    ]
    
    for tt in tax_types_data:
        if not TaxType.query.filter_by(code=tt['code']).first():
            tax_type = TaxType(**tt, is_active=True)
            db.session.add(tax_type)
    
    db.session.commit()
    print(f'Created {len(tax_types_data)} tax types')
    
    # Create sample entities
    entities_data = [
        {'name': 'Deloitte Germany GmbH', 'short_name': 'DEU', 'country': 'DE'},
        {'name': 'Deloitte Austria GmbH', 'short_name': 'AUT', 'country': 'AT'},
        {'name': 'Deloitte Switzerland AG', 'short_name': 'CHE', 'country': 'CH'},
        {'name': 'Tech Subsidiary GmbH', 'short_name': 'TECH', 'country': 'DE'},
        {'name': 'Finance Holding SE', 'short_name': 'FIN', 'country': 'DE'},
    ]
    
    for e in entities_data:
        if not Entity.query.filter_by(name=e['name']).first():
            entity = Entity(**e, is_active=True)
            db.session.add(entity)
    
    db.session.commit()
    print(f'Created {len(entities_data)} entities')
    
    # Create sample task templates
    kst = TaxType.query.filter_by(code='KSt').first()
    ust = TaxType.query.filter_by(code='USt').first()
    gewst = TaxType.query.filter_by(code='GewSt').first()
    
    templates_data = [
        {'tax_type_id': kst.id, 'keyword': 'KSt-Voranmeldung', 'description': 'Körperschaftsteuer Voranmeldung', 'default_recurrence': 'quarterly'},
        {'tax_type_id': kst.id, 'keyword': 'KSt-Erklärung', 'description': 'Jährliche Körperschaftsteuererklärung', 'default_recurrence': 'annual'},
        {'tax_type_id': ust.id, 'keyword': 'USt-Voranmeldung', 'description': 'Monatliche Umsatzsteuer-Voranmeldung', 'default_recurrence': 'monthly'},
        {'tax_type_id': ust.id, 'keyword': 'USt-Erklärung', 'description': 'Jährliche Umsatzsteuererklärung', 'default_recurrence': 'annual'},
        {'tax_type_id': gewst.id, 'keyword': 'GewSt-Erklärung', 'description': 'Jährliche Gewerbesteuererklärung', 'default_recurrence': 'annual'},
    ]
    
    for t in templates_data:
        if not TaskTemplate.query.filter_by(keyword=t['keyword']).first():
            template = TaskTemplate(**t, is_active=True)
            db.session.add(template)
    
    db.session.commit()
    print(f'Created {len(templates_data)} task templates')
    
    # Create sample tasks for current year
    year = date.today().year
    entities = Entity.query.filter_by(is_active=True).all()
    owner = User.query.filter_by(role='preparer').first()
    reviewer = User.query.filter_by(role='reviewer').first()
    
    tasks_created = 0
    for entity in entities[:3]:  # First 3 entities
        # Monthly USt tasks
        ust_template = TaskTemplate.query.filter_by(keyword='USt-Voranmeldung').first()
        for month in range(1, 13):
            due = date(year, month, 10) if month < 12 else date(year, 12, 10)
            if due < date.today():
                due = date.today() + timedelta(days=30)
            
            existing = Task.query.filter_by(
                entity_id=entity.id, 
                template_id=ust_template.id,
                year=year,
                period=f'M{month:02d}'
            ).first()
            
            if not existing:
                task = Task(
                    template_id=ust_template.id,
                    entity_id=entity.id,
                    year=year,
                    period=f'M{month:02d}',
                    title=f'{ust_template.keyword} {month:02d}/{year}',
                    description=ust_template.description,
                    due_date=due,
                    status='draft',
                    owner_id=owner.id if owner else None,
                    reviewer_id=reviewer.id if reviewer else None
                )
                db.session.add(task)
                tasks_created += 1
    
    db.session.commit()
    print(f'Created {tasks_created} sample tasks')
    print('Seed complete!')


# ============================================================================
# RUN
# ============================================================================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)

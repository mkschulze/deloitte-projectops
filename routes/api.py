"""
API Routes Blueprint

Handles JSON API endpoints:
- Dashboard chart data
- Task bulk operations
- Preset management API
- Approval status API

Note: This blueprint contains core API functionality.
Additional API routes remain in app.py for gradual migration.
"""

from datetime import date, timedelta
from flask import Blueprint, jsonify, request, session
from flask_login import login_required, current_user

from extensions import db
from models import Task, TaskPreset, TaskReviewer, TaskEvidence, Comment, Notification, AuditLog

api_bp = Blueprint('api', __name__, url_prefix='/api')


def log_action(action, entity_type, entity_id, entity_name, old_value=None, new_value=None):
    """Helper to log actions to audit log"""
    log = AuditLog(
        user_id=current_user.id if current_user.is_authenticated else None,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        entity_name=entity_name[:200] if entity_name else None,
        old_value=str(old_value)[:500] if old_value else None,
        new_value=str(new_value)[:500] if new_value else None
    )
    db.session.add(log)
    db.session.commit()


# ============================================================================
# TASK BULK OPERATIONS
# ============================================================================

@api_bp.route('/tasks/bulk-archive', methods=['POST'])
@login_required
def bulk_archive():
    """Bulk archive multiple tasks"""
    if not (current_user.is_admin() or current_user.is_manager()):
        return jsonify({'success': False, 'error': 'Permission denied'}), 403
    
    data = request.get_json()
    task_ids = data.get('task_ids', [])
    reason = data.get('reason', '')
    
    if not task_ids:
        return jsonify({'success': False, 'error': 'No tasks selected'}), 400
    
    archived_count = 0
    for task_id in task_ids:
        task = Task.query.get(task_id)
        if task and not task.is_archived:
            task.archive(current_user, reason)
            log_action('ARCHIVE', 'Task', task.id, task.title, 'active', 'archived')
            archived_count += 1
    
    db.session.commit()
    
    lang = session.get('lang', 'de')
    return jsonify({
        'success': True,
        'archived_count': archived_count,
        'message': f'{archived_count} Aufgabe(n) archiviert.' if lang == 'de' else f'{archived_count} task(s) archived.'
    })


@api_bp.route('/tasks/bulk-restore', methods=['POST'])
@login_required
def bulk_restore():
    """Bulk restore multiple tasks from archive"""
    if not (current_user.is_admin() or current_user.is_manager()):
        return jsonify({'success': False, 'error': 'Permission denied'}), 403
    
    data = request.get_json()
    task_ids = data.get('task_ids', [])
    
    if not task_ids:
        return jsonify({'success': False, 'error': 'No tasks selected'}), 400
    
    restored_count = 0
    for task_id in task_ids:
        task = Task.query.get(task_id)
        if task and task.is_archived:
            task.restore()
            log_action('RESTORE', 'Task', task.id, task.title, 'archived', 'active')
            restored_count += 1
    
    db.session.commit()
    
    lang = session.get('lang', 'de')
    return jsonify({
        'success': True,
        'restored_count': restored_count,
        'message': f'{restored_count} Aufgabe(n) wiederhergestellt.' if lang == 'de' else f'{restored_count} task(s) restored.'
    })


@api_bp.route('/tasks/archive/bulk-delete', methods=['POST'])
@login_required
def bulk_permanent_delete():
    """Bulk permanently delete multiple archived tasks (admin only)"""
    if not current_user.is_admin():
        return jsonify({'success': False, 'error': 'Permission denied - admin only'}), 403
    
    data = request.get_json()
    task_ids = data.get('task_ids', [])
    
    if not task_ids:
        return jsonify({'success': False, 'error': 'No tasks selected'}), 400
    
    deleted_count = 0
    for task_id in task_ids:
        task = Task.query.get(task_id)
        if task and task.is_archived:
            task_title = task.title
            
            # Delete related records first
            TaskEvidence.query.filter_by(task_id=task_id).delete()
            Comment.query.filter_by(task_id=task_id).delete()
            TaskReviewer.query.filter_by(task_id=task_id).delete()
            Notification.query.filter(Notification.entity_type == 'task', Notification.entity_id == task_id).delete()
            
            db.session.delete(task)
            log_action('DELETE', 'Task', task_id, task_title, 'archived', 'deleted')
            deleted_count += 1
    
    db.session.commit()
    
    lang = session.get('lang', 'de')
    return jsonify({
        'success': True,
        'deleted_count': deleted_count,
        'message': f'{deleted_count} Aufgabe(n) endgültig gelöscht.' if lang == 'de' else f'{deleted_count} task(s) permanently deleted.'
    })


@api_bp.route('/tasks/bulk-status', methods=['POST'])
@login_required
def bulk_status():
    """Bulk change status for multiple tasks"""
    if not (current_user.is_admin() or current_user.is_manager()):
        return jsonify({'success': False, 'error': 'Permission denied'}), 403
    
    data = request.get_json()
    task_ids = data.get('task_ids', [])
    new_status = data.get('status', '')
    
    if not task_ids:
        return jsonify({'success': False, 'error': 'No tasks selected'}), 400
    
    if not new_status:
        return jsonify({'success': False, 'error': 'No status specified'}), 400
    
    updated_count = 0
    for task_id in task_ids:
        task = Task.query.get(task_id)
        if task and task.status != new_status:
            old_status = task.status
            task.status = new_status
            log_action('STATUS_CHANGE', 'Task', task.id, task.title, old_status, new_status)
            updated_count += 1
    
    db.session.commit()
    
    lang = session.get('lang', 'de')
    return jsonify({
        'success': True,
        'updated_count': updated_count,
        'message': f'{updated_count} Aufgabe(n) aktualisiert.' if lang == 'de' else f'{updated_count} task(s) updated.'
    })


@api_bp.route('/tasks/bulk-assign-owner', methods=['POST'])
@login_required
def bulk_assign_owner():
    """Bulk assign owner to multiple tasks"""
    if not (current_user.is_admin() or current_user.is_manager()):
        return jsonify({'success': False, 'error': 'Permission denied'}), 403
    
    data = request.get_json()
    task_ids = data.get('task_ids', [])
    owner_id = data.get('owner_id')
    
    if not task_ids:
        return jsonify({'success': False, 'error': 'No tasks selected'}), 400
    
    updated_count = 0
    for task_id in task_ids:
        task = Task.query.get(task_id)
        if task:
            old_owner = task.owner_id
            task.owner_id = owner_id
            log_action('ASSIGN', 'Task', task.id, task.title, f'owner_id={old_owner}', f'owner_id={owner_id}')
            updated_count += 1
    
    db.session.commit()
    
    lang = session.get('lang', 'de')
    return jsonify({
        'success': True,
        'updated_count': updated_count,
        'message': f'{updated_count} Aufgabe(n) zugewiesen.' if lang == 'de' else f'{updated_count} task(s) assigned.'
    })


@api_bp.route('/tasks/bulk-delete', methods=['POST'])
@login_required
def bulk_delete():
    """Bulk delete multiple tasks"""
    if not current_user.is_admin():
        return jsonify({'success': False, 'error': 'Permission denied - admin only'}), 403
    
    data = request.get_json()
    task_ids = data.get('task_ids', [])
    
    if not task_ids:
        return jsonify({'success': False, 'error': 'No tasks selected'}), 400
    
    deleted_count = 0
    for task_id in task_ids:
        task = Task.query.get(task_id)
        if task:
            task_title = task.title
            
            # Delete related records first
            TaskEvidence.query.filter_by(task_id=task_id).delete()
            Comment.query.filter_by(task_id=task_id).delete()
            TaskReviewer.query.filter_by(task_id=task_id).delete()
            Notification.query.filter(Notification.entity_type == 'task', Notification.entity_id == task_id).delete()
            
            db.session.delete(task)
            log_action('DELETE', 'Task', task_id, task_title, '', 'deleted')
            deleted_count += 1
    
    db.session.commit()
    
    lang = session.get('lang', 'de')
    return jsonify({
        'success': True,
        'deleted_count': deleted_count,
        'message': f'{deleted_count} Aufgabe(n) gelöscht.' if lang == 'de' else f'{deleted_count} task(s) deleted.'
    })


# ============================================================================
# TASK APPROVAL STATUS
# ============================================================================

@api_bp.route('/tasks/<int:task_id>/approval-status')
@login_required
def task_approval_status(task_id):
    """Get approval status for a task"""
    task = Task.query.get_or_404(task_id)
    
    reviewers = []
    for tr in task.reviewers:
        reviewers.append({
            'user_id': tr.user_id,
            'name': tr.user.name if tr.user else 'Unknown',
            'decision': tr.decision,
            'decided_at': tr.decided_at.isoformat() if tr.decided_at else None,
            'note': tr.note
        })
    
    return jsonify({
        'task_id': task.id,
        'status': task.status,
        'reviewers': reviewers,
        'all_approved': all(tr.decision == 'approved' for tr in task.reviewers),
        'any_rejected': any(tr.decision == 'rejected' for tr in task.reviewers)
    })


@api_bp.route('/tasks/<int:task_id>/workflow-timeline')
@login_required
def task_workflow_timeline(task_id):
    """Get workflow timeline for a task"""
    task = Task.query.get_or_404(task_id)
    
    # Get audit logs for this task
    logs = AuditLog.query.filter_by(
        entity_type='Task',
        entity_id=task_id
    ).order_by(AuditLog.timestamp.desc()).limit(20).all()
    
    timeline = []
    for log in logs:
        timeline.append({
            'action': log.action,
            'user_name': log.user.name if log.user else 'System',
            'timestamp': log.timestamp.isoformat(),
            'old_value': log.old_value,
            'new_value': log.new_value
        })
    
    return jsonify({
        'task_id': task.id,
        'timeline': timeline
    })


# ============================================================================
# DASHBOARD CHART DATA
# ============================================================================

@api_bp.route('/dashboard/status-chart')
@login_required
def dashboard_status_chart():
    """Get task status data for dashboard chart"""
    # Build base query
    query = Task.query.filter((Task.is_archived == False) | (Task.is_archived == None))
    
    if not (current_user.is_admin() or current_user.is_manager()):
        accessible_entity_ids = current_user.get_accessible_entity_ids('view')
        if accessible_entity_ids:
            query = query.filter(
                (Task.owner_id == current_user.id) | 
                (Task.reviewer_id == current_user.id) |
                (Task.entity_id.in_(accessible_entity_ids))
            )
        else:
            query = query.filter(
                (Task.owner_id == current_user.id) | (Task.reviewer_id == current_user.id)
            )
    
    # Count by status
    status_counts = {}
    for status in ['draft', 'submitted', 'in_review', 'approved', 'completed', 'rejected']:
        status_counts[status] = query.filter_by(status=status).count()
    
    # Count overdue
    today = date.today()
    status_counts['overdue'] = query.filter(
        Task.due_date < today,
        Task.status != 'completed'
    ).count()
    
    return jsonify(status_counts)


@api_bp.route('/dashboard/monthly-chart')
@login_required
def dashboard_monthly_chart():
    """Get monthly task data for dashboard chart"""
    year = request.args.get('year', type=int, default=date.today().year)
    
    # Build base query
    query = Task.query.filter(
        Task.year == year,
        (Task.is_archived == False) | (Task.is_archived == None)
    )
    
    if not (current_user.is_admin() or current_user.is_manager()):
        accessible_entity_ids = current_user.get_accessible_entity_ids('view')
        if accessible_entity_ids:
            query = query.filter(
                (Task.owner_id == current_user.id) | 
                (Task.reviewer_id == current_user.id) |
                (Task.entity_id.in_(accessible_entity_ids))
            )
        else:
            query = query.filter(
                (Task.owner_id == current_user.id) | (Task.reviewer_id == current_user.id)
            )
    
    # Count by month
    monthly_data = []
    for month in range(1, 13):
        month_start = date(year, month, 1)
        if month == 12:
            month_end = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            month_end = date(year, month + 1, 1) - timedelta(days=1)
        
        month_query = query.filter(Task.due_date >= month_start, Task.due_date <= month_end)
        
        monthly_data.append({
            'month': month,
            'total': month_query.count(),
            'completed': month_query.filter_by(status='completed').count()
        })
    
    return jsonify({
        'year': year,
        'months': monthly_data
    })


# ============================================================================
# PRESETS API
# ============================================================================

@api_bp.route('/presets')
@login_required
def presets_list():
    """Get list of active presets"""
    presets = TaskPreset.query.filter_by(is_active=True).order_by(TaskPreset.category, TaskPreset.title).all()
    
    return jsonify([{
        'id': p.id,
        'title': p.title,
        'category': p.category,
        'description': p.description,
        'default_period': p.default_period,
        'estimation_hours': p.estimation_hours
    } for p in presets])


@api_bp.route('/presets/<int:preset_id>')
@login_required
def preset_get(preset_id):
    """Get a single preset by ID"""
    preset = TaskPreset.query.get_or_404(preset_id)
    
    return jsonify({
        'id': preset.id,
        'title': preset.title,
        'category': preset.category,
        'description': preset.description,
        'default_period': preset.default_period,
        'estimation_hours': preset.estimation_hours,
        'is_active': preset.is_active
    })

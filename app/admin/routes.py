from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app.extensions import db
from app.admin import admin_bp
from app.models import Ticket, User
from app.utils import admin_required
from app.admin.forms import AssignTicketForm, ChangeStatusForm

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    # Similar to main dashboard but could contain more metrics
    return redirect(url_for('main.index'))

@admin_bp.route('/tickets')
@login_required
@admin_required
def tickets():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    status_filter = request.args.get('status')
    
    query = Ticket.query
    
    if search:
        query = query.filter(Ticket.title.ilike(f'%{search}%') | Ticket.id.ilike(f'%{search}%'))
    if status_filter:
        query = query.filter_by(status=status_filter)
        
    pagination = query.order_by(Ticket.created_at.desc()).paginate(page=page, per_page=15, error_out=False)
    
    return render_template('admin/tickets.html', tickets=pagination, search=search, current_status=status_filter)

@admin_bp.route('/tickets/<int:ticket_id>/manage', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    
    assign_form = AssignTicketForm()
    status_form = ChangeStatusForm(status=ticket.status)
    
    if assign_form.validate_on_submit() and 'assign_submit' in request.form:
        ticket.assigned_to = assign_form.assignee.data
        if ticket.status == 'Open':
            ticket.status = 'Assigned'
        db.session.commit()
        flash('Ticket assigned successfully.', 'success')
        return redirect(url_for('admin.manage_ticket', ticket_id=ticket.id))
        
    if status_form.validate_on_submit() and 'status_submit' in request.form:
        ticket.status = status_form.status.data
        db.session.commit()
        flash('Ticket status updated.', 'success')
        return redirect(url_for('admin.manage_ticket', ticket_id=ticket.id))
        
    # Pre-populate assign form if already assigned
    if request.method == 'GET' and ticket.assigned_to:
        assign_form.assignee.data = ticket.assigned_to
        
    return render_template('tickets/view.html', ticket=ticket, assign_form=assign_form, status_form=status_form, admin_mode=True)

@admin_bp.route('/tickets/<int:ticket_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    db.session.delete(ticket)
    db.session.commit()
    current_app.logger.info(f'Admin {current_user.username} deleted ticket {ticket_id}')
    flash('Ticket deleted successfully.', 'success')
    return redirect(url_for('admin.tickets'))

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    page = request.args.get('page', 1, type=int)
    pagination = User.query.order_by(User.id.asc()).paginate(page=page, per_page=15, error_out=False)
    return render_template('admin/users.html', users=pagination)

@admin_bp.route('/users/<int:user_id>/reset_password', methods=['POST'])
@login_required
@admin_required
def reset_password(user_id):
    user = User.query.get_or_404(user_id)
    # Reset to default 'password123'
    user.set_password('password123')
    db.session.commit()
    current_app.logger.info(f'Admin {current_user.username} reset password for user {user.username}')
    flash(f"Password for {user.username} has been reset to 'password123'.", 'info')
    return redirect(url_for('admin.users'))

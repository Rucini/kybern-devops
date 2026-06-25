import os
from flask import render_template, redirect, url_for, flash, request, current_app, abort, send_from_directory
from flask_login import login_required, current_user
from app.extensions import db
from app.tickets import tickets_bp
from app.tickets.forms import TicketForm, CommentForm
from app.models import Ticket, Comment
from app.utils import save_attachment

@tickets_bp.route('/', methods=['GET'])
@login_required
def list_tickets():
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status')
    
    query = Ticket.query.filter_by(user_id=current_user.id)
    
    if status_filter:
        query = query.filter_by(status=status_filter)
        
    tickets = query.order_by(Ticket.updated_at.desc()).paginate(page=page, per_page=10, error_out=False)
    
    return render_template('tickets/list.html', tickets=tickets, current_status=status_filter)

@tickets_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = TicketForm()
    if form.validate_on_submit():
        attachment_filename = None
        if form.attachment.data:
            attachment_filename = save_attachment(form.attachment.data)
            
        ticket = Ticket(
            title=form.title.data,
            description=form.description.data,
            category=form.category.data,
            priority=form.priority.data,
            user_id=current_user.id,
            attachment=attachment_filename
        )
        db.session.add(ticket)
        db.session.commit()
        current_app.logger.info(f'Ticket created: {ticket.id} by User: {current_user.username}')
        flash('Ticket has been created successfully!', 'success')
        return redirect(url_for('tickets.view', ticket_id=ticket.id))
        
    return render_template('tickets/create_edit.html', form=form, title="Create Ticket")

@tickets_bp.route('/<int:ticket_id>', methods=['GET', 'POST'])
@login_required
def view(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    
    # Ensure only the owner or an admin can view the ticket
    if ticket.user_id != current_user.id and not current_user.is_admin:
        abort(403)
        
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data, ticket_id=ticket.id, user_id=current_user.id)
        db.session.add(comment)
        db.session.commit()
        flash('Comment added.', 'success')
        return redirect(url_for('tickets.view', ticket_id=ticket.id))
        
    comments = ticket.comments.order_by(Comment.created_at.asc()).all()
    return render_template('tickets/view.html', ticket=ticket, comments=comments, form=form)

@tickets_bp.route('/<int:ticket_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    
    # Only owner can edit, and maybe not if closed (but let's allow basic edits for now)
    if ticket.user_id != current_user.id:
        abort(403)
        
    form = TicketForm()
    if form.validate_on_submit():
        ticket.title = form.title.data
        ticket.description = form.description.data
        ticket.category = form.category.data
        ticket.priority = form.priority.data
        
        if form.attachment.data:
            attachment_filename = save_attachment(form.attachment.data)
            if attachment_filename:
                ticket.attachment = attachment_filename
                
        db.session.commit()
        flash('Ticket has been updated.', 'success')
        return redirect(url_for('tickets.view', ticket_id=ticket.id))
    elif request.method == 'GET':
        form.title.data = ticket.title
        form.description.data = ticket.description
        form.category.data = ticket.category
        form.priority.data = ticket.priority
        
    return render_template('tickets/create_edit.html', form=form, title="Edit Ticket", ticket=ticket)

@tickets_bp.route('/<int:ticket_id>/close', methods=['POST'])
@login_required
def close(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    if ticket.user_id != current_user.id and not current_user.is_admin:
        abort(403)
        
    ticket.status = 'Closed'
    db.session.commit()
    flash('Ticket has been closed.', 'info')
    return redirect(url_for('tickets.view', ticket_id=ticket.id))

@tickets_bp.route('/download/<filename>')
@login_required
def download(filename):
    # This route serves attachments
    # We should ensure the user has access to the ticket this belongs to,
    # but for simplicity in this lesson, we just ensure they are logged in.
    # In a real app, query the DB to verify ownership/admin status.
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

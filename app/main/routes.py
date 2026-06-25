from flask import render_template, jsonify, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.extensions import db
from app.main import main_bp
from app.models import Ticket, User
from app.main.forms import ChangePasswordForm

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.is_admin:
            # Admin dashboard: overview of all tickets
            open_tickets = Ticket.query.filter_by(status='Open').count()
            in_progress_tickets = Ticket.query.filter_by(status='In Progress').count()
            resolved_tickets = Ticket.query.filter_by(status='Resolved').count()
            recent_tickets = Ticket.query.order_by(Ticket.created_at.desc()).limit(5).all()
            return render_template('main/dashboard.html', 
                                   open_tickets=open_tickets,
                                   in_progress_tickets=in_progress_tickets,
                                   resolved_tickets=resolved_tickets,
                                   recent_tickets=recent_tickets)
        else:
            # User dashboard: overview of their own tickets
            my_open_tickets = Ticket.query.filter_by(user_id=current_user.id, status='Open').count()
            my_resolved_tickets = Ticket.query.filter_by(user_id=current_user.id, status='Resolved').count()
            recent_tickets = Ticket.query.filter_by(user_id=current_user.id).order_by(Ticket.created_at.desc()).limit(5).all()
            return render_template('main/dashboard.html',
                                   open_tickets=my_open_tickets,
                                   resolved_tickets=my_resolved_tickets,
                                   recent_tickets=recent_tickets)
    return render_template('index.html')

@main_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.check_password(form.old_password.data):
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash('Your password has been updated.', 'success')
            return redirect(url_for('main.profile'))
        else:
            flash('Invalid old password.', 'danger')
    return render_template('main/profile.html', form=form)

@main_bp.route('/health')
def health():
    return jsonify({"status": "ok"})

@main_bp.route('/version')
def version():
    return jsonify({"version": "1.0.0"})

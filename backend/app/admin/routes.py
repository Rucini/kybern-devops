from flask import jsonify, request, current_app
from flask_jwt_extended import jwt_required, current_user
from app.extensions import db
from app.admin import admin_bp
from app.models import Ticket, User
from app.utils import admin_required

@admin_bp.route('/tickets', methods=['GET'])
@jwt_required()
@admin_required
def get_tickets():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    status_filter = request.args.get('status')
    
    query = Ticket.query
    
    if search:
        query = query.filter(Ticket.title.ilike(f'%{search}%') | Ticket.id.ilike(f'%{search}%'))
    if status_filter:
        query = query.filter_by(status=status_filter)
        
    pagination = query.order_by(Ticket.created_at.desc()).paginate(page=page, per_page=15, error_out=False)
    
    return jsonify({
        "items": [t.to_dict() for t in pagination.items],
        "total": pagination.total,
        "pages": pagination.pages,
        "current_page": pagination.page
    }), 200

@admin_bp.route('/tickets/<int:ticket_id>/assign', methods=['PUT'])
@jwt_required()
@admin_required
def assign_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    data = request.get_json() or {}
    assignee_id = data.get('assignee_id')
    
    if not assignee_id:
        return jsonify({"error": "Missing assignee_id"}), 400
        
    ticket.assigned_to = assignee_id
    if ticket.status == 'Open':
        ticket.status = 'Assigned'
    db.session.commit()
    
    return jsonify({
        "message": "Ticket assigned successfully",
        "ticket": ticket.to_dict()
    }), 200

@admin_bp.route('/tickets/<int:ticket_id>/status', methods=['PUT'])
@jwt_required()
@admin_required
def change_ticket_status(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    data = request.get_json() or {}
    status = data.get('status')
    
    if not status:
        return jsonify({"error": "Missing status"}), 400
        
    ticket.status = status
    db.session.commit()
    
    return jsonify({
        "message": "Ticket status updated successfully",
        "ticket": ticket.to_dict()
    }), 200

@admin_bp.route('/tickets/<int:ticket_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    db.session.delete(ticket)
    db.session.commit()
    current_app.logger.info(f'Admin {current_user.username} deleted ticket {ticket_id}')
    return jsonify({"message": "Ticket deleted successfully"}), 200

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
@admin_required
def get_users():
    page = request.args.get('page', 1, type=int)
    pagination = User.query.order_by(User.id.asc()).paginate(page=page, per_page=15, error_out=False)
    
    return jsonify({
        "items": [u.to_dict() for u in pagination.items],
        "total": pagination.total,
        "pages": pagination.pages,
        "current_page": pagination.page
    }), 200

@admin_bp.route('/users/<int:user_id>/reset_password', methods=['POST'])
@jwt_required()
@admin_required
def reset_password(user_id):
    user = User.query.get_or_404(user_id)
    user.set_password('password123')
    db.session.commit()
    current_app.logger.info(f'Admin {current_user.username} reset password for user {user.username}')
    
    return jsonify({"message": f"Password for {user.username} has been reset to 'password123'."}), 200


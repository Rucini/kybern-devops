from flask import jsonify, request
from flask_jwt_extended import jwt_required, current_user
from app.extensions import db
from app.main import main_bp
from app.models import Ticket
from sqlalchemy import or_

@main_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    if current_user.is_admin:
        open_tickets = Ticket.query.filter_by(status='Open').count()
        in_progress_tickets = Ticket.query.filter_by(status='In Progress').count()
        resolved_tickets = Ticket.query.filter_by(status='Resolved').count()
        recent_tickets = Ticket.query.order_by(Ticket.created_at.desc()).limit(5).all()
        
        return jsonify({
            "open_tickets": open_tickets,
            "in_progress_tickets": in_progress_tickets,
            "resolved_tickets": resolved_tickets,
            "recent_tickets": [t.to_dict() for t in recent_tickets]
        }), 200
    else:
        my_open_tickets = Ticket.query.filter(or_(Ticket.user_id == current_user.id, Ticket.assigned_to == current_user.id), Ticket.status == 'Open').count()
        my_resolved_tickets = Ticket.query.filter(or_(Ticket.user_id == current_user.id, Ticket.assigned_to == current_user.id), Ticket.status == 'Resolved').count()
        recent_tickets = Ticket.query.filter(or_(Ticket.user_id == current_user.id, Ticket.assigned_to == current_user.id)).order_by(Ticket.created_at.desc()).limit(5).all()
        
        return jsonify({
            "open_tickets": my_open_tickets,
            "resolved_tickets": my_resolved_tickets,
            "recent_tickets": [t.to_dict() for t in recent_tickets]
        }), 200

@main_bp.route('/profile/password', methods=['PUT'])
@jwt_required()
def change_password():
    data = request.get_json() or {}
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    
    if not old_password or not new_password:
        return jsonify({"error": "Missing old or new password"}), 400
        
    if current_user.check_password(old_password):
        current_user.set_password(new_password)
        db.session.commit()
        return jsonify({"message": "Password updated successfully"}), 200
    else:
        return jsonify({"error": "Invalid old password"}), 401

@main_bp.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

@main_bp.route('/version', methods=['GET'])
def version():
    return jsonify({"version": "1.0.0"})


import os
from flask import jsonify, request, current_app, abort, send_from_directory
from flask_jwt_extended import jwt_required, current_user
from app.extensions import db
from app.tickets import tickets_bp
from app.models import Ticket, Comment
from app.utils import save_attachment

@tickets_bp.route('/', methods=['GET'])
@jwt_required()
def list_tickets():
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status')
    
    query = Ticket.query.filter_by(user_id=current_user.id)
    
    if status_filter:
        query = query.filter_by(status=status_filter)
        
    pagination = query.order_by(Ticket.updated_at.desc()).paginate(page=page, per_page=10, error_out=False)
    
    return jsonify({
        "items": [t.to_dict() for t in pagination.items],
        "total": pagination.total,
        "pages": pagination.pages,
        "current_page": pagination.page
    }), 200

@tickets_bp.route('/', methods=['POST'])
@jwt_required()
def create_ticket():
    title = request.form.get('title')
    description = request.form.get('description')
    category = request.form.get('category')
    priority = request.form.get('priority')
    
    if not title or not description or not category or not priority:
        return jsonify({"error": "Missing required fields"}), 400
        
    attachment_filename = None
    if 'attachment' in request.files:
        attachment_filename = save_attachment(request.files['attachment'])
        
    ticket = Ticket(
        title=title,
        description=description,
        category=category,
        priority=priority,
        user_id=current_user.id,
        attachment=attachment_filename
    )
    db.session.add(ticket)
    db.session.commit()
    
    current_app.logger.info(f'Ticket created: {ticket.id} by User: {current_user.username}')
    
    return jsonify({
        "message": "Ticket created successfully",
        "ticket": ticket.to_dict()
    }), 201

@tickets_bp.route('/<int:ticket_id>', methods=['GET'])
@jwt_required()
def view_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    
    if ticket.user_id != current_user.id and not current_user.is_admin:
        return jsonify({"error": "Forbidden"}), 403
        
    comments = ticket.comments.order_by(Comment.created_at.asc()).all()
    
    ticket_dict = ticket.to_dict()
    ticket_dict['comments'] = [c.to_dict() for c in comments]
    
    return jsonify(ticket_dict), 200

@tickets_bp.route('/<int:ticket_id>', methods=['PUT'])
@jwt_required()
def edit_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    
    if ticket.user_id != current_user.id and not current_user.is_admin:
        return jsonify({"error": "Forbidden"}), 403
        
    ticket.title = request.form.get('title', ticket.title)
    ticket.description = request.form.get('description', ticket.description)
    ticket.category = request.form.get('category', ticket.category)
    ticket.priority = request.form.get('priority', ticket.priority)
    
    if 'attachment' in request.files:
        attachment_filename = save_attachment(request.files['attachment'])
        if attachment_filename:
            ticket.attachment = attachment_filename
            
    db.session.commit()
    return jsonify({
        "message": "Ticket updated successfully",
        "ticket": ticket.to_dict()
    }), 200

@tickets_bp.route('/<int:ticket_id>/close', methods=['POST'])
@jwt_required()
def close_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    if ticket.user_id != current_user.id and not current_user.is_admin:
        return jsonify({"error": "Forbidden"}), 403
        
    ticket.status = 'Closed'
    db.session.commit()
    
    return jsonify({
        "message": "Ticket closed successfully",
        "ticket": ticket.to_dict()
    }), 200

@tickets_bp.route('/<int:ticket_id>/comments', methods=['POST'])
@jwt_required()
def add_comment(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    if ticket.user_id != current_user.id and not current_user.is_admin:
        return jsonify({"error": "Forbidden"}), 403
        
    data = request.get_json() or {}
    body = data.get('body')
    
    if not body:
        return jsonify({"error": "Missing comment body"}), 400
        
    comment = Comment(body=body, ticket_id=ticket.id, user_id=current_user.id)
    db.session.add(comment)
    db.session.commit()
    
    return jsonify({
        "message": "Comment added successfully",
        "comment": comment.to_dict()
    }), 201

@tickets_bp.route('/download/<filename>', methods=['GET'])
@jwt_required()
def download(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

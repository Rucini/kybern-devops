import os
from functools import wraps
from flask import abort, current_app
from flask_login import current_user
from werkzeug.utils import secure_filename

def admin_required(f):
    """Decorator to require admin role for a view."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    """Check if uploaded file has an allowed extension."""
    ALLOWED_EXTENSIONS = current_app.config.get('ALLOWED_EXTENSIONS', {'pdf', 'png', 'jpg', 'jpeg'})
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_attachment(file):
    """Saves a file securely to the upload folder and returns the filename."""
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Ensure the filename is unique to avoid overwrites
        import uuid
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        
        upload_path = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_path, exist_ok=True)
        
        file.save(os.path.join(upload_path, unique_filename))
        return unique_filename
    return None

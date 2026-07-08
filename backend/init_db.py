import os
from app import create_app
from app.extensions import db
from app.models import User

app = create_app()

def init_db():
    with app.app_context():
        # Create instance directory if it doesn't exist
        os.makedirs(app.instance_path, exist_ok=True)
        
        # Create all database tables
        db.create_all()
        
        # Check if admin user exists
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(username='admin', email='admin@example.com', role='admin')
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            db.session.commit()
            print("Database initialized and Admin user created (admin / admin123).")
        else:
            print("Database already initialized and Admin user exists.")

if __name__ == '__main__':
    init_db()

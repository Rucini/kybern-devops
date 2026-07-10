from app import create_app
from app.models import User, Ticket
app = create_app()
with app.app_context():
    u = User.query.filter_by(username="testuser1").first()
    print("User ID:", u.id)
    t = Ticket.query.filter_by(user_id=u.id).all()
    print("Tickets for testuser1:", [tk.id for tk in t])

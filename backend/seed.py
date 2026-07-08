import random
from app import create_app
from app.extensions import db
from app.models import User, Ticket, Comment

app = create_app()

def seed_data():
    with app.app_context():
        print("Starting seed process...")
        
        # Seed 20 Users
        users = []
        for i in range(1, 21):
            username = f'user{i}'
            email = f'{username}@example.com'
            user = User.query.filter_by(username=username).first()
            if not user:
                user = User(username=username, email=email)
                user.set_password('password123')
                db.session.add(user)
                users.append(user)
        
        db.session.commit()
        print(f"Seeded 20 normal users.")
        
        # Re-fetch users including admin to assign tickets to random users
        all_users = User.query.filter_by(role='user').all()
        admin_users = User.query.filter_by(role='admin').all()
        
        if not all_users:
            print("No users available to create tickets. Aborting seed.")
            return

        categories = ['Network', 'Hardware', 'Software', 'Email', 'Server', 'Security']
        priorities = ['Low', 'Medium', 'High', 'Critical']
        statuses = ['Open', 'Assigned', 'In Progress', 'Waiting', 'Resolved', 'Closed']
        
        # Seed 100 Tickets
        tickets_created = 0
        for i in range(1, 101):
            user = random.choice(all_users)
            ticket = Ticket(
                title=f'Sample Ticket Issue #{i}',
                description=f'This is an automatically generated description for ticket {i}. The user is experiencing an issue related to {random.choice(categories)}.',
                category=random.choice(categories),
                priority=random.choice(priorities),
                status=random.choice(statuses),
                user_id=user.id
            )
            
            # If status is assigned or later, assign to admin
            if ticket.status in ['Assigned', 'In Progress', 'Waiting', 'Resolved', 'Closed'] and admin_users:
                ticket.assigned_to = random.choice(admin_users).id
                
            db.session.add(ticket)
            db.session.commit() # commit here to get ticket id
            tickets_created += 1
            
            # Add random comments to the ticket
            num_comments = random.randint(0, 3)
            for j in range(num_comments):
                comment_user = random.choice([user, random.choice(admin_users)] if admin_users else [user])
                comment = Comment(
                    body=f'This is a sample comment {j+1} for ticket {ticket.id}',
                    ticket_id=ticket.id,
                    user_id=comment_user.id
                )
                db.session.add(comment)
        
        db.session.commit()
        print(f"Seeded 100 tickets with random comments.")
        print("Seed completed successfully.")

if __name__ == '__main__':
    seed_data()

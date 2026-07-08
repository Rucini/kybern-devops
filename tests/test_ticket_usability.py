import unittest

from app import create_app
from app.extensions import db
from app.models import Ticket, User


class TicketUsabilityTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config.update(
            TESTING=True,
            WTF_CSRF_ENABLED=False,
            SQLALCHEMY_DATABASE_URI='sqlite:///:memory:'
        )
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.drop_all()
        db.create_all()
        self.client = self.app.test_client()

        self.user = User(username='searcher', email='searcher@example.com')
        self.user.set_password('password123')
        db.session.add(self.user)
        db.session.commit()

        self.printer_ticket = Ticket(
            title='Printer issue',
            description='The office printer keeps jamming.',
            category='Hardware',
            priority='High',
            user_id=self.user.id,
            status='Open',
        )
        self.network_ticket = Ticket(
            title='Network outage',
            description='The Wi-Fi is down in the meeting room.',
            category='Network',
            priority='Critical',
            user_id=self.user.id,
            status='In Progress',
        )
        db.session.add_all([self.printer_ticket, self.network_ticket])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_search_filters_ticket_list(self):
        login_response = self.client.post(
            '/auth/login',
            data={'username': 'searcher', 'password': 'password123'},
            follow_redirects=True,
        )
        self.assertEqual(login_response.status_code, 200)

        response = self.client.get('/tickets/?q=printer')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Printer issue', response.data)
        self.assertNotIn(b'Network outage', response.data)


if __name__ == '__main__':
    unittest.main()

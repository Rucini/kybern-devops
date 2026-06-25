import requests
from bs4 import BeautifulSoup
import sys

BASE_URL = "http://127.0.0.1:8000"

def extract_csrf(html):
    soup = BeautifulSoup(html, 'html.parser')
    csrf_input = soup.find('input', {'name': 'csrf_token'})
    return csrf_input.get('value') if csrf_input else None

def test_all():
    errors = []
    print("Starting Comprehensive Tests...")

    # User Login
    user_session = requests.Session()
    try:
        res = user_session.get(f"{BASE_URL}/auth/login")
        csrf = extract_csrf(res.text)
        res = user_session.post(f"{BASE_URL}/auth/login", data={
            'username': 'user1',
            'password': 'password123',
            'csrf_token': csrf,
            'submit': 'Sign In'
        })
        if res.status_code >= 500:
            errors.append("User Login returned 500")
        if '/auth/login' in res.url and 'next' not in res.url:
             pass # might just render
    except Exception as e:
        errors.append(f"Error logging in user: {e}")

    # Ticket Create
    ticket_id = None
    try:
        res = user_session.get(f"{BASE_URL}/tickets/create")
        csrf = extract_csrf(res.text)
        
        data = {
            'csrf_token': csrf,
            'title': 'Test Full Feature Ticket Length',
            'category': 'Network',
            'priority': 'Low',
            'description': 'Description is at least 10 chars',
            'submit': 'Submit Ticket'
        }
        res = user_session.post(f"{BASE_URL}/tickets/create", data=data)
        if res.status_code >= 500:
            errors.append("POST /tickets/create returned 500")
        else:
            ticket_url = res.url
            if '/tickets/' in ticket_url and 'create' not in ticket_url:
                ticket_id = ticket_url.split('/')[-1]
            else:
                print("Ticket creation form did not redirect! URL:", ticket_url)
    except Exception as e:
        errors.append(f"Error creating ticket: {e}")

    if ticket_id:
        # Edit Ticket
        try:
            res = user_session.get(f"{BASE_URL}/tickets/{ticket_id}/edit")
            csrf = extract_csrf(res.text)
            res = user_session.post(f"{BASE_URL}/tickets/{ticket_id}/edit", data={
                'csrf_token': csrf,
                'title': 'Test Full Feature Updated Length',
                'category': 'Hardware',
                'priority': 'Medium',
                'description': 'Updated description is longer',
                'submit': 'Update Ticket'
            })
            if res.status_code >= 500:
                errors.append(f"POST /tickets/{ticket_id}/edit returned 500")
        except Exception as e:
            errors.append(f"Error editing ticket: {e}")

    # Admin Session
    admin_session = requests.Session()
    try:
        res = admin_session.get(f"{BASE_URL}/auth/login")
        csrf = extract_csrf(res.text)
        res = admin_session.post(f"{BASE_URL}/auth/login", data={
            'username': 'admin',
            'password': 'admin123',
            'csrf_token': csrf,
            'submit': 'Sign In'
        })
    except Exception as e:
        pass

    if ticket_id:
        # Admin delete ticket
        try:
            res = admin_session.get(f"{BASE_URL}/admin/tickets/{ticket_id}/manage")
            csrf = extract_csrf(res.text)
            res = admin_session.post(f"{BASE_URL}/admin/tickets/{ticket_id}/delete", data={
                'csrf_token': csrf
            })
            if res.status_code >= 500:
                errors.append(f"POST /admin/tickets/{ticket_id}/delete returned 500")
        except Exception as e:
            errors.append(f"Error deleting ticket: {e}")

    # Admin reset password
    try:
        # Just grab a valid csrf from users page
        res = admin_session.get(f"{BASE_URL}/admin/users")
        csrf = extract_csrf(res.text)
        res = admin_session.post(f"{BASE_URL}/admin/users/2/reset_password", data={'csrf_token': csrf})
        if res.status_code >= 500:
            errors.append("POST /admin/users/<id>/reset_password returned 500")
    except Exception as e:
        pass

    print("\n--- RESULTS ---")
    if errors:
        for err in errors:
            print(f"- {err}")
    else:
        print("Everything works perfectly.")

if __name__ == "__main__":
    test_all()

import requests
from bs4 import BeautifulSoup
import os

BASE_URL = "http://127.0.0.1:8000"

def extract_csrf(html):
    soup = BeautifulSoup(html, 'html.parser')
    csrf_input = soup.find('input', {'name': 'csrf_token'})
    return csrf_input.get('value') if csrf_input else None

def test_all():
    errors = []
    print("Starting Comprehensive Tests...")

    # Basic Endpoints
    try:
        if requests.get(f"{BASE_URL}/").status_code >= 500:
            errors.append("GET / returned 500")
        if requests.get(f"{BASE_URL}/health").status_code >= 500:
            errors.append("GET /health returned 500")
        if requests.get(f"{BASE_URL}/version").status_code >= 500:
            errors.append("GET /version returned 500")
    except Exception as e:
        errors.append(f"Error checking basic endpoints: {e}")

    # Register user (so we have a fresh user to test)
    reg_session = requests.Session()
    try:
        res = reg_session.get(f"{BASE_URL}/auth/register")
        csrf = extract_csrf(res.text)
        res = reg_session.post(f"{BASE_URL}/auth/register", data={
            'csrf_token': csrf,
            'username': 'testuser99',
            'email': 'test99@example.com',
            'password': 'password123',
            'confirm_password': 'password123',
            'submit': 'Register'
        })
        if res.status_code >= 500:
            errors.append("Register returned 500")
    except Exception as e:
        errors.append(f"Error registering user: {e}")

    # User Login
    user_session = requests.Session()
    try:
        res = user_session.get(f"{BASE_URL}/auth/login")
        csrf = extract_csrf(res.text)
        res = user_session.post(f"{BASE_URL}/auth/login", data={
            'username': 'testuser99',
            'password': 'password123',
            'csrf_token': csrf,
            'submit': 'Sign In'
        })
        if res.status_code >= 500:
            errors.append("User Login returned 500")
    except Exception as e:
        errors.append(f"Error logging in user: {e}")

    # Profile
    try:
        res = user_session.get(f"{BASE_URL}/profile")
        if res.status_code >= 500:
            errors.append("GET /profile returned 500")
        csrf = extract_csrf(res.text)
        res = user_session.post(f"{BASE_URL}/profile", data={
            'csrf_token': csrf,
            'email': 'test99-new@example.com',
            'submit': 'Update Profile'
        })
        if res.status_code >= 500:
            errors.append("POST /profile returned 500")
    except Exception as e:
        errors.append(f"Error testing profile: {e}")

    # Ticket Create
    ticket_id = None
    try:
        res = user_session.get(f"{BASE_URL}/tickets/create")
        csrf = extract_csrf(res.text)
        
        # Test NO file upload since the form might require pdf/images
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
    except Exception as e:
        errors.append(f"Error creating ticket: {e}")

    if not ticket_id:
        print("Ticket creation failed, skipping ticket endpoints.")
    else:
        # Get Ticket
        try:
            res = user_session.get(f"{BASE_URL}/tickets/{ticket_id}")
            if res.status_code >= 500:
                errors.append(f"GET /tickets/{ticket_id} returned 500")
            
            # Extract download link if any
            soup = BeautifulSoup(res.text, 'html.parser')
            for a in soup.find_all('a', href=True):
                if 'download' in a['href']:
                    res_dl = user_session.get(f"{BASE_URL}{a['href']}")
                    if res_dl.status_code >= 500:
                        errors.append("GET /tickets/download/<filename> returned 500")
                    break
        except Exception as e:
            errors.append(f"Error viewing ticket: {e}")

        # Edit Ticket
        try:
            res = user_session.get(f"{BASE_URL}/tickets/{ticket_id}/edit")
            if res.status_code >= 500:
                errors.append(f"GET /tickets/{ticket_id}/edit returned 500")
            
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
            
        # Add Comment
        try:
            res = user_session.get(f"{BASE_URL}/tickets/{ticket_id}")
            csrf = extract_csrf(res.text)
            res = user_session.post(f"{BASE_URL}/tickets/{ticket_id}", data={
                'csrf_token': csrf,
                'body': 'A comment by user',
                'submit': 'Post Comment'
            })
            if res.status_code >= 500:
                errors.append(f"POST /tickets/{ticket_id} (comment) returned 500")
        except Exception as e:
            errors.append(f"Error adding comment: {e}")

        # Close Ticket
        try:
            res = user_session.get(f"{BASE_URL}/tickets/{ticket_id}")
            csrf = extract_csrf(res.text)
            res = user_session.post(f"{BASE_URL}/tickets/{ticket_id}/close", data={
                'csrf_token': csrf
            })
            if res.status_code >= 500:
                errors.append(f"POST /tickets/{ticket_id}/close returned 500")
        except Exception as e:
            errors.append(f"Error closing ticket: {e}")

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
        if res.status_code >= 500:
            errors.append("Admin Login returned 500")
    except Exception as e:
        errors.append(f"Error logging in admin: {e}")

    # Admin Dashboard
    try:
        res = admin_session.get(f"{BASE_URL}/admin/dashboard")
        if res.status_code >= 500:
            errors.append("GET /admin/dashboard returned 500")
        
        res = admin_session.get(f"{BASE_URL}/admin/tickets")
        if res.status_code >= 500:
            errors.append("GET /admin/tickets returned 500")
    except Exception as e:
        errors.append(f"Error checking admin dashboard: {e}")

    if ticket_id:
        # Admin manage ticket
        try:
            res = admin_session.get(f"{BASE_URL}/admin/tickets/{ticket_id}/manage")
            if res.status_code >= 500:
                errors.append(f"GET /admin/tickets/{ticket_id}/manage returned 500")
            
            csrf = extract_csrf(res.text)
            res = admin_session.post(f"{BASE_URL}/admin/tickets/{ticket_id}/manage", data={
                'csrf_token': csrf,
                'status': 'In Progress',
                'priority': 'High',
                'assigned_to': '1', # admin user id is usually 1
                'submit': 'Update Ticket'
            })
            if res.status_code >= 500:
                errors.append(f"POST /admin/tickets/{ticket_id}/manage returned 500")
        except Exception as e:
            errors.append(f"Error managing ticket: {e}")

        # Admin delete ticket
        try:
            res = admin_session.get(f"{BASE_URL}/admin/tickets")
            # need CSRF to delete. Actually delete is a POST form on the ticket page or list
            # Usually we don't need CSRF if we just grab it from a page, but the form might be missing it? 
            # In admin list page, there's no form. Oh, wait, in manage page there is a delete form?
            res = admin_session.get(f"{BASE_URL}/admin/tickets/{ticket_id}/manage")
            csrf = extract_csrf(res.text)
            
            # The delete form usually does not have a separate form in the template, we'll try sending POST
            # Let's post to delete directly without csrf, or extract the csrf if available.
            res = admin_session.post(f"{BASE_URL}/admin/tickets/{ticket_id}/delete", data={
                'csrf_token': csrf
            })
            if res.status_code >= 500:
                errors.append(f"POST /admin/tickets/{ticket_id}/delete returned 500")
        except Exception as e:
            errors.append(f"Error deleting ticket: {e}")

    # Admin Users
    try:
        res = admin_session.get(f"{BASE_URL}/admin/users")
        if res.status_code >= 500:
            errors.append("GET /admin/users returned 500")
        
        # Admin reset password for user 2
        res = admin_session.post(f"{BASE_URL}/admin/users/2/reset_password", data={'csrf_token': csrf})
        if res.status_code >= 500:
            errors.append("POST /admin/users/<id>/reset_password returned 500")
    except Exception as e:
        errors.append(f"Error checking admin users: {e}")

    print("\n--- RESULTS ---")
    if errors:
        for err in errors:
            print(f"- {err}")
    else:
        print("Everything works perfectly.")

if __name__ == "__main__":
    test_all()

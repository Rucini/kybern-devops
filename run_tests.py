import requests
from bs4 import BeautifulSoup

BASE_URL = "http://127.0.0.1:8000"

def extract_csrf(html):
    soup = BeautifulSoup(html, 'html.parser')
    csrf_input = soup.find('input', {'name': 'csrf_token'})
    return csrf_input.get('value') if csrf_input else None

def test_app():
    errors = []
    print("Starting tests...")
    
    # 1. Access homepage
    try:
        res = requests.get(f"{BASE_URL}/")
        if res.status_code >= 500:
            errors.append(f"Homepage returned {res.status_code}")
        elif res.status_code != 200:
            errors.append(f"Homepage returned {res.status_code}")
    except Exception as e:
        errors.append(f"Error accessing homepage: {e}")

    # 2. Login as admin
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
            errors.append(f"Admin login returned {res.status_code}")
        if 'Logout' not in res.text and '/auth/logout' not in res.text:
            errors.append("Admin login failed")
    except Exception as e:
        errors.append(f"Error logging in admin: {e}")

    # 3. Admin dashboard and view tickets
    try:
        res = admin_session.get(f"{BASE_URL}/admin/tickets")
        if res.status_code >= 500:
            errors.append(f"Admin dashboard returned {res.status_code}")
        elif res.status_code != 200:
            errors.append(f"Admin dashboard returned {res.status_code}")
            
        # find a ticket link in dashboard
        soup = BeautifulSoup(res.text, 'html.parser')
        ticket_links = [a['href'] for a in soup.find_all('a', href=True) if '/tickets/' in a['href'] and a['href'] != '/tickets/']
        if ticket_links:
            res = admin_session.get(f"{BASE_URL}{ticket_links[0]}")
            if res.status_code >= 500:
                errors.append(f"Admin view ticket returned {res.status_code}")
    except Exception as e:
        errors.append(f"Error admin dashboard: {e}")

    # 4. Login as user1
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
            errors.append(f"User login returned {res.status_code}")
    except Exception as e:
        errors.append(f"Error user login: {e}")

    # 5. Create ticket
    ticket_url = None
    try:
        res = user_session.get(f"{BASE_URL}/tickets/create")
        csrf = extract_csrf(res.text)
        res = user_session.post(f"{BASE_URL}/tickets/create", data={
            'csrf_token': csrf,
            'title': 'Test Ticket that is long enough',
            'category': 'Network',
            'priority': 'Low',
            'description': 'Description is at least 10 chars',
            'submit': 'Submit Ticket'
        })
        if res.status_code >= 500:
            errors.append(f"Ticket creation returned {res.status_code}")
        elif res.url == f"{BASE_URL}/tickets/create":
            errors.append("Ticket creation form did not redirect (validation error?)")
        else:
            ticket_url = res.url
    except Exception as e:
        errors.append(f"Error creating ticket: {e}")

    # 6. Add comment
    if ticket_url:
        try:
            res = user_session.get(ticket_url)
            csrf = extract_csrf(res.text)
            res = user_session.post(ticket_url, data={
                'csrf_token': csrf,
                'body': 'This is a test comment',
                'submit': 'Post Comment'
            })
            if res.status_code >= 500:
                errors.append(f"Add comment returned {res.status_code}")
            elif "Internal Server Error" in res.text:
                errors.append("Add comment returned 500 Internal Server Error in HTML")
        except Exception as e:
            errors.append(f"Error adding comment: {e}")

    # 7. Verify all endpoints work
    print("Errors found:")
    for err in errors:
        print(f"- {err}")
    if not errors:
        print("No errors found!")

if __name__ == "__main__":
    test_app()

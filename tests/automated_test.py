import requests
from bs4 import BeautifulSoup
import sys

BASE_URL = "http://127.0.0.1:8000"

def extract_csrf(html):
    soup = BeautifulSoup(html, 'html.parser')
    csrf_input = soup.find('input', {'name': 'csrf_token'})
    return csrf_input.get('value') if csrf_input else None

def run_tests():
    errors = []
    print("--- IT Helpdesk Automated Tests ---")

    # 1. Access the homepage
    print("\n1. Accessing the homepage...")
    try:
        res = requests.get(f"{BASE_URL}/")
        if res.status_code != 200:
            errors.append(f"Homepage GET returned {res.status_code}")
        else:
            print("   -> Success")
    except Exception as e:
        errors.append(f"Homepage GET Error: {e}")

    # 2. Login as admin
    print("\n2. Logging in as Admin...")
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
        else:
            print("   -> Admin logged in successfully")
    except Exception as e:
        errors.append(f"Admin Login Error: {e}")

    # 3. Navigate to the admin dashboard and view tickets
    print("\n3. Navigating to Admin Dashboard and viewing tickets...")
    try:
        res = admin_session.get(f"{BASE_URL}/admin/dashboard")
        if res.status_code >= 500:
            errors.append(f"Admin dashboard returned {res.status_code}")
        
        res = admin_session.get(f"{BASE_URL}/admin/tickets")
        if res.status_code >= 500:
            errors.append(f"Admin tickets view returned {res.status_code}")
        else:
            print("   -> Admin dashboard and tickets loaded successfully")
    except Exception as e:
        errors.append(f"Admin Dashboard Error: {e}")

    # 4. Login as a normal user
    print("\n4. Logging in as normal user (user1)...")
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
        else:
            print("   -> User1 logged in successfully")
    except Exception as e:
        errors.append(f"User Login Error: {e}")

    # 5. Create a ticket
    print("\n5. Creating a ticket...")
    ticket_id = None
    try:
        res = user_session.get(f"{BASE_URL}/tickets/create")
        csrf = extract_csrf(res.text)
        res = user_session.post(f"{BASE_URL}/tickets/create", data={
            'csrf_token': csrf,
            'title': 'Test Automated Ticket',
            'category': 'Software',
            'priority': 'Medium',
            'description': 'This is a test description for the ticket',
            'submit': 'Submit Ticket'
        })
        if res.status_code >= 500:
            errors.append(f"Ticket creation POST returned {res.status_code}")
        else:
            if '/tickets/' in res.url and 'create' not in res.url:
                ticket_id = res.url.split('/')[-1]
                print(f"   -> Ticket created successfully! Ticket ID: {ticket_id}")
            else:
                errors.append("Ticket creation form did not redirect properly.")
    except Exception as e:
        errors.append(f"Ticket Creation Error: {e}")

    # 6. Add a comment to the ticket
    print("\n6. Adding a comment to the ticket...")
    if ticket_id:
        try:
            res = user_session.get(f"{BASE_URL}/tickets/{ticket_id}")
            csrf = extract_csrf(res.text)
            res = user_session.post(f"{BASE_URL}/tickets/{ticket_id}", data={
                'csrf_token': csrf,
                'body': 'Automated test comment on the ticket',
                'submit': 'Post Comment'
            })
            if res.status_code >= 500:
                errors.append(f"Ticket comment POST returned {res.status_code}")
            else:
                print("   -> Comment added successfully")
        except Exception as e:
            errors.append(f"Comment Error: {e}")
    else:
        print("   -> Skipping comment creation because ticket ID is missing")

    # 7. Verify other admin endpoints for 500 errors
    print("\n7. Verifying other admin endpoints (Delete Ticket, Reset Password)...")
    if ticket_id:
        try:
            res = admin_session.get(f"{BASE_URL}/admin/tickets/{ticket_id}/manage")
            csrf = extract_csrf(res.text)
            res = admin_session.post(f"{BASE_URL}/admin/tickets/{ticket_id}/delete", data={
                'csrf_token': csrf
            })
            if res.status_code == 500:
                errors.append(f"Admin Delete Ticket POST returned 500 Internal Server Error")
                print("   -> Found 500 Error on Delete Ticket")
        except Exception as e:
            errors.append(f"Admin Delete Ticket Error: {e}")

    try:
        res = admin_session.get(f"{BASE_URL}/admin/users")
        csrf = extract_csrf(res.text)
        res = admin_session.post(f"{BASE_URL}/admin/users/2/reset_password", data={'csrf_token': csrf})
        if res.status_code == 500:
            errors.append(f"Admin Reset Password POST returned 500 Internal Server Error")
            print("   -> Found 500 Error on Reset Password")
    except Exception as e:
        errors.append(f"Admin Reset Password Error: {e}")

    print("\n================ SUMMARY ================")
    if errors:
        print("Bugs / Errors Found:")
        for err in errors:
            print(f" - {err}")
    else:
        print("Everything works perfectly.")

if __name__ == "__main__":
    run_tests()

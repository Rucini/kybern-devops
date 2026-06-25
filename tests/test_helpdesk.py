import requests
from bs4 import BeautifulSoup
import traceback
import sys

BASE_URL = "http://127.0.0.1:8000"

def extract_csrf(html):
    soup = BeautifulSoup(html, 'html.parser')
    csrf_input = soup.find('input', {'name': 'csrf_token'})
    if csrf_input:
        return csrf_input.get('value')
    return None

def main():
    print("Starting Helpdesk Tests...")
    errors = []

    # Admin Session
    admin_session = requests.Session()
    
    # 1. Access the homepage
    try:
        print("1. Accessing Homepage...")
        res = admin_session.get(f"{BASE_URL}/")
        res.raise_for_status()
        if res.status_code == 500:
            errors.append("Homepage returned 500")
        print("Homepage accessed.")
    except Exception as e:
        errors.append(f"Error accessing homepage: {e}")

    # 2. Login as admin
    try:
        print("2. Logging in as admin...")
        res = admin_session.get(f"{BASE_URL}/auth/login")
        csrf = extract_csrf(res.text)
        
        login_data = {
            'username': 'admin',
            'password': 'admin123',
            'csrf_token': csrf,
            'submit': 'Sign In'
        }
        res = admin_session.post(f"{BASE_URL}/auth/login", data=login_data)
        
        if res.status_code >= 500:
            errors.append(f"Admin login returned {res.status_code}")
        
        # Check if login successful (usually redirects or shows logout)
        if 'Logout' not in res.text and '/auth/logout' not in res.text:
            errors.append("Admin login failed or 'Logout' not found in response")
        print("Admin login complete.")
    except Exception as e:
        errors.append(f"Error logging in admin: {e}")

    # 3. Navigate to admin dashboard and view tickets
    try:
        print("3. Navigating to Admin Dashboard...")
        # Often dashboard is at /admin or /dashboard or /tickets
        # Let's try to find the admin dashboard link from the response
        soup = BeautifulSoup(res.text, 'html.parser')
        admin_links = soup.find_all('a', href=True)
        dashboard_url = None
        for link in admin_links:
            if 'admin' in link['href'].lower() or 'dashboard' in link['href'].lower():
                dashboard_url = link['href']
                break
        
        if not dashboard_url:
            dashboard_url = "/admin" # Guessing fallback
            
        print(f"Using dashboard URL: {dashboard_url}")
        res = admin_session.get(f"{BASE_URL}{dashboard_url}" if dashboard_url.startswith("/") else f"{BASE_URL}/{dashboard_url}")
        if res.status_code >= 500:
            errors.append(f"Admin dashboard returned {res.status_code}")
        
        # Try to view a ticket list if it's there
        # Look for tickets links
        soup = BeautifulSoup(res.text, 'html.parser')
        ticket_links = [a['href'] for a in soup.find_all('a', href=True) if '/ticket/' in a['href']]
        if ticket_links:
            res = admin_session.get(f"{BASE_URL}{ticket_links[0]}")
            if res.status_code >= 500:
                errors.append(f"Admin view ticket returned {res.status_code}")
        print("Admin dashboard check complete.")
    except Exception as e:
        errors.append(f"Error accessing admin dashboard: {e}")

    # 4. Login as normal user
    user_session = requests.Session()
    try:
        print("4. Logging in as user1...")
        res = user_session.get(f"{BASE_URL}/auth/login")
        csrf = extract_csrf(res.text)
        login_data = {
            'username': 'user1',
            'password': 'password123',
            'csrf_token': csrf,
            'submit': 'Sign In'
        }
        res = user_session.post(f"{BASE_URL}/auth/login", data=login_data)
        if res.status_code >= 500:
            errors.append(f"User login returned {res.status_code}")
            
        if 'Logout' not in res.text and '/auth/logout' not in res.text:
            errors.append("User login failed or 'Logout' not found in response")
        print("User login complete.")
    except Exception as e:
        errors.append(f"Error logging in user1: {e}")

    # 5. Create a ticket
    ticket_url = None
    try:
        print("5. Creating a ticket...")
        # The form is probably at /ticket/new or /tickets/create
        res = user_session.get(f"{BASE_URL}/") # get dashboard
        soup = BeautifulSoup(res.text, 'html.parser')
        new_ticket_link = None
        for link in soup.find_all('a', href=True):
            if 'new' in link['href'].lower() or 'create' in link['href'].lower():
                if 'ticket' in link['href'].lower():
                    new_ticket_link = link['href']
                    break
        
        if not new_ticket_link:
            new_ticket_link = "/ticket/new" # Fallback
            
        print(f"New ticket URL: {new_ticket_link}")
        res = user_session.get(f"{BASE_URL}{new_ticket_link}")
        if res.status_code >= 500:
            errors.append(f"New ticket page returned {res.status_code}")
        
        csrf = extract_csrf(res.text)
        # We need to guess the ticket form fields: usually title, description, maybe priority, category
        # Let's inspect the form
        soup = BeautifulSoup(res.text, 'html.parser')
        form = soup.find('form')
        ticket_data = {'csrf_token': csrf}
        if form:
            for inp in form.find_all(['input', 'textarea', 'select']):
                name = inp.get('name')
                if not name or name == 'csrf_token' or name == 'submit':
                    continue
                if inp.name == 'select':
                    options = inp.find_all('option')
                    if options:
                        ticket_data[name] = options[0].get('value') or options[0].text
                else:
                    ticket_data[name] = 'Test Ticket Value'
        else:
            ticket_data.update({'title': 'Test Ticket', 'description': 'This is a test ticket'})
            
        ticket_data['submit'] = 'Submit'
        
        res = user_session.post(f"{BASE_URL}{new_ticket_link}", data=ticket_data)
        if res.status_code >= 500:
            errors.append(f"Ticket creation returned {res.status_code}")
            
        # Try to find the ticket URL
        soup = BeautifulSoup(res.text, 'html.parser')
        for link in soup.find_all('a', href=True):
            if '/ticket/' in link['href'] and 'new' not in link['href']:
                ticket_url = link['href']
                break
        print(f"Ticket created. Found ticket URL: {ticket_url}")
    except Exception as e:
        errors.append(f"Error creating ticket: {e}")

    # 6. Add a comment to the ticket
    try:
        print("6. Adding a comment...")
        if ticket_url:
            res = user_session.get(f"{BASE_URL}{ticket_url}")
            if res.status_code >= 500:
                errors.append(f"View ticket returned {res.status_code}")
            
            csrf = extract_csrf(res.text)
            # Find comment form
            soup = BeautifulSoup(res.text, 'html.parser')
            forms = soup.find_all('form')
            comment_form_action = ticket_url
            for f in forms:
                action = f.get('action')
                if action and 'comment' in action:
                    comment_form_action = action
                    break
            
            # Form data for comment
            comment_data = {
                'csrf_token': csrf,
                'body': 'This is a test comment',
                'submit': 'Submit'
            }
            # Some apps use 'comment', some use 'body', some use 'content'. We check inputs
            for f in forms:
                if 'comment' in f.get('action', '') or len(forms) == 1:
                    for inp in f.find_all(['textarea', 'input']):
                        name = inp.get('name')
                        if name and name not in ['csrf_token', 'submit']:
                            comment_data[name] = 'Test Comment Content'

            res = user_session.post(f"{BASE_URL}{comment_form_action}", data=comment_data)
            if res.status_code >= 500:
                errors.append(f"Add comment returned {res.status_code}")
                
            # If 500 happens, we might get an internal server error HTML
            if "Internal Server Error" in res.text:
                errors.append(f"Add comment returned 500 Internal Server Error string in HTML")
        else:
            errors.append("Could not find ticket URL to add comment to")
            
        print("Comment addition check complete.")
    except Exception as e:
        errors.append(f"Error adding comment: {e}")

    print("\n--- RESULTS ---")
    if errors:
        print("Bugs Found:")
        for err in errors:
            print(f"- {err}")
    else:
        print("No bugs found. Everything works perfectly.")

if __name__ == "__main__":
    main()

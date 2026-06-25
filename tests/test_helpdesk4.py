import requests
from bs4 import BeautifulSoup

BASE_URL = "http://127.0.0.1:8000"

def extract_csrf(html):
    soup = BeautifulSoup(html, 'html.parser')
    csrf_input = soup.find('input', {'name': 'csrf_token'})
    return csrf_input.get('value') if csrf_input else None

user_session = requests.Session()
user_session.post(f"{BASE_URL}/auth/login", data={'username': 'user1', 'password': 'password123', 'csrf_token': extract_csrf(user_session.get(f"{BASE_URL}/auth/login").text), 'submit': 'Sign In'})

res = user_session.get(f"{BASE_URL}/tickets/create")
csrf = extract_csrf(res.text)

ticket_data = {
    'csrf_token': csrf,
    'title': 'Test Ticket that is long enough',
    'category': 'Network',
    'priority': 'Low',
    'description': 'Description is at least 10 chars',
    'submit': 'Submit Ticket'
}

res = user_session.post(f"{BASE_URL}/tickets/create", data=ticket_data)
print(res.status_code, res.url)
print(res.text[:500])
if "This field is required." in res.text or "error" in res.text.lower():
    print("Found error in HTML")

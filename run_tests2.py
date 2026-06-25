import requests
from bs4 import BeautifulSoup

BASE_URL = "http://127.0.0.1:8000"

def extract_csrf(html):
    soup = BeautifulSoup(html, 'html.parser')
    csrf_input = soup.find('input', {'name': 'csrf_token'})
    return csrf_input.get('value') if csrf_input else None

user_session = requests.Session()
res = user_session.get(f"{BASE_URL}/auth/login")
csrf = extract_csrf(res.text)
user_session.post(f"{BASE_URL}/auth/login", data={
    'username': 'user1',
    'password': 'password123',
    'csrf_token': csrf,
    'submit': 'Sign In'
})

res = user_session.get(f"{BASE_URL}/tickets/create")
csrf = extract_csrf(res.text)
res = user_session.post(f"{BASE_URL}/tickets/create", data={
    'csrf_token': csrf,
    'title': 'Another test ticket',
    'category': 'Network',
    'priority': 'Low',
    'description': 'Description is at least 10 chars',
    'submit': 'Submit Ticket'
})

ticket_url = res.url
print(f"Created ticket: {ticket_url}")

res = user_session.get(ticket_url)
csrf = extract_csrf(res.text)
res = user_session.post(ticket_url, data={
    'csrf_token': csrf,
    'body': 'This is a test comment',
    'submit': 'Post Comment'
})

print(f"Comment post status: {res.status_code}")

res = user_session.get(ticket_url)
if "This is a test comment" in res.text:
    print("Comment successfully added and visible!")
else:
    print("Comment not found in page!")
    print(res.text)

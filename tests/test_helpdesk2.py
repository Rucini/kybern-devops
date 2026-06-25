import requests
from bs4 import BeautifulSoup
import traceback

BASE_URL = "http://127.0.0.1:8000"

def extract_csrf(html):
    soup = BeautifulSoup(html, 'html.parser')
    csrf_input = soup.find('input', {'name': 'csrf_token'})
    return csrf_input.get('value') if csrf_input else None

user_session = requests.Session()
res = user_session.get(f"{BASE_URL}/auth/login")
csrf = extract_csrf(res.text)
user_session.post(f"{BASE_URL}/auth/login", data={'username': 'user1', 'password': 'password123', 'csrf_token': csrf, 'submit': 'Sign In'})

res = user_session.get(f"{BASE_URL}/tickets/create")
csrf = extract_csrf(res.text)
ticket_data = {
    'csrf_token': csrf,
    'title': 'Another Test',
    'description': 'Description text',
    'priority': 'low',
    'category': 'hardware',
    'submit': 'Submit'
}

res = user_session.post(f"{BASE_URL}/tickets/create", data=ticket_data)
print("Create ticket status:", res.status_code)
print("Redirect URL:", res.url)
print("History:", res.history)

soup = BeautifulSoup(res.text, 'html.parser')
print("Links on page:")
for a in soup.find_all('a', href=True):
    print(" -", a['href'])

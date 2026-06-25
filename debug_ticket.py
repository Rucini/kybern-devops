import requests
from bs4 import BeautifulSoup
BASE_URL = "http://127.0.0.1:8000"

def extract_csrf(html):
    soup = BeautifulSoup(html, 'html.parser')
    csrf_input = soup.find('input', {'name': 'csrf_token'})
    return csrf_input.get('value') if csrf_input else None

session = requests.Session()
res = session.get(f"{BASE_URL}/auth/login")
csrf = extract_csrf(res.text)
session.post(f"{BASE_URL}/auth/login", data={
    'username': 'admin', 'password': 'admin123', 'csrf_token': csrf, 'submit': 'Sign In'
})

res = session.get(f"{BASE_URL}/tickets/create")
csrf = extract_csrf(res.text)

# We will create a dummy file to upload
with open("dummy.txt", "w") as f:
    f.write("Hello")

files = {'attachment': ('dummy.txt', open('dummy.txt', 'rb'))}
data = {
    'csrf_token': csrf,
    'title': 'Test Full Feature',
    'category': 'Network',
    'priority': 'Low',
    'description': 'Description is at least 10 chars',
    'submit': 'Submit Ticket'
}
res = session.post(f"{BASE_URL}/tickets/create", data=data, files=files)
print("Status:", res.status_code)
print("URL:", res.url)
print("Text:", res.text[:200])
if "error" in res.text.lower():
    soup = BeautifulSoup(res.text, 'html.parser')
    for err in soup.find_all(class_='invalid-feedback'):
        print(err.text)
    for err in soup.find_all(class_='alert'):
        print(err.text)

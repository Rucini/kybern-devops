import os
import time
from playwright.sync_api import sync_playwright

def run_ui_tests():
    os.makedirs('ui_screenshots', exist_ok=True)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Desktop view
        context = browser.new_context(viewport={'width': 1280, 'height': 720})
        page = context.new_page()

        print("Testing Homepage...")
        page.goto("http://127.0.0.1:8000/")
        page.screenshot(path="ui_screenshots/01_homepage.png", full_page=True)

        print("Testing Login...")
        page.goto("http://127.0.0.1:8000/auth/login")
        page.screenshot(path="ui_screenshots/02_login_page.png")
        
        # User Login
        page.fill("input[name='username']", "user1")
        page.fill("input[name='password']", "password123")
        page.click("input[type='submit']")
        page.wait_for_selector("text=Dashboard") # Wait for dashboard to load
        page.screenshot(path="ui_screenshots/03_user_dashboard.png", full_page=True)

        print("Testing Create Ticket...")
        page.click("text=Create Ticket")
        page.wait_for_selector("form")
        page.screenshot(path="ui_screenshots/04_create_ticket.png", full_page=True)

        # Fill ticket form
        page.fill("input[name='title']", "UI Test Ticket")
        page.fill("textarea[name='description']", "This is a ticket created during the UI test.")
        page.select_option("select[name='category']", label="Hardware")
        page.select_option("select[name='priority']", label="High")
        page.click("input[type='submit']")
        
        # Wait for redirect and view ticket
        page.wait_for_selector("text=Description")
        page.screenshot(path="ui_screenshots/05_ticket_view.png", full_page=True)

        print("Testing Admin Flow...")
        # Logout
        page.click("id=userDropdown")
        page.click("text=Logout")

        # Admin Login
        page.goto("http://127.0.0.1:8000/auth/login")
        page.fill("input[name='username']", "admin")
        page.fill("input[name='password']", "admin123")
        page.click("input[type='submit']")
        page.wait_for_selector("text=Admin Tools")

        # Go to Admin Tickets
        page.goto("http://127.0.0.1:8000/admin/tickets")
        page.screenshot(path="ui_screenshots/06_admin_tickets.png", full_page=True)

        # Go to Admin Manage Ticket
        page.click("text=Manage >> nth=0")
        page.screenshot(path="ui_screenshots/07_admin_manage_ticket.png", full_page=True)

        # Mobile View Test
        print("Testing Mobile Responsiveness...")
        mobile_context = browser.new_context(viewport={'width': 375, 'height': 667}, is_mobile=True)
        mobile_page = mobile_context.new_page()
        mobile_page.goto("http://127.0.0.1:8000/")
        mobile_page.screenshot(path="ui_screenshots/08_mobile_home.png", full_page=True)
        
        mobile_page.goto("http://127.0.0.1:8000/auth/login")
        mobile_page.fill("input[name='username']", "user1")
        mobile_page.fill("input[name='password']", "password123")
        mobile_page.click("input[type='submit']")
        mobile_page.wait_for_selector("text=Dashboard")
        mobile_page.screenshot(path="ui_screenshots/09_mobile_dashboard.png", full_page=True)

        browser.close()
        print("UI Tests completed. Screenshots saved in ui_screenshots/.")

if __name__ == "__main__":
    run_ui_tests()

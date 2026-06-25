# IT Helpdesk Ticket Management System

This is a production-ready Flask application designed as an IT Helpdesk Ticket Management System. The project is tailored for DevOps training scenarios focusing on standard Linux deployments (e.g., Ubuntu) without the use of containerization tools like Docker or Kubernetes.

## Features

*   **User Roles:** Normal users and Admin users.
*   **Ticket Lifecycle:** Create, Edit, View, Comment, and Close tickets.
*   **Admin Dashboard:** Manage all tickets, assign tickets, update statuses, manage users, and reset passwords.
*   **File Uploads:** Users can attach files (pdf, png, jpg, jpeg) up to 5MB to their tickets.
*   **Authentication & Security:** Secure login/registration with Flask-Login, CSRF protection, and password hashing (Werkzeug).
*   **Logging:** Application events are logged to `logs/app.log`.
*   **Health Checks:** Exposes `/health` and `/version` endpoints.

## Project Structure

The project uses Flask Blueprints for a clean, scalable architecture:
```text
project/
├── .env                 # Environment variables
├── config.py            # Application configuration
├── requirements.txt     # Python dependencies
├── run.py               # Application entry point
├── init_db.py           # Database initialization script
├── seed.py              # Script to populate mock data
├── logs/                # Application logs
├── uploads/             # Uploaded attachments
├── instance/            # SQLite database storage
└── app/
    ├── __init__.py      # App factory
    ├── extensions.py    # Flask extensions setup
    ├── models.py        # SQLAlchemy Database models
    ├── utils.py         # Helper functions
    ├── auth/            # Authentication blueprint
    ├── main/            # Core views blueprint
    ├── tickets/         # Ticket management blueprint
    ├── admin/           # Admin features blueprint
    ├── static/          # CSS and JS files
    └── templates/       # Jinja2 HTML templates
```

---

## 1. Local Development Setup

### 1.1 Prerequisites
*   Linux/macOS or Windows
*   Python 3.12+
*   `pip` installed

### 1.2 Virtual Environment
It is highly recommended to use a Python virtual environment to isolate dependencies.
```bash
python3 -m venv venv
source venv/bin/activate
```

### 1.3 Install Dependencies
```bash
pip install -r requirements.txt
```

### 1.4 Environment Variables
Configuration is handled via `.env`. A default `.env` is provided, but in production, you should modify it:
```ini
SECRET_KEY=change-this-in-production
DATABASE_URL=sqlite:///../instance/helpdesk.db
UPLOAD_FOLDER=uploads
FLASK_ENV=development
DEBUG=True
```

### 1.5 Database Initialization
Create the database schema and initialize the default administrator account.
```bash
python init_db.py
```
> **Default Admin:** `admin` / `admin123`

### 1.6 Seed Data (Optional)
To populate the database with mock users, tickets, and comments for testing:
```bash
python seed.py
```

### 1.7 Running the Application
Start the Flask development server:
```bash
python run.py
```
Access the application at `http://127.0.0.1:8000/`.

---

## 2. DevOps & Production Deployment (Linux/Ubuntu)

For a production setup, DO NOT use the built-in Flask server. Instead, use a WSGI server like **Gunicorn** and a reverse proxy like **Nginx**.

### 2.1 File & Directory Permissions
Ensure the application runs under a dedicated service user (e.g., `helpdesk_user`) and that file permissions are set correctly. The application needs write access to:
*   `instance/` (for SQLite database)
*   `uploads/` (for attachments)
*   `logs/` (for application logging)

```bash
sudo chown -R helpdesk_user:www-data /path/to/project
sudo chmod -R 775 /path/to/project/instance
sudo chmod -R 775 /path/to/project/uploads
sudo chmod -R 775 /path/to/project/logs
```

### 2.2 Gunicorn Setup
Install Gunicorn inside your virtual environment:
```bash
pip install gunicorn
```
Test Gunicorn:
```bash
gunicorn -w 4 -b 127.0.0.1:8000 "app:create_app()"
```

### 2.3 Systemd Service
Create a systemd service file `/etc/systemd/system/helpdesk.service` to manage the Gunicorn process.
```ini
[Unit]
Description=Gunicorn instance to serve IT Helpdesk
After=network.target

[Service]
User=helpdesk_user
Group=www-data
WorkingDirectory=/path/to/project
Environment="PATH=/path/to/project/venv/bin"
ExecStart=/path/to/project/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 "app:create_app()"

[Install]
WantedBy=multi-user.target
```
Enable and start the service:
```bash
sudo systemctl enable helpdesk
sudo systemctl start helpdesk
```

### 2.4 Nginx Reverse Proxy
Configure Nginx to proxy requests to Gunicorn. Create `/etc/nginx/sites-available/helpdesk`:
```nginx
server {
    listen 80;
    server_name your_domain_or_ip;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Serve static files directly
    location /static/ {
        alias /path/to/project/app/static/;
    }

    # Increase max upload size for attachments
    client_max_body_size 5M;
}
```
Enable the site and restart Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/helpdesk /etc/nginx/sites-enabled
sudo systemctl restart nginx
```

---

## 3. Monitoring & CI/CD Considerations

*   **Application Logs:** Monitor `/path/to/project/logs/app.log` for runtime errors and login events.
*   **Health Checks:** Configure external monitoring tools to ping the `/health` endpoint to ensure uptime.
*   **CI/CD Pipeline:** Set up GitHub Actions or GitLab CI to run automated tests, linting (flake8), and type checking (mypy). 
*   **Future Dockerization:** While this project is currently deployed natively to teach fundamental Linux operations, its modular structure makes it easily adaptable to Docker and Docker Compose for future lessons.

## Troubleshooting

*   **Database Locked Error:** Ensure proper directory permissions (`775` or `777` strictly inside `instance/`) if running behind a web server using a different user group.
*   **500 Internal Server Error:** Check `logs/app.log` for stack traces.
*   **File Upload Fails:** Ensure Nginx's `client_max_body_size` allows payloads up to 5MB, and verify write permissions for the `uploads/` directory.

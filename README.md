# IT Support Helpdesk System

A modern, production-ready Helpdesk System refactored into a three-tier architecture (React SPA, Flask REST API, PostgreSQL).

## Features
- **User Authentication**: JWT-based login and registration.
- **Ticket Management**: Create, view, and comment on support tickets.
- **File Uploads**: Attach files or screenshots to tickets.
- **Admin Dashboard**: Manage users, assign tickets, update statuses, and track metrics.
- **Modern UI**: Built with React and Ant Design for a responsive, clean interface.

## Architecture

This project is structured as a decoupled system:
- `frontend/`: React 18 SPA (Vite, TypeScript, Ant Design)
- `backend/`: Python Flask REST API (SQLAlchemy, JWT, PostgreSQL)
- `docs/`: Comprehensive system documentation

For detailed architecture diagrams, refer to [Architecture Docs](docs/architecture.md).

## Quickstart (Docker Compose)

The easiest way to run the entire stack is with Docker Compose.

1. **Clone the repository.**
2. **Copy `.env.example` to `.env`** and configure your secrets.
3. **Run Docker Compose:**
   ```bash
   docker-compose up -d --build
   ```
4. **Access the application:**
   - Frontend UI: `http://localhost:3000`
   - Default Admin credentials: `admin` / `password123`
   - Default User credentials: `user` / `password123`

## Documentation Index
- [Architecture & Diagrams](docs/architecture.md)
- [REST API Reference](docs/api.md)
- [Database Schema](docs/database.md)
- [Deployment Guide](docs/deployment.md)

<<<<<<< Updated upstream
## Tech Stack
- **Frontend**: React, Vite, TypeScript, Ant Design, Axios, React Router.
- **Backend**: Python 3, Flask, Flask-JWT-Extended, Flask-SQLAlchemy, Flask-CORS.
- **Database**: PostgreSQL 15.
- **Infrastructure**: Docker, Nginx, Gunicorn.
=======
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
```bashpython init_db.py

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
>>>>>>> Stashed changes

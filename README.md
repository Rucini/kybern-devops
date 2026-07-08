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

## Tech Stack
- **Frontend**: React, Vite, TypeScript, Ant Design, Axios, React Router.
- **Backend**: Python 3, Flask, Flask-JWT-Extended, Flask-SQLAlchemy, Flask-CORS.
- **Database**: PostgreSQL 15.
- **Infrastructure**: Docker, Nginx, Gunicorn.

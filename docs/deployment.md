# Deployment Guide

The application uses Docker and Docker Compose to containerize the frontend, backend, and database into a single cohesive deployment.

## Prerequisites
- Docker
- Docker Compose

## Development

For local development without Docker:

1. **Backend**:
   ```bash
   cd backend
   pip install -r requirements.txt
   python init_db.py
   python seed.py
   python run.py
   ```
2. **Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## Production Deployment with Docker Compose

1. **Environment Variables**:
   Copy `.env.example` to `.env` in the root directory and update the `SECRET_KEY` and `JWT_SECRET_KEY` for security.

2. **Build and Run**:
   From the root directory of the project, run:
   ```bash
   docker-compose up -d --build
   ```

3. **What happens**:
   - `db`: Pulls PostgreSQL 15 and initializes the `helpdesk` database.
   - `backend`: Builds the Python image, waits for the DB to be healthy, runs database initialization (`init_db.py`), seeds initial data (`seed.py`), and starts the Flask Gunicorn server on port 8000.
   - `frontend`: Builds the React SPA using Node, then serves the static assets via Nginx on port 80. Nginx is configured to proxy `/api` requests to the `backend` container.
   
4. **Accessing the App**:
   - Open your browser to `http://localhost:3000` (mapped to frontend port 80).
   - Use the default admin credentials (if seeded): `admin` / `password123`.

## Volumes
- `postgres_data`: Persists the PostgreSQL database.
- `backend_uploads`: Persists uploaded ticket attachments.

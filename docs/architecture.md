# Architecture Overview

This project implements a modern **Three-Tier Architecture**, cleanly separating the frontend user interface, the backend business logic (REST API), and the database layer.

## Overall System Architecture

```mermaid
graph TD
    User([User]) --> |HTTPS| React(React SPA Frontend)
    React --> |JSON / REST| FlaskAPI(Flask Backend API)
    FlaskAPI --> |SQLAlchemy| DB[(PostgreSQL Database)]
```

## Layered Architecture

1. **Presentation Layer (Frontend)**
   - **Framework**: React 18+ via Vite
   - **UI Library**: Ant Design
   - **Routing**: React Router DOM
   - **Responsibility**: Rendering UI, managing local state, input validation, communicating with the backend via Axios.
   
2. **Application Layer (Backend)**
   - **Framework**: Python 3.x with Flask
   - **Authentication**: JWT (JSON Web Tokens) using Flask-JWT-Extended
   - **Responsibility**: Exposing RESTful endpoints, validating requests, enforcing authorization, applying business logic.

3. **Data Access Layer (Database)**
   - **Database**: PostgreSQL
   - **ORM**: SQLAlchemy
   - **Responsibility**: Persisting users, tickets, comments, and relationships.

## Data Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant Database

    User->>Frontend: Clicks "Create Ticket"
    Frontend->>Frontend: Validates Form
    Frontend->>Backend: POST /api/tickets/ (JSON + JWT)
    Backend->>Backend: Verifies JWT & Validates Input
    Backend->>Database: INSERT into tickets table
    Database-->>Backend: Returns new record
    Backend-->>Frontend: 201 Created (JSON Response)
    Frontend->>User: Displays success message & redirects
```

## Container Diagram

```mermaid
graph TD
    Compose(Docker Compose)
    
    Compose --> FrontendContainer
    Compose --> BackendContainer
    Compose --> DBContainer

    subgraph Frontend Container
        Nginx(Nginx Web Server)
        StaticFiles(React Static Assets)
        Nginx --> |Serves| StaticFiles
        Nginx --> |Proxies /api| BackendContainer
    end

    subgraph Backend Container
        Gunicorn(Gunicorn / Flask)
        App(REST API)
        Gunicorn --> App
    end

    subgraph DB Container
        Postgres(PostgreSQL)
    end

    App --> |TCP 5432| Postgres
```

# Database Schema

The database uses PostgreSQL and is mapped using SQLAlchemy.

## ER Diagram

```mermaid
erDiagram
    USER ||--o{ TICKET : "creates"
    USER ||--o{ TICKET : "assigned to"
    USER ||--o{ COMMENT : "authors"
    TICKET ||--o{ COMMENT : "contains"

    USER {
        int id PK
        string username
        string email
        string password_hash
        string role "admin|user"
        datetime created_at
    }

    TICKET {
        int id PK
        string title
        text description
        string status "Open|Assigned|In Progress|Resolved|Closed"
        string priority "Low|Medium|High|Critical"
        string category
        string attachment
        int author_id FK
        int assignee_id FK
        datetime created_at
        datetime updated_at
    }

    COMMENT {
        int id PK
        text body
        int ticket_id FK
        int author_id FK
        datetime created_at
    }
```

## Indexes and Constraints
- `USER.username` is UNIQUE.
- `USER.email` is UNIQUE.
- Foreign Keys enforce relational integrity.

# BASE IMAGE
FROM python:3.11-alpine

WORKDIR /app

# Install system dependencies for PostgreSQL
RUN apk add --no-cache postgresql-dev gcc python3-dev musl-dev

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose port
EXPOSE 8000

# Start command
CMD ["python", "run.py"]
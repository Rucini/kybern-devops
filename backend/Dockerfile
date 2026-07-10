# BASE IMAGE
FROM python:3.11-alpine

WORKDIR /app

# Install system dependencies for PostgreSQL
RUN apk add postgresql-dev gcc python3-dev musl-dev && \
    addgroup -S appgroup && adduser -S appuser -G appgroup

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN chown -R appuser:appgroup /app && chmod -R 755 /app

USER appuser

EXPOSE 8000

# Start command
CMD ["python", "run.py"]
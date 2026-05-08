# Ke Bills API

A FastAPI backend for the Ke Bills application, built with SQLModel and Postgres.

## Prerequisites

- Python 3.10+
- Access to the Postgres database (e.g., via Tailscale)

## Setup Instructions

1. **Clone the repository and set up a virtual environment**
   ```bash
   git clone <repository_url>
   cd kebillie_py_api
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**
   Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
   Open `.env` and configure your settings:
   - `DATABASE_URL`: Ensure this points to your database (e.g., via Tailscale: `postgresql://user@tailscale_ip:5432/ke_bills_db`).
   - `SECRET_KEY`: Generate a secure key (e.g., `python3 -c "import secrets; print(secrets.token_hex(32))"`).

4. **Database Migrations**
   This project uses Alembic for database migrations. To apply the initial schema to your database:
   ```bash
   alembic upgrade head
   ```

## Running the Application

To start the FastAPI development server:
```bash
uvicorn app.main:app --reload
```

The server will start on `http://127.0.0.1:8000`.

## API Documentation

FastAPI automatically generates interactive API documentation. Once the server is running, you can access:
- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## Project Structure

This project follows a "Convention over Configuration" structure:
- `app/main.py`: Entry point and CORS configuration.
- `app/api/v1/`: API routers and endpoints (Controllers).
- `app/models/`: SQLModel database schemas.
- `app/schemas/`: Pydantic models for data validation (DTOs).
- `app/crud/`: Reusable database operations.
- `app/services/`: External integrations and complex business logic (e.g. ML models).
- `app/tasks/`: Asynchronous background jobs.
- `app/core/`: Configuration and settings.
- `app/db/`: Database connection and session management.

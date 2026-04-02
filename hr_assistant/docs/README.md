# HR Assistant — Setup Guide

A FastAPI backend, React/TypeScript frontend, and optional MCP server for an AI-powered HR assistant.

All commands below are run from the `hr_assistant/` directory unless stated otherwise.

---

## Prerequisites

- Python 3.11+
- Node.js 18+ and npm 9+
- PostgreSQL 15+ (or Docker)
- An OpenAI API key

---

## Step 1 — Start PostgreSQL

**Local install:** Start the PostgreSQL service — it will be available at `localhost:5432`.

**Docker:**
```bash
cd hr_assistant_api
docker-compose up -d postgres
```

---

## Step 2 — Set Up the Database

```bash
psql -U postgres -f docs/employee_db_schema_script/employee_db_schema.sql
```

This creates the `hr_assistant_db` database and all required tables.

---

## Step 3 — Set Up the Backend

**Activate the virtual environment** (from `GenAI_Masters_Program` root):
```bash
# macOS / Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

**Install dependencies:**
```bash
pip install -r requirements.txt
```

**Configure environment variables:**
```bash
cd hr_assistant_api
cp .env.example .env
```

Edit `.env` and set these required values:

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `OPENAI_API_KEY` | Your OpenAI API key |
| `SECRET_KEY` | A long random string |

**Start the backend:**
```bash
python run.py
```

The API will be available at `http://localhost:5000`. Verify with:
```bash
curl http://localhost:5000/health
# {"status": "ok"}
```

> **Windows:** Use `curl.exe` instead of `curl`.

---

## Step 4 — Set Up the Frontend

```bash
cd hr_assistant_web
npm install
cp .env.example .env
npm start
```

The app will open at `http://localhost:3000`.

---

## Step 5 — Set Up the MCP Server (Optional)

The MCP server requires the backend from Step 3 to be running first.

```bash
python -m hr_assistant_api.mcp_server.server
```

---

## Running Tests

From the `hr_assistant/` directory:

```bash
pytest test_hr_assistant/ -v
```

Tests use an in-memory SQLite database and mock OpenAI calls — no external services required.

---

## API Reference

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/api/departments` | List departments |
| POST | `/api/departments` | Create a department |
| GET | `/api/employees` | List employees |
| POST | `/api/employees` | Create an employee |
| GET | `/api/employees/<id>` | Get one employee |
| PUT | `/api/employees/<id>` | Update an employee |
| DELETE | `/api/employees/<id>` | Delete an employee |
| GET | `/api/employees/<id>/leave-requests` | List leave requests |
| POST | `/api/employees/<id>/leave-requests` | Submit a leave request |
| GET | `/api/employees/<id>/expense-claims` | List expense claims |
| POST | `/api/employees/<id>/expense-claims` | Submit an expense claim |
| POST | `/api/chat` | Get an AI response |
| POST | `/api/chat/stream` | Stream an AI response (SSE) |

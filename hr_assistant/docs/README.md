# HR Assistant — Setup Guide

This guide covers everything you need to get the HR Assistant application running locally, including the Python/FastAPI backend API, React/TypeScript frontend, MCP server, and test suite.

All shell commands below are run from the `hr_assistant/` directory unless stated otherwise.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Project Structure](#project-structure)
3. [Architecture Overview](#architecture-overview)
4. [Step 1 — Start PostgreSQL](#step-1--start-postgresql)
5. [Step 2 — Set Up the Database Schema](#step-2--set-up-the-database-schema)
6. [Step 3 — Set Up the Backend](#step-3--set-up-the-backend)
7. [Step 3.5 — Test API Endpoints (Windows)](#step-35--test-api-endpoints-windows)
8. [Step 4 — Set Up the Frontend](#step-4--set-up-the-frontend)
9. [Step 5 — Set Up the MCP Server (Optional)](#step-5--set-up-the-mcp-server-optional)
10. [Running Tests](#running-tests)
11. [API Endpoint Reference](#api-endpoint-reference)

---

## Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | 3.11+ | Use pyenv or the official installer |
| Node.js | 18+ | LTS recommended |
| npm | 9+ | Comes with Node |
| PostgreSQL | 15+ | Or use Docker (see Step 1) |
| Docker | 24+ | Optional — for containerised setup |
| curl.exe | — | For API testing (Windows) |
| OpenAI API Key | — | Required for AI chat features |

---

## Project Structure

```
GenAI_Masters_Program/
├── .venv/                                 # Shared virtual environment (recommended)
└── hr_assistant/
    ├── docs/
    │   ├── README.md                      # This file
    │   └── employee_db_schema_script/
    │       ├── employee_db_schema.md      # Schema documentation
    │       └── employee_db_schema.sql     # Executable PostgreSQL script
    ├── hr_assistant_api/                  # Python/FastAPI backend
    │   ├── app/
    │   │   ├── __init__.py                # App factory
    │   │   ├── config.py                  # Config classes
    │   │   ├── models/                    # SQLAlchemy ORM models
    │   │   ├── schemas/                   # Pydantic schemas
    │   │   ├── services/                  # AI, vector store, policy services
    │   │   └── routes/                    # FastAPI routers
    │   ├── mcp_server/                    # MCP server (stdio transport)
    │   ├── requirements.txt
    │   ├── .env.example
    │   ├── run.py
    │   ├── Dockerfile
    │   └── docker-compose.yml
    ├── hr_assistant_web/                  # React/TypeScript frontend
    │   ├── public/
    │   ├── src/
    │   │   ├── components/                # Reusable UI components
    │   │   ├── pages/                     # Route-level page components
    │   │   ├── services/                  # Axios API client
    │   │   └── types/                     # TypeScript interfaces
    │   ├── package.json
    │   └── tailwind.config.js
    ├── hr_policies/
    │   └── hr_policies.pdf                # Source HR policy document
    ├── test_hr_assistant/                 # Pytest test suite
    │   ├── conftest.py
    │   ├── test_employees.py
    │   ├── test_chat.py
    │   └── test_models.py
    └── requirements.txt                   # Installs hr_assistant_api dependencies
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        Browser                              │
│            React / TypeScript / Tailwind CSS                │
│                   hr_assistant_web                          │
└────────────────────────┬────────────────────────────────────┘
                         │  HTTP / REST + SSE
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  FastAPI REST API                            │
│              hr_assistant_api  (port 5000)                  │
│                                                             │
│  Routes: /api/employees  /api/departments  /api/chat        │
│  Services: AIService  VectorStoreService  HRPolicyService   │
└──────┬──────────────────────┬──────────────────────────────┘
       │                      │
       ▼                      ▼
┌────────────┐       ┌──────────────────────┐
│ PostgreSQL │       │      ChromaDB        │
│  (port     │       │  (vector embeddings) │
│   5432)    │       │      (port 8000)     │
│ Schema:    │       │                      │
│ hr_assistant│       │                      │
└────────────┘       └──────────┬───────────┘
                                │
                                ▼
                      ┌─────────────────┐
                      │   OpenAI API    │
                      │  GPT-4 + Ada    │
                      └─────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              MCP Server (stdio transport)                    │
│          hr_assistant_api/mcp_server/server.py              │
│  Tools: get_employee_info  answer_hr_question               │
│         submit_leave_request  submit_expense_claim          │
│         list_employees                                      │
└─────────────────────────────────────────────────────────────┘
```

**Key design decisions:**
- The FastAPI backend is the single source of truth for all business logic.
- ChromaDB persists HR policy embeddings locally; they are generated once on first load.
- The MCP server is a thin client that calls the FastAPI REST API — it does not access the database directly.
- The React frontend communicates exclusively through the REST API and SSE stream.

---

## Step 1 — Start PostgreSQL

Choose **one** option:

- **Option-1 — Local install**

  Install PostgreSQL 15 and start the service using your OS package manager or the official installer. PostgreSQL will be available at `localhost:5432`.

- **Option-2 — Docker**

  ```bash
  cd hr_assistant_api
  docker-compose up -d postgres
  ```

  PostgreSQL will be available at `localhost:5432` with user `postgres` and password `password`.

---

## Step 2 — Set Up the Database Schema

Run the SQL script to create the database, `hr_assistant` schema, all tables, indexes, and triggers in one step:

```bash
psql -U postgres -f docs/employee_db_schema_script/employee_db_schema.sql
```

This creates:
- Database: `hr_assistant_db`
- Schema: `hr_assistant`
- Tables: `departments`, `employees`, `benefits`, `leave_requests`, `expense_claims`, `onboarding_tasks`

---

## Step 3 — Set Up the Backend

### 3.1 Activate the virtual environment

Choose **one** option:

- **Option-1 — Shared root-level `.venv` (recommended for local development)**

  A single `.venv` at the `GenAI_Masters_Program` root can be shared across all sub-projects:

  ```bash
  # macOS / Linux
  source ../.venv/bin/activate

  # Windows
  ..\\.venv\Scripts\activate
  ```

- **Option-2 — Dedicated `.venv` inside `hr_assistant_api`**

  Create and activate an isolated environment for this project only:

  ```bash
  cd hr_assistant_api
  python -m venv .venv

  # macOS / Linux
  source .venv/bin/activate

  # Windows
  .venv\Scripts\activate
  ```

### 3.2 Install dependencies

Choose the option that matches your venv choice above:

- **Option-1 — Shared root-level `.venv`**

  Run from the `hr_assistant` directory. The top-level `requirements.txt` includes all API dependencies:

  ```bash
  pip install -r requirements.txt
  ```

- **Option-2 — Dedicated `.venv`**

  Run from inside `hr_assistant_api`:

  ```bash
  cd hr_assistant_api
  pip install -r requirements.txt
  ```

### 3.3 Configure environment variables

From inside `hr_assistant_api`:

```bash
cd hr_assistant_api
cp .env.example .env
```

Edit `.env` and set at minimum:

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `OPENAI_API_KEY` | Your OpenAI API key |
| `SECRET_KEY` | A long random string for application security |
| `CHROMA_PERSIST_DIR` | Directory where ChromaDB stores data (default: `./chroma_data`) |
| `HR_POLICIES_PATH` | Path to the HR policies PDF (default: `../hr_policies/hr_policies.pdf`) |
| `DEBUG` | Set to `true` for local development |

### 3.4 Run the backend

Choose **one** option:

- **Option-1 — Manual**

  From inside `hr_assistant_api`:

  ```bash
  python run.py
  ```

  The API will be available at `http://localhost:5000`. Verify with:

  **Windows:**
  ```bash
  curl.exe http://localhost:5000/health
  # {"status": "ok"}
  ```

  **macOS/Linux:**
  ```bash
  curl http://localhost:5000/health
  # {"status": "ok"}
  ```

- **Option-2 — Docker Compose (all services)**

  Starts PostgreSQL, ChromaDB, and the FastAPI backend together. Ensure `.env` has at least `OPENAI_API_KEY` and `SECRET_KEY` set first.

  ```bash
  cd hr_assistant_api
  docker-compose up --build
  ```

---

## Step 3.5 — Test API Endpoints (Windows)

### Windows curl.exe Usage

On Windows, use `curl.exe` instead of `curl` to access the real curl utility:

```bash
# Health check
curl.exe http://localhost:5000/health

# List all employees
curl.exe http://localhost:5000/api/employees

# List all departments
curl.exe http://localhost:5000/api/departments

# Create a new department
curl.exe -X POST http://localhost:5000/api/departments ^
  -H "Content-Type: application/json" ^
  -d "{\"name\": \"Research\", \"description\": \"R&D team\"}"

# Create a new employee
curl.exe -X POST http://localhost:5000/api/employees ^
  -H "Content-Type: application/json" ^
  -d "{\"employee_number\": \"EMP009\", \"first_name\": \"Alex\", \"last_name\": \"Taylor\", \"email\": \"alex.taylor@company.com\", \"department_id\": 1, \"position\": \"Product Manager\", \"hire_date\": \"2024-01-15\", \"salary\": 95000}"
```

### Troubleshooting Common Issues

**Permission Denied Errors:**
If you get database permission errors, run this SQL in pgAdmin:

```sql
-- Fix database permissions
GRANT ALL ON SCHEMA hr_assistant TO postgres;
GRANT ALL ON ALL TABLES IN SCHEMA hr_assistant TO postgres;
ALTER DEFAULT PRIVILEGES IN SCHEMA hr_assistant GRANT ALL ON TABLES TO postgres;
```

**PowerShell curl Issues:**
- Always use `curl.exe` not `curl` on Windows
- Use `^` for line continuation in PowerShell
- Escape quotes properly in JSON strings

**Success Verification:**
If everything is working correctly, you should see a response like this when testing:

```bash
curl.exe http://localhost:5000/api/employees
# Expected response: JSON with 8 employees and pagination info
```

The response should show employees with department information, confirming that the `hr_assistant` schema is properly configured and accessible.

---

## Step 4 — Set Up the Frontend

### 4.1 Install Node dependencies

```bash
cd hr_assistant_web
npm install
```

### 4.2 Configure environment variables

```bash
cp .env.example .env
```

Edit `.env`:

```
REACT_APP_API_URL=http://localhost:5000
```

### 4.3 Start the development server

```bash
npm start
```

The React app will open at `http://localhost:3000`.

### 4.4 Build for production (optional)

```bash
npm run build
```

The optimised output is placed in `hr_assistant_web/build/`.

---

## Step 5 — Set Up the MCP Server (Optional)

The MCP server exposes HR tools over the Model Context Protocol using stdio transport. It calls the FastAPI REST API internally, so the API must be running first (Step 3.4).

### 5.1 Configure the API base URL (optional)

By default the MCP server connects to `http://localhost:5000/api`. To override:

```bash
export HR_API_BASE=http://your-api-host:5000/api
```

### 5.2 Run the MCP server

From the `hr_assistant` directory:

```bash
python -m hr_assistant_api.mcp_server.server
# or
python hr_assistant_api/mcp_server/server.py
```

### 5.3 Available MCP tools

| Tool | Description |
|------|-------------|
| `get_employee_info` | Retrieve employee details by ID or email |
| `answer_hr_question` | Answer HR policy questions using GPT-4 + ChromaDB |
| `submit_leave_request` | Submit a leave request for an employee |
| `submit_expense_claim` | Submit an expense claim for an employee |
| `list_employees` | List employees with optional department filter |

---

## Running Tests

### 1. Activate the virtual environment

From the `GenAI_Masters_Program` root:

- **Option-1 — Shared root-level `.venv`**

  ```bash
  # macOS / Linux
  source .venv/bin/activate

  # Windows
  .venv\Scripts\activate
  ```

- **Option-2 — Dedicated `.venv`**

  ```bash
  # macOS / Linux
  source hr_assistant/hr_assistant_api/.venv/bin/activate

  # Windows
  hr_assistant\hr_assistant_api\.venv\Scripts\activate
  ```

### 2. Run the full test suite

From the `hr_assistant` directory:

```bash
pytest test_hr_assistant/ -v
```

### 3. Run a specific test file

```bash
pytest test_hr_assistant/test_employees.py -v
pytest test_hr_assistant/test_chat.py -v
pytest test_hr_assistant/test_models.py -v
```

### 4. Run with coverage

```bash
pip install pytest-cov
pytest test_hr_assistant/ --cov=app --cov-report=term-missing
```

Tests use an in-memory SQLite database and mock OpenAI calls — no external services are required to run the suite.

---

## API Endpoint Reference

### Health

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Liveness check |

### Departments

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/departments` | List all departments |
| POST | `/api/departments` | Create a department |

### Employees

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/employees` | List employees (pagination + filters) |
| POST | `/api/employees` | Create an employee |
| GET | `/api/employees/<id>` | Get one employee |
| PUT | `/api/employees/<id>` | Update an employee |
| DELETE | `/api/employees/<id>` | Delete an employee |

### Leave Requests

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/employees/<id>/leave-requests` | List leave requests |
| POST | `/api/employees/<id>/leave-requests` | Submit a leave request |
| PUT | `/api/employees/<id>/leave-requests/<req_id>` | Update a leave request |

### Expense Claims

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/employees/<id>/expense-claims` | List expense claims |
| POST | `/api/employees/<id>/expense-claims` | Submit an expense claim |

### Onboarding Tasks

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/employees/<id>/onboarding-tasks` | List onboarding tasks |

### Chat

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/chat` | Get a complete AI response |
| POST | `/api/chat/stream` | Stream an AI response via SSE |

#### POST `/api/chat` request body

```json
{
  "message": "How many days of annual leave am I entitled to?",
  "employee_id": 42
}
```

#### POST `/api/chat` response

```json
{
  "response": "According to company policy, full-time employees are entitled to 20 days of annual leave per year..."
}
```

#### POST `/api/chat/stream` SSE event format

```
data: {"token": "According"}
data: {"token": " to"}
...
data: {"done": true}
```

# HR Assistant

An AI-powered HR assistant with interactive org charts, searchable tables, and intelligent responses.

## 🚀 Features

- **Interactive Org Chart** - Expandable/collapsible organizational structure
- **Smart Tables** - Searchable and sortable employee data
- **AI-Powered** - Natural language HR queries with structured responses
- **Real-time Streaming** - Instant AI responses with SSE
- **Type-Safe** - Full TypeScript implementation

## 📋 Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- OpenAI API key

## ⚡ Quick Start

### 1. Database Setup
```bash
# Start PostgreSQL (Docker)
cd hr_assistant_api
docker-compose up -d postgres

# Create database
psql -U postgres -f docs/employee_db_schema_script/employee_db_schema.sql
```

### 2. Backend
```bash
# Activate virtual environment
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cd hr_assistant_api
cp .env.example .env
# Edit .env with your DATABASE_URL and OPENAI_API_KEY

# Start server
python run.py
```

### 3. Frontend
```bash
cd hr_assistant_web
npm install
cp .env.example .env
npm start
```

Visit `http://localhost:3000` to start using the HR Assistant.

## 🎯 Usage Examples

Try these queries in the chat:
- "What is the org structure?"
- "List all holidays"
- "How many employees are there?"
- "What is the vacation policy?"

## 🧪 Testing

```bash
pytest test_hr_assistant/ -v
```

## 📚 API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/chat` | Get AI response |
| POST | `/api/chat/stream` | Stream AI response |
| GET | `/api/employees` | List employees |
| GET | `/api/departments` | List departments |

## 🏗️ Architecture

- **Backend**: FastAPI + PostgreSQL + OpenAI
- **Frontend**: React + TypeScript + Tailwind CSS
- **AI**: Structured JSON responses with type-based rendering

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

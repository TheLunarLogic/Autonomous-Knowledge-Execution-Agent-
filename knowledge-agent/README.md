# 🧠 Autonomous Knowledge Execution Agent (AKEA)

An AI-powered full-stack application that retrieves knowledge from internal sources, reasons over it, decides and executes actions autonomously, and explains every decision — with full audit logging.

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18+-blue?logo=react&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-316192?logo=postgresql&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-0.4+-purple)

---

## ✨ What It Does

```
User Query → Retrieve Knowledge → Reason → Decide Action → Execute → Explain
```

1. **Retrieve** — Searches a vector database (ChromaDB) for relevant knowledge chunks
2. **Reason** — LLM analyzes retrieved data in context of the query
3. **Decide** — Picks an action: `answer_question`, `generate_report`, `flag_issue`, or `no_action`
4. **Execute** — Runs the chosen action function
5. **Explain** — Generates a human-readable explanation of the decision
6. **Audit** — Logs every execution to PostgreSQL for transparency

### 🔐 Bonus Features
- **Short-term memory** — Maintains last 5 queries for follow-up context
- **Approval flow** — Critical actions (e.g., `flag_issue`) require user confirmation
- **Empty retrieval handling** — Explicitly states when no knowledge matches

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│                React Frontend                    │
│  (Query Input → Answer Card → Audit Log Viewer) │
└────────────────────┬────────────────────────────┘
                     │ HTTP (Axios)
┌────────────────────▼────────────────────────────┐
│              FastAPI Backend                     │
│  POST /api/v1/ask    GET /api/v1/logs           │
├─────────────────────────────────────────────────┤
│           LangGraph Agent Pipeline               │
│  retrieve → reason → decide → execute → explain │
├──────────────┬──────────────┬───────────────────┤
│  PostgreSQL  │   ChromaDB   │   AWS Bedrock     │
│  (Knowledge  │   (Vector    │   (LLM +          │
│   + Audit)   │    Search)   │    Embeddings)    │
└──────────────┴──────────────┴───────────────────┘
```

---

## 📁 Project Structure

```
knowledge-agent/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point + lifespan
│   │   ├── core/
│   │   │   ├── config.py        # Pydantic Settings (.env)
│   │   │   └── logging.py       # Structured logger
│   │   ├── api/v1/
│   │   │   ├── router.py        # v1 route combiner
│   │   │   └── routes/
│   │   │       ├── ask.py       # POST /api/v1/ask
│   │   │       └── logs.py      # GET /api/v1/logs
│   │   ├── db/
│   │   │   ├── base.py          # SQLAlchemy base
│   │   │   ├── session.py       # Async engine + session
│   │   │   └── models.py        # KnowledgeItem + AuditLog
│   │   ├── schemas/
│   │   │   ├── query.py         # QueryRequest/Response
│   │   │   └── log.py           # AuditLogResponse
│   │   ├── knowledge/
│   │   │   ├── loader.py        # JSON/CSV → Postgres + ChromaDB
│   │   │   └── vector_store.py  # ChromaDB retrieve()
│   │   ├── agent/
│   │   │   ├── graph.py         # LangGraph state machine
│   │   │   ├── nodes.py         # 5 pipeline nodes
│   │   │   └── actions.py       # Action functions
│   │   ├── services/
│   │   │   └── audit_service.py # Audit log CRUD
│   │   └── utils/helpers.py
│   ├── alembic/                 # DB migrations
│   ├── data/                    # Sample JSON + CSV
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── api/agentApi.js
│   │   ├── components/
│   │   ├── pages/
│   │   ├── App.jsx
│   │   └── main.jsx
│   └── package.json
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.11+** (via Conda)
- **Node.js 18+**
- **PostgreSQL 15+** running on `localhost:5432`
- **AWS Account** with Bedrock access (for LLM)

### 1. Clone the Repository

```bash
git clone https://github.com/TheLunarLogic/Autonomous-Knowledge-Execution-Agent-.git
cd Autonomous-Knowledge-Execution-Agent-/knowledge-agent
```

### 2. Backend Setup

```bash
# Create and activate conda environment
conda create -n knowledge-agent python=3.11 -y
conda activate knowledge-agent

# Install dependencies
cd backend
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database URL and AWS credentials

# Create the PostgreSQL database
psql -U postgres -c "CREATE DATABASE knowledge_agent;"

# Run database migrations
alembic upgrade head

# Start the backend
uvicorn app.main:app --reload --port 8000
```

### 3. Load Sample Knowledge

With the backend running, load the sample data:

```bash
curl -X POST http://localhost:8000/api/v1/load-knowledge
```

### 4. Frontend Setup

```bash
# In a new terminal
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173** in your browser.

---

## 🔧 Configuration

Edit `backend/.env`:

```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/knowledge_agent

# AWS Bedrock
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
BEDROCK_EMBEDDING_MODEL_ID=amazon.titan-embed-text-v1

# ChromaDB
CHROMA_PATH=./chroma_data
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/ask` | Submit a query to the agent |
| `GET` | `/api/v1/logs` | Fetch audit log entries |
| `POST` | `/api/v1/load-knowledge` | Load sample data into knowledge base |
| `GET` | `/health` | Health check |

### Example Request

```bash
curl -X POST http://localhost:8000/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "What wireless headphones do you have?"}'
```

### Example Response

```json
{
  "answer": "Based on the available knowledge:\n\nWe have two wireless audio products...",
  "action_taken": "answer_question",
  "explanation": "I found relevant product information in the knowledge base matching your query about wireless headphones.",
  "require_approval": false
}
```

---

## 🧪 Sample Test Queries

| # | Query | Expected Action |
|---|-------|-----------------|
| 1 | "What wireless headphones do you have?" | `answer_question` |
| 2 | "Generate a report of all premium products" | `generate_report` |
| 3 | "What's the weather today?" | `no_action` |
| 4 | "Tell me more about the first one" | `answer_question` (uses memory) |
| 5 | "Flag all products with price over $500" | `flag_issue` (requires approval) |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11, FastAPI, SQLAlchemy (async) |
| Database | PostgreSQL + Alembic migrations |
| Vector DB | ChromaDB (persistent, local) |
| Agent Engine | LangGraph (state machine) |
| LLM | AWS Bedrock (Claude / Titan) |
| Frontend | React (Vite), Axios |
| Schemas | Pydantic v2 |

---

## 📝 License

MIT

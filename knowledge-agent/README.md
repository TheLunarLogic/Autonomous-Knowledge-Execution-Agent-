# Autonomous Knowledge Execution Agent

> A full-stack AI agent application that autonomously reasons over organizational knowledge, decides on appropriate actions, and requires human-in-the-loop approval for critical operations.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green.svg)
![React](https://img.shields.io/badge/React-18.x-blue.svg)

## 📖 Overview

The **Autonomous Knowledge Execution Agent** is an advanced AI system built with LangGraph and AWS Bedrock. Unlike simple chatbots, this agent processes a user's natural language request by querying internal databases, evaluating the context, and independently deciding what action to take. 

If the agent decides a critical action is required (e.g., flagging a security issue), it safely pauses execution and requests **human approval**, combining the speed of autonomous AI with the safety of human oversight.

### 🌟 Key Features

- **Semantic Knowledge Retrieval**: Integrates ChromaDB for vector-based semantic search alongside PostgreSQL for structured relational data.
- **Autonomous Reasoning (LangGraph)**: Implements a structured directed graph pipeline:
  1. `Retrieve`: Fetches relevant knowledge base items.
  2. `Reason`: Synthesizes retrieved data against the user query.
  3. `Decide`: Picks the most optimal business action (`answer_question`, `generate_report`, `flag_issue`, or `no_action`).
  4. `Execute`: Runs the action logic.
  5. `Explain`: Returns a human-readable explanation of why the decision was made.
- **Human-in-the-Loop Security**: Critical actions (like `flag_issue`) are blocked automatically until explicitly approved via the API.
- **Complete Audit Trail**: Every query, reasoning step, chosen action, and execution result is logged persistently in PostgreSQL for compliance and observability.

---

## 🏗️ Architecture

- **Frontend**: Built with **Next.js** and **React**, styled with **Tailwind CSS**. Provides a clean chat-like interface to view the agent's thought process and approve blocked actions.
- **Backend**: High-performance asynchronous API powered by **FastAPI**.
- **LLM Engine**: Powered by AWS Bedrock (`deepseek.v3.2` / `amazon.titan-embed-text-v2:0`) via `langchain_aws` using the modern Converse API format.
- **Databases**: 
  - **PostgreSQL (via SQLAlchemy/Alembic)**: Stores knowledge base metadata, categories, and audit logs.
  - **ChromaDB**: Local vector store for document embeddings.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL server running locally
- AWS Account with Bedrock model access

### 1. Backend Setup

1. **Clone and Setup Environment**
   ```bash
   git clone <your-repo-url>
   cd knowledge-agent/backend
   conda create -n knowledge-agent python=3.10
   conda activate knowledge-agent
   pip install -r requirements.txt
   ```

2. **Configure Environment Variables**
   Create a `.env` file in the `backend/` directory:
   ```env
   # Database
   DATABASE_URL=postgresql+asyncpg://postgres:yourpassword@localhost:5432/knowledge_db

   # AWS Bedrock
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   AWS_REGION=us-east-1
   BEDROCK_MODEL_ID=deepseek.v3.2
   ```

3. **Database Migrations**
   Initialize the PostgreSQL schema:
   ```bash
   alembic upgrade head
   ```

4. **Start the API Server**
   ```bash
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```
   *The API documentation will be available at `http://127.0.0.1:8000/docs`.*

### 2. Frontend Setup

1. **Navigate to the Frontend Directory**
   ```bash
   cd ../frontend
   ```

2. **Install Dependencies**
   ```bash
   npm install
   ```

3. **Start the Development Server**
   ```bash
   npm run dev
   ```
   *The application will be available at `http://localhost:3000`.*

---

## 🧪 Testing the Agent

You can test the agent's reasoning capabilities directly via the API. 
A helper script `test_queries.py` is included in the backend directory.

Run the tests:
```bash
python test_queries.py
```

**Example Output:**
```text
Q: Flag a security issue for James Wilson.
Action: flag_issue
Explanation: I chose to flag a security issue for James Wilson because your request was clear...
Requires Approval: True
```

---

## 🛠️ Project Structure

```text
knowledge-agent/
├── backend/
│   ├── alembic/              # Database migration scripts
│   ├── app/
│   │   ├── agent/            # LangGraph nodes and execution logic
│   │   ├── api/              # FastAPI endpoints (/ask, /load-knowledge)
│   │   ├── core/             # Configuration and logging
│   │   ├── db/               # SQLAlchemy session and models
│   │   ├── knowledge/        # ChromaDB setup and data loaders
│   │   └── schemas/          # Pydantic validation models
│   └── test_queries.py       # API test script
├── frontend/
│   ├── src/                  # Next.js React application
│   └── package.json
└── README.md
```

## 📄 License
This project is licensed under the MIT License.

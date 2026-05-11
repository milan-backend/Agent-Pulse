# Agent-Pulse

Agent-Pulse is an AI runtime orchestration, observability, and governance platform designed to monitor, control, and manage autonomous AI workflows in real time.

The platform provides durable task execution, live runtime telemetry, mission tracking, governance controls, retry orchestration, and distributed background execution using FastAPI, Celery, Redis, PostgreSQL, WebSockets, and Docker.

Agent-Pulse focuses on solving one of the biggest problems in modern AI systems:

> Running AI agents reliably, safely, and observably at scale.

---

# 🚀 Core Capabilities

## Runtime Observability
- Live mission monitoring
- Real-time execution dashboards
- WebSocket-based updates
- Step lifecycle tracking
- Pending / Running / Completed / Failed status visibility
- Runtime analytics and telemetry
- Mission execution summaries
- Agent activity monitoring

---

## AI Workflow Orchestration
- Durable background task execution
- Celery-based distributed workers
- Redis-backed task queue architecture
- Mission and step orchestration
- Concurrent workflow execution
- Retry orchestration system
- Queue-driven execution model
- Worker lifecycle management

---

## Governance & Runtime Control
- Kill switch for active agents
- Resume execution controls
- Runtime safeguard enforcement
- Dynamic max-step limits
- Retry limits
- Cost governance controls
- Repeated task detection
- Infinite-loop protection
- Runtime execution guards

---

## AI Runtime Analytics
- Token usage tracking
- Runtime cost monitoring
- Mission statistics
- Completion analytics
- Failure analytics
- Retry metrics
- Step execution metrics
- Worker execution visibility

---

## Durable Execution Architecture
- PostgreSQL-backed persistent execution state
- Mission durability
- Step durability
- Execution recovery architecture
- Async execution pipeline
- Distributed worker coordination
- Background processing infrastructure

---

# 🧠 Why Agent-Pulse Exists

Modern AI agents are powerful, but most systems fail to provide:

- Runtime visibility
- Governance controls
- Durable execution
- Execution tracing
- Real-time observability
- Safe orchestration
- Cost monitoring
- Failure recovery

Agent-Pulse is built to solve these problems by combining orchestration, observability, and governance into a unified AI runtime platform.

---

# 🏗️ System Architecture

```text
User Request
      ↓
FastAPI API Layer
      ↓
Execution Guard Layer
      ↓
Redis Queue
      ↓
Celery Workers
      ↓
Mission / Step Execution
      ↓
PostgreSQL Durable State
      ↓
WebSocket Live Dashboard
```

---

# 🛠️ Tech Stack

## Backend
- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL
- Celery
- Redis
- Python

---

## Frontend
- Next.js
- TypeScript
- Tailwind CSS

---

## Infrastructure
- Docker
- Docker Compose
- WebSockets
- Async Workers

---

# 📂 Project Structure

```bash
Agent-Pulse/
│
├── app/                    # Backend application
├── alembic/                # Database migrations
├── frontend/               # Next.js frontend
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

# ⚙️ Environment Variables

Create a `.env` file in the root directory.

Example:

```env
DATABASE_URL=your_database_url
DEBUG=True
SECRET_KEY=your_secret_key
ALGORITHM=HS256
OPENAI_API_KEY=your_openai_api_key
REDIS_URL=your_redis_url
```

---

# 🐳 Running with Docker

Start all services:

```bash
docker compose up --build
```

Stop services:

```bash
docker compose down
```

---

# 💻 Local Development

## Backend

Install dependencies:

```bash
pip install -r requirements.txt
```

Run FastAPI server:

```bash
uvicorn app.main:app --reload
```

---

## Frontend

Move to frontend folder:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start development server:

```bash
npm run dev
```

---

# 🧱 Database Migration

Run Alembic migrations:

```bash
alembic upgrade head
```

---

# 🌐 Application URLs

Frontend:
```bash
http://localhost:3000
```

Backend:
```bash
http://localhost:8000
```

API Docs:
```bash
http://localhost:8000/docs
```

---

# 📊 Runtime Features

## Mission Management
- Mission creation
- Mission tracking
- Mission execution monitoring
- Mission analytics

---

## Step Execution Engine
- Async step processing
- Durable execution pipeline
- Worker execution monitoring
- Concurrent execution support

---

## Runtime Governance
- Agent stop controls
- Resume controls
- Runtime guardrails
- Step limits
- Retry protection
- Cost protection

---

## Observability Dashboard
- Live updates
- Real-time metrics
- Mission telemetry
- Runtime summaries
- Worker execution visibility

---

# 🔬 Load Testing & Scalability

The platform has been tested using concurrent execution and load-testing workflows to validate:

- Worker orchestration
- Queue durability
- Retry behavior
- Runtime safeguards
- Governance controls
- WebSocket updates
- Mission execution stability

---

# 📌 Future Roadmap

- Multi-agent coordination
- Advanced workflow graphs
- Agent memory systems
- AI runtime tracing
- Distributed scaling
- Production telemetry pipelines
- Kubernetes deployment
- Advanced observability tooling

---

# 👨‍💻 Author

Milan Charan
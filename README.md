# Agent-Pulse

Agent-Pulse is an AI runtime orchestration, observability, governance, and execution-control platform designed for modern autonomous AI systems.

The platform provides durable task execution, distributed orchestration, runtime telemetry, mission tracing, governance enforcement, agent management, RBAC-based workspace collaboration, budget controls, execution analytics, and real-time operational visibility.

Built using FastAPI, Celery, Redis, PostgreSQL, WebSockets, Docker, and Next.js, Agent-Pulse focuses on solving one of the biggest operational challenges in modern AI systems:
Running AI agents reliably, observably, controllably, and safely at scale.

## 🚀 Platform Highlights

*   Multi-tenant workspace architecture
*   AI runtime orchestration
*   Durable execution pipelines
*   Real-time observability
*   Agent lifecycle management
*   Role-Based Access Control (RBAC)
*   Runtime governance & safety controls
*   Distributed worker execution
*   Mission tracing & analytics
*   Budget-aware AI execution
*   Live WebSocket telemetry
*   Retry-safe execution architecture
*   Idempotent durable workflows
*   ✅ BYOK (OpenAI & Gemini)
*   ✅ RAG Knowledge Infrastructure
*   ✅ ChromaDB Vector Search
*   ✅ Workspace API Provider Management
*   ✅ Agent-Specific Provider Overrides
*   ✅ Document Encryption
*   ✅ Retrieval Telemetry & Explainability

## 🧠 Why Agent-Pulse Exists

Modern AI systems are becoming increasingly autonomous, distributed, and operationally complex.
However, most AI workflows still lack:

*   Runtime visibility
*   Durable execution
*   Governance controls
*   Execution tracing
*   Failure recovery
*   Cost monitoring
*   Multi-agent management
*   Runtime analytics
*   Safe orchestration
*   Real-time observability
*   Workspace collaboration
*   Runtime control systems

Agent-Pulse is designed to unify: **observability**, **orchestration**, **governance**, **analytics**, **durable execution**, and **runtime control** into a single operational AI runtime platform.

---

## 🏢 Multi-Tenant Workspace Architecture

Agent-Pulse now supports a fully workspace-based SaaS architecture. Every agent, mission, runtime event, task, usage metric, and governance operation is securely isolated per workspace.

### Workspace Features
*   Workspace-based tenant isolation
*   Organization-style collaboration model
*   Workspace membership system
*   Workspace-aware APIs
*   Secure workspace validation
*   Workspace-scoped runtime telemetry
*   Workspace-specific analytics
*   Multi-organization support

---

## 🔐 Role-Based Access Control (RBAC)

Agent-Pulse includes backend-enforced RBAC infrastructure.

### Roles

*   **Admin**
    *   Full platform access
    *   Agent creation
    *   Budget controls
    *   API key regeneration
    *   Runtime governance access
    *   Workspace member management
*   **Operator**
    *   Operational runtime controls
    *   Kill/resume permissions
    *   Mission visibility
    *   Runtime monitoring
*   **Viewer**
    *   Read-only access
    *   Runtime observability
    *   Analytics visibility
    *   Mission tracking

### Security Enforcement
*   Backend role enforcement
*   Workspace membership validation
*   Protected runtime operations
*   Permission-aware execution control
*   Secure authorization layers

---

## 🤖 Agent Management System

Agent-Pulse includes a complete agent lifecycle management system.

### Agents Dashboard
*   Real-time agent overview
*   Workspace-scoped agents
*   Responsive agents UI
*   Agent runtime summaries
*   Agent operational statistics
*   Runtime state visibility

### Create Agent System
*   Secure agent creation flow
*   Runtime configuration support
*   API key generation
*   One-time API key visibility
*   Copy API key functionality
*   Workspace-bound agents
*   Role-protected creation access

---

## 📄 Agent Detail Dashboard

Each agent includes a dedicated operational dashboard.

### Per-Agent Features
*   Runtime details
*   Agent metadata
*   Agent status visibility
*   Mission tracking
*   Usage monitoring
*   Budget controls
*   API key regeneration
*   Kill/resume controls
*   Task visibility
*   Runtime analytics
*   Execution telemetry

---

## 🔑 Bring Your Own Key (BYOK)

Agent-Pulse supports Bring Your Own Key (BYOK) infrastructure, allowing organizations to connect their own AI providers and control model usage directly.

### Supported Providers
*   OpenAI
*   Gemini

### Provider Capabilities
*   Workspace-level provider management
*   Agent-specific provider assignment
*   Multiple provider configurations
*   Model selection support
*   Secure API key storage
*   Provider usage tracking
*   Provider source visibility

### Provider Resolution Order
1.  **Agent-Specific Provider Override** (Highest Priority)
2.  **Workspace Assigned Provider**
3.  **Workspace Default Provider**
4.  **Agent-Pulse Free Tier / System Provider** (Fallback Ground)

This architecture enables flexible AI infrastructure management across teams and organizations while tracking execution paths natively.

---

## 🧠 Knowledge & RAG Infrastructure

Agent-Pulse includes a Retrieval-Augmented Generation (RAG) system that allows agents to retrieve and utilize organization-specific knowledge blocks.

### Supported Documents
*   **PDF** (`.pdf`)
*   **TXT** (`.txt`)

### Knowledge Features
*   Document upload pipeline
*   Automatic chunking
*   Semantic indexing
*   Knowledge retrieval synthesis
*   Source attribution
*   Workspace-isolated knowledge boundaries
*   Agent-aware retrieval filtering
*   Metadata tracking

The platform enables agents to answer using company-specific information rather than relying solely on model training data.

---

## 🔎 ChromaDB Vector Infrastructure

Agent-Pulse integrates ChromaDB for semantic retrieval, low-latency embedding indexing, and contextual knowledge search.

### Capabilities
*   Vector embeddings calculation
*   Semantic similarity search
*   Workspace-scoped collections separation
*   Retrieval optimization metrics
*   Metadata indexing
*   Source tracing provenance
*   Context window payload generation

### Stored Metadata
*   `workspace_id`
*   `document_id`
*   `source_file`
*   `upload_timestamp`
*   `page_number`
*   `retrieval_similarity_confidence`

---

## 🔐 Knowledge Security & Encryption

Knowledge security and multi-tenant data isolation are treated as first-class, zero-trust platform concerns inside Agent-Pulse.

### Document Security Features
*   Encrypted document block storage
*   Secure stream upload verification pipeline
*   Workspace-aware encryption layers
*   Protected context retrieval workflows
*   Secure document lifecycle persistence

### Security Architecture Goals
*   Total multi-tenant workspace isolation
*   Knowledge extraction leak protection
*   Controlled retrieval access controls
*   Secure document lifecycle and destruction

---

## 📊 Retrieval Telemetry & Explainability

Agent-Pulse provides real-time visibility into exactly how retrieved corporate knowledge influences final LLM step outputs.

### Retrieval Telemetry Includes
*   Raw retrieval user search query
*   Ordered matched document chunks
*   Similarity distance confidence scores
*   Pure search latency times (in milliseconds)
*   Source file tracking provenance
*   Document contribution indicator tracking
*   Retrieval hit/miss metrics matching
*   Knowledge context footprint visibility

This allows engineering operators to understand exactly why an answer was generated and which specific document chunks influenced the final execution response.

---

## 🏢 Workspace Provider Management

Organizations can centrally manage AI engine nodes through workspace-level credential configurations.

### Workspace Provider Features
*   Multiple parallel provider configurations
*   Custom workspace provider naming profiles
*   Agent-to-provider routing assignment allocations
*   Shared team infrastructure access pools
*   Default fallback workspace keys
*   Centralized AI expense governance

### Configuration Profiles Examples
*   `OpenAI Production - Central Team`
*   `OpenAI Backup - Token Guard`
*   `Gemini Research - Tier 1 Labs`
*   `Gemini Team - Free Sandbox Dev`

This architecture supports enterprise-scale AI operations without duplicating API key management variables across local environments.

---

## 🤖 Agent-Specific Provider Overrides

Agent-Pulse allows specialized performance agents to clean override workspace-level providers when dedicated tokens or isolated billing scopes are mandatory.

### Agent Provider Features
*   Dedicated agent-specific API keys
*   Dedicated fine-tuned models selection
*   Agent-level custom model routing paths
*   Provider access containment boundaries
*   Custom isolated AI cost tracking tracking

This enables advanced agent-level infrastructure customization while maintaining overall centralized organizational governance.

---

## ⚙️ AI Workflow Orchestration

Agent-Pulse provides durable distributed orchestration infrastructure.

### Execution Features
*   Durable background execution
*   Celery distributed workers
*   Redis-backed execution queues
*   Concurrent workflow execution
*   Async execution pipelines
*   Queue-driven orchestration
*   Worker lifecycle coordination
*   Retry-safe execution model
*   Durable step tracking
*   Distributed task execution

---

## 🧱 Durable Execution System

The platform includes a durable runtime execution architecture.

### Durable Runtime Features
*   Idempotent execution support
*   Duplicate request prevention
*   Cached execution reuse
*   Durable step persistence
*   Persistent mission state
*   PostgreSQL-backed runtime state
*   Execution replay-ready design
*   Failure recovery architecture
*   Runtime state synchronization

---

## 🛡️ Runtime Governance & Controls

Agent-Pulse includes runtime governance systems for operational AI safety.

### Governance Features
*   Kill running agents
*   Resume paused agents
*   Runtime safeguard enforcement
*   Dynamic retry controls
*   Infinite-loop protection
*   Repeated task detection
*   Runtime execution guards
*   Mission execution protection
*   Safe execution boundaries
*   Runtime control enforcement
*   Failure containment architecture

---

## 💰 Budget Control System

Per-agent runtime budget management is built directly into the platform.

### Budget Features
*   Runtime budget limits
*   Agent-level budget control
*   Usage restriction controls
*   Runtime spend visibility
*   AI usage monitoring
*   Operational cost awareness

---

## 📋 Mission Runtime Infrastructure

Mission orchestration is a core operational layer inside Agent-Pulse.

### Mission Features
*   Mission execution engine
*   Step orchestration
*   Mission lifecycle tracking
*   Runtime mission visibility
*   Durable mission execution
*   Mission state persistence
*   Mission telemetry collection
*   Retry-aware execution tracking

---

## 🧩 Task Management System

Each agent contains task-level runtime visibility.

### Task Features
*   Agent-specific task dashboard
*   Runtime task monitoring
*   Task execution tracking
*   Input/output visibility
*   Runtime timestamps
*   Success/failure visibility
*   Mission-linked task tracing
*   Execution lifecycle tracking

---

## 📡 Real-Time Runtime Infrastructure

Agent-Pulse includes real-time runtime synchronization using WebSockets.

### Real-Time Features
*   WebSocket connectivity
*   Heartbeat monitoring
*   Live runtime updates
*   Real-time dashboard synchronization
*   Runtime activity feeds
*   Live mission telemetry
*   Runtime event streaming

---

## 📊 Usage & Analytics System

The platform provides workspace-wide and agent-specific analytics.

### Analytics Features
*   Usage event logging
*   Cache-hit tracking
*   Runtime analytics
*   Agent activity monitoring
*   Mission analytics
*   Token usage tracking
*   Runtime cost monitoring
*   Execution metrics
*   Retry analytics
*   Failure analytics
*   Runtime telemetry aggregation
*   Throughput tracking

---

## 🔭 Runtime Observability

Agent-Pulse provides operational observability for AI systems.

### Observability Features
*   Real-time mission monitoring
*   Live execution telemetry
*   Mission lifecycle tracking
*   Runtime execution visibility
*   Worker activity monitoring
*   Execution timelines
*   Runtime event monitoring
*   Agent telemetry systems
*   Distributed runtime analytics

---

## 🏗️ System Architecture

```text
User Request
      ↓
FastAPI API Layer
      ↓
Execution Guard Layer
      ↓
Workspace / RBAC Validation
      ↓
Redis Queue
      ↓
Celery Distributed Workers
      ↓
Mission / Step Execution
      ↓
PostgreSQL Durable State
      ↓
WebSocket Live Dashboard
🔄 Runtime Execution Flow
Plaintext
Mission Created
      ↓
Workspace Validation
      ↓
Execution Policies Applied
      ↓
Mission Queued
      ↓
Worker Picks Task
      ↓
Step Execution Starts
      ↓
Telemetry Generated
      ↓
Mission State Persisted
      ↓
Dashboard Updated Live
      ↓
Governance Rules Applied
      ↓
Mission Completed / Failed
🛠️ Tech Stack
Backend
FastAPI

Python

SQLAlchemy

Alembic

PostgreSQL

ChromaDB

Celery

Redis

WebSockets

Frontend
Next.js App Router

TypeScript

Tailwind CSS

Recharts

Infrastructure
Docker

Docker Compose

Async Workers

Distributed Queue System

Vercel Deployment

Render Deployment

🔐 Security Features
Workspace isolation boundaries

Cryptographic document encryption (AES)

Backend RBAC enforcement matrices

Workspace membership access token validation

API key one-way cryptographic hashing

Key rotation and regeneration infrastructure

Permission-protected runtime emergency kill switches

Workspace-scoped authentication workflows

🧪 Engineering Concepts Used
Distributed task orchestration

Durable workflow execution architectures

Runtime governance containment models

Retry-safe transactional execution loops

Real-time state machine streaming logs

Queue-based load balancing and execution

Asynchronous multi-model API execution pipelines

AI runtime trace telemetry graphs

Multi-tenant SaaS workspace cryptographic isolation

Hierarchical credential resolution pipelines

📂 Project Structure
Plaintext
Agent-Pulse/
│
├── app/                     # Backend application code modules
│   ├── core/                # Encryption, auth, and security guards
│   ├── models/              # Database models (PostgreSQL, User API keys)
│   ├── services/            # Core business engines (LLM, RAG, Tokenizer)
│   └── tasks/               # Background Celery event execution workers
│
├── alembic/                 # Database schema migrations versions
├── frontend/                # Next.js App Router UI dashboard app
├── docker-compose.yml       # Production/Local service orchestration
├── Dockerfile               # Container build recipes
├── requirements.txt         # Python server package allocations
├── .env.example             # Shell configuration properties mapping template
├── .gitignore               # Build footprint bypass array matching rules
└── README.md                # System documentation
⚙️ Environment Variables
Create a .env file in the root directory matching this template layout:

Code snippet
DATABASE_URL=your_database_url
REDIS_URL=your_redis_url
SECRET_KEY=your_secret_key
ALGORITHM=HS256
OPENAI_API_KEY=your_openai_api_key
GEMINI_API_KEY=your_gemini_api_key
CHROMA_HOST=your_chroma_http_host
CHROMA_TOKEN=your_chroma_auth_bearer_token
DEBUG=True
🐳 Running with Docker
Start all services using Docker Compose:

Bash
docker compose up --build
Stop background container cluster infrastructure:

Bash
docker compose down
💻 Local Development
Backend Setup
Install active development python package assignments:

Bash
pip install -r requirements.txt
Launch the local high-throughput FastAPI server execution lifecycle loop:

Bash
uvicorn app.main:app --reload
Frontend Dashboard Setup
Navigate into your Next.js application directory scope:

Bash
cd frontend
Install node package elements:

Bash
npm install
Boot your local dev compile observer system:

Bash
npm run dev
🧱 Database Migration
Execute Alembic tracking updates to bring your PostgreSQL schemas up to date:

Bash
alembic upgrade head
🌐 Application URLs
Frontend Dashboard UI: http://localhost:3000

Backend Server Root Engine: http://localhost:8000

Auto-Generated Interactive OpenAPI Docs: http://localhost:8000/docs

🚀 Production Infrastructure
Frontend Layer
Next.js App Router (React)

Responsive client dashboard panels layout

Workspace-aware global execution hooks

Vercel edge build optimization deployment

Backend Core Layer
FastAPI modular application routing architecture

PostgreSQL production durability database

ChromaDB cloud container semantic vectors store

Redis ephemeral messaging system / caching stack

Celery microservices distributed system background queue loops

Render server deployment infrastructure

🧑‍💻 Developer Experience
Modular context API route endpoints structure

Strictly typed frontend interfaces matching backend output schemas

Reusable structural service modules (RAG, Cryptography, Tokenizer)

Isolated workspace lookup validation patterns

Clean durable execution model step abstractions

🚧 Future Roadmap
Multi-agent graph cluster coordination frameworks

Persistent long-term cognitive agent memory networks

Advanced cross-step execution tool routing graphs

MCP-compatible tool execution endpoints

High-availability Kubernetes pod infrastructure deployment blueprints

Real-time AI behavioral anomaly detection guards

Granular micro-step sub-latency analytics tools

Screenshots
Dashboard Overview
Central runtime dashboard with live telemetry, execution monitoring and infrastructure health.

Mission Runtime
Track autonomous AI mission execution in real time with mission lifecycle telemetry.

Runtime Analytics
Execution analytics, runtime feeds and live observability for AI agents.

Runtime Usage Logs
Detailed token usage, completion metrics and execution cost monitoring.

Workspace Management
Manage team members, runtime roles and collaborative AI infrastructure.

Agent Infrastructure
Create and manage autonomous runtime agents with operational controls.

Dashboard Settings
Global runtime controls, API gateway management and infrastructure operations.

Agent Summary
Detailed agent runtime overview including missions, retries, execution state and cost telemetry.

Agent Settings
Configure API security, execution budgets, runtime limits and governance policies.

Agent Task Details
Inspect execution logs, cache states, input/output payloads and runtime task telemetry.

👨‍💻 Author
Milan Charan

📄 License
All Rights Reserved.
This project is currently proprietary and not licensed for redistribution or commercial reuse.
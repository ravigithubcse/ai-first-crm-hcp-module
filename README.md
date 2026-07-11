<div align="center">

# 🏥 AI-FIRST CRM — HCP MODULE

**Conversational, AI-Powered CRM for Pharmaceutical Field Reps & Healthcare Professional Interactions**

[![Python 3.10+](https://img.shields.io/badge/Python_3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React 19](https://img.shields.io/badge/React_19-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)](https://langchain-ai.github.io/langgraph/)
[![Groq](https://img.shields.io/badge/Groq-F55036?style=for-the-badge&logo=groq&logoColor=white)](https://groq.com/)

> A full-stack CRM that lets pharmaceutical field reps log, manage, and analyze
> Healthcare Professional (HCP) interactions — through a structured form **or**
> a natural-language AI chat interface. The AI agent is built with **LangGraph**
> and orchestrates 5 specialized tools (log, edit, view history, generate
> report, schedule follow-up) on top of **Groq's** `gemma2-9b-it` model.

[![View Repo](https://img.shields.io/badge/View%20Repo-1565C0?style=for-the-badge&logo=github&logoColor=white)](https://github.com/ravigithubcse/ai-first-crm-hcp-module)

</div>

---

## 🏗️ Architecture

```mermaid
flowchart LR
    FE["🌐 React 19 + TypeScript SPA
    Structured Form · AI Chat
    Dashboard · HCP Mgmt"]

    API["⚙️ FastAPI Backend  :8000
    REST Routes
    SQLAlchemy · Pydantic"]

    AGENT["🤖 LangGraph Agent
    5 Specialized Tools"]

    LLM["🧠 Groq LLM API
    gemma2-9b-it"]

    DB["🐘 PostgreSQL
    hcp_crm"]

    FE -->|Axios HTTP| API
    API -->|Invokes| AGENT
    AGENT -->|Prompts| LLM
    API <-->|SQLAlchemy ORM| DB

    classDef fe   fill:#0d47a1,stroke:#42a5f5,color:#e3f2fd
    classDef svc  fill:#1b5e20,stroke:#66bb6a,color:#e8f5e9
    classDef ai   fill:#4a148c,stroke:#ab47bc,color:#f3e5f5
    classDef db   fill:#3e2723,stroke:#ff8a65,color:#fbe9e7
    class FE fe
    class API svc
    class AGENT,LLM ai
    class DB db
```

**Request Flow:**
1. **React 19 + Redux Toolkit SPA** — structured interaction form, AI chat interface, dashboard, HCP management, follow-ups
2. Every request goes over **Axios** to the **FastAPI** backend (`:8000`)
3. **FastAPI** handles CRUD via **SQLAlchemy** models against **PostgreSQL**, validated with **Pydantic** schemas
4. AI-driven requests are routed to the **LangGraph agent**, which picks from 5 tools and calls the **Groq** LLM (`gemma2-9b-it`) for entity extraction, sentiment analysis, summarization, and report generation

---

## ✅ What Is Built

| Component | Status | Details |
|-----------|--------|---------|
| Structured Form Logging | ✅ Done | HCP selection, interaction type, date/time, attendees, topics, materials, samples, sentiment, outcomes, follow-ups |
| AI Chat Interface | ✅ Done | Natural-language interaction logging powered by Groq LLM |
| HCP Management | ✅ Done | Full CRUD with search & filtering |
| Interaction History | ✅ Done | Full history with AI-generated summaries, sentiment, and insights |
| Follow-up Scheduling | ✅ Done | AI-suggested follow-up actions with priority & due dates |
| Call Report Generation | ✅ Done | AI-generated structured reports from interaction data |
| LangGraph Agent — 5 Tools | ✅ Done | Log · Edit · View History · Generate Report · Schedule Follow-up |

## 🔮 What Is Planned

| Feature | Notes |
|---------|-------|
| Role-based access control | Multi-user auth for reps, managers, admins |
| Analytics dashboard | Team-level trend and sentiment rollups |
| Multi-LLM support | Pluggable providers beyond Groq |
| Mobile app | Field-rep companion app |

---

## 📁 Repository Layout

```
ai-first-crm-hcp-module/
├── app/                          # Frontend (React + TypeScript)
│   ├── src/
│   │   ├── components/           # UI components (incl. shadcn/ui)
│   │   ├── pages/                # Dashboard, HCPManagement, LogInteraction, Interactions, FollowUps
│   │   ├── services/              # Axios API layer
│   │   ├── store/                 # Redux Toolkit slices
│   │   └── types/                 # TypeScript definitions
│   ├── package.json
│   └── vite.config.ts
│
├── backend/                      # Backend (FastAPI)
│   ├── app/
│   │   ├── api/                   # hcp, interaction, follow_up, agent routes
│   │   ├── core/                  # config, database
│   │   ├── models/                # SQLAlchemy models
│   │   ├── schemas/                # Pydantic schemas
│   │   ├── services/               # Business logic
│   │   ├── langgraph_tools/        # LangGraph agent + 5 tools
│   │   └── main.py                 # FastAPI entry point
│   ├── requirements.txt
│   └── .env.example
│
└── README.md
```

---

## 📡 API Reference

**HCP Endpoints**

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/hcps` | Create a new HCP |
| GET | `/api/hcps` | List all HCPs (paginated) |
| GET | `/api/hcps/{id}` | Get HCP by ID |
| PUT | `/api/hcps/{id}` | Update HCP |
| DELETE | `/api/hcps/{id}` | Soft delete HCP |
| GET | `/api/hcps/search/by-name` | Search HCPs by name |

**Interaction Endpoints**

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/interactions` | Create interaction |
| GET | `/api/interactions` | List interactions |
| GET | `/api/interactions/{id}` | Get interaction by ID |
| PUT | `/api/interactions/{id}` | Update interaction |
| DELETE | `/api/interactions/{id}` | Delete interaction |
| POST | `/api/interactions/chat/log` | Log via AI chat |
| POST | `/api/interactions/reports/call` | Generate call report |

**Follow-up Endpoints**

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/follow-ups` | Create follow-up |
| GET | `/api/follow-ups` | List follow-ups |
| POST | `/api/follow-ups/{id}/complete` | Mark as completed |
| POST | `/api/follow-ups/schedule/ai` | AI schedule follow-up |

**AI Agent Endpoints**

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/agent/chat` | Chat with AI agent |
| POST | `/api/agent/tools/execute` | Execute a specific tool |
| GET | `/api/agent/tools` | List available tools |

---

## 🤖 LangGraph AI Agent Tools

### Role of the agent

The agent sits between the free-text chat box and the CRM's data layer. A
rep can either fill out the structured form on the left, or just describe
what happened in plain language on the right ("Met Dr. Sharma, discussed
OncoBoost Phase III efficacy, positive sentiment, left the brochure") --
both paths write to the same interaction record, and the two stay in sync:
logging or editing an interaction from chat auto-fills the structured form
in real time so the rep can review, correct, or add anything before saving.

Routing is genuinely LLM-driven, not keyword matching: all five tools below
are bound to a Groq-hosted model (`llama-3.3-70b-versatile`, chosen for
reliable tool-calling) via a standard LangGraph ReAct loop -- an `agent`
node reasons over the conversation and decides which tool to call and with
what arguments, a `tools` node executes it, and control loops back to the
agent to turn the result into a reply. Each tool then does its own
Groq call internally (`gemma2-9b-it`, the model this assignment specifies)
for the actual entity extraction, summarization, or insight generation --
so both mandated models are doing real work, at two different layers of
the same request.

| # | Tool | Description | Example |
|---|------|--------------|---------|
| 1 | **Log Interaction** | Extracts HCP name, topics, materials, sentiment, and summary from natural language; auto-creates HCP if not found | *"Met Dr. Smith today, discussed our new oncology drug, he seemed interested, left some samples"* |
| 2 | **Edit Interaction** | Modifies logged data via natural language or direct field updates | *"Change the sentiment to positive and add that he requested more literature"* |
| 3 | **View History** | Retrieves and analyzes historical interactions with AI insights | *"Show me all interactions with Dr. Johnson from last month"* |
| 4 | **Generate Report** | Creates a professional structured call report | *"Generate a detailed report for interaction 15"* |
| 5 | **Schedule Follow-up** | Plans follow-ups with AI-suggested timing, priority, and action type | *"Schedule a follow-up call with Dr. Williams next week"* |

---

## 🚀 Running Locally

### Prerequisites

- **Node.js** ≥ 18.x
- **Python** ≥ 3.10
- **PostgreSQL** ≥ 15 — either your own instance, or run `docker compose up -d` from the repo root to start one that matches `backend/.env.example` exactly (db `hcp_crm`, user/password `postgres`/`postgres`, port 5432)
- **Groq API Key** — get one free at [console.groq.com](https://console.groq.com/keys)

### Backend

```bash
docker compose up -d             # starts local Postgres (skip if you have your own)

cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env            # then paste your GROQ_API_KEY in

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

| Resource | URL |
|----------|-----|
| API | http://localhost:8000 |
| Swagger docs | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |

### Frontend

```bash
cd app
npm install
echo "VITE_API_URL=http://localhost:8000" > .env.local
npm run dev
```

Frontend runs at: **http://localhost:5173**

### Quick Start (Both Services)

```bash
# Terminal 1 - Backend
cd backend && source venv/bin/activate && uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd app && npm run dev
```

---

## ✅ Testing

```bash
cd backend
source venv/bin/activate
pytest -v
```

Covers HCP/Interaction/Follow-up CRUD end to end, the static agent tools
listing, and the LangGraph graph's structure (nodes wire up correctly, all
five tools register with valid schemas). These don't call the live Groq
API, so they pass with or without a real `GROQ_API_KEY` -- that keeps them
runnable in CI. Exercise the actual AI reasoning manually through the chat
panel once your key is in `backend/.env`.

---

## ⚙️ Environment Variables

**Backend (`backend/.env`)**

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:postgres@localhost:5432/hcp_crm` |
| `GROQ_API_KEY` | Groq API key for LLM access | *(required)* |
| `APP_NAME` | Application name | `AI-First CRM HCP Module` |
| `DEBUG` | Debug mode | `True` |
| `ALLOWED_ORIGINS` | CORS allowed origins | `http://localhost:5173,http://localhost:3000` |
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8000` |

**Frontend (`app/.env.local`)**

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API URL | `http://localhost:8000` |

---

## 🛠️ Tech Stack

| Layer | Technologies |
|-------|-------------|
| **Frontend** | React 19 · TypeScript 5.6 · Redux Toolkit · Tailwind CSS · shadcn/ui · Vite 7 · Axios |
| **Backend** | FastAPI · SQLAlchemy 2.0 · Pydantic 2.9 · Uvicorn |
| **Database** | PostgreSQL 15+ |
| **AI** | LangGraph · LangChain · Groq (`gemma2-9b-it`) |

---

## 👤 Author

<div align="center">

| | |
|---|---|
| **Name** | Ravi Kumar |
| **GitHub** | [github.com/ravigithubcse](https://github.com/ravigithubcse) |
| **Version** | 1.1.0 |
| **Date** | 2026-07-09 (v1.1.0: chat-to-form autofill, LLM-driven agent routing) |

[![GitHub](https://img.shields.io/badge/GitHub-1565C0?style=for-the-badge&logo=github&logoColor=white)](https://github.com/ravigithubcse/ai-first-crm-hcp-module)

*Built with care for pharmaceutical field representatives.*

</div>

---

## 📄 License

Copyright (c) 2026 Ravi Kumar. All rights reserved.
This project is proprietary software. Unauthorized copying, distribution, or use is strictly prohibited.

---

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) — Modern web framework
- [LangGraph](https://langchain-ai.github.io/langgraph/) — AI agent framework
- [Groq](https://groq.com/) — Ultra-fast LLM inference
- [shadcn/ui](https://ui.shadcn.com/) — UI components
- [Redux Toolkit](https://redux-toolkit.js.org/) — State management

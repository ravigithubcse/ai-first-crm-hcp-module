# AI-First CRM HCP Module

> A comprehensive, AI-powered Customer Relationship Management system specifically designed for Healthcare Professional (HCP) interactions in the life sciences industry.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
- [Environment Variables](#environment-variables)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [LangGraph AI Agent Tools](#langgraph-ai-agent-tools)
- [Project Structure](#project-structure)
- [Screenshots](#screenshots)
- [Author](#author)
- [License](#license)

---

## Overview

The **AI-First CRM HCP Module** is a full-stack application that empowers pharmaceutical field representatives to efficiently log, manage, and analyze their interactions with Healthcare Professionals (HCPs). The system features both a structured form interface and an AI-powered conversational chat interface for logging interactions.

The AI agent, built with **LangGraph**, orchestrates five specialized tools that help field reps:
- Log interactions via natural language
- View and analyze interaction history
- Generate structured call reports
- Schedule follow-up actions with AI suggestions
- Edit existing interaction records

---

## Features

### Core Features
- **Structured Form Logging**: Complete form with HCP selection, interaction type, date/time, attendees, topics, materials, samples, sentiment tracking, outcomes, and follow-up actions
- **AI Chat Interface**: Conversational interface powered by Groq LLM for natural language interaction logging
- **HCP Management**: Full CRUD for Healthcare Professionals with search and filtering
- **Interaction History**: Complete history with AI-generated summaries, sentiment analysis, and insights
- **Follow-up Scheduling**: AI-suggested follow-up actions with priority and due date management
- **Call Report Generation**: AI-generated structured call reports from interaction data

### AI Features
- **Natural Language Processing**: Extract entities, sentiment, and key points from conversation descriptions
- **Auto-summarization**: AI-generated summaries of interactions
- **Follow-up Suggestions**: Intelligent follow-up action recommendations
- **Sentiment Analysis**: Automatic sentiment detection (positive, neutral, negative)
- **Call Report Generation**: Professional structured reports for management

### UI Features
- **Responsive Design**: Works on desktop and mobile devices
- **Google Inter Font**: Clean, professional typography
- **Real-time Updates**: Redux state management with immediate UI updates
- **Toast Notifications**: Success/error feedback for all actions

---

## Tech Stack

### Frontend
| Technology | Version | Purpose |
|------------|---------|---------|
| React | 19.x | UI Framework |
| TypeScript | 5.6.x | Type Safety |
| Redux Toolkit | 2.6.x | State Management |
| Tailwind CSS | 3.4.x | Styling |
| shadcn/ui | latest | UI Components |
| Vite | 7.x | Build Tool |
| Axios | 1.8.x | HTTP Client |

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| FastAPI | 0.115.x | Web Framework |
| SQLAlchemy | 2.0.x | ORM |
| PostgreSQL | 15+ | Database |
| LangGraph | 0.2.x | AI Agent Framework |
| LangChain | 0.3.x | LLM Integration |
| Groq | 0.11.x | LLM API (gemma2-9b-it) |
| Pydantic | 2.9.x | Data Validation |
| Uvicorn | 0.32.x | ASGI Server |

---

## Architecture

```
+----------------------------------+        +----------------------------------+
|           Frontend               |        |           Backend               |
|  +----------------------------+  |        |  +----------------------------+  |
|  |  React + Redux Toolkit     |  |        |  |  FastAPI                   |  |
|  |  - Components              |  |        |  |  - REST API Routes         |  |
|  |  - Redux Store             |  |        |  |  - SQLAlchemy Models       |  |
|  |  - API Service Layer       |  |        |  |  - Pydantic Schemas        |  |
|  |  - Type Definitions        |  |        |  |  - Business Services       |  |
|  +----------------------------+  |        |  +----------------------------+  |
|              |                   |        |              |                   |
|         Axios HTTP               |        |      LangGraph Agent            |
|              |                   |        |              |                   |
+--------------|-------------------+        |  +------------------------+      |
               |                            |  |  5 AI Tools:           |      |
               v                            |  |  - Log Interaction     |      |
     +-------------------+                  |  |  - Edit Interaction    |      |
     |   Backend API     | <---------------+  |  |  - View History        |      |
     |   (FastAPI)       |                     |  |  - Generate Report     |      |
     +-------------------+                     |  |  - Schedule Follow-up  |      |
               |                              |  +------------------------+      |
               v                              |              |                   |
     +-------------------+                   |         Groq LLM API              |
     |   PostgreSQL      |                   |      (gemma2-9b-it)               |
     |   Database        |                   |                                   |
     +-------------------+                   +-----------------------------------+
```

---

## Prerequisites

- **Node.js** >= 18.x
- **Python** >= 3.10
- **PostgreSQL** >= 15
- **Groq API Key** (get one at [https://console.groq.com](https://console.groq.com))

---

## Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd ai-first-crm-hcp-module
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file and configure
cp .env.example .env
# Edit .env with your database URL and Groq API key
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd app

# Install dependencies
npm install

# Create environment file
echo "VITE_API_URL=http://localhost:8000" > .env.local
```

---

## Environment Variables

### Backend (.env)

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:postgres@localhost:5432/hcp_crm` |
| `GROQ_API_KEY` | Groq API key for LLM access | *(required)* |
| `APP_NAME` | Application name | `AI-First CRM HCP Module` |
| `DEBUG` | Debug mode | `True` |
| `ALLOWED_ORIGINS` | CORS allowed origins | `http://localhost:5173,http://localhost:3000` |
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8000` |

### Frontend (.env.local)

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API URL | `http://localhost:8000` |

---

## Running the Application

### Start the Backend

```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Start the FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or use:
python -m app.main
```

The API will be available at: `http://localhost:8000`
- Interactive API docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Start the Frontend

```bash
cd app

# Development mode
npm run dev

# Production build
npm run build
```

The frontend will be available at: `http://localhost:5173`

### Quick Start (Both Services)

```bash
# Terminal 1 - Backend
cd backend && source venv/bin/activate && uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd app && npm run dev
```

---

## API Documentation

### HCP Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/hcps` | Create a new HCP |
| `GET` | `/api/hcps` | List all HCPs (paginated) |
| `GET` | `/api/hcps/{id}` | Get HCP by ID |
| `PUT` | `/api/hcps/{id}` | Update HCP |
| `DELETE` | `/api/hcps/{id}` | Soft delete HCP |
| `GET` | `/api/hcps/search/by-name` | Search HCPs by name |

### Interaction Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/interactions` | Create interaction |
| `GET` | `/api/interactions` | List interactions |
| `GET` | `/api/interactions/{id}` | Get interaction by ID |
| `PUT` | `/api/interactions/{id}` | Update interaction |
| `DELETE` | `/api/interactions/{id}` | Delete interaction |
| `POST` | `/api/interactions/chat/log` | Log via AI chat |
| `POST` | `/api/interactions/reports/call` | Generate call report |

### Follow-up Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/follow-ups` | Create follow-up |
| `GET` | `/api/follow-ups` | List follow-ups |
| `POST` | `/api/follow-ups/{id}/complete` | Mark as completed |
| `POST` | `/api/follow-ups/schedule/ai` | AI schedule follow-up |

### AI Agent Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/agent/chat` | Chat with AI agent |
| `POST` | `/api/agent/tools/execute` | Execute specific tool |
| `GET` | `/api/agent/tools` | List available tools |

---

## LangGraph AI Agent Tools

The AI agent uses **LangGraph** to orchestrate 5 specialized tools:

### 1. Log Interaction
Captures interaction data from natural language input using LLM for:
- Entity extraction (HCP name, topics, materials)
- Sentiment analysis
- Summary generation
- Follow-up suggestions
- Auto-creates HCP if not found

**Example**: *"Met Dr. Smith today, discussed our new oncology drug, he seemed interested, left some samples"*

### 2. Edit Interaction
Allows modification of logged data via natural language or direct field updates.

**Example**: *"Change the sentiment to positive and add that he requested more literature"*

### 3. View Interaction History
Retrieves and analyzes historical interactions with AI-powered insights.

**Example**: *"Show me all interactions with Dr. Johnson from last month"*

### 4. Generate Call Report
Creates professional structured call reports from interaction data.

**Example**: *"Generate a detailed report for interaction 15"*

### 5. Schedule Follow-up
Plans follow-up actions with AI-suggested timing, priority, and action type.

**Example**: *"Schedule a follow-up call with Dr. Williams next week"*

---

## Project Structure

```
ai-first-crm-hcp-module/
├── app/                          # Frontend Application
│   ├── public/
│   ├── src/
│   │   ├── components/           # Reusable UI components
│   │   │   ├── ui/              # shadcn/ui components
│   │   │   └── Layout.tsx       # Main layout with sidebar
│   │   ├── pages/               # Page components
│   │   │   ├── Dashboard.tsx
│   │   │   ├── HCPManagement.tsx
│   │   │   ├── LogInteraction.tsx
│   │   │   ├── Interactions.tsx
│   │   │   └── FollowUps.tsx
│   │   ├── services/            # API service layer
│   │   │   └── api.ts
│   │   ├── store/               # Redux store
│   │   │   ├── index.ts
│   │   │   ├── hcpSlice.ts
│   │   │   ├── interactionSlice.ts
│   │   │   ├── chatSlice.ts
│   │   │   └── uiSlice.ts
│   │   ├── types/               # TypeScript definitions
│   │   │   └── index.ts
│   │   ├── App.tsx              # Root component
│   │   ├── main.tsx             # Entry point
│   │   └── index.css            # Global styles
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   └── tsconfig.json
│
├── backend/                      # Backend Application
│   ├── app/
│   │   ├── api/                 # API routes
│   │   │   ├── hcp_routes.py
│   │   │   ├── interaction_routes.py
│   │   │   ├── follow_up_routes.py
│   │   │   └── agent_routes.py
│   │   ├── core/                # Core configuration
│   │   │   ├── config.py
│   │   │   └── database.py
│   │   ├── models/              # SQLAlchemy models
│   │   │   ├── hcp.py
│   │   │   ├── interaction.py
│   │   │   └── follow_up.py
│   │   ├── schemas/             # Pydantic schemas
│   │   │   ├── hcp.py
│   │   │   ├── interaction.py
│   │   │   └── follow_up.py
│   │   ├── services/            # Business logic
│   │   │   ├── hcp_service.py
│   │   │   ├── interaction_service.py
│   │   │   └── follow_up_service.py
│   │   ├── langgraph_tools/     # LangGraph AI tools
│   │   │   ├── __init__.py
│   │   │   ├── agent.py
│   │   │   ├── llm_config.py
│   │   │   ├── log_interaction.py
│   │   │   ├── edit_interaction.py
│   │   │   ├── view_history.py
│   │   │   ├── generate_report.py
│   │   │   └── schedule_followup.py
│   │   └── main.py              # FastAPI entry point
│   ├── requirements.txt
│   └── .env.example
│
└── README.md
```

---

## Author

**Ravi Kumar**

- GitHub: [ravigithubcse](https://github.com/ravigithubcse)
- Date: 2026-07-09
- Version: 1.0.0

---

## License

Copyright (c) 2026 Ravi Kumar. All rights reserved.

This project is proprietary software. Unauthorized copying, distribution, or use is strictly prohibited.

---

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [LangGraph](https://langchain-ai.github.io/langgraph/) - AI agent framework
- [Groq](https://groq.com/) - Ultra-fast LLM inference
- [shadcn/ui](https://ui.shadcn.com/) - Beautiful UI components
- [Redux Toolkit](https://redux-toolkit.js.org/) - State management

---

*Built with care for pharmaceutical field representatives.*
# Interview Coach — Project Plan

> **Rule:** The `## Active Section` must be kept updated at all times.
> Update it whenever a task is started, completed, or the current focus changes.

---

## Active Section

**Current Week:** Week 1 — Backend Base
**Status:** In progress
**Focus:** OpenRouter integration (`POST /chat`)

**In Progress:**
- [ ] OpenRouter integration (`POST /chat`)

**Completed This Week:**
- [x] FastAPI project setup + folder structure
- [x] PostgreSQL models: `sessions`, `messages`, `documents`
- [x] Health check endpoint

**Blockers:**
- none

---

## The App

Upload your CV + paste a Job Description, and the agent runs a real interview, evaluates your answers, and gives you detailed feedback.

### Core Flow
```
CV + JD (uploaded)
      ↓
LangGraph: generate_question (using RAG context)
      ↓
User answers (streamed feedback)
      ↓
LangGraph: evaluate_answer → score + feedback
      ↓
continue? → next question OR final report
```

### Project Structure
```
interview-coach/
├── backend/          FastAPI + SQLite
├── langgraph/        Interview graph
├── mcp-server/       Agent tools
└── frontend/         React + TypeScript
```

### Tech Stack
| Layer | Technology |
|-------|-----------|
| LLM Provider | OpenRouter |
| RAG | sqlite-vec + OpenRouter embeddings |
| Agent Workflow | LangGraph |
| Agent Tools | MCP Server |
| Observability | Langfuse (local Docker) |
| Evaluation | LLM-as-judge via Langfuse |
| Backend | FastAPI + SQLAlchemy + SQLite |
| Frontend | React + TypeScript + Vite + TailwindCSS |
| Streaming | Server-Sent Events (SSE) |

---

## Roadmap

### Week 1 — Backend Base
**Goal:** Working API with OpenRouter and streaming

- [ ] FastAPI project setup + folder structure
- [ ] SQLite models: `sessions`, `messages`, `documents`
- [ ] OpenRouter integration (`POST /chat`)
- [ ] SSE streaming endpoint (`POST /chat/stream`)
- [ ] Basic health check and manual test

**Key concept:** How HTTP streaming works with Server-Sent Events.

#### Database Models

**`sessions`**
| Column | Type | Notes |
|--------|------|-------|
| id | int PK | |
| model | str | OpenRouter model used |
| status | enum | `in_progress` / `completed` |
| created_at | datetime TZ | |

**`messages`**
| Column | Type | Notes |
|--------|------|-------|
| id | int PK | |
| session_id | FK → sessions | |
| role | enum | `agent` / `user` |
| content | text | |
| created_at | datetime TZ | |

**`documents`**
| Column | Type | Notes |
|--------|------|-------|
| id | int PK | |
| session_id | FK → sessions | |
| type | enum | `cv` / `job_description` |
| content | text | |
| created_at | datetime TZ | |

Relationships: `session → messages` (1:N), `session → documents` (1:N). Cascade delete en ambas.

---

### Week 2 — Prompt Engineering + Langfuse
**Goal:** Model behaves like a real interviewer

- [ ] Interviewer system prompt (role, tone, style)
- [ ] Evaluator system prompt (scoring criteria)
- [ ] Prompt templates: generate question / evaluate answer
- [ ] Langfuse local setup (Docker)
- [ ] Instrument every LLM call: tokens, latency, prompt used

**Key concept:** How the same model changes completely with different prompts.

---

### Week 3 — RAG (supporting, not the star)
**Goal:** Questions are specific to YOUR CV and the real JD

- [ ] Parse CV (PDF → text) and JD (plain text)
- [ ] Simple chunking + embeddings via OpenRouter
- [ ] Store vectors in SQLite with `sqlite-vec`
- [ ] Retrieval: fetch relevant context before generating each question

**Key concept:** Why we chunk. Trade-off between chunk size and retrieval quality.

---

### Week 4 — LangGraph
**Goal:** The interview has logic, not just a chat loop

Nodes:
```
generate_question
      ↓
wait_for_answer
      ↓
evaluate_answer
      ↓
continue? ──yes──→ generate_question
    │
   no
    ↓
generate_final_report
```

- [ ] Basic LangGraph setup, first simple graph
- [ ] Implement all 4 nodes
- [ ] Conditional edge: max N questions configurable
- [ ] If answer is too short → prompt user to elaborate
- [ ] Final report with scores per category

**Key concept:** Difference between a linear chain and a graph with conditional logic.

---

### Week 5 — MCP Server
**Goal:** Agent has tools to access context intelligently

| Tool | What it does |
|------|-------------|
| `search_resume(query)` | Search within the CV |
| `search_jd(query)` | Search within the JD |
| `get_session_history()` | See which questions were already asked |

- [ ] MCP server setup (Python SDK)
- [ ] Implement the 3 tools
- [ ] Connect MCP tools to LangGraph as tool nodes

**Key concept:** MCP as an abstraction layer between the model and its tools.

---

### Week 6 — Frontend
**Goal:** Simple UI that feels like a real interview

Screens:
1. **Setup** — Upload CV + paste JD + choose model (OpenRouter)
2. **Interview** — Agent question, user answer, streaming feedback
3. **Report** — Final scores and breakdown

- [ ] Vite + React + TypeScript + TailwindCSS setup
- [ ] Setup screen with CV upload and JD input
- [ ] Interview screen with SSE streaming
- [ ] Report screen
- [ ] Model selector (OpenRouter models)

**Key concept:** How to consume streaming from a frontend with `fetch` + `ReadableStream`.

---

### Week 7 — LLM Evaluation
**Goal:** Measure if the system actually works well

- [ ] Create dataset: 10 questions with good and bad example answers
- [ ] Evaluator 1: `question_relevance` — is the question relevant to the role?
- [ ] Evaluator 2: `feedback_quality` — is the feedback useful and specific?
- [ ] Evaluator 3: `score_fairness` — does the score reflect the answer?
- [ ] Compare 2 OpenRouter models on the same answers
- [ ] View results in Langfuse dashboard

**Key concept:** LLM-as-judge — using one model to evaluate another.

---

### Week 8 — Final Integration
**Goal:** Everything connected, clean end-to-end flow

- [ ] Full flow: upload CV → complete interview → report → all traced in Langfuse
- [ ] Basic error handling in frontend and backend
- [ ] `.env` with all keys documented
- [ ] README with how to run each service
- [ ] Demo: complex question using RAG + LangGraph + MCP together

---

## Progress Tracker

| Week | Topic | Status |
|------|-------|--------|
| 1 | Backend Base | Not started |
| 2 | Prompt Engineering + Langfuse | Not started |
| 3 | RAG | Not started |
| 4 | LangGraph | Not started |
| 5 | MCP Server | Not started |
| 6 | Frontend | Not started |
| 7 | LLM Evaluation | Not started |
| 8 | Final Integration | Not started |

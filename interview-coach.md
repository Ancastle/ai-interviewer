# Interview Coach — Project Plan

> AI-powered mock interview app. Upload your CV and a job description, or select a study topic, and an LLM-powered agent conducts a structured technical interview, evaluates your answers in real time, and generates a detailed performance report.

---

## Active Section

**Current Week:** Week 6 — Done
**Status:** Paused / functional
**Focus:** App is working end-to-end. Both interview modes operational.

**Completed (Week 6):**
- [x] React + Vite frontend
- [x] Setup screen with mode toggle (CV+JD / Study Mode)
- [x] Chat screen with auto-scroll and Enter-to-send
- [x] Report screen with score bars
- [x] CORS enabled on backend
- [x] POST /session endpoint to create sessions from frontend

**Completed (Week 5):**
- [x] MCP server with FastMCP + stdio transport
- [x] Tools: search_resume, search_jd, get_session_history
- [x] GET /session/{id}/history endpoint
- [x] Tested via MCP Inspector

**Completed (Week 4):**
- [x] LangGraph setup + InterviewState
- [x] Nodes: generate_question, wait_for_answer, evaluate_answer, generate_final_report
- [x] Conditional edges + loop
- [x] Session endpoints: POST /session/start, POST /session/{id}/answer

**Completed (Week 3):**
- [x] Parse CV (PDF → text)
- [x] Chunking with overlap
- [x] Embeddings via OpenRouter
- [x] sqlite-vec vector store
- [x] Retrieval endpoint

**Completed (Week 2):**
- [x] Langfuse local setup (Docker)
- [x] Instrument LLM calls: tokens, latency, prompt used
- [x] Interviewer system prompt (categorized, conceptual questions)
- [x] Evaluator system prompt
- [x] Study mode prompt

**Completed (Week 1):**
- [x] FastAPI project setup + folder structure
- [x] PostgreSQL models: sessions, messages, documents
- [x] Health check endpoint
- [x] OpenRouter integration (POST /chat)
- [x] SSE streaming endpoint (POST /chat/stream)

**Extras (beyond original plan):**
- [x] Study Mode — select a subject and category from local study files, LangGraph uses the content as context instead of CV+JD
- [x] Improved interviewer prompt: 6 question categories, conceptual focus, no surface-level questions

**Blockers:**
- none

---

## The App

Two interview modes:

**CV + JD Mode:** Upload your CV (PDF) and paste a job description. The agent generates questions using RAG — it embeds each question and retrieves the most relevant chunks from your CV and the JD as context.

**Study Mode:** Select a subject (Evolve, React, Python) and a category. The agent asks questions strictly based on the study material for that category.

In both modes: the agent evaluates each answer, accumulates scores, and generates a final performance report.

### Core Flow
```
[Setup]
  CV + JD  ──→ POST /documents/cv + /documents/jd  ──→ embed + store in sqlite-vec
  Study    ──→ parse local .js study files                ──→ extract topics

[Interview — LangGraph]
  generate_question  (RAG from vectors OR study guide as context)
        ↓
  wait_for_answer    (interrupt — waits for HTTP POST)
        ↓
  evaluate_answer    (LLM-as-judge → scores: accuracy, depth, clarity, relevance)
        ↓
  should_continue?
        ├── more questions → generate_question
        └── done          → generate_final_report → END

[Report]
  Average scores + coach feedback paragraph
```

### Project Structure
```
interview-coach/
├── backend/
│   └── app/
│       ├── graph/          LangGraph nodes, state, graph definition
│       ├── models/         SQLAlchemy models (sessions, messages, documents)
│       ├── prompts/        Interviewer + evaluator + study mode prompts
│       ├── routers/        FastAPI routers (session, documents, study, chat)
│       └── services/       vector_store, openrouter, chunker, study_reader, langfuse
├── mcp-server/             FastMCP server — 3 tools over stdio transport
├── frontend/               React + Vite (Setup → Chat → Report)
└── docker-compose.yml      postgres, backend, frontend, langfuse
```

### Tech Stack
| Layer | Technology |
|-------|-----------|
| LLM Provider | OpenRouter (model configurable via config.py) |
| Embeddings | openai/text-embedding-3-small via OpenRouter |
| RAG | sqlite-vec (cosine distance) + chunking with overlap |
| Agent Workflow | LangGraph with MemorySaver |
| MCP Server | FastMCP — search_resume, search_jd, get_session_history |
| Observability | Langfuse (local Docker, port 3000) |
| Backend | FastAPI + SQLAlchemy + PostgreSQL |
| Frontend | React + Vite |
| Infrastructure | Docker Compose |

---

## Progress Tracker

| Week | Topic | Status |
|------|-------|--------|
| 1 | Backend Base | Done |
| 2 | Prompt Engineering + Langfuse | Done |
| 3 | RAG | Done |
| 4 | LangGraph | Done |
| 5 | MCP Server | Done |
| 6 | Frontend | Done |
| — | Study Mode (extra) | Done |
| 7 | LLM Evaluation | Not started |
| 8 | Final Integration | Not started |

---

## Roadmap (remaining)

### Week 7 — LLM Evaluation
**Goal:** Measure if the system actually works well

- [ ] Create dataset: questions with good and bad example answers
- [ ] Evaluator: question_relevance — is the question relevant to the role?
- [ ] Evaluator: feedback_quality — is the feedback useful and specific?
- [ ] Evaluator: score_fairness — does the score reflect the answer?
- [ ] Compare models on the same answers
- [ ] View results in Langfuse dashboard

**Key concept:** LLM-as-judge — using one model to evaluate another.

---

### Week 8 — Final Integration
**Goal:** Everything connected, clean end-to-end

- [ ] Full flow: upload CV → complete interview → report → all traced in Langfuse
- [ ] Error handling in frontend and backend
- [ ] .env with all keys documented
- [ ] Demo video or walkthrough

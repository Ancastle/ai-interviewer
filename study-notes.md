# Interview Coach — Cómo funciona end to end

## Stack

| Capa | Tecnología |
|---|---|
| Frontend | React + Vite |
| Backend | FastAPI + SQLAlchemy |
| Base de datos | PostgreSQL |
| Vectores | sqlite-vec (`/data/vectors.db`) |
| Agente | LangGraph (MemorySaver) |
| LLM | OpenRouter (nvidia/nemotron o cualquier modelo configurable) |
| Embeddings | `openai/text-embedding-3-small` via OpenRouter |
| Observabilidad | Langfuse |
| MCP Server | FastMCP + httpx |
| Infraestructura | Docker Compose |

---

## Flujo completo

### 1. El usuario sube CV y JD (Setup screen)

```
Usuario → POST /session          → crea fila en sessions (PostgreSQL) → devuelve session_id
Usuario → POST /documents/cv     → parse PDF → chunk text → embed chunks → guarda en sqlite-vec
Usuario → POST /documents/jd     → chunk text → embed chunks → guarda en sqlite-vec
```

Los chunks se guardan en dos tablas en `vectors.db`:
- `chunks(id, session_id, doc_type, chunk_idx, text)`
- `chunk_embeddings(chunk_id, embedding FLOAT[1536])`

`doc_type` es `"cv"` o `"job_description"`.

---

### 2. La entrevista inicia (POST /session/start)

El backend crea el estado inicial del grafo y llama a LangGraph:

```python
initial_state = {
    "session_id": 1,
    "model": "...",
    "max_questions": 5,
    "question_count": 0,
    "messages": [],
    "scores": [],
    ...
}
state = await interview_graph.ainvoke(initial_state, config)
```

LangGraph ejecuta el nodo `generate_question`:

1. Toma la query actual (o `"technical skills"` si es la primera)
2. Embebe la query → busca los top-3 chunks de CV más similares → busca los top-3 chunks de JD más similares
3. Construye el prompt del entrevistador con esos chunks como contexto
4. Llama al LLM → genera la primera pregunta
5. El grafo llega a `wait_for_answer` → se interrumpe (LangGraph `interrupt`)
6. El backend devuelve `{ done: false, question: "..." }` al frontend

---

### 3. El usuario responde (POST /session/{id}/answer)

```
Usuario → POST /session/1/answer { answer: "..." }
```

LangGraph resume desde donde estaba (`Command(resume=answer)`) y ejecuta `evaluate_answer`:

1. Toma la pregunta actual y la respuesta del usuario
2. Si la respuesta es muy corta (<20 chars) → pide elaborar, vuelve a `wait_for_answer`
3. Si no → llama al LLM con el prompt del evaluador
4. El evaluador devuelve JSON con scores: `{ scores: {accuracy, depth, clarity, relevance}, overall, feedback }`
5. El score se agrega al estado (`state["scores"]`)

Luego el edge condicional `should_continue` decide:
- `question_count >= max_questions` → va a `generate_final_report`
- Respuesta pedida de elaborar → vuelve a `wait_for_answer`
- Si no → vuelve a `generate_question` (siguiente pregunta)

Mientras no termine, devuelve `{ done: false, question: "..." }`.

---

### 4. El reporte final (generate_final_report)

Cuando se alcanza `max_questions`:

1. Calcula promedios de todos los scores acumulados
2. Llama al LLM con un prompt de coach → genera párrafo de feedback
3. Devuelve `{ done: true, report: "...", scores: [...] }`

El frontend detecta `done: true` → muestra la pantalla de reporte con barras de puntaje.

---

## El grafo de LangGraph

```
START
  ↓
generate_question   ← ←  ←  ← (loop si hay más preguntas)
  ↓                              ↑
wait_for_answer                  |
  ↓                              |
evaluate_answer                  |
  ↓                              |
should_continue ────────── "continue" ─────────────┘
  │
  └── "final_report" ──→ generate_final_report → END
```

`MemorySaver` persiste el estado del grafo entre llamadas HTTP usando `thread_id = session_id`.

---

## La búsqueda vectorial

Cuando `generate_question` necesita contexto:

```python
query_embedding = await embed([query])          # 1536 dimensiones
results = search(session_id, "cv", query_embedding, top_k=3)
```

La búsqueda en sqlite-vec usa distancia coseno:

```sql
SELECT c.text
FROM chunk_embeddings ce JOIN chunks c ON c.id = ce.chunk_id
WHERE c.session_id = ? AND c.doc_type = ?
ORDER BY vec_distance_cosine(ce.embedding, ?)
LIMIT 3
```

Los chunks más relevantes semánticamente se inyectan en el prompt del entrevistador. Esto es RAG (Retrieval-Augmented Generation).

---

## El MCP Server

Corre como proceso separado con stdio transport. Expone 3 tools a cualquier cliente MCP (Claude Desktop, Claude API tool_use, etc.):

| Tool | Qué hace |
|---|---|
| `search_resume(session_id, query, top_k)` | Llama `POST /documents/search` con `doc_type=cv` |
| `search_jd(session_id, query, top_k)` | Llama `POST /documents/search` con `doc_type=job_description` |
| `get_session_history(session_id)` | Llama `GET /session/{id}/history` |

Las tools no reimplementan la lógica — llaman al backend por HTTP. El backend hace el embedding de la query y ejecuta la búsqueda vectorial.

---

## Observabilidad (Langfuse)

Cada llamada al LLM genera un trace en Langfuse:
- La sesión de entrevista = un `trace`
- Cada nodo del grafo = un `span` dentro del trace
- Cada llamada al LLM = una `generation` con tokens de entrada/salida

Visible en `http://localhost:3000`.

---

## Conceptos clave aplicados

| Concepto | Dónde se usa |
|---|---|
| **RAG** | generate_question busca chunks relevantes antes de llamar al LLM |
| **Vector search** | sqlite-vec con distancia coseno sobre embeddings de 1536 dims |
| **Chunking con overlap** | Para no cortar contexto en los bordes de los chunks |
| **LangGraph interrupt** | Pausa el grafo entre preguntas para esperar input del usuario |
| **MemorySaver** | Persiste el estado del grafo en memoria entre requests HTTP |
| **MCP** | Protocolo estándar para exponer tools a agentes externos |
| **Langfuse** | Observabilidad de LLMs: traces, spans, generations, tokens |

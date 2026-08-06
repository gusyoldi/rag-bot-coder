# Architecture — PO Copilot

## Estado actual

Corazón RAG local con intención, retrieval, rerank y loop de confianza:

```
CLI → detect_trello
        ├─ yes → trello_agent (tools REST, máx. 5 turns) → END
        └─ no  → interpret_intent → retrieve (k=20) → rerank (top 5)
                 → generate → assess(confidence) → refine | fallback | END
```

| Componente | Estado |
|---|---|
| `domain/` | Hecho (`product-owner`) |
| `ingestion/` + `scripts/ingest_corpus.py` | Hecho |
| `retrieval/` (Chroma + Ollama embeddings) | Hecho |
| `ranking/` (cross-encoder MiniLM) | Hecho |
| `orchestration/` (prompts conceptual / case) | Hecho |
| `agent/` (LangGraph Plan B + Trello branch) | Hecho |
| `cli/` | Hecho (muestra intent + confidence) |
| `mcp/` Trello REST tools | Hecho |
| LangSmith / Arize Phoenix | Hecho (`src/observability/`, env-gated) |
| `docker-compose` / `k8s/` | Pendiente (placeholders) |

## Decisiones

- **Intent:** `conceptual` vs `case` vía LLM; cambia el prompt de generación y el refine.
- **Retrieve:** `k=20` con scores vectoriales; collection = `domain.id`.
- **Rerank:** `cross-encoder/ms-marco-MiniLM-L-6-v2` (lazy singleton; cold start en la 1ª query).
- **Confidence:** `max(rerank_score)` con umbrales en `src/agent/confidence.py`
  (`CONFIDENCE_OK=-10.0`, `CONFIDENCE_WEAK=-11.2`), calibrados porque el
  cross-encoder es anglocéntrico y el CLI habla español sobre corpus en inglés.
- **Assess:** OK → finish; débil → refine (máx. 3); muy débil tras 3 intentos → fallback.
- **Chroma embebido** en `CHROMA_PERSIST_DIR` (sin Docker en este slice).
- Referencias: CLASE 3 `modular_vectorial/` (grafo) + CLASE 6 `VECTORIAL_PDFS/retriever.py` (rerank).

## Observabilidad

`configure_observability()` en el CLI (después de `load_dotenv`, antes del import del grafo):

- **LangSmith:** si hay `LANGSMITH_API_KEY` (o legacy `LANGCHAIN_API_KEY`) → `LANGSMITH_TRACING=true`.
- **Phoenix:** si `PHOENIX_ENABLED=true` → `phoenix.otel.register` + `LangChainInstrumentor`.

## Trello

- Router por keywords (`trello`, `tablero`, `board`, `tarjeta`, `card`, …).
- Credenciales: `TRELLO_API_KEY` + `TRELLO_TOKEN` → `api.trello.com/1`.
- Tools: `list_boards`, `list_lists`, `create_card`, `move_card`.
- Sin credenciales: mensaje guía, sin exception al usuario.

## Pendiente

docker-compose, manifiestos k8s.

# Architecture — PO Copilot

## Estado actual (Plan A)

Implementado el vertical slice RAG local:

```
CLI → retrieve → generate → assess → refine|fallback|END
         │                      │
         └─ Chroma + Ollama     └─ docs vacíos: rewrite query (máx. 3)
            (nomic-embed-text)     docs presentes: responder
```

| Componente | Estado |
|---|---|
| `domain/` | Hecho (`product-owner`) |
| `ingestion/` + `scripts/ingest_corpus.py` | Hecho |
| `retrieval/` (Chroma embebido + Ollama embeddings) | Hecho |
| `orchestration/` (prompts grounded) | Hecho |
| `agent/` (LangGraph cíclico) | Hecho |
| `cli/` | Hecho (sin stub) |
| `ranking/` (cross-encoder) | Pendiente (Plan B) |
| Intent conceptual vs caso | Pendiente (Plan B) |
| `mcp/` Trello | Pendiente |
| LangSmith / Arize Phoenix | Pendiente |
| `docker-compose` / `k8s/` | Pendiente (placeholders) |

## Decisiones Plan A

- **Chroma embebido** en `CHROMA_PERSIST_DIR` (default `./data/chroma`), collection = `domain.id`.
- **Sin Docker** para el slice A: solo Ollama local + persistencia en disco.
- **Evaluate/assess:** si hay chunks recuperados → finish; si no, incrementa `attempts` y refine; a 3 intentos → fallback.
- **Refine:** reescritura de query con `llama3.1` (no el hack `+= " explicación"` de CLASE 3).
- Referencia didáctica: `CLASE 3/modular_vectorial/` (Gemini → Ollama en este repo).

## Pendiente

Ver Plan B (ranking + intención) y luego MCP, observabilidad y despliegue.

# PO Copilot

Asistente de consola que actúa como mentor de Product Owner, usando RAG
sobre una base de conocimiento de principios de producto y metodologías
ágiles. Interpreta si pedís teoría o traés un caso concreto, recupera
contexto, lo reordena con un reranker local y adapta la respuesta.

Proyecto final del curso de AI Engineering. Corre 100% local: LLM vía
Ollama, Chroma embebido, reranker cross-encoder local.

## Arquitectura

```
Consulta del usuario (CLI)
        │
        ▼
Interpretar intención  ──── conceptual vs caso práctico
        │
        ▼
Retrieve + rerank  ──── Chroma (k=20) + cross-encoder (top 5)
        │
        ▼
Generar respuesta PO  ──── llama3.1 + prompt según intención
        │
        ▼
Assess confianza  ──── score de rerank
   │        │
   │        └──── débil → reformular query (máx. 3)
   └───────────────────── OK → respuesta en consola
```

Detalle en [`docs/architecture.md`](docs/architecture.md).

### Dominio vs infraestructura

| Capa | Qué incluye | Cómo cambia |
|---|---|---|
| **Dominio** | `src/domain/` + `data/corpus/<domain-id>/` | Nuevo módulo + registry; `DOMAIN_ID` |
| **Infraestructura** | `cli`, `ingestion`, `retrieval`, `ranking`, `orchestration`, `agent`, … | Consume `get_domain()` |

### Componentes

| Componente | Responsabilidad | Tecnología |
|---|---|---|
| `domain/` | Identidad, corpus path, copy | Dataclass + registry |
| `ingestion/` | Carga y chunking | LangChain splitters |
| `retrieval/` | Búsqueda semántica | Chroma + `nomic-embed-text` |
| `ranking/` | Reordena por relevancia | `cross-encoder/ms-marco-MiniLM-L-6-v2` |
| `orchestration/` | Prompts conceptual / case | Prompt builders |
| `agent/` | Grafo cíclico LangGraph | LangGraph + Ollama |
| `mcp/` | Trello (pendiente) | MCP |
| `cli/` | Consola | Rich |
| `observability/` | Trazas (pendiente) | LangSmith + Phoenix |

## Cómo ejecutar

### 1. Requisitos

- Python 3.11+
- [Ollama](https://ollama.com) con:
  ```bash
  ollama pull llama3.1
  ollama pull nomic-embed-text
  ```

### 2. Instalación

```bash
git clone <repo>
cd product-rag
python -m venv .venv && source .venv/bin/activate
pip install -e .
cp .env.example .env
```

### 3. Ingestar corpus

```bash
python scripts/ingest_corpus.py
```

### 4. CLI

```bash
python -m src.cli.main
```

La primera consulta puede tardar: descarga/carga del cross-encoder.

## Estado del proyecto

**Plan A + B hechos:** corpus, ingestion, retrieval, ranking, intención,
grafo LangGraph y CLI.

**Pendiente:** MCP Trello, LangSmith/Phoenix, docker-compose, k8s, tests.

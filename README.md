# PO Copilot

Asistente de consola que actúa como mentor de Product Owner, usando RAG
sobre una base de conocimiento de principios de producto y metodologías
ágiles. No solo responde preguntas: interpreta el marco correspondiente
(RICE, Jobs to be Done, User Story Mapping, etc.) a partir del corpus
recuperado.

Proyecto final del curso de AI Engineering. Corre 100% local: LLM vía
Ollama, base vectorial embebida (Chroma).

## Arquitectura

El corazón del sistema es un grafo cíclico (LangGraph) que recupera
contexto, genera una respuesta grounded y, si no hay documentos, reformula
la búsqueda hasta un tope de intentos.

```
Consulta del usuario (CLI)
        │
        ▼
Retrieve + embeddings  ──── Chroma + nomic-embed-text (Ollama)
        │
        ▼
Generar respuesta PO  ──── llama3.1 (Ollama) + contexto recuperado
        │
        ▼
Assess  ──── ¿hay contexto?
   │        │
   │        └──── no → reformular query (vuelve a Retrieve, máx. 3)
   └───────────────────── sí → respuesta en consola
```

Detalle en [`docs/architecture.md`](docs/architecture.md).

### Dominio vs infraestructura

El “qué es este coach” vive en `src/domain/`. El resto del código es genérico
y no debe hardcodear copy, corpus ni identidad de negocio.

| Capa | Qué incluye | Cómo cambia |
|---|---|---|
| **Dominio** | `src/domain/` + `data/corpus/<domain-id>/` | Nuevo módulo de dominio + entrada en el registry; `DOMAIN_ID` elige cuál cargar |
| **Infraestructura** | `cli`, `ingestion`, `retrieval`, `ranking`, `orchestration`, `agent`, `mcp`, `observability` | Agnóstica al negocio; consume `get_domain()` |

Hoy el dominio default es `product-owner` (PO Copilot).

### Componentes

| Componente | Responsabilidad | Tecnología |
|---|---|---|
| `domain/` | Identidad del coach, corpus path, copy de negocio | Dataclass + registry (`DOMAIN_ID`) |
| `ingestion/` | Carga y chunking del corpus del dominio activo | LangChain loaders + text splitters |
| `retrieval/` | Búsqueda semántica sobre el corpus | ChromaDB + embeddings `nomic-embed-text` (Ollama) |
| `ranking/` | Reordena resultados por relevancia (pendiente) | `cross-encoder/ms-marco-MiniLM-L-6-v2` |
| `orchestration/` | Prompts que arman el contexto final para el LLM | LangChain-style prompts |
| `agent/` | Grafo cíclico retrieve → generate → assess → refine | LangGraph |
| `mcp/` | Adaptador Trello (pendiente) | MCP |
| `cli/` | Punto de entrada de consola | Python + `rich` |
| `observability/` | Trazas y métricas (pendiente) | LangSmith + Arize Phoenix |

## Estructura del repositorio

```
product-rag/
├── src/
│   ├── domain/
│   ├── ingestion/
│   ├── retrieval/
│   ├── ranking/          # pendiente
│   ├── orchestration/
│   ├── agent/
│   ├── mcp/              # pendiente
│   ├── cli/
│   └── observability/    # pendiente
├── data/corpus/product-owner/
├── scripts/ingest_corpus.py
├── docs/architecture.md
├── k8s/                  # placeholder — manifiestos pendientes
└── tests/                # pendiente
```

## Cómo ejecutar

### 1. Requisitos previos

- Python 3.11+
- [Ollama](https://ollama.com) instalado, con los modelos:
  ```bash
  ollama pull llama3.1
  ollama pull nomic-embed-text
  ```

### 2. Instalación

```bash
git clone <repo>
cd product-rag
python -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env   # DOMAIN_ID=product-owner
```

### 3. Ingestar el corpus

```bash
python scripts/ingest_corpus.py
# reindexar: python scripts/ingest_corpus.py --force
```

### 4. Correr el agente por consola

```bash
python -m src.cli.main
```

## Estado del proyecto

**Plan A hecho:** corpus seed, ingestion, retrieval Chroma/Ollama, grafo
LangGraph y CLI usable.

**Pendiente:** ranking + intención (Plan B), MCP Trello, LangSmith/Phoenix,
docker-compose, manifiestos Kubernetes, suite de tests.

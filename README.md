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
Detect Trello? ── sí → tools REST (boards/cards) → consola
        │ no
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
| `mcp/` | Trello (REST tools) | LangChain tools + API key |
| `cli/` | Consola | Rich |
| `observability/` | Trazas env-gated | LangSmith + Phoenix |

## Cómo ejecutar

Los comandos del día a día van por **pnpm scripts** (como en Node).
Siempre usan `.venv/bin/python -m …`, así no dependés de `pip`/`pytest` en el PATH.

| Comando | Qué hace |
|---|---|
| `pnpm setup` | Crea `.venv` e instala deps + dev |
| `pnpm install` / `pnpm build` | Reinstala el paquete editable |
| `pnpm ingest` | Ingesta el corpus |
| `pnpm ingest:force` | Reindexa el corpus |
| `pnpm start` / `pnpm dev` | CLI |
| `pnpm phoenix:up` / `phoenix:down` | Phoenix vía Docker Compose |
| `pnpm phoenix:logs` | Logs del contenedor Phoenix |
| `pnpm phoenix` | Phoenix en el venv (alternativa sin Docker) |
| `pnpm test` | Unitarios + coverage (terminal) |
| `pnpm test:cov` | Unitarios + coverage HTML con badges de color |
| `pnpm cov:open` | Abre el reporte HTML en el browser |
| `pnpm test:integration` | Smokes con Ollama |
| `pnpm test:all` | Unitarios + integration + coverage |

### 1. Requisitos

- Python 3.11+
- [pnpm](https://pnpm.io)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (para Phoenix vía Compose)
- [Ollama](https://ollama.com) con:
  ```bash
  ollama pull llama3.1
  ollama pull nomic-embed-text
  ```

### 2. Instalación

```bash
git clone <repo>
cd product-rag
cp .env.example .env
pnpm setup      # crea .venv e instala deps + extras dev
# si el venv ya existe:
pnpm install
```

### 3. Ingestar corpus

```bash
pnpm ingest
# reindexar: pnpm ingest:force
```

### 4. CLI

```bash
pnpm start
# alias: pnpm dev
```

La primera consulta puede tardar: descarga/carga del cross-encoder.

## Observabilidad

Tracing opcional, activado por env (ver `.env.example`).

### LangSmith (cloud)

1. Creá una API key en [LangSmith](https://smith.langchain.com).
2. En `.env`:
   ```bash
   LANGSMITH_API_KEY=ls-...
   LANGSMITH_PROJECT=po-copilot
   ```
3. Corré `pnpm start` y mirá los runs del grafo en LangSmith.

### Phoenix (local)

Preferido (Docker Compose — solo el servicio Phoenix; CLI y Ollama siguen en el host):

1. `pnpm phoenix:up` (UI en `http://localhost:6006`).
2. En `.env`:
   ```bash
   PHOENIX_ENABLED=true
   PHOENIX_COLLECTOR_ENDPOINT=http://localhost:6006
   ```
3. Corré `pnpm start` en otra terminal; las trazas aparecen en Phoenix.
4. Parar: `pnpm phoenix:down`. Logs: `pnpm phoenix:logs`.

Alternativa sin Docker: `pnpm phoenix` (servidor del venv, mismo puerto).

Podés usar LangSmith y Phoenix a la vez. Sin key / sin `PHOENIX_ENABLED`, el CLI no envía trazas.

## Trello

Si la consulta menciona Trello / tablero / tarjeta / board / card, el grafo
desvía a un agente con tools REST (no usa el path RAG).

1. En [Trello Power-Ups Admin](https://trello.com/power-ups/admin) generá API key y token.
2. En `.env`:
   ```bash
   TRELLO_API_KEY=...
   TRELLO_TOKEN=...
   ```
3. Ejemplos en el CLI:
   - `listá mis boards de trello`
   - `creá una tarjeta "Spike RICE" en el tablero Product`

Sin credenciales, el CLI responde con instrucciones (no crashea).

## Tests

```bash
pnpm test                 # unitarios + coverage (sin Ollama)
pnpm test:cov             # genera reporte HTML en htmlcov/
pnpm cov:open             # abre htmlcov/index.html en el browser
pnpm test:integration     # smokes (Ollama + corpus ingerido)
pnpm test:all             # unitarios + integration + coverage
```

Los integration pueden tardar en la primera corrida (cross-encoder / Ollama).



## Estado del proyecto

**Plan A + B hechos:** corpus, ingestion, retrieval, ranking, intención,
grafo LangGraph y CLI.

**Tests:** unitarios con coverage + smokes de integración opcionales.

**Observabilidad:** LangSmith + Phoenix (env-gated).

**Trello:** tools REST (`list_boards`, `list_lists`, `create_card`, `move_card`)
vía router por keywords.

**Docker Compose:** Phoenix (`arizephoenix/phoenix:version-19.18.0`) vía
`pnpm phoenix:up`.

**Pendiente:** k8s.

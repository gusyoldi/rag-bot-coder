# PO Copilot

Asistente de consola que actúa como mentor de Product Owner, usando RAG
sobre una base de conocimiento de principios de producto y metodologías
ágiles. No solo responde preguntas: interpreta si estás pidiendo teoría o
trayendo un caso concreto, y adapta su respuesta para actuar como un PO
real — aplicando el marco correspondiente (RICE, Jobs to be Done, User
Story Mapping, etc.) en vez de solo citarlo.

Proyecto final del curso de AI Engineering. Corre 100% local: LLM vía
Ollama, base vectorial embebida (Chroma), reranker local (cross-encoder),
y una herramienta MCP que conecta con Trello para crear/consultar
tarjetas del backlog real del usuario.

## Arquitectura

El corazón del sistema es un grafo cíclico (LangGraph) que decide en cada
paso si tiene contexto suficiente para responder, si necesita reformular
la búsqueda, o si necesita usar una herramienta externa.

```
Consulta del usuario (CLI)
        │
        ▼
Interpretar intención  ──── conceptual vs. caso práctico
        │
        ▼
Retrieve + rerank  ──── Chroma (búsqueda semántica) + cross-encoder
        │
        ▼
Evaluar confianza  ──── ¿el contexto recuperado alcanza?
   │        │        │
   │        │        └──── no alcanza → llamar MCP (Trello)
   │        └──────────── contexto débil → reformular query (vuelve a Retrieve)
   └───────────────────── contexto suficiente → continuar
        │
        ▼
Generar respuesta PO  ──── aplica el marco recuperado al caso del usuario
        │
        ▼
Respuesta en consola
```

Todo el recorrido del grafo queda trazado en **LangSmith**, y las métricas
de calidad (faithfulness, latencia por nodo) se envían a **Arize
Phoenix** (self-hosted, corre en Docker junto al resto del stack).

### Dominio vs infraestructura

El “qué es este coach” vive en `src/domain/`. El resto del código es genérico
y no debe hardcodear copy, corpus ni identidad de negocio.

| Capa | Qué incluye | Cómo cambia |
|---|---|---|
| **Dominio** | `src/domain/` + `data/corpus/<domain-id>/` | Nuevo módulo de dominio + entrada en el registry; `DOMAIN_ID` elige cuál cargar |
| **Infraestructura** | `cli`, `ingestion`, `retrieval`, `ranking`, `orchestration`, `agent`, `mcp`, `observability` | Agnóstica al negocio; consume `get_domain()` |

Hoy el dominio default es `product-owner` (PO Copilot). Para agregar otro:
crear `src/domain/<otro>.py`, registrarlo, y apuntar `DOMAIN_ID` (o el corpus)
sin tocar el CLI.

### Componentes

| Componente | Responsabilidad | Tecnología |
|---|---|---|
| `domain/` | Identidad del coach, corpus path, copy de negocio | Dataclass + registry (`DOMAIN_ID`) |
| `ingestion/` | Carga y chunking del corpus del dominio activo | LangChain document loaders |
| `retrieval/` | Búsqueda semántica sobre el corpus | ChromaDB + embeddings `nomic-embed-text` (Ollama) |
| `ranking/` | Reordena los resultados del retrieval por relevancia real | `cross-encoder/ms-marco-MiniLM-L-6-v2` |
| `orchestration/` | Prompts y chains que arman el contexto final para el LLM | LangChain |
| `agent/` | Grafo cíclico de decisión (reformular / usar herramienta / responder) | LangGraph |
| `mcp/` | Adaptador seguro a Trello (crear/buscar tarjetas de backlog) | MCP (protocolo oficial) |
| `cli/` | Punto de entrada de consola (genérico, lee el dominio) | Python + `rich` |
| `observability/` | Instrumentación de trazas y métricas | LangSmith + Arize Phoenix |

### Por qué estas decisiones

- **Todo local (Ollama + Chroma + reranker local):** evita dependencias de
  APIs pagas para un proyecto de curso, y mantiene consistencia — no tiene
  sentido medir "uso de recursos" como métrica si la mitad del pipeline
  corre en la nube de un tercero.
- **MCP a Trello y no a un mock:** le da al agente una acción real y útil
  (crear una tarjeta de backlog en vez de solo hablar de teoría), lo cual
  también hace más interesante medir latencia end-to-end con una llamada
  a herramienta externa real de por medio.
- **Loop con tope de iteraciones:** el estado del grafo lleva un contador
  para evitar que el ciclo de reformulación entre en un loop infinito si
  el corpus no tiene información suficiente sobre algo.

## Estructura del repositorio

```
po-copilot/
├── src/
│   ├── domain/           # identidad de negocio (default: product-owner)
│   ├── ingestion/
│   ├── retrieval/
│   ├── ranking/
│   ├── orchestration/
│   ├── agent/
│   ├── mcp/
│   ├── cli/
│   └── observability/
├── data/corpus/
│   └── product-owner/    # corpus del dominio default
├── k8s/                  # manifiestos de despliegue (Deployment, Service, HPA)
├── scripts/               # automatización de despliegue, escalado e ingestión
├── docs/
│   ├── architecture.md   # decisiones arquitectónicas en detalle
│   ├── metrics.md        # definición de métricas de observabilidad
│   └── deployment.md     # proceso de despliegue y monitoreo
└── tests/
```

## Cómo ejecutar cada módulo

### 1. Requisitos previos

- Python 3.11+
- [Ollama](https://ollama.com) instalado, con los modelos:
  ```bash
  ollama pull llama3.1
  ollama pull nomic-embed-text
  ```
- Docker (para levantar Arize Phoenix)

### 2. Instalación

```bash
git clone <repo>
cd po-copilot
pip install -e .
cp .env.example .env   # DOMAIN_ID=product-owner; completar TRELLO_*, LANGCHAIN_API_KEY
```

### 3. Levantar servicios locales

```bash
docker compose up -d   # Chroma + Arize Phoenix
```

### 4. Ingestar el corpus

```bash
python scripts/ingest_corpus.py --source data/corpus/product-owner/
```

### 5. Levantar el servidor MCP de Trello

```bash
python -m src.mcp.trello_server
```

### 6. Correr el agente por consola

```bash
python -m src.cli.main
```

### 7. Ver trazas y métricas

- LangSmith: [smith.langchain.com](https://smith.langchain.com) (proyecto `po-copilot`)
- Arize Phoenix: `http://localhost:6006`

## Despliegue

Los manifiestos de Kubernetes en `k8s/` están listos para un cluster real
(GKE/EKS/AKS), con resource limits y HPA basado en CPU ya definidos. Ver
`docs/deployment.md` para el detalle del proceso y de qué se monitorea
en producción.

## Estado del proyecto

🚧 En construcción — ver `docs/architecture.md` para el detalle de qué
componentes están implementados y cuáles son el siguiente paso.
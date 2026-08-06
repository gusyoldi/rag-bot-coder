---
name: Scaffold PO Copilot
overview: "Scaffold mínimo del CLI `po-copilot` en la raíz del workspace: estructura de carpetas, `pyproject.toml`, loop de consola stub con Rich, y `.env.example`, sin lógica RAG aún."
todos:
  - id: dirs
    content: Crear estructura de carpetas + __init__.py / .gitkeep
    status: completed
  - id: pyproject
    content: Escribir pyproject.toml con dependencias y Hatchling
    status: completed
  - id: cli
    content: Implementar src/cli/main.py (saludo + loop stub + exit/salir)
    status: completed
  - id: env
    content: Crear .env.example con las 5 variables
    status: completed
  - id: verify
    content: pip install -e . y verificar python -m src.cli.main
    status: completed
isProject: false
---

# Scaffold inicial de po-copilot

**Usando writing-plans** para el plan de implementación del scaffold mínimo.

**Goal:** Tener un proyecto Python instalable cuyo CLI salude, haga echo stub de la consulta y salga con `exit`/`salir`.

**Arquitectura:** Paquete importable `src` (como pediste con `python -m src.cli.main`). Los módulos `ingestion`, `retrieval`, etc. quedan como paquetes vacíos con `__init__.py`. Sin LangGraph, Chroma ni MCP en este paso.

**Tech stack:** Python ≥3.11, Rich para I/O, dependencias RAG/MCP declaradas en `pyproject.toml` pero no usadas todavía.

**Ubicación:** Archivos en la raíz de [`/Users/gustavoyoldi/src/product-rag`](/Users/gustavoyoldi/src/product-rag) (workspace vacío). El nombre del proyecto en `pyproject.toml` será `po-copilot` (no se crea una carpeta anidada `po-copilot/`).

## Estructura a crear

```
.
├── src/
│   ├── __init__.py
│   ├── ingestion/__init__.py
│   ├── retrieval/__init__.py
│   ├── ranking/__init__.py
│   ├── orchestration/__init__.py
│   ├── agent/__init__.py
│   ├── mcp/__init__.py
│   ├── cli/
│   │   ├── __init__.py
│   │   └── main.py
│   └── observability/__init__.py
├── data/corpus/.gitkeep
├── k8s/.gitkeep
├── scripts/.gitkeep
├── docs/.gitkeep
├── tests/.gitkeep
├── pyproject.toml
└── .env.example
```

## Archivos clave

### [`pyproject.toml`](pyproject.toml)

- `name = "po-copilot"`, `version = "0.1.0"`, `requires-python = ">=3.11"`
- Dependencias exactas pedidas: `langchain`, `langgraph`, `langchain-ollama`, `langchain-chroma`, `chromadb`, `sentence-transformers`, `mcp`, `rich`, `python-dotenv`
- Build con Hatchling, empaquetando el directorio `src` para que `python -m src.cli.main` funcione tras `pip install -e .`

### [`src/cli/main.py`](src/cli/main.py)

Loop mínimo con Rich:

- `Console` para saludo y respuestas
- `Prompt.ask` para input
- Saludo al iniciar: mensaje tipo “PO Copilot”
- `while True`: leer query; si `exit`/`salir` (case-insensitive, strip) → despedida y `break`
- Respuesta stub: `[stub] Todavía no tengo retrieval conectado, pero recibí: {query}`
- Guard `if __name__ == "__main__": main()`

### [`.env.example`](.env.example)

Variables placeholder (sin valores secretos):

```
OLLAMA_BASE_URL=http://localhost:11434
CHROMA_PERSIST_DIR=./data/chroma
TRELLO_API_KEY=
TRELLO_TOKEN=
LANGCHAIN_API_KEY=
```

## Fuera de alcance (explícito)

No implementar: ingestion, retrieval, ranking, grafo LangGraph, servidor MCP, tests reales, README, ni lógica que lea `.env` todavía.

## Verificación

1. Instalar en editable: `pip install -e .` (o `uv pip install -e .` si `uv` está disponible)
2. Probar el loop de forma no interactiva, p.ej.:
   `printf 'hola\nsalir\n' | python -m src.cli.main`
3. Confirmar: saludo “PO Copilot”, echo stub con `hola`, salida limpia sin traceback

Nota: `pnpm build` no aplica (proyecto Python). La verificación es el comando anterior.

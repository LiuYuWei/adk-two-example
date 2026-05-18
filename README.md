# adk-two-example

A small, runnable **Google ADK 2.0** project — Docker-first, with a Makefile,
so it works like a real GitHub repo you can clone and start.

It implements one graph **`Workflow`** (`smart_brief`) that shows off the
capabilities that are *new in ADK 2.0* and have no direct ADK 1.x equivalent:
explicit edge graph, parallel fan-out / fan-in, function nodes, shared state,
and an LLM quality-gate **loop**.

> ⚠️ ADK 2.0 is a **Beta / pre-release**. It is installed with `pip --pre`,
> not by a plain `pip install google-adk`. Do not use it in production:
> the session/event schema is not compatible with ADK 1.x.

## The workflow

```
                         ┌──────────────────────────┐
 START ─▶ process_input ─▶ research_angles ┐         │
                          gather_facts    ─┴▶ join ─▶ write_brief ─▶ grade_brief
                                                          ▲                │
                                              "revise" ◀──┴──── route_quality
                                                                           │
                                                                "good" ─▶ finalize
```

- `process_input` / `route_quality` / `finalize` — **plain Python functions** as nodes.
- `research_angles` ‖ `gather_facts` — **parallel fan-out**, merged by a `JoinNode`.
- `route_quality` — **deterministic routing** via `Event(route=...)`.
- `"revise" → write_brief` — a **loop** that re-drafts with editor feedback in shared `state`.

Code: [`app/smart_brief/agent.py`](app/smart_brief/agent.py).

## Quick start (Docker — recommended)

```bash
cp .env.example .env          # then edit .env: add GOOGLE_API_KEY
make up                       # build + run via docker compose
```

Open <http://localhost:8000>, pick **smart_brief**, and send a topic such as
`the economics of home solar`.

Without compose:

```bash
make build && make docker-run
```

## Quick start (local Python ≥ 3.10)

```bash
make venv      # .venv + pip install --pre -r requirements.txt
make env       # create .env, then edit it
make web       # dev UI at http://localhost:8000
# or:
make run       # run smart_brief interactively in the terminal
make test      # offline structural tests (no API key needed)
```

`make help` lists every target.

## Configuration

All config is via `.env` (auto-loaded by the ADK CLI). See
[`.env.example`](.env.example):

| Variable | Purpose |
|---|---|
| `ADK_MODEL` | Model for every agent (default `gemini-2.5-flash`) |
| `GOOGLE_API_KEY` + `GOOGLE_GENAI_USE_VERTEXAI=FALSE` | AI Studio auth (easiest) |
| `GOOGLE_CLOUD_PROJECT` / `GOOGLE_CLOUD_LOCATION` + `GOOGLE_GENAI_USE_VERTEXAI=TRUE` | Vertex AI auth |

Get an AI Studio key at <https://aistudio.google.com/apikey>.

## Project layout

```
.
├── app/
│   ├── __init__.py
│   ├── smart_brief/
│   │   ├── __init__.py      # `from . import agent` (ADK discovery contract)
│   │   ├── agent.py         # `root_agent = Workflow(...)`
│   │   └── agent.json       # A2A agent card (exposed with --a2a)
│   └── a2a_consumer/
│       ├── __init__.py
│       └── agent.py         # RemoteA2aAgent as a Workflow node
├── tests/
│   ├── test_workflow.py     # offline graph-structure tests
│   └── test_a2a_consumer.py # offline A2A wiring tests
├── Dockerfile               # installs ADK 2.0 (+a2a) with `pip --pre`
├── docker-compose.yml
├── Makefile
├── requirements.txt / pyproject.toml
└── .env.example
```

## How agent discovery works

`adk web app` / `adk run app/smart_brief` scan for a package that exposes
`root_agent`. The contract: a directory with `__init__.py` doing
`from . import agent`, and `agent.py` defining `root_agent`. Drop another
folder under `app/` with the same shape to add more agents to the same UI.

## A2A (Agent-to-Agent)

This repo supports the A2A protocol **both ways** on one server:

- **Exposes** `smart_brief` over A2A (it has `app/smart_brief/agent.json`).
- **Consumes** it from `app/a2a_consumer/` via `RemoteA2aAgent`, used as a
  plain `Workflow` node.

```bash
make a2a            # adk web --port 8000 --a2a app
make a2a-card       # print smart_brief's served A2A card
```

- Card: `http://localhost:8000/a2a/smart_brief/.well-known/agent-card.json`
- In the dev UI pick **`a2a_consumer`** to see a loopback A2A call.

Requires the `google-adk[a2a]` extra (already in `requirements.txt`).

## Notes & caveats

- 2.0 pre-releases ship breaking changes between builds; pin the version.
- Do **not** point this at an ADK 1.x session store/DB — schemas differ.
- This is a learning/example repo, not a production template.

## Sources

- ADK 2.0 overview: <https://adk.dev/2.0/> · Docs: <https://google.github.io/adk-docs/>
- Workflow samples (v2 branch): <https://github.com/google/adk-python/tree/v2/contributing/workflow_samples>
- PyPI: <https://pypi.org/project/google-adk/>

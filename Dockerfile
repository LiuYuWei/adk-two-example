# ADK 2.0 example image.
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /srv

# `--pre` is REQUIRED: ADK 2.0 is a pre-release and is not selected otherwise.
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --pre -r requirements.txt

# The `app/` package holds the agent(s). `adk web` discovers every
# subdirectory that exposes a `root_agent`.
COPY app ./app

EXPOSE 8000

# Dev UI + API server, with A2A enabled. --host 0.0.0.0 so it's reachable
# from the host. --a2a exposes every agent that has an agent.json card at
# /a2a/<name>/.well-known/agent-card.json (here: smart_brief).
# `app` is the agents-parent directory passed to the ADK CLI.
CMD ["adk", "web", "--host", "0.0.0.0", "--port", "8000", "--a2a", "app"]

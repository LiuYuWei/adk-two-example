# Copyright 2026
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

"""a2a_consumer — calling another agent over the A2A protocol.

This is the *other half* of A2A in ADK 2.0. `smart_brief` is **exposed**
as an A2A server (it has an ``agent.json`` agent card, and is served at
``/a2a/smart_brief`` when you start with ``--a2a``). This package
**consumes** it: ``RemoteA2aAgent`` wraps that remote endpoint and we
drop it into a ``Workflow`` as just another node.

Run everything on one server with::

    make a2a            # = adk web --a2a app

Then in the dev UI pick ``a2a_consumer`` and send a topic. The call path
is: dev UI -> a2a_consumer (this) -> HTTP/A2A -> smart_brief (loopback on
the same server) -> back.

The remote card URL is configurable so you can point this at a
``smart_brief`` running on a different host/port.
"""

from __future__ import annotations

import os

from google.adk import Event
from google.adk import Workflow
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent

# Where to find the remote agent's A2A card. Default = local smart_brief
# served by the same `adk web --a2a app` process.
REMOTE_BRIEF_CARD_URL = os.environ.get(
    "REMOTE_BRIEF_CARD_URL",
    "http://localhost:8000/a2a/smart_brief/.well-known/agent-card.json",
)

# A remote, A2A-spoken agent — usable anywhere a normal agent/node is.
remote_brief = RemoteA2aAgent(
    name="remote_smart_brief",
    description="The smart_brief workflow, reached over the A2A protocol.",
    agent_card=REMOTE_BRIEF_CARD_URL,
)


def announce(node_input: str):
    """Tiny function node so the trace shows the A2A hand-off clearly."""
    yield Event(
        message=f"→ 透過 A2A 呼叫遠端 smart_brief，主題：{node_input}",
        state={"topic": node_input},
    )


# A RemoteA2aAgent is just a node: the graph doesn't care that the work
# happens in another process / on another machine.
root_agent = Workflow(
    name="a2a_consumer",
    edges=[("START", announce, remote_brief)],
)

"""Structural tests for the A2A pieces — offline, no network.

Asserts the consumer graph wraps a RemoteA2aAgent and that smart_brief
ships a valid A2A agent card.
"""

import json
import pathlib

from google.adk import Workflow
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent

from app.a2a_consumer.agent import remote_brief
from app.a2a_consumer.agent import root_agent

CARD = pathlib.Path(__file__).parent.parent / "app" / "smart_brief" / "agent.json"


def test_consumer_is_workflow_with_remote_node():
    assert isinstance(root_agent, Workflow)
    assert root_agent.name == "a2a_consumer"
    assert isinstance(remote_brief, RemoteA2aAgent)


def test_smart_brief_agent_card_is_valid():
    card = json.loads(CARD.read_text())
    # A2A AgentCard required fields (camelCase per spec).
    for key in (
        "name",
        "description",
        "url",
        "version",
        "capabilities",
        "defaultInputModes",
        "defaultOutputModes",
        "skills",
    ):
        assert key in card, f"agent.json missing required field: {key}"
    assert card["name"] == "smart_brief"
    assert card["skills"], "at least one skill required"
    for sk in card["skills"]:
        assert {"id", "name", "description", "tags"} <= sk.keys()

"""Structural tests — no model calls, so they run offline / in CI.

These assert the workflow graph is wired the way we expect. End-to-end
runs that hit Gemini are done interactively via `make web` / `make run`.
"""

from google.adk import Workflow

from app.smart_brief.agent import finalize
from app.smart_brief.agent import root_agent
from app.smart_brief.agent import route_quality
from app.smart_brief.agent import write_brief


def test_root_agent_is_a_workflow():
    assert isinstance(root_agent, Workflow)
    assert root_agent.name == "smart_brief"


def test_graph_has_entry_and_loop_edges():
    edges = root_agent.edges
    # First edge starts at START and fans out then joins.
    assert edges[0][0] == "START"
    # Second edge is the quality-gate branch map.
    branch_src, branch_map = edges[1]
    assert branch_src is route_quality
    assert branch_map["good"] is finalize
    assert branch_map["revise"] is write_brief  # the loop-back

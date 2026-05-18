# Copyright 2026
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

"""smart_brief — an ADK 2.0 graph Workflow example.

This single workflow exercises the headline features that are *new in
ADK 2.0* and have no equivalent in ADK 1.x:

  * ``Workflow`` with an explicit ``edges`` graph (vs. 1.x
    ``SequentialAgent`` / ``ParallelAgent`` / ``LoopAgent``).
  * Fan-out / fan-in via a tuple of nodes plus ``JoinNode``.
  * Plain Python functions as first-class nodes (no tool wrapper).
  * ``Event`` to write shared workflow ``state`` and to drive routing.
  * A quality-gate loop that re-runs an upstream node until an
    LLM grader is satisfied.

Pipeline:

    START
      -> process_input            (store topic in state)
      -> (research_angles ‖ gather_facts)   fan-out, run in parallel
      -> join_node                fan-in
      -> write_brief              LLM draft, reads {angles}/{facts}
      -> grade_brief              LLM grader -> structured verdict
      -> route_quality            Event(route=...)
           "revise" -> write_brief   (loop with feedback in state)
           "good"   -> finalize
"""

from __future__ import annotations

import os
from typing import Literal

from google.adk import Agent
from google.adk import Event
from google.adk import Workflow
from google.adk.workflow import JoinNode
from pydantic import BaseModel
from pydantic import Field

# Model is configurable so the same code runs against AI Studio or Vertex.
MODEL = os.environ.get("ADK_MODEL", "gemini-2.5-flash")


# --------------------------------------------------------------------------- #
# 1. Entry node: a plain function that seeds shared workflow state.
# --------------------------------------------------------------------------- #
def process_input(node_input: str):
  """Take the raw user topic and place it in shared state."""
  yield Event(state={"topic": node_input.strip(), "feedback": ""})


# --------------------------------------------------------------------------- #
# 2. Fan-out: two independent LLM agents run in parallel.
#    `output_key` writes each result into shared state automatically.
# --------------------------------------------------------------------------- #
research_angles = Agent(
    name="research_angles",
    model=MODEL,
    instruction=(
        'Give 3 sharp, non-obvious angles for a brief about "{topic}". '
        "Return them as a short bulleted list, nothing else."
    ),
    output_key="angles",
)

gather_facts = Agent(
    name="gather_facts",
    model=MODEL,
    instruction=(
        'List 4 concrete, verifiable facts or data points about "{topic}". '
        "Bulleted list only."
    ),
    output_key="facts",
)

join_node = JoinNode(name="join_research")


# --------------------------------------------------------------------------- #
# 3. Draft writer. Reads the fanned-in state. `{feedback?}` is optional:
#    empty on the first pass, populated when the quality gate loops back.
# --------------------------------------------------------------------------- #
write_brief = Agent(
    name="write_brief",
    model=MODEL,
    instruction=(
        'Write a tight ~150-word executive brief about "{topic}".\n\n'
        "Use these angles:\n{angles}\n\n"
        "Ground it in these facts:\n{facts}\n\n"
        "If the reviewer left feedback, address it: {feedback?}"
    ),
    output_key="draft",
)


# --------------------------------------------------------------------------- #
# 4. LLM quality gate with a structured verdict (Pydantic output_schema).
# --------------------------------------------------------------------------- #
class Verdict(BaseModel):
  grade: Literal["good", "revise"] = Field(
      description="'good' if the brief is publishable, else 'revise'."
  )
  feedback: str = Field(
      description="If 'revise', concrete instructions to improve the draft."
  )


grade_brief = Agent(
    name="grade_brief",
    model=MODEL,
    instruction=(
        "You are a demanding editor. Judge this draft for clarity, accuracy "
        "and punchiness:\n\n{draft}\n\n"
        "Mark 'good' only if it needs no further edits."
    ),
    output_schema=Verdict,
    output_key="verdict",
)


def route_quality(verdict: Verdict):
  """Turn the grader's verdict into a routing decision + store feedback."""
  yield Event(
      state={"feedback": verdict.feedback},
      route=verdict.grade,
  )


def finalize(draft: str):
  """Terminal node: emit the approved brief to the user."""
  yield Event(message=f"✅ Final brief:\n\n{draft}")


# --------------------------------------------------------------------------- #
# 5. The graph itself. `root_agent` is what `adk web` / `adk run` discovers.
# --------------------------------------------------------------------------- #
root_agent = Workflow(
    name="smart_brief",
    edges=[
        (
            "START",
            process_input,
            (research_angles, gather_facts),  # fan-out (parallel)
            join_node,                        # fan-in
            write_brief,
            grade_brief,
            route_quality,
        ),
        (
            route_quality,
            {
                "revise": write_brief,  # loop back with feedback
                "good": finalize,
            },
        ),
    ],
)

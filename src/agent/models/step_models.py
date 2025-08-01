"""Step models for the agent.

This module contains the step models used by the agent.
"""

from pydantic import BaseModel, Field


class Step(BaseModel):
    description: str = Field(
        description="The description of the step that needs to be performed.",
    )


class StepList(BaseModel):
    steps: list[Step] = Field(
        description="List of steps to be performed.",
    )
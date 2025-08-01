"""Task models for the agent.

This module contains the task models used by the agent.
"""

from pydantic import BaseModel, Field


class Task(BaseModel):
    description: str = Field(
        description="The description of the task that needs to be performed.",
    )


class TaskList(BaseModel):
    tasks: list[Task] = Field(
        description="List of tasks to be performed.",
    )
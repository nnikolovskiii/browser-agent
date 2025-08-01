from __future__ import annotations

from typing import Annotated, TypedDict, List, Dict

from langgraph.graph import add_messages

from ..models.task_models import Task


# Graph state
class State(TypedDict):
    messages: Annotated[list, add_messages]
    user_task: str
    # Web-specific fields
    current_url: str          # To track the browser's current location
    page_content: str         # The "context" is now the content of the webpage
    plan: str                 # Re-use planning mechanism
    steps: List[Task]         # Re-use step segmentation
    current_step_index: int   # Re-use step tracking
    action_history: str       # Track actions performed
    # File-specific fields (kept for hybrid functionality)
    project_path: str
    context: str
    all_file_paths: Annotated[set, lambda x, y: x.union(y)]
    project_structure: str
    tasks: List[Task]
    current_task_index: int
    task_message_indices: Dict[int, int]
    input_type: str
    answer: str

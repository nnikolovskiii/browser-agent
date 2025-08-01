"""New LangGraph Agent.

This module defines a custom graph.
"""

# Core components
from .core.agent import llm_call, should_continue, tool_node, segment_into_steps
from .core.graph import llm_file_explore, llm_call_evaluator, build_context, make_plan
from .core.state import State
from .models.task_models import Task, TaskList

# Tools
from .tools.llm_tools import llm_with_tools, str_replace, run_bash_command, create_file, view_file
from .tools.file_utils import get_project_structure_as_string, concat_files_in_str, concat_folder_to_file

# Models
from .models.models import SearchFilePathsList, FileReflectionList, EnhanceTextInstruction, Route
from .models.schemas import SearchQueryList, Reflection

# Prompts
from .prompts.prompts import (
    file_planner_instructions,
    file_reflection_instructions,
    final_instruction,
    final_context_instruction,
    make_plan_instruction,
    get_current_date,
    agent_instruction,
    segment_plan_into_steps
)

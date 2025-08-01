from __future__ import annotations

import os
from typing import Literal

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field

from .ai_models import kimi_llm, deepseek_llm, gemini_flash_lite, gemini_flash
from .state import State
from ..prompts.prompts import final_context_instruction, make_plan_instruction, input_type_determination_prompt, answer_question_prompt, web_agent_instruction
from ..tools.file_utils import get_project_structure_as_string, concat_files_in_str
from ..tools.browser_tools import goto_url_helper, get_page_content, web_tools_by_name
from ..models.models import FileReflectionList, SearchFilePathsList, InputType
from ..prompts.prompts import file_planner_instructions, file_reflection_instructions

load_dotenv()



async def llm_file_explore(state: State):
    """
    Transcribes audio, then uses the text to find relevant files.
    """
    user_task = state["user_task"]
    project_path = state["project_path"]

    project_structure = get_project_structure_as_string(project_path)
    structured_llm = gemini_flash_lite.with_structured_output(SearchFilePathsList)

    formatted_prompt = file_planner_instructions.format(
        user_task=user_task,
        project_structure=project_structure,
        project_path=project_path,
    )

    print("Invoking LLM to find relevant file paths...")
    result: SearchFilePathsList = await structured_llm.ainvoke(formatted_prompt)
    filtered_file_paths = [path for path in result.file_paths if not path.endswith('.env')]
    context = concat_files_in_str(filtered_file_paths)
    return {"context": context, "all_file_paths": set(filtered_file_paths), "project_path": project_path,
            "project_structure": project_structure}


async def llm_call_evaluator(state: State):
    """LLM evaluates the files in context and suggests additions/removals"""
    user_task = state["user_task"]
    project_path = state["project_path"]
    context = state["context"]
    all_file_paths = state["all_file_paths"]

    # Filter out .env files from all_file_paths
    all_file_paths = {path for path in all_file_paths if not path.endswith('.env')}

    project_structure = get_project_structure_as_string(project_path)
    count = 0

    while True:
        structured_llm = gemini_flash_lite.with_structured_output(FileReflectionList)
        formatted_prompt = file_reflection_instructions.format(
            user_task=state["user_task"],
            project_structure=project_structure,
            context=context,
            project_path=project_path,

        )
        count += 1
        if count > 3:
            return {"context": context}

        try:
            result: FileReflectionList = await structured_llm.ainvoke(formatted_prompt)
            print(result)

            if result is None or result.additional_file_paths is None:
                break
        except Exception as e:
            print(f"Error in llm_call_evaluator: {e}")
            break
        new_files = [file_path for file_path in result.additional_file_paths if file_path not in all_file_paths]

        if len(new_files) == 0:
            break
        else:
            # Filter out .env files from new files before adding them
            filtered_new_files = [path for path in new_files if not path.endswith('.env')]
            all_file_paths.update(set(filtered_new_files))
            context = concat_files_in_str(list(all_file_paths))

    print("*************************************")
    print(all_file_paths)
    return {"file_reflection": result, "context": context}


async def build_context(state: State):
    """LLM evaluates the files in context and suggests additions/removals"""
    user_task = state["user_task"]
    project_structure = state["project_structure"]
    context = state["context"]
    project_path = state["project_path"]

    final_context = final_context_instruction.format(
        context=context,
        project_structure=project_structure,
        project_path=project_path,
    )

    output_path = os.path.join(os.getcwd(), 'context.txt')
    with open(output_path, 'w', encoding='utf-8') as output_file:
        output_file.write(final_context)
    return {"context": final_context}


async def determine_input_type(state: State):
    """Determine if the user input is a question or a task using the Kimi model"""
    user_input = state["user_task"]

    # Format the prompt with the user input
    formatted_prompt = input_type_determination_prompt.format(
        user_input=user_input
    )

    print("Invoking LLM to determine if input is a question or task...")
    result = await kimi_llm.ainvoke(formatted_prompt)

    # Parse the response to determine if it's a question or task
    response_text = result.content.lower()

    # Simple heuristic: if the response contains "question", classify as question
    if "question" in response_text:
        input_type = "question"
    else:
        input_type = "task"

    print(f"Determined input type: {input_type}")

    return {"input_type": input_type}


async def answer_question(state: State):
    """Answer a question using the Kimi model"""
    user_input = state["user_task"]
    context = state.get("context", "")

    # Format the prompt with the user input and context
    formatted_prompt = answer_question_prompt.format(
        user_input=user_input,
        context=context
    )

    print("Invoking LLM to answer the question...")
    result = await kimi_llm.ainvoke(formatted_prompt)

    # Save the answer to a file
    output_path = os.path.join(os.getcwd(), 'answer.md')
    with open(output_path, 'w', encoding='utf-8') as output_file:
        output_file.write(result.content)

    return {"messages": [HumanMessage(content=result.content)], "answer": result.content}


async def make_plan(state: State):
    """Plan the changes"""
    user_task = state["user_task"]
    context = state.get("context", "")

    instruction = make_plan_instruction.format(
        user_task=user_task,
        context=context,
    )

    result = await kimi_llm.ainvoke(instruction)
    output_path = os.path.join(os.getcwd(), 'example.md')
    with open(output_path, 'w', encoding='utf-8') as output_file:
        output_file.write(result.content)

    plan = result.content.split("</think>")[-1]

    return {"messages": [HumanMessage(content=result.content)], "plan": plan}


async def initialize_web_browser(state: State):
    """Initialize the web browser with a starting URL"""
    user_task = state["user_task"]

    # Default to a search engine if no specific URL is provided
    start_url = "https://duckduckgo.com/"

    # Navigate to the starting URL
    result = await goto_url_helper(start_url)

    # Get the initial page content
    page_content = await get_page_content("")

    return {
        "current_url": start_url,
        "page_content": page_content,
        "action_history": f"Initialized browser and navigated to {start_url}"
    }


async def web_agent_action(state: State):
    """Execute the web agent's action based on the current state"""
    from langchain_core.messages import ToolMessage

    user_task = state["user_task"]
    current_url = state.get("current_url", "")
    page_content = state.get("page_content", "")
    plan = state.get("plan", "")
    action_history = state.get("action_history", "")

    # Get all messages
    all_messages = state.get("messages", [])

    # Update action history with messages
    current_messages_history = "\n".join([str(msg) for msg in all_messages])

    # Get the latest page content before invoking the LLM
    from ..tools.browser_tools import web_tools, get_page_content, browser_session
    # Get the current URL directly from the browser session
    # Make sure browser session is initialized
    if browser_session._initialized and browser_session.page:
        current_url = browser_session.page.url

    latest_page_content = await get_page_content(current_url)

    # Format the web agent instruction with the current state and latest page content
    instruction = web_agent_instruction.format(
        user_task=user_task,
        current_url=current_url,
        page_content=latest_page_content,
        plan=plan,
        current_step="",  # No steps, using the plan directly
        action_history=action_history + "\n" + current_messages_history
    )

    # Invoke the LLM with the web tools
    llm_with_web_tools = gemini_flash.bind_tools(web_tools)
    result = await llm_with_web_tools.ainvoke(instruction)

    # We've already retrieved the latest page content before invoking the LLM,
    # so we don't need to get it again here.
    # The latest_page_content and current_url variables already contain the most up-to-date values.

    return {
        "messages": [result],
        "current_url": current_url,
        "page_content": latest_page_content
    }

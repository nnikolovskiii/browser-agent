from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
import os
import subprocess
from typing import Callable

from agent.core.ai_models import kimi_llm
from bash_client.client import bash_executor

load_dotenv()


@tool
def str_replace(old_str: str, new_str: str, file_path: str) -> str:
    """Replaces text in a file with new text.

    Notes for using the `str_replace` command:
* The `old_str` parameter should match EXACTLY one or more consecutive lines from the original file. Be mindful of whitespaces!
* If the `old_str` parameter is not unique in the file, the replacement will not be performed. Make sure to include enough context in `old_str` to make it unique
* The `new_str` parameter should contain the edited lines that should replace the `old_str`

    Args:
        old_str: The exact text to be replaced in the file
        new_str: The new text that will replace the old text
        file_path: Path to the file where the replacement will be performed

    Returns:
        A message indicating success or failure of the operation
    """
    try:
        with open(file_path, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        return f"Error: The file '{file_path}' was not found."

    # Check for the uniqueness of old_str
    occurrence_count = content.count(old_str)

    if occurrence_count == 0:
        return f"Error: The text to be replaced (old_str) was not found in {file_path}."

    if occurrence_count > 1:
        return f"Error: The text to be replaced (old_str) is not unique in {file_path}. Found {occurrence_count} occurrences."

    # Perform the replacement
    new_content = content.replace(old_str, new_str)

    # Write the new content back to the file
    try:
        with open(file_path, 'w') as f:
            f.write(new_content)
        return f"Successfully replaced text in {file_path}"
    except Exception as e:
        return f"Error writing to file '{file_path}': {e}"


@tool
def run_bash_command(command: str) -> str:
    """Executes a bash command in the terminal.

    This tool allows you to run shell commands and get their output.
    Use it for operations like listing files, checking file content,
    or running system commands.

    Args:
        command: The bash command to execute

    Returns:
        A string containing the combined stdout and stderr of the command.
    """
    return bash_executor.execute(command)


@tool
def create_file(file_path: str, file_text: str) -> str:
    """Creates a new file with the specified content.

    This tool allows you to create new files in the filesystem.
    If the file already exists, it will be overwritten.

    Args:
        file_path: The path where the file should be created
        file_text: The content to write to the file

    Returns:
        A message indicating success or failure of the operation
    """
    try:
        # Ensure parent directories exist
        directory = os.path.dirname(file_path)
        if directory:
            os.makedirs(directory, exist_ok=True)

        with open(file_path, 'w') as f:
            f.write(file_text)
        return f"File '{file_path}' created successfully."
    except Exception as e:
        return f"Error creating file '{file_path}': {e}"


@tool
def view_file(file_path: str) -> str:
    """Reads and returns the content of a file.

    This tool allows you to view the content of any file in the filesystem.
    The entire content of the file will be returned as a string.

    Args:
        file_path: The path to the file to be read

    Returns:
        The content of the file as a string, or an error message if the file cannot be read
    """
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: The file '{file_path}' was not found."
    except Exception as e:
        return f"Error reading file '{file_path}': {e}"


tools = [str_replace, run_bash_command, create_file, view_file]
tools_by_name = {tool.name: tool for tool in tools}
llm_with_tools = kimi_llm.bind_tools(tools)
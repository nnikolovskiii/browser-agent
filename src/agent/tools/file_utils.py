import os
from pathlib import Path
from typing import List

DEFAULT_IGNORE_PATTERNS = {'.git', '.venv', ".idea", ".pytest_cache",
                           '.git', '__pycache__', ".angular",
                           ".github", ".vscode", "dist", "node_modules",
                           ".chainlit", ".files", ".junie", ".langgraph_api"}


def get_project_structure_as_string(folder_path, ignore_patterns=None):
    """
    Generates a tree-like string representation of the project structure for the given folder path,
    excluding files and folders that match the ignore patterns by their basename.

    How to use `ignore_patterns`:
    - To ignore ".venv" IN ADDITION to default ignores ('.git', '__pycache__', '.DS_Store'):
      pass ignore_patterns=ProjectHelper.DEFAULT_IGNORE_PATTERNS.union({".venv"})
    - To ignore ONLY ".venv" and not other defaults:
      pass ignore_patterns={".venv"}
    - To ignore NOTHING (show all, overriding defaults):
      pass ignore_patterns=set()
    - If `ignore_patterns` is None (default), ProjectHelper.DEFAULT_IGNORE_PATTERNS is used.

    Args:
        folder_path (str): The path to the root folder of the project.
        ignore_patterns (set, optional): A set of file or folder basenames to ignore.
                                        Defaults to ProjectHelper.DEFAULT_IGNORE_PATTERNS.

    Returns:
        str: A formatted tree-like string representation of the project structure.
             Returns an error message if folder_path does not exist or is not a directory.
    """

    final_ignore_patterns = DEFAULT_IGNORE_PATTERNS if ignore_patterns is None else ignore_patterns

    if not os.path.exists(folder_path):
        return f"Error: The path '{folder_path}' does not exist."
    if not os.path.isdir(folder_path):
        return f"Error: The path '{folder_path}' is not a directory."

    project_root_name = folder_path

    output_lines = [f"└── {project_root_name}/"]

    structure_map = {}

    for current_root, dir_names, file_names in os.walk(folder_path, topdown=True):

        dir_names[:] = [d for d in dir_names if d not in final_ignore_patterns]

        children_of_current_root = []

        for name in sorted(dir_names):
            children_of_current_root.append((name, True))

        for name in sorted(file_names):
            if name not in final_ignore_patterns:
                children_of_current_root.append((name, False))

        if children_of_current_root:
            structure_map[current_root] = children_of_current_root

    def generate_tree_lines(dir_path_to_scan, current_prefix=""):
        lines = []

        children = structure_map.get(dir_path_to_scan, [])

        for index, (name, is_directory) in enumerate(children):
            is_last_item = (index == len(children) - 1)

            connector = "└── " if is_last_item else "├── "

            prefix_for_next_level = current_prefix + ("    " if is_last_item else "│   ")

            display_name = f"{name}/" if is_directory else name
            lines.append(f"{current_prefix}{connector}{display_name}")

            if is_directory:
                full_child_dir_path = os.path.join(dir_path_to_scan, name)
                lines.extend(generate_tree_lines(full_child_dir_path, prefix_for_next_level))
        return lines

    tree_item_lines = generate_tree_lines(folder_path, "")
    output_lines.extend(tree_item_lines)

    return "\n".join(output_lines)


from pathlib import Path
from typing import List
import re
from pypdf import PdfReader # New import for PDF handling

def read_file(file_path: str) -> str | None:
    """
    Read contents of a file.

    Args:
        file_path (str): Path to the file.

    Returns:
        str: File contents or None if error occurs.
    """
    path = Path(file_path)

    if not path.exists():
        print(f"File does not exist: {path}")
        return None

    if not path.is_file():
        print(f"Path is not a regular file: {path}")
        return None

    try:
        with open(path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Error reading text file {path}: {str(e)}")
        return None

def read_pdf(file_path: str) -> str | None:
    """
    Read contents of a PDF file.

    Args:
        file_path (str): Path to the PDF file.

    Returns:
        str: Extracted text from the PDF or None if error occurs.
    """
    path = Path(file_path)

    if not path.exists():
        print(f"File does not exist: {path}")
        return None

    if not path.is_file():
        print(f"Path is not a regular file: {path}")
        return None

    try:
        reader = PdfReader(path)
        text_content = ""
        for page in reader.pages:
            # Extract text from each page, add a newline for separation
            extracted_text = page.extract_text()
            if extracted_text: # Only add if text was actually extracted
                text_content += extracted_text + "\n"
        return text_content.strip() # Remove trailing newline if any
    except Exception as e:
        print(f"Error reading PDF file {path}: {str(e)}")
        return None

def concat_files_in_str(file_paths: List[str]) -> str:
    """
    Concatenates the contents of specified files (text or PDF) into a single string,
    with titles for each file.

    Args:
        file_paths (List[str]): A list of paths to the files.

    Returns:
        str: A concatenated string of file contents.
    """
    file_title_format = """================================================
FILE: {file_path}
================================================"""
    result = ""

    for file_path in file_paths:
        path_obj = Path(file_path)
        content = None

        if not path_obj.exists():
            print(f"Skipping non-existent path: {file_path}")
            continue

        if path_obj.is_dir():
            print(f"Skipping directory: {file_path}")
            continue

        if path_obj.suffix.lower() == '.pdf':
            content = read_pdf(file_path)
        elif path_obj.is_file(): # Covers .txt, .py, .md, etc.
            content = read_file(file_path)
        else:
            print(f"Skipping unsupported file type or special file: {file_path}")
            continue

        if content is not None:
            file_title = file_title_format.format(
                file_path=file_path
            )
            result += f"{file_title}\n{content}\n\n"

    return result


def concat_folder_to_file(folder_path: str, output_file: str = "concatenated_output.txt", ignore_patterns=None, binary_extensions=None):
    """
    Concatenates all files in a folder (and its subfolders) into a single output file,
    excluding files and folders that match the ignore patterns.

    Args:
        folder_path (str): The path to the folder containing files to concatenate.
        output_file (str, optional): The path to the output file. Defaults to "concatenated_output.txt".
        ignore_patterns (set, optional): A set of file or folder basenames to ignore.
                                        Defaults to DEFAULT_IGNORE_PATTERNS.
        binary_extensions (set, optional): A set of file extensions to treat as binary and skip.
                                          Defaults to {'.pdf', '.png', '.jpg', '.jpeg', '.gif', '.mp3', '.mp4', '.ogg', '.wav', '.zip', '.tar', '.gz'}.

    Returns:
        bool: True if successful, False otherwise.
    """
    final_ignore_patterns = DEFAULT_IGNORE_PATTERNS if ignore_patterns is None else ignore_patterns

    # Default binary file extensions to skip
    default_binary_extensions = {'.pdf', '.png', '.jpg', '.jpeg', '.gif', '.mp3', '.mp4', '.ogg', '.wav', '.zip', '.tar', '.gz'}
    final_binary_extensions = default_binary_extensions if binary_extensions is None else binary_extensions

    if not os.path.exists(folder_path):
        print(f"Error: The path '{folder_path}' does not exist.")
        return False

    if not os.path.isdir(folder_path):
        print(f"Error: The path '{folder_path}' is not a directory.")
        return False

    # Collect all file paths
    file_paths = []
    skipped_binary_files = 0

    for current_root, dir_names, file_names in os.walk(folder_path, topdown=True):
        # Filter out directories that match ignore patterns
        dir_names[:] = [d for d in dir_names if d not in final_ignore_patterns]

        # Filter and collect files that don't match ignore patterns
        for name in file_names:
            if name not in final_ignore_patterns:
                file_path = os.path.join(current_root, name)

                # Skip binary files based on extension
                file_ext = os.path.splitext(name)[1].lower()
                if file_ext in final_binary_extensions:
                    print(f"Skipping binary file: {file_path}")
                    skipped_binary_files += 1
                    continue

                file_paths.append(file_path)

    if not file_paths:
        print(f"No files found in '{folder_path}' after applying ignore patterns and skipping binary files.")
        return False

    # Concatenate all files
    concatenated_content = concat_files_in_str(file_paths)

    # Write to output file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(concatenated_content)
        print(f"Successfully concatenated {len(file_paths)} files to '{output_file}' (skipped {skipped_binary_files} binary files)")
        return True
    except Exception as e:
        print(f"Error writing to output file '{output_file}': {str(e)}")
        return False


def remove_python_comments(folder_path: str, ignore_patterns=None, clean_empty_lines=True):
    """
    Recursively removes all comments from Python files in the specified folder.

    This function:
    1. Finds all .py files in the given folder and its subfolders
    2. Removes all Python comments (# comments) while preserving docstrings
    3. Optionally cleans up consecutive empty lines
    4. Writes the modified content back to the original files

    Args:
        folder_path (str): The path to the folder containing Python files
        ignore_patterns (set, optional): A set of file or folder basenames to ignore.
                                        Defaults to DEFAULT_IGNORE_PATTERNS.
        clean_empty_lines (bool, optional): If True, reduces consecutive empty lines to a single empty line.
                                           Defaults to True.

    Returns:
        tuple: (int, int) - (number of files processed, number of files with errors)
    """
    final_ignore_patterns = DEFAULT_IGNORE_PATTERNS if ignore_patterns is None else ignore_patterns

    if not os.path.exists(folder_path):
        print(f"Error: The path '{folder_path}' does not exist.")
        return (0, 0)

    if not os.path.isdir(folder_path):
        print(f"Error: The path '{folder_path}' is not a directory.")
        return (0, 0)

    # Collect all Python file paths
    python_files = []

    for current_root, dir_names, file_names in os.walk(folder_path, topdown=True):
        # Filter out directories that match ignore patterns
        dir_names[:] = [d for d in dir_names if d not in final_ignore_patterns]

        # Filter and collect Python files that don't match ignore patterns
        for name in file_names:
            if name not in final_ignore_patterns and name.endswith('.py'):
                file_path = os.path.join(current_root, name)
                python_files.append(file_path)

    if not python_files:
        print(f"No Python files found in '{folder_path}' after applying ignore patterns.")
        return (0, 0)

    processed_count = 0
    error_count = 0

    for file_path in python_files:
        try:
            # Read the file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Remove comments while preserving docstrings
            modified_content = remove_comments_from_python_code(content)

            # Clean up consecutive empty lines if requested
            if clean_empty_lines:
                # First, normalize all whitespace-only lines to empty lines
                modified_content = re.sub(r'\n[ \t]+\n', '\n\n', modified_content)
                # Then, replace multiple consecutive empty lines (3 or more) with just one empty line
                modified_content = re.sub(r'\n\n\n+', '\n\n', modified_content)
                # Make sure we don't have empty lines at the beginning or end of the file
                modified_content = modified_content.strip('\n') + '\n'

            # Write the modified content back to the file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(modified_content)

            processed_count += 1
            print(f"Processed: {file_path}")

        except Exception as e:
            print(f"Error processing file '{file_path}': {str(e)}")
            error_count += 1

    print(f"Completed: {processed_count} files processed, {error_count} files with errors")
    return (processed_count, error_count)


def remove_comments_from_python_code(code: str) -> str:
    """
    Removes comments from Python code while preserving docstrings.

    Args:
        code (str): The Python code to process

    Returns:
        str: The code with comments removed
    """
    # State tracking
    in_string = False
    string_char = None
    triple_quotes = False
    i = 0
    result = []

    while i < len(code):
        # Check for string start/end
        if not in_string and (code[i] == "'" or code[i] == '"'):
            in_string = True
            string_char = code[i]

            # Check for triple quotes
            if i + 2 < len(code) and code[i:i+3] == string_char * 3:
                triple_quotes = True
                result.append(code[i:i+3])
                i += 3
                continue
            else:
                triple_quotes = False
                result.append(code[i])
                i += 1
                continue

        # Check for string end
        elif in_string and code[i] == string_char:
            if triple_quotes and i + 2 < len(code) and code[i:i+3] == string_char * 3:
                result.append(code[i:i+3])
                in_string = False
                triple_quotes = False
                i += 3
                continue
            elif not triple_quotes:
                result.append(code[i])
                in_string = False
                i += 1
                continue
            else:
                result.append(code[i])
                i += 1
                continue

        # Handle comments - only if not in a string
        elif not in_string and code[i] == '#':
            # Skip until end of line
            while i < len(code) and code[i] != '\n':
                i += 1
            continue

        # Add character to result
        result.append(code[i])
        i += 1

    return ''.join(result)

print(get_project_structure_as_string("/home/nnikolovskii/dev/reliabl.it/frontend"))
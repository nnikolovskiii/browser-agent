import os
from pathlib import Path
from typing import List, Dict, Tuple, Union

def apply_diff_changes(file_path: str, diff_content: str) -> bool:
    """
    Applies diff notation changes to a file.

    Args:
        file_path (str): Path to the file to be modified.
        diff_content (str): Diff notation content describing the changes to be made.
            Format should follow standard unified diff format:
            - Lines starting with '+' are additions
            - Lines starting with '-' are deletions
            - Lines starting with '@@ -a,b +c,d @@' are headers indicating line numbers
            - Lines without '+' or '-' are context lines

    Returns:
        bool: True if changes were applied successfully, False otherwise.
    """
    path = Path(file_path)

    if not path.exists():
        print(f"File does not exist: {path}")
        return False

    if not path.is_file():
        print(f"Path is not a regular file: {path}")
        return False

    try:
        # Read the original file content
        with open(path, 'r', encoding='utf-8') as file:
            original_lines = file.readlines()

        # Parse the diff content and apply changes
        modified_lines = parse_and_apply_diff(original_lines, diff_content)

        if modified_lines is None:
            print(f"Failed to parse diff content for file: {path}")
            return False

        # Write the modified content back to the file
        with open(path, 'w', encoding='utf-8') as file:
            file.writelines(modified_lines)

        print(f"Successfully applied diff changes to file: {path}")
        return True

    except Exception as e:
        print(f"Error applying diff changes to file {path}: {str(e)}")
        return False

def parse_and_apply_diff(original_lines: List[str], diff_content: str) -> Union[List[str], None]:
    """
    Parses diff content and applies changes to the original lines.

    Args:
        original_lines (List[str]): Original file content as a list of lines.
        diff_content (str): Diff notation content describing the changes.

    Returns:
        Union[List[str], None]: Modified lines if successful, None if parsing failed.
    """
    # Make a copy of the original lines to modify
    modified_lines = original_lines.copy()

    # Split the diff content into lines
    diff_lines = diff_content.splitlines()

    # Process the diff lines
    i = 0
    while i < len(diff_lines):
        line = diff_lines[i]

        # Look for diff header lines like "@@ -a,b +c,d @@"
        if line.startswith("@@"):
            # Parse the header to get line numbers
            try:
                header_parts = line.split("@@")[1].strip().split(" ")
                original_range = header_parts[0]
                modified_range = header_parts[1] if len(header_parts) > 1 else ""

                # Parse original range (format: -a,b)
                if original_range.startswith("-"):
                    original_start, original_count = map(int, original_range[1:].split(","))
                    # Adjust to 0-based indexing
                    original_start -= 1
                else:
                    print(f"Invalid original range format: {original_range}")
                    return None

                # Parse modified range (format: +c,d)
                if modified_range.startswith("+"):
                    modified_start, modified_count = map(int, modified_range[1:].split(","))
                    # Adjust to 0-based indexing
                    modified_start -= 1
                else:
                    print(f"Invalid modified range format: {modified_range}")
                    return None

                # Process the changes in this chunk
                i += 1
                changes = []
                while i < len(diff_lines) and not diff_lines[i].startswith("@@"):
                    changes.append(diff_lines[i])
                    i += 1

                # Apply the changes to the modified_lines
                modified_lines = apply_chunk_changes(modified_lines, original_start, changes)

                # Continue to the next chunk
                continue

            except Exception as e:
                print(f"Error parsing diff header: {line}, Error: {str(e)}")
                return None

        # Skip any other lines (like file names or comments)
        i += 1

    return modified_lines

def apply_chunk_changes(lines: List[str], start_line: int, changes: List[str]) -> List[str]:
    """
    Applies a chunk of diff changes to the lines.

    Args:
        lines (List[str]): Current file content as a list of lines.
        start_line (int): Starting line number (0-based) for the changes.
        changes (List[str]): List of change lines from the diff.

    Returns:
        List[str]: Modified lines after applying the changes.
    """
    result = lines[:start_line]

    i = start_line
    j = 0

    while j < len(changes):
        change = changes[j]

        if change.startswith("+"):
            # Addition: add the new line
            result.append(change[1:] + "\n" if not change[1:].endswith("\n") else change[1:])
        elif change.startswith("-"):
            # Deletion: skip the original line
            i += 1
        else:
            # Context line: keep the original line
            result.append(lines[i])
            i += 1

        j += 1

    # Add remaining lines
    result.extend(lines[i:])

    return result

def create_diff(original_file: str, modified_file: str) -> str:
    """
    Creates a diff between two files.

    Args:
        original_file (str): Path to the original file.
        modified_file (str): Path to the modified file.

    Returns:
        str: Diff notation content describing the changes.
    """
    try:
        # Read the original and modified files
        with open(original_file, 'r', encoding='utf-8') as file:
            original_lines = file.readlines()

        with open(modified_file, 'r', encoding='utf-8') as file:
            modified_lines = file.readlines()

        # Generate the diff
        diff_content = generate_diff(original_lines, modified_lines, original_file, modified_file)

        return diff_content

    except Exception as e:
        print(f"Error creating diff: {str(e)}")
        return ""

def generate_diff(original_lines: List[str], modified_lines: List[str], 
                 original_file: str = "a", modified_file: str = "b") -> str:
    """
    Generates a unified diff between two sets of lines.

    Args:
        original_lines (List[str]): Original file content as a list of lines.
        modified_lines (List[str]): Modified file content as a list of lines.
        original_file (str): Name of the original file for the diff header.
        modified_file (str): Name of the modified file for the diff header.

    Returns:
        str: Unified diff notation content.
    """
    # Simple diff header
    diff_header = f"--- {original_file}\n+++ {modified_file}\n"

    # Find the differences and generate chunks
    chunks = []
    i = 0
    j = 0

    # Ensure lines end with newline
    original_lines = [line if line.endswith('\n') else line + '\n' for line in original_lines]
    modified_lines = [line if line.endswith('\n') else line + '\n' for line in modified_lines]

    while i < len(original_lines) or j < len(modified_lines):
        # Find a difference
        if (i >= len(original_lines) or j >= len(modified_lines) or 
            original_lines[i] != modified_lines[j]):

            # Start a new chunk
            original_start = i + 1  # 1-based indexing for diff
            modified_start = j + 1

            # Collect the changes
            chunk_lines = []

            # Add context lines before (if available)
            context_before = 3
            for k in range(max(0, i - context_before), i):
                if k < len(original_lines) and k < len(modified_lines):
                    chunk_lines.append(" " + original_lines[k].rstrip('\n'))

            # Track original and modified positions
            orig_i = i
            mod_j = j

            # Process differences
            while (orig_i < len(original_lines) or mod_j < len(modified_lines)):
                if (orig_i >= len(original_lines) or mod_j >= len(modified_lines) or 
                    original_lines[orig_i] != modified_lines[mod_j]):

                    # Add deletions from original
                    while orig_i < len(original_lines) and (mod_j >= len(modified_lines) or 
                                                          original_lines[orig_i] != modified_lines[mod_j]):
                        chunk_lines.append("-" + original_lines[orig_i].rstrip('\n'))
                        orig_i += 1

                    # Add additions from modified
                    while mod_j < len(modified_lines) and (orig_i >= len(original_lines) or 
                                                         original_lines[orig_i] != modified_lines[mod_j]):
                        chunk_lines.append("+" + modified_lines[mod_j].rstrip('\n'))
                        mod_j += 1
                else:
                    # Found matching lines, add context and break
                    break

            # Add context lines after (if available)
            context_after = 3
            context_count = 0
            while (orig_i < len(original_lines) and mod_j < len(modified_lines) and 
                   original_lines[orig_i] == modified_lines[mod_j] and 
                   context_count < context_after):
                chunk_lines.append(" " + original_lines[orig_i].rstrip('\n'))
                orig_i += 1
                mod_j += 1
                context_count += 1

            # Update positions for next iteration
            i = orig_i
            j = mod_j

            # Create the chunk header
            original_count = orig_i - original_start + 1
            modified_count = mod_j - modified_start + 1
            chunk_header = f"@@ -{original_start},{original_count} +{modified_start},{modified_count} @@\n"

            # Add the chunk
            if chunk_lines:
                chunks.append(chunk_header + "\n".join(chunk_lines) + "\n")
        else:
            # Lines match, move to next line
            i += 1
            j += 1

    # Combine all chunks
    return diff_header + "".join(chunks)

diff = """--- a/src/pages/ResearchTasksPage.tsx
+++ b/src/pages/ResearchTasksPage.tsx
@@ -1,5 +1,5 @@
 import {useEffect, useState} from 'react';
-import {useParams} from 'react-router-dom';
+import {useParams, useNavigate} from 'react-router-dom';
 import axios from 'axios';
 import {Search, Filter, ArrowUpDown, ArrowUp, ArrowDown, MoreVertical, Edit, Trash2, Check, X} from 'lucide-react';
 import apiClient from "../axios.tsx";
@@ -29,6 +29,7 @@
 
 const ResearchTasksPage = () => {
     const {logAnalysisId} = useParams<{ logAnalysisId: string }>();
+    const navigate = useNavigate();
     const [tasks, setTasks] = useState<ResearchTask[]>([]);
     const [filteredTasks, setFilteredTasks] = useState<ResearchTask[]>([]);
     const [loading, setLoading] = useState<boolean>(true);
@@ -118,6 +119,10 @@
         // Add your edit logic here
     };
 
+    const handleRowClick = (taskId: number) => {
+        navigate(`/research-task/${taskId}`);
+    };
+
     const handleDelete = (task: ResearchTask) => {
         setOpenMenuId(null);
         setTaskToDelete(task);
@@ -194,15 +199,27 @@
                                 <tr><td colSpan={4} className="text-center py-8 text-gray-500">Loading tasks...</td></tr>
                             ) : filteredTasks.length > 0 ? (
                                 filteredTasks.map((task) => (
-                                    <tr key={task.id} className="hover:bg-gray-50 transition-colors duration-150">
+                                    <tr 
+                                        key={task.id}
+                                        onClick={() => handleRowClick(task.id)}
+                                        className="hover:bg-gray-50 transition-colors duration-150 cursor-pointer"
+                                    >
                                         <td className="px-6 py-4 font-medium text-gray-900 max-w-xs"><div className="flex"><span className="truncate" title={task.researchTopic}>{task.researchTopic}</span></div></td>
                                         <td className="px-6 py-4 whitespace-nowrap text-gray-500">{task.updatedAt.toISOString().split('T')[0]}</td>
                                         <td className="px-6 py-4 whitespace-nowrap"><StatusBadge status={task.status}/></td>
                                         <td className="px-6 py-4 whitespace-nowrap text-center">
-                                            <div className="relative">
+                                            {/* Stop propagation to prevent row click when interacting with the menu */}
+                                            <div className="relative" onClick={(e) => e.stopPropagation()}>
                                                 <button onClick={(e) => { e.stopPropagation(); setOpenMenuId(openMenuId === task.id ? null : task.id);}} className="p-1 text-gray-400 hover:text-gray-600 rounded-full hover:bg-gray-100 transition-colors"><MoreVertical className="h-4 w-4"/></button>
                                                 {openMenuId === task.id && (
                                                     <div className="absolute right-0 mt-2 w-32 bg-white rounded-md shadow-lg ring-1 ring-black ring-opacity-5 z-10">
                                                         <div className="py-1">
-                                                            <button onClick={() => handleEdit(task.id)} className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors"><Edit className="h-4 w-4 mr-2"/>Edit</button>
-                                                            <button onClick={() => handleDelete(task)} className="flex items-center w-full px-4 py-2 text-sm text-red-700 hover:bg-red-50 transition-colors"><Trash2 className="h-4 w-4 mr-2"/>Delete</button>
+                                                            <button onClick={() => handleEdit(task.id)} className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors">
+                                                                <Edit className="h-4 w-4 mr-2"/>
+                                                                Edit
+                                                            </button>
+                                                            <button onClick={() => handleDelete(task)} className="flex items-center w-full px-4 py-2 text-sm text-red-700 hover:bg-red-50 transition-colors">
+                                                                <Trash2 className="h-4 w-4 mr-2"/>
+                                                                Delete
+                                                            </button>
                                                         </div>
                                                     </div>
                                                 )}"""

apply_diff_changes("/home/nnikolovskii/dev/reliabl.it/frontend/src/pages/ResearchTasksPage.tsx", diff)
from datetime import datetime


# Get current date in a readable format
def get_current_date():
    return datetime.now().strftime("%B %d, %Y")


input_type_determination_prompt = """You are an AI assistant that determines whether a user input is a question or a task.

Instructions:
- Analyze the user input carefully.
- Determine if the input is asking for information (a question) or requesting an action to be performed (a task).
- Respond with a single word: either "question" or "task".
- If you're unsure, make your best determination based on whether the user seems to be asking for information or requesting an action.

User input:
{user_input}
"""

answer_question_prompt = """You are a helpful AI assistant answering a user's question.

Instructions:
- Provide a clear, concise, and accurate answer to the user's question.
- Use the provided context to inform your answer when relevant.
- If you don't know the answer or the context doesn't provide enough information, say so.

User question:
{user_input}

Context:
{context}
"""


file_planner_instructions = """Your goal is to determine which files need to be searched in order to complete the user's task.

Instructions:
- List all of the files that you think would be relevant for the user's task.
- Write the filepaths the same exact way as in the project structure.
- You must write the whole path: {project_path}

Format: 
- Format your response as a JSON object with ALL of these exact keys:
   - "file_paths": A list of file paths that should be searched
   - "rationale": A brief explanation of why these file_paths could prove relevant to the user's task.

User task:
{user_task}

Project structure: 
{project_structure}"""

file_reflection_instructions = """Your goal is to determine which files need to be searched in order to complete the user's task.

Instructions:
- Suggest any other files that need to be added on top of the existing ones.
- Remove files that are not needed for task. 
- If there is no need, do not add or remove files.
- Write the filepaths the same exact way as in the project structure.
- You must write the whole path: {project_path}

Format: 
- Format your response as a JSON object with ALL of these exact keys:
   - "additional_file_paths": A list of file paths that should be added to the context.
   - "remove_file_paths": A list of file paths that should be removed from the context.

User task:
{user_task}

Project path: {project_path}

Project structure: 
{project_structure}

Fetched files:
{context}
"""

final_instruction = """Your goal is to determine which files need to be searched in order to complete the user's task.

Instructions:
- Suggest any other files that need to be added on top of the existing ones.
- Remove files that are not needed for task. 
- If there is no need, do not add or remove files.
- Write the filepaths the same exact way as in the project structure.
- You must write the whole path: {project_path}

Format: 
- Format your response as a JSON object with ALL of these exact keys:
   - "additional_file_paths": A list of file paths that should be added to the context.
   - "remove_file_paths": A list of file paths that should be removed from the context.

User task:
{user_task}

Project path: {project_path}

Project structure: 
{project_structure}

Fetched files:
{context}
"""

final_context_instruction = """Project path: {project_path}

Project structure: 
{project_structure}

Fetched files:
{context}
"""

make_plan_instruction = """You are a helpful assistant whose job is to create a plan based on the user's task.

Instructions:
- Create a clear, step-by-step plan to accomplish the user's task.
- Your plan should be adaptable to different environments (file system, web browsing, etc.).
- Focus on high-level actions rather than specific implementation details.
- Be concise but comprehensive in your planning.
- Do not provide any recommendations outside the scope of the task.

User task: {user_task}

Context:
{context}
"""

segment_plan_into_steps = """Below is a given plan of actions. Your job is to detect the steps that need to be performed and return them in a JSON object.

Instructions:
- Identify the key steps in the plan that need to be executed.
- Each step should be a clear, actionable item.
- Do not make up or create any steps by yourself.
- Do not provide any recommendations.
- Ensure steps are applicable to any environment (file system, web browsing, etc.).

# Plan:
{plan}
"""

agent_instruction = """You are a helpful assistant which job is to complete the user's task. You will be given the current step that you have to complete, all the previous steps you have completed, and the whole plan you have generated before starting anything.
You will also be given tools if you need to use them.
Below you will be given your action history of the current step for you to know the progress and which step you are at.

# Current step:
{current_step}

# Previous finished steps:
{previous_steps}

# Folder structure:
{project_structure}

# Plan:
{plan}

# Action history:
{action_history}
"""

web_agent_instruction = """You are a capable web browsing assistant. Your goal is to complete the user's task by navigating and interacting with websites.

You have access to a set of tools to control a web browser. After every action, the page content will be updated. Analyze the page content to decide your next step.

# User Task:
{user_task}

# Current URL:
{current_url}

# Current Page Content (HTML):
{page_content}

# Plan:
{plan}

# Current step to execute:
{current_step}

# Action history for this step:
{action_history}

Based on the above, decide which tool to use next to progress on the current step.
"""
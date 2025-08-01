Here is a plan to tackle the task of adding a `main` function to the example scripts.

### Goal
The goal is to refactor the Python example scripts (`exa_example.py` and `openai_example.py`) by encapsulating their logic within a `main` function. This is a standard Python best practice that prevents code from running automatically when the files are imported into other modules, while still allowing them to be executed as standalone scripts.

### Plan

#### Step 1: Refactor `src/monitor_app/examples/exa_example.py`

1.  **Define a `main` function:** Create a new function named `main()`.
2.  **Move the script's logic:** Indent and move all the existing executable code into the `main()` function. This includes loading environment variables, initializing the `Exa` client, defining the task, making the API calls, and printing the result.
3.  **Add the entry point guard:** At the end of the file, add the standard `if __name__ == "__main__":` block.
4.  **Call the `main` function:** Inside the `if` block, call the `main()` function.

**File to be modified:** `/home/nnikolovskii/dev/reliabl.it/monitor-app/src/monitor_app/examples/exa_example.py`

**Pseudocode for changes:**

```python
# Imports remain at the top level
import os
from exa_py import Exa
from flask.cli import load_dotenv

def main():
    # All the executable logic goes here
    load_dotenv()
    exa = Exa(os.environ["EXA_API_KEY"])

    # Create a research task
    instructions = "Summarize the history of San Francisco..."
    schema = { ... }

    task = exa.research.create_task(...)
    result = exa.research.poll_task(task.id)
    print(result)

# Add the entry point to run the main function
if __name__ == "__main__":
    main()
```

---

#### Step 2: Refactor `src/monitor_app/examples/openai_example.py`

This step follows the exact same pattern as Step 1.

1.  **Define a `main` function:** Create a `main()` function in the script.
2.  **Move the script's logic:** Indent and move the executable code (loading dotenv, initializing the client, defining the input, making the API call, and printing the output) into the new `main()` function.
3.  **Add the entry point guard:** Add the `if __name__ == "__main__":` block at the end of the script.
4.  **Call the `main` function:** Call `main()` from within the `if` block.

**File to be modified:** `/home/nnikolovskii/dev/reliabl.it/monitor-app/src/monitor_app/examples/openai_example.py`

**Pseudocode for changes:**

```python
# Imports remain at the top level
from openai import OpenAI
from dotenv import load_dotenv
import os
from openai.types import Reasoning, ReasoningEffort

def main():
    # All the executable logic goes here
    load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(timeout=3600, api_key=openai_api_key)

    input_text = """Your job is to research..."""

    response = client.responses.create(...)

    print(response.output_text)

# Add the entry point to run the main function
if __name__ == "__main__":
    main()
```

By following this plan, both example scripts will be updated according to Python best practices, improving the project's structure and code quality.
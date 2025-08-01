# Web Agent with Playwright

This project extends the existing file-based agent architecture to create a web-based agent using Playwright. The web agent can navigate and interact with websites, performing tasks like searching for information, clicking on elements, and filling out forms.

## Features

- **Browser Session Management**: A singleton `BrowserSession` class that persists across tool calls
- **Session Persistence**: Login information, cookies, and browser state are saved between runs using a persistent user data directory
- **Web Tools**: A set of tools for interacting with web pages (goto_url, click_element, fill_text, get_page_content)
- **State Management**: Adapted state to track web browsing context (current_url, page_content, etc.)
- **Web Agent Instruction**: A prompt template specifically designed for web browsing tasks
- **Web Agent Graph**: A LangGraph workflow for web browsing tasks

## Usage

To use the web agent, run the following command:

```bash
python src/agent/run_web_graph.py
```

This will start the web agent with a default task to search for information about 'langchain agents' and summarize the first result.

To use your own task, modify the `user_task` variable in `src/agent/run_web_graph.py`.

## Implementation Details

The web agent is implemented as an extension of the existing agent architecture:

1. **Browser Tools (`src/agent/tools/browser_tools.py`)**: A set of tools for interacting with web pages using Playwright.
2. **State Adaptation (`src/agent/core/state.py`)**: The `State` class is adapted to include web-specific fields like `current_url` and `page_content`.
3. **Web Agent Instruction (`src/agent/prompts/prompts.py`)**: A new prompt template `web_agent_instruction` is added for web browsing tasks.
4. **Web Agent Nodes (`src/agent/core/graph.py`)**: New nodes `initialize_web_browser` and `web_agent_action` are added for web browsing.
5. **Web Agent Graph (`src/agent/core/configs.py`)**: A new function `web_explore_plan_action()` is added to create a graph for web browsing tasks.
6. **Web Agent Runner (`src/agent/run_web_graph.py`)**: A new file to run the web agent.

## Switching Between Agents

To switch between the file-based agent and the web-based agent, modify the `optimizer_builder` variable in `src/agent/core/configs.py`:

```python
# For file-based agent:
optimizer_builder = explore_plan_action()
# For web-based agent:
# optimizer_builder = web_explore_plan_action()
```

## Dependencies

- Playwright: `pip install playwright`
- After installation, you need to install the browser binaries: `playwright install`

## Session Persistence

The web agent is configured to persist login information and cookies between runs. This means that if you log in to a website during one run, you will remain logged in for subsequent runs until you explicitly log out or clear the user data directory.

### How it works

- The browser session uses a persistent user data directory located at `~/.playwright_user_data`
- This directory stores cookies, localStorage, sessionStorage, and other browser state
- When you restart the agent, it will reuse this data, maintaining your login sessions

### Clearing session data

If you need to clear the session data and start fresh:

```bash
rm -rf ~/.playwright_user_data
```

This will remove all saved login information and cookies, requiring you to log in again on the next run.

## Browser Security Configuration

The browser is configured to bypass common security checks that might prevent automated browsers from logging in to certain websites (like Google). The configuration includes:

- Setting a realistic user agent string
- Disabling automation flags
- Setting a common desktop viewport size
- Bypassing Content Security Policy
- Handling JavaScript dialogs automatically
- Setting appropriate HTTP headers
- Using JavaScript to mask automation indicators

These configurations help ensure that you can log in to most websites without encountering security warnings or being blocked as an automated browser.

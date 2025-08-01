from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
import asyncio

import sys
sys.path.insert(0, '/home/nnikolovskii/dev/ai_task_agent')
from src.agent.core.configs import web_explore_plan_action

# Create the web agent graph
web_graph = web_explore_plan_action().compile()

# Define a web browsing task
user_task = """Search for information about 'langchain agents' and summarize the first result."""

config = RunnableConfig(recursion_limit=250)

# Run the web agent using the async API
async def main():
    state = await web_graph.ainvoke(
        {
            "user_task": user_task,
            "messages": HumanMessage(content=user_task),
        },
        config=config
    )
    return state

# Run the async main function
if __name__ == "__main__":
    asyncio.run(main())

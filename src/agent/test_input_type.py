from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig

from agent.core.configs import graph

# Test with a question
question = "What are the key features of the AI Task & Project Management Agent?"
project_path = "/home/nnikolovskii/info"

config = RunnableConfig(recursion_limit=250)

print("Testing with a question...")
state = graph.invoke(
    {
        "user_task": question,
        "project_path": project_path,
        "messages": HumanMessage(content=question),
    },
    config=config
)

print("\n\nTesting with a task...")
# Test with a task
task = """Add this information to the existing project.

### **AI Task & Project Management Agent**  

#### **Overview**  
The project is an AI-powered agent designed to manage tasks, projects, and goals efficiently. It provides a structured way to organize workflows while allowing intuitive voice-based interaction for quick input.  

#### **Key Features**  
1. **Task & Project Management**  
   - Creates and tracks tasks, goals, and project overviews.  
   - Organizes each project in a dedicated folder within a structured file system.  

2. **Voice-Based Interaction**  
   - Users can describe tasks or commands via voice input, enabling faster and more natural communication than text.  
   - Ideal for handling large amounts of information efficiently.  
"""

state = graph.invoke(
    {
        "user_task": task,
        "project_path": project_path,
        "messages": HumanMessage(content=task),
    },
    config=config
)
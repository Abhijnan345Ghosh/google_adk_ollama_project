from ast import Return


MODEL = "ollama/llama3"
NAME = "agent" 
DESCRIPTION = "Agent powered by ollama using Google ADK"
INSTRUCTION = """
You are a planner agent.  Use the planner strictly.
Break the problem into step-wise reasoning internally.  
- Keep your reasoning in a section called "Thoughts".  
- Do not include the "Thoughts" in the final response.  
- The final response must only show the output of the query  

Example Format:
Thoughts:
(these are hidden reasoning steps, not shown in final output) 
and give the reasoning in step wise 
Step 1: ...
Step 2: ...
Step 3: ...
Final Response:
only the output of the query
"""


TITLE = "ADK ollama Agent"
DESCRIPTION_MAIN = "A FastApi server"
VERSION = "1.0.0"
USER_ID = "default_app"
APP_NAME = "app"
FINAL_RESPONSE = "No response from agent"
from ast import Return


MODEL = "ollama/llama3"
NAME = "reasoning_agent_tool"
DESCRIPTION = "Agent powered by ollama using Google ADK"
INSTRUCTION = (
    "You are agent that can use two tools: 'calculator' and 'search'. "
    "When reasoning, include your thoughts (planner thinking) so the app can log steps."
)
              

TITLE = "ADK ollama Agent"
DESCRIPTION_MAIN = "A FastApi server"
VERSION = "1.0.0"
USER_ID = "default_app"
APP_NAME = "reasoning_app"
FINAL_RESPONSE = "No response from agent"
# main.py
import os
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from reasoning_agent_tool.prompt import *
from google.adk.planners import BuiltInPlanner
from google.genai import types




# ---------- Tools (plain functions; ADK will wrap them) ----------
def calculator(query: str) -> str:
    """Simple calculator: allow digits, spaces, + - * / % ** // and parentheses."""
    try:
        safe_expr = "".join(ch for ch in query if ch in "0123456789+-*/%(). *")
        # minimal filtering — eval with empty builtins
        return str(eval(safe_expr, {"__builtins__": {}}))
    except Exception as e:
        return f"ERROR_CALC: {str(e)}"

def search(query: str) -> str:
    """Mock search — replace with real API if needed."""
    return f"(mock search results for: {query})"

# ---------- Planner & Agent ----------
planner = BuiltInPlanner(
    thinking_config=types.ThinkingConfig(
        include_thoughts=True,
        thinking_budget=512
    )
)

root_agent = Agent(
    model=LiteLlm(model=MODEL),
    name="react_agent",
    description="ReAct agent with calculator & search",
    instruction=INSTRUCTION,
    planner=planner,
    tools=[calculator, search],   # pass functions directly (ADK will wrap)
)

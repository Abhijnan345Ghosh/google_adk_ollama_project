import os
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from reasoning_agent.prompt import *
from google.adk.planners import BuiltInPlanner
from google.genai import types

planner = BuiltInPlanner(
    thinking_config=types.ThinkingConfig(
        include_thoughts=True,
        thinking_budget=1024
    )
)

root_agent = Agent(
    model = LiteLlm(model = MODEL),
    name = NAME,    
    description= DESCRIPTION,
    instruction = INSTRUCTION,
    planner = planner,
    tools = []
)
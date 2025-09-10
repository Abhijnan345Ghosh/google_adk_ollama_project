import os
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from reasoning_agent.prompt import *
from google.adk.planners import PlanReActPlanner
from google.genai import types
from reasoning_agent.model import *


root_agent = Agent(
    model = LiteLlm(model = MODEL),
    name = NAME,    
    description= DESCRIPTION,
    instruction = INSTRUCTION,
    planner = PlanReActPlanner(),
    tools = []
)
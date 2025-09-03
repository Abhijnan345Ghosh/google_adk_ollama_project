import os
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from greeting_agent.prompt import *

root_agent = Agent(
    model = LiteLlm(model = MODEL),
    name = NAME,    
    description= DESCRIPTION,
    instruction = INSTRUCTION,
    tools = []
)
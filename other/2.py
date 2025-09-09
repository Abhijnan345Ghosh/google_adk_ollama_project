# main.py
import os
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.planners import BuiltInPlanner
from google.genai import types

# Your exact prompt configuration
MODEL = "ollama/llama3"
NAME = "reasoning_agent_tool" 
DESCRIPTION = "Agent powered by ollama using Google ADK"
INSTRUCTION = (
    "You are agent that can use two tools: 'calculator' and 'search'. "
    "When reasoning, include your thoughts (planner thinking) so the app can log steps."
)

# Additional constants
TITLE = "ADK ollama Agent"
DESCRIPTION_MAIN = "A FastApi server"
VERSION = "1.0.0"
USER_ID = "default_app"
APP_NAME = "reasoning_app"
FINAL_RESPONSE = "No response from agent"

# ---------- Tools (plain functions; ADK will wrap them) ----------
def calculator(query: str) -> str:
    """Simple calculator: allow digits, spaces, + - * / % ** // and parentheses."""
    try:
        # Clean and validate the expression
        allowed_chars = "0123456789+-*/%(). "
        safe_expr = "".join(ch for ch in query if ch in allowed_chars)
        safe_expr = safe_expr.strip()
        
        if not safe_expr:
            return "ERROR_CALC: Empty expression"
        
        # Evaluate safely
        result = eval(safe_expr, {"__builtins__": {}})
        return f"Result: {result}"
    except Exception as e:
        return f"ERROR_CALC: {str(e)}"

def search(query: str) -> str:
    """Mock search — replace with real API if needed."""
    return f"Search results for '{query}': [Mock data - replace with real search API]"

# ---------- Create Agent with Proper Error Handling ----------
def create_agent():
    """Create the reasoning agent with proper configuration"""
    try:
        print(f"Creating agent with MODEL: {MODEL}")
        print(f"Agent NAME: {NAME}")
        
        # Configure planner
        planner = BuiltInPlanner(
            thinking_config=types.ThinkingConfig(
                include_thoughts=True,
                thinking_budget=1024
            )
        )
        
        # Create agent - IMPORTANT: Use a different variable name than the module
        agent = Agent(
            model=LiteLlm(model=MODEL),
            name="reasoning_assistant",  # Changed to avoid conflicts
            description=DESCRIPTION,
            instruction=INSTRUCTION,
            planner=planner,
            tools=[calculator, search],
        )
        
        print("✓ Agent created successfully!")
        return agent
        
    except Exception as e:
        print(f"✗ Error creating agent: {e}")
        import traceback
        traceback.print_exc()
        return None

# Create the agent
reasoning_agent_tool = create_agent()

# Verification
if reasoning_agent_tool:
    print(f"Agent ready with {len(reasoning_agent_tool.tools)} tools")
    
    # Test tools
    print("\n--- Testing Tools ---")
    print("Calculator:", calculator("5 + 3"))
    print("Search:", search("test query"))
else:
    print("Failed to create agent - check your configuration")

# ============================================================================
# FastAPI Server Implementation
# ============================================================================

from fastapi import FastAPI
from pydantic import BaseModel
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

# Request/Response models
class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    response: str

# Initialize FastAPI and ADK components
session_service = InMemorySessionService()

if reasoning_agent_tool:
    runner = Runner(
        agent=reasoning_agent_tool,
        app_name=APP_NAME,
        session_service=session_service
    )

app = FastAPI(
    title=TITLE,
    description=DESCRIPTION_MAIN,
    version=VERSION
)

# Routes
@app.get("/health")
async def health_check():
    return {"status_message": "ok", "status_code": 200}

@app.post("/reason_chat", response_model=QueryResponse)
async def reasoning_agent_endpoint(req: QueryRequest):
    if not reasoning_agent_tool:
        return QueryResponse(response="Agent not initialized properly")
    
    try:
        user_id = USER_ID
        final_response = ""
        thoughts = ""
        
        # Create session
        session = await session_service.create_session(
            user_id=user_id,
            app_name=APP_NAME
        )
        
        # Create message that encourages reasoning
        reasoning_query = f"Think step by step and show your reasoning: {req.query}"
        
        user_message = types.Content(
            role="user",
            parts=[types.Part(text=reasoning_query)]
        )
        
        # Run agent
        events = runner.run_async(
            new_message=user_message,
            user_id=user_id,
            session_id=session.id
        )
        
        print("=== Processing Agent Events ===")
        
        async for event in events:
            print(f"\nEvent type: {type(event).__name__}")
            print(f"Event: {event}")
            
            # Extract content
            if hasattr(event, 'content') and event.content:
                if hasattr(event.content, 'parts') and event.content.parts:
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            text = part.text
                            
                            # Check if it's thinking content
                            if hasattr(part, 'thought') and part.thought:
                                thoughts += text + "\n"
                                print(f"THOUGHT: {text}")
                            else:
                                # Look for reasoning patterns in regular text
                                if any(keyword in text.lower() for keyword in 
                                      ['step 1', 'step 2', 'thinking', 'reasoning', 'because', 'therefore']):
                                    thoughts += text + "\n"
                                    print(f"REASONING: {text}")
                                else:
                                    final_response += text + "\n"
                                    print(f"RESPONSE: {text}")
            
            if event.is_final_response():
                print(">>> Final response event detected <<<")
        
        # Combine thoughts and response
        result = final_response.strip()
        if thoughts.strip():
            result = f"Reasoning Process:\n{thoughts.strip()}\n\nFinal Answer:\n{result}"
        
        print(f"\n=== FINAL OUTPUT ===")
        print(f"Thoughts: {thoughts}")
        print(f"Response: {final_response}")
        
        return QueryResponse(response=result or "No response generated")
        
    except Exception as e:
        print(f"Error in reasoning endpoint: {e}")
        import traceback
        traceback.print_exc()
        return QueryResponse(response=f"Error: {str(e)}")

@app.get("/agent_info")
async def get_agent_info():
    """Get information about the agent configuration"""
    if reasoning_agent_tool:
        return {
            "agent_name": reasoning_agent_tool.name,
            "model": MODEL,
            "tools_count": len(reasoning_agent_tool.tools),
            "planner_configured": reasoning_agent_tool.planner is not None,
            "status": "active"
        }
    else:
        return {
            "status": "error",
            "message": "Agent not initialized"
        }

if __name__ == "__main__":
    import uvicorn
    print(f"Starting {TITLE} server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
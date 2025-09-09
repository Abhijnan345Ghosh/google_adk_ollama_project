# agent.py
import os
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from reasoning_agent.prompt import *
from google.adk.planners import BuiltInPlanner
from google.genai import types

# Configure the planner with proper thinking settings
planner = BuiltInPlanner(
    thinking_config=types.ThinkingConfig(
        include_thoughts=True,
        thinking_budget=1024
    )
)

# Simple reasoning tools to encourage planner usage
def analyze_problem(problem: str) -> str:
    """Analyze a problem step by step"""
    return f"Breaking down the problem: {problem}"

def make_decision(options: str) -> str:
    """Help make decisions between options"""
    return f"Evaluating options: {options}"

root_agent = Agent(
    model=LiteLlm(model=MODEL),
    name=NAME,    
    description=DESCRIPTION,
    instruction=INSTRUCTION + "\n\nAlways think through problems step by step before responding. Use your reasoning capabilities to break down complex questions.",
    planner=planner,
    tools=[analyze_problem, make_decision]  # Add some tools to encourage reasoning
)

# main.py
from fastapi import FastAPI
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from reasoning_agent.reasoning_agent import root_agent
from reasoning_agent.prompt import *
from reasoning_agent.model import *

session_service = InMemorySessionService()

runner = Runner(
    agent=root_agent,
    app_name=APP_NAME,
    session_service=session_service
)

app = FastAPI(
    title=TITLE,
    description=DESCRIPTION_MAIN,
    version=VERSION
)

# -- Routes --

@app.get("/health")
async def health_check():
    return {"status_message": "ok", "status_code": 200}

# Enhanced endpoint for the reasoning agent
@app.post("/reason_chat", response_model=QueryResponse)
async def reasoning_agent(req: QueryRequest):
    user_id = USER_ID
    final_response = ""
    thoughts = ""
    app_name = APP_NAME
    
    try:
        # Create session
        session = await session_service.create_session(
            user_id=user_id,
            app_name=app_name
        )
        
        # Create user message with reasoning prompt
        reasoning_prompt = f"""
        Please think through this step by step and show your reasoning process:
        
        {req.query}
        
        Break down your thinking process before providing the final answer.
        """
        
        user_message = types.Content(
            role="user",
            parts=[types.Part(text=reasoning_prompt)]
        )
        
        # Run the agent
        events = runner.run_async(
            new_message=user_message,
            user_id=user_id,
            session_id=session.id
        )
        
        print("=== Processing Agent Response ===")
        
        async for event in events:
            print(f"\n--- EVENT TYPE: {type(event).__name__} ---")
            print(f"Event: {event}")
            
            # Check for different event types
            if hasattr(event, 'content') and event.content:
                print(f"Content available: {event.content}")
                
                if hasattr(event.content, 'parts') and event.content.parts:
                    for i, part in enumerate(event.content.parts):
                        print(f"\nPart {i}:")
                        print(f"  Type: {type(part)}")
                        print(f"  Text: {getattr(part, 'text', 'No text')}")
                        
                        # Check for thinking/thoughts
                        if hasattr(part, 'thought') and part.thought:
                            print(f"  >> THOUGHT FOUND: {part.text}")
                            thoughts += part.text + "\n"
                        elif hasattr(part, 'text') and part.text:
                            # Check if the text contains reasoning patterns
                            text = part.text.lower()
                            if any(keyword in text for keyword in ['thinking', 'reasoning', 'step by step', 'let me think', 'analysis']):
                                print(f"  >> REASONING CONTENT: {part.text}")
                                thoughts += part.text + "\n"
                            else:
                                print(f"  >> FINAL RESPONSE: {part.text}")
                                final_response += part.text + "\n"
            
            # Check if it's the final response
            if event.is_final_response():
                print(">>> FINAL EVENT DETECTED <<<")
                
                # Try to extract thinking content from the final response
                if hasattr(event, 'content') and event.content:
                    if hasattr(event.content, 'parts'):
                        for part in event.content.parts:
                            if hasattr(part, 'text') and part.text:
                                # Look for thinking patterns in the text
                                if "thinking:" in part.text.lower() or "reasoning:" in part.text.lower():
                                    thoughts += part.text + "\n"
                                else:
                                    final_response += part.text + "\n"
        
        # If we didn't get explicit thoughts, check if the response contains reasoning
        if not thoughts and final_response:
            lines = final_response.split('\n')
            reasoning_lines = []
            answer_lines = []
            
            for line in lines:
                if any(keyword in line.lower() for keyword in ['step 1', 'step 2', 'first,', 'then,', 'therefore,', 'because', 'reasoning']):
                    reasoning_lines.append(line)
                else:
                    answer_lines.append(line)
            
            if reasoning_lines:
                thoughts = '\n'.join(reasoning_lines)
                final_response = '\n'.join(answer_lines)
        
        print(f"\n=== FINAL RESULTS ===")
        print(f"Thoughts: {thoughts}")
        print(f"Response: {final_response}")
        
        # Return response with thoughts if available
        response_text = final_response.strip()
        if thoughts.strip():
            response_text = f"Reasoning:\n{thoughts.strip()}\n\nAnswer:\n{response_text}"
        
        return QueryResponse(response=response_text or "No response generated")
    
    except Exception as e:
        print(f"Error in reasoning agent: {e}")
        import traceback
        traceback.print_exc()
        return QueryResponse(response=f"Error processing request: {str(e)}")

# Additional endpoint to test planner functionality
@app.post("/test_reasoning")
async def test_reasoning():
    """Test endpoint to verify reasoning capabilities"""
    test_query = "What is 25 * 17 and why is this calculation important in mathematics?"
    
    user_id = "test_user"
    session = await session_service.create_session(
        user_id=user_id,
        app_name=APP_NAME
    )
    
    user_message = types.Content(
        role="user",
        parts=[types.Part(text=f"Think step by step: {test_query}")]
    )
    
    events = runner.run_async(
        new_message=user_message,
        user_id=user_id,
        session_id=session.id
    )
    
    response_parts = []
    async for event in events:
        if hasattr(event, 'content') and event.content and hasattr(event.content, 'parts'):
            for part in event.content.parts:
                if hasattr(part, 'text') and part.text:
                    response_parts.append(part.text)
    
    return {"test_response": " ".join(response_parts), "planner_active": bool(root_agent.planner)}
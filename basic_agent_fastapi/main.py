from fastapi import FastAPI
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from greeting_agent.greeting_agent import root_agent
from greeting_agent.prompt import *
from greeting_agent.model import *

session_service = InMemorySessionService()

runner = Runner(
    agent = root_agent,
    app_name=APP_NAME,
    session_service=session_service
)

app = FastAPI(
    title = TITLE,
    description=DESCRIPTION_MAIN, 
    version=VERSION
)

#-- Routes -- 
@app.get("/health")
async def health_check():
    return {"status_message": "ok","status_code": 200}

# Endpoint for the greeting agent
@app.post("/greet", response_model=QueryResponse)
async def greeting_agent(req: QueryRequest):
    user_id = USER_ID
    final_response = FINAL_RESPONSE
    app_name = APP_NAME

    session = await session_service.create_session(
        user_id=user_id, 
        app_name=app_name
    )

    user_message = types.Content(
        role = "user",
        parts = [types.Part(text = req.query)]
    )

    events = runner.run_async(
        new_message  = user_message,
        user_id = user_id,
        session_id = session.id
    )

    async for event in events:
        if event.is_final_response():
            if event.content and event.content.parts:
                final_response = event.content.parts[0].text
                print(f"Agent Response", final_response)

    return QueryResponse(response = final_response)
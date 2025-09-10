import uuid
from fastapi import FastAPI
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from reasoning_agent.agent import root_agent
from reasoning_agent.prompt import *
from reasoning_agent.model import *

SESSION_ID = str(uuid.uuid4())
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

# Endpoint for the reasoning agent
@app.post("/reason_chat", response_model=QueryResponse)
async def reasoning_agent(req: QueryRequest):
    user_id = USER_ID
    final_response = FINAL_RESPONSE
    app_name = APP_NAME

    session = await session_service.create_session(
        user_id=user_id, 
        app_name=app_name,
        session_id=SESSION_ID
    )

    user_message = types.Content(
        role = "user",
        parts = [types.Part(text = req.query)]
    )

    events = runner.run_async(
        new_message  = user_message,
        user_id = user_id,
        session_id=SESSION_ID
    )

    """Here when trying to divide the thoughts and final response, the response was commming in 2 parts and 
    hence the split was not happening correctly."""
    # async for event in events:
    #     if event.is_final_response():
    #         if event.content and event.content.parts:
    #             print("========================================================================")
    #             print(f"Actual Response: \n{event.content.parts}")
    #             print("========================================================================")

    #             raw_text = event.content.parts[0].text
    #             if "FINAL_ANSWER" in raw_text:
    #                 thoughts, final_response = raw_text.split("FINAL_ANSWER", 1)
    #                 thoughts = thoughts.strip()
    #                 final_response = final_response.strip()
    #             else:
    #                 thoughts = raw_text.strip()
    #                 final_response = ""

    #             print(f"Agent Thoughts: \n{thoughts}")
    #             print("========================================================================")
    #             print(f"Agent Response: \n{final_response}")
    #             print("========================================================================")


    # return QueryResponse(thoughts=thoughts, response=final_response)

    async for event in events:

        if event.is_final_response():
            if event.content and event.content.parts:
                print("========================================================================")
                print(f"Actual Response: \n{event.content.parts}")
                print("========================================================================")
                #print(event.content.parts.thoughts)
                final_response = event.content.parts[0].text
                print(f"Agent Response", final_response)

    return QueryResponse(response=final_response)



        
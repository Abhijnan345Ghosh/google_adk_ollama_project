from fastapi import FastAPI
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from reasoning_agent_tool.reasoning_agent import reasoning_agent_tool
from reasoning_agent_tool.prompt import *
from reasoning_agent_tool.model import *

session_service = InMemorySessionService()

runner = Runner(
    agent = reasoning_agent_tool,
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

    # async for event in events:

    #     if event.is_final_response():
    #         if event.content and event.content.parts:
    #             print(event.content.parts.thoughts)
    #             final_response = event.content.parts[0].text
    #             print(f"Agent Response", final_response)

    thoughts = ""
    final_response = ""

    async for event in events:
        print(f"\nDEBUG EVENT: {event}\n")
        if event.is_final_response():
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if not part.text:
                        continue
                    elif getattr(part, "thought", False):  # check if it's a thought
                        if not thoughts:
                            print("Thoughts summary:")
                        print(part.text)
                        thoughts += part.text
                    else:
                        if not final_response:
                            print("Answer:")
                        print(part.text)
                        final_response += part.text
    print("Thoughts Summary:", thoughts)
    print("Final Response:", final_response)

    return QueryResponse(response=final_response)



        
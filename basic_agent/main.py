from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from greeting_agent.agent import root_agent
from greeting_agent.prompt import *
from greeting_agent.model import *
import asyncio
import uuid
SESSION_ID = str(uuid.uuid4())

async def greeting_agent(req: QueryRequest):
    user_id = USER_ID
    final_response = FINAL_RESPONSE
    app_name = APP_NAME

    session_service = InMemorySessionService()
    
    session = await session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=SESSION_ID
    )
    print("========================================================================")
    print("Session ID:", session.id)
    print("========================================================================")


    # Runner for the greeting agent
    runner = Runner(
        agent=root_agent,
        app_name=app_name,
        session_service=session_service
    )


    user_message = types.Content(
        role = "user",
        parts = [types.Part(text = req.query)]
    )
    
    # run the agent
    events = runner.run_async(
        new_message  = user_message,
        user_id = USER_ID,
        #session_id = session.id
        session_id = SESSION_ID
    )

    # print the response
    async for event in events:
        if event.is_final_response():
            final_response = event.content.parts[0].text
            print(f"Agent Response", final_response)

    session = await session_service.get_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID
    )

    print("========================================================================")
    print("\n\n\nSession Details:", session)
    print("========================================================================")
    print("\n\n\nSession Eevents:", session.events)
    print("========================================================================")
    print("\n\n\nSession ID:", session.id)
    print("========================================================================")
    print("\n\n\nSession state:", session.state)
    print("========================================================================")
    for key, value in session.state.items():
        print(f"{key}: {value}")

    return QueryResponse(response=final_response)

if __name__ == "__main__":
    req = QueryRequest(query="What is the advantage of using google adk")
    asyncio.run(greeting_agent(req))


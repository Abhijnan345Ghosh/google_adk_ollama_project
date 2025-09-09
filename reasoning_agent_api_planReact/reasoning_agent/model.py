from pydantic import BaseModel, Field

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    thoughts: str = Field(
        description="The agent's reasoning process and intermediate steps taken to arrive at the final response.")
    response: str = Field(
        description="A brief summary of the core issues identified from the user's query.")
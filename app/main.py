from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.agentic_systeem import front_desk_agent 
from openai.types.responses import ResponseTextDeltaEvent
from agents import  Runner
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator
from pydantic import BaseModel
from typing import List, Dict, AsyncGenerator
from uuid import uuid4
from app.config_gemni import model_gemini, config
from app.zip_code_finder import zip_code_finder_agent 

app : FastAPI = FastAPI(
    title="Zipi AI",
    description="A friendly assistant to help you find internet providers in your area.",
    version="1.0.0",
)
origins = [
    "http://localhost:3000",
    "https://your-production-domain.com",
    "https://gen-002.asdev.tech"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

# @app.get("/call")
# async def read_call(message: str):
#     """
#     This endpoint is a placeholder for the call functionality.
#     """
#     result = Runner.run_streamed(front_desk_agent, input=message)
#     async for event in result.stream_events():
#         if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
#             print(event.data.delta, end="", flush=True)
#             result = event.data.delta
#     return result

# @app.get("/call")
# async def read_call(message: str):
#     """
#     This endpoint streams the response as chunks are generated.
#     """
#     # conversation = []

#     async def event_generator() -> AsyncGenerator[str, None]:
#         conversation = []

#         conversation.append({"role": "user", "content": message})
#         result = Runner.run_streamed(front_desk_agent, input=conversation)
#         async for event in result.stream_events():
#             if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
#                 chunk = event.data.delta
#                 yield chunk  # send each chunk as it comes

#     return StreamingResponse(event_generator(), media_type="text/plain")

# In-memory store for chat history (replace with database for production)
chat_sessions: Dict[str, List[Dict[str, str]]] = {}

class Message(BaseModel):
    content: str
    session_id: str = None  # Optional session ID for chat continuity
    
@app.post("/call")
async def process_message(message: Message) -> StreamingResponse:
    try:
        # Generate or use session ID for chat history
        session_id = message.session_id or str(uuid4())
        
        # Retrieve or initialize chat history
        history = chat_sessions.get(session_id, [])
        
        # Append user's message to history
        history.append({"role": "user", "content": message.content})
        
        async def event_generator() -> AsyncGenerator[str, None]:
            response_content = ""
            # Run the agent with streaming
            result = Runner.run_streamed(front_desk_agent, input=history)
            print("result", result)
            
            # Stream response chunks
            async for event in result.stream_events():
                if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                    chunk = event.data.delta
                    response_content += chunk
                    yield chunk
            
            # Append assistant's response to history
            history.append({"role": "assistant", "content": response_content})
            
            # Update chat history in store
            chat_sessions[session_id] = history        
        return StreamingResponse(
            event_generator(),
            media_type="text/plain",
            headers={"X-Session-ID": session_id}
        )
    
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    

class Coordinates(BaseModel):
    lat: float
    lon: float
# coords: Coordinates
@app.post("/coordinates")
async def get_coordinates(Coordinates: Coordinates):
    result = await Runner.run(
         zip_code_finder_agent,
        [{"role":"user" , "content" : f"my pin location is {Coordinates.lat}, {Coordinates.lon}"}],
        run_config=config,

        )
    # print(result.final_output.zip_code)
    
    return result.final_output


# uv run uvicorn app.main:app --reload
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
from app.model import ZipData
from app.zip_code_finder import zip_code_finder_agent 
from app.testing_systeem import front_desk_agent_updated
import json
from fastapi.responses import JSONResponse
import pymysql



app : FastAPI = FastAPI(
    title="Zipi AI",
    description="A friendly assistant to help you find internet providers in your area.",
    version="1.0.3",
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
DB_CONFIG = {
    "host": "localhost",
    "user": "nearme_us",
    "password": "nearme&j417Btt5",
    "database": "internet_nrearme",
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor
}

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

@app.post("/providers")
async def get_providers(content: str):
    # print("content", content)
    try:
        result = await Runner.run(
            front_desk_agent_updated,
            [{"role": "user", "content": content}],
        )
        data = json.loads(result.final_output)  # Parse the JSON string
        return JSONResponse(content=data)       # Return valid JSON

    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
# uv run uvicorn app.main:app --reload




# Function to get database connection
def get_db_connection():
    return pymysql.connect(**DB_CONFIG)

@app.get("/zip/{zip_code}", response_model=List[ZipData])
async def get_zip_data(zip_code: str):
    # Validate ZIP code (basic check for 5 digits)
    if not zip_code.isdigit() or len(zip_code) != 5:
        raise HTTPException(status_code=400, detail="ZIP code must be a 5-digit number")
    
    try:
        # Connect to the database
        connection = get_db_connection()
        with connection.cursor() as cursor:
            # Query to fetch data for the given ZIP code
            sql = "SELECT * FROM us_zip WHERE zip = %s"
            cursor.execute(sql, (zip_code,))
            result = cursor.fetchall()
        
        # Check if data was found
        if not result:
            raise HTTPException(status_code=404, detail=f"No data found for ZIP code {zip_code}")
        
        # Convert result to list of ZipData objects
        return [ZipData(**item) for item in result]
    
    except pymysql.MySQLError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    finally:
        connection.close()



@app.get("/providers/by_zip/{zip_code}")
async def get_providers_by_zip(zip_code: str):
    # Validate ZIP code (basic check for 5 digits)
    if not zip_code.isdigit() or len(zip_code) != 5:
        raise HTTPException(status_code=400, detail="ZIP code must be a 5-digit number")
    
    try:
        # Connect to the database
        connection = get_db_connection()
        with connection.cursor() as cursor:
            # Query to fetch providers for the given ZIP code
            sql = "SELECT providers FROM by_zip WHERE zip = %s"
            cursor.execute(sql, (zip_code,))
            result = cursor.fetchone()
        
        # Check if data was found
        if not result:
            raise HTTPException(status_code=404, detail=f"No providers found for ZIP code {zip_code}")
        
        # Parse the providers JSON string into a Python dict
        providers_data = json.loads(result['providers'])
        return providers_data
    
    except pymysql.MySQLError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid providers data format")
    finally:
        connection.close()
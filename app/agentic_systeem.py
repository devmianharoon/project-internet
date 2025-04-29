from agents import Agent, Runner, function_tool,WebSearchTool
from agents import set_default_openai_key 
from openai.types.responses import ResponseTextDeltaEvent
from app.tool import get_providers
from app.instruction import instructions

from dotenv import load_dotenv
import os
import asyncio

load_dotenv()
set_default_openai_key(os.getenv('OPENAI_API_KEY'))
search_agent = Agent(
    name="Web Search Agent",
    instructions=instructions,
    tools=[WebSearchTool()],
)
front_desk_agent = Agent(
    name="Internat Packages Provider",
    instructions=instructions,
    handoffs=[search_agent],
    handoff_description="Search the web for information about internet packages.",
    model="gpt-4",
    # tools=[get_providers],

)
# prompt = """
# The Best Internet Near Me {10034}.,"""
# result = Runner.run_sync(
#     front_desk_agent,
#     prompt,
# )
# print(result)
# print("raw resposne /n ",result.raw_responses)
# print("new itesm /n",result.new_items)
# print("tools /n ",result.last_agent)

# async def main():
#     result  = Runner.run_streamed(
#         front_desk_agent,
#         "hi what about you  "
#     )
#     print(result)
#     async for event in result.stream_events():
#         if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
#             print(event.data.delta, end="", flush=True)

# asyncio.run(main())
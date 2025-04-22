from agents import Agent, Runner
from pydantic import BaseModel
from app.config_gemni import model_gemini



class ZipCode(BaseModel):
    zip_code: int


zip_code_finder_agent: Agent = Agent(
    name="Zip Code Finder",
    instructions="This agent is responsible for finding zip codes based on pin location like lat and long.",
    tools=[],
    output_type=ZipCode,
    model=model_gemini,
)
# code = """


# 36.227517, -115.271882



# """
# result = Runner.run_sync(
#     zip_code_finder_agent,
#     [{"role":"user" , "content" : "my pin location is 36.285786, -115.208437"}],
#         run_config=config,
#     )
# print(result)
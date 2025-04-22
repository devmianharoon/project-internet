from dotenv import load_dotenv
import os
from agents import  AsyncOpenAI, OpenAIChatCompletionsModel
from agents.run import RunConfig

load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")
base_url = os.getenv("BASE_URL")
model = os.getenv("MODEL")

if not gemini_api_key:
    print(gemini_api_key)
    raise ValueError("GEMINI_API_KEY is not set. Please ensure it is defined in your .env file.")

external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url=base_url,
)
model_gemini = OpenAIChatCompletionsModel(
    model=model,
    openai_client=external_client,
)
config = RunConfig(
    model=model_gemini,
    model_provider=external_client,
    tracing_disabled=True,
)
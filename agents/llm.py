from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("API_KEY")

llm = ChatOpenAI(
    api_key = api_key,
    base_url="https://openrouter.ai/api/v1",
    model="openrouter/free",
    temperature=0.5
)
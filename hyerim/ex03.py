from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langgraph.prebuilt import create_react_agent
import os

load_dotenv()
os.environ["LANGCHAIN_TRACING_V2"] = 'true'
os.environ["LANGCHAIN_ENDPOINT"] = os.getenv("LANGCHAIN_ENDPOINT")
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT")
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
CHATROUTER = os.getenv("OPENROUTER")
BASE_URL = os.getenv("OPENROUTER_API_BASE")

llm = ChatOpenAI(
    api_key= CHATROUTER,
    base_url = BASE_URL,
    model= "google/gemini-2.5-flash-lite",
    temperature=0.5
)

def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"


agent = create_react_agent(
    model=llm,
    tools=[get_weather],
    prompt="You are a helpful assistant.",
)

# Run the agent
agent.invoke(
    {"messages": [{"role": "user", "content": "What is the weather in San Francisco?"}]}
)

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
from operator import itemgetter
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
    model= "google/gemini-2.5-flash",
    temperature=0.5
)

prompt_text = """you are a assistant you have to 'answer' the 'question'

            you have to follow below examples:
            
            Example1
            what are you doing?
            내가 너가 뭐하는지 어떻게 알아?
            
            Here is the question:
            {question}

            """
prompt = ChatPromptTemplate.from_template(prompt_text)
chain = {"question":itemgetter("question")} | prompt | llm | StrOutputParser()

response = chain.invoke({"question":"where are you?"})
print(response)
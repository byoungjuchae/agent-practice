# 예시 코드

from langchain_openai import ChatOpenAI # LangChain OpenAI 모델 사용
from langchain.prompts import ChatPromptTemplate # 프롬프트 템플릿 사용
from langchain_core.output_parsers import StrOutputParser # 출력 파서 사용
from dotenv import load_dotenv # 환경 변수 로드
from operator import itemgetter # 아이템 가져오기 사용
import os # 환경 변수 사용

load_dotenv() # 환경 변수 로드

# 환경 변수 설정
os.environ["LANGCHAIN_TRACING_V2"] = 'true'
os.environ["LANGCHAIN_ENDPOINT"] = os.getenv("LANGCHAIN_ENDPOINT")
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT")
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
CHATROUTER = os.getenv("OPENROUTER") 
BASE_URL = os.getenv("OPENROUTER_API_BASE") 

# 모델 설정
llm = ChatOpenAI(
    api_key= CHATROUTER,
    base_url = BASE_URL,
    model= "google/gemini-2.5-flash-lite",
    temperature=0.5
)

# 프롬프트 템플릿 설정
prompt_text = """you are a assistant you have to answer the question.

            Here is the question:
            {question}

            """
prompt = ChatPromptTemplate.from_template(prompt_text) # 프롬프트 템플릿 설정
chain = {"question":itemgetter("question")} | prompt | llm | StrOutputParser() # 체인 설정

response = chain.invoke({"question":"what do you do?"})

# 응답 출력
print(response)
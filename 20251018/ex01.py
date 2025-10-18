#create_react_agent 활용하여 Agent 만들어보기
import random
import os

from operator import itemgetter
from typing import Any

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.tools import tool

load_dotenv()
os.environ["LANGCHAIN_TRACING_V2"] = 'true'
os.environ["LANGCHAIN_ENDPOINT"] = os.getenv("LANGCHAIN_ENDPOINT")
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT")
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
CHATROUTER = os.getenv("OPENROUTER")
BASE_URL = os.getenv("OPENROUTER_API_BASE")

model = ChatOpenAI(
    api_key=CHATROUTER,
    base_url=BASE_URL,
    model= "anthropic/claude-sonnet-4.5",
    temperature=0.5 #0이 비창의적 1이 창의적
)


@tool
def random_dice(dice_count : int) -> list[Any]:
    "너는 사용자가 주사위를 사용할 때 사용하는 tool이야. argument인 dice_count는 주사위를 던질 횟수야. "
    dice_value_str = []
    for x in range(dice_count) :
        dice = random.randint(1,6)
        dice_value_str.append(str(dice))

    return dice_value_str



if __name__ == "__main__":

    agent = create_agent(
        model=model,
        tools=[random_dice]  # 함수의 이름 list 형태로 넣으면 됨.
    )

    define_prompt = """ 너는 사용자를 도와주는 assistant야 ReAct 로 이루어져있고 tool이 등록되어있어
        너는 random_dice tool을 사용 할 수 있어. 
        - 주사위를 던지고싶을때 사용하는 함수야    

        here is the user_question:
        {question}
        """

    prompt = ChatPromptTemplate.from_template(define_prompt)
    chain = {"question": itemgetter("question")} | prompt | agent
    response = chain.invoke({"question": "주사위 갯수는 3개야"})
    print(response)


import os
import asyncio
from typing_extensions import TypedDict, NotRequired
from dotenv import load_dotenv
from operator import itemgetter
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langgraph.graph import StateGraph, END

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
    temperature=0.5
)

class State(TypedDict) :
    region : str
    today : NotRequired[str]
    user_prompt : str
    answer : NotRequired[str]

async def today(state: State) :
    define_prompt = """당신은 사용자에게 날짜를 알려주는 에이전트입니다.
    사용자가 "날짜"와 관련된 질문을 하면 시스템 날짜가 아닌 사용자가 실제 현실세계 날짜를 정확히 알려주세요.
    "한국" 일경우엔 한국 날짜만 "미국" 일경우엔 미국날짜만 "둘다"일 경우겐 양쪽 나라의 시간 모두 알려주세요.
    
    region : {region}
    """

    prompt = ChatPromptTemplate.from_template(define_prompt)
    chain = {"region": itemgetter("region")} | prompt | model | StrOutputParser()
    today = await chain.ainvoke({"region": state["region"]})
    return {"today": today.strip()}


async def influencer(state : State) :
    define_prompt = """너는 인플루언서 생일축하 봇이야.
     사용자들에게 한국과 미국의 연예인들 생일 질문을 받으면 답변해줘야하고 오늘 생일인 연예인도 알려줘야해
     답변은 예시를 보여줄게
     
     예시1) 질문:"오늘 생일인 연예인이 누구야 ? "
     답변: "오늘 생일인 연예인은 한국의 개그맨 전현무과 미국의 배우 스칼렛 요한슨입니다.
     전현무는 kbs공채 1기 출신으로 ~~한 이력을 쌓았습니다. 스칼렛 요한슨은 할리우드 배우로 유명작으론 Lucy 와 어벤져스가 있습니다.
     
     예시2) 질문: "오늘 생일인 한국 연예인이 누구야 ? "
     답변: "오늘 생일인 한국 연예인은 전현무 입니다
     - 내용은 위와 같음-
     
     위처럼 특정 나라를 정하고 물어보면 그 나라에 해당하는 연예인의 생일만 검색해서 알려주면 되.
     
     예시3) 질문 : "오늘과 가장 가까운 날이 생일인 연예인을 알려줘"
     답변 : "다가오는 생일이 가장 가까운 연예인은 전지현입니다
     전지현은 한국의 배우로 다수의 영화 및 드라마에 출현했습니다.
     
     가장 가까운 생일인 연예인도 알려줘.
     
     모든 답변의 연예인은 최대 4명을 넘지 않도록 알아서 조절해주고
     항상 한국의 연예인 먼저 말해줘.
     
     아래는 사용자 입력이야.
     
     region : {region}
     today : {today}
     user_prompt : {user_prompt}
     """

    prompt = ChatPromptTemplate.from_template(define_prompt)

    chain = {"user_prompt": itemgetter("user_prompt"), "today" : itemgetter("today"), "region":itemgetter("region")} | prompt | model | StrOutputParser()
    answer = await chain.ainvoke(state)

    return {"answer": answer.strip()}


graph_builder = StateGraph(State)
graph_builder.add_node("today", today)
graph_builder.add_node("influencer", influencer)

graph_builder.add_edge("today", "influencer")
graph_builder.set_entry_point("today")
graph_builder.add_edge("influencer", END)

graph = graph_builder.compile()

async def main():
    init_state: State = {"region": "한국", "user_prompt": "오늘 생일인 연예인은 누구야?"}
    final_state = await graph.ainvoke(init_state)

    print("\n[질문]")
    print(final_state["user_prompt"])
    print("\n[답변]")
    print(final_state["answer"])



if __name__ == "__main__":
    asyncio.run(main())


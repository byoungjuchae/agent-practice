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
from datetime import datetime, timedelta, timezone

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
    today : NotRequired[datetime]
    user_prompt : str
    answer : NotRequired[str]

async def today(state: State) :

    global today
    define_prompt = """당신은 사용자에게 국가를 입력받아 정규화 해주는 에이전트입니다.
    사용자에게 "국가" 를 어떤 언어로든 입력받으면 해당 국가명을 "한국어로" 번역해서 알려주세요.
    다른거 다 필요없이 오롯이 나라이름만 답변해
    '한국', '미국', '중국', '일본' 식으로 접두사 접미사 다 제외
    
    예시1) 대한민국 관련 -> '한국' , 미국 관련 -> '미국', 중국 관련 -> '중국'
    
    region : {region}
    """

    prompt = ChatPromptTemplate.from_template(define_prompt)
    chain = {"region": itemgetter("region")} | prompt | model | StrOutputParser()
    region = await chain.ainvoke({"region": state["region"]})
    # import pdb; pdb.set_trace()
    if region == "한국" :

        KST = timezone(timedelta(hours=9))
        today = datetime.now(KST).strftime("%Y-%m-%d")
    elif region =="미국" :
        UST = timezone(timedelta())
        today = datetime.now(UST).strftime("%Y-%m-%d")

    return {"today": today}


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




# ===== 5) 실행 예시 =====
async def main():
    init_state: State = {"region": "korea", "user_prompt": "오늘 생일인 연예인은 누구야?"}
    final_state = await graph.ainvoke(init_state)

    print("\n[질문]")
    print(final_state["user_prompt"])
    print("\n[답변]")
    print(final_state["answer"])



if __name__ == "__main__":
    asyncio.run(main())


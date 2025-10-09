import os
import asyncio
from dotenv import load_dotenv
from typing_extensions import TypedDict, NotRequired
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

llm = ChatOpenAI(
    api_key= CHATROUTER,
    base_url = BASE_URL,
    model= "google/gemini-2.5-flash-lite",
    temperature=0.5
)

class SwarmState(TypedDict):
    a: int
    b: int
    problem: NotRequired[str]
    solution: NotRequired[str]


async def create_math(state: SwarmState) :
    prompt_text = """당신은 간단하고 명확한 수학 문제를 만드는 어시스턴트입니다.
    - 입력으로 두 정수 a, b가 주어집니다.
    - a, b를 활용한 단일 문제를 한 문장으로 만드세요.
    - 계산으로 풀 수 있고, 모호하지 않으며, 정답이 하나여야 합니다.
    - 출력은 문제 문장만, 다른 말 없이.

    예시:
    - "두 수 12와 5의 (합 × 차)를 구하시오."  # 예시는 예시일 뿐. 당신은 a, b로 새로운 문제를 만드세요.

    입력:
    a = {a}
    b = {b}
    """

    prompt = ChatPromptTemplate.from_template(prompt_text)
    chain = {"a": itemgetter("a"), "b": itemgetter("b")} | prompt | llm | StrOutputParser()
    problem = await chain.ainvoke({"a": state["a"], "b": state["b"]})
    return {"problem": problem.strip()}

async def solve(state: SwarmState):
    prompt_text = """당신은 문제 풀이 어시스턴트입니다.
    아래의 수학 문제를 풀이하되, 간단한 계산 과정 후 마지막 줄에
    "정답: <값>" 형식으로 최종 수치만 제시하세요.

    문제:
    {problem}
    """

    prompt = ChatPromptTemplate.from_template(prompt_text)
    chain = {"problem": itemgetter("problem") | RunnablePassthrough()} | prompt | llm | StrOutputParser()
    solution = await chain.ainvoke({"problem": state["problem"]})
    return {"solution": solution.strip()}


graph_builder = StateGraph(SwarmState)
graph_builder.add_node("create_math", create_math)
graph_builder.add_node("solve", solve)

graph_builder.add_edge("create_math", "solve")
graph_builder.set_entry_point("create_math")
graph_builder.add_edge("solve", END)

graph = graph_builder.compile()


# ===== 5) 실행 예시 =====
async def main():
    # 사용자가 두 숫자 입력 (예: 12와 5)
    init_state: SwarmState = {"a": 2, "b": 2}
    final_state = await graph.ainvoke(init_state)

    print("\n[생성된 문제]")
    print(final_state["problem"])
    print("\n[풀이/결과]")
    print(final_state["solution"])

if __name__ == "__main__":
    asyncio.run(main())
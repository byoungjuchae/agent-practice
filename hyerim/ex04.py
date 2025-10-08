from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import AIMessage
from langgraph.graph import StateGraph
from langgraph.types import Command
from tools_cover.llm_type import llm, collection
from .util.total_state import SwarmState
from typing_extensions import TypedDict
from operator import itemgetter
import base64

async def planner_tool(state:SwarmState):    
    prompt_text = """You are a planner of the cover letter and analyzing portfolio, JD, CV etc. 
                    You have to plan the user's query based on the user's input.
                    you also consider about the jd check result.
                    
                    you can use two agent systems and each agent's tools to run the user's query.
                    
                    <agent> 
                    1. analyze agent: This agent can analyze the CV, JD, portfolio. CV, JD, and portfolio are ready to use.
                    you don't have a process of gathering CV, JD, and portfolio.
                    - Here is the analyze agent's tools:
                    - analyze_resume: This agent can analyze the resume or CV. you have a resume to use this tool and result is the resume analysis.
                    - analyze_JD: This agent can analyze the JD. you have a JD analysis to use this tool. JD analysis is not the input of this tool. but it must need to use prompt.
                  
                    
                    2. writing agent: This agent can write the cover letter and rewrite the CV.
                    - Here is the writing agent's tools:
                    - writer: This agent can write the cover letter based on the CV and JD analysis.
                    - CV_Re: This agent can rewrite the CV based on the JD analysis and CV.
                    </agent>
                    
                    
                    Here is the user's input:
                    {user_input}
                    
                    Here is the jd check result:
                    {jd_check}
                    
                    think step by step and make a plan."""
                     
    prompt = ChatPromptTemplate.from_template(prompt_text)
    
    chain = {"user_input": itemgetter("user_input") | RunnablePassthrough(), "jd_check": itemgetter("jd_check") | RunnablePassthrough()} | prompt | llm | StrOutputParser()
    
    user_input = collection.find_one({"_id":state['id']}, {"user_input": 1, "_id": 0}).get("user_input", "No user input found")

    response = await chain.ainvoke({"user_input": user_input,"jd_check": state['jd_check']})
    
    collection.update_one({"_id": state['id']}, {"$set": {"plan": response}}, upsert=True)    

    state['response'] = response
    
    state['messages'][-1] AIMessage(content=response)
    
    return Command(goto='workflow_compile', 
                   update={state["id"]:state['id'],
                           state["messages"]:state['messages']})

async def check_jd(state:SwarmState):

    prompt_text = """You are a JD checker. You have to check the JD and previous JD are similar job and company.

                    Here is the JD:
                    {JD}
    
                    Here is the previous JD:
                    {previous_JD}
                    
                    you answer the only 'YES' or 'NO'
                    """

    previous_JD = collection.find_one({"_id": state['id']}, {"JD_analysis": 1, "_id": 0}).get("JD_analysis", "No JD analysis found")
    job_description = collection.find_one({"_id": state['id']}, {"job_description": 1, "_id": 0}).get("job_description", "No job description found") 
    prompt = ChatPromptTemplate.from_template(prompt_text)

    chain = {"JD": itemgetter("JD") | RunnablePassthrough(), "previous_JD": itemgetter("previous_JD") | RunnablePassthrough()} | prompt | llm | StrOutputParser()

    response = await chain.ainvoke({"JD": job_description, "previous_JD": previous_JD})

    collection.update_one({"_id": state['id']}, {"$set": {"jd_check": response}}, upsert=True)

    state['jd_check'] = response
    
    return state

planner_graph_builder = StateGraph(SwarmState)
planner_graph_builder.add_node("check_jd",check_jd)
planner_graph_builder.add_node("planner_tool",planner_tool)
planner_graph_builder.add_edge("check_jd","planner_tool") # 노드 2개 연결
planner_graph_builder.set_entry_point("check_jd") # 시작점 
planner_graph = planner_graph_builder.compile()                     
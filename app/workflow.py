from __future__ import annotations

import os
from typing import Any, Literal

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import create_react_agent
from langgraph.types import Command
from typing_extensions import Annotated, TypedDict

from .prompts import system_prompt
from .tools import (
    cancel_appointment,
    check_availability_by_doctor,
    check_availability_by_specialization,
    reschedule_appointment,
    set_appointment,
)


class Router(TypedDict):
    next: Literal["information_node", "booking_node", "FINISH"]
    reasoning: str


class AgentState(TypedDict):
    messages: Annotated[list[Any], add_messages]
    id_number: int
    next: str
    query: str
    current_reasoning: str


load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
if openai_api_key:
    os.environ["OPENAI_API_KEY"] = openai_api_key

openai_model = ChatOpenAI(model="gpt-4o")


def supervisor_node(state: AgentState) -> Command[Literal["information_node", "booking_node", "__end__"]]:
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"user's identification number is {state['id_number']}"},
    ] + state["messages"]

    query = ""
    if len(state["messages"]) == 1:
        query = state["messages"][0].content

    response = openai_model.with_structured_output(Router).invoke(messages)
    goto = response["next"]

    if goto == "FINISH":
        goto = END

    if query:
        return Command(
            goto=goto,
            update={
                "next": goto,
                "query": query,
                "current_reasoning": response["reasoning"],
                "messages": [HumanMessage(content=f"user's identification number is {state['id_number']}")],
            },
        )

    return Command(goto=goto, update={"next": goto, "current_reasoning": response["reasoning"]})


def information_node(state: AgentState) -> Command[Literal["supervisor"]]:
    information_prompt = (
        "You are specialized agent to provide information related to availability of doctors or any FAQs related to hospital based on the query. "
        "You have access to the tool. Make sure to ask user politely if you need any further information to execute the tool. "
        "For your information, Always consider current year is 2024."
    )

    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", information_prompt),
            ("placeholder", "{messages}"),
        ]
    )

    information_agent = create_react_agent(
        model=openai_model,
        tools=[check_availability_by_doctor, check_availability_by_specialization],
        prompt=prompt_template,
    )

    result = information_agent.invoke(state)

    return Command(
        update={"messages": state["messages"] + [AIMessage(content=result["messages"][-1].content, name="information_node")]},
        goto="supervisor",
    )


def booking_node(state: AgentState) -> Command[Literal["supervisor"]]:
    booking_prompt = (
        "You are specialized agent to set, cancel or reschedule appointment based on the query. "
        "You have access to the tool. Make sure to ask user politely if you need any further information to execute the tool. "
        "For your information, Always consider current year is 2024."
    )

    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", booking_prompt),
            ("placeholder", "{messages}"),
        ]
    )
    booking_agent = create_react_agent(
        model=openai_model,
        tools=[set_appointment, cancel_appointment, reschedule_appointment],
        prompt=prompt_template,
    )

    result = booking_agent.invoke(state)

    return Command(
        update={"messages": state["messages"] + [AIMessage(content=result["messages"][-1].content, name="booking_node")]},
        goto="supervisor",
    )


def build_workflow():
    graph = StateGraph(AgentState)
    graph.add_node("supervisor", supervisor_node)
    graph.add_node("information_node", information_node)
    graph.add_node("booking_node", booking_node)
    graph.add_edge(START, "supervisor")
    return graph.compile()

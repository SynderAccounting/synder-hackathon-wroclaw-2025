from typing import Annotated
from typing import List

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.sessions import StreamableHttpConnection
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import AnyMessage, add_messages
from langgraph.prebuilt import tools_condition, ToolNode
from typing_extensions import TypedDict

from agent.agent_config import AGENT_LLM
from prompts.chat_system_prompt import CHAT_SYSTEM_PROMPT

GRAPH_MEMORY = MemorySaver()

MCP_SERVER_CLIENT = MultiServerMCPClient(
    {
        "shopify": StreamableHttpConnection(url="http://localhost:8001/mcp", transport="streamable_http"),
    }
)


async def create_graph(*sessions):
    tools = []
    for session in sessions:
        tool_set = await load_mcp_tools(session)
        tools.extend(tool_set)

    llm_with_tool = AGENT_LLM.bind_tools(tools)

    prompt_template = ChatPromptTemplate.from_messages([
        ("system", CHAT_SYSTEM_PROMPT),
        MessagesPlaceholder("messages")
    ])
    chat_llm = prompt_template | llm_with_tool

    class State(TypedDict):
        messages: Annotated[List[AnyMessage], add_messages]

    async def chat_node(state: State) -> State:
        state["messages"] = await chat_llm.ainvoke({"messages": state["messages"]})
        return state

    agent_workflow = (
        StateGraph(State)

        .add_node("chat_node", chat_node)
        .add_node("tool_node", ToolNode(tools=tools))

        .add_edge(START, 'chat_node')

        .add_conditional_edges(
            'chat_node',
            tools_condition,
            {"tools": "tool_node", "__end__": END}
        )
        .add_edge('tool_node', 'chat_node')
    )

    graph = agent_workflow.compile(checkpointer=GRAPH_MEMORY)
    return graph

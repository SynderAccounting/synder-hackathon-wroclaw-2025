import json
from typing import Optional

from langchain_core.messages import AIMessage, ToolMessage, HumanMessage
from starlette.websockets import WebSocket

from agent.graph import GRAPH_MEMORY, MCP_SERVER_CLIENT, create_graph
from configs.logger import LOGGER
from exceptions.agent_exceptions import GeneralAgentException
from schemas.websocket import UserRequest, BotResponse


class AgentChatHandler:
    def __init__(self, user_request: UserRequest, websocket: WebSocket):
        self.user_request = user_request
        self.websocket = websocket

    async def handle_request(self) -> Optional[BotResponse]:
        config = {
            "configurable": {
                "thread_id": self.user_request.session_id
            },
            "checkpoint": GRAPH_MEMORY,
        }
        last_message = None
        try:
            async with MCP_SERVER_CLIENT.session("shopify") as shopify_session:
                agent = await create_graph(shopify_session)
                async for name, mode, chunk in agent.astream(
                        {"messages": self.user_request.text},
                        subgraphs=True,
                        config=config,
                        stream_mode=["custom", "values"]
                ):
                    if mode == "custom":
                        pass
                    elif mode == "values":
                        last_message = next(iter(chunk.values()))
                    else:
                        LOGGER.error(f"Unexpected mode: {mode}")
                if isinstance(last_message[-1], AIMessage):
                    index = 0
                    for _ in range(5):
                        try:
                            if isinstance(last_message[-(index + 2)], ToolMessage):
                                res = json.loads(last_message[-(index + 2)].content)
                                if 'image' in res:
                                    await self.websocket.send_json(res)
                            elif isinstance(last_message[-(index + 2)], HumanMessage):
                                break
                        except Exception:
                            pass
                        finally:
                            index += 1
                    return BotResponse(text=last_message[-1].content)
        except Exception as ex:

            LOGGER.error(f"Error in AgentChatHandler: {ex}")
            raise GeneralAgentException(ex)

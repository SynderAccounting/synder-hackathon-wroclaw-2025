"""Chat service for managing conversations and LLM interactions."""

import os
from typing import Dict
from sqlalchemy.sql import text
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage
from langchain_core.chat_history import InMemoryChatMessageHistory
from sqlalchemy.ext.asyncio import AsyncSession

from .tools import get_tools
from .provider_registry import MODEL_PROVIDERS


class ChatService:
    """Service for managing chat sessions and LLM interactions."""

    def __init__(self):
        self.chat_histories: Dict[str, InMemoryChatMessageHistory] = {}

    def get_chat_model(self):
        """Get the configured LLM model with tools."""
        model_provider = os.getenv("MODEL_PROVIDER", "openai").lower()
        model_name = os.getenv("MODEL_NAME", "gpt-4o")
        streaming = True

        tools = get_tools()

        factory = MODEL_PROVIDERS.get(model_provider)
        if not factory:
            raise ValueError(f"Unsupported model provider: {model_provider}")

        llm = factory(model_name, streaming)
        return llm.bind_tools(tools)

    def get_session_history(self, session_id: str) -> InMemoryChatMessageHistory:
        """Get or create chat history for a session."""
        if session_id not in self.chat_histories:
            self.chat_histories[session_id] = InMemoryChatMessageHistory()

            # Add system message
            self.chat_histories[session_id].add_message(
                SystemMessage(
                    content=(
                        "You are a helpful AI assistant for an e-commerce merchant. "
                        "You have the ability to recall and refer to the entire conversation. "
                        "When a user asks what they said before or references a past message, "
                        "use the provided chat history to answer accurately. "
                        "\n\n"
                        "IMPORTANT - DATABASE STRUCTURE:\n"
                        "- The person you're talking to is a MERCHANT (store owner)\n"
                        "- CUSTOMERS are people who buy from the merchant\n"
                        "- ORDERS are placed by customers on the merchant's store\n"
                        "- Database schema: merchants → customers → orders → order_items\n"
                        "\n"
                        "When the merchant asks 'how many orders do I have?' they mean:\n"
                        "- Orders placed by THEIR customers (not orders the merchant placed elsewhere)\n"
                        "- Query the orders table (which automatically filters to this merchant's data via RLS)\n"
                        "\n"
                        "Available tables:\n"
                        "- merchants: The app users (store owners)\n"
                        "- customers: People who buy from merchants (linked via merchant_id)\n"
                        "- products: Product catalog owned by merchants (linked via merchant_id)\n"
                        "- orders: Purchases made by customers (linked via customer_id)\n"
                        "- order_items: Line items in orders (references products via product_id)\n"
                        "- addresses: Billing/shipping addresses\n"
                        "- fulfillments: Shipment tracking\n"
                        "- discounts: Discount codes\n"
                        "\n"
                        "IMPORTANT - Product vs Order Items:\n"
                        "- products table = product catalog (e.g., 'Gray Socks' exists ONCE)\n"
                        "- order_items = references products in orders with quantity\n"
                        "- To see what was sold, JOIN order_items with products\n"
                        "- Example: If someone bought 2 Gray Socks twice, that's 2 order_items both referencing the same product\n"
                        "\n"
                        "Use tools as often as possible when they would be helpful. "
                        "Remember - you can check the database directly, no need to ask the merchant. "
                        "UNDER NO CIRCUMSTANCES should you tell the user what SQL queries you ran."
                    )
                )
            )

        return self.chat_histories[session_id]

    def clear_session_history(self, session_id: str) -> bool:
        """Clear chat history for a session."""
        if session_id in self.chat_histories:
            del self.chat_histories[session_id]
            return True
        return False

    async def process_message(
        self,
        message: str,
        session_id: str,
        db_session: AsyncSession,
        on_token=None,
        on_tool_call=None,
        on_tool_result=None,
        on_error=None,
        on_plot_created=None,
    ) -> str:
        """
        Process a user message and return the AI response.

        Args:
            message: User message
            session_id: Chat session ID
            db_session: Database session for tool calls
            on_token: Callback for streaming tokens
            on_tool_call: Callback when a tool is called
            on_tool_result: Callback when a tool returns
            on_error: Callback for errors

        Returns:
            Complete AI response text
        """
        try:
            llm = self.get_chat_model()
            tools_dict = {tool.name: tool for tool in get_tools()}

            history = self.get_session_history(session_id)
            history.add_message(HumanMessage(content=message))

            messages = history.messages
            full_response = ""

            max_iterations = 10
            iteration = 0

            while iteration < max_iterations:
                iteration += 1
                current_response = AIMessage(content="")
                tool_calls = []
                chunks = []

                # Stream the response
                async for chunk in llm.astream(messages):
                    chunks.append(chunk)

                    if chunk.content:
                        current_response.content += chunk.content
                        full_response += chunk.content

                        # Call token callback
                        if on_token:
                            await on_token(chunk.content)

                # Check for tool calls
                if chunks:
                    merged_chunk = chunks[0]
                    for chunk in chunks[1:]:
                        merged_chunk += chunk

                    if hasattr(merged_chunk, 'tool_calls') and merged_chunk.tool_calls:
                        tool_calls = [tc for tc in merged_chunk.tool_calls if tc.get('id') is not None]

                # If no tool calls, we're done
                if not tool_calls:
                    break

                # Add AI message with tool calls to history
                current_response = AIMessage(content=current_response.content, tool_calls=tool_calls)
                history.add_message(current_response)

                # Execute tool calls
                for tool_call in tool_calls:
                    tool_name = tool_call["name"]
                    tool_args = tool_call["args"]
                    tool_id = tool_call["id"]

                    # Notify about tool call
                    if on_tool_call:
                        await on_tool_call(tool_name, tool_args)

                    if tool_name in tools_dict:
                        tool = tools_dict[tool_name]
                        try:
                            put_plot_here = {}
                            tool_result = await tool.ainvoke(
                                tool_args,
                                config={"configurable": {"db": db_session, "put_plot_here": put_plot_here}},
                            )

                            if tool_name in {"pie_chart_from_sql_query", "horizontal_bar_chart_from_query"} and on_plot_created is not None:
                                if "plot" in put_plot_here:
                                    await on_plot_created(put_plot_here["plot"])

                            # Notify about tool result
                            if on_tool_result:
                                await on_tool_result(tool_name, str(tool_result))

                            history.add_message(
                                ToolMessage(content=str(tool_result), tool_call_id=tool_id)
                            )
                        except Exception as e:
                            # Handle tool execution errors
                            print(f"Tool {tool_name} failed: {str(e)}")

                            # Abort any pending database transaction
                            try:
                                await db_session.execute(text("ABORT"))
                            except Exception as e:
                                pass

                            error_msg = f"Error executing tool {tool_name}: {str(e)}"

                            # Notify about error
                            if on_tool_result:
                                await on_tool_result(tool_name, error_msg)

                            history.add_message(
                                ToolMessage(content=error_msg, tool_call_id=tool_id)
                            )

                # Continue with updated messages
                messages = history.messages
                current_response = AIMessage(content="")

            # Add final response to history if it has content
            if current_response.content and not tool_calls:
                history.add_message(current_response)

            return full_response

        except Exception as e:
            error_msg = f"Error processing message: {str(e)}"
            if on_error:
                await on_error(error_msg)
            raise


# Global chat service instance
chat_service = ChatService()

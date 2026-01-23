"""
LangChain agent setup for the AI shopping assistant.

Uses Claude as the LLM with tool-calling capabilities.
"""
from typing import Generator, Any

from django.conf import settings

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from .prompts import SYSTEM_PROMPT
from .tools import ALL_TOOLS
from .models import Conversation, Message


def get_llm():
    """Get the Claude LLM instance."""
    return ChatAnthropic(
        model="claude-sonnet-4-20250514",
        anthropic_api_key=settings.ANTHROPIC_API_KEY,
        streaming=True,
        max_tokens=4096,
    )


def build_message_history(conversation: Conversation) -> list:
    """Convert database messages to LangChain message format."""
    messages = []

    for msg in conversation.messages.all():
        if msg.role == 'user':
            content = msg.content
            # Handle images in user messages (only HTTPS URLs - Claude API requirement)
            if msg.image_url and msg.image_url.startswith('https://'):
                content = [
                    {"type": "text", "text": msg.content},
                    {"type": "image_url", "image_url": {"url": msg.image_url}},
                ]
            messages.append(HumanMessage(content=content))

        elif msg.role == 'assistant':
            messages.append(AIMessage(content=msg.content, tool_calls=msg.tool_calls or []))

        elif msg.role == 'tool':
            messages.append(ToolMessage(
                content=msg.content,
                tool_call_id=msg.tool_call_id,
            ))

    return messages


def execute_tool(tool_name: str, tool_args: dict, cart_id: str = None) -> str:
    """Execute a tool by name with the given arguments."""
    import json

    # Find the tool function
    tool_func = None
    for t in ALL_TOOLS:
        if t.name == tool_name:
            tool_func = t
            break

    if not tool_func:
        return json.dumps({'error': f'Unknown tool: {tool_name}'})

    # Inject cart_id for cart-related tools
    if cart_id and 'cart_id' in tool_func.args_schema.schema().get('properties', {}):
        tool_args['cart_id'] = cart_id

    try:
        result = tool_func.invoke(tool_args)
        return json.dumps(result) if not isinstance(result, str) else result
    except Exception as e:
        return json.dumps({'error': str(e)})


def run_agent(
    conversation: Conversation,
    user_message: str,
    image_url: str = None,
    cart_id: str = None,
) -> Generator[dict, None, None]:
    """
    Run the agent with a user message and yield streaming responses.

    Args:
        conversation: The conversation object
        user_message: The user's message
        image_url: Optional URL of an attached image
        cart_id: Optional cart ID for cart operations

    Yields:
        dict with 'type' and 'content' keys for streaming response chunks
    """
    import json

    llm = get_llm()
    llm_with_tools = llm.bind_tools(ALL_TOOLS)

    # Save user message to database
    user_msg_content = user_message
    Message.objects.create(
        conversation=conversation,
        role='user',
        content=user_message,
        image_url=image_url or '',
    )

    # Build message history
    history = build_message_history(conversation)

    # Build the prompt
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        *history[:-1],  # Exclude the just-added user message since we'll add it fresh
    ]

    # Add user message with optional image (only HTTPS URLs - Claude API requirement)
    if image_url and image_url.startswith('https://'):
        messages.append(HumanMessage(content=[
            {"type": "text", "text": user_message},
            {"type": "image_url", "image_url": {"url": image_url}},
        ]))
    else:
        messages.append(HumanMessage(content=user_message))

    # Agent loop - handle tool calls
    max_iterations = 10
    iteration = 0

    while iteration < max_iterations:
        iteration += 1

        # Stream the response
        full_response = ""
        tool_calls = []

        for chunk in llm_with_tools.stream(messages):
            # Handle text content
            if chunk.content:
                if isinstance(chunk.content, str):
                    full_response += chunk.content
                    yield {'type': 'text', 'content': chunk.content}
                elif isinstance(chunk.content, list):
                    for item in chunk.content:
                        if isinstance(item, dict) and item.get('type') == 'text':
                            full_response += item.get('text', '')
                            yield {'type': 'text', 'content': item.get('text', '')}

            # Collect tool calls
            if hasattr(chunk, 'tool_calls') and chunk.tool_calls:
                tool_calls.extend(chunk.tool_calls)
            if hasattr(chunk, 'tool_call_chunks') and chunk.tool_call_chunks:
                for tc in chunk.tool_call_chunks:
                    # Accumulate tool call chunks
                    pass  # Tool calls are aggregated at the end

        # Get the final message to check for tool calls
        final_response = llm_with_tools.invoke(messages)

        if hasattr(final_response, 'tool_calls') and final_response.tool_calls:
            tool_calls = final_response.tool_calls

        # Save assistant message
        assistant_msg = Message.objects.create(
            conversation=conversation,
            role='assistant',
            content=full_response or final_response.content,
            tool_calls=[{
                'id': tc['id'],
                'name': tc['name'],
                'args': tc['args'],
            } for tc in tool_calls] if tool_calls else None,
        )

        # If no tool calls, we're done
        if not tool_calls:
            break

        # Execute tool calls
        messages.append(AIMessage(
            content=full_response or final_response.content,
            tool_calls=tool_calls,
        ))

        for tool_call in tool_calls:
            yield {
                'type': 'tool_use',
                'tool': tool_call['name'],
                'args': tool_call['args'],
            }

            # Execute the tool
            result = execute_tool(
                tool_call['name'],
                tool_call['args'],
                cart_id=cart_id,
            )

            # Save tool result
            Message.objects.create(
                conversation=conversation,
                role='tool',
                content=result,
                tool_call_id=tool_call['id'],
            )

            # Add to messages for next iteration
            messages.append(ToolMessage(
                content=result,
                tool_call_id=tool_call['id'],
            ))

            # Parse JSON result (could be object {} or array [])
            try:
                parsed_result = json.loads(result)
            except (json.JSONDecodeError, TypeError):
                parsed_result = result

            yield {
                'type': 'tool_result',
                'tool': tool_call['name'],
                'result': parsed_result,
            }

    yield {'type': 'done'}


def run_agent_sync(
    conversation: Conversation,
    user_message: str,
    image_url: str = None,
    cart_id: str = None,
) -> str:
    """
    Run the agent synchronously and return the final response.

    Useful for testing or when streaming isn't needed.
    """
    full_response = ""

    for chunk in run_agent(conversation, user_message, image_url, cart_id):
        if chunk['type'] == 'text':
            full_response += chunk['content']

    return full_response

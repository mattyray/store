"""
LangChain agent setup for the AI shopping assistant.

Uses Claude as the LLM with tool-calling capabilities.
"""
import json
import uuid
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
        # Include the URL in the text so Claude can pass it to analyze_room_image tool
        text_with_url = f"{user_message}\n\n[Attached image URL: {image_url}]"
        messages.append(HumanMessage(content=[
            {"type": "text", "text": text_with_url},
            {"type": "image_url", "image_url": {"url": image_url}},
        ]))
    else:
        messages.append(HumanMessage(content=user_message))

    # Agent loop - handle tool calls
    max_iterations = 10
    iteration = 0
    total_text_yielded = False

    while iteration < max_iterations:
        iteration += 1

        # Stream the response - use astream_events or collect chunks properly
        full_response = ""
        tool_calls = []
        tool_call_chunks = {}  # Dict to accumulate tool call chunks by index

        for chunk in llm_with_tools.stream(messages):
            # Handle text content
            if chunk.content:
                if isinstance(chunk.content, str):
                    # Add separator between iterations if we already yielded text
                    if total_text_yielded and not full_response:
                        yield {'type': 'text', 'content': '\n\n'}
                    full_response += chunk.content
                    total_text_yielded = True
                    yield {'type': 'text', 'content': chunk.content}
                elif isinstance(chunk.content, list):
                    for item in chunk.content:
                        if isinstance(item, dict) and item.get('type') == 'text':
                            if total_text_yielded and not full_response:
                                yield {'type': 'text', 'content': '\n\n'}
                            full_response += item.get('text', '')
                            total_text_yielded = True
                            yield {'type': 'text', 'content': item.get('text', '')}

            # Collect tool calls from chunks - they come in pieces during streaming
            if hasattr(chunk, 'tool_call_chunks') and chunk.tool_call_chunks:
                for tc_chunk in chunk.tool_call_chunks:
                    idx = tc_chunk.get('index', 0)
                    if idx not in tool_call_chunks:
                        tool_call_chunks[idx] = {'id': '', 'name': '', 'args': ''}
                    if tc_chunk.get('id'):
                        tool_call_chunks[idx]['id'] = tc_chunk['id']
                    if tc_chunk.get('name'):
                        tool_call_chunks[idx]['name'] = tc_chunk['name']
                    if tc_chunk.get('args'):
                        tool_call_chunks[idx]['args'] += tc_chunk['args']

        # Convert accumulated chunks to tool calls
        for idx in sorted(tool_call_chunks.keys()):
            tc = tool_call_chunks[idx]
            if tc['name']:  # Only include if we have a tool name
                args = {}
                if tc['args']:
                    try:
                        args = json.loads(tc['args'])
                    except json.JSONDecodeError:
                        pass
                tool_calls.append({
                    'id': tc['id'] or f"call_{uuid.uuid4().hex[:24]}",
                    'name': tc['name'],
                    'args': args,
                })

        # Save assistant message
        assistant_msg = Message.objects.create(
            conversation=conversation,
            role='assistant',
            content=full_response,
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
            content=full_response,
            tool_calls=tool_calls,
        ))

        for tool_call in tool_calls:
            # Skip invalid tool calls (empty name or missing data)
            tool_name = tool_call.get('name', '')
            tool_id = tool_call.get('id', '')
            tool_args = tool_call.get('args', {})

            if not tool_name:
                continue

            # Generate a tool_call_id if missing
            if not tool_id:
                tool_id = f"call_{uuid.uuid4().hex[:24]}"

            yield {
                'type': 'tool_use',
                'tool': tool_name,
                'args': tool_args,
            }

            # Execute the tool
            result = execute_tool(
                tool_name,
                tool_args,
                cart_id=cart_id,
            )

            # Save tool result
            Message.objects.create(
                conversation=conversation,
                role='tool',
                content=result,
                tool_call_id=tool_id,
            )

            # Add to messages for next iteration
            messages.append(ToolMessage(
                content=result,
                tool_call_id=tool_id,
            ))

            # Parse JSON result (could be object {} or array [])
            try:
                parsed_result = json.loads(result)
            except (json.JSONDecodeError, TypeError):
                parsed_result = result

            yield {
                'type': 'tool_result',
                'tool': tool_name,
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

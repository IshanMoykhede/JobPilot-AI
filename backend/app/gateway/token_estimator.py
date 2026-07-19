"""
Token Estimator.
Heuristics to estimate prompt token usage before sending the request.
"""
from langchain_core.messages import BaseMessage

from app.schemas.gateway_schemas import GatewayRequest
from app.gateway.tokenizer import estimate_tokens

SCHEMA_TOKEN_BUFFER = 500


def estimate_request_tokens(request: GatewayRequest) -> int:
    """
    Estimate the total number of tokens required for an LLM request.
    """

    # Render the prompt using the payload
    formatted_messages = request.prompt_template.format_messages(**request.payload)

    # Convert all messages into a single string
    prompt_text = messages_to_text(formatted_messages)

    # Count prompt tokens
    prompt_tokens = estimate_tokens(prompt_text)

    # Total estimate
    total_tokens = (
        prompt_tokens
        + SCHEMA_TOKEN_BUFFER
        + request.expected_output_tokens
    )

    return total_tokens


def messages_to_text(messages):
    """
    Convert LangChain messages into a single string.
    """

    text = ""

    for message in messages:
        text += message.content + "\n"

    return text
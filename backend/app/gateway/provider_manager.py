"""
Provider Manager.
Abstracts the specific logic for calling Groq or Gemini.
"""
from __future__ import annotations

import time
from typing import Any

from app.gateway.schemas import (
    GatewayRequest,
    GatewayResponse,
    TokenUsage,
)


async def execute(
    request: GatewayRequest,
) -> GatewayResponse:
    """
    Execute an already constructed LangChain Runnable.

    Responsibilities:
        - Execute the chain
        - Measure latency
        - Extract provider token usage
        - Return a standardized GatewayResponse

    NOTE:
        Token estimation, scheduling, queueing and rate limiting
        are handled before this function is called.
    """

    start_time = time.perf_counter()

    response = await _invoke_chain(request)

    latency_ms = (time.perf_counter() - start_time) * 1000

    usage = _extract_usage(response)

    return GatewayResponse(
        data=response,
        usage=usage,
        provider="groq",
        latency_ms=latency_ms,
    )


async def _invoke_chain(
    request: GatewayRequest,
) -> Any:
    """
    Execute the LangChain Runnable.
    """

    return await request.chain.ainvoke(request.payload)


def _extract_usage(
    response: Any,
) -> TokenUsage:
    """
    Extract token usage from the provider response.

    Returns zero usage if metadata is unavailable.
    """

    metadata = getattr(response, "response_metadata", {}) or {}

    token_usage = metadata.get("token_usage", {}) or {}

    return TokenUsage(
        prompt_tokens=token_usage.get("prompt_tokens", 0),
        completion_tokens=token_usage.get("completion_tokens", 0),
        total_tokens=token_usage.get("total_tokens", 0),
    )
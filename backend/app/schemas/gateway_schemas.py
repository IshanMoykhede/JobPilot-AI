from __future__ import annotations

from enum import Enum
from typing import Any, Dict
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, ConfigDict


class RequestPriority(str, Enum):
    HTTP = "http"
    BACKGROUND = "background"


class GatewayRequest(BaseModel):
    """
    Standard request object accepted by the LLM Gateway.

    The Gateway should know NOTHING about the business logic
    (Resume Parser, Query Optimizer, Job Knowledge Generator, etc.).
    It only receives a chain and executes it safely.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    # ---------- Request Tracking ----------
    request_id: UUID = Field(
        default_factory=uuid4,
        description="Unique identifier for tracing a request across logs."
    )

    # ---------- LangChain Execution ----------
    chain: Any = Field(
        ...,
        description="Configured LangChain Runnable to execute."
    )

    payload: Dict[str, Any] = Field(
        ...,
        description="Variables injected into the prompt."
    )

    prompt_template: Any | None = Field(
        default=None,
        description="Prompt template used for accurate token estimation."
    )

    # ---------- Token Estimation ----------
    expected_output_tokens: int = Field(
        default=1000,
        ge=1,
        description="Estimated completion tokens reserved before execution."
    )

    # ---------- Gateway Controls ----------
    priority: RequestPriority = Field(
        default=RequestPriority.HTTP,
        description="Scheduling priority used by the rate limiter."
    )


class TokenUsage(BaseModel):
    """
    Exact token usage returned by the provider.
    """

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class GatewayResponse(BaseModel):
    """
    Standard response returned by the Gateway.
    """

    data: Any = Field(
        description="Structured output returned by the chain."
    )

    usage: TokenUsage = Field(
        default_factory=TokenUsage,
        description="Actual provider token usage."
    )

    provider: str = Field(
        default="unknown",
        description="Provider that served the request."
    )

    latency_ms: float = Field(
        default=0.0,
        description="End-to-end execution latency."
    )

    retry_count: int = Field(
        default=0,
        description="Number of retries performed."
    )

    wait_time_ms: float = Field(
        default=0.0,
        description="Time spent waiting for token reservation."
    )
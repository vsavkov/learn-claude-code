#!/usr/bin/env python3
"""FastAPI gateway for the containerlab agent."""

from __future__ import annotations

import json
import os
import time
import uuid
from pathlib import Path
from typing import Any, Literal

import anthropic
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, field_validator

from containerlab_agent import TOOLS, process_tool_call

# Keep behavior consistent with the CLI agent by loading .env from this folder.
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                if key not in os.environ:
                    os.environ[key] = value

DEFAULT_MODEL = os.getenv("MODEL_ID", "claude-sonnet-4-5-20250929")
SYSTEM_PROMPT = """You are a containerlab infrastructure assistant. You help users understand,
visualize, and manage their containerlab network topologies.

You have access to tools that can:
- List all running labs
- Inspect lab details, nodes, and configurations
- Show network interface information
- Generate topology graphs
- Display topology file contents
- Execute commands inside containerlab nodes

When a user asks about their containerlab infrastructure:
1. Use the appropriate tools to gather information
2. Present the information clearly and concisely
3. Offer helpful insights about the topology
4. Suggest useful next steps if appropriate

Be proactive in using tools to provide complete answers. If you need to check multiple things
to fully answer a question, use multiple tools in sequence."""


class QueryRequest(BaseModel):
    query: str = Field(..., description="Natural language query")
    model: str = Field(default=DEFAULT_MODEL)
    max_tokens: int = Field(default=4096, ge=1, le=16384)
    timeout_seconds: int = Field(default=60, ge=1, le=120)

    @field_validator("query")
    @classmethod
    def validate_query(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("query must not be empty")
        return cleaned


class ToolCallTrace(BaseModel):
    id: str
    name: str
    input: dict[str, Any]
    status: Literal["success", "error"]
    duration_ms: int


class RawOutput(BaseModel):
    tool_use_id: str
    content: str


class QueryResponse(BaseModel):
    answer: str
    tool_calls: list[ToolCallTrace]
    raw_outputs: list[RawOutput]
    timing_ms: int
    model: str
    request_id: str
    timestamp: str

    model_config = ConfigDict(extra="forbid")


class ErrorResponse(BaseModel):
    error_code: str
    message: str
    request_id: str
    details: dict[str, Any] | None = None


class GatewayError(Exception):
    def __init__(
        self,
        error_code: str,
        message: str,
        status_code: int,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.error_code = error_code
        self.message = message
        self.status_code = status_code
        self.details = details


def _log_json(event: str, request_id: str, **kwargs: Any) -> None:
    payload = {
        "event": event,
        "request_id": request_id,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    payload.update(kwargs)
    print(json.dumps(payload), flush=True)


def _extract_text(content: list[Any]) -> str:
    parts: list[str] = []
    for block in content:
        text = getattr(block, "text", None)
        if text:
            parts.append(text)
    return "\n".join(parts).strip()


def _elapsed_ms(start: float) -> int:
    return int((time.monotonic() - start) * 1000)


def run_agent_with_trace(
    user_message: str,
    model: str,
    max_tokens: int,
    timeout_seconds: int,
) -> tuple[str, list[ToolCallTrace], list[RawOutput]]:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise GatewayError(
            error_code="anthropic_config_error",
            message="ANTHROPIC_API_KEY is not set",
            status_code=500,
        )

    client = anthropic.Anthropic(api_key=api_key)
    messages: list[dict[str, Any]] = [{"role": "user", "content": user_message}]
    traces: list[ToolCallTrace] = []
    outputs: list[RawOutput] = []

    start = time.monotonic()

    while True:
        if (time.monotonic() - start) >= timeout_seconds:
            raise GatewayError(
                error_code="request_timeout",
                message=f"Request exceeded timeout of {timeout_seconds} seconds",
                status_code=504,
            )

        try:
            response = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                system=SYSTEM_PROMPT,
                tools=TOOLS,
                messages=messages,
            )
        except Exception as exc:
            raise GatewayError(
                error_code="anthropic_api_error",
                message="Anthropic API request failed",
                status_code=502,
                details={"error": str(exc)},
            ) from exc

        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            return _extract_text(response.content), traces, outputs

        if response.stop_reason == "tool_use":
            tool_results: list[dict[str, Any]] = []

            for block in response.content:
                if getattr(block, "type", None) != "tool_use":
                    continue

                tool_start = time.monotonic()
                tool_name = getattr(block, "name", "unknown_tool")
                tool_input_raw = getattr(block, "input", {})
                tool_input = dict(tool_input_raw) if isinstance(tool_input_raw, dict) else {}
                tool_status: Literal["success", "error"] = "success"

                try:
                    result = process_tool_call(tool_name, tool_input)
                except Exception as exc:
                    tool_status = "error"
                    result = f"Error: {exc}"

                tool_duration = _elapsed_ms(tool_start)
                tool_id = getattr(block, "id", str(uuid.uuid4()))

                traces.append(
                    ToolCallTrace(
                        id=tool_id,
                        name=tool_name,
                        input=tool_input,
                        status=tool_status,
                        duration_ms=tool_duration,
                    )
                )
                outputs.append(RawOutput(tool_use_id=tool_id, content=result))

                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_id,
                        "content": result,
                    }
                )

            messages.append({"role": "user", "content": tool_results})
            continue

        raise GatewayError(
            error_code="anthropic_api_error",
            message=f"Unexpected model stop reason: {response.stop_reason}",
            status_code=502,
        )


app = FastAPI(title="Containerlab API Gateway", version="1.0.0")


@app.middleware("http")
async def request_context_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    started = time.monotonic()

    _log_json("request_started", request_id, path=request.url.path, method=request.method)

    try:
        response = await call_next(request)
    except Exception as exc:  # pragma: no cover
        duration_ms = _elapsed_ms(started)
        _log_json(
            "request_failed",
            request_id,
            path=request.url.path,
            method=request.method,
            duration_ms=duration_ms,
            error=str(exc),
        )
        raise

    duration_ms = _elapsed_ms(started)
    response.headers["X-Request-ID"] = request_id
    _log_json(
        "request_finished",
        request_id,
        path=request.url.path,
        method=request.method,
        status_code=response.status_code,
        duration_ms=duration_ms,
    )
    return response


@app.exception_handler(GatewayError)
async def gateway_error_handler(request: Request, exc: GatewayError):
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    payload = ErrorResponse(
        error_code=exc.error_code,
        message=exc.message,
        request_id=request_id,
        details=exc.details,
    )
    return JSONResponse(status_code=exc.status_code, content=payload.model_dump())


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/agent/query", response_model=QueryResponse, responses={422: {"model": ErrorResponse}})
async def query_agent(payload: QueryRequest, request: Request) -> QueryResponse:
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    started = time.monotonic()

    answer, traces, outputs = run_agent_with_trace(
        user_message=payload.query,
        model=payload.model,
        max_tokens=payload.max_tokens,
        timeout_seconds=payload.timeout_seconds,
    )

    return QueryResponse(
        answer=answer,
        tool_calls=traces,
        raw_outputs=outputs,
        timing_ms=_elapsed_ms(started),
        model=payload.model,
        request_id=request_id,
        timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    )

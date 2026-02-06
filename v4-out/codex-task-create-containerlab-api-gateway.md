# Task 1
Read all from this folder.
Create containerlab API gateway.
Use containerlab_agent.py functionality.

  ## Build FastAPI Query Gateway for Containerlab Agent

  ### Summary

  Implement a localhost-only, synchronous FastAPI gateway that exposes a single POST /agent/query endpoint and reuses containerlab_agent.py behavior via a
  gateway-specific orchestration engine (no refactor to existing agent file). The API returns a structured JSON envelope with final answer, tool-call trace, raw
  tool outputs, and timing metadata. Include /health, structured logging, and Docker packaging.

  ### Scope

  - In scope:
      - Read and use existing functions/tool contracts from containerlab_agent.py.
      - Add HTTP API layer with OpenAPI docs.
      - Add structured response model and error model.
      - Add operational baseline: health endpoint, JSON logs, Dockerfile.
      - Add tests for endpoint behavior and failure modes.
  - Out of scope:
      - Auth beyond localhost bind.
      - Async jobs or streaming.
      - OIDC/JWT/API-key auth.
      - Refactoring containerlab_agent.py internals.

  ### Public API / Interface Changes

  - New endpoint: POST /agent/query
  - New endpoint: GET /health
  - New runtime entrypoint: uvicorn api_gateway:app --host 127.0.0.1 --port 8080

  #### POST /agent/query request schema

  - query (string, required): natural language request.
  - model (string, optional): defaults to MODEL_ID env var or existing default.
  - max_tokens (integer, optional): defaults 4096.
  - timeout_seconds (integer, optional): defaults 60, max 120.

  #### POST /agent/query success schema (200)

  - answer (string)
  - tool_calls (array)
  - Each tool_calls item:
      - id (string)
      - name (string)
      - input (object)
      - status ("success" | "error")
      - duration_ms (integer)
  - raw_outputs (array)
  - Each raw_outputs item:
      - tool_use_id (string)
      - content (string)
  - timing_ms (integer)
  - model (string)
  - request_id (string)
  - timestamp (ISO-8601 string)

  #### Error schema (4xx/5xx)

  - error_code (string)
  - message (string)
  - request_id (string)
  - details (object, optional)

  ### Implementation Design

  1. Create api_gateway.py.

  - Define FastAPI app and Pydantic request/response models.
  - Load env (.env) similarly to existing behavior.
  - Validate query non-empty and timeout bounds.
  - Add middleware for request_id and timing.
  - Add structured JSON logging for request start/end/error.
  - Add /health returning { "status": "ok" }.

  2. Add gateway-specific orchestration engine in api_gateway.py.

  - Copy tool metadata usage from containerlab_agent.py (TOOLS) by import.
  - Import and reuse process_tool_call from containerlab_agent.py for execution.
  - Implement internal run_agent_with_trace(...) that:
      - Calls Anthropic Messages API.
      - Loops on tool_use.
      - Records tool call input, output, timing, and status.
      - Returns final assistant text and trace artifacts.
  - Keep containerlab_agent.py unchanged.

  3. Error handling behavior.

  - Anthropic auth/config errors -> 500 with error_code=anthropic_config_error.
  - Anthropic API runtime failures -> 502 with error_code=anthropic_api_error.
  - Tool execution exceptions -> keep request alive where possible; mark per-tool status=error.
  - Request timeout -> 504 with error_code=request_timeout.
  - Validation issues -> 422.

  4. Packaging and dependencies.

  - Add requirements.txt (or update if present) with:
      - fastapi
      - uvicorn[standard]
      - anthropic
      - pydantic
  - Add Dockerfile:
      - Python slim base.
      - Install requirements.
      - Copy project files.
      - Expose 8080.
      - Start uvicorn bound to 127.0.0.1 by default (can override with env for container use).

  5. Documentation updates.

  - Add API_GATEWAY.md with endpoint contract and curl examples.
  - Update README_CONTAINERLAB_AGENT.md with API gateway section and run instructions.

  ### Files To Add / Update

  - Add api_gateway.py
  - Add requirements.txt (if missing)
  - Add Dockerfile
  - Add API_GATEWAY.md
  - Update README_CONTAINERLAB_AGENT.md

  ### Data Flow

  1. Client sends POST /agent/query.
  2. Gateway validates payload and sets request_id.
  3. Gateway calls run_agent_with_trace.
  4. Model may request tool calls.
  5. Gateway executes tool via imported process_tool_call.
  6. Gateway accumulates trace and raw outputs.
  7. Gateway returns structured JSON envelope.

  ### Edge Cases and Failure Modes

  - Empty/whitespace query.
  - No ANTHROPIC_API_KEY present.
  - clab unavailable in PATH during tool calls.
  - Tool command timeout from existing subprocess logic.
  - Model returns end_turn without text blocks.
  - Multiple tool loops with mixed success/error outputs.

  ### Test Cases and Scenarios

  - Unit tests (tests/test_api_gateway.py):
      - Valid query returns envelope fields.
      - Empty query returns 422.
      - Missing API key path returns expected error code.
      - Tool call trace captures name, input, status, duration_ms.
      - Timeout path returns 504.
  - Integration-style tests with mocking:
      - Mock Anthropic client for tool_use then end_turn.
      - Mock process_tool_call success and failure outputs.
  - Health test:
      - GET /health returns 200 and status=ok.

  ### Rollout / Operations

  - Local run command:
      - uvicorn api_gateway:app --host 127.0.0.1 --port 8080
  - Docker run command:
      - Build and run with ANTHROPIC_API_KEY env injected.
  - Logging:
      - JSON logs with request_id, path, status_code, duration.
  - Initial deployment assumption:
      - Localhost-only access for v1.

  ### Assumptions and Defaults Chosen

  - API is query-only, no separate per-tool REST endpoints.
  - Runtime is Python + FastAPI.
  - Authentication is none for v1, mitigated by localhost bind.
  - Execution is synchronous request-response only.
  - Structured response always includes trace fields.
  - Existing containerlab_agent.py remains unchanged; gateway uses parallel orchestration engine.

# Task 2 Web UI

  ## Next.js Web UI With Dedicated Node BFF for API Gateway

  ### Summary

  Build a Next.js Web UI that never calls FastAPI directly from the browser. Add a dedicated Node.js BFF service (Express + TypeScript) that receives UI
  requests, calls the FastAPI gateway (/agent/query), normalizes the response DTO, and returns it to the UI.
  V1 UI scope is Dashboard + Chat with health visibility and tool-trace rendering.

  ### Goals and Success Criteria

  - Browser traffic goes only to Next.js and BFF, never directly to FastAPI.
  - BFF is the mandatory server hop for all query/health calls.
  - UI supports:
      - Query input + submit
      - Assistant answer rendering
      - Tool call trace table
      - Timing and request metadata
      - Health status indicator
  - Local development runs as two+ processes:
      - FastAPI gateway
      - Node BFF
      - Next.js UI
  - Strict localhost CORS at BFF layer.
  - Basic test coverage for BFF normalization + UI flow.

  ### Architecture

  1. Next.js UI (App Router)

  - Renders dashboard and chat console.
  - Calls only BFF endpoints via fetch from browser.

  2. Dedicated BFF (Express + TypeScript)

  - Exposes REST endpoints to UI:
      - GET /api/health
      - POST /api/query
  - Calls FastAPI gateway with server-side fetch.
  - Normalizes gateway payload into stable DTO.
  - Applies localhost-only CORS policy.

  3. FastAPI Gateway (existing)

  - Existing endpoints:
      - GET /health
      - POST /agent/query

  ### Public APIs / Interfaces

  #### New BFF API

  1. GET /api/health

  - Response 200:
      - status: "ok" | "degraded"
      - gatewayReachable: boolean
      - gatewayStatusCode?: number
      - timestamp: string

  2. POST /api/query

  - Request body:
      - query: string (required, trimmed, non-empty)
      - model?: string
      - maxTokens?: number
      - timeoutSeconds?: number
  - Response 200 normalized DTO:
      - answer: string
      - toolCalls: Array<{ id, name, input, status, durationMs }>
      - timingMs: number
      - requestId: string
      - timestamp: string
      - debug?: { rawGatewayPayload } (returned only when BFF_DEBUG=true)
  - Error response (4xx/5xx):
      - errorCode: string
      - message: string
      - requestId?: string
      - details?: object

  #### UI Contracts

  - UI fetches BFF:
      - NEXT_PUBLIC_BFF_BASE_URL (default http://127.0.0.1:3001)
  - BFF fetches gateway:
      - GATEWAY_BASE_URL (default http://127.0.0.1:8080)

  ### File/Project Layout (decision-complete)

  1. ui/ (Next.js project)

  - app/page.tsx dashboard + chat page
  - app/layout.tsx
  - components/QueryForm.tsx
  - components/AnswerPanel.tsx
  - components/TraceTable.tsx
  - components/HealthBadge.tsx
  - lib/types.ts DTO types matching BFF response
  - lib/api.ts browser API client for BFF
  - styles/globals.css

  2. bff/ (Express TypeScript project)

  - src/server.ts app bootstrap + middleware
  - src/routes/health.ts
  - src/routes/query.ts
  - src/services/gatewayClient.ts FastAPI call layer
  - src/mappers/normalize.ts gateway -> DTO mapping
  - src/types.ts request/response types
  - src/middleware/errorHandler.ts
  - src/middleware/requestId.ts
  - src/config.ts
  - tsconfig.json, package.json

  3. Root docs/scripts

  - WEB_UI.md run instructions and endpoint contracts
  - Update README_CONTAINERLAB_AGENT.md with UI + BFF startup section
  - Optional Makefile targets:
      - run-gateway
      - run-bff
      - run-ui

  ### Request/Response Flow

  1. User submits query in Next.js UI.
  2. Browser sends POST /api/query to BFF.
  3. BFF validates input and generates request ID.
  4. BFF calls FastAPI POST /agent/query.
  5. BFF maps gateway JSON to normalized DTO.
  6. BFF returns DTO to UI.
  7. UI renders answer + tool trace + timing.

  ### Validation and Error Handling

  - Client-side:
      - Disable submit for empty query.
      - Show inline validation.
  - BFF:
      - Enforce request schema (zod or equivalent).
      - Timeout FastAPI calls (default 65s).
      - Map FastAPI failures to stable error envelope.
  - UI:
      - Show friendly error message and technical detail toggle.
      - Preserve last successful response while showing new error state.

  ### Security and Localhost Policy

  - No auth for v1.
  - BFF CORS allowlist:
      - http://127.0.0.1:3000
      - http://localhost:3000
  - Reject other origins in browser context.
  - Do not expose FastAPI URL or keys in browser env.
  - ANTHROPIC_API_KEY remains only in gateway environment.

  ### Testing Plan

  #### BFF tests

  1. Unit:

  - normalize.ts maps gateway payload to DTO correctly.
  - Error mapping for 422/500/502/504.

  2. Integration:

  - POST /api/query success with mocked gateway.
  - Empty query -> 400.
  - Gateway unavailable -> 502.
  - CORS behavior for allowed/disallowed origins.

  3. Health:

  - GET /api/health reports gateway reachable/unreachable.

  #### UI tests

  1. Component tests:

  - Query form validation and submit behavior.
  - Trace table renders rows and statuses.
  - Error banner rendering.

  2. Integration (mock BFF):

  - Full query flow updates answer and trace.
  - Health badge updates from healthy/degraded.

  ### Run and Dev Workflow

  1. Start gateway:

  - uvicorn api_gateway:app --host 127.0.0.1 --port 8080

  2. Start BFF:

  - cd bff && npm run dev on 127.0.0.1:3001

  3. Start UI:

  - cd ui && npm run dev on 127.0.0.1:3000

  4. Open:

  - http://127.0.0.1:3000

  ### Non-Goals (v1)

  - Authentication/login.
  - Streaming token responses.
  - Persistent conversation history DB.
  - Production deployment automation.

  ### Assumptions and Defaults

  - Next.js uses App Router + TypeScript.
  - BFF uses Express + TypeScript.
  - Response shape is normalized DTO (not raw pass-through).
  - Dev mode is separate local processes.
  - Strict localhost CORS is sufficient for v1.
  - Gateway API contract remains as currently implemented in api_gateway.py.



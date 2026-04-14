# HTTP/ASGI Modernization Design

## Context

Phase 1 modernized the repository baseline and packaging, but the HTTP/ASGI plugin family still advertises and tests only old dependency versions:

- `aiohttp` support matrix still only mentions `3.7.*`
- `fastapi` support matrix still only mentions `0.88/0.89`
- `httpx` support matrix still only mentions `0.22/0.23`
- `websockets` support matrix still only mentions `10.3/10.4`

The user approved the "target upgrade" strategy for this group: move these plugins to current mainstream stable versions, adapt implementation only where needed, and verify with plugin tests before moving to the next family.

## Goals

- Extend the HTTP/ASGI support matrices to cover current mainstream stable versions
- Fix implementation breakage caused by API drift in the targeted libraries
- Keep compatibility with the previously tested versions where it remains cheap
- Regenerate plugin support documentation from the updated matrices

## Non-Goals

- Modernizing non-HTTP plugin families such as MongoDB, Redis, Celery, or Kafka
- Rewriting plugin internals for new architecture or context propagation models
- Removing all compatibility code for older tested versions

## Target Version Bands

- `aiohttp`: keep `3.9.*`, add `3.13.*`
- `fastapi`: keep `0.89.*`, add `0.135.*`
- `httpx`: keep `0.23.*`, add `0.28.*`
- `websockets`: keep `10.4`, add `16.0`

These choices intentionally cover one older already-supported line plus one current stable line, giving better confidence than a single-point upgrade while keeping the scope bounded.

## Design

### aiohttp

The client hook (`ClientSession._request`) remains viable in current aiohttp 3.x. The server hook (`RequestHandler._handle_request`) changed signature in newer aiohttp releases, so the plugin wrapper must accept the additional `request_handler` parameter and forward it conditionally.

### fastapi

The plugin continues to instrument `starlette.middleware.exceptions.ExceptionMiddleware.__call__`, which still exists in current FastAPI/Starlette. The main work is updating the support matrix and verifying the request/websocket wrapper still captures status and parameters correctly.

### httpx

The send hooks on `httpx.Client.send` and `httpx.AsyncClient.send` still exist in current versions. The URL sanitization logic should be made more robust so it does not depend on replacing raw username/password fragments in the string form.

### websockets

`websockets.legacy.client.WebSocketClientProtocol.handshake` still exists in current releases, so the plugin can keep that instrumentation path. Test fixtures should prefer the new `websockets.asyncio.client.connect` import when present and fall back to the legacy import for older versions.

## Verification

- Run targeted plugin tests for:
  - `tests/plugin/http/sw_aiohttp/test_aiohttp.py`
  - `tests/plugin/web/sw_fastapi/test_fastapi.py`
  - `tests/plugin/http/sw_httpx/test_httpx.py`
  - `tests/plugin/http/sw_websockets/test_websockets.py`
- Regenerate `docs/en/setup/Plugins.md`
- Build the package to ensure plugin source updates remain publishable

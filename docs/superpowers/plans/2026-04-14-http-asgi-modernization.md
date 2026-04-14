# HTTP/ASGI Modernization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade the aiohttp, FastAPI, httpx, and websockets plugins to current mainstream stable version bands and verify them with targeted plugin tests.

**Architecture:** Keep the existing plugin hook strategy for each library, broaden the support matrices to cover one historical and one current stable band, and apply only the compatibility fixes needed for signature or import drift in the newer libraries.

**Tech Stack:** Poetry, Docker-based plugin tests, aiohttp, FastAPI/Starlette, httpx, websockets

---

### Task 1: Update support matrices and low-risk compatibility points

**Files:**
- Modify: `skywalking/plugins/sw_aiohttp.py`
- Modify: `skywalking/plugins/sw_fastapi.py`
- Modify: `skywalking/plugins/sw_httpx.py`
- Modify: `skywalking/plugins/sw_websockets.py`

- [ ] **Step 1: Expand aiohttp support and adapt the server hook**

```python
support_matrix = {
    'aiohttp': {
        '>=3.10': ['3.9.*', '3.13.*']
    }
}

async def _sw_handle_request(self, request, start_time, request_handler=None):
    ...
    if request_handler is None:
        resp, reset = await _handle_request(self, request, start_time)
    else:
        resp, reset = await _handle_request(self, request, start_time, request_handler)
```

- [ ] **Step 2: Expand FastAPI support**

```python
support_matrix = {
    'fastapi': {
        '>=3.10': ['0.89.*', '0.135.*']
    }
}
```

- [ ] **Step 3: Expand httpx support and harden URL sanitization**

```python
support_matrix = {
    'httpx': {
        '>=3.10': ['0.23.*', '0.28.*']
    }
}

safe_url = str(request.url.copy_with(username=None, password=None))
```

- [ ] **Step 4: Expand websockets support**

```python
support_matrix = {
    'websockets': {
        '>=3.10': ['10.4', '16.0']
    }
}
```

- [ ] **Step 5: Run unit-level smoke checks**

Run: `python -m pytest -q tests/unit/test_version_check.py`
Expected: pass

### Task 2: Update plugin test fixtures for modern imports

**Files:**
- Modify: `tests/plugin/web/sw_fastapi/docker-compose.yml`
- Modify: `tests/plugin/http/sw_httpx/docker-compose.yml`
- Modify: `tests/plugin/http/sw_websockets/docker-compose.yml`
- Modify: `tests/plugin/web/sw_fastapi/services/consumer.py`
- Modify: `tests/plugin/http/sw_websockets/services/consumer.py`

- [ ] **Step 1: Pin explicit package installations where the compose files rely on transitive latest behavior**

```yaml
command: ['bash', '-c', 'pip install websockets uvicorn && pip install -r /app/requirements.txt && sw-python run python3 /app/services/consumer.py']
```

- [ ] **Step 2: Make websockets test consumers prefer the modern asyncio client import**

```python
try:
    from websockets.asyncio.client import connect
except ImportError:
    from websockets.client import connect
```

- [ ] **Step 3: Keep the FastAPI service layer compatible with both old and new websockets client imports**

```python
try:
    from websockets.asyncio.client import connect
except ImportError:
    from websockets.client import connect
```

- [ ] **Step 4: Inspect compose files for duplicate `sw-python run` or stale command assumptions**

Run: `rg -n "sw-python run sw-python run|websockets.client" tests/plugin/http/sw_aiohttp tests/plugin/web/sw_fastapi tests/plugin/http/sw_httpx tests/plugin/http/sw_websockets -S`
Expected: no stale patterns remain

- [ ] **Step 5: Commit**

```bash
git add skywalking/plugins tests/plugin
git commit -m "feat: modernize HTTP and ASGI plugin support"
```

### Task 3: Verify targeted plugin tests

**Files:**
- Modify: `docs/en/setup/Plugins.md`

- [ ] **Step 1: Run aiohttp plugin tests**

Run: `python -m pytest -q tests/plugin/http/sw_aiohttp/test_aiohttp.py -s`
Expected: all parametrized cases pass

- [ ] **Step 2: Run FastAPI plugin tests**

Run: `python -m pytest -q tests/plugin/web/sw_fastapi/test_fastapi.py -s`
Expected: all parametrized cases pass

- [ ] **Step 3: Run httpx plugin tests**

Run: `python -m pytest -q tests/plugin/http/sw_httpx/test_httpx.py -s`
Expected: all parametrized cases pass

- [ ] **Step 4: Run websockets plugin tests**

Run: `python -m pytest -q tests/plugin/http/sw_websockets/test_websockets.py -s`
Expected: all parametrized cases pass

- [ ] **Step 5: Regenerate plugin docs**

Run: `poetry run python3 tools/plugin_doc_gen.py`
Expected: `docs/en/setup/Plugins.md` reflects the updated support matrices

### Task 4: Final package verification

**Files:**
- Modify: `docs/superpowers/specs/2026-04-14-http-asgi-modernization-design.md`
- Modify: `docs/superpowers/plans/2026-04-14-http-asgi-modernization.md`

- [ ] **Step 1: Build the distribution**

Run: `poetry build`
Expected: sdist and wheel build successfully

- [ ] **Step 2: Validate metadata**

Run: `python -m twine check dist/*`
Expected: PASS

- [ ] **Step 3: Confirm the plugin doc is stable after regeneration**

Run: `before=$(sha256sum docs/en/setup/Plugins.md | awk '{print $1}') && poetry run python3 tools/plugin_doc_gen.py && after=$(sha256sum docs/en/setup/Plugins.md | awk '{print $1}') && test "$before" = "$after"`
Expected: exit code 0

- [ ] **Step 4: Commit any remaining generated-doc or plan/spec changes**

```bash
git add docs/en/setup/Plugins.md docs/superpowers/specs/2026-04-14-http-asgi-modernization-design.md docs/superpowers/plans/2026-04-14-http-asgi-modernization.md
git commit -m "docs: record HTTP and ASGI modernization"
```

- [ ] **Step 5: Push**

```bash
git push origin main
```

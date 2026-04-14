# Modernization Phase 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Raise the engineering baseline of the maintained fork to Python 3.10+, clean up packaging, and align workflows and docs with the current repository.

**Architecture:** Keep the existing Poetry-based package structure, but modernize the supported interpreter floor, stop publishing accidental files, separate runtime and code-generation dependencies, and update GitHub workflows plus maintained docs to reflect the current fork’s branch and repository ownership.

**Tech Stack:** Poetry, GitHub Actions, Twine, Markdown docs, Python packaging metadata

---

### Task 1: Raise the package baseline and clean runtime metadata

**Files:**
- Modify: `pyproject.toml`
- Modify: `Makefile`
- Delete: `skywalking/trace/carrier.py.bak`
- Test: `dist/sparticle_skywalking-*.whl`

- [ ] **Step 1: Update the package metadata**

```toml
[tool.poetry.dependencies]
python = ">=3.10,<4.0"
grpcio = ">=1.51.1"
protobuf = ">=4.21.6,<5.0dev"
packaging = ">=23.0"
wrapt = ">=1.14"
psutil = ">=5.9"
requests = { version = ">=2.31.0", optional = true }
kafka-python = { version = ">=2.0.2", optional = true }
```

- [ ] **Step 2: Move `grpcio-tools` out of runtime dependencies**

```toml
[tool.poetry.group.dev.dependencies]
grpcio-tools = ">=1.51.1"
```

- [ ] **Step 3: Remove the accidental backup file from the tracked source tree**

```bash
git rm skywalking/trace/carrier.py.bak
```

- [ ] **Step 4: Update Makefile cleanup and local build helpers**

```makefile
test:
	docker build --build-arg BASE_PYTHON_IMAGE=3.10-slim -t apache/skywalking-python-agent:latest-plugin --no-cache . -f tests/plugin/Dockerfile.plugin

clean:
	rm -rf apache_skywalking.egg-info sparticle_skywalking.egg-info dist build
```

- [ ] **Step 5: Verify the package builds without the backup file**

Run: `poetry build`
Expected: `sparticle_skywalking-<version>` artifacts are created and `carrier.py.bak` is absent from the wheel

### Task 2: Align GitHub workflows with the maintained fork

**Files:**
- Modify: `.github/workflows/CI.yaml`
- Modify: `.github/workflows/dead-link-checker.yaml`
- Modify: `.github/workflows/publish-docker.yaml`
- Modify: `.github/workflows/publish-pypi.yml`

- [ ] **Step 1: Switch push triggers from `master` to `main`**

```yaml
on:
  push:
    branches:
      - main
```

- [ ] **Step 2: Update scheduled-job repository guards to `sparticleinc/skywalking-python`**

```yaml
if: |
  ( always() && ! cancelled() ) &&
  ((github.event_name == 'schedule' && github.repository == 'sparticleinc/skywalking-python') || needs.changes.outputs.agent == 'true')
```

- [ ] **Step 3: Drop Python 3.7 through 3.9 from CI matrices**

```yaml
python-version: [ "3.10", "3.11", "3.12", "3.13", "3.14" ]
python-image-variant: [ "3.10-slim", "3.11-slim", "3.12-slim", "3.13-slim", "3.14-slim" ]
```

- [ ] **Step 4: Keep the PyPI workflow aligned with Poetry metadata lookup**

```yaml
package_version = project["tool"]["poetry"]["version"]
```

- [ ] **Step 5: Validate workflow hygiene**

Run: `rg -n "master|apache/skywalking-python" .github/workflows -S`
Expected: only intentional legacy Docker naming or documentation references remain

### Task 3: Align maintained docs with Python 3.10+ and `main`

**Files:**
- Modify: `README.md`
- Modify: `docs/menu.yml`
- Modify: `docs/en/setup/Installation.md`
- Modify: `docs/en/setup/Container.md`
- Modify: `docs/en/setup/faq/How-to-build-from-sources.md`
- Modify: `docs/en/contribution/Developer.md`
- Modify: `docs/en/contribution/How-to-test-plugin.md`
- Modify: `docs/en/contribution/How-to-test-locally.md`
- Modify: `docs/en/contribution/How-to-develop-plugin.md`
- Modify: `.github/PULL_REQUEST_TEMPLATE`

- [ ] **Step 1: Update package-level Python support statements**

```md
SkyWalking Python Agent requires Apache SkyWalking 8.0+ and Python 3.10+.
```

- [ ] **Step 2: Update contributor docs from `master` to `main`**

```md
Plugin tests are required and should pass before a new plugin is able to merge into the `main` branch.
```

- [ ] **Step 3: Update maintained GitHub links to the fork**

```md
https://github.com/sparticleinc/skywalking-python/blob/main/CHANGELOG.md
```

- [ ] **Step 4: Update local development examples to a supported interpreter**

```md
pyenv shell 3.12.0
```

- [ ] **Step 5: Verify there are no stale support statements in maintained docs**

Run: `rg -n "Python 3\\.7|3\\.7\\+|>=3\\.7|master branch|blob/master" README.md docs .github/PULL_REQUEST_TEMPLATE -S`
Expected: no stale maintained-doc references remain

### Task 4: Regenerate plugin support docs with a package-level baseline note

**Files:**
- Modify: `tools/plugin_doc_gen.py`
- Modify: `docs/en/setup/Plugins.md`

- [ ] **Step 1: Add a package-level support note to the generator header**

```python
doc_head = """# Supported Libraries
This document is **automatically** generated from the SkyWalking Python testing matrix.

The package itself requires Python 3.10+.
Historical plugin ranges below may mention older Python versions because they describe past test coverage, not the current package installation floor.
"""
```

- [ ] **Step 2: Regenerate the plugin documentation**

Run: `poetry run python3 tools/plugin_doc_gen.py`
Expected: `docs/en/setup/Plugins.md` is updated from the generator

- [ ] **Step 3: Check that the generated file carries the new baseline note**

Run: `sed -n '1,40p' docs/en/setup/Plugins.md`
Expected: the package-level Python 3.10+ note appears near the top

- [ ] **Step 4: Verify doc generation is clean**

Run: `make check-doc-gen`
Expected: no generated-doc drift remains

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml Makefile .github/workflows README.md docs .github/PULL_REQUEST_TEMPLATE
git commit -m "chore: modernize baseline to python 3.10"
```

### Task 5: Final verification

**Files:**
- Modify: `docs/superpowers/specs/2026-04-14-modernization-phase1-design.md`
- Modify: `docs/superpowers/plans/2026-04-14-modernization-phase1.md`

- [ ] **Step 1: Refresh the lockfile**

Run: `poetry lock`
Expected: `poetry.lock` updates cleanly for the new dependency model

- [ ] **Step 2: Run packaging verification**

Run: `poetry check && poetry build && python -m twine check dist/*`
Expected: all commands succeed

- [ ] **Step 3: Verify the wheel content**

Run: `python - <<'PY'
import zipfile
zf = zipfile.ZipFile('dist/sparticle_skywalking-1.0.6-py3-none-any.whl')
assert not any(name.endswith('.bak') for name in zf.namelist())
print('wheel-clean')
PY`
Expected: `wheel-clean`

- [ ] **Step 4: Smoke-test isolated installation**

Run: `tmpdir=$(mktemp -d) && python -m venv "$tmpdir/venv" && "$tmpdir/venv/bin/pip" install dist/sparticle_skywalking-1.0.6-py3-none-any.whl && cd "$tmpdir" && "$tmpdir/venv/bin/python" -I - <<'PY'
import skywalking
print(skywalking.__file__)
PY`
Expected: import resolves from the virtual environment `site-packages`

- [ ] **Step 5: Push**

```bash
git push origin main
```

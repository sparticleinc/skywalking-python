# Sparticle PyPI Release Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish this repository to PyPI as `sparticle-skywalking` with automated tag-based GitHub Actions releases.

**Architecture:** Keep the existing Poetry build backend and package layout, update repository metadata and release-facing docs to the new package identity, then add a dedicated PyPI publish workflow that validates the version tag before uploading through Trusted Publisher.

**Tech Stack:** Poetry, GitHub Actions, PyPI Trusted Publisher, Twine, Markdown docs

---

### Task 1: Align package metadata and README

**Files:**
- Modify: `pyproject.toml`
- Modify: `README.md`
- Modify: `docs/README.md`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Update package metadata to the new distribution name and version**

```toml
[tool.poetry]
name = "sparticle-skywalking"
version = "1.0.6"
authors = ["Sparticle Community <hy.zhu@sparticle.com>"]
maintainers = ["Sparticle Community <hy.zhu@sparticle.com>"]
homepage = "https://github.com/sparticleinc/skywalking-python"
repository = "https://github.com/sparticleinc/skywalking-python"
documentation = "https://github.com/sparticleinc/skywalking-python/blob/main/README.md"

[tool.poetry.urls]
"Bug Tracker" = "https://github.com/sparticleinc/skywalking-python/issues"
```

- [ ] **Step 2: Update the README package badges and installation instructions**

```md
[![GitHub stars](https://img.shields.io/github/stars/sparticleinc/skywalking-python.svg?style=for-the-badge&label=Stars&logo=github)](https://github.com/sparticleinc/skywalking-python)
![Release](https://img.shields.io/pypi/v/sparticle-skywalking)
![Version](https://img.shields.io/pypi/pyversions/sparticle-skywalking)
![Build](https://github.com/sparticleinc/skywalking-python/actions/workflows/CI.yaml/badge.svg?event=push)

```bash
pip install "sparticle-skywalking"
pip install "sparticle-skywalking[all]"
```
```

- [ ] **Step 3: Add a short release note entry for `1.0.6`**

```md
### 1.0.6

- Others:
  - Publish the Sparticle-maintained distribution to PyPI as `sparticle-skywalking`
  - Add GitHub Actions based PyPI publishing through Trusted Publisher
```

- [ ] **Step 4: Build the package locally to verify metadata changes**

Run: `poetry build`
Expected: `Built sparticle_skywalking-1.0.6.tar.gz` and `Built sparticle_skywalking-1.0.6-py3-none-any.whl`

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml README.md docs/README.md CHANGELOG.md
git commit -m "build: rename package to sparticle-skywalking"
```

### Task 2: Update user and maintainer documentation

**Files:**
- Modify: `docs/en/setup/Installation.md`
- Modify: `docs/en/setup/Intrusive.md`
- Modify: `docs/en/contribution/How-to-release.md`

- [ ] **Step 1: Update installation docs to the new PyPI package**

```md
The Python agent module is published to [PyPI](https://pypi.org/project/sparticle-skywalking/),
from where you can use `pip` to install:

```shell
pip install "sparticle-skywalking"
pip install "sparticle-skywalking[all]"
pip install "sparticle-skywalking[http]"
pip install "sparticle-skywalking[kafka]"
pip install sparticle-skywalking==1.0.6
```
```

- [ ] **Step 2: Update intrusive setup examples for optional extras**

```md
> Remember you should install the package with the `http` extra, `pip install "sparticle-skywalking[http]"`.

> Remember you should install the package with the `kafka` extra, `pip install "sparticle-skywalking[kafka]"`.
```

- [ ] **Step 3: Replace the legacy Apache release guide with the repository's PyPI release flow**

```md
## Release Steps

1. Update `CHANGELOG.md` and the version in `pyproject.toml`.
2. Merge to `main`.
3. Push a version tag such as `v1.0.6`.
4. Wait for `.github/workflows/publish-pypi.yml` to publish the distribution.
5. Verify installation from PyPI.
```

- [ ] **Step 4: Inspect the updated docs**

Run: `sed -n '1,220p' docs/en/setup/Installation.md`
Expected: install commands point to `sparticle-skywalking`

- [ ] **Step 5: Commit**

```bash
git add docs/en/setup/Installation.md docs/en/setup/Intrusive.md docs/en/contribution/How-to-release.md
git commit -m "docs: align installation and release guides"
```

### Task 3: Add automated PyPI publishing

**Files:**
- Create: `.github/workflows/publish-pypi.yml`

- [ ] **Step 1: Add a tag-triggered publish workflow**

```yaml
name: publish-pypi

on:
  push:
    tags:
      - "v*"
```

- [ ] **Step 2: Add build, version-check, and artifact upload steps**

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@v5
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: python -m pip install --upgrade pip "packaging>=24.2" poetry twine
      - run: poetry build
      - run: python -m twine check dist/*
```

- [ ] **Step 3: Add a publish job using Trusted Publisher**

```yaml
  publish:
    needs: build
    runs-on: ubuntu-latest
    permissions:
      id-token: write
    environment:
      name: pypi
      url: https://pypi.org/project/sparticle-skywalking/
    steps:
      - uses: actions/download-artifact@v5
        with:
          name: python-package-distributions
          path: dist/
      - uses: pypa/gh-action-pypi-publish@release/v1
```

- [ ] **Step 4: Validate the workflow file syntax and build behavior locally**

Run: `poetry build`
Expected: distributions are created and ready for the workflow upload step

- [ ] **Step 5: Commit**

```bash
git add .github/workflows/publish-pypi.yml
git commit -m "ci: add trusted publisher release workflow"
```

### Task 4: Final verification and release

**Files:**
- Modify: `docs/superpowers/specs/2026-04-14-sparticle-pypi-release-design.md`
- Modify: `docs/superpowers/plans/2026-04-14-sparticle-pypi-release.md`

- [ ] **Step 1: Run repository checks for the release change**

Run: `poetry build`
Expected: `sparticle_skywalking-1.0.6` distributions are generated without errors

- [ ] **Step 2: Confirm the workflow file exists at the PyPI-configured path**

Run: `test -f .github/workflows/publish-pypi.yml`
Expected: exit code `0`

- [ ] **Step 3: Commit the plan and spec along with the release changes if still uncommitted**

```bash
git add docs/superpowers/specs/2026-04-14-sparticle-pypi-release-design.md docs/superpowers/plans/2026-04-14-sparticle-pypi-release.md
git commit -m "docs: record PyPI release design and plan"
```

- [ ] **Step 4: Push the branch**

Run: `git push origin main`
Expected: remote branch updates successfully

- [ ] **Step 5: Create and push the release tag**

```bash
git tag v1.0.6
git push origin v1.0.6
```

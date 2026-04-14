# Modernization Phase 1 Design

## Context

The repository is now publishing successfully to PyPI as `sparticle-skywalking`, but the engineering baseline is still inconsistent with the maintained fork:

- the package metadata still targets Python `>=3.7`
- the main CI workflows still assume the default branch is `master`
- several scheduled jobs still gate on `apache/skywalking-python`
- the published wheel contains an accidental backup file, `skywalking/trace/carrier.py.bak`
- runtime dependencies are too loose and rely on `grpcio-tools` transitively providing the `protobuf` runtime
- user-facing docs still describe the project as supporting Python 3.7+

The user explicitly approved a phased modernization strategy rather than a single large dependency jump.

## Goals

- Raise the supported Python floor to `3.10`
- Align CI, release, and maintenance workflows with the current repository reality: `sparticleinc/skywalking-python` on `main`
- Remove accidental artifacts from source distributions and wheels
- Separate runtime dependencies from code generation tooling
- Update core docs so the published support story matches the package and workflows
- Regenerate plugin support docs with an explicit note that the package itself now requires Python 3.10+

## Non-Goals

- Full plugin ecosystem modernization to latest major versions
- Rewriting the package to a different build backend
- Reworking Docker image naming beyond the minimum needed to stop using stale Apache-specific repo gates

## Decisions

### Python Baseline

The package will now require Python `>=3.10,<4.0`.

This removes three EOL interpreter lines at once, reduces the compatibility burden for future dependency upgrades, and matches the user's stated tolerance for dropping Python 3.7 through 3.9.

### Packaging Cleanup

- Remove `grpcio-tools` from runtime dependencies
- Add `protobuf` explicitly as a runtime dependency
- Replace `*` runtime dependency pins with minimum supported bounds where the repository already has evidence for safe baselines
- Delete `skywalking/trace/carrier.py.bak` from the repository so it can no longer leak into wheels
- Keep the existing Poetry build backend for this phase

### Workflow Alignment

Repository automation will be updated to:

- trigger push-based CI from `main`
- run scheduled jobs for `sparticleinc/skywalking-python`
- remove stale Apache-only repository guards where they block maintenance in the maintained fork
- drop Python 3.7 through 3.9 from active CI matrices

### Documentation Alignment

Docs will be updated so that:

- package installation docs state Python 3.10+
- contributor docs no longer reference `master` as the integration branch
- plugin support docs explain that package-level support starts at Python 3.10 even when historical plugin test ranges mention older interpreters

## Verification

- `poetry check`
- `poetry lock`
- `poetry build`
- `python -m twine check dist/*`
- targeted repository searches for stale `master` / `>=3.7` references in maintained docs and workflows
- smoke install of the built wheel in an isolated virtual environment

## Follow-Up Work

Phase 2 should focus on plugin-family upgrades in isolated batches:

1. HTTP and ASGI plugins
2. database and cache plugins
3. messaging plugins
4. framework-specific plugins with thin compatibility bands such as Sanic and Falcon

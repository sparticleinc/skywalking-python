# Sparticle SkyWalking Python Release Guide

This guide documents how this repository publishes the `sparticle-skywalking` package to PyPI.

## Prerequisites

1. Update `CHANGELOG.md` and the version in `pyproject.toml`.
2. Make sure the package name in `pyproject.toml` is `sparticle-skywalking`.
3. Make sure the PyPI Trusted Publisher for `sparticle-skywalking` points to:
   - GitHub owner: `sparticleinc`
   - repository: `skywalking-python`
   - workflow: `publish-pypi.yml`
   - environment: `pypi`
4. Merge the release commit into `main`.

## Local verification

Build the package before pushing a release tag:

```bash
poetry build
python -m pip install --upgrade "packaging>=24.2" twine
python -m twine check dist/*
```

The build should produce:

- `dist/sparticle_skywalking-$VERSION.tar.gz`
- `dist/sparticle_skywalking-$VERSION-py3-none-any.whl`

## Publish a release

Set the version you want to release:

```bash
export VERSION=1.0.6
```

Create and push the Git tag:

```bash
git checkout main
git pull --ff-only origin main
git tag "v$VERSION"
git push origin "v$VERSION"
```

The publish workflow at `.github/workflows/publish-pypi.yml` will:

1. verify that `v$VERSION` matches the version in `pyproject.toml`
2. build the distribution with Poetry
3. run `twine check`
4. publish to PyPI through Trusted Publisher

## Post-release verification

After the workflow succeeds, verify installation from PyPI:

```bash
python -m pip install --upgrade "sparticle-skywalking==$VERSION"
python - <<'PY'
import skywalking
print(skywalking.__file__)
PY
```

Also confirm the project page renders correctly:

- <https://pypi.org/project/sparticle-skywalking/>

# Sparticle PyPI Release Design

## Context

This repository currently builds a valid Python distribution with Poetry, but it is not configured to publish a maintained package to `pypi.org` under a Sparticle-owned name. The historical PyPI project `sparticleinc-skywalking` is not usable because the original PyPI account cannot be recovered, so the new distribution will use a new package name.

## Goals

- Publish this repository to PyPI under the new package name `sparticle-skywalking`.
- Keep the import path unchanged as `skywalking`.
- Keep the GitHub repository path unchanged as `sparticleinc/skywalking-python`.
- Publish automatically from GitHub Actions when a version tag such as `v1.0.6` is pushed.
- Use PyPI Trusted Publisher instead of a long-lived API token.

## Non-Goals

- Renaming the GitHub repository.
- Rewriting the runtime package layout or import paths.
- Changing Docker image publishing behavior in this change.

## Decisions

### Package Identity

- PyPI package name: `sparticle-skywalking`
- Python import name: `skywalking`
- Initial release version on the new package line: `1.0.6`

Using a fresh package name avoids the blocked ownership problem on `sparticleinc-skywalking` while keeping the installed library API stable for users.

### Metadata Alignment

The package metadata and user-facing repository documentation must consistently point to the Sparticle-maintained distribution:

- update package name and version in `pyproject.toml`
- replace stale Apache-specific package badges and installation commands in `README.md`
- update installation and release documentation that still instructs users to install `apache-skywalking`
- keep Apache license and upstream attribution intact

### Release Automation

A dedicated GitHub Actions workflow will publish to PyPI:

- trigger only on pushed tags matching `v*`
- build distributions from the repository source
- verify that the Git tag version matches the Poetry package version
- run a distribution metadata check before publishing
- publish through PyPI Trusted Publisher using GitHub OIDC
- use the GitHub Actions environment `pypi`

### Operational Flow

1. Merge the release configuration into `main`.
2. Push a Git tag such as `v1.0.6`.
3. GitHub Actions builds and publishes `sdist` and `wheel`.
4. Validate installation from PyPI with `pip install sparticle-skywalking==1.0.6`.

## Error Handling

- If the Git tag and `pyproject.toml` version differ, the publish workflow fails before upload.
- If `poetry build` fails, no artifact is published.
- If `twine check` fails, the publish job is skipped because the build job does not complete successfully.
- If Trusted Publisher is misconfigured, the publish step fails without exposing reusable credentials.

## Verification

- local `poetry build`
- local inspection of generated distribution metadata
- GitHub Actions build on the release tag
- post-release install verification from PyPI

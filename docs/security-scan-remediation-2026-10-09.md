# Security scan remediation, 2026-10-09

## Scope

This change addresses scan `3803fdeb-8ffa-4641-b785-117c7bbfaaae` from
<https://security-scan.gbase.ai/scans>, taken at commit
`68dbba872f4e35e187515e3eacf64eba25aa813a`.

The scan reported 764 records. Most dependency records came from two stale
inputs: a Poetry lock last resolved against old plugin and development package
constraints, and a UTF-16 `requirements.txt` copied from an unrelated Python
environment in 2023. The root requirements file had no consumer in the build,
CI, package metadata, Docker image, or current documentation. Plugin tests
create their own case-local `requirements.txt` files through
`tests/plugin/conftest.py`; those files do not consume the deleted root file.

## Remediation

- Replaced UUID version 1 defaults for agent instance and trace IDs with UUID
  version 4 values and added trace ID contract tests.
- Disabled Flask and Bottle debug mode in demo and container test servers.
  Demo servers now bind to loopback. Container fixtures retain `0.0.0.0`
  because sibling test containers must reach them.
- Added bounded timeouts to the requests calls identified by Bandit.
- Replaced explicit PyYAML loader calls in the plugin validator with
  `yaml.safe_load`. The old `Loader` alias selected `CSafeLoader` or
  `SafeLoader`, so this also makes the existing safe behavior clear to static
  analysis.
- Kept the aiohttp URL credential stripping and renamed the sanitized value so
  the tag path is unambiguous. The original code already removed user and
  password data; the credential-log report was a naming false positive.
- Removed the unused environment dump, raised vulnerable runtime, plugin, and
  test dependency floors, and regenerated `poetry.lock`. The published `http`
  and `all` extras constrain optional urllib3 to `>=2.8.0,<3.0.0` so requests
  cannot resolve a release affected by the current urllib3 advisories.
- Changed the agent image to UID/GID `65532`, and corrected the runtime wheel
  glob from the obsolete `apache_skywalking` name to the published
  `sparticle_skywalking` distribution name.

## Validation

- `pytest tests/unit -q`: 27 passed.
- urllib3 HTTP regression checks cover positional and keyword request bodies, JSON, form fields, preserved headers, response bytes, and trace propagation against a loopback server. The positional-body case failed before the compatibility fix and passed after.
- Poetry package build: source archive and wheel built.
- Full `dev,plugins` Poetry install completed. MariaDB headers and libraries
  were extracted under `/var/tmp/henry-build` for the mysqlclient build; the
  workstation was not modified.
- Imports and instrumentation installation passed for 29 maintained plugin
  dependency set, including mysqlclient, asyncpg, aiohttp, Django, Flask,
  FastAPI, pymongo, redis, tornado, urllib3, and websockets. The lock no longer
  installs aioredis 2.0.1, which fails on Python 3.12 with a duplicate
  `TimeoutError` base class, or Sanic, whose support matrix already declares no
  supported Python 3.10 release. Pyramid was also removed from this aggregate
  development group because its current release requires a vulnerable
  setuptools line. The agent plugins remain present. Plugin integration tests
  create case-local requirements from each plugin's support matrix, so these
  development-group removals do not remove shipped instrumentation.
- Trivy dependency scan, including development dependencies: 0 findings.
- pip-audit over 102 packages exported from the Poetry lock: 0 findings.
- Docker-format image build passed. Image metadata reports user
  `65532:65532`, `sw-python --help` ran in the image, and pip-audit reported 0
  findings across seven third-party packages in the eight-package runtime image.
- Bandit over `skywalking`, `demo`, and `tests`: 0 high, 47 medium, and 32 low.
  The production package has no medium or high Bandit finding. The 47 medium
  reports are test-only: 43 container listener bindings, three fixed-scheme
  URL-open calls, and one container-local Kafka commit-log path.
- Generated plugin and configuration documentation matches the urllib3 2.8 support matrix and UUID4 runtime default.
- Full-repository lint remains unavailable as a passing gate: Flake8 reports 82 pre-existing diagnostics on both the baseline and this branch. Pylint 2.13 cannot parse a Python 3.12 type alias in a dependency; the baseline also fails this gate. No new Flake8 diagnostics were introduced.
- Semgrep with the platform Python, security-audit, and local rules: 0 findings
  and 0 errors.

## Residual scanner reports

The test services bind to all interfaces so Docker Compose peers can reach
them. Test database passwords are fixed fixture values for isolated containers.
Random values in tracing tests do not make authorization decisions. These
reports describe test topology and test data, not deployed agent behavior.

Trivy config check `DS-0026` remains: the agent image has no universal
`HEALTHCHECK`. Its entrypoint wraps an arbitrary user application, so the image
cannot know the application's protocol, port, or health path. Deployments must
define a probe for the wrapped application.

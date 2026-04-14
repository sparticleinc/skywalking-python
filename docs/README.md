# SkyWalking Python Agent

**This repository publishes the Sparticle-maintained PyPI distribution `sparticle-skywalking`.**

The Python Agent for Apache SkyWalking provides the native tracing/metrics/logging/profiling abilities for Python projects.

This documentation covers a number of ways to set up the Python agent for various use cases.

[![GitHub stars](https://img.shields.io/github/stars/sparticleinc/skywalking-python.svg?style=for-the-badge&label=Stars&logo=github)](https://github.com/sparticleinc/skywalking-python)
[![Twitter Follow](https://img.shields.io/twitter/follow/asfskywalking.svg?style=for-the-badge&label=Follow&logo=twitter)](https://twitter.com/AsfSkyWalking)

![Release](https://img.shields.io/pypi/v/sparticle-skywalking)
![Version](https://img.shields.io/pypi/pyversions/sparticle-skywalking)
![Build](https://github.com/sparticleinc/skywalking-python/actions/workflows/CI.yaml/badge.svg?event=push)

## Capabilities

The following table demonstrates the currently supported telemetry collection capabilities in SkyWalking Python agent:

| Reporter  | Supported?      | Details                                                    | 
|:----------|:----------------|:-----------------------------------------------------------|
| Trace     | ✅ (default: ON) | Automatic instrumentation + Manual SDK                     |            
| Log       | ✅ (default: ON) | Direct reporter only. (Tracing context in log planned)     |
| Meter     | ✅ (default: ON) | Meter API + Automatic PVM metrics                          |
| Event     | ❌ (Planned)     | Report lifecycle events of your awesome Python application |
| Profiling | ✅ (default: ON) | Threading and Greenlet Profiler                            |


## Live Demo

- Find the [live demo](https://skywalking.apache.org/#demo) with Python agent on our website.
- Follow the [showcase](https://skywalking.apache.org/docs/skywalking-showcase/next/readme/) to set up preview
  deployment quickly.

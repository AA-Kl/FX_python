---
# Fill in the fields below to create a basic custom agent for your repository.
# The Copilot CLI can be used for local testing: https://gh.io/customagents/cli
# To make this agent available, merge this file into the default repository branch.
# For format details, see: https://gh.io/customagents/config

name: agent_fxpy
description: agent assigned to fx_python
---

## Purpose

This repository is maintained using AI coding agents.
Work is defined through GitHub Issues.

## Rules

* Always work from a GitHub Issue.
* One Issue = one branch = one Pull Request.
* Do not make unrelated changes.
* Preserve existing functionality.
* Prefer simple, readable Python code.

## Workflow

1. Read assigned Issue.
2. Create branch:

   * feature/<issue-number>-description
   * fix/<issue-number>-description
   * refactor/<issue-number>-description
3. Implement only requested work.
4. Create Pull Request when finished.

## Definition of Done

* Code runs without errors
* Imports work
* No debug prints
* Documentation updated if needed

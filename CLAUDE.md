# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

A research notebook about Claude Code itself — how to use it, and how agents, skills, slash commands, memory, best practices, and common pitfalls work (see `README.md`).

There is no application source code — the artifacts are agent definitions, notes, and small supporting scripts. No test suite or linter yet.

## Commands

```
make            # list targets
make validate   # check agent frontmatter (shared venv)
make validate-uv  # same check, ephemeral env, no venv needed
make env        # create/repair the shared venv
```

`make validate` fails on frontmatter that Claude Code would accept but silently misread — an unknown key like `tool:` or `maxturns:` costs you the restriction you thought you configured, with no load-time error. Run it after editing anything in `agents/`.

## Python environment

Python work uses **uv**, never `pip3` against system or Homebrew Python. The shared venv is `~/Dev/uv/envs/dev` (CPython 3.14.6); `make env` creates it, and `VENV=...` overrides the path. Do not put venvs in `~/.venvs` or under `~/.local/share/uv/` — the latter is uv's own managed state.

Prefer `uv run --with <pkg>` or PEP 723 inline script metadata for one-off scripts; that needs no named env at all. `agents/scripts/validate-frontmatter.py` carries such a header, which is what makes `make validate-uv` work anywhere.

`~/.zshrc` configures mamba/conda, so never prepend a venv to `PATH` globally — invoke interpreters by absolute path instead.

## Two paths, one repository

These two paths are the *same* directory, reached through a symlink (`/Users/ilirium/Projects/code-2026` → `/Users/ilirium/Storage/OneDrive/software-engineering/code-2026`):

- `/Users/ilirium/Library/CloudStorage/OneDrive-Personal/software-engineering/code-2026/claude_code_research`
- `/Users/ilirium/Projects/code-2026/claude_code_research`

Both are registered as working directories. Editing a file under one path changes it under the other — they are not two copies to keep in sync. Prefer the OneDrive-Personal path (the primary working directory) when writing paths into files or commands, so references stay consistent.

The repository lives inside OneDrive, so files may be touched by cloud sync; `.DS_Store` noise and sync artifacts are expected.

## Remote

`git@github.com:ilirium/claude_code_research.git` (https://github.com/ilirium/claude_code_research). `main` is the default and only branch.

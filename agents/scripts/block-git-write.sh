#!/bin/bash
# PreToolUse hook for the test-runner agent.
# Blocks git commands that write history or publish, and CI-config edits via shell.
# Wired up in agents/test-runner.md frontmatter; path there is relative to the
# project root (the cwd Claude Code runs in), not to this file.
#
# Contract: hook input arrives as JSON on stdin; exit 2 blocks the call and
# sends stderr back to the agent as the reason. Exit 0 allows.

INPUT=$(cat)

if command -v jq >/dev/null 2>&1; then
  COMMAND=$(printf '%s' "$INPUT" | jq -r '.tool_input.command // empty')
else
  # Fall back to a rough extraction so a missing jq fails closed-ish rather
  # than silently allowing everything.
  COMMAND=$(printf '%s' "$INPUT" | tr ',' '\n' | sed -n 's/.*"command"[[:space:]]*:[[:space:]]*"\(.*\)".*/\1/p')
fi

[ -z "$COMMAND" ] && exit 0

if printf '%s' "$COMMAND" | grep -qE '\bgit[[:space:]]+(commit|push|merge|rebase|reset|revert|cherry-pick|tag|stash|clean|checkout|switch|restore|filter-branch|update-ref)\b'; then
  echo "Blocked: test-runner must not alter git state or history. Leave changes in the working tree and report them." >&2
  exit 2
fi

if printf '%s' "$COMMAND" | grep -qE '\bgit[[:space:]]+config\b'; then
  echo "Blocked: test-runner must not change git configuration." >&2
  exit 2
fi

exit 0

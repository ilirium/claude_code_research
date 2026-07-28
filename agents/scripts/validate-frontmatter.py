# /// script
# requires-python = ">=3.13"
# dependencies = ["pyyaml"]
# ///
"""Validate the YAML frontmatter of Claude Code agent definition files.

Two ways to run it:

    make validate                                  # shared venv at ~/Dev/uv/envs/dev
    uv run agents/scripts/validate-frontmatter.py  # ephemeral env from the header above

Arguments may be files or directories; directories are scanned for *.md.
Defaults to ./agents. Files without frontmatter (task notes, READMEs) are skipped.

The check that matters most is the unknown-field one: Claude Code silently ignores
frontmatter keys it doesn't recognize, so a typo like `tool:` or `maxturns:` costs
you the restriction you thought you had, with no error at load time.
"""

import sys
from pathlib import Path

import yaml

REQUIRED = {"name", "description"}

# Supported frontmatter fields, per https://code.claude.com/docs/en/sub-agents
KNOWN = REQUIRED | {
    "tools",
    "disallowedTools",
    "model",
    "permissionMode",
    "maxTurns",
    "skills",
    "mcpServers",
    "hooks",
    "memory",
    "background",
    "effort",
    "isolation",
    "color",
    "initialPrompt",
}

MODELS = {"sonnet", "opus", "haiku", "fable", "inherit"}
COLORS = {"red", "blue", "green", "yellow", "purple", "orange", "pink", "cyan"}
PERMISSION_MODES = {
    "default",
    "acceptEdits",
    "auto",
    "dontAsk",
    "bypassPermissions",
    "plan",
    "manual",
}
EFFORTS = {"low", "medium", "high", "xhigh", "max"}
MEMORY_SCOPES = {"user", "project", "local"}


def parse(text: str) -> dict | None:
    """Return the frontmatter mapping, or None if the file has no frontmatter."""
    if not text.startswith("---"):
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    return yaml.safe_load(parts[1])


def check(front: dict) -> list[str]:
    problems = [f"missing required field: {f}" for f in sorted(REQUIRED - front.keys())]
    problems += [
        f"unknown field, silently ignored at load time: {f}"
        for f in sorted(front.keys() - KNOWN)
    ]

    name = front.get("name")
    if isinstance(name, str) and name != name.lower().replace(" ", ""):
        problems.append(f"name should be lowercase-with-hyphens: {name!r}")

    model = front.get("model")
    if model is not None and model not in MODELS and not str(model).startswith("claude-"):
        problems.append(f"model {model!r} is not an alias {sorted(MODELS)} or a claude-* id")

    for field, allowed in (
        ("color", COLORS),
        ("permissionMode", PERMISSION_MODES),
        ("effort", EFFORTS),
        ("memory", MEMORY_SCOPES),
    ):
        value = front.get(field)
        if value is not None and value not in allowed:
            problems.append(f"{field} {value!r} not in {sorted(allowed)}")

    turns = front.get("maxTurns")
    if turns is not None and (not isinstance(turns, int) or turns < 1):
        problems.append(f"maxTurns must be a positive integer, got {turns!r}")

    isolation = front.get("isolation")
    if isolation is not None and isolation != "worktree":
        problems.append(f"isolation must be 'worktree', got {isolation!r}")

    return problems


def collect(args: list[str]) -> list[Path]:
    paths: list[Path] = []
    for arg in args or ["agents"]:
        path = Path(arg)
        paths.extend(sorted(path.glob("*.md")) if path.is_dir() else [path])
    return paths


def main(argv: list[str]) -> int:
    failed = False
    names: dict[str, Path] = {}

    for path in collect(argv):
        if not path.exists():
            print(f"FAIL {path}  does not exist")
            failed = True
            continue

        try:
            front = parse(path.read_text())
        except yaml.YAMLError as exc:
            print(f"FAIL {path.name}  frontmatter does not parse: {exc}")
            failed = True
            continue

        if front is None:
            print(f"skip {path.name}  (no frontmatter)")
            continue
        if not isinstance(front, dict):
            print(f"FAIL {path.name}  frontmatter is not a mapping")
            failed = True
            continue

        problems = check(front)

        # Duplicate names in one directory resolve by filesystem read order,
        # so only one definition loads and which one is undefined.
        name = front.get("name")
        if isinstance(name, str):
            if name in names:
                problems.append(f"duplicate name {name!r}, also in {names[name].name}")
            names[name] = path

        if problems:
            failed = True
            print(f"FAIL {path.name}")
            for problem in problems:
                print(f"       - {problem}")
        else:
            tools = front.get("tools", "(inherits all)")
            model = front.get("model", "inherit")
            print(f"ok   {path.name:18} model={model:9} tools={tools}")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

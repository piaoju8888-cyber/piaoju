#!/usr/bin/env python3
"""Validate the standalone OpenAI skill package structure without third-party deps."""

from __future__ import annotations

import re
import sys
from pathlib import Path


def main() -> int:
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
    errors: list[str] = []

    required = [
        root / "SKILL.md",
        root / "references" / "operating-system.md",
        root / "agents" / "openai.yaml",
    ]
    forbidden = [
        root / "operating-system.md",
        root / "openai.yaml",
    ]

    for path in required:
        if not path.is_file():
            errors.append(f"missing required file: {path.relative_to(root)}")

    for path in forbidden:
        if path.exists():
            errors.append(f"stale compatibility path must be absent: {path.relative_to(root)}")

    skill_path = root / "SKILL.md"
    if skill_path.is_file():
        skill = skill_path.read_text(encoding="utf-8")
        if not skill.startswith("---\n"):
            errors.append("SKILL.md must start with YAML front matter")
        else:
            parts = skill.split("---", 2)
            frontmatter = parts[1] if len(parts) >= 3 else ""
            if not re.search(r"(?m)^name:\s*\S+", frontmatter):
                errors.append("SKILL.md front matter is missing non-empty name")
            if not re.search(r"(?m)^description:\s*\S+", frontmatter):
                errors.append("SKILL.md front matter is missing non-empty description")

        if "references/operating-system.md" not in skill:
            errors.append("SKILL.md must reference references/operating-system.md")

    agent_path = root / "agents" / "openai.yaml"
    if agent_path.is_file():
        agent = agent_path.read_text(encoding="utf-8")
        for pattern, label in [
            (r"(?m)^interface:\s*$", "interface"),
            (r"(?m)^\s+display_name:\s*\S+", "interface.display_name"),
            (r"(?m)^\s+short_description:\s*\S+", "interface.short_description"),
        ]:
            if not re.search(pattern, agent):
                errors.append(f"agents/openai.yaml is missing {label}")

    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("PASS: skill structure is consistent with the intended OpenAI layout.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

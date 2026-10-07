#!/usr/bin/env python3
"""Run the skill trigger smoke set with Codex and save JSONL traces.

Prerequisite: the skill must already be installed/discoverable by the local Codex
environment. This runner does not copy or rewrite the skill.
"""

from __future__ import annotations

import csv
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "evals" / "litao-superteam-workflow.prompts.csv"
ARTIFACTS = ROOT / "evals" / "artifacts"
VALIDATOR = ROOT / "scripts" / "validate-skill-structure.py"


def main() -> int:
    structure = subprocess.run([sys.executable, str(VALIDATOR), str(ROOT)], cwd=ROOT)
    if structure.returncode != 0:
        return structure.returncode

    codex = shutil.which("codex")
    if not codex:
        print("FAIL: codex CLI was not found on PATH.", file=sys.stderr)
        return 2

    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    failures = 0

    with CASES.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))

    for row in rows:
        case_id = row["id"]
        trace_path = ARTIFACTS / f"{case_id}.jsonl"
        stderr_path = ARTIFACTS / f"{case_id}.stderr.txt"

        proc = subprocess.run(
            [codex, "exec", "--json", row["prompt"]],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        trace_path.write_text(proc.stdout, encoding="utf-8")
        stderr_path.write_text(proc.stderr, encoding="utf-8")

        status = "OK" if proc.returncode == 0 else "ERROR"
        print(
            f"{case_id}: {status}; expected should_trigger={row['should_trigger']}; "
            f"trace={trace_path.relative_to(ROOT)}"
        )
        if proc.returncode != 0:
            failures += 1

    print(
        "Trigger runs complete. Review the JSONL traces against the expected "
        "should_trigger labels and output-quality expectations in the prompts."
    )
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

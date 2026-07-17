#!/usr/bin/env python3
"""Regenerate the sample fixture in isolation and assert its intended failure."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="olimazi-fixture-") as tmp:
        work = Path(tmp)
        (work / "fixtures").mkdir()
        (work / "engine").mkdir()
        shutil.copy2(ROOT / "fixtures" / "make_fixture.py", work / "fixtures")
        shutil.copy2(ROOT / "engine" / "reconcile.py", work / "engine")

        generated = run([sys.executable, "fixtures/make_fixture.py"], work)
        if generated.returncode != 0:
            raise AssertionError(f"fixture generator failed:\n{generated.stderr}")

        reconciled = run(
            [sys.executable, "engine/reconcile.py", "fixtures/sample-property"],
            work,
        )
        result_path = work / "fixtures" / "sample-property" / "reconciliation.json"
        result = json.loads(result_path.read_text(encoding="utf-8"))
        failures = [
            check for check in result["checks"] if check.get("status") == "FAIL"
        ]

        assert reconciled.returncode == 1, reconciled.stdout + reconciled.stderr
        assert result["fails"] == 1, result
        assert len(failures) == 1, failures
        assert "missing-locksmith-receipt.pdf" in failures[0]["detail"], failures[0]

        print("Fixture regression: PASS")
        print("  reconcile exit: 1")
        print("  failures: 1")
        print("  intended missing reference: missing-locksmith-receipt.pdf")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

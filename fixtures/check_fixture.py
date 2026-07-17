#!/usr/bin/env python3
"""Regenerate the sample fixture in isolation and assert its intended failure."""

from __future__ import annotations

import hashlib
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
        shutil.copy2(ROOT / "engine" / "match_receipts.py", work / "engine")

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
        assert "missing-gardener-invoice.pdf" in failures[0].get("detail", ""), failures

        tracker = work / "fixtures" / "sample-property" / "sample-tracker.xlsx"
        before = hashlib.sha256(tracker.read_bytes()).hexdigest()
        matched_once = run(
            [sys.executable, "engine/match_receipts.py", "fixtures/sample-property"],
            work,
        )
        assert matched_once.returncode == 0, matched_once.stdout + matched_once.stderr
        first_state = json.loads(
            (work / "fixtures" / "sample-property" / "match_state.json").read_text(
                encoding="utf-8"
            )
        )
        assert len(first_state["proposals"]) == 1, first_state
        assert not first_state["ambiguous"], first_state
        assert len(first_state["misses"]) == 1, first_state
        proposal = first_state["proposals"][0]
        miss = first_state["misses"][0]
        assert proposal["vendor"] == "Sample Electric", proposal
        assert proposal["file"] == "source-docs/2026-04-10_sample-electric_145.pdf", proposal
        assert miss["vendor"] == "Sample Locksmith", miss
        assert miss["miss_count"] == 1, miss
        assert hashlib.sha256(tracker.read_bytes()).hexdigest() == before

        matched_twice = run(
            [sys.executable, "engine/match_receipts.py", "fixtures/sample-property"],
            work,
        )
        assert matched_twice.returncode == 0, matched_twice.stdout + matched_twice.stderr
        second_state = json.loads(
            (work / "fixtures" / "sample-property" / "match_state.json").read_text(
                encoding="utf-8"
            )
        )
        assert second_state["misses"][0]["miss_count"] == 2, second_state
        proposals_text = (
            work / "fixtures" / "sample-property" / "MatchProposals.md"
        ).read_text(encoding="utf-8")
        assert "## Need from you" in proposals_text, proposals_text
        after = hashlib.sha256(tracker.read_bytes()).hexdigest()
        assert after == before

        source_docs = work / "fixtures" / "sample-property" / "source-docs"
        shutil.copy2(
            source_docs / "2026-04-10_sample-electric_145.pdf",
            source_docs / "2026-04-11_electric_145.pdf",
        )
        ambiguous_run = run(
            [sys.executable, "engine/match_receipts.py", "fixtures/sample-property"],
            work,
        )
        assert ambiguous_run.returncode == 0, ambiguous_run.stdout + ambiguous_run.stderr
        ambiguous_state = json.loads(
            (work / "fixtures" / "sample-property" / "match_state.json").read_text(
                encoding="utf-8"
            )
        )
        assert not ambiguous_state["proposals"], ambiguous_state
        assert len(ambiguous_state["ambiguous"]) == 1, ambiguous_state
        assert len(ambiguous_state["ambiguous"][0]["candidates"]) == 2, ambiguous_state
        assert hashlib.sha256(tracker.read_bytes()).hexdigest() == before

        print("Fixture regression: PASS")
        print("  reconcile exit: 1; failures: 1 (intended: missing-gardener-invoice.pdf)")
        print("  matcher: 1 proposal, 0 ambiguous, 1 miss")
        print("  proposal: source-docs/2026-04-10_sample-electric_145.pdf")
        print("  miss after two runs: Sample Locksmith (Need from you)")
        print("  ambiguity rule: 2 plausible files -> 0 proposals, 1 ambiguous")
        print(f"  workbook sha256 unchanged: {before}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

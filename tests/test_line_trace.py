from __future__ import annotations

import unittest
from pathlib import Path

import openpyxl

from engine.reconcile import build_line_traces, read_expenses


class LineTraceInvariantTest(unittest.TestCase):
    def test_every_fixture_line_trace_sums_to_its_displayed_total(self):
        root = Path(__file__).resolve().parents[1]
        workbook = openpyxl.load_workbook(
            root / "fixtures" / "sample-property" / "sample-tracker.xlsx",
            data_only=False,
        )
        expenses = read_expenses(workbook["Expenses"])

        traces = build_line_traces(expenses)
        displayed = {
            line: round(sum(expense["paid"] for expense in expenses
                            if line == 20 or expense["line"] == line), 2)
            for line in traces
        }

        for line, components in traces.items():
            with self.subTest(line=line):
                self.assertEqual(
                    round(sum(component["amount"] for component in components), 2),
                    displayed[line],
                )

        line14 = traces[14]
        self.assertGreater(sum(item["amount"] for item in line14
                               if item["amount"] >= 0), displayed[14])
        self.assertLess(sum(item["amount"] for item in line14
                            if item["amount"] < 0), 0)


if __name__ == "__main__":
    unittest.main()

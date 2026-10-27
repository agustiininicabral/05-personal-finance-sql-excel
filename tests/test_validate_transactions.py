from __future__ import annotations

import csv
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_transactions import analyze_transactions  # noqa: E402


class FinanceTransactionTests(unittest.TestCase):
    def test_included_dataset_passes_and_balances_reconcile(self) -> None:
        report = analyze_transactions(ROOT / "data" / "transactions.csv")
        self.assertEqual(report["status"], "PASS", report["failures"][:10])
        self.assertEqual(report["row_count"], 2200)
        self.assertEqual(
            float(report["totals"]["net_balance"]),
            round(float(report["totals"]["income"]) - float(report["totals"]["expenses"]), 2),
        )
        self.assertEqual(sum(row["transactions"] for row in report["monthly"]), 2200)

    def test_duplicate_transaction_id_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            source = ROOT / "data" / "transactions.csv"
            shutil.copy(source, folder / source.name)
            path = folder / source.name
            with path.open(newline="", encoding="utf-8") as stream:
                rows = list(csv.DictReader(stream))
            rows[1]["tx_id"] = rows[0]["tx_id"]
            with path.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
                writer.writeheader()
                writer.writerows(rows)
            report = analyze_transactions(path)

        self.assertTrue(any("unique" in error for error in report["failures"]))

    def test_invalid_date_amount_and_payment_method_are_detected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "transactions.csv"
            path.write_text(
                "tx_id,tx_date,category,method,amount,description\n"
                "1,not-a-date,Comida,Cash,0,Invalid row\n",
                encoding="utf-8",
            )
            report = analyze_transactions(path)

        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("invalid date or amount" in error for error in report["failures"]))


if __name__ == "__main__":
    unittest.main()

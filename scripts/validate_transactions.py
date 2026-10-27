"""Validate synthetic personal-finance transactions and calculate summaries."""

import argparse
import csv
import json
from collections import defaultdict
from datetime import date
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {"tx_id", "tx_date", "category", "method", "amount", "description"}
METHODS = {"Débito", "Crédito", "Efectivo", "Transferencia"}


def analyze_transactions(path):
    source = Path(path)
    if not source.is_file():
        return {"status": "FAIL", "failure_count": 1, "failures": ["Input CSV is missing."], "row_count": 0}

    with source.open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        missing = REQUIRED - set(reader.fieldnames or [])
        if missing:
            return {
                "status": "FAIL",
                "failure_count": 1,
                "failures": [f"Missing columns: {', '.join(sorted(missing))}"],
                "row_count": 0,
            }
        rows = list(reader)

    failures = []
    ids = [row["tx_id"].strip() for row in rows]
    if any(not value for value in ids) or len(ids) != len(set(ids)):
        failures.append("tx_id values must be non-empty and unique.")

    monthly = defaultdict(lambda: {"income": Decimal("0"), "expense": Decimal("0"), "count": 0})
    by_category = defaultdict(lambda: {"amount": Decimal("0"), "count": 0})
    income_total = Decimal("0")
    expense_total = Decimal("0")

    for row in rows:
        tx_id = row.get("tx_id", "?")
        try:
            month = date.fromisoformat(row["tx_date"]).strftime("%Y-%m")
            amount = Decimal(row["amount"])
            if not amount.is_finite() or amount <= 0:
                failures.append(f"Transaction {tx_id}: amount must be positive and finite.")
                continue
        except (KeyError, ValueError, ArithmeticError):
            failures.append(f"Transaction {tx_id}: invalid date or amount.")
            continue

        category = row.get("category", "").strip()
        method = row.get("method", "").strip()
        if not category:
            failures.append(f"Transaction {tx_id}: category is blank.")
        if method not in METHODS:
            failures.append(f"Transaction {tx_id}: unsupported payment method.")

        if category == "Ingresos":
            income_total += amount
            monthly[month]["income"] += amount
        else:
            expense_total += amount
            monthly[month]["expense"] += amount
        monthly[month]["count"] += 1
        by_category[category]["amount"] += amount
        by_category[category]["count"] += 1

    monthly_rows = [
        {
            "month": month,
            "transactions": values["count"],
            "income": str(values["income"].quantize(Decimal("0.01"))),
            "expenses": str(values["expense"].quantize(Decimal("0.01"))),
            "net": str((values["income"] - values["expense"]).quantize(Decimal("0.01"))),
        }
        for month, values in sorted(monthly.items())
    ]
    category_rows = [
        {
            "category": category,
            "transactions": values["count"],
            "amount": str(values["amount"].quantize(Decimal("0.01"))),
        }
        for category, values in sorted(by_category.items())
    ]
    return {
        "status": "PASS" if not failures else "FAIL",
        "row_count": len(rows),
        "failure_count": len(failures),
        "failures": failures,
        "totals": {
            "income": str(income_total.quantize(Decimal("0.01"))),
            "expenses": str(expense_total.quantize(Decimal("0.01"))),
            "net_balance": str((income_total - expense_total).quantize(Decimal("0.01"))),
        },
        "monthly": monthly_rows,
        "by_category": category_rows,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default=str(ROOT / "data" / "transactions.csv"))
    parser.add_argument("--out", default=str(ROOT / "reports" / "finance_quality_report.json"))
    args = parser.parse_args()
    report = analyze_transactions(args.input)
    output = Path(args.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        f"{report['status']}: {report['row_count']} transactions; "
        f"{report['failure_count']} validation failures"
    )
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

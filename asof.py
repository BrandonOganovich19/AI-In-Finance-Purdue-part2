"""Lab 16 - Provenance Gate: a point-in-time (as-of) filter.

Run:  python asof.py                 (uses DECISION_DATE below)
      python asof.py 2026-04-15      (optional override for the swap-and-break test)

Standard library only. Every number printed is computed from the inputs below.
"""
import sys
from datetime import date

# ---------------------------------------------------------------- editable inputs
DECISION_DATE = "2026-03-31"

# Training table pasted from the lab (fictional one-year zero-coupon bond funds).
# Columns: Row | Ticker | Month measured | Published on | Price
TABLE = """
| 1  | AAA | 2026-01 | 2026-02-10 | 101.0 |
| 2  | AAA | 2026-02 | 2026-03-10 | 104.0 |
| 3  | AAA | 2026-03 | 2026-04-10 | 109.0 |
| 4  | AAA | 2026-02 | 2026-03-25 | 103.0 |
| 5  | BBB | 2026-01 | 2026-02-10 | 98.0  |
| 6  | BBB | 2026-02 | 2026-03-10 | 97.0  |
| 7  | BBB | 2026-02 | 2026-03-10 | 97.0  |
| 8  | BBB | 2026-03 | 2026-04-10 | 92.0  |
| 9  | CCC | 2026-01 | 2026-02-10 | 110.0 |
| 10 | CCC | 2026-02 | 2026-04-05 | 112.0 |
| 11 |     | 2026-02 | 2026-03-10 | 99.0  |
| 12 | CCC | 2026-02 | 2026-03-10 | 111.0 |
"""
# ---------------------------------------------------------------------------------

MONTH_NAMES = ["January", "February", "March", "April", "May", "June", "July",
               "August", "September", "October", "November", "December"]


def parse_table(text):
    """Turn the pasted markdown rows into a list of dicts, keeping the row number."""
    rows = []
    for line in text.strip().splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not line.strip() or not cells[0].isdigit():
            continue  # skip blank lines, the header row and the |---:| separator if pasted
        if len(cells) != 5:
            raise ValueError(f"Expected 5 columns, got {len(cells)}: {line!r}")
        row_no, ticker, month, published, price = cells
        rows.append({
            "row": int(row_no),
            "ticker": ticker,                          # may be blank
            "month": month,                            # month measured, YYYY-MM
            "published": date.fromisoformat(published),  # realtime_start
            "price": float(price),
        })
    return rows


def content_key(r):
    """Everything except the row number: two rows with the same key are exact duplicates."""
    return (r["ticker"], r["month"], r["published"], r["price"])


def rule1_quarantine_no_ticker(rows):
    kept = [r for r in rows if r["ticker"]]
    out = [r for r in rows if not r["ticker"]]
    return kept, out


def rule2_remove_exact_duplicates(rows):
    seen, kept, out = set(), [], []
    for r in rows:                       # rows are in row-number order, so the first copy is kept
        k = content_key(r)
        if k in seen:
            out.append(r)
        else:
            seen.add(k)
            kept.append(r)
    return kept, out


def rule3_remove_after_decision(rows, decision):
    kept = [r for r in rows if r["published"] <= decision]
    out = [r for r in rows if r["published"] > decision]
    return kept, out


def latest_publication(rows):
    """Rule 4: for each (ticker, month) keep only the most recently published row.

    Applied after rule 3, every row left is already published on or before the decision
    date, so 'latest' here means 'latest knowable on the decision date'.
    """
    best = {}
    for r in rows:
        k = (r["ticker"], r["month"])
        if k not in best or r["published"] > best[k]["published"]:
            best[k] = r
    keep_ids = {r["row"] for r in best.values()}
    kept = [r for r in rows if r["row"] in keep_ids]
    out = [r for r in rows if r["row"] not in keep_ids]
    return kept, out


def signals(panel):
    """Per ticker: percent change from the previous month to the latest month in the panel."""
    by_ticker = {}
    for r in panel:
        by_ticker.setdefault(r["ticker"], {})[r["month"]] = r
    result = {}
    for ticker in sorted(by_ticker):
        months = sorted(by_ticker[ticker])
        if len(months) < 2:
            result[ticker] = None
            continue
        prev, last = by_ticker[ticker][months[-2]], by_ticker[ticker][months[-1]]
        pct = (last["price"] / prev["price"] - 1) * 100
        result[ticker] = (pct, last)
    return result


def month_name(yyyy_mm):
    return MONTH_NAMES[int(yyyy_mm[5:7]) - 1]


def ids(rows):
    return ", ".join(str(r["row"]) for r in rows) or "-"


def print_panel(panel):
    print(f"  {'Row':>3}  {'Ticker':<6} {'Month':<8} {'Published':<11} {'Price':>7}")
    for r in sorted(panel, key=lambda r: r["row"]):
        print(f"  {r['row']:>3}  {r['ticker']:<6} {r['month']:<8} "
              f"{r['published'].isoformat():<11} {r['price']:>7.1f}")


def run(decision_text=DECISION_DATE, table=TABLE):
    decision = date.fromisoformat(decision_text)
    raw = parse_table(table)

    # ---- as-of path: the four rules, in order
    s1, q1 = rule1_quarantine_no_ticker(raw)
    s2, q2 = rule2_remove_exact_duplicates(s1)
    s3, q3 = rule3_remove_after_decision(s2, decision)
    panel, q4 = latest_publication(s3)

    # ---- naive path: every row's latest publication, ignoring the publication date.
    # Rules 1 and 2 are data hygiene, not timing, so the naive comparison still applies them;
    # only rule 3 (the decision-date cut) is skipped.
    naive_panel, _ = latest_publication(s2)

    asof_sig, naive_sig = signals(panel), signals(naive_panel)

    print(f"Lab 16 - Provenance gate | decision date {decision.isoformat()}")
    print(f"Rows in: {len(raw)}\n")
    print("ROW FUNNEL")
    funnel = [
        ("1. Quarantined: no ticker", q1),
        ("2. Removed: exact duplicate", q2),
        (f"3. Removed: published after {decision.isoformat()}", q3),
        ("4. Removed: older vintage replaced by a revision", q4),
    ]
    for label, removed in funnel:
        print(f"  {label:<52} {len(removed)} row(s): {ids(removed)}")
    print(f"  {'As-of panel':<52} {len(panel)} row(s): {ids(sorted(panel, key=lambda r: r['row']))}\n")

    print("AS-OF PANEL")
    print_panel(panel)
    print()

    print("SIGNALS (percent change, previous month -> latest month)")
    print(f"  {'Ticker':<6}  {'As-of signal':<26}  {'Naive signal':<26}")
    for t in sorted(set(asof_sig) | set(naive_sig)):
        cells = []
        for sig in (asof_sig.get(t), naive_sig.get(t)):
            if sig is None:
                cells.append("not enough knowable months")
            else:
                pct, last = sig
                cells.append(f"{pct:+.2f}% ({month_name(last['month'])}, row {last['row']})")
        print(f"  {t:<6}  {cells[0]:<26}  {cells[1]:<26}")
    print()

    # ---- report-only sanity check (does NOT change the panel): zero-coupon yield = 100/price - 1
    print("SANITY CHECK - report only, the provenance gate does not act on this")
    credit_order = ["AAA", "BBB", "CCC"]  # safest first: a safer fund should be priced higher
    by_month = {}
    for r in panel:
        by_month.setdefault(r["month"], {})[r["ticker"]] = r["price"]
    for r in sorted(panel, key=lambda r: r["row"]):
        yld = (100 / r["price"] - 1) * 100
        breaks = []
        if r["price"] > 100:
            breaks.append("negative yield")
        if r["ticker"] in credit_order:
            safer = credit_order[:credit_order.index(r["ticker"])]
            same_month = by_month[r["month"]]
            cheaper_safer = [t for t in safer if t in same_month and same_month[t] < r["price"]]
            if cheaper_safer:
                breaks.append("priced above " + " and ".join(cheaper_safer))
        print(f"  row {r['row']:>2} {r['ticker']} {r['month']} price {r['price']:>6.1f} "
              f"yield {yld:+.2f}%  -> {'; '.join(breaks) or 'nothing'}")

    return {"funnel": [[r["row"] for r in rem] for _, rem in funnel],
            "panel": sorted(r["row"] for r in panel),
            "asof": {t: (round(v[0], 2), v[1]["month"]) for t, v in asof_sig.items() if v},
            "naive": {t: (round(v[0], 2), v[1]["month"]) for t, v in naive_sig.items() if v}}


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else DECISION_DATE)

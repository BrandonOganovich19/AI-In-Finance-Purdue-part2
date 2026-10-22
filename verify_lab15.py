"""Rebuild the test and recorded-data audit: python verify_lab15.py."""
import csv
import hashlib
import io
import json
from datetime import datetime, timezone
from pathlib import Path
import unittest
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_lab15  # Locate local dependencies when present; does not launch the app.


def main():
    root = Path(__file__).resolve().parent
    output = io.StringIO()
    output.write('Lab 15 reproducible verification\n')
    output.write('Run UTC: ' + datetime.now(timezone.utc).isoformat() + '\n\n')
    with (root/'prices.csv').open(newline='', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        rows = list(reader)
        tickers = reader.fieldnames[1:]
    assert tickers == ['VTI','QQQ','VOO','SCHD']
    assert len(rows) == 60
    meta = json.loads((root/'lab15_data/metadata.json').read_text())
    for ticker in tickers:
        raw = json.loads((root/'lab15_data'/f'{ticker}.json').read_text())
        chart = raw['chart']['result'][0]
        assert chart['meta']['symbol'] == ticker
        assert chart['meta']['currency'] == 'USD'
        month_ends = {}
        for stamp, value in zip(chart['timestamp'],chart['indicators']['adjclose'][0]['adjclose']):
            # Saved US daily bars occur during the same UTC and NY calendar date.
            day = datetime.fromtimestamp(stamp,timezone.utc).date().isoformat()
            if value is not None: month_ends[day[:7]] = (day,value)
        for row in rows:
            day,value = month_ends[row['Date'][:7]]
            assert row['Date'] == day and float(row[ticker]) == value
        output.write(f'{ticker}: all 60 prices match saved Yahoo adjusted closes.\n')
        output.write(f"Recorded download: {meta['downloaded_utc']}\nSource: {meta['sources'][ticker]}\n")
    output.write('\nAll 240 prices reconcile to recorded responses; no new retrieval claimed.\n')
    output.write('SHA256 prices.csv: '+hashlib.sha256((root/'prices.csv').read_bytes()).hexdigest()+'\n\n')
    suite = unittest.defaultTestLoader.loadTestsFromNames(['test_portfolio','test_lab15','test_lab15_app'])
    result = unittest.TextTestRunner(stream=output,verbosity=2).run(suite)
    output.write('\nThis project was made with Codex. I am not a financial advisor.\n')
    (root/'lab15_verification.txt').write_text(output.getvalue(),encoding='utf-8')
    print(output.getvalue())
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    raise SystemExit(main())

# This project was made with Codex. I am not a financial advisor.
# For educational purposes only; this is not investment advice.


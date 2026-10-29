"""Download reproducible evidence, check live known answers, and run offline tests."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import hashlib
import json
import io
import unittest
from datetime import date, timedelta
from asof_data import fetch, compare

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'lab17_data'

def main():
    DATA.mkdir(exist_ok=True)
    today = date.today()
    month_end = today.replace(day=1) - timedelta(days=1)
    expected = {'BAA': ('2026-09-01', 6.47), 'FEDFUNDS': ('2026-09-01', 3.75),
                'DGS10': ('2026-10-02', 5.28), 'MORTGAGE30US': ('2026-10-01', 7.28)}
    records, memo, lines = [], {}, ['Lab 17 live verification', f'Run date: {today}']
    def get(series, vintage=None):
        key = (series, vintage)
        if key not in memo:
            packet = fetch(series, vintage)
            name = f'{series}_{vintage or "current"}.csv'
            payload = packet['raw_csv'].encode('utf-8')
            (DATA / name).write_bytes(payload)
            records.append({'file': name, 'url': packet['url'], 'downloaded_utc': packet['downloaded_utc'],
                            'sha256': hashlib.sha256(payload).hexdigest()})
            memo[key] = packet['values']
        return memo[key]
    checks = []
    for series, (day, value) in expected.items():
        current, old = get(series), get(series, date(2026, 10, 5))
        result = compare(current, old)
        passed = str(result['known_date']) == day and result['known_value'] == value
        checks.append(passed)
        lines.append(f'{series}: {result}; expected {day} / {value}; {"PASS" if passed else "FAIL"}')
    current, old = get('PAYEMS'), get('PAYEMS', date(2025, 1, 15))
    result = compare(current, old)
    december = date(2024, 12, 1)
    passed = max(old) == december and old.get(december) == 159536 and current.get(december, float('inf')) < 159536 and result['revised_count'] > 0
    checks.append(passed)
    lines.append(f'PAYEMS Dec 2024: known {old.get(december)}, current {current.get(december)}, revised count {result["revised_count"]}; {"PASS" if passed else "FAIL"}')
    for vintage in (month_end, today):
        result = compare(get('DGS10'), get('DGS10', vintage))
        lines.append(f'Portfolio DGS10 as known {vintage}: {result}')
    for day in (date(2026, 10, 23), date(2026, 10, 26), date(2026, 10, 27)):
        lines.append(f'DGS10 page cross-check {day}: CSV {get("DGS10").get(day)}')
    (DATA / 'manifest.json').write_text(json.dumps(records, indent=2), encoding='utf-8')
    output = io.StringIO()
    result = unittest.TextTestRunner(stream=output, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromName('test_lab17'))
    lines.append(output.getvalue())
    lines.append(f'Live checks: {sum(checks)}/{len(checks)}; offline tests successful: {result.wasSuccessful()}')
    report = '\n'.join(lines)
    (ROOT / 'lab17_verification.txt').write_text(report, encoding='utf-8')
    print(report)
    return 0 if all(checks) and result.wasSuccessful() else 1

if __name__ == '__main__':
    raise SystemExit(main())

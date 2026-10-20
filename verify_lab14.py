"""Save reproducible lab evidence without changing Lab 13 verification.txt."""
import copy
import csv
import io
import math
import json
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
from contextlib import redirect_stdout
import unittest
import mandate
import portfolio as p

root = Path(__file__).resolve().parent
output = io.StringIO()
with redirect_stdout(output):
    p.main()
    print('\nMANDATE CHECKS (including benchmark E)')
    mandate.main()
    # Preserve and verify the previous lab's original verdicts.
    for name, failures in [('A', 0), ('B', 3), ('C', 1), ('D', 0), ('E', 1)]:
        assert sum(not row[2] for row in mandate.check_candidate(mandate.CANDIDATES[name])) == failures
    corr = copy.deepcopy(p.CORRELATIONS)
    corr[2][3] = corr[3][2] = .5
    print(f'\nCorrelation 0.50 probe: {100*p.portfolio_volatility([0, 0, .4, .6], p.covariance_matrix(p.SLEEVES, corr)):.2f}%')
    corr[2][3] = corr[3][2] = 1.3
    try:
        p.covariance_matrix(p.SLEEVES, corr)
        raise AssertionError('Invalid correlation accepted')
    except ValueError as exc:
        print(f'Correlation 1.3 rejected: {exc}')
    print(f'Delivered IG/equity correlation: {p.CORRELATIONS[2][3]}')
    with (root / 'prices.csv').open(newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        assert reader.fieldnames == ['Date', 'BIL', 'IEF', 'LQD', 'VT']
        rows = list(reader)
    assert len(rows) == 60
    dates = [r['Date'] for r in rows]
    assert dates == sorted(set(dates))
    for row in rows:
        for ticker in ['BIL', 'IEF', 'LQD', 'VT']:
            assert math.isfinite(float(row[ticker])) and float(row[ticker]) > 0
    expected_months = [f'{year}-{month:02}' for year in range(2021, 2027)
                       for month in range(1, 13)
                       if '2021-10' <= f'{year}-{month:02}' <= '2026-09']
    assert [d[:7] for d in dates] == expected_months
    for ticker in ['BIL', 'IEF', 'LQD', 'VT']:
        raw = json.loads((root / 'lab14_data' / f'{ticker}.json').read_text())
        chart = raw['chart']['result'][0]
        assert chart['meta']['symbol'] == ticker
        assert chart['meta']['currency'] == 'USD'
        month_ends = {}
        for stamp, value in zip(chart['timestamp'], chart['indicators']['adjclose'][0]['adjclose']):
            date = datetime.fromtimestamp(stamp, ZoneInfo('America/New_York')).date().isoformat()
            if value is not None:
                month_ends[date[:7]] = (date, value)
        for row in rows:
            date, value = month_ends[row['Date'][:7]]
            assert row['Date'] == date
            assert float(row[ticker]) == value
    print(f'CSV validated: {len(rows)} rows, four funds, {dates[0]} to {dates[-1]}, no missing prices.')
    print('All 240 price cells reconcile exactly to saved Yahoo adjusted-close responses; every month is present.')
result = unittest.TextTestRunner(stream=output, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromName('test_portfolio'))
(root / 'lab14_verification.txt').write_text(output.getvalue(), encoding='utf-8')
print(output.getvalue())
if not result.wasSuccessful():
    raise SystemExit(1)

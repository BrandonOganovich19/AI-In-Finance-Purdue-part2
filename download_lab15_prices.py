"""Download Yahoo adjusted closes; save raw responses for provenance.

Standard library only. Completed months Oct 2021-Sep 2026 (60 prices,
59 subsequent monthly returns). No filling, interpolation or synthetic data.
"""
import csv
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_lab15

TICKERS = ['VTI', 'QQQ', 'VOO', 'SCHD']
ROOT = Path(__file__).resolve().parent


def main():
    start = int(datetime(2021, 10, 1, tzinfo=timezone.utc).timestamp())
    end = int(datetime(2026, 10, 1, tzinfo=timezone.utc).timestamp())
    raw_dir = ROOT / 'lab15_data'
    raw_dir.mkdir(exist_ok=True)
    series, sources = {}, {}
    for ticker in TICKERS:
        url = f'https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?period1={start}&period2={end}&interval=1d&events=div%2Csplits'
        request = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urlopen(request, timeout=60) as response:
            data = json.load(response)
        (raw_dir / f'{ticker}.json').write_text(json.dumps(data), encoding='utf-8')
        chart = data['chart']['result'][0]
        adjusted = chart['indicators']['adjclose'][0]['adjclose']
        monthly = {}
        for stamp, value in zip(chart['timestamp'], adjusted):
            date = datetime.fromtimestamp(stamp, ZoneInfo('America/New_York')).date().isoformat()
            if value is not None and math.isfinite(value) and value > 0:
                monthly[date[:7]] = (date, value)
        expected = [f'{year}-{month:02}' for year in range(2021, 2027) for month in range(1, 13)
                    if '2021-10' <= f'{year}-{month:02}' <= '2026-09']
        if sorted(monthly) != expected:
            raise ValueError(f'{ticker}: incomplete or unexpected monthly coverage; refusing CSV export.')
        series[ticker] = monthly
        sources[ticker] = url
    rows = []
    for month in expected:
        dates = {series[t][month][0] for t in TICKERS}
        if len(dates) != 1:
            raise ValueError(f'Misaligned month-end dates: {month}')
        rows.append([dates.pop()] + [series[t][month][1] for t in TICKERS])
    with (ROOT / 'prices.csv').open('w', newline='', encoding='utf-8') as output:
        writer = csv.writer(output)
        writer.writerow(['Date'] + TICKERS)
        writer.writerows(rows)
    metadata = {'downloaded_utc': datetime.now(timezone.utc).isoformat(), 'sources': sources,
                'currency': 'USD', 'field': 'adjclose', 'sampling': 'last available daily adjusted close of each completed month',
                'rows': len(rows), 'first_date': rows[0][0], 'last_date': rows[-1][0]}
    (raw_dir / 'metadata.json').write_text(json.dumps(metadata, indent=2), encoding='utf-8')
    print(json.dumps(metadata, indent=2))


if __name__ == '__main__':
    main()

# This project was made with Codex. I am not a financial advisor.
# For educational purposes only; this is not investment advice.


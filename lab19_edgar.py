"""Keyless SEC data access and deterministic Lab 18 calculations (standard library)."""
from __future__ import annotations
import argparse
from datetime import date, datetime, timezone
from decimal import Decimal
import hashlib
import json
import os
from pathlib import Path
import re
import time
from urllib.request import Request, urlopen

TAGS = {
    'revenue': ['RevenueFromContractWithCustomerExcludingAssessedTax', 'Revenues'],
    'net_income': ['NetIncomeLoss'],
    'operating_cash_flow': ['NetCashProvidedByUsedInOperatingActivities'],
    'capital_spending': ['PaymentsToAcquirePropertyPlantAndEquipment', 'PaymentsToAcquireProductiveAssets'],
    'equity': ['StockholdersEquity'],
}
LABELS = dict(zip(TAGS, ['Revenue', 'Net income', 'Operating cash flow', 'Capital spending', 'Equity']))
ROOT = Path(__file__).resolve().parent

def ticker_symbol(value):
    value = value.strip().upper()
    if not re.fullmatch(r'[A-Z][A-Z0-9.-]{0,9}', value):
        raise ValueError('Enter a valid ticker (letters, numbers, dot or hyphen).')
    return value

def download(url, user_agent, destination):
    if not re.search(r'\S+@\S+\.\S+', user_agent) or len(user_agent.split()) < 2:
        raise ValueError('SEC User-Agent must contain your name and contact email.')
    # Two requests per company, serial and comfortably below SEC rate limits.
    time.sleep(0.2)
    with urlopen(Request(url, headers={'User-Agent': user_agent, 'Accept': 'application/json'}), timeout=45) as response:
        raw = response.read()
    data = json.loads(raw)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(raw)
    metadata = {'url': url, 'retrieved_utc': datetime.now(timezone.utc).isoformat(),
                'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}
    destination.with_suffix('.source.json').write_text(json.dumps(metadata, indent=2), encoding='utf-8')
    return data, metadata

def fetch_company(ticker, user_agent, directory):
    ticker = ticker_symbol(ticker)
    directory = Path(directory)
    mapping, _ = download('https://www.sec.gov/files/company_tickers.json', user_agent, directory / 'company_tickers.json')
    match = next((v for v in mapping.values() if v['ticker'].upper() == ticker), None)
    if match is None:
        raise ValueError(f'{ticker} was not found in the SEC ticker directory.')
    cik = int(match['cik_str'])
    url = f'https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json'
    return download(url, user_agent, directory / f'{ticker}_companyfacts.json')

def annual(fact):
    """Allow a 52/53-week or calendar year; reject quarterly and YTD flows."""
    try:
        days = (date.fromisoformat(fact['end']) - date.fromisoformat(fact['start'])).days + 1
        return 350 <= days <= 380
    except (KeyError, TypeError, ValueError):
        return False

def usable(fact):
    return (fact.get('form') == '10-K' and isinstance(fact.get('val'), (int, float))
            and not isinstance(fact.get('val'), bool)
            and Decimal(str(fact['val'])).is_finite())

def fiscal_ends(facts):
    """One current annual end per 10-K accession, not the observation's `fy`."""
    filings = {}
    for tag in facts.values():
        for fact in tag.get('units', {}).get('USD', []):
            if usable(fact) and annual(fact):
                accession = fact.get('accn', fact.get('filed', ''))
                filings[accession] = max(filings.get(accession, ''), fact['end'])
    return sorted(set(filings.values()))[-5:]

def select_fact(facts, tags, end, instant=False):
    for tag in tags:  # The assignment's tag priority precedes filing recency.
        candidates = [f for f in facts.get(tag, {}).get('units', {}).get('USD', [])
                      if usable(f) and f.get('end') == end
                      and (('start' not in f) if instant else annual(f))]
        if candidates:
            latest = max(candidates, key=lambda f: (f.get('filed', ''), f.get('accn', ''), f.get('start', '')))
            return {'value': latest['val'], 'tag': tag, 'start': latest.get('start'),
                    'end': end, 'filed': latest.get('filed'), 'accn': latest.get('accn'), 'form': '10-K'}
    return {'value': None, 'tag': None, 'searched_tags': tags, 'end': end}

def make_year_row(facts, end):
    """Explain this function line by line during the lab's no-AI exercise."""
    row = {'fiscal_year_end': end}
    for metric, tags in TAGS.items():
        row[metric] = select_fact(facts, tags, end, instant=(metric == 'equity'))
    ni = row['net_income']['value']
    equity = row['equity']['value']
    ocf = row['operating_cash_flow']['value']
    capex = row['capital_spending']['value']
    row['roe'] = None if ni is None or equity is None or equity <= 0 else str(Decimal(str(ni)) / Decimal(str(equity)))
    row['owner_earnings'] = None if ocf is None or capex is None else ocf - capex
    return row

def checks(rows):
    roe = [r['roe'] for r in rows]
    oe = [r['owner_earnings'] for r in rows]
    def all_years(values, condition):
        if len(values) != 5 or any(v is None for v in values):
            return 'not known'
        return 'pass' if all(condition(Decimal(str(v))) for v in values) else 'fail'
    growth = 'not known' if len(rows) != 5 or oe[0] is None or oe[-1] is None else ('pass' if oe[-1] > oe[0] else 'fail')
    return {'ROE at least 15.0% every year': all_years(roe, lambda x: x >= Decimal('0.15')),
            'Owner earnings positive every year': all_years(oe, lambda x: x > 0),
            'Owner earnings grew first to last': growth}

def analyze(company, ticker, source=None):
    facts = company.get('facts', {}).get('us-gaap', {})
    ends = fiscal_ends(facts)
    if not ends:
        raise ValueError('No eligible annual USD facts from 10-K filings were found.')
    rows = [make_year_row(facts, end) for end in ends]
    return {'ticker': ticker_symbol(ticker), 'company': company.get('entityName', ticker),
            'cik': company.get('cik'), 'source': source or {}, 'rows': rows, 'checks': checks(rows)}

def money(value):
    if value is None:
        return 'not found'
    amount = Decimal(str(value)) / Decimal(1000000)
    return f'{amount:,.3f}'.rstrip('0').rstrip('.') if amount % 1 else f'{amount:,.0f}'

def percent(value):
    return 'not known' if value is None else f'{Decimal(value) * 100:.1f}%'

def report_text(result):
    lines = [f"# {result['ticker']} — {result['company']}", '',
             'Source: SEC EDGAR company facts; 10-K only. USD millions; fiscal-year-end labels.',
             'ROE = net income / year-end equity. Owner earnings = operating cash flow - capital spending.', '',
             '| Fiscal year end | Revenue | Net income | Operating cash flow | Capital spending | Equity | ROE | Owner earnings |',
             '|---|---:|---:|---:|---:|---:|---:|---:|']
    for row in result['rows']:
        cells = [row['fiscal_year_end']] + [money(row[k]['value']) for k in TAGS] + [percent(row['roe']), money(row['owner_earnings'])]
        lines.append('| ' + ' | '.join(cells) + ' |')
    lines += ['', '## Code-computed checks'] + [f'- {k}: **{v}**' for k, v in result['checks'].items()]
    lines += ['', '## XBRL provenance', '', '| Fiscal year end | Metric | XBRL tag | Period start | Filed | Accession |', '|---|---|---|---|---|---|']
    for row in result['rows']:
        for key in TAGS:
            f = row[key]
            lines.append('| ' + ' | '.join([row['fiscal_year_end'], LABELS[key], f.get('tag') or 'not found (' + ', '.join(TAGS[key]) + ')', f.get('start') or ('instant' if key == 'equity' else 'not found'), f.get('filed') or 'not found', f.get('accn') or 'not found']) + ' |')
        lines.append(f"| {row['fiscal_year_end']} | ROE (derived) | NetIncomeLoss / StockholdersEquity | annual / instant | — | — |")
        lines.append(f"| {row['fiscal_year_end']} | Owner earnings (derived) | {row['operating_cash_flow'].get('tag') or 'not found'} - {row['capital_spending'].get('tag') or 'not found'} | annual | — | — |")
    return '\n'.join(lines) + '\n'

# Match complete numeric tokens, preserving signs and percent units. Never accept
# 40.0% merely because a filing accession contains 40 or a cash value is 40.
NUMBER = re.compile(r'(?<![\d.])[-+−]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?%?(?!\d|\.\d)')

def number_tokens(text):
    return [(m.group(), m.start()) for m in NUMBER.finditer(text)]

def unsupported_numbers(memo, printed):
    allowed = {token for token, _ in number_tokens(printed)}
    return [{'number': token, 'line': memo.count('\n', 0, pos) + 1}
            for token, pos in number_tokens(memo) if token not in allowed]

def save_result(result, directory):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    ticker = result['ticker']
    (directory / f'{ticker}_analysis.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    report = report_text(result)
    (directory / f'{ticker}_facts.md').write_text(report, encoding='utf-8')
    return report

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('ticker')
    parser.add_argument('--user-agent', default=os.getenv('SEC_USER_AGENT', ''))
    parser.add_argument('--output-dir', type=Path, default=ROOT)
    parser.add_argument('--facts-file', type=Path, help='Replay an explicitly selected saved SEC response; no live download.')
    parser.add_argument('--check-memo', type=Path)
    args = parser.parse_args()
    try:
        ticker = ticker_symbol(args.ticker)
        if args.facts_file:
            raw = args.facts_file.read_bytes()
            company = json.loads(raw)
            mapping = json.loads((args.facts_file.parent / 'company_tickers.json').read_text(encoding='utf-8'))
            entry = next((v for v in mapping.values() if v['ticker'].upper() == ticker), None)
            if entry is None or int(entry['cik_str']) != int(company['cik']):
                raise ValueError('Saved company facts do not match the selected ticker.')
            source = json.loads(args.facts_file.with_suffix('.source.json').read_text())
            if hashlib.sha256(raw).hexdigest() != source['sha256']:
                raise ValueError('Saved SEC response failed its SHA-256 check.')
        else:
            company, source = fetch_company(ticker, args.user_agent, args.output_dir)
        result = analyze(company, ticker, source)
        printed = save_result(result, args.output_dir)
        print(printed)
        if args.check_memo:
            flags = unsupported_numbers(args.check_memo.read_text(encoding='utf-8'), printed)
            print(json.dumps({'unsupported_numbers': flags}, indent=2))
            return bool(flags)
    except (ValueError, OSError, KeyError) as error:
        parser.exit(2, f'Error: {error}\n')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())

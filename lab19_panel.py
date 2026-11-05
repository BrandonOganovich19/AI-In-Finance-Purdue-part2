"""Lab 19: deterministic panel on shared SEC annual facts; no model arithmetic."""
from decimal import Decimal
from pathlib import Path
import argparse
import hashlib
import json
import os
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import lab19_edgar as base

ROOT = Path(__file__).resolve().parent
EXTRA = {'liabilities': 'Liabilities', 'current_assets': 'AssetsCurrent',
         'current_liabilities': 'LiabilitiesCurrent'}
INVESTORS = ('Buffett', 'Graham', 'Burry')

def skill_threshold():
    return json.loads((ROOT / 'lab19_graham_rules.json').read_text(encoding='utf-8'))['current_ratio_min']

def ratio(numerator, denominator):
    if numerator is None or denominator is None or denominator <= 0 or numerator < 0:
        return None
    return str(Decimal(str(numerator)) / Decimal(str(denominator)))

def fmt_ratio(value):
    return 'not known' if value is None else f'{Decimal(value):.2f}'

def status(value, predicate):
    return 'not known' if value is None else ('pass' if predicate(Decimal(str(value))) else 'fail')

def all_five(values, predicate):
    # A missing year or value never becomes an assumed pass or zero.
    if len(values) != 5 or any(v is None for v in values):
        return 'not known'
    return 'pass' if all(predicate(Decimal(str(v))) for v in values) else 'fail'

def graham_checks(rows, threshold):
    """Explain this function in the required independent classroom exercise."""
    threshold = Decimal(str(threshold))
    if not threshold.is_finite() or threshold <= 0:
        raise ValueError('Graham threshold must be positive and finite.')
    income = [row['net_income']['value'] for row in rows]
    latest_ratio = rows[-1]['current_ratio'] if rows else None
    growth = None if len(income) != 5 or income[0] is None or income[-1] is None else Decimal(str(income[-1])) - Decimal(str(income[0]))
    return {
        f'Current ratio at least {threshold:.2f}, latest year': status(latest_ratio, lambda x: x >= threshold),
        'Net income positive every year': all_five(income, lambda x: x > 0),
        'Net income grew first to last': status(growth, lambda x: x > 0),
    }

def burry_checks(rows):
    surplus = [None if r['operating_cash_flow']['value'] is None or r['net_income']['value'] is None
               else Decimal(str(r['operating_cash_flow']['value'])) - Decimal(str(r['net_income']['value'])) for r in rows]
    return {'Operating cash flow at least net income every year': all_five(surplus, lambda x: x >= 0),
            'Liabilities no more than 2.00 times equity, latest year': status(rows[-1]['liabilities_equity'] if rows else None, lambda x: x <= 2)}

def analyze(company, ticker, source, threshold=None):
    threshold = skill_threshold() if threshold is None else threshold
    result = base.analyze(company, ticker, source)
    facts = company.get('facts', {}).get('us-gaap', {})
    for row in result['rows']:
        for key, tag in EXTRA.items():
            row[key] = base.select_fact(facts, [tag], row['fiscal_year_end'], instant=True)
        row['current_ratio'] = ratio(row['current_assets']['value'], row['current_liabilities']['value'])
        row['liabilities_equity'] = ratio(row['liabilities']['value'], row['equity']['value'])
    result['threshold'] = str(threshold)
    result['panel'] = {'Buffett': result['checks'], 'Graham': graham_checks(result['rows'], threshold),
                       'Burry': burry_checks(result['rows'])}
    return result

def load_saved(ticker, directory=ROOT, threshold=None):
    ticker = base.ticker_symbol(ticker)
    path = Path(directory) / f'lab19_{ticker}_companyfacts.json'
    raw = path.read_bytes()
    source = json.loads(path.with_suffix('.source.json').read_text(encoding='utf-8'))
    if hashlib.sha256(raw).hexdigest() != source['sha256']:
        raise ValueError('Saved SEC evidence failed SHA-256 verification.')
    company = json.loads(raw)
    mapping = json.loads((Path(directory) / 'lab19_company_tickers.json').read_text(encoding='utf-8'))
    match = next((v for v in mapping.values() if v['ticker'].upper() == ticker), None)
    if match is None or int(match['cik_str']) != int(company['cik']):
        raise ValueError('Ticker and SEC company identity do not match.')
    return analyze(company, ticker, source, threshold)

def panel_rows(result):
    return [{'Investor': investor, 'Check': check, 'Status': outcome}
            for investor, checks in result['panel'].items() for check, outcome in checks.items()]

def summary(checks):
    values = list(checks.values())
    return f"{values.count('pass')} of {len(values)} pass; {values.count('fail')} fail; {values.count('not known')} not known"

def report_text(result):
    text = base.report_text(result)
    lines = ['', '## Shared balance-sheet facts and derived ratios', '',
             'Amounts: USD millions. Ratios: times, rounded only for display.',
             'Current ratio = AssetsCurrent / LiabilitiesCurrent; liabilities/equity = Liabilities / StockholdersEquity.',
             'Nonpositive denominators and missing inputs produce not known. No substituted or estimated tags.', '',
             '| Fiscal year end | Liabilities | Current assets | Current liabilities | Current ratio | Liabilities/equity |',
             '|---|---:|---:|---:|---:|---:|']
    for r in result['rows']:
        lines.append('| ' + ' | '.join([r['fiscal_year_end']] + [base.money(r[k]['value']) for k in EXTRA]
                                      + [fmt_ratio(r['current_ratio']), fmt_ratio(r['liabilities_equity'])]) + ' |')
    lines += ['', '## Panel', '', '| Investor | Check | Status |', '|---|---|---|']
    lines += [f"| {r['Investor']} | {r['Check']} | {r['Status']} |" for r in panel_rows(result)]
    lines += ['', *[f'- {name}: {summary(checks)}' for name, checks in result['panel'].items()]]
    lines += ['', '## Additional fact provenance', '', '| Fiscal year end | Tag | Filed | Accession |', '|---|---|---|---|']
    for r in result['rows']:
        for key, tag in EXTRA.items():
            f = r[key]
            lines.append(f"| {r['fiscal_year_end']} | {f.get('tag') or 'not found: ' + tag} | {f.get('filed') or 'not found'} | {f.get('accn') or 'not found'} |")
    lines += ['', '## Source snapshot', '', json.dumps(result['source'], indent=2)]
    return text + '\n'.join(lines) + '\n'

def audit_memos(memos, printed):
    return [{'investor': name, **flag} for name, memo in memos.items()
            for flag in base.unsupported_numbers(memo, printed)]

def read_memos(ticker, directory=ROOT):
    return {name: (Path(directory) / f'lab19_{ticker}_{name.lower()}_memo.md').read_text(encoding='utf-8')
            if (Path(directory) / f'lab19_{ticker}_{name.lower()}_memo.md').exists() else '' for name in INVESTORS}

def save(result, directory=ROOT):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    ticker = result['ticker']
    (directory / f'lab19_{ticker}_panel.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    printed = report_text(result)
    (directory / f'lab19_{ticker}_panel.md').write_text(printed, encoding='utf-8')
    return printed

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('ticker')
    parser.add_argument('--directory', type=Path, default=ROOT)
    parser.add_argument('--threshold', default=None)
    parser.add_argument('--live', action='store_true')
    parser.add_argument('--check-memos', action='store_true')
    args = parser.parse_args()
    try:
        if args.live:
            company, source = base.fetch_company(args.ticker, os.getenv('SEC_USER_AGENT', ''), args.directory / 'lab19_live_cache')
            for name in [f'{base.ticker_symbol(args.ticker)}_companyfacts.json', f'{base.ticker_symbol(args.ticker)}_companyfacts.source.json', 'company_tickers.json', 'company_tickers.source.json']:
                (args.directory / 'lab19_live_cache' / name).replace(args.directory / ('lab19_' + name))
            result = analyze(company, args.ticker, source, args.threshold)
        else:
            result = load_saved(args.ticker, args.directory, args.threshold)
        printed = save(result, args.directory)
        print(printed)
        if args.check_memos:
            memos = read_memos(result['ticker'], args.directory)
            flags = audit_memos(memos, printed)
            missing = [name for name, memo in memos.items() if not memo.strip()]
            print(json.dumps({'unprinted_numbers': flags, 'missing_memos': missing}, indent=2))
            return bool(flags or missing)
        return 0
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(2, f'Error: {exc}\n')

if __name__ == '__main__':
    raise SystemExit(main())

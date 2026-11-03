"""Compare user-supplied browser figures to calculations from saved SEC facts."""
from pathlib import Path
import sys
from decimal import Decimal
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from test_lab18 import load
from lab18_edgar import percent

rows=load('COST')['rows']
browser=['30.6%','27.5%','30.3%','30.7%','28.4%']
lines=['# Fresh-chat numerical comparison','',
       'Browser figures are user-supplied. SEC figures are computed from the saved, hash-checked download.', '',
       '| Fiscal end | Browser ROE | Required year-end ROE | Browser minus required (percentage points) | Average-equity ROE recomputed |',
       '|---|---:|---:|---:|---:|']
for i,(r,b) in enumerate(zip(rows,browser)):
    actual=percent(r['roe'])
    difference=Decimal(b.rstrip('%'))-Decimal(actual.rstrip('%'))
    average='Not recomputed: prior equity outside displayed window'
    if i:
        equity=(Decimal(rows[i-1]['equity']['value'])+Decimal(r['equity']['value']))/2
        average=percent(str(Decimal(r['net_income']['value'])/equity))
    lines.append(f"| {r['fiscal_year_end']} | {b} | {actual} | {difference:+.1f} | {average} |")
lines += ['', 'Differences use displayed, rounded percentages. Average-equity calculations retain precision until presentation.', '',
          'The browser explicitly chose average equity, whereas the lab mandates year-end equity. Its net income and ending equity agree with the SEC table, but its ROE column answers a different question. Its named secondary sources lack direct URLs, XBRL tags, accession numbers, and filing-selection rules. The supplied transcript therefore does not establish their provenance.', '',
          'The FY2023–FY2026 average-equity results are reproducible from adjacent SEC equity balances. FY2022 requires the preceding equity balance, so no unsupported reconstruction is supplied here. FY2024 year-end ROE is higher, not lower, than average-equity ROE because closing equity is below the adjacent-year average. A decrease in the denominator can raise ROE without improved operating performance.', '',
          'The browser also introduces prices, EPS, valuation multiples, and historical anecdotes outside this lab. Those claims were not used in either memo and are not independently verified here. A plausible narrative is not a substitute for a reproducible extraction rule.']
text='\n'.join(lines)+'\n'
(ROOT/'fresh_chat_comparison.md').write_text(text,encoding='utf-8')
print(text)

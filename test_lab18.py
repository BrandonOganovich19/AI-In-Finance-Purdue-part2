"""Independent answer-table assertions and financial boundary cases."""
import copy
from decimal import Decimal
import hashlib
import io
import json
from pathlib import Path
import sys
import unittest
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import lab18_edgar as edgar

def load(ticker):
    path = ROOT / f'{ticker}_companyfacts.json'
    source = json.loads(path.with_suffix('.source.json').read_text())
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == source['sha256']
    return edgar.analyze(json.loads(raw), ticker, source)

def fact(value=100, **changes):
    result = dict(val=value, start='2024-01-01', end='2024-12-31', form='10-K',
                  filed='2025-02-01', accn='a', fy=2024, fp='FY')
    result.update(changes)
    return result

def wrap(values):
    return {'units': {'USD': values}}

class FinanceTests(unittest.TestCase):
    def test_cost_every_answer_cell(self):
        expected = [
            ['2022-08-28',226954,5844,7392,3891,20642,'28.3%',3501],
            ['2023-09-03',242290,6292,11068,4323,25058,'25.1%',6745],
            ['2024-09-01',254453,7367,11339,4710,23622,'31.2%',6629],
            ['2025-08-31',275235,8099,13335,5498,29164,'27.8%',7837],
            ['2026-08-30',303154,9226,15817,6435,35803,'25.8%',9382],
        ]
        result = load('COST')
        actual = [[r['fiscal_year_end']] + [r[k]['value']/1e6 for k in edgar.TAGS]
                  + [edgar.percent(r['roe']), r['owner_earnings']/1e6] for r in result['rows']]
        self.assertEqual(actual, expected)
        self.assertEqual(list(result['checks'].values()), ['pass']*3)

    def test_jpm_missing_capex_does_not_become_zero(self):
        result = load('JPM')
        for r in result['rows']:
            self.assertIsNone(r['capital_spending']['value'])
            self.assertIsNone(r['owner_earnings'])
        self.assertEqual(list(result['checks'].values()), ['fail','not known','not known'])
        self.assertIn('cannot judge owner earnings', (ROOT/'JPM_memo.md').read_text())

    def test_latest_filing_and_annual_flow_only(self):
        data = {'NetIncomeLoss': wrap([fact(10), fact(20, filed='2026-01-01', fy=2025),
                                      fact(999, start='2024-10-01', filed='2027-01-01'),
                                      fact(777, form='10-Q', filed='2028-01-01')])}
        picked = edgar.select_fact(data, ['NetIncomeLoss'], '2024-12-31')
        self.assertEqual(picked['value'],20)
        self.assertEqual(picked['filed'],'2026-01-01')

    def test_tag_priority_and_fallback(self):
        first, second = edgar.TAGS['revenue']
        data = {first: wrap([fact(11)]), second: wrap([fact(22, filed='2026-01-01')])}
        self.assertEqual(edgar.select_fact(data,[first,second],'2024-12-31')['value'],11)
        del data[first]
        self.assertEqual(edgar.select_fact(data,[first,second],'2024-12-31')['value'],22)
        a,b = edgar.TAGS['capital_spending']
        self.assertEqual(edgar.select_fact({b:wrap([fact(8)])},[a,b],'2024-12-31')['tag'],b)

    def test_leap_year_and_53_week_periods(self):
        self.assertTrue(edgar.annual(fact()))
        self.assertTrue(edgar.annual(fact(start='2022-08-29',end='2023-09-03')))
        self.assertFalse(edgar.annual(fact(start='2024-07-01')))
        self.assertFalse(edgar.annual(fact(start='2023-01-01')))
        self.assertFalse(edgar.annual({'end':'invalid'}))

    def test_equity_nonpositive_and_missing_inputs(self):
        for equity in [0, -5, None]:
            instant = fact(equity)
            del instant['start']
            row = edgar.make_year_row({'NetIncomeLoss':wrap([fact(15)]), 'StockholdersEquity':wrap([instant])}, '2024-12-31')
            self.assertIsNone(row['roe'])
            self.assertIsNone(row['owner_earnings'])
            self.assertEqual(edgar.checks([row]*5)['ROE at least 15.0% every year'],'not known')

    def test_roe_threshold_uses_unrounded_value(self):
        rows = [{'roe': '0.15', 'owner_earnings': n+1} for n in range(5)]
        self.assertEqual(list(edgar.checks(rows).values()),['pass']*3)
        rows[0]['roe']='0.14999'
        self.assertEqual(edgar.percent(rows[0]['roe']),'15.0%')
        self.assertEqual(list(edgar.checks(rows).values())[0],'fail')

    def test_owner_earnings_zero_negative_and_growth(self):
        rows = [{'roe':'0.2','owner_earnings':5} for _ in range(5)]
        self.assertEqual(list(edgar.checks(rows).values()),['pass','pass','fail'])
        for value in [0,-1]:
            rows[2]['owner_earnings']=value
            self.assertEqual(list(edgar.checks(rows).values())[1],'fail')
        rows[2]['owner_earnings']=None
        self.assertEqual(list(edgar.checks(rows).values())[1],'not known')
        self.assertEqual(list(edgar.checks(rows[:4]).values()),['not known']*3)

    def test_row_formula_and_instant_selection(self):
        equity=fact(200); del equity['start']
        facts={'NetIncomeLoss':wrap([fact(-20)]), 'StockholdersEquity':wrap([equity,fact(999)]),
               'NetCashProvidedByUsedInOperatingActivities':wrap([fact(25)]),
               'PaymentsToAcquirePropertyPlantAndEquipment':wrap([fact(30)])}
        row=edgar.make_year_row(facts,'2024-12-31')
        self.assertEqual(Decimal(row['roe']),Decimal('-0.1'))
        self.assertEqual(row['owner_earnings'],-5)

    def test_fiscal_end_not_filing_fy_or_quarter(self):
        values=[fact(1,end=f'{y}-12-31', start=f'{y}-01-01',accn=str(y),fy=y+2) for y in range(2018,2025)]
        values += [fact(1,start='2025-01-01',end='2025-03-31',form='10-Q',accn='q')]
        self.assertEqual(edgar.fiscal_ends({'NetIncomeLoss':wrap(values)}),[f'{y}-12-31' for y in range(2020,2025)])

    def test_invalid_and_empty_data(self):
        for symbol in ['','../COST','COST; rm','A/B']:
            with self.assertRaises(ValueError): edgar.ticker_symbol(symbol)
        with self.assertRaises(ValueError): edgar.analyze({},'COST')
        self.assertEqual(edgar.ticker_symbol(' cost '),'COST')
        for value in [float('nan'),float('inf'),True,'100']:
            self.assertFalse(edgar.usable(fact(value)))

    def test_clean_memos_and_hand_typed_probe(self):
        for ticker in ['COST','JPM']:
            report=edgar.report_text(load(ticker))
            memo=(ROOT/f'{ticker}_memo.md').read_text(encoding='utf-8')
            self.assertEqual(edgar.unsupported_numbers(memo,report),[])
        edited=memo+'\nUnsupported ROE: 40.0%. Another claim: 999,999.\nAgain 40.0%.'
        flags=edgar.unsupported_numbers(edited,report)
        self.assertEqual([f['number'] for f in flags],['40.0%','999,999','40.0%'])

    def test_audit_sign_unit_and_substring(self):
        allowed='25.8% 9,382 -147,782 40'
        for unsupported in ['25.8','9382','147,782','40.0%','125.8%']:
            self.assertTrue(edgar.unsupported_numbers(unsupported,allowed))
        self.assertEqual(edgar.unsupported_numbers('ROE 25.8%. Cash -147,782.',allowed),[])

if __name__=='__main__':
    output=io.StringIO()
    result=unittest.TextTestRunner(stream=output,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(FinanceTests))
    text=output.getvalue()
    (ROOT/'calculation_tests.txt').write_text(text,encoding='utf-8')
    print(text)
    raise SystemExit(not result.wasSuccessful())

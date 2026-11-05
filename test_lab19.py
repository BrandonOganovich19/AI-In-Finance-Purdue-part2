"""Known answers, boundary behavior, missing-data propagation, and memo audits."""
import copy
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import lab19_panel as panel

class PanelTests(unittest.TestCase):
    def setUp(self):
        self.cost = panel.load_saved('COST')

    def test_known_cost_all_years_and_all_checks(self):
        self.assertEqual([r['fiscal_year_end'] for r in self.cost['rows']],
                         ['2022-08-28','2023-09-03','2024-09-01','2025-08-31','2026-08-30'])
        self.assertEqual([panel.fmt_ratio(r['current_ratio']) for r in self.cost['rows']], ['1.02','1.07','0.97','1.03','1.06'])
        self.assertEqual([panel.fmt_ratio(r['liabilities_equity']) for r in self.cost['rows']], ['2.11','1.75','1.96','1.64','1.49'])
        self.assertEqual([list(x.values()) for x in self.cost['panel'].values()],
                         [['pass']*3, ['fail','pass','pass'], ['pass']*2])

    def test_probe_uses_skill_config_and_restores_it(self):
        path = ROOT / 'lab19_graham_rules.json'
        original = path.read_bytes()
        try:
            path.write_text(json.dumps({'current_ratio_min':'1.00'}), encoding='utf-8')
            self.assertEqual(list(panel.load_saved('COST')['panel']['Graham'].values()), ['pass']*3)
        finally:
            path.write_bytes(original)
        self.assertEqual(list(panel.load_saved('COST')['panel']['Graham'].values())[0], 'fail')

    def test_nvda_divergence_from_real_facts(self):
        result = panel.load_saved('NVDA')
        self.assertEqual([list(x.values()) for x in result['panel'].values()],
                         [['pass']*3, ['pass']*3, ['fail','pass']])
        latest = result['rows'][-1]
        self.assertEqual(latest['operating_cash_flow']['value'], 102718000000)
        self.assertEqual(latest['net_income']['value'], 120067000000)
        self.assertEqual(panel.fmt_ratio(latest['current_ratio']), '3.91')
        self.assertEqual(panel.fmt_ratio(latest['liabilities_equity']), '0.31')

    def test_inclusive_ratio_boundaries_unrounded(self):
        rows = copy.deepcopy(self.cost['rows'])
        rows[-1]['current_ratio'] = '2.00'
        self.assertEqual(list(panel.graham_checks(rows,'2.00').values())[0], 'pass')
        rows[-1]['current_ratio'] = '1.999999'
        self.assertEqual(panel.fmt_ratio(rows[-1]['current_ratio']), '2.00')
        self.assertEqual(list(panel.graham_checks(rows,'2.00').values())[0], 'fail')
        rows[-1]['liabilities_equity'] = '2.00'
        self.assertEqual(list(panel.burry_checks(rows).values())[-1], 'pass')
        rows[-1]['liabilities_equity'] = '2.000001'
        self.assertEqual(list(panel.burry_checks(rows).values())[-1], 'fail')

    def test_zero_negative_missing_and_incomplete(self):
        for denominator in [0,-1,None]:
            self.assertIsNone(panel.ratio(5,denominator))
        self.assertIsNone(panel.ratio(None,5))
        self.assertIsNone(panel.ratio(-1,5))
        self.assertEqual(panel.ratio(0,5),'0')
        for value in [0,-100]:
            rows = copy.deepcopy(self.cost['rows'])
            rows[2]['net_income']['value'] = value
            self.assertEqual(list(panel.graham_checks(rows,2).values())[1], 'fail')
        rows[2]['net_income']['value'] = None
        self.assertEqual(list(panel.graham_checks(rows,2).values())[1], 'not known')
        self.assertEqual(list(panel.burry_checks(rows).values())[0], 'not known')
        self.assertEqual(list(panel.graham_checks(rows[:4],2).values())[1:], ['not known']*2)
        self.assertTrue(all(x == 'not known' for x in panel.graham_checks([],2).values()))
        for threshold in ['NaN','Infinity','0','-1']:
            with self.assertRaises(ValueError):
                panel.graham_checks(rows,threshold)

    def test_growth_equality_and_cash_equality(self):
        rows = copy.deepcopy(self.cost['rows'])
        rows[-1]['net_income']['value'] = rows[0]['net_income']['value']
        self.assertEqual(list(panel.graham_checks(rows,2).values())[-1], 'fail')
        for row in rows:
            row['operating_cash_flow']['value'] = row['net_income']['value']
        self.assertEqual(list(panel.burry_checks(rows).values())[0], 'pass')

    def test_honest_jpm_gaps(self):
        result = panel.load_saved('JPM')
        self.assertTrue(all(r['capital_spending']['value'] is None for r in result['rows']))
        self.assertEqual(list(result['panel']['Buffett'].values())[1:], ['not known']*2)
        self.assertEqual(list(result['panel']['Graham'].values())[0], 'not known')
        self.assertIn('not found',panel.report_text(result))

    def test_memo_flags_every_investor(self):
        for ticker in ['COST','NVDA','JPM']:
            printed = panel.report_text(panel.load_saved(ticker))
            memos = panel.read_memos(ticker)
            self.assertTrue(all(memos.values()))
            self.assertEqual(panel.audit_memos(memos,printed),[])
            for investor in panel.INVESTORS:
                edited = dict(memos)
                edited[investor] += '\nUnsupported claim: 987654321.123%.'
                flags = panel.audit_memos(edited,printed)
                self.assertEqual([f['investor'] for f in flags],[investor])
                self.assertEqual(flags[0]['number'],'987654321.123%')

    def test_new_tags_require_annual_filing_and_latest_instant(self):
        entries = [{'val':10,'end':'2025-12-31','form':'10-K','filed':'2026-02-01','accn':'a'},
                   {'val':20,'end':'2025-12-31','form':'10-K','filed':'2026-03-01','accn':'b'},
                   {'val':999,'end':'2025-12-31','form':'10-Q','filed':'2026-04-01','accn':'c'}]
        facts = {'AssetsCurrent': {'units': {'USD': entries}}}
        selected = panel.base.select_fact(facts,['AssetsCurrent'],'2025-12-31',instant=True)
        self.assertEqual(selected['value'],20)
        self.assertEqual(selected['accn'],'b')
        self.assertTrue(panel.base.annual({'start':'2023-01-01','end':'2023-12-31'}))
        self.assertTrue(panel.base.annual({'start':'2024-01-01','end':'2024-12-31'}))
        self.assertFalse(panel.base.annual({'start':'2024-10-01','end':'2024-12-31'}))

    def test_hash_and_company_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            dest = Path(directory)
            for name in ['lab19_COST_companyfacts.json','lab19_COST_companyfacts.source.json','lab19_company_tickers.json']:
                (dest/name).write_bytes((ROOT/name).read_bytes())
            with (dest/'lab19_COST_companyfacts.json').open('ab') as file:
                file.write(b' ')
            with self.assertRaisesRegex(ValueError,'SHA-256'):
                panel.load_saved('COST',dest)

if __name__ == '__main__':
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(PanelTests))
    (ROOT/'lab19_calculation_tests.txt').write_text(stream.getvalue(),encoding='utf-8')
    print(stream.getvalue())
    raise SystemExit(not result.wasSuccessful())

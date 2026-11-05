"""Integration tests of the actual Streamlit panel and all memo editors."""
from pathlib import Path
import io
import sys
import unittest
ROOT = Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
import run_lab19
from streamlit.testing.v1 import AppTest

class AppTests(unittest.TestCase):
    def test_panel_probe_company_gaps_and_all_memo_flags(self):
        app = AppTest.from_file(str(ROOT/'lab19_app.py')).run(timeout=30)
        self.assertEqual(len(app.exception),0)
        self.assertEqual([m.value for m in app.metric],['3 / 3 pass','2 / 3 pass','2 / 2 pass'])
        self.assertEqual(len(app.text_area),3)
        self.assertEqual(len(app.error),0)
        self.assertEqual(len(app.get('vega_lite_chart')),1)
        for index, investor in enumerate(['Buffett','Graham','Burry']):
            original = app.text_area[index].value
            app.text_area[index].set_value(original+'\nUnprinted 987654321.123%.').run()
            self.assertEqual(len(app.exception),0)
            self.assertIn('Unprinted memo numbers',app.error[0].value)
            flagged = [d.value for d in app.dataframe if 'investor' in d.value.columns][0]
            self.assertEqual(flagged.iloc[0]['investor'],investor)
            app.text_area[index].set_value(original).run()
            self.assertEqual(len(app.error),0)
        app.sidebar.selectbox(key='threshold').select('1.00').run()
        self.assertEqual(app.metric[1].value,'3 / 3 pass')
        self.assertTrue(any('Sensitivity probe' in w.value for w in app.warning))
        app.sidebar.selectbox(key='threshold').select('2.00').run()
        app.sidebar.text_input(key='ticker').set_value('NVDA').run()
        self.assertEqual(len(app.exception),0)
        self.assertEqual([m.value for m in app.metric],['3 / 3 pass','3 / 3 pass','1 / 2 pass'])
        self.assertEqual(len(app.error),0)
        app.sidebar.text_input(key='ticker').set_value('JPM').run()
        self.assertEqual(len(app.exception),0)
        self.assertTrue(any('not known' in str(d.value) for d in app.dataframe))
        self.assertEqual(len(app.error),0)
        app.sidebar.text_input(key='ticker').set_value('../BAD').run()
        self.assertEqual(len(app.exception),0)
        self.assertIn('valid ticker',app.error[0].value)

if __name__ == '__main__':
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(AppTests))
    (ROOT/'lab19_app_tests.txt').write_text(stream.getvalue(),encoding='utf-8')
    print(stream.getvalue())
    raise SystemExit(not result.wasSuccessful())

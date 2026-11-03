"""Exercise real saved SEC responses through Streamlit's AppTest."""
import io
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
import run_lab18
from streamlit.testing.v1 import AppTest

class AppTests(unittest.TestCase):
    def test_cost_jpm_and_tampered_memo(self):
        app=AppTest.from_file(str(ROOT/'lab18_app.py')).run(timeout=30)
        self.assertEqual(len(app.exception),0)
        self.assertIn('not investment advice',app.caption[0].value)
        self.assertEqual(len(app.get('vega_lite_chart')),1)
        self.assertEqual(app.dataframe[0].value.iloc[-1]['Owner earnings'],'9,382')
        self.assertEqual([m.value for m in app.metric],['PASS']*3)
        self.assertEqual(len(app.error),0)
        memo=app.text_area[0].value
        app.text_area[0].set_value(memo+'\nI claim ROE was 40.0%.').run()
        self.assertEqual(len(app.exception),0)
        self.assertIn('40.0%',app.error[0].value)
        app.text_area[0].set_value(memo).run()
        self.assertEqual(len(app.error),0)
        app.sidebar.text_input(key='ticker').set_value('JPM').run()
        self.assertEqual(len(app.exception),0)
        self.assertEqual([m.value for m in app.metric],['FAIL','NOT KNOWN','NOT KNOWN'])
        self.assertTrue(all(app.dataframe[0].value['Capital spending']=='not found'))
        self.assertEqual(len(app.error),0)
        app.sidebar.text_input(key='ticker').set_value('../BAD').run()
        self.assertEqual(len(app.exception),0)
        self.assertIn('valid ticker',app.error[0].value)

if __name__=='__main__':
    output=io.StringIO()
    result=unittest.TextTestRunner(stream=output,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(AppTests))
    text=output.getvalue()
    (ROOT/'app_tests.txt').write_text(text,encoding='utf-8')
    print(text)
    raise SystemExit(not result.wasSuccessful())

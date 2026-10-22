"""Exercise the real Streamlit page and its engine integration."""
import unittest
from unittest.mock import patch
from io import BytesIO
from pathlib import Path
from streamlit.testing.v1 import AppTest
import portfolio


class AppTests(unittest.TestCase):
    def test_current_equity_universe_upload(self):
        with patch('streamlit.delta_generator.DeltaGenerator.file_uploader', return_value=BytesIO(Path('prices.csv').read_bytes())):
            app = AppTest.from_file('app.py', default_timeout=30).run()
            app.sidebar.number_input[0].set_value(5.5).run()
            for last in (False,True):
                app.sidebar.checkbox[0].set_value(last).run()
                self.assertFalse(app.exception)
                self.assertEqual(len(app.warning),2)
                self.assertTrue(all(w.value == 'no mix meets the objective' for w in app.warning))
                self.assertEqual(len(app.metric),0)
                self.assertEqual(app.sidebar.number_input[0].value,5.5)
                self.assertEqual(app.sidebar.number_input[1].value,3.0)

    def test_meridian_widgets_and_infeasible(self):
        app = AppTest.from_file('app.py', default_timeout=30).run()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[0].value, '6.51%')
        app.number_input(key='return_meridian_False_3').set_value(7.0).run()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[0].value, '6.53%')
        self.assertEqual(app.metric[1].value, '12.94%')
        self.assertEqual(app.metric[-1].value, '25.00 percentage points')
        app.sidebar.number_input[0].set_value(20.0).run()
        self.assertEqual(len(app.warning), 2)

    def test_engine_correlation_reaches_page(self):
        corr = [row[:] for row in portfolio.CORRELATIONS]
        corr[2][3] = corr[3][2] = .5
        with patch.object(portfolio, 'CORRELATIONS', corr):
            app = AppTest.from_file('app.py', default_timeout=30).run()
            self.assertFalse(app.exception)
            self.assertEqual(app.metric[0].value, '6.52%')
            self.assertEqual(app.metric[1].value, '9.73%')

    def test_reported_partner_attack_on_page(self):
        app = AppTest.from_file('app.py', default_timeout=30).run()
        app.number_input(key='return_meridian_False_2').set_value(4.0).run()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[0].value,'6.52%')
        self.assertEqual(app.metric[1].value,'9.73%')
        self.assertEqual(app.metric[-1].value,'25.00 percentage points')
        self.assertEqual(list(app.table[0].value['Weight (%)']),['0.00','40.00','0.00','60.00'])

    def test_csv_windows_and_invalid_upload(self):
        # Mock only the upload widget's returned bytes; run the actual page and math.
        with patch('streamlit.delta_generator.DeltaGenerator.file_uploader', return_value=BytesIO(Path('lab14_data/prices.csv').read_bytes())):
            app = AppTest.from_file('app.py', default_timeout=30).run()
            app.sidebar.number_input[0].set_value(5.5)
            for checkbox in app.checkbox:
                if checkbox.label in ['BIL reserve-eligible', 'IEF reserve-eligible']:
                    checkbox.set_value(True)
            app.run()
            self.assertFalse(app.exception)
            self.assertEqual(app.metric[0].value, '5.51%')
            app.sidebar.checkbox[0].set_value(True).run()
            self.assertFalse(app.exception)
            self.assertEqual(app.metric[0].value, '5.95%')
            self.assertEqual(app.metric[-1].value, '15.00 percentage points')
        with patch('streamlit.delta_generator.DeltaGenerator.file_uploader', return_value=BytesIO(b'date,A\nwrong,0')):
            app = AppTest.from_file('app.py', default_timeout=30).run()
            self.assertFalse(app.exception)
            self.assertTrue(app.error)


if __name__ == '__main__':
    unittest.main(verbosity=2)

# This project was made with Codex. I am not a financial advisor.
# For educational purposes only; this is not investment advice.




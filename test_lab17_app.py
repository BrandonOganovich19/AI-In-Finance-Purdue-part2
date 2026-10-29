"""Streamlit UI checks against saved authentic downloads; no network required."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_lab17
import unittest
from datetime import date
from unittest.mock import patch
from streamlit.testing.v1 import AppTest
from asof_data import parse_csv, NAMES

ROOT = Path(__file__).resolve().parent

def saved_fetch(series, vintage=None):
    if series == 'NOTAREALSERIES':
        raise ValueError('Unknown series')
    path = ROOT / 'lab17_data' / f'{series}_{vintage or "current"}.csv'
    if not path.exists() and vintage == date.today():
        path = ROOT / 'lab17_data' / f'{series}_current.csv'
    raw = path.read_text(encoding='utf-8')
    return {'values': parse_csv(raw, series, vintage), 'raw_csv': raw,
            'downloaded_utc': 'Recorded fixture; see manifest.json',
            'url': 'https://fred.stlouisfed.org/series/' + series}

class AppTests(unittest.TestCase):
    def test_defaults_historical_probe_and_invalid_id(self):
        with patch('asof_data.fetch', side_effect=saved_fetch):
            app = AppTest.from_file(str(ROOT / 'asof_app.py')).run(timeout=30)
            self.assertEqual(len(app.exception), 0)
            self.assertEqual(app.sidebar.multiselect[0].value, list(NAMES))
            self.assertEqual(len(app.get('vega_lite_chart')), 4)
            app.sidebar.date_input[1].set_value(date(2026,10,5)).run()
            self.assertEqual(len(app.exception), 0)
            table = app.dataframe[-1].value
            self.assertEqual(list(table['Known: value']), [6.47,3.75,5.28,7.28])
            app.sidebar.multiselect[0].set_value([])
            app.sidebar.text_input[0].set_value('PAYEMS')
            app.sidebar.date_input[1].set_value(date(2025,1,15)).run()
            table = app.dataframe[-1].value
            self.assertEqual(table.iloc[0]['Known: value'], 159536)
            self.assertEqual(table.iloc[0]['Revised values'], 381)
            app.sidebar.multiselect[0].set_value(list(NAMES))
            app.sidebar.date_input[1].set_value(date(2026,10,5))
            app.sidebar.text_input[0].set_value('NOTAREALSERIES').run()
            self.assertEqual(len(app.exception), 0)
            self.assertEqual(len(app.error), 1)
            self.assertEqual(len(app.dataframe[-1].value), 4)

if __name__ == '__main__':
    with (ROOT / 'lab17_app_verification.txt').open('w', encoding='utf-8') as output:
        result = unittest.TextTestRunner(stream=output, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(AppTests))
    print((ROOT / 'lab17_app_verification.txt').read_text())
    raise SystemExit(0 if result.wasSuccessful() else 1)

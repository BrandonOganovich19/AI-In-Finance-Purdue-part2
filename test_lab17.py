"""Small synthetic fixtures test timing logic; they are not empirical evidence."""
import unittest
from datetime import date
from asof_data import parse_csv, compare, validate_id

class AuditTests(unittest.TestCase):
    def test_missing_zero_negative_and_sort(self):
        result = parse_csv('observation_date,X\n2025-01-03,-1\n2025-01-01,0\n2025-01-02,.\n', 'X')
        self.assertEqual(list(result.values()), [0, -1])

    def test_actual_vintage_column_and_cutoff(self):
        self.assertEqual(parse_csv('observation_date,X_20250101\n2025-01-01,2\n', 'X', date(2025,1,1)), {date(2025,1,1):2})
        with self.assertRaises(ValueError):
            parse_csv('observation_date,X_20250101\n2025-01-02,2\n', 'X', date(2025,1,1))

    def test_revision_alignment_and_later_count(self):
        old = {date(2024,12,31):10, date(2025,1,2):20}
        current = {date(2024,12,31):9, date(2025,1,1):5, date(2025,1,2):20, date(2025,1,3):30}
        result = compare(current, old)
        self.assertEqual(result['revised_count'], 1)
        self.assertEqual(result['later_count'], 1)
        self.assertEqual(result['known_value'], 20)

    def test_empty_vintage_not_zero(self):
        result = compare({date(2025,1,1):1}, {})
        self.assertIsNone(result['known_value'])
        self.assertIsNone(result['later_count'])
        self.assertEqual(result['revised_count'], 0)

    def test_bad_source_rejected(self):
        for text in ['<html>Error</html>', 'observation_date,Y\n2025-01-01,1', 'observation_date,X\n2025-01-01,nan', 'observation_date,X\n2025-01-01,1\n2025-01-01,2']:
            with self.subTest(text=text), self.assertRaises(ValueError):
                parse_csv(text, 'X')

    def test_id_validation(self):
        self.assertEqual(validate_id(' payems '), 'PAYEMS')
        with self.assertRaises(ValueError):
            validate_id('X&vintage_date=2026-01-01')

if __name__ == '__main__':
    unittest.main()

"""Known answers, sensitivity, invalid inputs, and mandate integration."""
import copy
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest
import portfolio as p
import mandate


class PortfolioTests(unittest.TestCase):
    def test_known_answers(self):
        cov = p.covariance_matrix(p.SLEEVES, p.CORRELATIONS)
        expected = [(6.80, 10.46, 0, True), (5.20, 5.21, 50, False), (3.77, 1.05, 90.3, False)]
        for w, (ret, vol, reserve, meets) in zip(p.baseline_weights(p.SLEEVES).values(), expected):
            self.assertAlmostEqual(sum(w), 1)
            self.assertEqual(round(100*p.expected_return(w, p.SLEEVES), 2), ret)
            self.assertEqual(round(100*p.portfolio_volatility(w, cov), 2), vol)
            self.assertEqual(round(100*p.reserve_weight(w, p.SLEEVES), 1), reserve)
            self.assertEqual(p.meets_objective(p.expected_return(w, p.SLEEVES), p.OBJECTIVE_RETURN), meets)

    def test_every_displayed_weight(self):
        expected = {
            'Benchmark': ['0.0', '0.0', '40.0', '60.0'],
            'Equal weight': ['25.0', '25.0', '25.0', '25.0'],
            'Inverse volatility': ['84.3', '6.0', '7.0', '2.6'],
        }
        for name, weights in p.baseline_weights(p.SLEEVES).items():
            self.assertEqual([f'{100*w:.1f}' for w in weights], expected[name])

    def run_engine(self, source):
        # Execute a disposable standalone copy, including its actual error handler.
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / 'portfolio.py'
            file.write_text(source, encoding='utf-8')
            return subprocess.run([sys.executable, str(file)], capture_output=True,
                                  text=True, timeout=15)

    def test_standalone_printed_outputs(self):
        result = self.run_engine(Path(p.__file__).read_text(encoding='utf-8'))
        self.assertEqual(result.returncode, 0, result.stderr)
        for block in (
            'Benchmark: 0.0 / 0.0 / 40.0 / 60.0\n  Return: 6.80% | Volatility: 10.46%\n  Reserve-eligible: 0.0%\n  Meets 6.5% objective? yes',
            'Equal weight: 25.0 / 25.0 / 25.0 / 25.0\n  Return: 5.20% | Volatility: 5.21%\n  Reserve-eligible: 50.0%\n  Meets 6.5% objective? no',
            'Inverse volatility: 84.3 / 6.0 / 7.0 / 2.6\n  Return: 3.77% | Volatility: 1.05%\n  Reserve-eligible: 90.3%\n  Meets 6.5% objective? no',
        ):
            self.assertIn(block, result.stdout)

    def test_standalone_mutations_and_refusal(self):
        source = Path(p.__file__).read_text(encoding='utf-8')
        # Match the editable input cells, not calculation code or known outputs.
        self.assertIn('[.05, .8, 1, .25]', source)
        self.assertIn('[0, -.1, .25, 1]', source)
        for value in ('.50', '1.3'):
            edited = source.replace('[.05, .8, 1, .25]', f'[.05, .8, 1, {value}]')
            edited = edited.replace('[0, -.1, .25, 1]', f'[0, -.1, {value}, 1]')
            result = self.run_engine(edited)
            if value == '.50':
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn('Return: 6.80% | Volatility: 11.00%', result.stdout)
            else:
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('Input error:', result.stderr)
                self.assertIn('between -1 and 1', result.stderr)
                self.assertNotIn('Benchmark:', result.stdout)
        asymmetric = source.replace('[.05, .8, 1, .25]', '[.05, .8, 1, .50]')
        result = self.run_engine(asymmetric)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('symmetric', result.stderr)
        self.assertNotIn('Benchmark:', result.stdout)
        self.assertEqual(Path(p.__file__).read_text(encoding='utf-8'), source)

    def test_covariance_and_diversification_boundaries(self):
        cov = p.covariance_matrix(p.SLEEVES, p.CORRELATIONS)
        self.assertAlmostEqual(cov[2][3], .0024)
        self.assertAlmostEqual(cov[3][2], .0024)
        self.assertAlmostEqual(cov[2][2], .0036)
        self.assertAlmostEqual(cov[3][3], .0256)
        sleeves = [{'return': .05, 'volatility': .10}] * 2
        # Perfect offset and perfect co-movement are valid boundary cases.
        for rho, expected in [(-1, 0), (1, .10)]:
            c = p.covariance_matrix(sleeves, [[1, rho], [rho, 1]])
            self.assertAlmostEqual(p.portfolio_volatility([.5, .5], c), expected)
        impossible = [[1, .9, .9], [.9, 1, -.9], [.9, -.9, 1]]
        with self.assertRaisesRegex(ValueError, 'positive semidefinite'):
            p.covariance_matrix(sleeves + sleeves[:1], impossible)

    def test_correlation_probe(self):
        corr = copy.deepcopy(p.CORRELATIONS)
        corr[2][3] = corr[3][2] = .50
        vol = p.portfolio_volatility([0, 0, .4, .6], p.covariance_matrix(p.SLEEVES, corr))
        self.assertEqual(round(100*vol, 2), 11.00)
        self.assertEqual(p.CORRELATIONS[2][3], .25)

    def test_invalid_correlations(self):
        for value in (1.3, -1.3, float('nan')):
            corr = copy.deepcopy(p.CORRELATIONS)
            corr[2][3] = corr[3][2] = value
            with self.assertRaises(ValueError): p.covariance_matrix(p.SLEEVES, corr)
        corr = copy.deepcopy(p.CORRELATIONS)
        corr[2][3] = .5
        with self.assertRaisesRegex(ValueError, 'symmetric'): p.covariance_matrix(p.SLEEVES, corr)
        with self.assertRaises(ValueError): p.covariance_matrix(p.SLEEVES, [[1]])

    def test_edges(self):
        for w in ([-.1, .1, .4, .6], [0, 0, .4, .5], [float('nan')]*4):
            with self.assertRaises(ValueError): p.expected_return(w, p.SLEEVES)
        sleeves = copy.deepcopy(p.SLEEVES)
        sleeves[0]['return'] = -.05
        self.assertEqual(p.expected_return([1, 0, 0, 0], sleeves), -.05)
        sleeves[0]['volatility'] = 0
        self.assertEqual(p.portfolio_volatility([1, 0, 0, 0], p.covariance_matrix(sleeves, p.CORRELATIONS)), 0)
        with self.assertRaises(ValueError): p.inverse_volatility_weights(sleeves)
        self.assertTrue(p.meets_objective(.065, .065))
        self.assertFalse(p.meets_objective(.064, .065))

    def test_benchmark_mandate(self):
        results = mandate.check_candidate(mandate.CANDIDATES['E'])
        self.assertEqual([r[1] for r in results], [100, 0, 0, 100, 0])
        self.assertEqual([r[2] for r in results], [True, True, False, True, True])


if __name__ == '__main__':
    unittest.main(verbosity=2)

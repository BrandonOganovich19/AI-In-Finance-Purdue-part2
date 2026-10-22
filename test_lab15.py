"""Formula, grid, CSV and Streamlit behavior checks for Lab 15."""
import copy
import io
import math
import unittest
import csv
import itertools
from statistics import mean, stdev, covariance
from unittest.mock import patch
import portfolio as p


class Lab15Tests(unittest.TestCase):
    def test_current_equity_universe_is_infeasible_under_reserve_rule(self):
        for last in (False, True):
            sleeves, corr = p.estimate_from_csv('prices.csv', last)
            self.assertEqual([s['name'] for s in sleeves], ['VTI','QQQ','VOO','SCHD'])
            self.assertTrue(all(not s['reserve'] for s in sleeves))
            self.assertIsNone(p.search_portfolio(sleeves,corr,.055,.03))
            with open('prices.csv',newline='',encoding='utf-8-sig') as file:
                prices = [[float(v) for v in row[1:]] for row in list(csv.reader(file))[1:]]
            returns = [[b[i]/a[i]-1 for i in range(4)] for a,b in zip(prices,prices[1:])]
            columns = list(zip(*(returns[-36:] if last else returns)))
            for i,sleeve in enumerate(sleeves):
                self.assertAlmostEqual(sleeve['return'],mean(columns[i])*12,places=12)
                self.assertAlmostEqual(sleeve['volatility'],stdev(columns[i])*math.sqrt(12),places=12)

    def test_independent_statistics_and_exhaustive_optimum(self):
        # Independent oracle: direct portfolio monthly returns, not engine covariance.
        with open('lab14_data/prices.csv', newline='', encoding='utf-8-sig') as file:
            rows = list(csv.reader(file))[1:]
        prices = [[float(v) for v in row[1:]] for row in rows]
        monthly = [[b[i]/a[i]-1 for i in range(4)] for a,b in zip(prices,prices[1:])]
        for last in (False, True):
            sample = monthly[-36:] if last else monthly
            s,c = p.estimate_from_csv('lab14_data/prices.csv', last)
            for a in s: a['reserve'] = a['name'] in ['BIL','IEF']
            cols = list(zip(*sample))
            annual_means = [mean(col)*12 for col in cols]
            engine_cov = p.covariance_matrix(s,c)
            for i in range(4):
                self.assertAlmostEqual(s[i]['return'],annual_means[i],places=12)
                self.assertAlmostEqual(s[i]['volatility'],stdev(cols[i])*math.sqrt(12),places=12)
                for j in range(4):
                    self.assertAlmostEqual(engine_cov[i][j],covariance(cols[i],cols[j])*12,places=12)
            candidates = []
            for units in itertools.product(range(21),repeat=4):
                if sum(units) != 20: continue
                weights = [v/20 for v in units]
                ret = sum(w*m for w,m in zip(weights,annual_means))
                if ret < .055-1e-12 or weights[0]+weights[1] < .03-1e-12: continue
                portfolio_returns = [sum(w*r for w,r in zip(weights,row)) for row in sample]
                candidates.append((stdev(portfolio_returns)*math.sqrt(12),weights))
            risk, weights = min(candidates)
            result = p.search_portfolio(s,c,.055,.03)
            self.assertEqual(result['weights'],weights)
            self.assertAlmostEqual(result['volatility'],risk,places=12)

    def test_grid_covers_three_to_six_assets(self):
        for n in (3,4,5,6):
            s = [dict(name=str(i),volatility=.1,reserve=False,**{'return':0}) for i in range(n)]
            c = [[float(i==j) for j in range(n)] for i in range(n)]
            with patch.object(p,'expected_return', wraps=p.expected_return) as calls:
                self.assertIsNone(p.search_portfolio(s,c,.1,0))
                self.assertEqual(calls.call_count,math.comb(20+n-1,n-1))

    def test_meridian_and_probes(self):
        s, c = copy.deepcopy(p.SLEEVES), copy.deepcopy(p.CORRELATIONS)
        a = p.search_portfolio(s, c)
        self.assertEqual(a['weights'], [0, .2, .25, .55])
        self.assertEqual(round(a['return_estimate']*100, 2), 6.51)
        self.assertEqual(round(a['volatility']*100, 2), 9.44)
        s[3]['return'] = .07
        b = p.search_portfolio(s, c)
        self.assertEqual(b['weights'], [0, .1, .1, .8])
        self.assertEqual(round(b['return_estimate']*100, 2), 6.53)
        self.assertEqual(round(b['volatility']*100, 2), 12.94)
        self.assertAlmostEqual(max(abs(x-y) for x,y in zip(a['weights'],b['weights'])), .25)
        c[2][3] = c[3][2] = .5
        b = p.search_portfolio(p.SLEEVES, c)
        self.assertEqual(b['weights'], [0, .4, 0, .6])
        self.assertEqual(round(b['return_estimate']*100, 2), 6.52)
        self.assertEqual(round(b['volatility']*100, 2), 9.73)

    def test_constraints_and_boundaries(self):
        self.assertIsNone(p.search_portfolio(p.SLEEVES, p.CORRELATIONS, .09))
        s = [dict(name=str(i),return_estimate=0,volatility=0,reserve=False) for i in range(3)]
        for a in s: a['return'] = -.01
        c = [[1,0,0],[0,1,0],[0,0,1]]
        self.assertIsNone(p.search_portfolio(s,c,-.01,.03))
        self.assertEqual(p.search_portfolio(s,c,-.01,0)['volatility'], 0)
        for floor in [-.01,1.01,float('nan')]:
            with self.assertRaises(ValueError): p.search_portfolio(s,c,0,floor)

    def test_estimation_hand_calculation(self):
        # Across a year boundary: monthly returns +10%, -10%; sample SD sqrt(.02).
        data = 'date,A,B,C\n2025-12-31,100,100,100\n2026-01-31,110,100,110\n2026-02-28,99,100,99\n'
        s,c = p.estimate_from_csv(io.StringIO(data))
        self.assertAlmostEqual(s[0]['return'], 0)
        self.assertAlmostEqual(s[0]['volatility'], math.sqrt(.02)*math.sqrt(12))
        self.assertAlmostEqual(c[0][2], 1)
        self.assertEqual(s[1]['volatility'], 0)
        self.assertEqual(c[0][1], 0)
        for bad in [data.replace('2026-01-31','2025-12-30'),
                    data.replace('2026-02-28','2026-03-31'),
                    data.replace('110,100,110','0,100,110'),
                    data.replace('110,100,110','nan,100,110'),
                    data.replace('110,100,110',',100,110')]:
            with self.assertRaises(ValueError): p.estimate_from_csv(io.StringIO(bad))
        with self.assertRaises(ValueError): p.estimate_from_csv(io.StringIO(data), True)

    def test_project_results(self):
        for last, weights in [(False,[.75,0,0,.25]),(True,[.9,0,0,.1])]:
            s,c = p.estimate_from_csv('lab14_data/prices.csv',last)
            for a in s: a['reserve'] = a['name'] in ['BIL','IEF']
            result = p.search_portfolio(s,c,.055,.03)
            self.assertEqual(result['weights'],weights)
            self.assertAlmostEqual(sum(weights),1)
            self.assertGreaterEqual(result['return_estimate'],.055)

    def test_reported_partner_ig_attack(self):
        s = copy.deepcopy(p.SLEEVES)
        baseline = p.search_portfolio(s,p.CORRELATIONS)
        s[2]['return'] = .04
        attacked = p.search_portfolio(s,p.CORRELATIONS)
        self.assertEqual(attacked['weights'],[0,.4,0,.6])
        self.assertEqual(round(attacked['return_estimate']*100,2),6.52)
        self.assertEqual(round(attacked['volatility']*100,2),9.73)
        changes = [round((b-a)*100,8) for a,b in zip(baseline['weights'],attacked['weights'])]
        self.assertEqual(changes,[0,20,-25,5])


if __name__ == '__main__':
    unittest.main(verbosity=2)

# This project was made with Codex. I am not a financial advisor.
# For educational purposes only; this is not investment advice.


"""Lab 14 risk engine. Standard library only. Run: python portfolio.py.

AI-assisted educational exercise; annual course training inputs, not forecasts.
Returns, volatilities and weights use decimals internally. No costs or taxes
are supplied; meeting the expected-return target is not full mandate approval.
"""
from math import isclose, isfinite, sqrt

# Editable inputs, in the same order throughout.
SLEEVES = [
    {"name": "Treasury bills", "return": .035, "volatility": .005, "reserve": True},
    {"name": "Treasury 10-year note", "return": .043, "volatility": .07, "reserve": True},
    {"name": "Investment-grade bond fund", "return": .05, "volatility": .06, "reserve": False},
    {"name": "Global equity index fund", "return": .08, "volatility": .16, "reserve": False},
]
CORRELATIONS = [[1, .1, .05, 0], [.1, 1, .8, -.1],
                [.05, .8, 1, .25], [0, -.1, .25, 1]]
OBJECTIVE_RETURN = .065  # CPI estimate 2.5% + 4 percentage points.


def validate_inputs(sleeves, correlations):
    n = len(sleeves)
    if not n or len(correlations) != n or any(len(row) != n for row in correlations):
        raise ValueError("Correlation table must be square with one row per sleeve.")
    for s in sleeves:
        if not isfinite(s["return"]) or not isfinite(s["volatility"]) or s["volatility"] < 0:
            raise ValueError("Returns must be finite and volatility finite and nonnegative.")
    for i in range(n):
        for j in range(n):
            r = correlations[i][j]
            if not isfinite(r) or not -1 <= r <= 1:
                raise ValueError("Every correlation must be finite and between -1 and 1.")
            if not isclose(r, correlations[j][i], rel_tol=0, abs_tol=1e-12):
                raise ValueError("Correlation table must be symmetric.")
        if not isclose(correlations[i][i], 1, rel_tol=0, abs_tol=1e-12):
            raise ValueError("Each diagonal correlation must equal 1.")
    # Semidefinite Cholesky check also catches impossible correlation tables.
    lower = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1):
            residual = correlations[i][j] - sum(lower[i][k] * lower[j][k] for k in range(j))
            if i == j:
                if residual < -1e-10:
                    raise ValueError("Correlation table must be positive semidefinite.")
                lower[i][j] = sqrt(max(0, residual))
            elif lower[j][j] > 1e-12:
                lower[i][j] = residual / lower[j][j]
            elif abs(residual) > 1e-10:
                raise ValueError("Correlation table must be positive semidefinite.")


def covariance_matrix(sleeves, correlations):
    validate_inputs(sleeves, correlations)
    return [[r * sleeves[i]["volatility"] * sleeves[j]["volatility"]
             for j, r in enumerate(row)] for i, row in enumerate(correlations)]


def validate_weights(weights, n):
    if len(weights) != n or any(not isfinite(w) or w < 0 for w in weights):
        raise ValueError("Supply one finite nonnegative weight per sleeve.")
    if not isclose(sum(weights), 1, rel_tol=0, abs_tol=1e-10):
        raise ValueError("Weights must sum to 1.")


def expected_return(weights, sleeves):
    validate_weights(weights, len(sleeves))
    return sum(w * s["return"] for w, s in zip(weights, sleeves))


def portfolio_volatility(weights, covariance):
    validate_weights(weights, len(covariance))
    if any(len(row) != len(weights) for row in covariance):
        raise ValueError("Covariance matrix must be square.")
    variance = sum(weights[i] * weights[j] * covariance[i][j]
                   for i in range(len(weights)) for j in range(len(weights)))
    if not isfinite(variance) or variance < -1e-12:
        raise ValueError("Invalid portfolio variance.")
    return sqrt(max(0, variance))


def reserve_weight(weights, sleeves):
    validate_weights(weights, len(sleeves))
    return sum(w for w, s in zip(weights, sleeves) if s["reserve"])


def meets_objective(value, objective):
    if not isfinite(value) or not isfinite(objective):
        raise ValueError("Return and objective must be finite.")
    return value >= objective or isclose(value, objective, rel_tol=0, abs_tol=1e-12)


def equal_weights(sleeves):
    if not sleeves:
        raise ValueError("Supply at least one sleeve.")
    return [1 / len(sleeves)] * len(sleeves)


def inverse_volatility_weights(sleeves):
    if not sleeves or any(not isfinite(s["volatility"]) or s["volatility"] <= 0 for s in sleeves):
        raise ValueError("Inverse volatility requires strictly positive finite volatility.")
    inverse = [1 / s["volatility"] for s in sleeves]
    return [v / sum(inverse) for v in inverse]


def baseline_weights(sleeves):
    benchmark = [(.4 if s["name"] == "Investment-grade bond fund" else
                  .6 if s["name"] == "Global equity index fund" else 0) for s in sleeves]
    validate_weights(benchmark, len(sleeves))
    return {"Benchmark": benchmark, "Equal weight": equal_weights(sleeves),
            "Inverse volatility": inverse_volatility_weights(sleeves)}


def search_portfolio(sleeves, correlations, objective=.065, reserve_min=.03):
    """Exhaustive 5-point grid; first lexicographic mix wins exact risk ties."""
    if not 3 <= len(sleeves) <= 6:
        raise ValueError("Supply three to six assets.")
    if not isfinite(objective) or not isfinite(reserve_min) or not 0 <= reserve_min <= 1:
        raise ValueError("Objective must be finite and reserve minimum between 0 and 1.")
    covariance = covariance_matrix(sleeves, correlations)

    def allocations(left, count):
        if count == 1:
            yield [left / 20]
        else:
            for units in range(left + 1):
                for tail in allocations(left - units, count - 1):
                    yield [units / 20] + tail

    best = None
    for weights in allocations(20, len(sleeves)):
        ret = expected_return(weights, sleeves)
        reserve = reserve_weight(weights, sleeves)
        if not meets_objective(ret, objective) or not meets_objective(reserve, reserve_min):
            continue
        vol = portfolio_volatility(weights, covariance)
        if best is None or vol < best['volatility']:
            best = dict(weights=weights, return_estimate=ret, volatility=vol, reserve=reserve)
    return best


def estimate_from_csv(source, last_36=False):
    """Monthly simple returns; sample SD/correlation; 36 returns need 37 prices.

    source is a path or text stream. Missing months/prices are rejected, never filled.
    Zero-variance assets use zero off-diagonal correlations (zero covariance).
    """
    import csv
    from datetime import date
    from pathlib import Path
    from statistics import mean, stdev
    from io import StringIO

    if isinstance(source, (str, Path)):
        source = StringIO(Path(source).read_text(encoding='utf-8-sig'))
    rows = list(csv.reader(source))
    if not rows or not 4 <= len(rows[0]) <= 7:
        raise ValueError("CSV requires a date column and three to six asset columns.")
    names = [name.strip() for name in rows[0][1:]]
    if any(not name for name in names) or len(set(names)) != len(names):
        raise ValueError("Ticker names must be nonempty and unique.")
    prices, dates = [], []
    for row in rows[1:]:
        if len(row) != len(names) + 1:
            raise ValueError("Every CSV row must contain a date and all prices.")
        try:
            day = date.fromisoformat(row[0])
            values = [float(v) for v in row[1:]]
        except ValueError:
            raise ValueError("Use ISO dates YYYY-MM-DD and numeric prices.") from None
        if any(not isfinite(v) or v <= 0 for v in values):
            raise ValueError("Prices must be positive and finite.")
        if dates and day.year * 12 + day.month != dates[-1].year * 12 + dates[-1].month + 1:
            raise ValueError("Dates must be consecutive months, oldest first, without duplicates.")
        dates.append(day)
        prices.append(values)
    if len(prices) < (37 if last_36 else 3):
        raise ValueError("Need 37 prices for 36 returns, or at least three prices for estimation.")
    returns = [[b[i] / a[i] - 1 for i in range(len(names))]
               for a, b in zip(prices, prices[1:])]
    if last_36:
        returns = returns[-36:]
    columns = list(zip(*returns))
    means = [mean(col) for col in columns]
    sds = [stdev(col) for col in columns]
    corr = [[1.0 if i == j else
             (max(-1.0, min(1.0, sum((x-means[i])*(y-means[j]) for x, y in zip(columns[i], columns[j]))
              / (len(returns)-1) / sds[i] / sds[j])) if sds[i] and sds[j] else 0.0)
             for j in range(len(names))] for i in range(len(names))]
    sleeves = [dict(name=name, return_estimate=means[i]*12,
                    volatility=sds[i]*sqrt(12), reserve=False) for i, name in enumerate(names)]
    for sleeve in sleeves:
        sleeve['return'] = sleeve.pop('return_estimate')
    validate_inputs(sleeves, corr)
    return sleeves, corr


def main():
    covariance = covariance_matrix(SLEEVES, CORRELATIONS)
    print("Annual course training inputs; weights and results in percent.")
    print("Sleeve order: " + " / ".join(s["name"] for s in SLEEVES))
    for name, weights in baseline_weights(SLEEVES).items():
        ret = expected_return(weights, SLEEVES)
        print(f"\n{name}: " + " / ".join(f"{100*w:.1f}" for w in weights))
        print(f"  Return: {100*ret:.2f}% | Volatility: {100*portfolio_volatility(weights, covariance):.2f}%")
        print(f"  Reserve-eligible: {100*reserve_weight(weights, SLEEVES):.1f}%")
        print(f"  Meets {100*OBJECTIVE_RETURN:.1f}% objective? {'yes' if meets_objective(ret, OBJECTIVE_RETURN) else 'no'}")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, TypeError, KeyError) as exc:
        raise SystemExit(f"Input error: {exc}") from None

# This project was made with Codex. I am not a financial advisor.
# For educational purposes only; this is not investment advice.

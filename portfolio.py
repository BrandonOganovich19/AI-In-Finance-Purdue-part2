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

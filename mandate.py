"""FIN43900 Lab 13: static mandate checks. Run: python mandate.py.

AI-use disclosure: ChatGPT was utilized as the AI agent to assist with
developing, explaining, and verifying this portfolio mandate checker.

Disclaimer (adapted from Agents.MD, Safety and Professional Boundaries):
I am not a financial advisor. This work is for educational purposes only.
The clients, portfolios, and scenarios are fictional examples. This material
does not constitute personalized investment advice or fiduciary, legal, tax,
or accounting representation, and it provides no guarantee of performance.
It is not certified, audited, or approved for a regulated filing. Consult a
qualified professional before making real financial decisions.
"""

from collections import defaultdict
from math import isclose, isfinite

# Editable inputs. Weights are percentage points; money is USD millions.
HOLDINGS = [
    {"holding": "Cash", "issuer": "none", "days": 0, "reserve_eligible": True},
    {"holding": "Treasury bills", "issuer": "U.S. Treasury", "days": 1, "reserve_eligible": True},
    {"holding": "Treasury 10-year note", "issuer": "U.S. Treasury", "days": 1, "reserve_eligible": True},
    {"holding": "Global equity index fund", "issuer": "diversified fund", "days": 2, "reserve_eligible": False},
    {"holding": "Investment-grade bond fund", "issuer": "diversified fund", "days": 3, "reserve_eligible": False},
    {"holding": "Private real estate fund", "issuer": "diversified fund", "days": 90, "reserve_eligible": False},
    {"holding": "Acme Corp bonds", "issuer": "Acme Corp", "days": 4, "reserve_eligible": False},
    {"holding": "Acme Corp stock", "issuer": "Acme Corp", "days": 1, "reserve_eligible": False},
]
# Each list follows the holdings order above, including zero allocations.
CANDIDATES = {
    "A": [2, 2, 10, 60, 26, 0, 0, 0],
    "B": [1, 0, 0, 55, 20, 15, 5, 4],
    "C": [1, 1, 0, 70, 20, 0, 0, 8],
    "D": [100, 0, 0, 0, 0, 0, 0, 0],
    "E": [0, 0, 0, 60, 40, 0, 0, 0],  # Lab 14 benchmark
}
RESERVE_SIZE = 100
QUARTERLY_DISTRIBUTION = 0.75
QUARTERS_TO_COVER = 4
LIQUIDITY_WINDOW = 5
MINIMUM_LIQUID_SHARE = 90
ISSUER_LIMIT = 8
EXEMPT_ISSUERS = {"none", "U.S. Treasury", "diversified fund"}


def reserve_minimum():
    if RESERVE_SIZE <= 0:
        raise ValueError("Reserve size must be positive.")
    return QUARTERS_TO_COVER * QUARTERLY_DISTRIBUTION / RESERVE_SIZE * 100


def check_candidate(weights):
    if len(weights) != len(HOLDINGS) or not weights:
        raise ValueError("Supply one weight for every holding.")
    if not all(isfinite(weight) for weight in weights):
        raise ValueError("All weights must be finite numbers.")
    total = sum(weights)
    lowest = min(weights)
    reserve = sum(w for h, w in zip(HOLDINGS, weights) if h["reserve_eligible"])
    liquid = sum(w for h, w in zip(HOLDINGS, weights) if h["days"] <= LIQUIDITY_WINDOW)
    companies = defaultdict(float)
    for holding, weight in zip(HOLDINGS, weights):
        if holding["issuer"] not in EXEMPT_ISSUERS:
            companies[holding["issuer"]] += weight
    largest = max(companies.values(), default=0.0)
    return [
        ("Weights sum to 100", total, isclose(total, 100, rel_tol=0, abs_tol=1e-9)),
        ("Long-only (lowest weight)", lowest, lowest >= 0),
        (f"Reserve >= {reserve_minimum():.1f}%", reserve, reserve >= reserve_minimum()),
        (f"Redeemable in {LIQUIDITY_WINDOW} days >= {MINIMUM_LIQUID_SHARE:g}%", liquid, liquid >= MINIMUM_LIQUID_SHARE),
        (f"Largest single company <= {ISSUER_LIMIT:g}%", largest, largest <= ISSUER_LIMIT),
    ]


def main():
    print(f"Reserve minimum: {reserve_minimum():.1f}%")
    for name, weights in CANDIDATES.items():
        print(f"\nCandidate {name}")
        results = check_candidate(weights)
        for label, value, passed in results:
            print(f"  {label}: {value:.1f} {'pass' if passed else 'FAIL'}")
        print("  Calendar-year loss: requires CIO clarification")
        failures = sum(not passed for _, _, passed in results)
        print("  " + (f"fails {failures} rule(s)" if failures else "passes every checkable rule"))


if __name__ == "__main__":
    main()

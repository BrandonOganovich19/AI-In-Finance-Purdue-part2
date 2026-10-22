# Lab 14 — Portfolio Baselines

Brandon Oganovich | FIN43900 | October 20, 2026

## Decision

None of these three baselines establishes compliance with Meridian's full mandate. The benchmark clears the expected-return target but holds no eligible reserve. Equal weight and inverse volatility hold ample eligible reserves but miss the return target. A low volatility estimate also cannot guarantee the absence of a calendar-year loss above 10%.

## Assumptions and inputs

The risk engine uses annual, course-authored training assumptions, not historical market estimates or investment recommendations. All internal weights, returns, and standard deviations are decimals. Displayed results use percentages. The nominal expected-return objective is 6.5%, using the lab's additive convention of an estimated 2.5% CPI plus four percentage points. No fees or taxes are supplied or deducted, so this comparison does not prove achievement of the original net-of-cost rolling five-year objective. USD is the mandate and fund-price currency.

The editable input block in `portfolio.py` is the authoritative source for sleeve returns, volatilities, reserve flags, correlations, and the objective. Bills and the 10-year Treasury are reserve-eligible under the classroom rules; their price risks differ. Meridian's reserve requirement remains $3 million / $100 million = 3%.

## Calculated results

Weights below are in the order bills / 10-year Treasury / investment-grade bonds / global equity.

| Portfolio | Weights (%) | Expected return | Volatility | Eligible reserve | Meets 6.5%? |
|---|---|---:|---:|---:|---|
| Benchmark | 0.0 / 0.0 / 40.0 / 60.0 | 6.80% | 10.46% | 0.0% | Yes |
| Equal weight | 25.0 / 25.0 / 25.0 / 25.0 | 5.20% | 5.21% | 50.0% | No |
| Inverse volatility | 84.3 / 6.0 / 7.0 / 2.6 | 3.77% | 1.05% | 90.3% | No |

Rounding makes displayed inverse-volatility weights total 99.9%; unrounded weights total 100%. Calculations retain full floating-point precision.

Candidate E in `mandate.py` holds 60% equity and 40% investment-grade bonds in that file's different holdings order. It totals 100%, is long-only, has 100% five-day liquidity, and has zero non-exempt company exposure under the supplied diversified-fund exemption. It fails only the checkable reserve rule: 0% versus 3% required. Calendar-year loss remains subject to CIO clarification. The benchmark is a comparison reference, not evidence of a suitable implementable mandate allocation.

## Formulas and diversification

For expected returns mu, weights w, volatilities sigma and correlations rho:

- Expected portfolio return: sum(w_i * mu_i).
- Covariance entry C_ij: rho_ij * sigma_i * sigma_j.
- Portfolio variance: sum over every i and j of w_i * w_j * C_ij.
- Portfolio volatility: square root of portfolio variance.
- Inverse-volatility weight: (1 / sigma_i) / sum_j(1 / sigma_j).
- Reserve share: sum of weights whose reserve flag is true.

Diversification combines exposures whose returns do not move perfectly together. For two positive-weight assets, reducing their correlation below +1 reduces the covariance contribution relative to perfect positive correlation. Diversification can reduce volatility below either individual asset, but it does not always do so: the benchmark is less volatile than equity and more volatile than the bond sleeve. It does not remove market risk or promise against losses, and correlations can rise during stress.

By hand, with returns expressed in decimals:

```text
Benchmark variance
= (0.40^2 * 0.06^2) + (0.60^2 * 0.16^2)
  + 2 * 0.40 * 0.60 * 0.25 * 0.06 * 0.16
= 0.000576 + 0.009216 + 0.001152
= 0.010944
Volatility = sqrt(0.010944) = 0.1046136... = 10.46%.
Return = 0.40 * 5% + 0.60 * 8% = 6.80%.
```

At correlation 0.50 the covariance contribution becomes 0.002304, total variance becomes 0.012096, and volatility becomes 10.99818...%, displayed as 11.00%. Ignoring cross-asset covariance would give approximately 9.90% at the original inputs and understate this benchmark's risk.

## Verification and use

```powershell
python portfolio.py
python mandate.py
python -m unittest test_portfolio -v
python verify_lab14.py
python download_prices.py
```

The risk engine and downloader use only the Python standard library. The saved verification record is `lab14_verification.txt`. Tests reproduce all three known results, change both IG/equity correlation cells to 0.50, reject out-of-range and asymmetric correlations, and check candidate E. Additional checks cover malformed dimensions, missing total weight, negative and nonfinite weights, negative expected return, zero volatility, and equality at the return target. Zero volatility is permitted for portfolio risk calculation but rejected by inverse-volatility weighting because division by zero is undefined. Correlation validation also checks the diagonal and positive semidefiniteness. The sensitivity test works on a copy; the delivered matrix retains 0.25.

The variance function iterates over every pair of sleeves, multiplies their two weights by their covariance, adds those contributions, and takes the square root. The diagonal contains each asset's own weighted variance. Tiny negative floating-point noise is clipped at zero, while materially negative or nonfinite variance is rejected. Function inputs are separate from printed output so a future application can reuse the calculations.

### Final audit of assignment requirements

The expanded audit passed **9 tests**. `python verify_lab14.py` regenerates the evidence in `lab14_verification.txt` using the existing source data; it does not need a new download. `download_prices.py` is only needed to retrieve prices again and may produce revised adjusted levels.

| Requirement | Evidence and result |
|---|---|
| Rerun prior mandate results | A and D still pass all static rules; B fails three and C fails one. |
| One reusable standard-library engine | `portfolio.py` runs independently; calculations are separate functions with editable inputs. |
| Correct inputs and covariance | All supplied inputs match; IG/equity covariance is 0.0024 in decimal-return-squared units. |
| Every displayed weight | All 12 weights match the reference to one decimal, including the inverse-volatility allocation. |
| Returns, risks, reserves and verdicts | All values in the results table above match the reference at the required precision; full printed output is tested. |
| Correlation sensitivity | A disposable copy with both cells set to 0.50 prints 11.00% benchmark volatility; delivered inputs remain 0.25. |
| Invalid correlation refusal | A disposable standalone copy with 1.3 exits unsuccessfully with a clear input error and prints no portfolio results. |
| Asymmetry refusal | Changing only one mirrored cell also exits unsuccessfully with a symmetry error. |
| Benchmark mandate integration | Candidate E holds 60 equity / 40 IG in the mandate file's order and fails the 3% reserve floor with 0.0%. |
| Diversification and hand calculation | Formula, covariance contribution, square root and interpretation appear above. |
| Reflection | Both requested topics are addressed in the AI-assisted draft below. |
| Fund preparation | Four funds, names, roles, sources and download date are documented. |
| Price-file structure and provenance | Date first, oldest first, 60 consecutive months, four ticker columns; all 240 values reconcile exactly to saved source responses. |
| Personal learning and partner activities | Still require actual student participation; automated probes do not establish a partner exchange. |
| GitHub checkout | Files are prepared locally; upload and individual file-link submission remain outstanding. |

### Code walkthrough for study

Use this guide to prepare, then explain the actual function without AI during the required exercise.

| Expression in `portfolio_volatility` | Meaning |
|---|---|
| `validate_weights(weights, len(covariance))` | Require one nonnegative finite weight for each asset and a fully invested total of one. |
| `any(len(row) != len(weights) for row in covariance)` | Check that the covariance table has the correct number of columns. |
| `for i in range(len(weights)) for j in range(len(weights))` | Visit every row-column pair, including each asset paired with itself. |
| `weights[i] * weights[j] * covariance[i][j]` | Calculate one pair's weighted contribution to portfolio variance. |
| `sum(...)` | Add all contributions, retaining both mirrored off-diagonal entries. |
| `not isfinite(variance) or variance < -1e-12` | Reject unusable results and materially negative variance. |
| `sqrt(max(0, variance))` | Convert variance to standard deviation, allowing only tiny rounding noise at zero. |

For an additional hypothetical illustration, two assets each with 10% volatility, equal weights and zero correlation have portfolio volatility sqrt(0.5^2 * 0.10^2 + 0.5^2 * 0.10^2) = 7.07%, below either asset. This is a separate teaching example, not a replacement for the lab's benchmark inputs.

### Partner question — AI-assisted response

**My partner asked:** “Where in your code does the correlation actually change the answer, and what would the benchmark’s volatility be if that line were missing?”

**Answer:** Correlation enters in `covariance_matrix()` in `portfolio.py`, through this expression:

```python
r * sleeves[i]["volatility"] * sleeves[j]["volatility"]
```

Here, `r` is the correlation between sleeves i and j. For IG bonds and equity, it makes their covariance 0.25 × 0.06 × 0.16 = 0.0024. `portfolio_volatility()` then uses that covariance in:

```python
weights[i] * weights[j] * covariance[i][j]
```

The sum includes both IG–equity and equity–IG, so together they contribute 2 × 0.40 × 0.60 × 0.0024 = 0.001152 to benchmark variance. Including this contribution gives sqrt(0.010944) = **10.46% volatility**.

If “missing” means leaving out the cross-asset covariance terms and adding only the weighted individual variances, the answer becomes:

```text
sqrt(0.40^2 * 0.06^2 + 0.60^2 * 0.16^2)
= sqrt(0.009792)
= 0.0989545... = 9.90% volatility.
```

That would understate this benchmark's risk by about 0.57 percentage points using unrounded results. It implicitly assumes zero correlation. There is an important distinction: removing only the multiplier `r` while keeping all pairwise terms would instead imply correlation +1 and give **12.00%**, while literally deleting a required code line could make the program fail. The lab's **9.90%** error refers specifically to omitting the cross-asset covariance contribution.

The partner question was reported by the student; this answer was prepared with AI assistance. It does not establish completion of the separate no-AI oral explanation or partner code-testing exercise.

## Reflection — AI-assisted draft

Inverse volatility puts most capital in bills because their supplied 0.5% volatility is far below the other sleeves. Their reciprocal volatility is 200, versus about 14.29, 16.67 and 6.25 for the other three sleeves. This method uses standalone volatility for allocation; it does not optimize expected return or account for correlations when choosing weights. Its low risk comes with a substantial expected-return shortfall. Equal weight uses a more balanced capital allocation, but equal capital does not mean equal risk contribution.

I would show the CIO the benchmark first. It connects directly to the client's stated performance reference and immediately exposes the conflict between the benchmark and the reserve rule. I would then show equal weight and inverse volatility to illustrate the return/risk tradeoff and ask the CIO to resolve the target and downside-risk priorities before optimizing. None is presented as a final recommendation.

## Project 2 fund universe and prices

**Historical record:** The universe below was used for Lab 14. On October 22, Project 2 was changed to VTI, QQQ, VOO and SCHD. The prior CSV is now `lab14_data/prices.csv`; the current root `prices.csv` and Lab 15 report use the new universe. `download_prices.py` and `verify_lab14.py` use the archived Lab 14 path, while `download_lab15_prices.py` maintains the current CSV.

The universe supports the fictional Campus Access Scholarship Reserve from Lab 13: $2 million, a ten-year horizon, $60,000 reserve requirement and CPI + 3% objective. That objective is distinct from Meridian's 6.5%. These funds are educational proxies; they have not been optimized or endorsed for a real account.

| Ticker | Fund name | Role | Historical source | Download date |
|---|---|---|---|---|
| BIL | State Street SPDR Bloomberg 1-3 Month T-Bill ETF | Cash/reserve proxy; short Treasury bills | [Yahoo history](https://finance.yahoo.com/quote/BIL/history/) | 2026-10-20 |
| IEF | iShares 7-10 Year Treasury Bond ETF | Government-bond sleeve with duration exposure | [Yahoo history](https://finance.yahoo.com/quote/IEF/history/) | 2026-10-20 |
| LQD | iShares iBoxx $ Investment Grade Corporate Bond ETF | Investment-grade corporate fixed income | [Yahoo history](https://finance.yahoo.com/quote/LQD/history/) | 2026-10-20 |
| VT | Vanguard Total World Stock ETF | Broad global equity growth exposure | [Yahoo history](https://finance.yahoo.com/quote/VT/history/) | 2026-10-20 |

Fund identities and roles were checked against the providers: [BIL](https://www.ssga.com/us/en/intermediary/etfs/state-street-spdr-bloomberg-1-3-month-t-bill-etf-bil), [IEF](https://www.ishares.com/us/products/239456/ishares-7-10-year-treasury-bond-etf), [LQD](https://www.ishares.com/us/products/239566/ishares-iboxx-investment-grade-corporate-bond-etf), and [VT](https://advisors.vanguard.com/investments/products/new/vt/vanguard-total-world-stock-etf). ETF government exposure is a proxy for the classroom reserve sleeves; real policy eligibility needs confirmation. LQD is a corporate-bond proxy, not the entire U.S. investment-grade bond market.

`prices.csv` contains 60 monthly adjusted closing prices per fund, oldest first, from October 2021 through September 2026. Dates are the last available trading day of each completed month (2021-10-29 through 2026-09-30). October 2026 is excluded because it is incomplete. Sixty prices produce 59 month-to-month returns; obtaining 60 returns would require an additional initial price.

Yahoo's history webpages were rate-limited during retrieval, so the downloader used Yahoo's chart endpoint and its explicit `adjclose` field, sampling the final daily observation of each month. This avoids the ambiguous date labels of monthly bars. Prices reflect Yahoo's distribution and split adjustments; they are not raw closing prices, forecasts, or guaranteed reinvestment outcomes. Adjusted levels may be revised with subsequent corporate actions. The source responses and exact URLs/timestamp are preserved in `lab14_data/`, including `metadata.json`. All four series have 60 positive finite observations, matching dates, and no filled or invented values. A five-year sample is not proof of future risk or return.

## Authorship and remaining personal checkout


**Disclaimer (adapted from Agents.MD, Safety and Professional Boundaries):** I am not a financial advisor. This work is for educational purposes only. The clients, portfolios, and scenarios are fictional examples. This material does not constitute personalized investment advice or fiduciary, legal, tax, or accounting representation, and it provides no guarantee of performance. It is not certified, audited, or approved for a regulated filing. Consult a qualified professional before making real financial decisions.

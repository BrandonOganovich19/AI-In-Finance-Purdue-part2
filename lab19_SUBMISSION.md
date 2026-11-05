# Lab 19 — Legend Panel

Brandon Oganovich · FIN43900 · November 5, 2026

**Disclaimer:** I am not a financial advisor. This project was made with Codex for educational purposes only and is not investment advice. Historical results and screening outcomes do not guarantee future performance.

**Decision (draft for my review):** I would use the panel only as a preliminary research screen, conditional on checking source completeness, keeping thresholds fixed in advance, and reconciling NVIDIA's cash-flow shortfall before admitting it to a favorable screen; valuation and fund-level concentration still require separate analysis.

**AI-use disclosure:** Codex assisted with the code, calculations, simulated investor memos, verification, and these written responses. The partner exchange, the independent no-AI explanation, personal adoption of the decision, and GitHub/Brightspace submission are not claimed as completed. This is an educational analysis, not investment advice.

## D — question and request

When three investors' skills read the same annual filing facts, where do they agree, where do they split, and would I trust the panel?

**Build request used:** Extend the existing Buffett application without changing its SEC extraction, tag priority, annual-period selection, owner-earnings proxy, missing-data treatment, chart, or memo audit. Add Graham and Burry skills with code-based checks using the same facts plus total liabilities, current assets, and current liabilities; show the checks, separate qualitative verdicts, and three memos side by side. Reproduce COST, run the Graham threshold probe, analyze the largest company in one of my Project 2 funds, and retain every missing value and unknown check.

**Preparation for the partner comparison:** Graham would reject Costco under the strict liquidity screen even though Buffett's cash-generation and ROE checks pass. Burry would focus on whether accounting earnings are supported by operating cash flow and whether aggregate liabilities are excessive, so favorable Burry results do not resolve Graham's current-asset concern.

## V — Costco known answer reproduced

These are code-calculated results from saved SEC company facts, not values inserted into the production calculation. Expected values appear only in the separate tests.

| Fiscal year end | Current ratio | Liabilities / equity |
|---|---:|---:|
| 2022-08-28 | 1.02 | 2.11 |
| 2023-09-03 | 1.07 | 1.75 |
| 2024-09-01 | 0.97 | 1.96 |
| 2025-08-31 | 1.03 | 1.64 |
| 2026-08-30 | 1.06 | 1.49 |

| Investor | Check | COST |
|---|---|---|
| Buffett | ROE at least 15% every year | pass |
| Buffett | Owner earnings positive every year | pass |
| Buffett | Owner earnings grew first to last | pass |
| Graham | Latest current ratio at least 2.00 | fail |
| Graham | Net income positive every year | pass |
| Graham | Net income grew first to last | pass |
| Burry | Operating cash flow at least net income every year | pass |
| Burry | Latest liabilities no more than twice equity | pass |

Totals: **Buffett 3/3; Graham 2/3; Burry 2/2**. Latest current ratio **1.06** fails Graham; latest liabilities/equity **1.49** passes Burry. Burry's leverage rule concerns the latest year, so the older 2.11 observation does not make that check fail.

The three qualitative verdicts are Buffett **watch it**, Graham **pass on the defensive screen**, and Burry **watch it; no red flag in the assigned checks**. Check totals are mechanical; qualitative judgments require interpretation and need not be identical to those totals.

### Threshold probe

The test changes Graham's executable skill setting from **2.00** to **1.00**, runs the same COST evidence, confirms Graham becomes **3/3**, and restores **2.00** in a finally block. The app also provides the same temporary probe. The business facts do not change; only the rule changes. The saved memos describe the retained rule and the app explicitly warns when the probe is active.

**Threshold retained: 2.00, to preserve the defensive liquidity cushion and avoid selecting a cutoff merely because it makes Costco pass.**

## My company — NVIDIA from VOO

My earlier portfolio work identifies VTI, QQQ, VOO, and SCHD. I selected **VOO**. Vanguard's official fact sheet dated **September 30, 2026**, lists **NVIDIA as its largest holding at 8.4%**; Apple follows at 7.4%. NVIDIA files annual reports with the SEC, so no fallback company was necessary. [Vanguard fact sheet, page 2](https://workplace.vanguard.com/assets/corp/fund_communications/pdf_publish/us-products/fact-sheet/F0968.pdf).

Holdings evidence identifies the company; it is not an additional numerical input to the investor memos. The company analysis uses the downloaded SEC snapshot dated November 5, 2026. Its five fiscal ends run from January 30, 2022, through January 25, 2026.

| Investor | Check | NVDA |
|---|---|---|
| Buffett | ROE at least 15% every year | pass |
| Buffett | Owner earnings positive every year | pass |
| Buffett | Owner earnings grew first to last | pass |
| Graham | Latest current ratio at least 2.00 | pass: 3.91 |
| Graham | Net income positive every year | pass |
| Graham | Net income grew first to last | pass |
| Burry | Operating cash flow at least net income every year | fail |
| Burry | Latest liabilities no more than twice equity | pass: 0.31 |

Totals: **Buffett 3/3; Graham 3/3; Burry 1/2**. Buffett's verdict is **watch it**, Graham's is **watch it; clears the assigned defensive screen**, and Burry's is **hold for cash-conversion review**.

Latest operating cash flow is **USD 102,718 million**, below net income of **USD 120,067 million**. The cash-conversion failure occurs in several years, not just the latest year. Meanwhile, owner earnings remain positive and grow from **USD 8,132 million** to **USD 96,676 million** across the window. This is a substantive split: strong cash generation in absolute terms does not guarantee that cash flow equals accounting income.

There are no missing required facts in the selected COST or NVDA windows. This is a result of extraction, not a rule that all fields must be present. The additional JPM example preserves absent capital spending and current-balance-sheet tags: owner earnings and the current ratio remain unknown. No estimates or zero substitutions repair those gaps.

### Bull case — two sentences, prepared for discussion

NVIDIA passes all Buffett and Graham checks, with positive owner earnings growing from USD 8,132 million to USD 96,676 million and a latest current ratio of 3.91. Its latest liabilities/equity ratio of 0.31 also passes Burry's leverage screen, supporting continued business research while keeping the cash-conversion concern visible.

### Bear case — two sentences, prepared for discussion

NVIDIA fails Burry's earnings-quality screen because operating cash flow falls below net income in several periods, including USD 102,718 million against USD 120,067 million in the latest year. Until the cash-flow reconciliation explains that difference and separate valuation work establishes an acceptable purchase price, favorable ROE and liquidity screens are insufficient grounds to approve the investment.

## Learn — a panel of AI agents

A panel assigns different analytical roles to a shared evidence base. Here each role is implemented as reusable skill instructions, deterministic screening code, and a separate AI-assisted memo; the application replays saved results rather than calling live autonomous agents on every interaction.

The pipeline is SEC evidence → shared annual facts → each role's explicit checks → printed numbers → separate memos → cross-memo numeric audit → human decision. Using the same facts removes one source of inconsistency, but different priorities still produce different judgments: Buffett emphasizes returns and cash generation, Graham a defensive liquidity cushion and earnings, and Burry cash conversion and liabilities.

Agreement is not independent confirmation when the roles share data, extraction code, and the same underlying AI assistance. A common source or logic error can affect every perspective. Majority vote is therefore not a substitute for reconciliation or professional judgment.

## Reflection

For NVIDIA, the panel agrees that the record contains substantial profitability and cash generation, and its latest liquidity and leverage ratios meet the assigned rules. It splits over whether the accounting-income record is sufficiently supported by operating cash flow; Burry highlights a concern that Buffett's positive owner-earnings rule does not test.

The Costco probe shows that a verdict is conditional on the screen's design. Lowering a threshold changes classification without changing economic reality, so thresholds should be justified and recorded before inspecting the desired outcome. Sensitivity analysis reveals this dependence; it does not justify tuning the screen until a favored stock passes.

## Assumptions and limitations

- Amounts are reported nominal USD, displayed in millions; ratios are times, and ROE is a percentage. No FX conversion, inflation adjustment, tax model, projections, or stock-price input is applied.
- Only eligible USD observations from annual 10-K filings are used. Annual flow durations allow 350–380 days, accommodating calendar and retail fiscal years; instant balance-sheet facts require the matching fiscal end.
- Tag priority and latest-filed duplicate selection follow Lab 18. This is a reproducible snapshot of currently available annual history, **not** a historical point-in-time trading backtest; later filings can restate earlier figures.
- ROE uses ending equity. Owner earnings is operating cash flow less total capital spending, not estimated maintenance capex. Current ratio uses AssetsCurrent / LiabilitiesCurrent; leverage uses Liabilities / StockholdersEquity.
- Five-year tests require the full window. Missing required inputs keep a check not known; endpoint growth needs first and last observations within that full window. Positive means strictly above zero; at least and no more than include equality. Nonpositive ratio denominators remain unknown.
- Comparisons use full-precision Decimal ratios before display rounding. A displayed boundary value can fail if its unrounded value is below the required minimum.
- The numeric audit checks exact token membership in printed output for every memo. It cannot prove correct attribution, economic meaning, or semantic truth; memo metrics, dates and units were also manually reviewed.
- No screen proves a moat, accounting fraud, future growth, or an attractive price. Fund allocation also needs concentration, overlap, liquidity, and mandate analysis.

## Evidence for the five merit criteria

| Criterion | Evidence to open |
|---|---|
| Known answer reproduced | COST panel report; calculation tests check every expected ratio and all eight checks |
| Numbers in code | lab19_panel.py; all memo files; audit report; app test injects an unsupported number into each editor |
| Honest gaps | JPM report; missing-input and zero-denominator tests; no inferred or estimated values |
| My company run | NVDA report and three memos; official VOO holdings source above |
| Decision | Conditional decision at the top; bull/bear cases and company-specific cash-conversion condition |

Read the companion RUN_ME and WALKTHROUGH files for commands and independent explanation preparation. Upload the individual files to GitHub, then paste actual links into the lab checkout. No upload or quiz submission has been performed.

## Sources

- [Lab 19 assignment and rubric](https://github.com/CinderZhang/FIN43900-Fall2026/blob/main/lessons/week-11/lab-19-legend-panel.md)
- [FAskills Graham](https://github.com/CinderZhang/FAskills/blob/main/financial-researcher/experts/ben_graham.md) and [FAskills Burry](https://github.com/CinderZhang/FAskills/blob/main/financial-researcher/experts/michael_burry.md): qualitative inspiration narrowed to the assigned checks, not their broader price/forecast requirements.
- [SEC API documentation](https://www.sec.gov/search-filings/edgar-application-programming-interfaces), [COST facts endpoint](https://data.sec.gov/api/xbrl/companyfacts/CIK0000909832.json), [NVDA facts endpoint](https://data.sec.gov/api/xbrl/companyfacts/CIK0001045810.json), and saved hash/provenance sidecars.
- [Streamlit columns](https://docs.streamlit.io/develop/api-reference/layout/st.columns) and [AppTest](https://docs.streamlit.io/develop/api-reference/app-testing/st.testing.v1.apptest) for presentation and integration testing.

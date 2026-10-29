# Lab 17 — Point-in-Time Audit

Brandon Oganovich | FIN43900 | October 29, 2026  
Partner: **Josh McDonald** (publication-timing challenge received; response below)

## Result and question

**Was each number in my series knowable on the day I would have traded on it, and may Project 2 use it?** Only observations actually available in the appropriate ALFRED vintage qualify. I conditionally admit **DGS10** as a macroeconomic input for my VTI / QQQ / VOO / SCHD portfolio, with the timing rule below. I do not admit a file of today's observations indexed only by measurement date.

The live downloads reproduce all four required October 5 answers and the PAYEMS revision example. Six calculation/input tests and the Streamlit interaction test pass. Josh's publication-timing challenge and an evidence-based response are recorded below; my three independent FRED page checks are complete, as confirmed by Brandon; the remaining classroom/submission steps are still pending. This is not a claim of a completed oral exercise or a guaranteed grade.

## Run and share

On this computer, from the project folder:

```powershell
.\tmp\python-3.12.10-embed-amd64\python.exe run_lab17.py
```

With a standard Python installation, including on Josh's computer:

```powershell
python -m pip install -r requirements-lab17.txt
python -m streamlit run asof_app.py
```

Keep `asof_app.py` and `asof_data.py` together. No API key or account is required. The old portfolio app and Lab 16 files are unchanged. To reproduce the evidence:

```powershell
python verify_lab17.py
python test_lab17_app.py
```

The bundled interpreter can also run those two scripts. Verification refreshes the saved downloads; current values can change. The saved manifest records actual UTC retrieval timestamps, source URLs, and SHA-256 hashes.

| File | Purpose |
|---|---|
| [asof_app.py](asof_app.py) | Streamlit controls, cached downloads, charts, linked comparison table |
| [asof_data.py](asof_data.py) | CSV validation and date-aligned comparisons |
| [run_lab17.py](run_lab17.py) | Launcher for this computer's existing environment |
| [requirements-lab17.txt](requirements-lab17.txt) | Dependencies for another computer |
| [verify_lab17.py](verify_lab17.py) | Live-source checks and calculation tests |
| [test_lab17.py](test_lab17.py) | Missing data, timing, revisions, invalid inputs, and empty histories |
| [test_lab17_app.py](test_lab17_app.py) | UI checks using saved real responses |
| [lab17_verification.txt](lab17_verification.txt) | Live results and six passing tests |
| [lab17_app_verification.txt](lab17_app_verification.txt) | Passing UI test |
| [lab17_data/manifest.json](lab17_data/manifest.json) | Provenance for saved CSV evidence |

## App behavior and calculation rules

All four required rates are selected initially. The chart starts January 1, 2020; the vintage defaults to the computer's current date. The text box accepts an additional FRED ID, including PAYEMS. Each successful series has a current-history chart, its last available vintage observation date, and a row in the comparison table. An unknown ID reports an error without removing the other series.

Each series uses one current CSV request and one vintage CSV request on a cache miss. The two wrapper functions cache results for one hour; the download-day argument prevents yesterday's cache from carrying into today. Changing a vintage requests that vintage, while the current history remains cached. Individual retrieval times are displayed in the evidence expanders.

Dates are observation periods: September's monthly value is labeled `2026-09-01`, not necessarily published on September 1. The ALFRED URL's `vintage_date` selects the historically available file. Truncating today's CSV at the decision date would not undo revisions or remove delayed publications correctly.

- **Latest known value:** value on the greatest nonmissing observation date in the vintage.
- **Later count:** number of nonmissing current observations with a measured date after that vintage's last measured date.
- **Revised count:** number of dates present in both histories whose values differ by more than `1e-9` source units. This tiny tolerance avoids representation noise; it does not round financial values for comparison.

Counts use the entire downloaded history, independent of the chart window. A newly filled historical gap is not a revision of an existing nonmissing observation, nor a later date if it precedes the vintage's endpoint. Missing `.` or blank cells are excluded, never interpreted as zero. An empty vintage has an undefined later count, shown as missing, rather than a misleading zero. Negative and zero numerical values remain valid.

## Required live checks

Set **As known on = 2026-10-05**. Saved downloads produced:

| Series | Last measured period available | Value (%) | Result |
|---|---|---:|---|
| BAA | September 2026 | 6.47 | Match |
| FEDFUNDS | September 2026 | 3.75 | Match |
| DGS10 | October 2, 2026 | 5.28 | Match |
| MORTGAGE30US | October 1, 2026 | 7.28 | Match |

Add **PAYEMS**, then choose **2025-01-15**. The latest measured month is December 2024, at **159,536 thousand persons**. Today's file has **158,316 thousand persons** for that same month: a downward change of **1,220 thousand persons**. Across the full shared history, **381 observations changed**. Thus the vintage request demonstrably differs from the current request. These numbers come from saved source CSVs, not values embedded in the app. Expected values appear only in verification assertions.

## My portfolio data card — DGS10

| Field | Definition and evidence |
|---|---|
| Source and links | Board of Governors of the Federal Reserve System, H.15; distributed by [FRED](https://fred.stlouisfed.org/series/DGS10), historical vintages through [ALFRED](https://alfred.stlouisfed.org/series?seid=DGS10). |
| Measure | Nominal U.S. Treasury market yield at a constant ten-year maturity, quoted on an investment basis. It is a yield-curve measure, not an ETF price or realized holding-period return. |
| Units and frequency | Percent per annum; daily; not seasonally adjusted. `5.05` means 5.05%, or `0.0505` in a formula requiring a decimal rate. No currency conversion or tax/inflation adjustment is applied. No compounding or day-count calculation is performed by this app. |
| Publication timing | The [H.15 release](https://www.federalreserve.gov/releases/h15/) is posted on business days at 4:15 p.m., excluding holidays/closures. The two audited vintages show a one-calendar-day observation lag: September 30 contains September 29, and October 29 contains October 28. Treat this as observed availability, not a promise that every lag is exactly one day; weekends, holidays, and distributor updates matter. |
| Revisions | Zero changed shared observations in both audited DGS10 comparisons. This supports low revision risk in this evidence, not a guarantee that corrections never occur; FRED explicitly allows revisions. |
| Download date | October 29, 2026. Exact UTC retrieval timestamps and URLs are in the manifest. |
| Missing data | Nonbusiness days or unavailable quotes may be absent or marked `.`. Do not replace them with zero or silently treat them as a new observation. |
| Portfolio relevance | Research hypothesis: higher Treasury yields can increase the discount rate applied to equity cash flows and alter the relative appeal of dividend income. This matters to VTI, QQQ, VOO, and SCHD; longer-duration growth valuations may be particularly sensitive. This audit does not establish predictive power, causation, or an allocation recommendation. |

### Last month versus today

| Vintage | Last measured date | Last value (%) | Current dates after endpoint | Revised shared observations |
|---|---|---:|---:|---:|
| September 30, 2026 | September 29, 2026 | 5.26 | 20 | 0 |
| October 29, 2026 | October 28, 2026 | 5.05 | 0 | 0 |

The twenty later observations were unavailable in the September 30 vintage. A daily market rate has little lag and, here, no observed revisions; that still does not authorize trading on a measurement before its publication.

### Three source-page checks

The assistant independently read the FRED page and compared these rows with the downloaded CSV. The H.15 page also corroborates them. **Brandon confirmed completing all three manual FRED checks.**

| Measured date | FRED page (%) | CSV (%) | Assistant comparison | Brandon checked |
|---|---:|---:|---|---|
| October 23, 2026 | 5.00 | 5.00 | Equal | Completed |
| October 26, 2026 | 5.00 | 5.00 | Equal | Completed |
| October 27, 2026 | 4.99 | 4.99 | Equal | Completed |

The FRED page retrieved during research still displayed October 27 as its latest observation, whereas the later CSV included October 28 at 5.05. Comparing the same three dated rows avoids confusing a page refresh delay with a historical revision.

## Fresh eyes — Josh McDonald

**Challenged field: publication date and freshness.** Josh's challenge, supplied by Brandon: the September 30 vintage already contains September 29's 5.26%, so selecting the prior day's vintage introduces additional lag; does a vintage dated D mean known before trading on D, and from which endpoint is the seven-day cutoff measured?

**Two-sentence response:** Vintage D identifies information known as of that calendar date, not necessarily before a trade earlier that day: ALFRED's real-time periods are date-based and inclusive, and H.15 is released at 4:15 p.m., so the September 30 vintage containing September 29's 5.26% does not establish its availability at the September 30 market open ([ALFRED timing documentation](https://fred.stlouisfed.org/docs/api/fred/realtime_period.html), [H.15 schedule](https://www.federalreserve.gov/releases/h15/)). I therefore explicitly assume execution at the regular-session open on D and retain the deliberately conservative prior-calendar-day vintage, measuring staleness as `D minus the latest observation date actually selected` and quarantining ages greater than seven calendar days; the extra lag is acknowledged rather than described as the freshest possible information.

**What the challenge corrected:** The previous rule omitted the execution time and left the age calculation implicit. The revised rule below makes both explicit; a date-only audit cannot prove that the 5.26% observation was available before every September 30 trade. The saved current file confirms September 28 = 5.24%, but a September 29 vintage was not downloaded in the original audit, so its endpoint/value is not claimed as independently verified. If that vintage ends at September 28 as Josh proposes, the September 30 feature age is two calendar days, not one. Weekends and holidays also mean the endpoint is not invariably D minus two.

Brandon supplied the conceptual no-AI discussion notes, the code walkthrough, and Josh's code question with his answer, all recorded below.

### No-AI explanation — reported by Brandon

Brandon reported explaining the following without AI during the explanation (these notes were subsequently supplied here for inclusion):

- DGS10 is the daily ten-year Treasury yield, in percent, from the Fed's H.15 release.
- Measurement date differs from availability date: September 30's 5.29% was absent from the September 30 vintage.
- An ALFRED vintage represents the series as it appeared on a past date.
- Cutting today's file at a decision date cannot remove later revisions or publication delays.
- December 2024 PAYEMS was 159,536 thousand persons in the January 15, 2025 vintage and 158,316 in the current download: a decrease of 1,220 thousand persons; 381 shared observations changed.
- DGS10 had zero revisions in the two audited comparisons, which does not guarantee that it is never revised.
- The decision is conditional admission using the appropriate as-of vintage, with quarantine for missing data or a selected observation more than seven calendar days old.
- Unexplained corrections, missing vintages, unit changes, or an unverified release schedule would trigger reconsideration.
- Josh's challenge, the response, and its effect on the rule were included in the explanation notes. The documented change above specifies 9:30 a.m. Eastern execution and age measured from the selected observation to the trade date; the conservative prior-day vintage remains.

These are Brandon's reported discussion topics, not an independently witnessed assessment. His summary phrase “appropriate as-of vintage” refers to the precise Project 2 rule below.

## Explain the code — walkthrough supplied by Brandon

**Status: walkthrough documented.** Brandon supplied the following explanation of the actual implementation. References use function names because line numbers can change. The cache wording is clarified below: a new `download_day` prevents reuse under yesterday's key; it does not itself delete or expire that cache entry.

| Code | Brandon's explanation, with cache wording clarified |
|---|---|
| `download_as_known` | Cached for one hour. All three arguments participate in the cache key; changing `download_day` selects a new key. `fetch(series, as_known_on)` passes the historical date to the data layer. |
| `validate_id` | Trim and uppercase the ID, then allow only 1–80 ASCII letters, digits, or underscores. Invalid IDs are rejected before building the URL. |
| `fetch` URL construction | Start with the series ID; when a vintage is supplied, add `vintage_date` and switch to ALFRED. `urlencode` constructs the query. |
| `fetch` request and result | Make one request with a 45-second timeout, decode the CSV, and retain the URL, UTC retrieval time, raw CSV, and parsed values. A failed vintage request never falls back to today's data. |
| `parse_csv` columns | Require two columns and an accepted date-column name. Accept either the series ID or a value-column name beginning with the ID plus an underscore, including ALFRED's dated suffix. |
| `parse_csv` missing cells | Skip `.` and blank values instead of turning them into zero. |
| `parse_csv` validation | Reject non-finite values, duplicate retained observation dates, and nonmissing observations after the vintage date. Return observations sorted by date. |
| `compare` | `old_last` is the last nonmissing vintage date; `shared` contains dates in both files; revised values differ by more than `1e-9`. `later_count` counts current dates after `old_last`: 20 for the recorded September 30 DGS10 comparison, a result specific to the saved current download. |

### Josh's code question and Brandon's answer — completed

**Josh's question:** “Line 38 uses `day > vintage`. Your vintage files never contain the vintage date itself. Shouldn't it be `>=`, so a same-day value gets caught?”

**Brandon's answer, as supplied:** “The vintage request is what prevents leaks, and line 38 is only a backstop. `>=` would be stricter. But for a series where the value for D is posted on D, `>=` would wrongly reject a legitimate observation. DGS10 posts D−1 on D, so it would be safe here. I'd keep `>` as the general rule and test `>=` only for DGS10.”

**Technical clarification added during documentation:** Keep `>` for DGS10 as well. The audited DGS10 vintages show earlier observation dates, but do not establish a permanent invariant that same-day observations are invalid; `>=` would leave those particular fixtures unchanged, not prove a better validation rule. The vintage request selects historically available values, while this comparison only rejects future measurement dates. Neither comparison establishes availability before a particular intraday trade. The existing `test_actual_vintage_column_and_cutoff` test already accepts an observation dated on the vintage date and rejects one dated after it.

**Prepared revision follow-up (not claimed as another question Josh asked):** Filtering observation dates does not remove later revisions. Requesting the PAYEMS historical vintage retrieves December 2024's then-known 159,536 rather than the current download's 158,316.

### Supporting study guide

Read `download_as_known` in `asof_app.py`, then the called `fetch` and `parse_csv` functions in `asof_data.py`:

1. The cache decorator reuses identical calls for up to an hour.
2. `series` selects the series, `as_known_on` selects the vintage, and `download_day` separates daily caches.
3. `return fetch(series, as_known_on)` passes the vintage into the data layer.
4. `validate_id` normalizes the ID and rejects malformed characters.
5. `params` begins with the series ID. When a vintage is supplied, `vintage_date` is added in ISO date format and the endpoint changes to ALFRED.
6. `urlencode` builds the query safely. `urlopen` performs one request with a 45-second timeout; it does not fall back to today's data on failure.
7. The returned CSV is decoded and parsed. The parser validates the date/value columns, accepts ALFRED's dated column suffix, skips missing cells, preserves valid numbers, and rejects duplicate dates or observations beyond the vintage.
8. The packet retains the source URL, retrieval time, raw CSV, and sorted observations for display and audit.

Practice question: “Does filtering observation dates alone stop revisions from leaking?” Answer: No. It is the request to ALFRED with `vintage_date` that selects the historic values; date validation is an additional consistency check. This guide prepares the exercise but is not evidence that the required no-AI explanation took place.

## Project 2 decision

**Admit DGS10 conditionally as a contextual macro input.** Explicit research assumption: execute at the regular U.S. equity-session open (9:30 a.m. America/New_York) on trading date D. Select the ALFRED vintage V = D minus one calendar day and its latest nonmissing observation M. This intentionally sacrifices potential freshness because a vintage dated D does not establish availability before that day's open; it is not a claim to use the freshest timestamp-verified information.

Compute **feature age = (D - M).days**, in calendar days. Do not compute age from V or from the latest observation in today's CSV. Exactly seven days is allowed; more than seven triggers quarantine. If V is unavailable, contains no observations, or the chosen observation is future-dated relative to D, also quarantine rather than substitute today's data. Preserve execution time/time zone, decision date D, selected vintage V, measured date M, feature age, retrieval timestamp, units, and raw-file hash. This is the Project 2 policy; the lab app reports vintage comparisons and does not execute trades or implement the seven-day gate.

The seven-day threshold is a stated research policy, not a source guarantee. **What changes the decision:** unexplained historical corrections, missing vintage coverage, changed units, or an unverified publication schedule trigger quarantine until resolved and the relevant backtest is rerun. A strategy requiring same-day execution needs verified release timestamps and execution after publication before relaxing the prior-day rule. Admission is permission to research a timely input, not evidence of profitable forecasting; any predictive rule still needs a frozen specification and an untouched holdout.

## Learn and reflect — AI-assisted preparation

A data card is a concise record of what a dataset represents, who publishes it, its units and frequency, timing and revision behavior, and when it was retrieved. The timing fields prevent confusing measurement with availability; the vintage and provenance let a reviewer reconstruct the exact information set. “Cleaned the data” describes processing but does not establish when a trader could know a number, whether it was later revised, or whether the units were understood.

For DGS10, the tested vintage endpoints show short publication lag and zero revisions, but dates still matter: September 30's 5.29% would leak into a decision whose actual vintage only had September 29's 5.26%. Today's PAYEMS data create a larger revision example: a backtest would incorrectly know December 2024's later downward adjustment. Such leakage overstates the information available and can inflate apparent forecasting skill; the effect on actual portfolio return cannot be quantified without a defined and tested trading rule.

## Rubric evidence and remaining actions

| Criterion | Prepared evidence | Remaining action |
|---|---|---|
| Historical verification | Four matching rates and PAYEMS revision, saved CSVs and log | None for the recorded source checks |
| Functioning app | Four charts, additional ID, vintage table, counts, links, isolated errors; UI test passes | Run locally for the classroom demonstration |
| Data card | All metadata fields, dated comparisons, three reconciled source rows | Complete — Brandon confirmed all three manual checks |
| Fresh eyes | Josh's publication-timing challenge recorded and answered with sources; rule clarified | Discuss the response with Josh |
| Decision | Conditional admission, explicit as-of rule, quarantine conditions | Review and explain the decision personally |

Before submission: confirm the no-screen activity if not already completed, complete the Lab 17 Brightspace attempt, and upload the Markdown, app, data module, dependencies, tests, and evidence to your GitHub repository. Brandon's conceptual no-AI explanation, code walkthrough, Josh's code question and Brandon's answer, and completed manual FRED checks are recorded above. Submit actual GitHub file links; none are invented here. The local folder has no `.git` metadata and no destination repository was supplied, so publication is not claimed.

Assignment: [Lab 17 — Point-in-Time Audit](https://github.com/CinderZhang/FIN43900-Fall2026/blob/main/lessons/week-10/lab-17-point-in-time.md).

Built with Codex assistance. Educational demonstration, not investment advice.


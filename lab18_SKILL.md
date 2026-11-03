---
name: buffett-business
description: Assess a ticker as a Buffett-style business using five annual SEC 10-K periods, deterministic ROE and owner earnings checks, and a grounded Markdown memo. Use for Lab 18 or a business-quality review; excludes stock prices and valuation.
---

# Buffett business review

Run the bundled `lab18_edgar.py TICKER --user-agent "Name email" --output-dir PATH`.
Use the user's actual SEC contact identification, or `SEC_USER_AGENT`; never invent it.
For reproduction use `--facts-file PATH` with the saved ticker directory and provenance sidecar.
The script downloads SEC's ticker mapping and companyfacts without keys. Do not install
FAskills or call its paid data services. Read its Buffett page only as philosophical guidance:
https://github.com/CinderZhang/FAskills/blob/main/financial-researcher/experts/warren_buffett.md

The code alone selects the latest five fiscal-year ends, 10-K filings, annual flows,
latest-filed duplicate observations, and the lab's ordered XBRL tags. It computes ROE
using year-end equity and the simplified owner-earnings proxy OCF minus total capital
spending. Do not substitute a maintenance-capex estimate. Missing values stay
`not found`; invalid ROE and incomplete checks stay `not known`. Derived metrics have
input tags, not invented XBRL tags. Inspect the printed table and provenance.

Write `TICKER_memo.md` after reading the script's output. Adopt a clearly labeled,
AI-simulated Buffett perspective, not an authentic Buffett statement. Select **own the
business**, **watch it**, or **pass**. Judge durability, understandable economics,
capital allocation, and uncertainty; distinguish inference from demonstrated facts.
Passing numerical checks does not prove a moat or management quality. Do not use
market prices, price targets, projections, unsupported ratios, or external numbers.
Use only numeric tokens exactly printed by the script, preserving units and metric
context. State that JPM's owner earnings cannot be judged when its required tags
are absent. Do not generate the qualitative verdict mechanically from the checks.

Run the script again with the same saved input and `--check-memo TICKER_memo.md`.
Resolve every unsupported number before delivery. This token audit checks numeric
support, not semantic truth; manually confirm metric, period, units, and attribution.
Give the user the report, memo, provenance, and limitations. Keep the user's own
trust decision distinct from the AI memo; a proposed decision is a draft until adopted.

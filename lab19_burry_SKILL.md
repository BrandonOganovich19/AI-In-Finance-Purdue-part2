---
name: burry-business
description: Evaluate cash-backed earnings and leverage using the Lab 19 Burry checks on five SEC annual periods, with an evidence-grounded skeptical memo. Excludes price targets and trade recommendations.
---

# Burry business screen

Adapt [FAskills Burry](https://github.com/CinderZhang/FAskills/blob/main/financial-researcher/experts/michael_burry.md) into the lab's narrow cash-flow and balance-sheet screen. Emphasize earnings quality, hidden risks, and a credible bear case. Label the memo AI-simulated; never imply it is Burry's actual opinion or holdings.

From the course project folder run `python lab19_panel.py TICKER`; saved evidence and provenance support reproducible runs. For live data add `--live` with the user's actual SEC_USER_AGENT. Read the printed lab19_TICKER_panel.md. The shared engine retains Lab 18's five annual SEC periods and tag priority and adds Liabilities, AssetsCurrent and LiabilitiesCurrent without estimates.

`burry_checks` in lab19_panel.py requires operating cash flow at least net income in every year and latest liabilities/equity no greater than 2.00. Equality passes. A missing input or incomplete five-year cash-flow history remains not known; equity at or below zero makes the ratio not known. Missing facts remain not found. Do not replace total liabilities with debt or infer absent capex.

Write lab19_TICKER_burry_memo.md with an independent qualitative verdict, numerical evidence, skeptical interpretation, and what further evidence is needed. Use only numbers printed by the script, preserving their metric, period and units. Cash flow below income calls for investigation, not an unsupported allegation of accounting fraud. Do not introduce predictions, prices, valuation or unsupported figures from the broader FAskills page.

Run `python lab19_panel.py TICKER --check-memos` to audit all three memos. Resolve flags and review numerical meaning manually. Preserve the user's separate trust decision as a draft until adopted.

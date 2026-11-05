---
name: graham-business
description: Evaluate a company with the Lab 19 Graham defensive screen on five SEC annual periods and write a memo grounded in printed facts. Excludes price targets and full Graham valuation.
---

# Graham business screen

Use the lab adaptation of [FAskills Graham](https://github.com/CinderZhang/FAskills/blob/main/financial-researcher/experts/ben_graham.md): emphasize defensive financial condition, earnings stability, and disciplined rules. This is an AI-simulated perspective, not an authentic statement by Graham. The lab deliberately narrows the source's much broader valuation framework.

From the the course project folder project directory run `python lab19_panel.py TICKER` on saved SEC evidence, or add `--live` with the user's real SEC_USER_AGENT environment variable. The shared engine selects the same five annual periods and facts for all investors, preserving ordered Lab 18 tags and missing values. Read lab19_TICKER_panel.md before writing lab19_TICKER_graham_memo.md.

The skill's executable parameter is in [lab19_graham_rules.json](lab19_graham_rules.json). `panel.py` loads its current_ratio_min default. Keep 2.00 for the defensive screen. For the required probe change it to 1.00, run COST, compare, then restore 2.00; a command-line `--threshold 1.00` is an explicit temporary override of the same parameter. Do not edit observed facts.

`graham_checks` in lab19_panel.py applies: latest current ratio at least the configured threshold; net income strictly positive in every year; last net income strictly greater than first. Incomplete five-year histories or missing required inputs stay not known; unavailable facts stay not found. Ratios use unrounded Decimal arithmetic and positive denominators.

Write a separate qualitative verdict and memo using only numbers printed by the shared script, with their correct metric, year and USD-million units. Explain how liquidity and earnings lead to the judgment; distinguish inference from fact. Do not invent prices, margin of safety, predictions, or missing inputs. A passing screen is not proof of investment suitability. Include one line under the memo naming the retained threshold and why.

Run `python lab19_panel.py TICKER --check-memos` after all three memos exist. Resolve every unprinted token and manually check meaning and units; token membership does not prove semantic accuracy.

# Lab 18 — Study notes for the partner explanation

These notes were prepared with AI help. They support preparation; they do not certify completion of the required no-AI classroom explanation.

## What can code do, and what requires judgment?

Code can select reported annual facts, divide income by equity, subtract capital spending from operating cash flow, and apply explicit thresholds. These operations should produce the same answer for the same inputs and rules.

Judgment decides whether the economics are understandable, competitive advantages are durable, management allocates capital responsibly, and the evidence is sufficient. The historical table alone does not establish those claims. The model can explain its interpretation, but it cannot turn an interpretation into an audited fact.

## Explain `make_year_row` line by line

Open [edgar.py](lab18_edgar.py) and find `def make_year_row(facts, end)`.

| Code | Explanation |
|---|---|
| `row = {'fiscal_year_end': end}` | Start the output with the actual accounting period end, not the year the filing was submitted. |
| `for metric, tags in TAGS.items():` | Visit the required metrics and each metric's ordered list of acceptable XBRL tags. |
| `row[metric] = select_fact(...)` | Find the annual fact for this end. Equity instead requires an instant balance. Keep provenance with the value. |
| `ni = row['net_income']['value']` | Read reported net income; it can be `None` if absent. |
| `equity = row['equity']['value']` | Read ending shareholders' equity, not an average of balances. |
| `ocf = row['operating_cash_flow']['value']` | Read annual operating cash flow without changing a negative sign. |
| `capex = row['capital_spending']['value']` | Read annual capital spending from the allowed tag; do not estimate it. |
| `row['roe'] = ...` | If income/equity is missing or equity is nonpositive, store `None`; otherwise calculate the unrounded Decimal ratio and retain its precision as text in JSON. |
| `row['owner_earnings'] = ...` | If either cash input is missing, store `None`; otherwise subtract capital spending from operating cash flow. |
| `return row` | Return the data and derived values to the report and app layers. |

**Where does “not found” come from?** `select_fact` returns `value: None` after exhausting the acceptable tags with no eligible observation. `money(None)` renders that absence as `not found`. The calculation does not insert the words into a numeric field or treat them as zero. `percent(None)` instead displays `not known`, and `checks` propagates missing inputs into unknown results.

**How does `select_fact` choose a value?** It visits tags in prescribed order, keeps only USD 10-K observations with the requested end and appropriate duration, and selects the greatest filing date and accession. It only tries the fallback tag when no qualifying primary-tag fact exists.

**Why not use `fy` directly?** A filing can repeat comparative observations. A past accounting period can therefore appear in a filing with a later fiscal-year label. The start/end dates identify the period whose performance is measured.

**Why preserve a failed threshold after rounding?** A ratio just below the cutoff can display as the cutoff after rounding. Testing the original Decimal value avoids a false pass.

## Agent-skills learning

A skill is a discoverable instruction package with a name, description, and task-specific procedure. This package also includes a deterministic program. The name and description let the assistant decide whether the task matches; loading the full instructions only when needed avoids filling context with unrelated procedures. Supporting code can execute without requiring the model to mentally reproduce every calculation. [Official documentation](https://learn.chatgpt.com/docs/build-skills).

Numbers belong in code because period filters, tag priority, arithmetic, and missing-data rules need to be inspectable and repeatable. A model can silently change the denominator, confuse a filing year with a fiscal period, or repeat an unsupported figure. Our browser comparison demonstrates that even plausible figures can use the wrong convention for this assignment.

## Reflection preparation

**What stays the same?** With the same saved SEC response, the extraction rules, selected periods/tags, formulas, checks, and printed results stay the same. A live refresh can change the source data; a saved hash and retrieval date make that distinction visible. The memo's language and qualitative judgment can vary, so those parts require review.

**What remains the model's job?** Interpret what the cash and equity record suggests, explain uncertainty, and choose a business-quality stance without inventing additional numbers or pretending to establish a purchase price.

**Why is “not found” better than an estimate?** It preserves the actual limit of the source and avoids converting missing capex into a false owner-earnings figure. JPM shows why a seemingly convenient substitution could produce unjustified checks and a misleading verdict. A disclosed gap guides additional research.

## Demonstration sequence

1. Start the app on COST. Show both chart series, the annual table, the pass results, and the underlying tags.
2. Explain the positive endpoint growth alongside the intermediate owner-earnings decline. The endpoint rule does not require monotonic growth.
3. Add `The ROE was 40.0%.` in the memo editor. Show the flag, then remove it and show the successful audit.
4. Switch to JPM. Explain why missing capital spending stays missing and why the two owner-earnings checks cannot be decided.
5. Show the fresh-chat comparison and explain the difference between average and ending equity.
6. Read Brandon's decision under the COST memo. Explain why a business-quality judgment is not a price recommendation.

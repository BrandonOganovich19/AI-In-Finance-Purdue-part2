# Lab 19 — explanation preparation

These are AI-assisted study notes. Practice until you can explain the actual code without using these notes or AI in the required classroom exercise; they do not establish completion of that exercise.

## Explain graham_checks line by line

| Statement | Explanation |
|---|---|
| `threshold = Decimal(str(threshold))` | Read the explicit screen parameter as a decimal rather than rounding a computed ratio. |
| `if not threshold.is_finite() or threshold <= 0` | Reject meaningless thresholds such as NaN, infinity, zero, and negatives. |
| `income = [...]` | Collect each selected year's actual net income; an absent fact is None, never zero. |
| `latest_ratio = ... if rows else None` | Use the final chronological year's current ratio; an empty series has no known ratio. |
| `growth = None if ... else ...` | Require a five-period window and both endpoint income values, then subtract first income from last. An absent intermediate income makes the every-year positivity check unknown, even if endpoint growth is measurable. |
| First dictionary entry | Use `status` to apply the inclusive current-ratio threshold to the latest valid ratio. |
| Second dictionary entry | Use `all_five` to require positive income for every annual period. |
| Third dictionary entry | Use `status` to require strictly positive endpoint income growth. Flat income fails. |
| `return {...}` | Return independent pass/fail/not-known statuses; no qualitative verdict is generated here. |

`status` returns not known immediately for None. Otherwise it applies its predicate and returns pass or fail. `all_five` returns not known if the window is incomplete or any required value is missing, then applies the predicate across all five known values. The conservative missing-data convention keeps even a known failing observation from being summarized as a complete-window result when another required observation is absent.

## Likely partner questions

**What if current liabilities are zero?** The ratio helper rejects a nonpositive denominator and returns None. Graham's ratio check becomes not known; it does not create infinity or automatically pass.

**What if one year of net income is missing?** The positivity check is not known. Endpoint growth can still be known if both endpoints and the five-period calendar are present. Each check depends only on its required inputs.

**Why can Burry fail when Buffett passes?** Buffett asks whether cash after total capex is positive and has grown. Burry asks whether operating cash flow covers accounting net income in every year; a company can generate positive cash while generating less cash than reported profit.

**Why do you not simply average the votes?** The checks test different properties and share common evidence and extraction logic. Averaging would hide a specific concern and would not provide independent confirmation.

**Is liabilities/equity debt/equity?** No. The required numerator is total Liabilities, which includes obligations beyond interest-bearing debt. The report and memos keep that distinction.

**Why latest-year leverage but every-year cash conversion?** These are the assignment's explicit rules. Changing the scope would change the model, so the function makes the distinction visible.

**Does a clean number flag prove the memo is true?** No. A printed number could be attached to the wrong year or metric. The audit is an exact-token guard plus a separate human semantic review.

## Demonstration sequence

1. Open the app on COST, showing the panel table and all three memo columns. Identify the 1.06 current ratio and 1.49 liabilities/equity ratio in the annual evidence.
2. Select the 1.00 Graham probe and show his total changing to all passes. Explain the unchanged facts, warning, and restored 2.00 rule.
3. Add `Unsupported 987654321.123%.` to each memo editor in turn. Show the investor-specific flag, then remove the addition.
4. Switch to NVDA and explain Burry's cash-flow failure alongside the favorable liquidity and leverage results.
5. Switch to JPM and show that missing capital spending does not become zero and missing current-balance-sheet facts do not become a guessed current ratio.
6. Open graham_checks and practice the line-by-line explanation. Discuss the prepared bull and bear cases and decide whether to adopt or revise the proposed condition.

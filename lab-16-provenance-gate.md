# Lab 16 — Provenance Gate

Brandon Oganovich | FIN43900 | October 27, 2026

## Result

`asof.py` reproduces the Lab 16 known answer exactly: the row funnel (11 quarantined; 7, 3, 8, 10 and 2 removed), the six-row as-of panel (1, 4, 5, 6, 9, 12), and both signal columns. Setting the decision date to 2026-04-15 turns the as-of signal into the naive signal, ticker for ticker. Every number is computed from the pasted table and the decision date. None is typed in.

The gap between the two signal columns comes only from rows published after 31 March (rows 3, 8 and 10). On AAA that leak is **+3.85 points** that nobody had on 31 March (+5.83% naive vs +1.98% knowable). The provenance gate passes all six panel rows, but four of them (1, 4, 9, 12) break basic bond pricing. On time is not the same as true.

## Files and use

|File|Purpose|
|-|-|
|[`asof.py`](asof.py)|The point-in-time filter, standard library only. Editable inputs at the top: the pasted table and `DECISION\_DATE = "2026-03-31"`.|
|[`test\_asof.py`](test_asof.py)|Known-answer tests: funnel, panel, both signal columns, a hand-calculated check, the row 2 / row 4 revision trap, a row published *on* the decision date, swap and break.|
|[`verify\_lab16.py`](verify_lab16.py)|Regenerates `lab16\_verification.txt` (both runs plus the tests), like `verify\_lab15.py`.|
|[`lab16\_verification.txt`](lab16_verification.txt)|Saved verification record.|

With a standard Python installation (no packages to install):

```powershell
python asof.py                    # decision date 2026-03-31
python -m unittest test\_asof -v
python verify\_lab16.py            # rebuilds lab16\_verification.txt
```

For swap and break, edit `DECISION\_DATE` at the top of `asof.py` to `"2026-04-15"`, run it, then undo. `python asof.py 2026-04-15` does the same without editing the file. From the Lab 15 folder, the bundled runtime also works: `.\\tmp\\python-3.12.10-embed-amd64\\python.exe asof.py`.

## D — the question

> On the day you would have traded, what did this data actually say — and how much of what you see now came later?

**Month measured vs. published on.** Every data point has two dates. The *month measured* (ALFRED's `date`) is the period the number describes. The *published-on* date (`realtime\_start`) is the first day anyone could see it. AAA's February price measures February, but it was first published on 10 March (104.0) and revised on 25 March (103.0). A decision on 31 March can use only rows published on or before 31 March. A revision replaces the earlier number only from the day the revision is published.

## R — the training table and the four rules

Twelve rows of fictional one-year zero-coupon bond funds (AAA, BBB, CCC), per 100 of face value, flattened from ALFRED-style API records. Decision date **31 March 2026**. The table is pasted into `asof.py` unchanged, with row numbers kept from start to end.

Rules, in this order:

1. Quarantine a row with no ticker.
2. Remove an exact duplicate (same ticker, month, published-on date and price; the first copy is kept).
3. Remove a row published after the decision date.
4. Where one ticker and month has two publications, keep the latest one published by the decision date (a revision).

**As-of signal** = latest knowable month's price ÷ previous month's price − 1, per ticker.
**Naive signal** = the same calculation using every row's latest publication, ignoring the publication date. In code, the naive path applies rules 1 and 2, skips rule 3, then applies rule 4. Rules 1 and 2 are data hygiene, not timing; dropping them would not change any naive value here.

## V — known answer: matched

### Row funnel

|Funnel step|Rows removed (`asof.py`)|Known answer|
|-|-|-|
|Quarantined: no ticker|11|✅ 11|
|Exact duplicate|7|✅ 7|
|Published after 31 March|3, 8, 10|✅ 3, 8, 10|
|Older vintage replaced by a revision|2|✅ 2|
|**As-of panel**|**1, 4, 5, 6, 9, 12**|✅ 1, 4, 5, 6, 9, 12|

### Signals

|Ticker|As-of signal|Naive signal|Known answer|
|-|-|-|-|
|AAA|+1.98% (February: 103.0 ÷ 101.0)|+5.83% (March: 109.0 ÷ 103.0)|✅|
|BBB|−1.02% (February: 97.0 ÷ 98.0)|−5.15% (March: 92.0 ÷ 97.0)|✅|
|CCC|+0.91% (February: 111.0 ÷ 110.0)|+1.82% (February, revised: 112.0 ÷ 110.0)|✅|

**Classic error avoided:** row 4 (103.0, published 25 March) is kept and row 2 (104.0, published 10 March) is removed as the older vintage. Keeping row 2 would report AAA at 104.0 ÷ 101.0 − 1 = +2.97%.

### Sanity check — by hand on the as-of panel

Zero-coupon yield = 100 ÷ price − 1. Two facts every price must respect: above 100 the yield is negative, and at the same maturity riskier credit is priced lower (AAA above BBB above CCC).

|Row|Fund|Month|Price|Yield|Breaks|
|-:|-|-|-:|-:|-|
|1|AAA|Jan|101.0|−0.99%|negative yield|
|4|AAA|Feb|103.0|−2.91%|negative yield|
|5|BBB|Jan|98.0|+2.04%|nothing|
|6|BBB|Feb|97.0|+3.09%|nothing|
|9|CCC|Jan|110.0|−9.09%|negative yield; priced above BBB and AAA|
|12|CCC|Feb|111.0|−9.91%|negative yield; priced above BBB and AAA|

`asof.py` also prints this check as a **report-only** section, which matches the table above. It does not change the panel or the signals. The four rules form a provenance gate: they ask *when* a number was knowable, not whether it makes sense. A sanity gate has to sit behind them.

## Explain the code — rule 4 (study guide)

```python
def latest\_publication(rows):
    best = {}
    for r in rows:
        k = (r\["ticker"], r\["month"])
        if k not in best or r\["published"] > best\[k]\["published"]:
            best\[k] = r
    keep\_ids = {r\["row"] for r in best.values()}
    kept = \[r for r in rows if r\["row"] in keep\_ids]
    out = \[r for r in rows if r\["row"] not in keep\_ids]
    return kept, out
```

* `best = {}`: one slot per ticker-month, holding the newest publication seen so far.
* `k = (r\["ticker"], r\["month"])`: the grouping key. Two rows with the same key are two vintages of the same number.
* `if k not in best or r\["published"] > best\[k]\["published"]`: take the row if it is the first for that key, or if it was published later than the one stored. For AAA February, row 2 (10 March) goes in first, then row 4 (25 March) replaces it.
* `keep\_ids`: the row numbers of the winners, so original row numbers survive the gate.
* `kept` / `out`: split the input into survivors and removed rows; `out` feeds the funnel print.
* **Why this means "by the decision date":** the function runs *after* rule 3, so every row it sees was already published on or before 31 March. Row 10 (CCC February, 5 April) never reaches it. The naive path calls the same function *without* rule 3, so there row 10 wins. That gives the naive CCC "February, revised" signal.

Likely partner question: *"What if two publications had the same date?"* The `>` is strict, so the first one in table order is kept. That case doesn't occur here: the only same-date pair is row 7, an exact duplicate already removed by rule 2.

## Swap and break

With `DECISION\_DATE = "2026-04-15"`, rule 3 removes nothing. Rule 4 then removes rows 2 and 12, because CCC's later publication (row 10) is now knowable. The as-of signal equals the naive signal ticker for ticker: AAA +5.83% (March), BBB −5.15% (March), CCC +1.82% (February). The difference between the two columns on 31 March is exactly the rows not yet published: 3, 8 and 10.

Partner run of my `asof.py`: Bernat Pascuet — same values ✅ · 2026-04-15 turned as-of into naive ✅
My run of Bernat Pascuet's `asof.py`: same values ✅ · 2026-04-15 turned as-of into naive ✅

## Point-in-time — learn on your own (AI-assisted study draft)

1. **What is look-ahead bias?** Using information in a backtest or decision that was not available when the decision would have been made. It makes weak signals look strong, because the backtest answers a question nobody could have asked at the time.
2. **How it works.** *Event time* is the month a number measures. *Publication time* is when it became public. A *revision* is a later publication of the same event-time number. Look-ahead bias enters when data is indexed by event time and today's final file is used. That file already contains every late release and every revision, including ones published after the decision date.
3. **AAA example.** On 31 March, the newest AAA data anyone had was February's revised 103.0 against January's 101.0: +1.98%. The +5.83% uses March's 109.0, published 10 April, ten days after the trade. It looks better because it is built from a number from the future: +3.85 points of leak.

## Reflect (AI-assisted draft for my review)

1. **Which rule removed the row that mattered most?** Rule 3, the decision-date cut. It removed rows 3, 8 and 10, and those three rows are the *entire* gap between the naive and as-of columns: AAA 3.85 points (row 3), BBB 4.13 points (row 8, the single biggest), CCC 0.91 points (row 10). Rule 4's removal of row 2 matters only to the as-of signal, which it moves by 0.99 points (+2.97% vs +1.98%). It doesn't create the naive gap, because the naive path also replaces row 2 with its revision.
2. **What a backtest built on the naive column would claim:** that on 31 March you already knew March prices for AAA and BBB, and CCC's 5 April revision. It would show a long-AAA / short-BBB spread of about 11 points (+5.83% vs −5.15%) when only about 3 points (+1.98% vs −1.02%) was knowable. The backtest would credit the strategy with returns built on information no trader had.
3. **The fifth rule:** *quarantine any zero-coupon price above 100 per 100 face (implied yield below zero).* On the as-of panel it catches exactly rows 1, 4, 9 and 12 and leaves 5 and 6. A credit-order rule (riskier fund priced above a safer one in the same month) would catch only rows 9 and 12, so it doesn't reach AAA's rows 1 and 4.

## Verification record

`python verify\_lab16.py` passed all **9 tests** on Python 3.12 (also checked on 3.11 and 3.13). See `lab16\_verification.txt`. The tests cover:

* the funnel and panel;
* both signal columns, against the known answer and against a hand calculation;
* the +3.85-point AAA leak;
* the row 2 / row 4 revision trap;
* a row published on the decision date itself counting as knowable (25 March: +1.98%; 24 March: +2.97%);
* swap and break at 2026-04-15;
* pasting the lab table with its header row.

As a preview of Thursday, the tests also check two of Lab 17's training-table dates: 28 February 2026 prints "not enough knowable months", and 30 April 2026 equals the naive signal. Lab 17's multi-date and CSV features are not built yet.

To check that the tests can actually fail, I deliberately broke the code in six ways: rule 4 keeping the earliest vintage, rule 3 using `<` instead of `<=`, no duplicate removal, no quarantine, naive applying the date cut, and a wrong return formula. The suite caught each one.

## Floor evidence map — self-audit, not a promised grade

|Floor requirement|Evidence|Remaining condition|
|-|-|-|
|The filter matches the known answer|Funnel, panel and both signal columns above; `test\_asof.py`; `lab16\_verification.txt`|—|
|The partner's later date turns it into the naive signal|Swap-and-break section; `test\_swap\_and\_break\_later\_date\_equals\_naive` — (done with Bernat Pascuet, recorded above)||
|Submitted individually on GitHub|This file, `asof.py`, tests and record in my repo|Submit the links|

## Personal activities still to complete

* The no-screen explanation (month measured vs. published on) and the no-AI line-by-line explanation of rule 4 with my partner. The study guide above is preparation, not a record that it happened.
* Ask my AI to quiz me on the line I understand least.
* Brightspace → Quizzes → Lab 16.
* Before Thursday: keep `asof.py` matching this known answer, and build my ALFRED series table (prework).

Submit links to this Markdown file and `asof.py`, with `test\_asof.py`, `verify\_lab16.py` and `lab16\_verification.txt` as supporting files.

Assignment: [Lab 16 — Provenance Gate](https://github.com/CinderZhang/FIN43900-Fall2026/blob/main/lessons/week-10/lab-16-provenance-gate.md).

**Disclaimer: This lab was made with Claude. I am not a financial advisor. This project is for educational purposes only and is not investment advice. The bond funds in the training table are fictional.**


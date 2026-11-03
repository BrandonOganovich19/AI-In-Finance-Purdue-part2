# Lab 18 — Legend Investor as Skill

Brandon Oganovich · FIN43900 · November 3, 2026

**Disclaimer:** This project was made with Codex. I am not a financial advisor. For educational purposes only; this is not investment advice.

**Result:** the SEC download reproduces all five COST rows in the lab answer table. All three Buffett checks pass. JPM's capital spending and owner earnings remain missing, and its two owner-earnings checks remain unknown. The app detects an inserted `40.0%`. Thirteen calculation tests and one multi-step Streamlit interaction test pass. The installed skill is discoverable in Codex.

**Brandon's decision:** I provisionally trust the business verdict, but it does not establish a moat or an attractive stock price.

The local technical deliverables, fresh-chat comparison, and decision are complete. Partner exercises, the Brightspace attempt, and actual GitHub publication are not claimed as completed. This folder has no Git repository metadata or configured remote, and no destination repository was supplied. The assignment is completion-based; only the instructor can award points. [Assignment](https://github.com/CinderZhang/FIN43900-Fall2026/blob/main/lessons/week-11/lab-18-legend-investor-as-skill.md).

## Run the app

From the project root on this computer:

```powershell
.\tmp\python-3.12.10-embed-amd64\python.exe run_lab18.py
```

On a computer with standard Python:

```powershell
python -m pip install -r requirements-lab18.txt
python -m streamlit run lab18_app.py
```

Saved SEC evidence is the default, so COST and JPM work without a network connection. For another ticker, choose **Live SEC download** and enter your name and email in the sidebar. The app caches live results for one hour; **Refresh live data** clears the cache. Failures display an error rather than silently substituting saved data. The memo editor updates the audit immediately and provides a Markdown download. New tickers require a memo generated through the skill from their own printed results.

## Use the installed skill

In Codex, request:

> Use $buffett-business on COST. Use my SEC contact identification, save the script results in ., and save the Buffett-style business memo in COST_memo.md. Keep my personal decision separate.

The installed files are [SKILL.md](.agents/skills/buffett-business/SKILL.md) and [edgar.py](.agents/skills/buffett-business/scripts/edgar.py). A visible reference copy is [lab18_SKILL.md](lab18_SKILL.md). On another computer, copy the installed skill folder to `.agents/skills/buffett-business` at the project root. Codex discovery of project skills is documented in [Build skills](https://learn.chatgpt.com/docs/build-skills).

Run a fresh SEC download with standard Python (replace the contact with your own when sharing):

```powershell
$env:SEC_USER_AGENT = 'Brandon Oganovich boganovi@purdue.edu'
python lab18_edgar.py COST --output-dir .
python lab18_edgar.py JPM --output-dir .
```

To replay the exact downloaded data and audit the memo without network access:

```powershell
python lab18_edgar.py COST --facts-file COST_companyfacts.json --output-dir . --check-memo COST_memo.md
```

Replace `python` with `.\tmp\python-3.12.10-embed-amd64\python.exe` on this computer. The script uses only the standard library. Contact identification is supplied at runtime; no account credentials or API keys are stored. The evidence sidecars retain retrieval times, URLs, byte counts, and SHA-256 hashes.

## Objective and build request

The question is whether a repeatable extraction-and-calculation procedure can support an investor-style judgment without allowing the language model to invent the figures.

This is the AI-assisted build specification used for this implementation, not a claim that Brandon independently wrote it before the session:

> Build a reusable Buffett business-review skill and a small Streamlit app. Make Python responsible for SEC downloads, period and tag selection, calculations, checks, and numeric auditing. Preserve missing inputs and expose filing provenance. Let the model judge business quality using only the printed evidence. Demonstrate the result on COST and JPM, compare a separate browser answer, and package reproducible tests and an explanation of the annual-row function. Keep price data out of the analysis.

## Deliverables and evidence

| Requirement | File or evidence | Result |
|---|---|---|
| Discoverable skill with trigger description | [.agents skill](.agents/skills/buffett-business/SKILL.md) | Installed and discovered in this session |
| Bundled ticker-to-CIK download and calculation script | [edgar.py](lab18_edgar.py) | Live COST and JPM downloads completed |
| Five annual rows, tags, and computed checks | [COST output](COST_facts.md), [JPM output](JPM_facts.md) | Required results reproduced |
| AI judgment in Markdown | [COST memo](COST_memo.md), [JPM memo](JPM_memo.md) | Both pass numeric audit |
| Chart, table, checks, editable memo, audit, disclosure | [lab18_app.py](lab18_app.py) | Tested through Streamlit AppTest |
| Known-answer comparison and boundaries | [test_lab18.py](test_lab18.py), [results](calculation_tests.txt) | 13 tests pass |
| Hand-entered unsupported ROE probe in UI | [test_lab18_app.py](test_lab18_app.py), [results](app_tests.txt) | `40.0%` flagged; error clears after removal |
| Separate no-skill chat | [User-supplied response](fresh_chat_response.md), [comparison](fresh_chat_comparison.md) | Received from Brandon and analyzed |
| Personal decision | [COST memo, final line](COST_memo.md) | Supplied by Brandon |
| Learning, reflection, code explanation | [Walkthrough](lab18_WALKTHROUGH.md) | Prepared for the required oral exercise |

The raw companyfacts JSON files are authentic saved responses, not constructed answer fixtures. The answer table appears only in tests. Production calculations never read the expected answers. To reproduce the tests:

```powershell
python test_lab18.py
python test_lab18_app.py
python compare_fresh_chat.py
```

The official skill-creator validator also reported `Skill is valid!`. Its YAML dependency was installed in a temporary project tooling folder, not added to the application runtime.

## Calculation choices and limitations

All accounting values are historical nominal USD. Presentation converts dollars to millions and displays ROE to one decimal place. No inflation, tax, compounding, price, or forecast adjustment is applied. Decimal arithmetic preserves ratio precision before display; checks use unrounded ratios.

The parser accepts only `10-K`, USD facts. A one-year flow must cover 350–380 inclusive calendar days, accommodating leap years and retail calendars while excluding quarters, most transition periods, and multi-year flows. For each annual filing accession, it identifies the latest annual period end, then keeps the latest five distinct ends. It does not mistake a comparative fact's filing-year `fy` label for its accounting period. An unusual nonstandard fiscal transition can be excluded under this documented implementation choice.

For each end, the prescribed first available tag wins; within that tag, the most recently filed qualifying observation wins. This deliberately allows later comparative disclosures to replace earlier numbers. Consequently this is a latest-restated historical review, not a point-in-time backtest. Every selected fact includes tag, start/end, form, filing date, and accession. Only equity is an instant balance; missing flows are not treated as instants.

ROE divides net income by ending equity. Missing or nonpositive equity makes ROE unknown. The owner-earnings proxy subtracts all reported capital spending from operating cash flow. It does not estimate maintenance spending, normalize working capital, or calculate intrinsic value. Missing inputs propagate; zero remains zero and negative cash flow remains negative. A missing year makes the full-window checks unknown. The growth check compares endpoints and does not require every intermediate year to rise. No liabilities/equity ratio is displayed or used.

The memo audit matches complete digit-based numeric tokens against the printed report, preserving signs, separators, and percentage suffixes. It flags unsupported occurrences with line numbers; format changes can conservatively trigger a flag. It cannot establish that a number is used with the correct metric, units, period, or meaning, nor verify qualitative claims. The skill therefore also requires a contextual review. Both memos were reviewed against their respective reports. A numerical pass is not evidence of investment suitability.

## Fresh-chat lesson

The browser response used average equity and named secondary sources without direct source URLs or filing identifiers. Our required denominator is ending equity. Its underlying income and ending-equity figures match, but its ROE figures answer a different question. In FY2024 our result is higher, illustrating why the denominator matters. The full comparison is calculated in [compare_fresh_chat.py](compare_fresh_chat.py). Browser price claims and anecdotes were excluded from the memos.

## Checkout steps still requiring Brandon

1. Perform the no-screen explanation and the line-by-line code walkthrough with your partner. Use the study notes beforehand; do the required explanation without AI. No partner completion or name is invented here.
2. Open and complete the Lab 18 Brightspace attempt yourself.
3. Upload the individual files listed in lab18_submission_manifest.json directly from this project folder, plus .agents/skills/buffett-business. No ZIP or lab18 subfolder is needed for this layout. Do not upload tmp, installed dependencies, or unrelated prior labs.
4. Submit actual GitHub links to this README, the skill, the script, the app, and the memos. Include the individual evidence files so the grader can reproduce the checks. Verify those links open for the instructor. Publication is pending; no GitHub links have been fabricated.

## Sources consulted

- [Lab 18](https://github.com/CinderZhang/FIN43900-Fall2026/blob/main/lessons/week-11/lab-18-legend-investor-as-skill.md) and [prework](https://github.com/CinderZhang/FIN43900-Fall2026/blob/main/lessons/week-11/student-prework.md).
- [FAskills README](https://github.com/CinderZhang/FAskills/blob/main/lab-18-legend-investor-as-skill.md) and [Buffett philosophy](https://github.com/CinderZhang/FAskills/blob/main/financial-researcher/experts/warren_buffett.md), read only. The implementation narrows that broader philosophy to this lab; no FAskills installation or paid data service was used.
- [SEC API documentation](https://www.sec.gov/search-filings/edgar-application-programming-interfaces), [ticker directory](https://www.sec.gov/files/company_tickers.json), [COST facts](https://data.sec.gov/api/xbrl/companyfacts/CIK0000909832.json), [JPM facts](https://data.sec.gov/api/xbrl/companyfacts/CIK0000019617.json).
- [Codex skills](https://learn.chatgpt.com/docs/build-skills) and [Streamlit AppTest](https://docs.streamlit.io/develop/api-reference/app-testing/st.testing.v1.apptest).

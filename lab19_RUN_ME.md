# Lab 19 — start here

The final upload files are saved individually in the usual course folder. No ZIP is needed. Start with [the written submission](lab19_SUBMISSION.md).

## Open the app on this computer

From the course folder in PowerShell:

```powershell
.\tmp\python-3.12.10-embed-amd64\python.exe run_lab19.py
```

Open the local URL printed by Streamlit, normally http://localhost:8501. Start on COST, try the threshold probe, then enter NVDA. JPM is included as an additional missing-data demonstration. All saved examples work without an SEC request or credentials.

On another computer with Python installed:

```text
python -m pip install -r requirements-lab19.txt
python run_lab19.py
```

## Reproduce the calculations and audit

```text
python lab19_panel.py COST --check-memos
python lab19_panel.py NVDA --check-memos
python lab19_panel.py JPM --check-memos
python test_lab19.py
python test_lab19_app.py
```

On this computer, substitute `.\tmp\python-3.12.10-embed-amd64\python.exe` for `python` in those commands. The core SEC calculations require only the Python standard library; the app integration test requires the requirements file's packages.

The numerical tests use independent expected COST answers, boundary and missing-data examples, full memo audits, tampered-memo probes, the actual skill-setting change, and NVDA/JPM source evidence. App tests exercise the actual editors, threshold control, company switching, chart, and invalid ticker handling. See [calculation results](lab19_calculation_tests.txt), [app results](lab19_app_tests.txt), [cross-memo audit](lab19_memo_audit.json), and [threshold probe](lab19_threshold_probe.md).

For a fresh SEC download, set SEC_USER_AGENT locally to your own name and email, then run `python lab19_panel.py NVDA --live --check-memos`. Never commit your contact setting. Refreshing can change the selected years and makes the old memos subject to review; do not assume they remain current.

## Upload these individual files

- Main written work: `lab19_SUBMISSION.md`, `lab19_WALKTHROUGH.md`, `lab19_RUN_ME.md`.
- Code: `lab19_panel.py`, `lab19_edgar.py`, `lab19_app.py`, `run_lab19.py`, `requirements-lab19.txt`, `test_lab19.py`, `test_lab19_app.py`, `verify_lab19.py`.
- Skill definitions: `lab19_buffett_SKILL.md`, `lab19_graham_SKILL.md`, `lab19_burry_SKILL.md`, `lab19_graham_rules.json`.
- Computed evidence: all `lab19_COST_*`, `lab19_NVDA_*`, and `lab19_JPM_*` files; these include raw SEC JSON, source sidecars, printed reports, calculation JSON, and the three memos per ticker.
- Mapping/provenance: `lab19_company_tickers.json`, `lab19_company_tickers.source.json`.
- Verification: `lab19_calculation_tests.txt`, `lab19_app_tests.txt`, `lab19_memo_audit.json`, `lab19_threshold_probe.md`, `lab19_skill_validation.txt`, `lab19_verification.txt`, `lab19_manifest.json`.

The final `lab19_manifest.json` enumerates the upload set with file hashes. The earlier build folder `Lab19_BrandonOganovich` and the helper `prepare_lab19_files.py` are not required for this flat-file version. Do not upload runtime logs, Python packages, caches, or older labs unless separately requested.

The three skill definitions are provided as individual Markdown files for convenient upload. A standard discoverable skill installation uses `.agents/skills/<skill-name>/SKILL.md`; the complete folder-form versions already exist inside `Lab19_BrandonOganovich/.agents/skills/`. The flat runnable application reads `lab19_graham_rules.json` directly, so it needs no skill-installation step to reproduce the checks.

## Before checkout

Review the proposed personal decision and adapt it to your own judgment. Perform the lab's partner exchange and no-AI code explanation yourself; the walkthrough is preparation. Upload the files to your GitHub repository and submit actual GitHub links through the assigned checkout. No grade is guaranteed and no quiz, partner activity, or upload is represented as completed.

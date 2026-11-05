---
name: buffett-business
description: Review business quality using the Lab 18 Buffett checks inside the Lab 19 shared SEC panel and produce a printed-number-grounded memo. Excludes valuation and price predictions.
---

# Buffett business review in the shared panel

This preserves the existing Lab 18 Buffett skill's business focus and rules. Use [FAskills Buffett](https://github.com/CinderZhang/FAskills/blob/main/financial-researcher/experts/warren_buffett.md) for qualitative perspective, not additional data or requirements.

From the course project folder run `python lab19_panel.py TICKER`. The shared pipeline uses the existing lab19_edgar.py extraction and checks: five annual SEC periods; ROE = net income/year-end equity, at least 15.0% every year; owner earnings = operating cash flow minus total capex, positive every year and increasing first to last. Do not estimate maintenance capex. Missing facts remain not found and incomplete checks not known. Live downloads require --live and the user's real SEC_USER_AGENT.

Read lab19_TICKER_panel.md and write lab19_TICKER_buffett_memo.md. Label the viewpoint AI-simulated and select own the business, watch it, or pass based on an explained qualitative judgment, not an automatic count. Discuss durable economics, uncertainty and capital allocation only as far as evidence supports. Use only printed numeric tokens with correct units and periods; no stock prices, predictions or unsupported moat claims. JPM owner earnings cannot be judged when required tags are absent.

Run `python lab19_panel.py TICKER --check-memos` after the three memos are written. Resolve flags and manually review meaning. The user's decision stays separate from the simulated memo.

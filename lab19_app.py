"""Presentation only. Shared calculations and memo auditing live in panel.py."""
import json
import os
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import lab19_panel as panel
import pandas as pd
import streamlit as st

st.set_page_config(page_title='Legend Investor Panel', page_icon='📊', layout='wide')
st.title('Legend Investor Panel')
st.caption('Built with AI help for FIN43900. Educational analysis, not investment advice.')
st.write('Shared SEC annual facts. Different financial priorities. One auditable comparison.')

@st.cache_data(ttl=3600, show_spinner=False)
def live(ticker, contact):
    return panel.base.fetch_company(ticker, contact, ROOT / 'lab19_live_cache')

with st.sidebar:
    st.header('Company and evidence')
    entered = st.text_input('Ticker', 'COST', key='ticker')
    mode = st.radio('Data source', ['Saved SEC evidence', 'Live SEC download'])
    st.caption('Saved examples: COST, NVDA, JPM. JPM demonstrates honest gaps.')
    contact = st.text_input('SEC User-Agent: name and email', os.getenv('SEC_USER_AGENT', ''), type='password')
    if st.button('Refresh live data'):
        live.clear()
    threshold = st.selectbox('Graham current-ratio threshold', ['2.00', '1.00'], key='threshold')
    st.caption('Default retained: 2.00. The 1.00 setting is the sensitivity probe.')

try:
    ticker = panel.base.ticker_symbol(entered)
    if mode == 'Saved SEC evidence':
        result = panel.load_saved(ticker, threshold=threshold)
    else:
        company, source = live(ticker, contact)
        result = panel.analyze(company, ticker, source, threshold)
except (ValueError, OSError, KeyError) as exc:
    st.error(f'Cannot load company: {exc}')
    st.stop()

printed = panel.report_text(result)
st.subheader(f"{ticker} · {result['company']}")
st.caption(f"Retrieved {result['source'].get('retrieved_utc', 'unknown')} · USD millions · ratios in times · ROE uses year-end equity")
if result['source'].get('url'):
    st.markdown(f"[SEC source]({result['source']['url']})")
if len(result['rows']) != 5:
    st.warning('Fewer than five eligible annual periods. Five-year checks remain not known.')
if threshold != '2.00':
    st.warning('Sensitivity probe active. Saved qualitative memos describe the retained 2.00 threshold; they are not automatically rewritten.')

st.subheader('Investor × check')
st.dataframe(pd.DataFrame(panel.panel_rows(result)), hide_index=True, width='stretch')
for col, (name, checks) in zip(st.columns(3), result['panel'].items()):
    col.metric(name + ' checks', f"{list(checks.values()).count('pass')} / {len(checks)} pass")
    col.caption(panel.summary(checks))

st.subheader('Three independent perspectives')
st.caption('AI-simulated perspectives, not statements by the named investors. Qualitative verdicts are analyst judgments, separate from check totals.')
saved = panel.read_memos(ticker)
memos = {}
for col, name in zip(st.columns(3), panel.INVESTORS):
    with col:
        st.markdown(f'### {name}')
        memo = st.text_area(f'{name} memo editor', saved[name], height=290, key=f'{ticker}_{name}')
        memos[name] = memo
        if memo.strip():
            match = re.search(r'\*\*Verdict: (.+?)\*\*', memo)
            st.markdown(match.group(0) if match else '**Verdict: not stated**')
            st.markdown(memo)
            st.download_button(f'Download {name} memo', memo, f'{ticker}_{name.lower()}_memo.md')
        else:
            st.info('Memo not found. Read the printed output and run this investor skill before supplying a verdict.')
        if name == 'Graham':
            st.caption('Threshold retained: 2.00, to preserve the defensive liquidity screen rather than tune it to make a company pass.')

# Always audit every memo, including an editor the user has not touched.
flags = panel.audit_memos(memos, printed)
st.subheader('Unprinted-number flag · all memos')
if flags:
    st.error('Unprinted memo numbers found. Fix the named memo before relying on it.')
    st.dataframe(pd.DataFrame(flags), hide_index=True)
elif all(m.strip() for m in memos.values()):
    st.success('No unprinted numeric tokens across the three memos.')
else:
    st.warning('No unprinted tokens in available text, but the memo panel is incomplete.')
st.caption('This exact-token check cannot verify the meaning, year, units, or attribution of an otherwise supported number. Review those manually.')

st.subheader('Annual evidence · USD millions')
table = []
for r in result['rows']:
    table.append({'Fiscal year end': r['fiscal_year_end'],
                  **{panel.base.LABELS[k]: panel.base.money(r[k]['value']) for k in panel.base.TAGS},
                  'ROE': panel.base.percent(r['roe']), 'Owner earnings': panel.base.money(r['owner_earnings']),
                  **{tag: panel.base.money(r[k]['value']) for k, tag in panel.EXTRA.items()},
                  'Current ratio': panel.fmt_ratio(r['current_ratio']),
                  'Liabilities/equity': panel.fmt_ratio(r['liabilities_equity'])})
st.dataframe(pd.DataFrame(table), hide_index=True, width='stretch')
chart = pd.DataFrame([{'Fiscal year end': r['fiscal_year_end'],
                      'Net income': None if r['net_income']['value'] is None else r['net_income']['value'] / 1e6,
                      'Owner earnings': None if r['owner_earnings'] is None else r['owner_earnings'] / 1e6}
                     for r in result['rows']]).set_index('Fiscal year end')
st.line_chart(chart, x_label='Fiscal year end', y_label='USD millions')
if any(r['owner_earnings'] is None for r in result['rows']):
    st.warning('Owner earnings not found where cash flow or capex is absent. No zero filling.')
st.text_input('Your decision and condition', key=f'decision_{ticker}')
with st.expander('Printed script output and complete provenance'):
    st.markdown(printed)
st.download_button('Download printed evidence', printed, f'{ticker}_panel.md')
st.download_button('Download calculation JSON', json.dumps(result, indent=2), f'{ticker}_panel.json')
st.caption('Owner earnings = operating cash flow less total capital spending; maintenance capex is not estimated. No prices, valuations or forecasts.')

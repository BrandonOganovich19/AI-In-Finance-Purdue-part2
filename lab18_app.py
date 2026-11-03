"""Streamlit presentation; all financial calculations live in the bundled script."""
import hashlib
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import lab18_edgar as edgar
import pandas as pd
import streamlit as st

st.set_page_config(page_title='Buffett Business Review', page_icon='📊', layout='wide')
st.title('Buffett Business Review')
st.caption('Data from SEC EDGAR; built with AI help, a learning demonstration, not investment advice.')
st.caption('This project was made with Codex. I am not a financial advisor. For educational purposes only; this is not investment advice.')
st.write('Study the business through annual cash generation and returns on equity. All amounts are USD millions; ROE uses year-end equity.')

@st.cache_data(ttl=3600, show_spinner=False)
def live_analysis(ticker, contact):
    company, source = edgar.fetch_company(ticker, contact, ROOT / 'live_cache')
    return edgar.analyze(company, ticker, source)

def saved_analysis(ticker):
    path = ROOT / f'{ticker}_companyfacts.json'
    raw = path.read_bytes()
    source = json.loads(path.with_suffix('.source.json').read_text(encoding='utf-8'))
    if hashlib.sha256(raw).hexdigest() != source['sha256']:
        raise ValueError('Saved evidence hash mismatch. Refresh the SEC download.')
    return edgar.analyze(json.loads(raw), ticker, source)

with st.sidebar:
    st.header('Company and evidence')
    entered = st.text_input('Ticker', 'COST', key='ticker')
    mode = st.radio('Data source', ['Saved SEC evidence', 'Live SEC download'], key='mode')
    st.caption('Saved evidence supports COST and JPM. Live mode accepts any SEC-listed ticker with eligible annual facts.')
    contact = st.text_input('SEC User-Agent: name and email', os.getenv('SEC_USER_AGENT', ''), key='contact')
    if st.button('Refresh live data'):
        live_analysis.clear()
    st.caption('No API keys. Missing facts remain missing. A refresh can change the latest five years.')

try:
    ticker = edgar.ticker_symbol(entered)
    with st.spinner('Reading SEC evidence…'):
        result = saved_analysis(ticker) if mode == 'Saved SEC evidence' else live_analysis(ticker, contact)
except (OSError, ValueError, KeyError) as error:
    st.error(f'Cannot load company: {error}')
    st.stop()

printed = edgar.report_text(result)
st.subheader(f"{ticker} · {result['company']}")
source = result['source']
st.caption(f"{'Saved snapshot' if mode == 'Saved SEC evidence' else 'Live download (cached up to one hour)'} · Retrieved {source.get('retrieved_utc', 'unknown')}")
if source.get('url'):
    st.markdown(f"[SEC company-facts source]({source['url']})")
if len(result['rows']) < 5:
    st.warning('Fewer than five eligible annual periods are available. Five-year checks are not known.')

chart = pd.DataFrame([{'Fiscal year end': r['fiscal_year_end'],
                       'Owner earnings': None if r['owner_earnings'] is None else r['owner_earnings'] / 1e6,
                       'Net income': None if r['net_income']['value'] is None else r['net_income']['value'] / 1e6}
                      for r in result['rows']]).set_index('Fiscal year end')
st.subheader('Cash generation and accounting earnings')
st.line_chart(chart, y_label='USD millions', x_label='Fiscal year end')
if any(r['owner_earnings'] is None for r in result['rows']):
    st.warning('Owner earnings: not found where operating cash flow or capital spending is missing. Missing values are not plotted as zero.')

table = pd.DataFrame([{'Fiscal year end': r['fiscal_year_end'],
                      **{edgar.LABELS[k]: edgar.money(r[k]['value']) for k in edgar.TAGS},
                      'ROE': edgar.percent(r['roe']), 'Owner earnings': edgar.money(r['owner_earnings'])}
                     for r in result['rows']])
st.subheader('Annual facts · USD millions')
st.dataframe(table, hide_index=True, width='stretch')
st.subheader('Code-computed Buffett checks')
for column, (label, status) in zip(st.columns(3), result['checks'].items()):
    column.metric(label, status.upper())

st.subheader('AI-simulated Buffett memo')
memo_path = ROOT / f'{ticker}_memo.md'
default_memo = memo_path.read_text(encoding='utf-8') if memo_path.exists() else ''
memo = st.text_area('Memo editor — paste a skill-generated memo or test an unsupported number',
                    default_memo, height=290, key=f'memo_{ticker}')
if not memo:
    st.info('No memo saved for this ticker. Run the Buffett skill on the printed facts below, then paste its Markdown memo here. The app does not invent a verdict.')
else:
    flags = edgar.unsupported_numbers(memo, printed)
    if flags:
        st.error('Unsupported memo numbers: ' + '; '.join(f"{f['number']} (line {f['line']})" for f in flags))
        st.dataframe(pd.DataFrame(flags), hide_index=True)
    else:
        st.success('Every numeric token in this memo appears in the script output.')
    st.caption('Exact printed-number audit: signs and percent units matter. It does not verify that a supported number is assigned to the correct metric or year; review those claims too.')
    st.markdown(memo)
    st.download_button('Download edited memo (.md)', memo, f'{ticker}_memo.md', 'text/markdown')

st.text_input('Your decision — do you trust this verdict, and why?', key=f'decision_{ticker}')
with st.expander('Full script output and XBRL provenance'):
    st.markdown(printed)
    st.json(source)
st.download_button('Download script output (.md)', printed, f'{ticker}_facts.md', 'text/markdown')
st.download_button('Download calculation evidence (.json)', json.dumps(result, indent=2), f'{ticker}_analysis.json', 'application/json')
st.caption('Owner earnings here means operating cash flow minus total capital spending, the lab proxy. It is not a maintenance-capex valuation. No stock-price data or investment-price judgment is included.')

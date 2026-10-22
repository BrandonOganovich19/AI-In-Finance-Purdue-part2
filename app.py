"""Run: python -m streamlit run app.py"""
from copy import deepcopy
from hashlib import sha256
from io import StringIO
from html import escape
import streamlit as st
import portfolio as engine

st.set_page_config(page_title='Portfolio Lab | Finance', page_icon='📊', layout='wide')
st.markdown('''
<style>
.stApp { background: #f7f8fa; }
.block-container { max-width: 1440px; padding-top: 1.8rem; }
[data-testid="stSidebar"] { background: #fff; border-right: 1px solid #e4e7ec; }
h1, h2, h3 { letter-spacing: -.035em; color: #151820; }
h1 { font-size: 2rem !important; }
h3 { font-size: 1.2rem !important; }
.finance-header { display:flex; align-items:center; justify-content:space-between;
  gap:16px; flex-wrap:wrap; border-bottom: 1px solid #dfe3eb; padding-bottom:20px; margin-bottom:24px; }
.finance-brand { font-size:27px; font-weight:850; letter-spacing:-1.2px; color:#6001d2; }
.finance-brand span { color:#1c2230; font-weight:500; }
.finance-tag { color:#596273; font-size:12px; letter-spacing:.08em; text-transform:uppercase; }
.finance-kicker { font-size:11px; font-weight:700; letter-spacing:.12em; color:#687184; margin-bottom:6px; }
.quote-card { background:white; border:1px solid #e1e5ed; border-top:3px solid #6001d2;
  padding:16px; border-radius:9px; margin:8px 0 22px; min-height:139px; }
.quote-name { font-weight:650; font-size:13px; color:#30384a; min-height:36px; }
.quote-value { font-size:25px; font-weight:750; color:#161c28; font-variant-numeric:tabular-nums; }
.quote-note { color:#697386; font-size:11px; margin-top:4px; }
[data-testid="stMetric"] { background:white; border:1px solid #e1e5ed; border-radius:9px; padding:16px; }
[data-testid="stMetricValue"] { font-size:1.8rem; letter-spacing:-.04em; }
[data-testid="stTable"] { background:white; border-radius:9px; overflow:hidden; }
[data-testid="stTable"] th { background:#f0edf8; color:#45405a; }
[data-testid="stExpander"] { background:white; border-radius:9px; }
.allocation-row { display:grid; grid-template-columns:minmax(100px, 1fr) 2fr 54px;
  gap:12px; align-items:center; padding:10px 0; font-size:12px; color:#475166; }
.allocation-track { background:#ece7f5; border-radius:4px; height:9px; overflow:hidden; }
.allocation-fill { background:#6001d2; height:100%; border-radius:4px; }
.allocation-weight { text-align:right; font-weight:700; font-variant-numeric:tabular-nums; }
.footer-note { border-top:1px solid #dfe3eb; padding-top:16px; font-size:12px; color:#687184; }
@media (max-width: 700px) {
  .block-container { padding-left:1rem; padding-right:1rem; }
  .finance-brand { font-size:23px; }
  .quote-card { margin-bottom:8px; min-height:110px; }
}
</style>
<div class="finance-header">
  <div class="finance-brand">portfolio<span> / finance</span></div>
  <div class="finance-tag">FIN43900 · Research workspace · Educational estimates</div>
</div>
<div class="finance-kicker">PORTFOLIO LAB / STABILITY ANALYSIS</div>
''', unsafe_allow_html=True)
st.title('Portfolio Stability Decision')
st.caption('Built with AI help, a learning demonstration, not investment advice.')
st.sidebar.markdown('### Portfolio setup')
st.sidebar.caption('Set the mandate, then stress-test the estimates.')
st.sidebar.header('Mandate controls')
objective = st.sidebar.number_input('Annual nominal return objective (%)', value=6.5, step=.1) / 100
reserve_min = st.sidebar.number_input('Minimum reserve (%)', min_value=0.0, max_value=100.0, value=3.0, step=1.0) / 100
uploaded = st.sidebar.file_uploader('Monthly adjusted prices CSV', type=['csv'])
last_36 = st.sidebar.checkbox('Use last 36 monthly returns', disabled=uploaded is None)
st.sidebar.caption('Project 2: VTI / QQQ / VOO / SCHD. Objective 5.5% assumes 2.5% CPI; reserve minimum 3%. None of these equity ETFs is reserve-eligible under the existing mandate.')

try:
    if uploaded is None:
        loaded, loaded_corr = deepcopy(engine.SLEEVES), deepcopy(engine.CORRELATIONS)
        current, corr = deepcopy(loaded), deepcopy(loaded_corr)
        dataset = 'meridian'
        st.info('Meridian annual training estimates. Reserve eligibility follows the course inputs.')
    else:
        raw = uploaded.getvalue()
        dataset = sha256(raw).hexdigest()[:16]
        text = raw.decode('utf-8-sig')
        loaded, loaded_corr = engine.estimate_from_csv(StringIO(text))
        current, corr = engine.estimate_from_csv(StringIO(text), last_36)
        st.info('Historical estimates, not forecasts. CSV reserve eligibility starts unchecked; apply your mandate.')
        if {s['name'].upper() for s in current} == {'VTI', 'QQQ', 'VOO', 'SCHD'}:
            st.info('Your selected funds are all equity ETFs. Leave their reserve boxes unchecked under the current mandate. With the 3% reserve floor, no mix is feasible; dividends do not make SCHD a government-security reserve.')
    quotes = st.container()
    with st.expander('Edit return estimates & reserve eligibility', expanded=True):
        st.caption('Change an annual return estimate to see how the allocation responds. All values below are percentages.')
        for i, asset in enumerate(current):
            left, right = st.columns([3, 2])
            asset['return'] = left.number_input(
                f"{asset['name']} return estimate (%)", value=asset['return']*100,
                step=.1, key=f'return_{dataset}_{last_36}_{i}') / 100
            eligible = right.checkbox(f"{asset['name']} reserve-eligible",
                                      value=asset['reserve'], key=f'reserve_{dataset}_{i}')
            asset['reserve'] = loaded[i]['reserve'] = eligible
    with quotes:
        for column, asset in zip(st.columns(len(current)), current):
            column.markdown(
                f'<div class="quote-card"><div class="quote-name">{escape(asset["name"])}</div>'
                f'<div class="quote-value">{asset["return"]*100:.2f}%</div>'
                '<div class="quote-note">Annual return estimate · not a live quote</div></div>',
                unsafe_allow_html=True)
    baseline = engine.search_portfolio(loaded, loaded_corr, objective, reserve_min)
    result = engine.search_portfolio(current, corr, objective, reserve_min)

    def display(column, title, answer):
        with column:
            st.subheader(title)
            if answer is None:
                st.warning('no mix meets the objective')
                return
            st.table([{'Asset': s['name'], 'Weight (%)': f'{w*100:.2f}'}
                      for s, w in zip(current, answer['weights'])])
            st.metric('Annual return estimate', f"{answer['return_estimate']*100:.2f}%")
            st.metric('Annual volatility estimate', f"{answer['volatility']*100:.2f}%")
            st.metric('Reserve-eligible weight', f"{answer['reserve']*100:.2f}%")
            bars = ''.join(
                f'<div class="allocation-row"><span>{escape(s["name"])}</span>'
                f'<div class="allocation-track"><div class="allocation-fill" style="width:{w*100:.2f}%"></div></div>'
                f'<span class="allocation-weight">{w*100:.2f}%</span></div>'
                for s, w in zip(current, answer['weights']))
            st.markdown(bars, unsafe_allow_html=True)

    st.subheader('Portfolio comparison')
    st.caption('Lowest estimated volatility on the 5-point allocation grid, subject to your mandate.')
    left, right = st.columns(2)
    display(left, 'Current inputs', result)
    display(right, 'As loaded (all months for CSV)', baseline)
    if result and baseline:
        change = max(abs(a-b) for a, b in zip(result['weights'], baseline['weights']))*100
        st.metric('Largest absolute weight change', f'{change:.2f} percentage points')
    else:
        st.caption('Largest weight change: unavailable when either search is infeasible.')
    st.caption('Both searches use the same objective and reserve selections. Long-only, fully invested, 5-point grid. '
               'Minimum risk means minimum estimated volatility on this grid. Costs, taxes, turnover, issuer limits '
               'and future loss limits are not modeled. The 36-month option uses 37 prices.')
except (ValueError, UnicodeDecodeError, TypeError, KeyError) as exc:
    st.error(f'Input error: {exc}')

st.divider()
st.caption('This project was made with Codex. I am not a financial advisor. For educational purposes only; this is not investment advice.')
st.caption('Independent classroom project. Not affiliated with Yahoo Finance. No live market feed.')

# This project was made with Codex. I am not a financial advisor.
# For educational purposes only; this is not investment advice.

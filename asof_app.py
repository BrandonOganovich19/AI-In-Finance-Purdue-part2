"""Run with python -m streamlit run asof_app.py. AI-assisted educational lab."""
from datetime import date
import pandas as pd
import streamlit as st
from asof_data import NAMES, compare, fetch, validate_id

@st.cache_data(ttl=3600, show_spinner=False)
def download_current(series, download_day):
    """One public FRED CSV request; the day prevents yesterday's cache being reused."""
    return fetch(series)

@st.cache_data(ttl=3600, show_spinner=False)
def download_as_known(series, as_known_on, download_day):
    """Request the actual historical vintage, never a truncated current file."""
    return fetch(series, as_known_on)

def main():
    st.set_page_config(page_title='Point-in-Time Rates Audit', layout='wide')
    today = date.today()
    st.title('Point-in-Time Rates Audit')
    st.caption(f'Data from FRED and ALFRED, Federal Reserve Bank of St. Louis, downloaded today ({today}); built with AI help, a learning demonstration, not investment advice.')
    selected = st.sidebar.multiselect('Series', list(NAMES), default=list(NAMES),
                                     format_func=lambda x: f'{x} — {NAMES[x]}')
    extra = st.sidebar.text_input('Add a FRED series ID', placeholder='PAYEMS')
    start = st.sidebar.date_input('Chart start date', date(2020, 1, 1), min_value=date(1776, 1, 1), max_value=today)
    known = st.sidebar.date_input('As known on', today, min_value=date(1776, 1, 1), max_value=today)
    if extra.strip():
        try:
            series = validate_id(extra)
            if series not in selected:
                selected.append(series)
        except ValueError as exc:
            st.error(str(exc))
    st.info('Portfolio focus: DGS10 for VTI / QQQ / VOO / SCHD. Dates label periods measured, not publication timestamps. An ALFRED vintage represents information available on that calendar date; use an earlier vintage for a trade before that day’s release.')
    rows = []
    for series in selected:
        st.subheader(f'{series} — {NAMES.get(series, "Additional FRED series")}')
        st.markdown(f'[FRED source and units](https://fred.stlouisfed.org/series/{series}) · [ALFRED vintages](https://alfred.stlouisfed.org/series?seid={series})')
        try:
            current = download_current(series, today)
            past = download_as_known(series, known, today)
            result = compare(current['values'], past['values'])
            chart = {d: v for d, v in current['values'].items() if d >= start}
            unit = 'Percent per annum' if series in NAMES else ('Thousands of persons, seasonally adjusted' if series == 'PAYEMS' else 'Source units — see FRED link')
            st.caption(unit)
            if chart:
                frame = pd.DataFrame({'Date': pd.to_datetime(list(chart)), series: list(chart.values())}).set_index('Date')
                st.line_chart(frame)
            else:
                st.warning('No current observations in the chart window.')
            st.caption(f'Last measured date available as known on {known}: {result["known_date"] or "No observations"}.')
            rows.append({'Series': f'https://fred.stlouisfed.org/series/{series}',
                         'Units': unit, 'Known: measured date': result['known_date'],
                         'Known: value': result['known_value'], 'Today: measured date': result['current_date'],
                         'Today: value': result['current_value'], 'Later values': result['later_count'],
                         'Revised values': result['revised_count']})
            with st.expander(f'{series}: download and revision evidence'):
                st.write(f'Current fetched UTC: {current["downloaded_utc"]}; vintage fetched UTC: {past["downloaded_utc"]}')
                st.markdown(f'[Current CSV]({current["url"]}) · [Vintage CSV]({past["url"]})')
                changed = result['revised_dates']
                st.dataframe(pd.DataFrame([{'Measured date': d, 'As known': past['values'][d], 'Today': current['values'][d]} for d in changed]), hide_index=True)
        except Exception as exc:
            st.error(f'{series}: could not load or validate data. {exc}')
    st.subheader('As-known comparison')
    st.caption('Full-history counts, independent of chart start. Later = nonmissing current dates after the last known date; revised = changed values on dates present in both files. Missing values are excluded. An empty vintage has no last date, so its later count is undefined.')
    if rows:
        st.dataframe(pd.DataFrame(rows), hide_index=True, column_config={
            'Series': st.column_config.LinkColumn('Series', display_text=r'https://fred\.stlouisfed\.org/series/(.*)')})
    elif not selected:
        st.info('Select a series to begin.')

if __name__ == '__main__':
    main()

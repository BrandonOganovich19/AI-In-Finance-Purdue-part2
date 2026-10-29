"""Public FRED/ALFRED transport and auditable point-in-time comparisons."""
import csv
import io
import math
import re
from datetime import date, datetime, timezone
from urllib.parse import urlencode
from urllib.request import urlopen

NAMES = {'BAA': "Moody's Baa corporate bond yield", 'FEDFUNDS': 'Federal funds rate',
         'DGS10': '10-year Treasury yield', 'MORTGAGE30US': '30-year mortgage rate'}

def validate_id(series):
    series = series.strip().upper()
    if not re.fullmatch(r'[A-Z0-9_]{1,80}', series):
        raise ValueError('Enter a FRED series ID using letters, numbers, or underscores.')
    return series

def parse_csv(text, series, vintage=None):
    """ALFRED appends the vintage date to the value-column name."""
    reader = csv.DictReader(io.StringIO(text.lstrip('\ufeff')))
    fields = reader.fieldnames or []
    if len(fields) != 2 or fields[0].lower() not in ('date', 'observation_date'):
        raise ValueError('The source did not return a two-column observation CSV.')
    if fields[1] != series and not fields[1].startswith(series + '_'):
        raise ValueError('The response does not identify the requested series.')
    observations = {}
    for row in reader:
        day = date.fromisoformat(row[fields[0]])
        raw = row[fields[1]].strip()
        if raw in ('', '.'):
            continue  # Missing days are not zero or forward-filled observations.
        value = float(raw)
        if not math.isfinite(value):
            raise ValueError('Non-finite observation in source.')
        if day in observations:
            raise ValueError('Duplicate observation date in source.')
        if vintage is not None and day > vintage:
            raise ValueError('Vintage response contains a future observation date.')
        observations[day] = value
    return dict(sorted(observations.items()))

def fetch(series, vintage=None):
    series = validate_id(series)
    params = {'id': series}
    endpoint = 'https://fred.stlouisfed.org/graph/fredgraph.csv'
    if vintage is not None:
        params['vintage_date'] = vintage.isoformat()
        endpoint = 'https://alfred.stlouisfed.org/graph/alfredgraph.csv'
    url = endpoint + '?' + urlencode(params)
    with urlopen(url, timeout=45) as response:
        raw = response.read().decode('utf-8-sig')
    return {'series': series, 'url': url, 'downloaded_utc': datetime.now(timezone.utc).isoformat(),
            'raw_csv': raw, 'values': parse_csv(raw, series, vintage)}

def compare(current, vintage):
    """Counts use full histories; chart start date cannot change audit results."""
    old_last = max(vintage, default=None)
    new_last = max(current, default=None)
    shared = current.keys() & vintage.keys()
    revised = sorted(d for d in shared if not math.isclose(current[d], vintage[d], rel_tol=0, abs_tol=1e-9))
    return {'known_date': old_last, 'known_value': vintage.get(old_last),
            'current_date': new_last, 'current_value': current.get(new_last),
            'later_count': sum(d > old_last for d in current) if old_last else None,
            'revised_count': len(revised), 'revised_dates': revised}

"""Publish individually named Lab 19 files into the existing course folder; no ZIP."""
from pathlib import Path
import json
import shutil
import sys

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / 'Lab19_BrandonOganovich'

def write(name, text):
    (ROOT / name).write_text(text, encoding='utf-8')

def read(name):
    return (SOURCE / name).read_text(encoding='utf-8')

write('lab19_edgar.py', read('lab18_edgar.py'))
code = read('panel.py').replace('import lab18_edgar as base', 'import lab19_edgar as base')
code = code.replace("'.agents/skills/graham-business/rules.json'", "'lab19_graham_rules.json'")
code = code.replace("f'{ticker}_", "f'lab19_{ticker}_")
code = code.replace("'company_tickers.json'", "'lab19_company_tickers.json'")
# Live fetch writes the standard raw names; move only newly fetched files to this lab's names.
code = code.replace("result = analyze(company, args.ticker, source, args.threshold)",
    """for name in [f'{base.ticker_symbol(args.ticker)}_companyfacts.json', f'{base.ticker_symbol(args.ticker)}_companyfacts.source.json', 'company_tickers.json', 'company_tickers.source.json']:
                (args.directory / name).replace(args.directory / ('lab19_' + name))
            result = analyze(company, args.ticker, source, args.threshold)""")
# Avoid writing standard names into the shared root during live downloads.
code = code.replace("os.getenv('SEC_USER_AGENT', ''), args.directory)", "os.getenv('SEC_USER_AGENT', ''), args.directory / 'lab19_live_cache')")
code = code.replace("(args.directory / name).replace", "(args.directory / 'lab19_live_cache' / name).replace")
write('lab19_panel.py', code)
write('lab19_app.py', read('app.py').replace('import panel\n', 'import lab19_panel as panel\n').replace("ROOT / 'live_cache'", "ROOT / 'lab19_live_cache'"))
write('run_lab19.py', read('run_app.py').replace("ROOT.parent / 'tmp'", "ROOT / 'tmp'").replace("ROOT / 'app.py'", "ROOT / 'lab19_app.py'"))
write('requirements-lab19.txt',read('requirements.txt'))
for source, dest in [('test_panel.py','test_lab19.py'),('test_app.py','test_lab19_app.py')]:
    text = read(source).replace('import panel\n','import lab19_panel as panel\n').replace('import run_app\n','import run_lab19\n')
    text = text.replace("'.agents/skills/graham-business/rules.json'", "'lab19_graham_rules.json'")
    text = text.replace("ROOT/'app.py'", "ROOT/'lab19_app.py'")
    for name in ['calculation_tests.txt','app_tests.txt','COST_companyfacts.json','COST_companyfacts.source.json','company_tickers.json']:
        text = text.replace("'" + name + "'", "'lab19_" + name + "'")
    write(dest,text)

for path in SOURCE.glob('*_memo.md'):
    shutil.copyfile(path,ROOT / ('lab19_' + path.name))
for path in SOURCE.glob('*companyfacts*.json'):
    shutil.copyfile(path,ROOT / ('lab19_' + path.name))
for name in ['company_tickers.json','company_tickers.source.json']:
    shutil.copyfile(SOURCE/name,ROOT/('lab19_'+name))
shutil.copyfile(SOURCE/'.agents/skills/graham-business/rules.json',ROOT/'lab19_graham_rules.json')
for investor in ['buffett','graham','burry']:
    text = read(f'.agents/skills/{investor}-business/SKILL.md')
    text = text.replace('Lab19_BrandonOganovich','the course project folder').replace('python panel.py','python lab19_panel.py')
    text = text.replace('TICKER_panel.md','lab19_TICKER_panel.md').replace(f'TICKER_{investor}_memo.md', f'lab19_TICKER_{investor}_memo.md')
    text = text.replace('../../../panel.py','lab19_panel.py').replace('lab18_edgar.py','lab19_edgar.py')
    text = text.replace('[rules.json](rules.json)', '[lab19_graham_rules.json](lab19_graham_rules.json)')
    write(f'lab19_{investor}_SKILL.md',text)
write('lab19_SUBMISSION.md',read('LAB19_SUBMISSION.md').replace('panel.py','lab19_panel.py'))
write('lab19_WALKTHROUGH.md',read('WALKTHROUGH.md'))
sys.path.insert(0,str(ROOT))
import lab19_panel as panel
audit = {}
for ticker in ['COST','NVDA','JPM']:
    result = panel.load_saved(ticker)
    printed = panel.save(result)
    memos = panel.read_memos(ticker)
    flags = panel.audit_memos(memos,printed)
    if flags or not all(memos.values()):
        raise ValueError(f'Memo audit failed for {ticker}: {flags}')
    audit[ticker] = {'all_three_memos_present': True, 'unprinted_numbers': flags,
                     'checks': result['panel']}
write('lab19_memo_audit.json',json.dumps(audit,indent=2))
baseline = panel.load_saved('COST')
probe = panel.load_saved('COST',threshold='1.00')
write('lab19_threshold_probe.md', '# COST threshold probe — executed comparison\n\n'
      + '| Rule | Graham result |\n|---|---|\n'
      + f"| Retained 2.00 | {panel.summary(baseline['panel']['Graham'])} |\n"
      + f"| Probe 1.00 | {panel.summary(probe['panel']['Graham'])} |\n\n"
      + 'Only the threshold differs. The unchanged latest current ratio is '
      + panel.fmt_ratio(baseline['rows'][-1]['current_ratio'])
      + '. Retain 2.00 to preserve the defensive liquidity standard rather than tune the screen to Costco.\n'
      + 'The automated calculation test also edits the skill configuration, verifies the pass, and restores it.\n')
print('Saved individual lab19 files in',ROOT)

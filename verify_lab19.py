"""Run the final flat-file tests and record reproducibility evidence."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
ROOT = Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
import lab19_panel as panel

def main():
    lines = ['Lab 19 final verification', '']
    failed = False
    for script in ['test_lab19.py','test_lab19_app.py']:
        run = subprocess.run([sys.executable,str(ROOT/script)],cwd=ROOT,capture_output=True,text=True)
        lines.extend([f'{script}: exit {run.returncode}',run.stdout])
        if run.returncode:
            lines.append(run.stderr)
            failed = True
    for ticker in ['COST','NVDA','JPM']:
        result = panel.load_saved(ticker)
        printed = panel.save(result)
        memos = panel.read_memos(ticker)
        flags = panel.audit_memos(memos,printed)
        missing = [name for name, memo in memos.items() if not memo.strip()]
        lines.append(f'{ticker}: unprinted numbers={flags}; missing memos={missing}')
        failed = failed or bool(flags or missing)
    lines.append('Graham retained threshold: ' + panel.skill_threshold())
    lines.append('PASS' if not failed else 'FAIL')
    (ROOT/'lab19_verification.txt').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print('\n'.join(lines))
    files = sorted(set(ROOT.glob('lab19_*')) | {ROOT/n for n in ['run_lab19.py','requirements-lab19.txt','test_lab19.py','test_lab19_app.py','verify_lab19.py']})
    manifest = [{'file':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
                for p in files if p.is_file() and p.name != 'lab19_manifest.json' and p.suffix != '.log']
    (ROOT/'lab19_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    return int(failed)

if __name__ == '__main__':
    raise SystemExit(main())

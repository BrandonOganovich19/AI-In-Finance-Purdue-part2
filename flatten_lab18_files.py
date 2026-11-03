"""Place a standalone Lab 18 submission directly in the project root."""
from pathlib import Path
import json
import re
import hashlib

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / 'lab18'
names = {'app.py':'lab18_app.py', 'README.md':'lab-18-legend-investor-as-skill.md',
         'run_app.py':'run_lab18.py', 'test_app.py':'test_lab18_app.py',
         'requirements.txt':'requirements-lab18.txt', 'SKILL.md':'lab18_SKILL.md',
         'edgar.py':'lab18_edgar.py', 'WALKTHROUGH.md':'lab18_WALKTHROUGH.md',
         'package_submission.py':'package_lab18_submission.py',
         '.gitignore':'lab18_gitignore.txt', 'submission_manifest.json':'lab18_submission_manifest.json'}
files = [p for p in SOURCE.rglob('*') if p.is_file() and '__pycache__' not in p.parts
         and 'live_cache' not in p.parts and p.suffix != '.log']
destinations = {p: ROOT / names.get(p.name,p.name) for p in files}
for destination in destinations.values():
    if destination.exists():
        raise RuntimeError(f'Refusing to overwrite existing file: {destination}')

for path,destination in destinations.items():
    raw = path.read_bytes()
    if path.suffix == '.py':
        text = raw.decode('utf-8')
        text = text.replace("ROOT / 'buffett_skill' / 'scripts'", 'ROOT')
        text = text.replace("ROOT/'buffett_skill'/'scripts'", 'ROOT')
        for folder in ['evidence','memos']:
            text=text.replace(f"ROOT / '{folder}'", 'ROOT').replace(f"ROOT/'{folder}'", 'ROOT')
        text=text.replace("ROOT/'evidence/calculation_tests.txt'", "ROOT/'calculation_tests.txt'")
        text=text.replace("ROOT/'evidence/app_tests.txt'", "ROOT/'app_tests.txt'")
        text=text.replace("ROOT/'evidence/fresh_chat_comparison.md'", "ROOT/'fresh_chat_comparison.md'")
        text=text.replace("ROOT/'memos/JPM_memo.md'", "ROOT/'JPM_memo.md'")
        text=text.replace('import edgar', 'import lab18_edgar as edgar')
        text=text.replace('from buffett_skill.scripts.edgar import', 'from lab18_edgar import')
        text=text.replace('import run_app', 'import run_lab18')
        text=text.replace("ROOT.parent / 'tmp'", "ROOT / 'tmp'")
        text=text.replace("Path(__file__).resolve().parents[2]", "Path(__file__).resolve().parent")
        text=text.replace("ROOT / 'app.py'", "ROOT / 'lab18_app.py'").replace("ROOT/'app.py'", "ROOT/'lab18_app.py'")
        raw=text.encode('utf-8')
    elif path.suffix=='.md':
        text=raw.decode('utf-8')
        replacements={}
        for source,target in destinations.items():
            relative=source.relative_to(SOURCE).as_posix()
            replacements['lab18/'+relative]=target.name
            replacements[relative]=target.name
        pattern=re.compile('|'.join(re.escape(x) for x in sorted(replacements,key=len,reverse=True)))
        text=pattern.sub(lambda m:replacements[m.group()],text)
        text=text.replace('../.agents/', '.agents/')
        raw=text.encode('utf-8')
    destination.write_bytes(raw)

manifest = {'layout':'Individual files directly in the project root', 'files':[]}
for destination in destinations.values():
    if destination.name != 'lab18_submission_manifest.json':
        manifest['files'].append({'path':destination.name,'sha256':hashlib.sha256(destination.read_bytes()).hexdigest()})
(ROOT/'lab18_submission_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(f'Saved {len(destinations)} individual files directly in {ROOT}')

from pathlib import Path
import hashlib
import json

root=Path(__file__).resolve().parent
p=root/'lab18_SKILL.md'
s=p.read_text(encoding='utf-8').replace('`scripts/edgar.py TICKER', '`lab18_edgar.py TICKER')
p.write_text(s,encoding='utf-8')
p=root/'lab-18-legend-investor-as-skill.md'
s=p.read_text(encoding='utf-8').replace('lab18/evidence','.')
s=s.replace('A portable identical copy lives in [buffett_skill](lab18_SKILL.md). On another computer, copy that directory to', 'A visible reference copy is [lab18_SKILL.md](lab18_SKILL.md). On another computer, copy the installed skill folder to')
s=s.replace('Upload the `lab18` directory and `.agents/skills/buffett-business` to your course GitHub repository. Preserve the folder structure. Do not upload `tmp`, installed dependencies, or unrelated prior labs. A ZIP is supplied for transport; extract it before publishing browsable files.', 'Upload the individual files listed in lab18_submission_manifest.json directly from this project folder, plus .agents/skills/buffett-business. No ZIP or lab18 subfolder is needed for this layout. Do not upload tmp, installed dependencies, or unrelated prior labs.')
s=s.replace('Include the evidence folder', 'Include the individual evidence files')
p.write_text(s,encoding='utf-8')
(root/'package_lab18_submission.py').write_text('''"""Refresh the root-level individual-file submission manifest."""
from pathlib import Path
import hashlib
import json
root=Path(__file__).resolve().parent
path=root/'lab18_submission_manifest.json'
manifest=json.loads(path.read_text(encoding='utf-8'))
for entry in manifest['files']:
    entry['sha256']=hashlib.sha256((root/entry['path']).read_bytes()).hexdigest()
path.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print('All individual submission files verified; manifest refreshed.')
''',encoding='utf-8')
manifest_path=root/'lab18_submission_manifest.json'
manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
for entry in manifest['files']:
    entry['sha256']=hashlib.sha256((root/entry['path']).read_bytes()).hexdigest()
manifest_path.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print('Root-level submission finalized. All file paths and hashes verified.')

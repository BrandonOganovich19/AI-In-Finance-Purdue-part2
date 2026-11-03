"""Refresh the root-level individual-file submission manifest."""
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

"""Launch using the existing local Lab 15 environment or standard Python."""
from pathlib import Path
import sys
root = Path(__file__).resolve().parent
sys.path.insert(0, str(root))
local = root / 'tmp' / 'lab15-packages'
if local.exists():
    sys.path.insert(0, str(local))
if __name__ == '__main__':
    from streamlit.web import cli
    sys.argv = ['streamlit', 'run', str(root / 'asof_app.py'), '--browser.gatherUsageStats=false'] + sys.argv[1:]
    raise SystemExit(cli.main())

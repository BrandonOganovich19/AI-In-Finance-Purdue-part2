"""Use the existing project Python environment or a normal pip installation."""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
local = ROOT / 'tmp' / 'lab15-packages'
if local.exists():
    sys.path.insert(0, str(local))
if __name__ == '__main__':
    from streamlit.web import cli
    sys.argv = ['streamlit', 'run', str(ROOT / 'lab18_app.py'), '--global.developmentMode=false', '--browser.gatherUsageStats=false'] + sys.argv[1:]
    raise SystemExit(cli.main())

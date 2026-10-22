"""Launch with the bundled runtime or a standard Python installation."""
from pathlib import Path
import sys
import os

root = Path(__file__).resolve().parent
os.chdir(root)
sys.path.insert(0, str(root))
local_packages = root / 'tmp' / 'lab15-packages'
if local_packages.exists():
    sys.path.insert(0, str(local_packages))

if __name__ == '__main__':
    from streamlit.web import cli
    sys.argv = ['streamlit', 'run', str(root / 'app.py'), '--browser.gatherUsageStats=false']
    raise SystemExit(cli.main())

# This project was made with Codex. I am not a financial advisor.
# For educational purposes only; this is not investment advice.

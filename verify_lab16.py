"""Rebuild the Lab 16 verification record: python verify_lab16.py -> lab16_verification.txt"""
import contextlib
import io
import platform
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import asof  # noqa: E402


def main():
    root = Path(__file__).resolve().parent
    out = io.StringIO()
    out.write("Lab 16 reproducible verification\n")
    out.write("Run UTC: " + datetime.now(timezone.utc).isoformat() + "\n")
    out.write("Python: " + platform.python_version() + "\n\n")

    for label, decision in (("python asof.py", asof.DECISION_DATE),
                            ("swap and break: DECISION_DATE = 2026-04-15", "2026-04-15")):
        out.write(f"$ {label}\n")
        with contextlib.redirect_stdout(out):
            asof.run(decision)
        out.write("\n")

    out.write("$ python -m unittest test_asof -v\n")
    suite = unittest.defaultTestLoader.loadTestsFromName("test_asof")
    result = unittest.TextTestRunner(stream=out, verbosity=2).run(suite)

    (root / "lab16_verification.txt").write_text(out.getvalue(), encoding="utf-8")
    print(out.getvalue())
    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()

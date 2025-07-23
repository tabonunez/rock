"""Pytest configuration – ensure project root is on sys.path so that `import trading` works
when tests are run from the `tests` directory (e.g. `pytest` inside tests/).
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
print('[conftest] Adding project root to sys.path:', ROOT)
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Sanity check for import path during test collection
try:
    import trading  # noqa: F401
except ModuleNotFoundError as e:
    print("[conftest] Failed to import 'trading' after adjusting sys.path:", e)


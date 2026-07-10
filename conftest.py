"""
pytest configuration.

Makes the project root and the scripts/ folder importable during tests, so the
test files can simply `import validate_dataset` or `from isd.constant... import`.
"""

import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))

for path in (ROOT, os.path.join(ROOT, "scripts")):
    if path not in sys.path:
        sys.path.insert(0, path)

"""
Pytest configuration and fixtures.
"""

import sys
from pathlib import Path

# Add src to path to ensure we're testing the local source
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


#!/usr/bin/env python3
"""CRAC ! - Eduardo Skate Rush (version bureau).

    python3 main.py             fenetre redimensionnable
    python3 main.py --fullscreen
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from crac.game import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())

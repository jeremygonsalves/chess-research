#!/usr/bin/env python3
"""Run the interactive chess game - wrapper to ensure correct path."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    from app.game.interactive_game import main
    main()


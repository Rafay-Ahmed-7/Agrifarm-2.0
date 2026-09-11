"""AgriFarm executable launcher."""
import sys
import os
from pathlib import Path

base_dir = Path(__file__).resolve().parent
internal_dir = base_dir / "_internal"
if internal_dir.exists() and str(internal_dir) not in sys.path:
    sys.path.insert(0, str(internal_dir))

if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    meipass_internal = Path(sys._MEIPASS) / "_internal"
    if meipass_internal.exists() and str(meipass_internal) not in sys.path:
        sys.path.insert(0, str(meipass_internal))
    if str(sys._MEIPASS) not in sys.path:
        sys.path.insert(0, str(sys._MEIPASS))

import main

if __name__ == "__main__":
    main.main()

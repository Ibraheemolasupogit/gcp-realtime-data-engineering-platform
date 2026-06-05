"""Generate local synthetic retail and customer event samples."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def main() -> None:
    """Run synthetic event generation from the package implementation."""
    from realtime_data_platform.data_generation.events import main as generate_events_main

    generate_events_main()


if __name__ == "__main__":
    main()

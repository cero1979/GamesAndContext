"""Run only the new synthetic Quality & Quantity revision diagnostics."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from context_games.qq_audit import main


if __name__ == "__main__":
    main()

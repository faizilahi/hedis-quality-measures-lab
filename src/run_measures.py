"""CLI entry: compute measures and write CSV summaries."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from measure_calculator import run_all  # noqa: E402
from paths import DATA_DIR, OUTPUT_DIR  # noqa: E402


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    results = run_all(DATA_DIR)
    for key in (
        "control_totals",
        "hba1c_summary",
        "bc_summary",
        "hba1c_by_age",
        "hba1c_by_facility",
    ):
        path = OUTPUT_DIR / f"{key}.csv"
        results[key].to_csv(path, index=False)
        print(f"Wrote {path}")
    print("\nHbA1c summary:")
    print(results["hba1c_summary"].to_string(index=False))
    print("\nBreast cancer screening summary:")
    print(results["bc_summary"].to_string(index=False))


if __name__ == "__main__":
    main()

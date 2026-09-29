"""Generate matplotlib charts for README / docs."""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from measure_calculator import run_all  # noqa: E402

DATA_DIR = ROOT / "data"
IMG_DIR = ROOT / "docs" / "images"


def main() -> None:
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    results = run_all(DATA_DIR)
    by_age = results["hba1c_by_age"]
    by_fac = results["hba1c_by_facility"]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(by_age["age_band"], by_age["rate"], color="#2E86AB")
    ax.set_title("Educational Proxy: HbA1c Screening Rate by Age Band (2024)")
    ax.set_ylabel("Rate")
    ax.set_xlabel("Age Band")
    ax.set_ylim(0, 1)
    fig.tight_layout()
    p1 = IMG_DIR / "hba1c_rate_by_age_band.png"
    fig.savefig(p1, dpi=120)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(by_fac["primary_facility"], by_fac["rate"], color="#A23B72")
    ax.set_title("Educational Proxy: HbA1c Screening Rate by Facility (2024)")
    ax.set_xlabel("Rate")
    fig.tight_layout()
    p2 = IMG_DIR / "hba1c_rate_by_facility.png"
    fig.savefig(p2, dpi=120)
    plt.close(fig)

    summary = pd.concat([results["hba1c_summary"], results["bc_summary"]], ignore_index=True)
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(summary["measure"], summary["rate"], color=["#F18F01", "#C73E1D"])
    ax.set_ylim(0, 1)
    ax.set_ylabel("Rate")
    ax.set_title("Overall Measure Rates (Synthetic Cohort)")
    plt.xticks(rotation=15, ha="right")
    fig.tight_layout()
    p3 = IMG_DIR / "overall_measure_rates.png"
    fig.savefig(p3, dpi=120)
    plt.close(fig)
    print(f"Saved charts to {IMG_DIR}")


if __name__ == "__main__":
    main()

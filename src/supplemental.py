"""Supplemental electronic clinical data load helpers."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from .config import DATA


def load_supplemental_lab(path: Path | None = None) -> pd.DataFrame:
    p = path or (DATA / "supplemental_lab.csv")
    df = pd.read_csv(p)
    required = {"lab_id", "member_id", "loinc", "result_date", "systolic", "diastolic"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"supplemental lab missing columns: {sorted(missing)}")
    return df


def supplemental_only_members(
    with_supp: set[str],
    without_supp: set[str],
) -> set[str]:
    return with_supp - without_supp

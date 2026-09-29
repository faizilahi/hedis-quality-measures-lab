"""Measurement-year constants and code sets for the CDC proxy."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUTPUT = ROOT / "output"

MEASUREMENT_YEAR = 2024
MY_START = date(2024, 1, 1)
MY_END = date(2024, 12, 31)
MAX_GAP_DAYS = 45
MIN_AGE = 18
MAX_AGE = 85

# Proxy code sets — educational stand-ins, not official NCQA value sets.
CLAIM_BP_CONTROL_CPTS = frozenset({"3074F", "3075F", "3078F", "3079F"})
LAB_BP_LOINC = frozenset({"85354-9", "8480-6", "8462-4"})
HTN_ICD10 = frozenset({"I10", "I11.9", "I12.9", "I13.10"})


@dataclass(frozen=True)
class RateCut:
    label: str
    denominator: int
    numerator: int

    @property
    def rate(self) -> float:
        if self.denominator == 0:
            return 0.0
        return self.numerator / self.denominator

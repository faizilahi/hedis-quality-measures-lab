"""Rate calculation and member-level lineage export."""
from __future__ import annotations

from dataclasses import asdict

import pandas as pd

from .config import RateCut
from .numerator import NumeratorHit


def compute_cut(
    label: str,
    denom: pd.DataFrame,
    hits: dict[str, NumeratorHit],
) -> RateCut:
    d = len(denom)
    n = sum(1 for mid in denom["member_id"] if mid in hits)
    return RateCut(label=label, denominator=d, numerator=n)


def member_level(
    denom: pd.DataFrame,
    hits: dict[str, NumeratorHit],
) -> pd.DataFrame:
    rows = []
    for _, r in denom.iterrows():
        mid = r["member_id"]
        hit = hits.get(mid)
        rows.append(
            {
                "member_id": mid,
                "age": r["age"],
                "gap_days": r["gap_days"],
                "in_numerator": hit is not None,
                "numerator_source": hit.source if hit else "",
                "source_row_id": hit.source_row_id if hit else "",
                "source_detail": hit.detail if hit else "",
            }
        )
    return pd.DataFrame(rows)


def cut_to_row(cut: RateCut) -> dict:
    d = asdict(cut)
    d["rate"] = round(cut.rate, 6)
    d["rate_pct"] = round(cut.rate * 100, 2)
    return d

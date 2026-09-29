"""Multi-source numerator: claims, lab supplemental, pharmacy (N/A for CDC)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import pandas as pd

from .config import CLAIM_BP_CONTROL_CPTS, LAB_BP_LOINC, MY_END, MY_START


@dataclass
class NumeratorHit:
    member_id: str
    source: str  # claims | lab | pharmacy
    source_row_id: str
    detail: str


def claims_hits(claims: pd.DataFrame, member_ids: set[str]) -> dict[str, NumeratorHit]:
    hits: dict[str, NumeratorHit] = {}
    window = claims[
        (claims["member_id"].isin(member_ids))
        & (claims["service_date"] >= str(MY_START))
        & (claims["service_date"] <= str(MY_END))
        & (claims["procedure_code"].isin(CLAIM_BP_CONTROL_CPTS))
    ]
    for _, r in window.iterrows():
        mid = r["member_id"]
        if mid in hits:
            continue
        hits[mid] = NumeratorHit(
            member_id=mid,
            source="claims",
            source_row_id=str(r["claim_id"]),
            detail=f"CPT {r['procedure_code']} on {r['service_date']}",
        )
    return hits


def lab_hits(labs: pd.DataFrame, member_ids: set[str]) -> dict[str, NumeratorHit]:
    hits: dict[str, NumeratorHit] = {}
    window = labs[
        (labs["member_id"].isin(member_ids))
        & (labs["result_date"] >= str(MY_START))
        & (labs["result_date"] <= str(MY_END))
        & (labs["loinc"].isin(LAB_BP_LOINC))
    ]
    for _, r in window.iterrows():
        mid = r["member_id"]
        if mid in hits:
            continue
        sys_v = float(r["systolic"])
        dia_v = float(r["diastolic"])
        if sys_v < 140 and dia_v < 90:
            hits[mid] = NumeratorHit(
                member_id=mid,
                source="lab",
                source_row_id=str(r["lab_id"]),
                detail=f"LOINC {r['loinc']} SYS {sys_v:.0f}/DIA {dia_v:.0f} on {r['result_date']}",
            )
    return hits


def pharmacy_hits(_rx: pd.DataFrame, _member_ids: set[str]) -> dict[str, NumeratorHit]:
    """CDC BP control does not use pharmacy fills as numerator evidence."""
    return {}


def resolve_numerators(
    denom_ids: set[str],
    claims: pd.DataFrame,
    labs: pd.DataFrame,
    rx: pd.DataFrame,
    include_supplemental_lab: bool = True,
) -> dict[str, NumeratorHit]:
    """Precedence: claims > lab > pharmacy. Lab gated by supplemental flag."""
    resolved: dict[str, NumeratorHit] = {}
    for mid, hit in claims_hits(claims, denom_ids).items():
        resolved[mid] = hit
    if include_supplemental_lab:
        for mid, hit in lab_hits(labs, denom_ids).items():
            if mid not in resolved:
                resolved[mid] = hit
    for mid, hit in pharmacy_hits(rx, denom_ids).items():
        if mid not in resolved:
            resolved[mid] = hit
    return resolved


def trace_member(
    member_id: str,
    hits: dict[str, NumeratorHit],
) -> Optional[NumeratorHit]:
    return hits.get(member_id)

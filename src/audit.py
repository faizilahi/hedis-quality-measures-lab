"""Rate-to-source-row audit helpers."""
from __future__ import annotations

import pandas as pd

from .enrollment import explain_exclusion
from .numerator import NumeratorHit


def rate_to_source_bundle(
    member_id: str,
    denom: pd.DataFrame,
    hits: dict[str, NumeratorHit],
    members: pd.DataFrame,
    enrollment: pd.DataFrame,
    claims: pd.DataFrame,
) -> dict:
    in_denom = member_id in set(denom["member_id"])
    hit = hits.get(member_id)
    return {
        "member_id": member_id,
        "in_denominator": in_denom,
        "exclusion_or_qual_note": explain_exclusion(
            member_id, members, enrollment, claims
        ),
        "in_numerator": hit is not None,
        "source": hit.source if hit else None,
        "source_row_id": hit.source_row_id if hit else None,
        "detail": hit.detail if hit else None,
    }

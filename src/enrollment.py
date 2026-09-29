"""Continuous enrollment and denominator construction."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Iterable

import pandas as pd

from .config import (
    HTN_ICD10,
    MAX_AGE,
    MAX_GAP_DAYS,
    MIN_AGE,
    MY_END,
    MY_START,
)


def _parse(d: str | date) -> date:
    if isinstance(d, date) and not isinstance(d, datetime):
        return d
    return datetime.strptime(str(d)[:10], "%Y-%m-%d").date()


@dataclass
class EnrollmentSpan:
    member_id: str
    start: date
    end: date


def gap_days_in_measurement_year(spans: Iterable[EnrollmentSpan]) -> int:
    """Total days in [MY_START, MY_END] not covered by any enrollment span."""
    covered: set[date] = set()
    for span in spans:
        s = max(span.start, MY_START)
        e = min(span.end, MY_END)
        if s > e:
            continue
        cur = s
        while cur <= e:
            covered.add(cur)
            cur += timedelta(days=1)
    total = (MY_END - MY_START).days + 1
    return total - len(covered)


def age_as_of(dob: date, as_of: date = MY_END) -> int:
    years = as_of.year - dob.year
    if (as_of.month, as_of.day) < (dob.month, dob.day):
        years -= 1
    return years


def has_hypertension_evidence(claims: pd.DataFrame, member_id: str) -> bool:
    """HTN diagnosis in prior year (2023) on any claim."""
    prior = claims[
        (claims["member_id"] == member_id)
        & (claims["service_date"] >= "2023-01-01")
        & (claims["service_date"] <= "2023-12-31")
        & (claims["diagnosis_code"].isin(HTN_ICD10))
    ]
    return not prior.empty


def build_denominator(
    members: pd.DataFrame,
    enrollment: pd.DataFrame,
    claims: pd.DataFrame,
) -> pd.DataFrame:
    """Return member-level denom rows with gap_days and age."""
    rows = []
    for _, m in members.iterrows():
        mid = m["member_id"]
        dob = _parse(m["dob"])
        age = age_as_of(dob)
        if age < MIN_AGE or age > MAX_AGE:
            continue
        spans = [
            EnrollmentSpan(mid, _parse(r["enroll_start"]), _parse(r["enroll_end"]))
            for _, r in enrollment[enrollment["member_id"] == mid].iterrows()
        ]
        gaps = gap_days_in_measurement_year(spans)
        if gaps > MAX_GAP_DAYS:
            continue
        if not has_hypertension_evidence(claims, mid):
            continue
        rows.append(
            {
                "member_id": mid,
                "age": age,
                "gap_days": gaps,
                "sex": m["sex"],
                "in_denominator": True,
            }
        )
    return pd.DataFrame(rows)


def explain_exclusion(
    member_id: str,
    members: pd.DataFrame,
    enrollment: pd.DataFrame,
    claims: pd.DataFrame,
) -> str:
    """Auditor-facing prose for why a member is out of the denom."""
    m = members[members["member_id"] == member_id]
    if m.empty:
        return f"{member_id}: unknown member"
    dob = _parse(m.iloc[0]["dob"])
    age = age_as_of(dob)
    if age < MIN_AGE or age > MAX_AGE:
        return f"{member_id}: age {age} outside {MIN_AGE}-{MAX_AGE}"
    spans = [
        EnrollmentSpan(member_id, _parse(r["enroll_start"]), _parse(r["enroll_end"]))
        for _, r in enrollment[enrollment["member_id"] == member_id].iterrows()
    ]
    gaps = gap_days_in_measurement_year(spans)
    if gaps > MAX_GAP_DAYS:
        return f"{member_id}: gap_days={gaps} exceeds max {MAX_GAP_DAYS}"
    if not has_hypertension_evidence(claims, member_id):
        return f"{member_id}: no HTN ICD-10 evidence in prior year"
    return f"{member_id}: qualifies for denominator (gap_days={gaps}, age={age})"

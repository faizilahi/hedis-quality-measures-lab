#!/usr/bin/env python3
"""Run MY2024 CDC proxy: before/after supplemental lab, optional member trace."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.audit import rate_to_source_bundle
from src.config import DATA, OUTPUT
from src.enrollment import build_denominator
from src.hybrid_gap import hybrid_status
from src.numerator import resolve_numerators
from src.rate import compute_cut, cut_to_row, member_level
from src.supplemental import load_supplemental_lab, supplemental_only_members


def load_all():
    members = pd.read_csv(DATA / "members.csv")
    enrollment = pd.read_csv(DATA / "enrollment.csv")
    claims = pd.read_csv(DATA / "claims.csv")
    rx = pd.read_csv(DATA / "pharmacy.csv")
    labs = load_supplemental_lab()
    return members, enrollment, claims, rx, labs


def main() -> None:
    parser = argparse.ArgumentParser(description="MY2024 CDC measurement-year close")
    parser.add_argument("--trace", help="member_id to audit to source rows")
    args = parser.parse_args()

    OUTPUT.mkdir(exist_ok=True)
    members, enrollment, claims, rx, labs = load_all()
    denom = build_denominator(members, enrollment, claims)
    denom_ids = set(denom["member_id"])

    hits_before = resolve_numerators(denom_ids, claims, labs, rx, include_supplemental_lab=False)
    hits_after = resolve_numerators(denom_ids, claims, labs, rx, include_supplemental_lab=True)

    before = compute_cut("before_supplemental_lab", denom, hits_before)
    after = compute_cut("after_supplemental_lab", denom, hits_after)
    lab_only = supplemental_only_members(set(hits_after), set(hits_before))

    summary = pd.DataFrame([cut_to_row(before), cut_to_row(after)])
    summary.to_csv(OUTPUT / "cdc_my2024_summary.csv", index=False)
    member_level(denom, hits_after).to_csv(OUTPUT / "member_level.csv", index=False)

    print("=== MY2024 CDC proxy (synthetic) ===")
    print(summary.to_string(index=False))
    print(f"Supplemental-lab-only numerator adds: {len(lab_only)}")
    print("Hybrid status:", json.dumps(hybrid_status(), indent=2))

    if args.trace:
        bundle = rate_to_source_bundle(
            args.trace, denom, hits_after, members, enrollment, claims
        )
        print("\n=== Rate -> source trace ===")
        print(json.dumps(bundle, indent=2))


if __name__ == "__main__":
    main()

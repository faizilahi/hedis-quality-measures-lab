#!/usr/bin/env python3
"""Generate synthetic eligibility, claims, pharmacy, and supplemental lab feeds."""
from __future__ import annotations

import random
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)

RNG = random.Random(2024)
N_MEMBERS = 1200


def _d(y: int, m: int, day: int) -> str:
    return date(y, m, day).isoformat()


def main() -> None:
    members = []
    enrollment = []
    claims = []
    rx = []
    labs = []
    claim_n = 0
    lab_n = 0
    rx_n = 0

    # Planted member for README worked example
    special = "M-000417"

    for i in range(1, N_MEMBERS + 1):
        mid = f"M-{i:06d}"
        sex = RNG.choice(["F", "M"])
        # Ages mostly in 18-85
        age = RNG.randint(18, 85)
        dob = date(2024 - age, RNG.randint(1, 12), RNG.randint(1, 28))
        members.append({"member_id": mid, "sex": sex, "dob": dob.isoformat()})

        # Most continuously enrolled; ~12% with large gaps
        if RNG.random() < 0.12 and mid != special:
            enrollment.append(
                {
                    "member_id": mid,
                    "enroll_start": _d(2024, 1, 1),
                    "enroll_end": _d(2024, 3, 15),
                }
            )
            enrollment.append(
                {
                    "member_id": mid,
                    "enroll_start": _d(2024, 7, 1),
                    "enroll_end": _d(2024, 12, 31),
                }
            )
        else:
            enrollment.append(
                {
                    "member_id": mid,
                    "enroll_start": _d(2023, 6, 1),
                    "enroll_end": _d(2024, 12, 31),
                }
            )

        # Prior-year HTN evidence for ~75%
        if mid == special or RNG.random() < 0.75:
            claim_n += 1
            claims.append(
                {
                    "claim_id": f"CLM-{claim_n:06d}",
                    "member_id": mid,
                    "service_date": _d(2023, RNG.randint(1, 12), RNG.randint(1, 28)),
                    "procedure_code": "99213",
                    "diagnosis_code": RNG.choice(["I10", "I11.9", "I12.9"]),
                    "claim_type": "professional",
                }
            )

        # MY2024 claim BP control for ~35% of members
        if mid != special and RNG.random() < 0.35:
            claim_n += 1
            claims.append(
                {
                    "claim_id": f"CLM-{claim_n:06d}",
                    "member_id": mid,
                    "service_date": _d(2024, RNG.randint(1, 12), RNG.randint(1, 28)),
                    "procedure_code": RNG.choice(["3074F", "3075F", "3078F", "3079F"]),
                    "diagnosis_code": "I10",
                    "claim_type": "professional",
                }
            )

        # Pharmacy fills (loaded but unused for CDC numerator)
        if RNG.random() < 0.4:
            rx_n += 1
            rx.append(
                {
                    "rx_id": f"RX-{rx_n:06d}",
                    "member_id": mid,
                    "fill_date": _d(2024, RNG.randint(1, 12), RNG.randint(1, 28)),
                    "ndc": "00093-7201-01",
                    "days_supply": 30,
                }
            )

        # Supplemental lab: special member + ~8% others without claim control
        plant_lab = mid == special or RNG.random() < 0.08
        if plant_lab:
            lab_n += 1
            controlled = mid == special or RNG.random() < 0.85
            labs.append(
                {
                    "lab_id": "LAB-8821" if mid == special else f"LAB-{lab_n:05d}",
                    "member_id": mid,
                    "loinc": "85354-9",
                    "result_date": "2024-06-11" if mid == special else _d(
                        2024, RNG.randint(1, 12), RNG.randint(1, 28)
                    ),
                    "systolic": 128 if controlled else RNG.randint(140, 170),
                    "diastolic": 78 if controlled else RNG.randint(90, 110),
                }
            )

        # Noise claims
        for _ in range(RNG.randint(0, 3)):
            claim_n += 1
            claims.append(
                {
                    "claim_id": f"CLM-{claim_n:06d}",
                    "member_id": mid,
                    "service_date": _d(2024, RNG.randint(1, 12), RNG.randint(1, 28)),
                    "procedure_code": RNG.choice(["99213", "99214", "80053"]),
                    "diagnosis_code": RNG.choice(["E11.9", "J06.9", "M54.5", "I10"]),
                    "claim_type": "professional",
                }
            )

    pd.DataFrame(members).to_csv(DATA / "members.csv", index=False)
    pd.DataFrame(enrollment).to_csv(DATA / "enrollment.csv", index=False)
    pd.DataFrame(claims).to_csv(DATA / "claims.csv", index=False)
    pd.DataFrame(rx).to_csv(DATA / "pharmacy.csv", index=False)
    pd.DataFrame(labs).to_csv(DATA / "supplemental_lab.csv", index=False)
    print(
        f"Wrote {len(members)} members, {len(claims)} claims, "
        f"{len(labs)} supplemental labs, {len(rx)} pharmacy fills -> {DATA}"
    )


if __name__ == "__main__":
    main()

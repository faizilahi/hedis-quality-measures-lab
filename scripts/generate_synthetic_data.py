"""Generate synthetic membership, enrollment, and claims for educational HEDIS-style labs."""

from __future__ import annotations

import random
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
random.seed(42)
np.random.seed(42)

FACILITIES = ["FAC-NORTH", "FAC-SOUTH", "FAC-EAST", "FAC-WEST", "FAC-CENTRAL"]
N_MEMBERS = 2500


def age_band(age: int) -> str:
    if age < 30:
        return "18-29"
    if age < 45:
        return "30-44"
    if age < 60:
        return "45-59"
    if age < 75:
        return "60-74"
    return "75+"


def random_dob(min_age: int, max_age: int) -> date:
    age = random.randint(min_age, max_age)
    return date(2024, 6, 15) - timedelta(days=age * 365 + random.randint(0, 364))


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    members = []
    for i in range(1, N_MEMBERS + 1):
        mid = f"M{i:05d}"
        sex = random.choice(["F", "M"])
        dob = random_dob(18, 90)
        age = 2024 - dob.year
        has_diabetes = random.random() < (0.22 if age >= 45 else 0.08)
        members.append(
            {
                "member_id": mid,
                "sex": sex,
                "dob": dob.isoformat(),
                "age_2024": age,
                "age_band": age_band(age),
                "primary_facility": random.choice(FACILITIES),
                "has_diabetes_flag": int(has_diabetes),
            }
        )
    members_df = pd.DataFrame(members)

    enrollment_rows = []
    for _, row in members_df.iterrows():
        start = date(2023, 1, 1) + timedelta(days=random.randint(0, 180))
        end = None if random.random() > 0.12 else date(2024, random.randint(1, 11), 15)
        enrollment_rows.append(
            {
                "member_id": row["member_id"],
                "plan_id": random.choice(["HMO-001", "PPO-002", "EPO-003"]),
                "enroll_start": start.isoformat(),
                "enroll_end": end.isoformat() if end else "",
            }
        )
    enrollment_df = pd.DataFrame(enrollment_rows)

    claims = []
    claim_id = 1
    for _, row in members_df.iterrows():
        n_claims = random.randint(2, 12)
        for _ in range(n_claims):
            svc = date(2024, random.randint(1, 12), random.randint(1, 28))
            proc = random.choice(
                ["99213", "99214", "80053", "83036", "4548-4", "77067", "36415", "96372"]
            )
            if row["has_diabetes_flag"] and random.random() < 0.65 and proc not in ("83036", "4548-4"):
                proc = random.choice(["83036", "4548-4"])
            if row["sex"] == "F" and 50 <= row["age_2024"] <= 74 and random.random() < 0.55:
                proc = random.choice(["77067", "99213"])
            claims.append(
                {
                    "claim_id": f"C{claim_id:06d}",
                    "member_id": row["member_id"],
                    "service_date": svc.isoformat(),
                    "procedure_code": proc,
                    "claim_type": random.choice(["professional", "institutional"]),
                    "facility_id": row["primary_facility"],
                }
            )
            claim_id += 1

    claims_df = pd.DataFrame(claims)

    diabetes_denom = members_df[members_df["has_diabetes_flag"] == 1][
        ["member_id", "age_band", "primary_facility"]
    ].copy()
    diabetes_denom["measurement_year"] = 2024

    breast_denom = members_df[
        (members_df["sex"] == "F") & (members_df["age_2024"].between(50, 74))
    ][["member_id", "age_band", "primary_facility"]].copy()
    breast_denom["measurement_year"] = 2024

    members_df.to_csv(DATA_DIR / "members.csv", index=False)
    enrollment_df.to_csv(DATA_DIR / "enrollment.csv", index=False)
    claims_df.to_csv(DATA_DIR / "claims.csv", index=False)
    diabetes_denom.to_csv(DATA_DIR / "diabetes_denominator.csv", index=False)
    breast_denom.to_csv(DATA_DIR / "breast_cancer_denominator.csv", index=False)

    print(f"Wrote {len(members_df)} members, {len(enrollment_df)} enrollment rows")
    print(f"Wrote {len(claims_df)} claims, diabetes denom {len(diabetes_denom)}, breast denom {len(breast_denom)}")


if __name__ == "__main__":
    main()

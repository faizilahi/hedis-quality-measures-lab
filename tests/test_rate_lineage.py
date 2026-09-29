import pandas as pd

from src.audit import rate_to_source_bundle
from src.enrollment import build_denominator
from src.numerator import NumeratorHit, resolve_numerators


def test_trace_includes_source_row():
    members = pd.DataFrame(
        [{"member_id": "M1", "sex": "F", "dob": "1970-01-15"}]
    )
    enrollment = pd.DataFrame(
        [{"member_id": "M1", "enroll_start": "2023-01-01", "enroll_end": "2024-12-31"}]
    )
    claims = pd.DataFrame(
        [
            {
                "claim_id": "C0",
                "member_id": "M1",
                "service_date": "2023-05-01",
                "procedure_code": "99213",
                "diagnosis_code": "I10",
                "claim_type": "professional",
            }
        ]
    )
    labs = pd.DataFrame(
        [
            {
                "lab_id": "L9",
                "member_id": "M1",
                "loinc": "85354-9",
                "result_date": "2024-08-01",
                "systolic": 118,
                "diastolic": 76,
            }
        ]
    )
    rx = pd.DataFrame(columns=["rx_id", "member_id", "fill_date", "ndc", "days_supply"])
    denom = build_denominator(members, enrollment, claims)
    hits = resolve_numerators(set(denom["member_id"]), claims, labs, rx, True)
    bundle = rate_to_source_bundle("M1", denom, hits, members, enrollment, claims)
    assert bundle["in_denominator"] is True
    assert bundle["in_numerator"] is True
    assert bundle["source_row_id"] == "L9"

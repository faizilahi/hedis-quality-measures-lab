import pandas as pd

from src.numerator import resolve_numerators


def test_claims_beat_lab_precedence():
    claims = pd.DataFrame(
        [
            {
                "claim_id": "C1",
                "member_id": "M1",
                "service_date": "2024-03-01",
                "procedure_code": "3074F",
                "diagnosis_code": "I10",
                "claim_type": "professional",
            }
        ]
    )
    labs = pd.DataFrame(
        [
            {
                "lab_id": "L1",
                "member_id": "M1",
                "loinc": "85354-9",
                "result_date": "2024-04-01",
                "systolic": 120,
                "diastolic": 70,
            }
        ]
    )
    rx = pd.DataFrame(columns=["rx_id", "member_id", "fill_date", "ndc", "days_supply"])
    hits = resolve_numerators({"M1"}, claims, labs, rx, include_supplemental_lab=True)
    assert hits["M1"].source == "claims"
    assert hits["M1"].source_row_id == "C1"


def test_lab_only_when_no_claim():
    claims = pd.DataFrame(
        columns=["claim_id", "member_id", "service_date", "procedure_code", "diagnosis_code", "claim_type"]
    )
    labs = pd.DataFrame(
        [
            {
                "lab_id": "LAB-8821",
                "member_id": "M-000417",
                "loinc": "85354-9",
                "result_date": "2024-06-11",
                "systolic": 128,
                "diastolic": 78,
            }
        ]
    )
    rx = pd.DataFrame(columns=["rx_id", "member_id", "fill_date", "ndc", "days_supply"])
    hits = resolve_numerators({"M-000417"}, claims, labs, rx, True)
    assert hits["M-000417"].source == "lab"
    assert hits["M-000417"].source_row_id == "LAB-8821"

"""Simplified educational HEDIS-style measure logic (not NCQA-certified)."""

from __future__ import annotations

import pandas as pd


MEASUREMENT_YEAR = 2024


def load_tables(data_dir) -> dict[str, pd.DataFrame]:
    return {
        "members": pd.read_csv(data_dir / "members.csv", parse_dates=["dob"]),
        "enrollment": pd.read_csv(
            data_dir / "enrollment.csv", parse_dates=["enroll_start", "enroll_end"]
        ),
        "claims": pd.read_csv(data_dir / "claims.csv", parse_dates=["service_date"]),
        "diabetes_denominator": pd.read_csv(data_dir / "diabetes_denominator.csv"),
        "breast_cancer_denominator": pd.read_csv(
            data_dir / "breast_cancer_denominator.csv"
        ),
    }


def active_enrollment(enrollment: pd.DataFrame, year: int) -> pd.DataFrame:
    start = pd.Timestamp(f"{year}-01-01")
    end = pd.Timestamp(f"{year}-12-31")
    mask = (enrollment["enroll_start"] <= end) & (
        enrollment["enroll_end"].isna() | (enrollment["enroll_end"] >= start)
    )
    return enrollment.loc[mask].copy()


def hba1c_screening_rate(
    claims: pd.DataFrame,
    denominator: pd.DataFrame,
    year: int = MEASUREMENT_YEAR,
) -> pd.DataFrame:
    """CDC HbA1c screening proxy: CPT 83036 or LOINC 4548-4 in measurement year."""
    denom = denominator[denominator["measurement_year"] == year].copy()
    screening_codes = {"83036", "4548-4", "83037"}
    year_claims = claims[
        (claims["service_date"].dt.year == year)
        & (claims["procedure_code"].astype(str).isin(screening_codes))
    ]
    screened = year_claims.groupby("member_id").size().reset_index(name="screening_count")
    merged = denom.merge(screened, on="member_id", how="left")
    merged["screened"] = merged["screening_count"].fillna(0).gt(0)
    rate = merged["screened"].mean()
    summary = pd.DataFrame(
        [
            {
                "measure": "Diabetes HbA1c Screening (Educational Proxy)",
                "measurement_year": year,
                "denominator": len(merged),
                "numerator": int(merged["screened"].sum()),
                "rate": round(rate, 4),
            }
        ]
    )
    return summary, merged


def breast_cancer_screening_proxy(
    claims: pd.DataFrame,
    denominator: pd.DataFrame,
    year: int = MEASUREMENT_YEAR,
) -> pd.DataFrame:
    """Mammography proxy: CPT 77067 in measurement year for eligible female members."""
    denom = denominator[denominator["measurement_year"] == year].copy()
    mammo_codes = {"77067", "77063", "G0202"}
    year_claims = claims[
        (claims["service_date"].dt.year == year)
        & (claims["procedure_code"].astype(str).isin(mammo_codes))
    ]
    screened = year_claims.groupby("member_id").size().reset_index(name="screening_count")
    merged = denom.merge(screened, on="member_id", how="left")
    merged["screened"] = merged["screening_count"].fillna(0).gt(0)
    rate = merged["screened"].mean()
    summary = pd.DataFrame(
        [
            {
                "measure": "Breast Cancer Screening (Educational Proxy)",
                "measurement_year": year,
                "denominator": len(merged),
                "numerator": int(merged["screened"].sum()),
                "rate": round(rate, 4),
            }
        ]
    )
    return summary, merged


def rates_by_dimension(
    member_detail: pd.DataFrame, dimension: str
) -> pd.DataFrame:
    grouped = (
        member_detail.groupby(dimension, dropna=False)
        .agg(denominator=("member_id", "count"), numerator=("screened", "sum"))
        .reset_index()
    )
    grouped["rate"] = (grouped["numerator"] / grouped["denominator"]).round(4)
    return grouped


def control_totals(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows = []
    for name, df in tables.items():
        rows.append({"table": name, "row_count": len(df)})
    return pd.DataFrame(rows)


def run_all(data_dir) -> dict:
    tables = load_tables(data_dir)
    hba1c_summary, hba1c_detail = hba1c_screening_rate(tables["claims"], tables["diabetes_denominator"])
    bc_summary, bc_detail = breast_cancer_screening_proxy(
        tables["claims"], tables["breast_cancer_denominator"]
    )
    hba1c_by_age = rates_by_dimension(hba1c_detail, "age_band")
    hba1c_by_facility = rates_by_dimension(hba1c_detail, "primary_facility")
    return {
        "control_totals": control_totals(tables),
        "hba1c_summary": hba1c_summary,
        "bc_summary": bc_summary,
        "hba1c_by_age": hba1c_by_age,
        "hba1c_by_facility": hba1c_by_facility,
        "hba1c_detail": hba1c_detail,
    }

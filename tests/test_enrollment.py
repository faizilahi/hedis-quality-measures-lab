from datetime import date

from src.config import MAX_GAP_DAYS
from src.enrollment import EnrollmentSpan, age_as_of, gap_days_in_measurement_year


def test_full_year_zero_gap():
    spans = [EnrollmentSpan("M1", date(2023, 1, 1), date(2024, 12, 31))]
    assert gap_days_in_measurement_year(spans) == 0


def test_large_gap_flags():
    spans = [
        EnrollmentSpan("M1", date(2024, 1, 1), date(2024, 2, 1)),
        EnrollmentSpan("M1", date(2024, 10, 1), date(2024, 12, 31)),
    ]
    gaps = gap_days_in_measurement_year(spans)
    assert gaps > MAX_GAP_DAYS


def test_age_boundary():
    assert age_as_of(date(2006, 12, 31), date(2024, 12, 31)) == 18
    assert age_as_of(date(2007, 1, 1), date(2024, 12, 31)) == 17

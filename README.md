# MY2024 CDC Close - Rate Movement After Supplemental Lab Feed

Faiz Elahi - https://www.linkedin.com/in/faizilahi - https://pendataco.com - https://github.com/faizilahi

Portfolio project (synthetic members only). Implements NCQA-style *measure logic in code* for a Controlling High Blood Pressure (CDC) proxy - not NCQA certification, not Inovalon/Cotiviti, not a claim of employment at any payer.

## Who this is for

Recruiters and hiring managers screening for HEDIS / quality data engineers who need to see continuous enrollment, multi-source numerators (claims, lab, pharmacy), supplemental data, rate-to-row lineage, and an honest hybrid-measure gap note - in Python you can run locally, with Snowflake-shaped SQL alongside.

## The rate that moved

Measurement year **2024**. Administrative-only CDC proxy on a 1,200-member synthetic book.

| Cut | Denominator | Numerator | Rate |
|-----|-------------|-----------|------|
| Before supplemental lab feed | 797 | 298 | **37.39%** |
| After lab LOINC rows landed | 797 | 335 | **42.03%** |

The jump is entirely from supplemental lab results that were already in the EHR extract but missing from the administrative claim path (37 lab-only numerator adds). Claims and pharmacy fills did not change between cuts.

## Continuous enrollment

Denominator members must be continuously enrolled from 2024-01-01 through 2024-12-31 with allowable gaps ≤ 45 days total. Age 18-85 as of 2024-12-31 and a hypertension evidence window in the prior year. Logic lives in `src/enrollment.py`; SQL twin in `sql/continuous_enrollment.sql`.

## Numerator from claims vs lab vs pharmacy

A member hits the numerator if **any** of these fire in MY2024:

1. **Claims** - outpatient CPT with a controlled BP reading code set (proxy).
2. **Lab** - LOINC blood-pressure panel result with systolic < 140 and diastolic < 90 on the same draw.
3. **Pharmacy** - not used as numerator evidence for this CDC proxy (documented); pharmacy feeds still load because other measures in the annual cycle share the same eligibility spine.

Source precedence for audit display: claims first, then lab, then (N/A) pharmacy. See `src/numerator.py`.

## Supplemental rows

Supplemental file `data/supplemental_lab.csv` is the EHR lab feed. It is *not* claim-derived. After load, 37 additional members clear the numerator solely via lab. Trace any one of them with:

```bash
python scripts/run_measurement_year.py --trace M-000417
```

That prints the rate contribution and the exact source row IDs.

## How to rerun the year

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
python scripts/generate_synthetic.py
python scripts/run_measurement_year.py
pytest -q
```

Outputs land in `output/cdc_my2024_summary.csv` and `output/member_level.csv`.

## What the auditor asks

- Can you show continuous-enrollment math for a denied member?
- Which source row flipped this member into the numerator?
- Was supplemental data allowed under the measure's administrative path?
- Why is hybrid medical-record review **not** implemented here?

**Hybrid gap (documented, not claimed):** this repo stops at administrative + supplemental electronic clinical data. Chart-chase / hybrid medical-record abstraction is out of scope - no NCQA HEDIS Certification, no vendor measure engine.

### Worked numeric example (member M-000417)

| Step | Value |
|------|-------|
| In continuous-enrollment denom? | Yes (0 gap days) |
| Claims numerator? | No |
| Lab supplemental before fix | Missing row |
| Rate contribution before feed fix | 0 (denom only) |
| Lab row after feed fix | `LAB-8821` LOINC 85354-9 SYS 128 / DIA 78 on 2024-06-11 |
| Numerator after | Yes |
| Book rate before -> after | 37.39% -> 42.03% (37 lab-only adds including this member) |

Rows in `data/` are synthetic and sized for git.

---

Faiz Elahi - [LinkedIn](https://www.linkedin.com/in/faizilahi) - [pendataco.com](https://pendataco.com) - [GitHub](https://github.com/faizilahi)


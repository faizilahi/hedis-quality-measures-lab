# Architecture Notes — HEDIS Quality Measures Lab

**Author:** Faiz Elahi ([faizelahi](https://github.com/faizelahi))  
**Purpose:** Educational portfolio lab only. Synthetic data. Not NCQA-certified measure logic.

## Data flow

1. `scripts/generate_synthetic_data.py` builds CSV extracts under `data/`.
2. `src/measure_calculator.py` loads tables, applies simplified numerator/denominator rules.
3. `src/run_measures.py` writes summaries to `output/`.
4. `scripts/generate_charts.py` renders PNG charts into `docs/images/`.

## Design choices

- Denominators are pre-flagged cohorts (diabetes, breast screening age/sex) to keep the lab readable.
- Claims use CPT/LOINC-like codes as **proxies** for screening events in the measurement year.
- Rates by `age_band` and `primary_facility` support stratified quality reporting practice.

See the main `README.md` for the full mermaid diagram and file walkthrough.

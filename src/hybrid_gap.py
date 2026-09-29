"""Documented hybrid-measure gap — do not claim chart abstraction."""

HYBRID_GAP_NOTE = (
    "This engine covers administrative claims plus supplemental electronic "
    "clinical lab results. Hybrid medical-record review / chart chase is not "
    "implemented. Do not present this repo as NCQA-certified HEDIS software "
    "or as an Inovalon/Cotiviti replacement."
)


def hybrid_status() -> dict[str, str]:
    return {
        "administrative": "implemented",
        "supplemental_electronic_clinical": "implemented",
        "hybrid_medical_record_review": "documented_gap_not_implemented",
        "ncqa_certification": "not_claimed",
        "note": HYBRID_GAP_NOTE,
    }

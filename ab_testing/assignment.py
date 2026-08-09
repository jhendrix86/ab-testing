"""
Deterministic, weighted variant assignment.

The same (experiment_id, subject_id) pair always resolves to the same
variant - critical for real experiments: a customer who sees "price $29"
today must see the same price on their next visit, not a new random draw.
Uses SHA-256 rather than Python's hash() because hash() is randomized
per-process (PYTHONHASHSEED) - the same subject would get different
variants across restarts otherwise.
"""

import hashlib

from .models import Experiment

_BUCKET_COUNT = 10_000


def assign_variant(experiment: Experiment, subject_id: str) -> str:
    """Return the name of the variant `subject_id` is assigned to in `experiment`."""
    digest = hashlib.sha256(f"{experiment.id}:{subject_id}".encode("utf-8")).hexdigest()
    bucket = int(digest, 16) % _BUCKET_COUNT

    total_weight = sum(v.weight for v in experiment.variants)
    cumulative_buckets = 0.0
    for variant in experiment.variants:
        cumulative_buckets += (variant.weight / total_weight) * _BUCKET_COUNT
        if bucket < cumulative_buckets:
            return variant.name

    # Floating-point rounding can leave the last few buckets unassigned;
    # they belong to the final variant.
    return experiment.variants[-1].name

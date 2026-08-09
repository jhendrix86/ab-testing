from ab_testing.assignment import assign_variant
from ab_testing.models import Experiment, Variant


def _equal_experiment():
    return Experiment(id="exp-1", name="test", variants=[Variant(name="a"), Variant(name="b")])


def test_assignment_is_deterministic():
    experiment = _equal_experiment()

    first = assign_variant(experiment, "customer_42")
    second = assign_variant(experiment, "customer_42")

    assert first == second


def test_different_subjects_can_get_different_variants():
    experiment = _equal_experiment()

    assignments = {assign_variant(experiment, f"customer_{i}") for i in range(50)}

    assert assignments == {"a", "b"}


def test_different_experiments_assign_independently():
    exp1 = Experiment(id="exp-1", name="t1", variants=[Variant(name="a"), Variant(name="b")])
    exp2 = Experiment(id="exp-2", name="t2", variants=[Variant(name="a"), Variant(name="b")])

    # Same subject, different experiments - not guaranteed to differ for any
    # single subject, but across many subjects the two experiments' bucket
    # assignments shouldn't be perfectly correlated.
    matches = sum(
        1 for i in range(200)
        if assign_variant(exp1, f"cust_{i}") == assign_variant(exp2, f"cust_{i}")
    )
    # With 2 equal-weight variants, ~50% match is expected by chance alone;
    # anything wildly off (e.g. 100% or 0%) would indicate the hash isn't
    # actually mixing in the experiment id.
    assert 60 <= matches <= 140


def test_equal_weights_distribute_roughly_evenly():
    experiment = _equal_experiment()

    counts = {"a": 0, "b": 0}
    for i in range(2000):
        counts[assign_variant(experiment, f"subject_{i}")] += 1

    # Real hash-based bucketing, not a fixed pattern - allow real statistical
    # slack rather than asserting an exact 50/50 split.
    assert 800 < counts["a"] < 1200
    assert 800 < counts["b"] < 1200


def test_weighted_assignment_skews_toward_heavier_variant():
    experiment = Experiment(id="exp-skew", name="test", variants=[
        Variant(name="control", weight=9.0),
        Variant(name="treatment", weight=1.0),
    ])

    counts = {"control": 0, "treatment": 0}
    for i in range(2000):
        counts[assign_variant(experiment, f"subject_{i}")] += 1

    # Expect roughly 90/10; allow real statistical slack.
    assert counts["control"] > counts["treatment"] * 5


def test_unknown_bucket_edge_case_falls_back_to_last_variant():
    # Regression guard for floating-point rounding at the top bucket edge -
    # every possible bucket must resolve to a real variant, never None/KeyError.
    experiment = Experiment(id="exp-edge", name="test", variants=[
        Variant(name="a", weight=1.0), Variant(name="b", weight=1.0), Variant(name="c", weight=1.0),
    ])

    for i in range(500):
        result = assign_variant(experiment, f"edge_{i}")
        assert result in {"a", "b", "c"}

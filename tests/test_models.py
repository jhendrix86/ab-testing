import pytest

from ab_testing.models import Experiment, Variant


def test_experiment_requires_at_least_two_variants():
    with pytest.raises(ValueError, match="at least 2 variants"):
        Experiment(id="e1", name="test", variants=[Variant(name="a")])


def test_experiment_rejects_non_positive_weight():
    with pytest.raises(ValueError, match="non-positive weight"):
        Experiment(id="e1", name="test", variants=[
            Variant(name="a", weight=1.0), Variant(name="b", weight=0),
        ])


def test_experiment_rejects_duplicate_variant_names():
    with pytest.raises(ValueError, match="duplicate variant names"):
        Experiment(id="e1", name="test", variants=[
            Variant(name="a"), Variant(name="a"),
        ])


def test_get_variant_returns_the_named_variant():
    experiment = Experiment(id="e1", name="test", variants=[
        Variant(name="a", payload={"subject": "A"}),
        Variant(name="b", payload={"subject": "B"}),
    ])

    assert experiment.get_variant("b").payload["subject"] == "B"


def test_get_variant_raises_for_unknown_name():
    experiment = Experiment(id="e1", name="test", variants=[Variant(name="a"), Variant(name="b")])

    with pytest.raises(KeyError):
        experiment.get_variant("c")

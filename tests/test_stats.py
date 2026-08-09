import pytest

from ab_testing.stats import two_proportion_z_test


def test_matches_independently_computed_reference_values():
    """
    100/1000 (10%) vs 150/1000 (15%) - z and p independently computed via
    the same textbook two-proportion z-test formula, outside this codebase,
    to confirm the implementation isn't just directionally plausible but
    numerically correct.
    """
    result = two_proportion_z_test(conversions_a=100, visitors_a=1000, conversions_b=150, visitors_b=1000)

    assert result.rate_a == pytest.approx(0.10)
    assert result.rate_b == pytest.approx(0.15)
    assert result.z_score == pytest.approx(3.3806170189140654, abs=1e-9)
    assert result.p_value == pytest.approx(0.0007232327164301555, abs=1e-9)
    assert result.significant_at_95 is True
    assert result.winner == "b"


def test_identical_rates_are_not_significant():
    result = two_proportion_z_test(conversions_a=50, visitors_a=500, conversions_b=50, visitors_b=500)

    assert result.z_score == pytest.approx(0.0)
    assert result.p_value == pytest.approx(1.0)
    assert result.significant_at_95 is False
    assert result.winner is None


def test_small_sample_difference_is_not_significant():
    """A tiny sample can't distinguish a real 2% difference from noise."""
    result = two_proportion_z_test(conversions_a=2, visitors_a=20, conversions_b=3, visitors_b=20)

    assert result.significant_at_95 is False
    assert result.winner is None


def test_variant_a_winning_is_reported_correctly():
    result = two_proportion_z_test(conversions_a=150, visitors_a=1000, conversions_b=100, visitors_b=1000)

    assert result.winner == "a"


def test_zero_visitors_reports_an_error_not_a_crash():
    result = two_proportion_z_test(conversions_a=0, visitors_a=0, conversions_b=5, visitors_b=100)

    assert result.significant_at_95 is False
    assert result.error is not None


def test_conversions_exceeding_visitors_reports_an_error():
    result = two_proportion_z_test(conversions_a=50, visitors_a=10, conversions_b=5, visitors_b=100)

    assert result.error is not None


def test_perfect_conversion_rates_do_not_crash():
    """100% vs 100%: pooled_rate=1.0, standard_error=0 - must not divide by zero."""
    result = two_proportion_z_test(conversions_a=10, visitors_a=10, conversions_b=10, visitors_b=10)

    assert result.z_score == 0.0
    assert result.significant_at_95 is False

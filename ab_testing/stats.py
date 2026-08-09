"""
Real statistical significance testing for conversion-rate experiments
(two-proportion z-test) - no scipy dependency, uses math.erf for the
normal CDF, which is exact (not an approximation).
"""

import math
from dataclasses import dataclass
from typing import Optional


def _normal_cdf(x: float) -> float:
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


@dataclass
class ZTestResult:
    rate_a: float
    rate_b: float
    z_score: float
    p_value: float
    significant_at_95: bool
    error: Optional[str] = None

    @property
    def winner(self) -> Optional[str]:
        """'a', 'b', or None if not statistically significant."""
        if not self.significant_at_95:
            return None
        return "b" if self.rate_b > self.rate_a else "a"


def two_proportion_z_test(
    conversions_a: int, visitors_a: int, conversions_b: int, visitors_b: int,
) -> ZTestResult:
    """
    Two-proportion z-test comparing variant A's conversion rate to variant
    B's. Standard formula: pool the two proportions to estimate the shared
    standard error under the null hypothesis (no real difference), then
    compute how many standard errors apart the observed rates are.
    """
    if visitors_a <= 0 or visitors_b <= 0:
        return ZTestResult(
            rate_a=0.0, rate_b=0.0, z_score=0.0, p_value=1.0, significant_at_95=False,
            error="Both variants need at least 1 visitor to compare",
        )
    if conversions_a > visitors_a or conversions_b > visitors_b:
        return ZTestResult(
            rate_a=0.0, rate_b=0.0, z_score=0.0, p_value=1.0, significant_at_95=False,
            error="conversions cannot exceed visitors",
        )

    rate_a = conversions_a / visitors_a
    rate_b = conversions_b / visitors_b
    pooled_rate = (conversions_a + conversions_b) / (visitors_a + visitors_b)

    standard_error = math.sqrt(pooled_rate * (1 - pooled_rate) * (1 / visitors_a + 1 / visitors_b))

    if standard_error == 0:
        # Both rates are identical (both 0% or both 100%) - no difference to detect.
        z_score = 0.0
    else:
        z_score = (rate_b - rate_a) / standard_error

    p_value = 2 * (1 - _normal_cdf(abs(z_score)))  # two-tailed

    return ZTestResult(
        rate_a=rate_a,
        rate_b=rate_b,
        z_score=z_score,
        p_value=p_value,
        significant_at_95=p_value < 0.05,
    )

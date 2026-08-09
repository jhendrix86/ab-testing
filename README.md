# ab-testing

Shared A/B testing primitives for the OS42 engine fleet: deterministic
weighted variant assignment and two-proportion z-test statistical
significance. No database models here deliberately - each engine has its
own database, so this is a logic/assignment library (same pattern as
`unkey-auth`), not a shared data layer. Each consuming engine defines its
own tables for storing experiments, assignments, and outcomes.

## Setup

Each engine depends on this as a local editable install, matching the
`autonomy-events`/`unkey-auth` convention:

```
-e ../ab-testing
```

in the engine's `requirements.txt`.

## Usage

```python
from ab_testing import Experiment, Variant, assign_variant, two_proportion_z_test

experiment = Experiment(
    id="subject-line-test-42",
    name="Welcome email subject line",
    variants=[
        Variant(name="a", payload={"subject": "Welcome aboard!"}),
        Variant(name="b", payload={"subject": "You're in - here's what's next"}),
    ],
)

# Deterministic: the same subject_id always gets the same variant.
variant_name = assign_variant(experiment, subject_id="customer_123")
variant = experiment.get_variant(variant_name)
send_email(subject=variant.payload["subject"], to="customer_123")

# Later, once you have real send/open/click counts per variant:
result = two_proportion_z_test(
    conversions_a=42, visitors_a=500,   # variant "a": 42 opens out of 500 sent
    conversions_b=58, visitors_b=500,   # variant "b": 58 opens out of 500 sent
)
print(result.winner)            # "b", "a", or None if not statistically significant
print(result.p_value)           # real two-tailed p-value
print(result.significant_at_95) # True if p < 0.05
```

Unequal variant weights (e.g. 90% control / 10% treatment) are supported
via `Variant(weight=...)` - weights are normalized, they don't need to sum
to 1.

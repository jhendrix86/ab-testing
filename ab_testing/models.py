"""
Experiment/Variant spec - not tied to any ORM, deliberately. Each engine
that runs experiments has its own database; this package provides shared
assignment and statistics logic, not shared storage (same pattern as
unkey-auth: a shared client/logic library, not a shared data layer).
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class Variant:
    """One arm of an experiment."""
    name: str
    weight: float = 1.0  # relative traffic share; weights are normalized, don't need to sum to 1
    payload: Dict[str, Any] = field(default_factory=dict)  # the actual thing being tested (subject line, price, copy, ...)


@dataclass
class Experiment:
    """A named experiment with 2+ variants."""
    id: str
    name: str
    variants: List[Variant]

    def __post_init__(self):
        if len(self.variants) < 2:
            raise ValueError(f"Experiment '{self.id}' needs at least 2 variants, got {len(self.variants)}")
        if any(v.weight <= 0 for v in self.variants):
            raise ValueError(f"Experiment '{self.id}' has a variant with non-positive weight")
        names = [v.name for v in self.variants]
        if len(names) != len(set(names)):
            raise ValueError(f"Experiment '{self.id}' has duplicate variant names: {names}")

    def get_variant(self, name: str) -> Variant:
        for v in self.variants:
            if v.name == name:
                return v
        raise KeyError(f"No variant '{name}' in experiment '{self.id}'")

"""QAxelrod: quantum-game extension layer for Axelrod-style IPD simulations."""
from .quantum_ipd import PayoffMatrix, action_unitary, entangler, expected_payoffs, outcome_probabilities
from .simulation import play_match, round_robin, moran_fixation_probability
from .strategies import default_strategies

__all__ = [
    "PayoffMatrix",
    "action_unitary",
    "entangler",
    "expected_payoffs",
    "outcome_probabilities",
    "play_match",
    "round_robin",
    "moran_fixation_probability",
    "default_strategies",
]

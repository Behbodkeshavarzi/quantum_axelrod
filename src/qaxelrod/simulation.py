"""Simulation routines for repeated quantum IPD matches and simple evolution."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np

from .quantum_ipd import (
    PayoffMatrix,
    action_unitary,
    expected_payoffs,
    outcome_probabilities,
    sample_outcome,
)
from .strategies import Strategy


@dataclass
class MatchResult:
    actions_a: list[str]
    actions_b: list[str]
    measured_a: list[str]
    measured_b: list[str]
    payoff_a: float
    payoff_b: float

    @property
    def cooperation_rate(self) -> float:
        outcomes = self.measured_a + self.measured_b
        return outcomes.count("C") / len(outcomes) if outcomes else 0.0


def bit_to_action(bit: int) -> str:
    return "C" if bit == 0 else "D"


def play_match(
    strategy_a: Strategy,
    strategy_b: Strategy,
    rounds: int = 100,
    gamma: float = 0.0,
    noise: float = 0.0,
    noise_model: str = "none",
    lift: str = "classical",
    phase: float = np.pi / 2,
    seed: int | None = None,
    payoff: PayoffMatrix = PayoffMatrix(),
) -> MatchResult:
    """Play a repeated two-player quantum IPD match.

    Histories are updated with the measured C/D outcomes, because these are the
    public actions observed by Axelrod-style strategies after each round.
    """
    rng = np.random.default_rng(seed)
    a = strategy_a.clone()
    b = strategy_b.clone()
    a.reset(); b.reset()
    hist_a: list[tuple[str, str]] = []
    hist_b: list[tuple[str, str]] = []
    planned_a: list[str] = []
    planned_b: list[str] = []
    measured_a: list[str] = []
    measured_b: list[str] = []
    payoff_a = 0.0
    payoff_b = 0.0

    for _ in range(rounds):
        act_a = a.move(hist_a, rng)
        act_b = b.move(hist_b, rng)
        planned_a.append(act_a); planned_b.append(act_b)
        units = [action_unitary(act_a, lift=lift, phase=phase), action_unitary(act_b, lift=lift, phase=phase)]
        probs = outcome_probabilities(units, gamma=gamma, noise=noise, noise_model=noise_model)
        _, bits = sample_outcome(probs, rng)
        obs_a = bit_to_action(bits[0])
        obs_b = bit_to_action(bits[1])
        measured_a.append(obs_a); measured_b.append(obs_b)
        # Realized payoff from the sampled outcome.
        if obs_a == "C" and obs_b == "C":
            payoff_a += payoff.R; payoff_b += payoff.R
        elif obs_a == "C" and obs_b == "D":
            payoff_a += payoff.S; payoff_b += payoff.T
        elif obs_a == "D" and obs_b == "C":
            payoff_a += payoff.T; payoff_b += payoff.S
        else:
            payoff_a += payoff.P; payoff_b += payoff.P
        hist_a.append((obs_a, obs_b))
        hist_b.append((obs_b, obs_a))

    return MatchResult(planned_a, planned_b, measured_a, measured_b, payoff_a / rounds, payoff_b / rounds)


def round_robin(
    strategies: Sequence[Strategy],
    rounds: int = 100,
    repetitions: int = 10,
    gamma: float = 0.0,
    noise: float = 0.0,
    noise_model: str = "none",
    lift: str = "phase",
    phase: float = np.pi / 2,
    seed: int = 12345,
) -> dict[str, dict[str, float]]:
    """Run a round-robin tournament and return mean payoff/cooperation by strategy."""
    rng = np.random.default_rng(seed)
    totals = {s.name: 0.0 for s in strategies}
    coop = {s.name: 0.0 for s in strategies}
    counts = {s.name: 0 for s in strategies}
    for rep in range(repetitions):
        for i, si in enumerate(strategies):
            for j, sj in enumerate(strategies):
                if i == j:
                    continue
                result = play_match(
                    si,
                    sj,
                    rounds=rounds,
                    gamma=gamma,
                    noise=noise,
                    noise_model=noise_model,
                    lift=lift,
                    phase=phase,
                    seed=int(rng.integers(0, 2**32 - 1)),
                )
                totals[si.name] += result.payoff_a
                coop[si.name] += result.measured_a.count("C") / rounds
                counts[si.name] += 1
    return {
        name: {
            "mean_payoff": totals[name] / counts[name],
            "cooperation_rate": coop[name] / counts[name],
        }
        for name in totals
    }


def stage_payoff_matrix(
    strategies: Sequence[Strategy],
    gamma: float,
    lift: str = "phase",
    phase: float = np.pi / 2,
    noise: float = 0.0,
    noise_model: str = "none",
) -> np.ndarray:
    """Expected one-stage payoff matrix using first moves only."""
    rng = np.random.default_rng(2026)
    n = len(strategies)
    mat = np.zeros((n, n), dtype=float)
    for i, si in enumerate(strategies):
        for j, sj in enumerate(strategies):
            ai = si.clone().move([], rng)
            aj = sj.clone().move([], rng)
            units = [action_unitary(ai, lift=lift, phase=phase), action_unitary(aj, lift=lift, phase=phase)]
            mat[i, j] = expected_payoffs(units, gamma, noise=noise, noise_model=noise_model)[0]
    return mat


def moran_fixation_probability(
    resident: Strategy,
    mutant: Strategy,
    population_size: int = 20,
    rounds: int = 30,
    gamma: float = np.pi / 4,
    noise: float = 0.02,
    noise_model: str = "bit_flip",
    lift: str = "phase",
    selection_strength: float = 0.8,
    runs: int = 100,
    seed: int = 7,
) -> float:
    """Estimate fixation probability in a well-mixed birth-death Moran process.

    This is a compact reference implementation for reproducible examples. It is
    not optimized for very large populations or the full Axelrod catalog.
    """
    rng = np.random.default_rng(seed)
    fixations = 0
    for _ in range(runs):
        pop: list[Strategy] = [resident.clone() for _ in range(population_size - 1)] + [mutant.clone()]
        rng.shuffle(pop)
        for _step in range(1_500):
            mutant_count = sum(ind.name == mutant.name for ind in pop)
            if mutant_count == population_size:
                fixations += 1
                break
            if mutant_count == 0:
                break
            payoffs = np.zeros(population_size, dtype=float)
            # Each individual plays a small sample of opponents for speed.
            for i in range(population_size):
                opponents = rng.choice([j for j in range(population_size) if j != i], size=min(4, population_size - 1), replace=False)
                for j in opponents:
                    r = play_match(
                        pop[i], pop[j], rounds=rounds, gamma=gamma, noise=noise,
                        noise_model=noise_model, lift=lift, seed=int(rng.integers(0, 2**32 - 1))
                    )
                    payoffs[i] += r.payoff_a / len(opponents)
            fitness = np.exp(selection_strength * payoffs)
            parent_idx = int(rng.choice(population_size, p=fitness / fitness.sum()))
            death_idx = int(rng.integers(0, population_size))
            pop[death_idx] = pop[parent_idx].clone()
    return fixations / runs

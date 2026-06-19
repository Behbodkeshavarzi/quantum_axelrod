"""Small reference strategy set and an optional adapter hook for Axelrod."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence, Tuple

import numpy as np

Action = str
History = List[Tuple[Action, Action]]


class Strategy:
    """Base class for deterministic or stochastic C/D policies."""

    name = "Strategy"

    def reset(self) -> None:
        pass

    def move(self, history: History, rng: np.random.Generator) -> Action:
        raise NotImplementedError

    def clone(self) -> "Strategy":
        return self.__class__()

    def __repr__(self) -> str:
        return self.name


class Cooperator(Strategy):
    name = "ALLC"

    def move(self, history: History, rng: np.random.Generator) -> Action:
        return "C"


class Defector(Strategy):
    name = "ALLD"

    def move(self, history: History, rng: np.random.Generator) -> Action:
        return "D"


class TitForTat(Strategy):
    name = "TFT"

    def move(self, history: History, rng: np.random.Generator) -> Action:
        return "C" if not history else history[-1][1]


class SuspiciousTitForTat(Strategy):
    name = "STFT"

    def move(self, history: History, rng: np.random.Generator) -> Action:
        return "D" if not history else history[-1][1]


class GrimTrigger(Strategy):
    name = "Grim"

    def move(self, history: History, rng: np.random.Generator) -> Action:
        return "D" if any(opp == "D" for _, opp in history) else "C"


class WinStayLoseShift(Strategy):
    name = "WSLS"

    def move(self, history: History, rng: np.random.Generator) -> Action:
        if not history:
            return "C"
        mine, opp = history[-1]
        # Stay after CC or DD, shift after CD or DC.
        if mine == opp:
            return mine
        return "D" if mine == "C" else "C"


@dataclass
class GenerousTitForTat(Strategy):
    forgiveness: float = 0.30
    name: str = "GTFT"

    def move(self, history: History, rng: np.random.Generator) -> Action:
        if not history or history[-1][1] == "C":
            return "C"
        return "C" if rng.random() < self.forgiveness else "D"

    def clone(self) -> "Strategy":
        return GenerousTitForTat(self.forgiveness)


@dataclass
class RandomStrategy(Strategy):
    p_cooperate: float = 0.5
    name: str = "Random"

    def move(self, history: History, rng: np.random.Generator) -> Action:
        return "C" if rng.random() < self.p_cooperate else "D"

    def clone(self) -> "Strategy":
        return RandomStrategy(self.p_cooperate)


@dataclass
class MemoryOne(Strategy):
    """Memory-one strategy with probabilities p(CC), p(CD), p(DC), p(DD)."""

    p: Sequence[float]
    name: str = "MemoryOne"

    def move(self, history: History, rng: np.random.Generator) -> Action:
        if not history:
            return "C"
        index = {("C", "C"): 0, ("C", "D"): 1, ("D", "C"): 2, ("D", "D"): 3}[history[-1]]
        return "C" if rng.random() < float(self.p[index]) else "D"

    def clone(self) -> "Strategy":
        return MemoryOne(tuple(self.p), self.name)


def default_strategies() -> list[Strategy]:
    """Return a compact strategy panel for quick, reproducible examples."""
    return [
        Cooperator(),
        Defector(),
        TitForTat(),
        SuspiciousTitForTat(),
        WinStayLoseShift(),
        GrimTrigger(),
        GenerousTitForTat(0.30),
        RandomStrategy(0.50),
        MemoryOne((0.90, 0.20, 0.70, 0.10), "ContriteMO"),
        MemoryOne((0.70, 0.05, 0.30, 0.00), "ExtortLike"),
    ]


def axelrod_strategy_names(limit: int | None = None) -> list[str]:
    """Return available Axelrod strategies when the optional dependency exists.

    This function intentionally avoids importing Axelrod at package import time.
    A full production adapter should translate Axelrod's Action objects to C/D
    and should respect each class's constructor requirements.
    """
    try:
        import axelrod as axl  # type: ignore
    except Exception:
        return []
    names = [cls.__name__ for cls in axl.strategies]
    return names if limit is None else names[:limit]

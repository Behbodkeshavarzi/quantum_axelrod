# QAxelrod

QAxelrod is a compact research package for running Axelrod-style Iterated Prisoner's Dilemma (IPD) experiments in a quantum-game execution layer. It separates classical policy logic from quantum execution: strategies choose `C` or `D` from observed histories, and the execution layer maps those symbols to EWL-style unitaries.

## Why this revision matters

The original manuscript contained a critical mathematical issue: a pairwise `ZZ` phase applied directly to `|00...0>` does not entangle the state. QAxelrod uses a GHZ-type EWL entangler and includes tests verifying both entangler behavior and exact classical recovery.

A second correction is conceptual: mapping classical actions only to classical EWL operators is a control condition. Entanglement-dependent effects require a non-classical phase lift, genuinely quantum strategies, or noise.

## Installation

```bash
python -m pip install -e .[test]
```

## Run tests

```bash
PYTHONPATH=src pytest -q
```

## Reproduce figures and CSV files

```bash
PYTHONPATH=src python scripts/reproduce_figures.py
```

Generated outputs are written to:

- `results/*.csv`
- `paper/figures/*.pdf`
- `paper/figures/*.png`

## Minimal example

```python
import numpy as np
from qaxelrod.simulation import play_match
from qaxelrod.strategies import TitForTat, Defector

result = play_match(
    TitForTat(), Defector(),
    rounds=100,
    gamma=np.pi / 4,
    noise=0.02,
    noise_model="bit_flip",
    lift="phase",
    seed=2026,
)
print(result.payoff_a, result.payoff_b, result.cooperation_rate)
```

## Project structure

```text
src/qaxelrod/quantum_ipd.py   Core unitaries, entangler, noise, measurement, payoffs
src/qaxelrod/strategies.py    Reference strategies and optional Axelrod discovery hook
src/qaxelrod/simulation.py    Repeated matches, round-robin tournaments, fixation examples
scripts/reproduce_figures.py  Recreates example results and figures
tests/                        Unit tests
paper/full_manuscript.tex     Revised full LaTeX manuscript
paper/paper.md                JOSS-format software paper
```

## Before submission

Replace all anonymous metadata with author names, affiliations, ORCID IDs, repository URL, and software archive DOI. For JOSS, host the software and `paper.md` in a public Git repository with an OSI-approved license, issue tracker, tests, and documentation.

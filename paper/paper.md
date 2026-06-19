---
title: 'QAxelrod: A quantum-game extension layer for Axelrod-style Iterated Prisoner’s Dilemma simulations'
tags:
  - Python
  - quantum game theory
  - iterated prisoner's dilemma
  - Axelrod
  - multi-agent simulation
  - evolutionary dynamics
authors:
  - name: Anonymous Author
    orcid: 0000-0000-0000-0000
    affiliation: 1
affiliations:
  - name: Anonymous affiliation
    index: 1
date: 19 June 2026
bibliography: paper.bib
---

# Summary

QAxelrod is a Python package for running Axelrod-style Iterated Prisoner’s Dilemma (IPD) experiments in a quantum-game execution layer. Classical IPD strategies choose cooperation or defection from observed histories, while QAxelrod maps these symbols to configurable one-qubit operations in an Eisert--Wilkens--Lewenstein (EWL) inspired game. The package provides corrected entanglement primitives, local noise channels, repeated matches, round-robin tournaments, reference evolutionary calculations, unit tests, and figure-generation scripts.

The project is designed for researchers who want to compare classical and quantum variants of cooperation dynamics without rewriting established IPD strategies. It separates the policy layer from the execution layer: a policy may remain a conventional Tit-for-Tat, Win-Stay-Lose-Shift, Grim Trigger, or memory-one rule, but the executed action may be a classical EWL action or a non-classical phase action. This separation makes it possible to ask which effects are due to classical policy logic and which are due to the quantum execution environment.

# Statement of need

The classical IPD is a standard model for reciprocity, cooperation, punishment, and evolutionary selection [@Axelrod1984; @Axelrod1997; @Nowak2006]. The open-source Axelrod ecosystem has made large-scale strategy tournaments reusable by implementing a broad catalog of classical strategies [@Knight2016]. Quantum game theory, in contrast, studies how coherent operations, entanglement, and measurement can alter strategic incentives [@Eisert1999; @Meyer1999; @Flitney2002]. These literatures are closely related but computationally disconnected: most quantum-game examples use small hand-written strategy sets, while most Axelrod-style studies are purely classical.

QAxelrod addresses this gap by providing a tested bridge between Axelrod-style policy logic and quantum-game dynamics. A central design feature is mathematical defensibility. The package avoids a common modeling error: applying a pairwise $ZZ$ phase to $|0\ldots0\rangle$ does not entangle the state, because that vector is an eigenstate of every $Z_iZ_j$ term. QAxelrod instead implements a GHZ-type EWL entangler, together with unit tests showing that the classical lift exactly recovers the classical IPD in the noiseless control condition. This is important because a purely classical lift of cooperation and defection should not itself generate an entanglement-dependent advantage; non-classical phase lifts, genuinely quantum strategies, or noise are required for quantum effects to appear.

# Functionality

QAxelrod currently provides:

- EWL one-qubit strategy operators and a multi-player GHZ-type EWL entangler.
- A density-matrix stage-game simulator with bit-flip and depolarizing noise channels.
- Pairwise-additive $n$-player payoffs that reduce to the standard two-player Prisoner’s Dilemma.
- Classical, phase, and mixed-phase action lifts for mapping policy outputs to quantum operations.
- A compact reference strategy panel, including ALLC, ALLD, Tit-for-Tat, Win-Stay-Lose-Shift, Grim Trigger, Generous Tit-for-Tat, random, and memory-one policies.
- Repeated-match and round-robin tournament routines that update histories using measured actions.
- A reference Moran-style fixation calculation for small evolutionary examples.
- Tests for probability normalization, classical recovery, and entangler correctness.
- Reproducibility scripts that regenerate the example CSV files and manuscript figures.

The package is intentionally modular. Researchers can use the bundled strategies for quick experiments or connect to the full Axelrod library through the optional adapter hook. The current adapter exposes strategy discovery and is intended to be extended into a production wrapper that respects the constructor requirements and metadata of the external Axelrod package.

# Example use

The package can be installed from a cloned repository in editable mode:

```bash
python -m pip install -e .[test]
PYTHONPATH=src pytest -q
PYTHONPATH=src python scripts/reproduce_figures.py
```

A minimal two-strategy experiment is:

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

# Research applications

QAxelrod supports experiments on quantum extensions of reciprocity, extortion, generous strategies, memory-one policies, noise robustness, and evolutionary selection. It is also useful as a teaching package because it exposes the distinction between classical policy choice and quantum execution choice. This distinction reduces the risk of attributing a quantum effect to entanglement when the underlying model is actually a classical control case.

The included manuscript and scripts are not an exhaustive benchmark of all Axelrod strategies. They are a reproducible starting point for larger studies that sweep entanglement, noise, strategy subsets, topology, and evolutionary rules. Future development should add a complete Axelrod wrapper, graph-structured populations, circuit backends for quantum hardware experiments, and continuous integration benchmarks.

# Acknowledgements

Replace this paragraph with funding, institutional, and contributor acknowledgements before submission.

# References

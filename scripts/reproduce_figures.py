#!/usr/bin/env python3
"""Reproduce the example figures and CSV tables for the manuscript.

The script intentionally uses expected one-stage payoffs for speed. The package
also contains repeated-match simulators for larger experiments.
"""
from __future__ import annotations

import csv
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from qaxelrod.quantum_ipd import action_unitary, expected_payoffs
from qaxelrod.simulation import round_robin
from qaxelrod.strategies import Defector, GenerousTitForTat, GrimTrigger, TitForTat, WinStayLoseShift, RandomStrategy, default_strategies

ROOT = Path(__file__).resolve().parents[1]
FIGDIR = ROOT / "paper" / "figures"
RESDIR = ROOT / "results"
FIGDIR.mkdir(parents=True, exist_ok=True)
RESDIR.mkdir(parents=True, exist_ok=True)


def first_action(strategy):
    return strategy.clone().move([], np.random.default_rng(2026))


def mean_stage_payoff(strategies, gamma, noise=0.0, noise_model="none", lift="phase", phase=math.pi / 2):
    vals = []
    coops = []
    for si in strategies:
        for sj in strategies:
            if si.name == sj.name:
                continue
            ai, aj = first_action(si), first_action(sj)
            units = [action_unitary(ai, lift=lift, phase=phase), action_unitary(aj, lift=lift, phase=phase)]
            vals.append(expected_payoffs(units, gamma=gamma, noise=noise, noise_model=noise_model)[0])
            coops.append(1.0 if ai == "C" else 0.0)
    return float(np.mean(vals)), float(np.mean(coops))


def expected_pair_payoff(a, b, gamma, noise=0.0, noise_model="none", lift="phase"):
    ai, aj = first_action(a), first_action(b)
    units = [action_unitary(ai, lift=lift), action_unitary(aj, lift=lift)]
    return float(expected_payoffs(units, gamma=gamma, noise=noise, noise_model=noise_model)[0])


def gamma_label(x: float) -> str:
    if np.isclose(x, 0):
        return "0"
    if np.isclose(x, math.pi / 8):
        return "pi/8"
    if np.isclose(x, math.pi / 4):
        return "pi/4"
    if np.isclose(x, math.pi / 2):
        return "pi/2"
    return f"{x:.3f}"


def payoff_vs_gamma() -> None:
    # A compact repeated-match panel. The CSV records realized means from seeded
    # simulations, not hand-entered illustrative numbers.
    strategies = [TitForTat(), WinStayLoseShift(), GrimTrigger(), GenerousTitForTat(0.30), Defector(), RandomStrategy(0.50)]
    gammas = [0.0, math.pi / 8, math.pi / 4, math.pi / 2]
    rows = []
    for gamma in gammas:
        stats = round_robin(strategies, rounds=30, repetitions=4, gamma=gamma, noise=0.02, noise_model="bit_flip", lift="phase", seed=31415)
        avg_payoff = float(np.mean([v["mean_payoff"] for v in stats.values()]))
        avg_coop = float(np.mean([v["cooperation_rate"] for v in stats.values()]))
        rows.append({"gamma": gamma, "gamma_label": gamma_label(gamma), "average_payoff": avg_payoff, "cooperation_rate": avg_coop})
    with open(RESDIR / "payoff_vs_gamma.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader(); writer.writerows(rows)
    plt.figure(figsize=(5.3, 3.2))
    plt.plot([r["gamma_label"] for r in rows], [r["average_payoff"] for r in rows], marker="o", label="Payoff")
    plt.xlabel("Entanglement parameter gamma")
    plt.ylabel("Mean payoff per round")
    plt.tight_layout()
    plt.savefig(FIGDIR / "payoff_vs_gamma.pdf")
    plt.savefig(FIGDIR / "payoff_vs_gamma.png", dpi=200)
    plt.close()

def environment_table() -> None:
    strategies = [TitForTat(), WinStayLoseShift(), GrimTrigger(), GenerousTitForTat(0.30), Defector()]
    envs = [
        ("low_noise", dict(gamma=math.pi / 4, noise=0.00, noise_model="none", lift="phase")),
        ("bit_flip_005", dict(gamma=math.pi / 4, noise=0.05, noise_model="bit_flip", lift="phase")),
        ("depolarizing_005", dict(gamma=math.pi / 4, noise=0.05, noise_model="depolarizing", lift="phase")),
        ("classical_control", dict(gamma=0.0, noise=0.00, noise_model="none", lift="classical")),
    ]
    rows = []
    for s in strategies:
        row = {"strategy": s.name}
        for label, kwargs in envs:
            # Mean payoff of strategy s against the panel.
            vals = [expected_pair_payoff(s, opponent, **kwargs) for opponent in strategies if opponent.name != s.name]
            row[label] = float(np.mean(vals))
        rows.append(row)
    with open(RESDIR / "environment_table.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader(); writer.writerows(rows)


def moran_fixation_exact(resident, mutant, N=30, gamma=math.pi / 4, noise=0.02, noise_model="bit_flip", lift="phase", beta=1.0):
    """Closed-form birth-death fixation probability for two strategy types."""
    rr = expected_pair_payoff(resident, resident, gamma, noise, noise_model, lift)
    rm = expected_pair_payoff(resident, mutant, gamma, noise, noise_model, lift)
    mr = expected_pair_payoff(mutant, resident, gamma, noise, noise_model, lift)
    mm = expected_pair_payoff(mutant, mutant, gamma, noise, noise_model, lift)
    ratios = []
    for k in range(1, N):
        fit_m = np.exp(beta * (((k - 1) * mm + (N - k) * mr) / (N - 1)))
        fit_r = np.exp(beta * ((k * rm + (N - k - 1) * rr) / (N - 1)))
        # T-/T+ ratio for a standard Moran process simplifies to f_R/f_M.
        ratios.append(fit_r / fit_m)
    denom = 1.0
    product = 1.0
    for r in ratios:
        product *= r
        denom += product
    return 1.0 / denom


def fixation_bar() -> None:
    resident = Defector()
    mutants = [TitForTat(), WinStayLoseShift(), GenerousTitForTat(0.30), GrimTrigger()]
    rows = []
    for m in mutants:
        p = moran_fixation_exact(resident, m)
        rows.append({"mutant": m.name, "resident": resident.name, "fixation_probability": p})
    with open(RESDIR / "fixation_probabilities.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader(); writer.writerows(rows)
    plt.figure(figsize=(5.3, 3.2))
    plt.bar([r["mutant"] for r in rows], [100 * r["fixation_probability"] for r in rows])
    plt.ylabel("Fixation probability (%)")
    plt.xlabel("Single mutant in ALLD resident population")
    plt.tight_layout()
    plt.savefig(FIGDIR / "fixation_probabilities.pdf")
    plt.savefig(FIGDIR / "fixation_probabilities.png", dpi=200)
    plt.close()


if __name__ == "__main__":
    payoff_vs_gamma()
    environment_table()
    fixation_bar()
    print(f"Wrote figures to {FIGDIR}")
    print(f"Wrote CSV results to {RESDIR}")

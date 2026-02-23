# Quantum Triadic Autopsy

> **Open-source diagnostic tools for NISQ quantum hardware stability —  
> calculating the "real" vs "marketed" qubit count from public calibration data**

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.18475832-blue)](https://doi.org/10.5281/zenodo.18475832)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org)
[![CI](https://github.com/UniversalModel/Quantum-triadic-autopsy/actions/workflows/ci.yml/badge.svg)](https://github.com/UniversalModel/Quantum-triadic-autopsy/actions/workflows/ci.yml)
[![Challenge](https://img.shields.io/badge/Challenge-0.618%20open-gold)](https://github.com/UniversalModel/Quantum-triadic-autopsy#the-0618-challenge)

---

## Quick Start — 3 Commands

```bash
git clone https://github.com/UniversalModel/Quantum-triadic-autopsy
cd Quantum-triadic-autopsy
pip install -r requirements.txt
python run_all.py           # runs all tools, outputs go to results/
```

No IBM account needed. Demo mode uses a public 127-qubit Brisbane snapshot (Feb 2026).

---

## The Problem in One Number

**IBM Brisbane, 127 qubits — average SI_Q = 0.11**

That means **99% of the chip is computationally useless** by an objective metric.  
IBM counts qubits. This repo counts *useful* computation.

---

## The SI_Q Metric

A single hardware health score computed from three independent properties:

```
SI_Q = cbrt(F_Q x P_Q x A_Q) / (1 + delta)^2

F_Q   = min(1, (T1 + T2) / 500 us)              -- Form     (coherence lifetime)
P_Q   = min(1, n_neighbors / 6)                  -- Position (connectivity)
A_Q   = max(0, 1 - gate_err*100 - ro_err*10)    -- Action   (gate fidelity)
delta = (max(F,P,A) - min(F,P,A)) / max(F,P,A)  -- Triadic imbalance
```

| SI_Q | Zone | Meaning |
|---|---|---|
| >= 0.618 | **Utility Zone** | Error suppression exceeds encoding overhead |
| 0.40-0.617 | Warning Zone | Marginal -- overhead approaching break-even |
| < 0.40 | **Dead Zone** | Active error amplification -- computationally useless |

**No current real hardware platform on > 40 qubits reaches even 0.50.**

---

## The Four Tools

### `IBM_Q_SI_Q_Autopsy.py` -- Qubit-level Diagnostic

```bash
python IBM_Q_SI_Q_Autopsy.py --demo                          # no account needed
python IBM_Q_SI_Q_Autopsy.py --backend ibm_brisbane          # live data
```

Outputs: chip heatmap (PNG), per-qubit F/P/A bar chart (PNG), full report (TXT).

**Brisbane 127q result:** avg SI_Q = 0.11 -- 99.2% qubits in Dead Zone

---

### `sisyphus_diagram.py` -- The Sisyphus Diagram

```bash
python sisyphus_diagram.py
python sisyphus_diagram.py --lang bg    # Bulgarian labels
```

Four-panel diagram from IBM public data: physical qubits (exponential) vs useful
logical qubits (flat zero) vs U-Core projection vs Dead Zone ratio.

> *"Sisyphus pushes the boulder up. The boulder stays at zero useful qubits."*

---

### `golden_ratio_challenge.py` -- The Open Leaderboard

```bash
python golden_ratio_challenge.py
```

Generates a ranked leaderboard + challenge declaration.

**Current standings (Feb 2026):**

| Platform | Qubits | SI_Q | Status |
|---|---|---|---|
| Quantinuum H2-1 | 32 | 0.47 | Below 40q threshold |
| QuEra Aquila | 256 | 0.39 | Estimated |
| IBM Heron R2 | 133 | 0.36 | Estimated |
| Google Willow | 105 | 0.34 | Estimated |
| IBM Brisbane | 127 | **0.11** | Measured |

**Gap to 0.618: >= 0.148**

---

### `u_core_simulator_v25_2.py` -- Alternative Architecture

```bash
python u_core_simulator_v25_2.py              # interactive
python u_core_simulator_v25_2.py --no-show   # headless / CI
```

Simulation of a Gaussian Concentric QPU designed to reach SI_Q >= 0.618.

| Metric | IBM Brisbane | U-Core Simulation |
|---|---|---|
| Avg SI_Q | 0.11 | **0.71** |
| Dead Zone | 99.2% | **0%** |
| Logical overhead | Surface Code ~10,000:1 | MELQ ~3:1 |

*Note: U-Core results are simulation -- not yet validated on real hardware.*

---

## Why 0.618?

The threshold is derived from MELQ DFS encoding at 3:1 overhead
with typical superconducting imbalance delta ~ 0.07:

```
Logical error rate:  eps_L = 3 * eps_P^2   (DFS second-order suppression)
Break-even:          eps_P < 1/3  ->  A_Q > 0.667
With delta=0.07:     SI_Q_threshold = 0.667 / (1.07)^2 = 0.618
```

This falls in the **tight neighborhood of phi^-1 = 0.6180...** under realistic parameters.

| Encoding overhead | Avg delta | Threshold |
|---|---|---|
| 2:1 (optimistic) | 0.03 | 0.707 |
| 3:1 (MELQ baseline) | 0.07 | **0.618** |
| 4:1 (conservative) | 0.12 | 0.553 |

We do not claim 0.618 is universally exact. We claim no platform reaches even 0.50.

---

## The 0.618 Challenge

**Falsifiable. Public. Open to everyone.**

Achieve avg SI_Q >= 0.618 on real quantum hardware with > 40 physical qubits.

1. Run `python IBM_Q_SI_Q_Autopsy.py --backend YOUR_BACKEND`
2. [Open a Validation Submission issue](https://github.com/UniversalModel/Quantum-triadic-autopsy/issues/new?template=validation_submission.yml)
3. Or email **petar@u-model.org** with subject `[SI_Q] <backend> <date>`

**Reward:** credited as *"Triadic Optimizer 2026/27"* in U-Theory v26.0 and next arXiv preprint.

---

## Falsifiable Predictions

| ID | Prediction | How to falsify |
|---|---|---|
| QC-P1 | TQC achieves SI_Q > 0.65 on 43q U-Core | Show standard VQE on 86q beats TQC-43q |
| QC-P3 | Triadic VQE reduces gate depth 30%+ vs Qiskit Level-3 | Show Qiskit transpiler matches on LiH |
| QC-P17 | delta < 0.3 guarantees polynomial VQA gradient | Show random ansatz with delta<0.3 has exponential gradient |

---

## Installation

```bash
git clone https://github.com/UniversalModel/Quantum-triadic-autopsy
cd Quantum-triadic-autopsy
pip install -r requirements.txt

# Optional -- for live IBM backend access:
pip install qiskit-ibm-runtime
```

**Requirements:** `numpy >= 1.24`, `matplotlib >= 3.7`, `networkx >= 3.0`, Python 3.9+

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) -- the most valuable contribution is running
the tools on hardware we do not have access to and reporting the results.

---

## Citation

```bibtex
@software{nikolov2026quantum_triadic_autopsy,
  author    = {Nikolov, Petar},
  title     = {Quantum Triadic Autopsy -- NISQ hardware diagnostic tools},
  year      = {2026},
  publisher = {GitHub},
  url       = {https://github.com/UniversalModel/Quantum-triadic-autopsy},
  doi       = {10.5281/zenodo.18475832}
}
```

---

## Theory Reference

| | |
|---|---|
| Full theory | [U-Theory v25.2 -- Zenodo](https://doi.org/10.5281/zenodo.18475832) |
| Author | Petar Nikolov, 2026 |
| Contact | petar@u-model.org |
| Website | [U-Model.org](https://u-model.org) |

---

**Copyright (c) 2026 Petar Nikolov -- CC BY 4.0**

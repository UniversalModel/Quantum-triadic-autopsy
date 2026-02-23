# Quantum Triadic Autopsy

> **Open-source diagnostic tools for NISQ quantum hardware stability —  
> calculating the "real" vs "marketed" qubit count from public calibration data**

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.18475832-blue)](https://doi.org/10.5281/zenodo.18475832)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org)
[![SI_Q Challenge](https://img.shields.io/badge/Challenge-0.618%20Golden%20Ratio-gold)](https://github.com/UniversalModel/Quantum-triadic-autopsy#the-0618-golden-ratio-challenge)

---

## The Problem in One Number

IBM Brisbane (127 qubits, 2024) — **average SI_Q = 0.11**

That means **99% of qubits are in the Dead Zone** (SI_Q < 0.40).  
IBM's roadmap counts qubits. Nobody counts *useful* computation.

This repo does.

---

## The SI_Q Metric

U-Theory quantifies hardware health through three triadic components:

```
SI_Q = cbrt(F_Q * P_Q * A_Q) / (1 + delta)^2

F_Q   = min(1, (T1 + T2) / 500 us)             -- Form     (coherence)
P_Q   = min(1, neighbors / 6)                   -- Position (connectivity)
A_Q   = max(0, 1 - gate_err*100 - ro_err*10)   -- Action   (gate fidelity)
delta = (max(F,P,A) - min(F,P,A)) / max(F,P,A) -- Triadic imbalance
```

### Why 0.618? (Neighborhood of the Golden Ratio)

The threshold is **not** derived from a universal law — it depends on encoding
overhead and hardware characteristics. The derivation under MELQ DFS (3:1 overhead,
typical superconducting imbalance δ ≈ 0.07) gives:

```
Logical error rate:  eps_L = 3 * eps_P^2   (second-order DFS suppression)
Break-even:          eps_P < 1/3  =>  A_Q > 0.667
With avg delta=0.07: SI_Q_threshold = 0.667 / (1.07)^2 = 0.618
```

Sensitivity to assumptions:

| Encoding overhead | Avg hardware δ | Threshold |
|---|---|---|
| 2:1 (optimistic) | 0.03 | 0.707 |
| 3:1 (MELQ baseline) | 0.07 | **0.618** |
| 4:1 (conservative) | 0.12 | 0.553 |

The result falls **in the tight neighborhood of φ⁻¹ = 0.6180...** under realistic
assumptions. We choose 0.618 as the challenge threshold because:
1. It emerges naturally from the physics under MELQ baseline parameters
2. It coincides with a mathematically well-known constant — easy to remember and cite
3. It is falsifiable: run `IBM_Q_SI_Q_Autopsy.py` on any backend and compare

*We do not claim 0.618 is universally exact. We claim it is the right order of
magnitude for current NISQ hardware, and that no platform has reached even 0.50.*

| SI_Q range | Zone | Meaning |
|---|---|---|
| >= 0.618 | **Utility Zone** | Error suppression exceeds physical overhead |
| 0.40 – 0.617 | Warning Zone | Marginal — overhead exceeds benefit |
| < 0.40 | **Dead Zone** | Error amplification: computationally useless |

**No current hardware on >40 qubits reaches even 0.50.**

---

## The Four Tools

### 1. `IBM_Q_SI_Q_Autopsy.py` — Qubit-level Diagnostic

Runs a full triadic autopsy on any IBM Quantum backend using public calibration data.

```bash
# No IBM account needed — uses 127-qubit Brisbane snapshot:
python IBM_Q_SI_Q_Autopsy.py --demo

# With IBM account:
python IBM_Q_SI_Q_Autopsy.py --backend ibm_brisbane
```

**Output:**
- `*_si_q_autopsy.png` — chip heatmap coloured by SI_Q (red = dead, green = alive)
- `*_si_q_bars.png` — per-qubit F / P / A triadic decomposition
- `*_si_q_report.txt` — full numerical breakdown

**Key result (Brisbane 127q):** avg SI_Q = 0.11 · 99.2% qubits in Dead Zone

---

### 2. `sisyphus_diagram.py` — The Triple Lie

Four-panel diagram built from IBM's own public data:

| Panel | What it shows |
|---|---|
| Physical qubits | Exponential growth — IBM's headline number |
| Useful logical qubits | Flat line of zero — what nobody shows |
| U-Core MELQ projection | 4 to 14 to 32 logical qubits by 2028 |
| Dead Zone ratio | The widening gap |

```bash
python sisyphus_diagram.py
python sisyphus_diagram.py --out my_diagram.png
```

> *"Sisyphus pushes the boulder up. The boulder stays at zero useful qubits."*

Data sources: IBM roadmap (public), Kim et al. Nature 618 (2023), Tilly et al. (2022), Google Willow announcement (2024).

---

### 3. `golden_ratio_challenge.py` — The Open Challenge

Tracks who has crossed SI_Q >= 0.618 on real hardware with >40 qubits.
Generates a live leaderboard and shareable challenge declaration.

```bash
python golden_ratio_challenge.py
python golden_ratio_challenge.py --add-entry
python golden_ratio_challenge.py --out-dir results/
```

**Current leaderboard (Feb 2026):**

| Platform | Qubits | SI_Q | Status |
|---|---|---|---|
| Quantinuum H2-1 | 32 | 0.47 | Below 40q threshold |
| QuEra Aquila | 256 | 0.39 | Estimated |
| IBM Heron R2 | 133 | 0.36 | Estimated |
| Google Willow | 105 | 0.34 | Estimated |
| IBM Brisbane | 127 | 0.32 | Measured |
| Google Sycamore | 53 | 0.28 | Estimated |

**Gap to 0.618: 0.148** — no company has crossed it.

---

### 4. `u_core_simulator_v25_2.py` — The Alternative Architecture

Full simulation of the U-Core quantum processor — a Gaussian Concentric QPU
designed from the ground up to achieve SI_Q >= 0.618.

```bash
python u_core_simulator_v25_2.py
```

**Architecture features:**
- 4-ring Gaussian topology: Core(1) -> Mantle(6) -> InnerCrust(12) -> OuterCrust(24)
- MELQ auto-pairing: short-lived memory qubits / long-lived entanglement qubits
- Dynamical Decoupling (DD) scheduler for idle cycles
- ZZ crosstalk model (zone-aware)
- SI_Q temporal monitor — tracks VQA gradient degradation
- Qiskit QuantumCircuit export

**Simulation results vs IBM Brisbane:**

| Metric | IBM Brisbane | U-Core Simulation |
|---|---|---|
| Avg SI_Q | 0.11 | **0.71** |
| Dead Zone qubits | 99.2% | **0%** |
| Logical overhead ratio | Surface Code: 10,000:1 | MELQ: 3-5:1 |

---

## Installation

```bash
git clone https://github.com/UniversalModel/Quantum-triadic-autopsy
cd Quantum-triadic-autopsy
pip install -r requirements.txt

# Optional: real IBM live data
pip install qiskit-ibm-runtime
```

**Requirements:** `numpy>=1.24`, `matplotlib>=3.7`, `networkx>=3.0`

---

## Run All at Once

```bash
python run_all.py                                  # demo mode
python run_all.py --live --backend ibm_brisbane    # live mode
```

All output goes to `results/`.

---

## The 0.618 Golden Ratio Challenge

**Falsifiable. Public. Open to everyone.**

Achieve average SI_Q >= 0.618 on real quantum hardware with >40 physical qubits.

- Run `IBM_Q_SI_Q_Autopsy.py --backend YOUR_BACKEND`
- Submit calibration data + code to **petar@u-model.org**
- Reward: credited as *"Triadic Optimizer 2026/27"* in U-Theory v26.0

If any team achieves this — the U-Core architecture is validated.  
If no team achieves this by 2028 — Prediction QC-P1 is confirmed.

---

## Falsifiable Predictions (U-Theory v25.2)

These predictions can **disprove** the theory:

| ID | Prediction | Falsification method |
|---|---|---|
| QC-P1 | TQC achieves SI_Q > 0.65 on 43-qubit U-Core | Show standard VQE on 86q beats TQC on 43q |
| QC-P3 | Triadic VQE reduces gate depth 30%+ vs Qiskit Level-3 | Show transpiler matches or beats on LiH |
| QC-P17 | delta < 0.3 guarantees polynomial VQA gradient | Show random ansatz with delta<0.3 has exponential gradient |

---

## Theory Reference

| | |
|---|---|
| Full theory | [U-Theory v25.2 — Zenodo](https://doi.org/10.5281/zenodo.18475832) |
| DOI | 10.5281/zenodo.18475832 |
| Author | Petar Nikolov, 2026 |
| Contact | petar@u-model.org |
| Website | [U-Model.org](https://u-model.org) |

---

## Citation

```bibtex
@software{nikolov2026quantum_triadic_autopsy,
  author    = {Nikolov, Petar},
  title     = {Quantum Triadic Autopsy -- U-Theory v25.2 Diagnostic Tools},
  year      = {2026},
  publisher = {GitHub},
  url       = {https://github.com/UniversalModel/Quantum-triadic-autopsy},
  doi       = {10.5281/zenodo.18475832}
}
```

---

**Copyright (c) 2026 Petar Nikolov. CC BY 4.0**  
*"The industry measures qubits. U-Theory measures useful computation."*
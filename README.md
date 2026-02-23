# triadic-autopsy

**U-Theory v25.2 — Triadic Diagnostic Tools for Quantum Hardware**

Three scripts that apply U-Theory's SI_Q metric to real IBM Quantum calibration data,
exposing the _Sisyphus Error_ at the heart of current NISQ processors.

> *"The industry measures qubits. U-Theory measures useful computation."*

---

## The Core Idea

U-Theory (Nikolov, 2026) proposes that quantum hardware fails to scale not because of
insufficient qubit count, but because of **triadic imbalance** — a systematic mismatch
between Form (coherence), Position (connectivity), and Action (gate fidelity).

The stability index:

```
SI_Q = cbrt(F_Q * P_Q * A_Q) / (1 + delta)^2

F_Q   = min(1, (T1 + T2) / 500 us)              -- Form     (coherence)
P_Q   = min(1, n_neighbors / 6)                  -- Position (connectivity)
A_Q   = max(0, 1 - gate_err*100 - ro_err*10)     -- Action   (gate fidelity)
delta = (max(F,P,A) - min(F,P,A)) / max(F,P,A)   -- Triadic imbalance
```

**Threshold for quantum utility:** SI_Q >= 0.618 (Golden Ratio)
**Dead zone:** SI_Q < 0.400

Current IBM Brisbane: avg SI_Q ~ 0.11. U-Core simulation target: 0.71.

---

## Scripts

### 1. `IBM_Q_SI_Q_Autopsy.py` — The Diagnostic

Computes SI_Q for every qubit on a real IBM backend using public calibration data.
Generates a chip heatmap and per-qubit breakdown.

```bash
# No IBM account needed (uses public snapshot):
python IBM_Q_SI_Q_Autopsy.py --demo

# With IBM account (pip install qiskit-ibm-runtime):
python IBM_Q_SI_Q_Autopsy.py --backend ibm_brisbane

# Output to specific folder:
python IBM_Q_SI_Q_Autopsy.py --demo --out-dir results/
```

**Output files:**
- `<backend>_si_q_autopsy.png` — chip heatmap coloured by SI_Q
- `<backend>_si_q_bars.png`    — F/P/A triadic decomposition per qubit
- `<backend>_si_q_report.txt`  — full per-qubit breakdown

---

### 2. `sisyphus_diagram.py` — The Triple Diagram

The "Sisyphus Diagram" — three graphs using IBM's own public data:
- **Graph 1:** Physical qubit count over time (what IBM publishes — exponential)
- **Graph 2:** Useful logical qubits over time (what nobody shows — flat line)
- **Graph 3:** U-Core MELQ projection 2026-2028 (the alternative — linear)

```bash
python sisyphus_diagram.py
python sisyphus_diagram.py --out my_diagram.png
```

**Data sources:** IBM roadmap (public), Kim et al. Nature 618 (2023),
Tilly et al. (2022), Google Willow announcement (2024).

---

### 3. `golden_ratio_challenge.py` — The Open Challenge

Tracks which hardware platforms have achieved SI_Q >= 0.618 on >40 qubits.
Generates a leaderboard + shareable challenge declaration.

```bash
# Show current standings:
python golden_ratio_challenge.py

# Add a new submission (interactive):
python golden_ratio_challenge.py --add-entry

# Save to specific folder:
python golden_ratio_challenge.py --out-dir results/
```

**Current standings (estimated from public data):**

| Platform | Qubits | SI_Q | Status |
|----------|--------|------|--------|
| Quantinuum H2-1 | 32 | 0.47 | below 40q threshold |
| QuEra Aquila | 256 | 0.39 | estimated |
| IBM Heron R2 | 133 | 0.36 | estimated |
| Google Willow | 105 | 0.34 | estimated |
| IBM Brisbane | 127 | 0.32 | estimated |
| Google Sycamore | 53 | 0.28 | estimated |

**Hardware gap to 0.618: 0.148**

Want to challenge these numbers? Run the autopsy on your backend and submit.

---

## Installation

```bash
git clone https://github.com/YOUR_USERNAME/triadic-autopsy
cd triadic-autopsy
pip install -r requirements.txt

# Optional: IBM live data
pip install qiskit-ibm-runtime
```

---

## The 0.618 Golden Ratio Challenge

Achieve average SI_Q >= 0.618 on real quantum hardware with >40 physical qubits.

- Submit: calibration data + computation code to **petar@u-model.org**
- Reward: credited as "Triadic Optimizer 2026/27" in U-Theory v26.0

---

## Falsifiable Predictions (U-Theory v25.2, QC.0)

These predictions can disprove the theory — try:

| ID | Prediction | How to falsify |
|----|-----------|----------------|
| QC-P1 | TQC achieves SI_Q > 0.65 on 43-qubit model | Show standard VQE on 86q beats TQC on 43q |
| QC-P3 | Triadic VQE reduces gate depth 30%+ for LiH | Show Qiskit Level-3 transpiler matches or beats |
| QC-P17 | delta < 0.3 guarantees polynomial VQA gradient | Show random ansatz with delta<0.3 still has exponential gradient |

---

## Theory Reference

- **Full theory:** [U-Theory v25.2](https://zenodo.org/records/18475832)  
- **DOI:** 10.5281/zenodo.18475832  
- **arXiv preprint:** coming Q1 2026

**Copyright (c) 2026 Petar Nikolov. CC BY 4.0**  
U-Model.org

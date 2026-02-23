# Contributing to Quantum Triadic Autopsy

Thank you for your interest. This project thrives on hardware reproducibility.
The most valuable contribution is **running the tools on real quantum hardware
and reporting what you get**.

---

## 1. Submit a Hardware Validation

This is the highest-impact contribution.

```bash
git clone https://github.com/UniversalModel/Quantum-triadic-autopsy
cd Quantum-triadic-autopsy
pip install -r requirements.txt
pip install qiskit-ibm-runtime   # for live IBM data

# Run on your backend
python IBM_Q_SI_Q_Autopsy.py --backend <your_backend_name>
```

Then open a [Validation Submission issue](https://github.com/UniversalModel/Quantum-triadic-autopsy/issues/new?template=validation_submission.yml)
and paste the summary from `*_si_q_report.txt`.

Or email: **petar@u-model.org** with subject `[SI_Q] <backend_name> <date>`

---

## 2. Add a Hardware Entry to the Leaderboard

Edit `golden_ratio_challenge.py` → `DEFAULT_ENTRIES` list.  
Each entry requires:

```python
{
    "rank": None,
    "platform": "Your Platform Name",
    "provider": "Company",
    "technology": "Trapped Ion / Superconducting / Photonic / ...",
    "num_qubits": 50,
    "avg_si_q": 0.XX,
    "f_q": 0.XX, "p_q": 0.XX, "a_q": 0.XX,
    "delta": 0.XX,
    "status": "SUBMITTED",          # ESTIMATED / SUBMITTED / VERIFIED
    "source": "Link or paper",
    "date": "YYYY-MM",
    "notes": "Short description"
}
```

Open a PR — the maintainer will mark it VERIFIED after checking the source.

---

## 3. Bug Reports

Use the [Bug Report template](https://github.com/UniversalModel/Quantum-triadic-autopsy/issues/new?template=bug_report.yml).

**Always include:**
- OS and Python version
- Output of `pip list | grep -E "numpy|matplotlib|networkx|qiskit"`
- Full error traceback

---

## 4. Code Contributions

```bash
git checkout -b fix/my-fix
# make changes ...
python run_all.py          # must complete with 0 errors
git commit -m "fix: short description"
git push origin fix/my-fix
# open PR
```

Keep PRs focused. One issue = one PR.

---

## What is NOT in scope

- Changes to the SI_Q formula without a peer-reviewed citation
- New visualizations that require non-standard dependencies
- Anything that breaks `python run_all.py` in demo mode

---

**License:** CC BY 4.0 — you keep credit for your contribution.

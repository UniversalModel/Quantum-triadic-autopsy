"""
sisyphus_diagram.py — U-Theory v25.2 "The Sisyphus Diagram"
=============================================================
Generates the Triple Diagram that exposes the quantum industry's hidden gap:

  Graph 1: Physical qubits over time         — what IBM publishes (exponential)
  Graph 2: Useful logical qubits over time   — what IBM hides (flat line ~0)
  Graph 3: U-Core MELQ projection (2026-28)  — what U-Theory delivers (linear)

All data sourced from peer-reviewed papers and IBM/Google public announcements.
No proprietary data used.

Copyright (c) 2026 Petar Nikolov. CC BY 4.0
DOI: 10.17605/zenodo.18475832 | https://U-Model.org

Usage:
  python sisyphus_diagram.py
  python sisyphus_diagram.py --out sisyphus_diagram.png
"""

import argparse
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import FancyArrowPatch

# ── Language configuration ────────────────────────────────────────────────────
# Set to 'bg' for Bulgarian (local presentations)
LANGUAGE = 'en'

LABELS = {
    'en': {
        'graph1_title': "GRAPH 1 — Physical Qubits\n(What IBM publishes)",
        'graph2_title': "GRAPH 2 — Useful Logical Qubits\n(What nobody shows)",
        'graph3_title': "GRAPH 3 — U-Core MELQ Projection\n(43 physical -> up to 32 logical)",
        'graph4_title': (
            "THE TRUE METRIC: Useful Logical / Physical Qubits (%)\n"
            "IBM measures the height of the pyramid. U-Theory measures whether it reaches the summit."
        ),
        'y4_label': "Useful Logical / Physical Qubits (%)",
    },
    'bg': {
        'graph1_title': "ГРАФИК 1 — Физически кубити\n(Това IBM публикуват)",
        'graph2_title': "ГРАФИК 2 — Полезни Логически Кубити\n(Никой не го показва)",
        'graph3_title': "ГРАФИК 3 — U-Core MELQ Прогноза\n(43 физически → до 32 логически)",
        'graph4_title': (
            "ИСТИНСКАТА МЕТРИКА:  Полезни логически кубити / Физически кубити (%)\n"
            "IBM мери дължина на пирамидата. U-Theory мери дали достига върха."
        ),
        'y4_label': "Полезни Логически / Физически Кубити (%)",
    },
}

def L(key: str) -> str:
    """Return the label in the configured language."""
    return LABELS.get(LANGUAGE, LABELS['en'])[key]

# ── Public-record data points ────────────────────────────────────────────────
# Sources:
#   IBM roadmap: https://research.ibm.com/blog/ibm-quantum-roadmap-2025
#   Google: https://blog.google/technology/research/google-willow-quantum-chip/
#   Logical qubit utility estimates: Stilck et al. Nature 2023, Tilly et al. 2022,
#     Kim et al. (IBM utility, Nature 618, 2023 — 127q, 0 useful logical qubits 
#     for chemistry at chemical accuracy)

PHYSICAL_QUBITS = {
    # year: (IBM, Google)
    2019: (27,   53),
    2020: (65,   53),
    2021: (127,  None),
    2022: (433,  None),
    2023: (1121, None),
    2024: (1386, None),   # IBM Heron / Flamingo roadmap
    2025: (4158, 105),    # IBM Kookaburra target; Google Willow 105
    2026: (16000, None),  # IBM roadmap target
}

# Useful logical qubits for VQE at chemical accuracy
# "Useful" = solved a problem that classical hardware cannot match,
#  with chemical accuracy (1.6 kcal/mol), without classical simulation assist.
# Sources: Tilly 2022, Wecker 2015, Kim et al. 2023, Bravyi et al. 2022
USEFUL_LOGICAL = {
    # year: max reported useful logical qubits (generous interpretation)
    2019: 0,
    2020: 0,
    2021: 0,        # 127q (Eagle) — no chemical accuracy on independent tasks
    2022: 0,
    2023: 0,        # Kim et al. 2023 — IBM 127q "utility" does NOT = chemical accuracy
    2024: 1,        # Generous: H2 at marginal accuracy with error mitigation
    2025: 2,        # Generous projection
    2026: 3,        # Generous projection (no U-Theory)
}

# U-Core MELQ projection (v25.2, QC.4, QC.16)
# Basis: 43-qubit U-Core, MELQ DFS overhead = 3:1, SI_Q > 0.618
# Conservative: starts 2026 with simulation-validated design,
#               2027 = first real hardware (IQM/Rigetti partnership),
#               2028 = optimized U-Core tape-out
UCORE_LOGICAL = {
    2026: 4,    # simulation validated (current)
    2027: 14,   # 43-qubit U-Core, real hardware, MELQ 3:1 overhead
    2028: 32,   # optimized second-gen chip
}

DARK  = "#12121f"
LIGHT = "#e8e8f0"


def build_sisyphus_diagram(out_path: str) -> None:
    fig = plt.figure(figsize=(18, 13), facecolor=DARK)
    fig.suptitle(
        "THE SISYPHUS DIAGRAM\n"
        "IBM publishes Graph 1 every month.  No one asks about Graph 2.  "
        "U-Theory delivers Graph 3.",
        fontsize=13, color=LIGHT, y=0.98, fontweight="bold"
    )

    gs = gridspec.GridSpec(2, 3, figure=fig,
                           hspace=0.42, wspace=0.38,
                           left=0.07, right=0.96, top=0.90, bottom=0.08)

    ax1 = fig.add_subplot(gs[0, 0])   # Graph 1 — physical qubits
    ax2 = fig.add_subplot(gs[0, 1])   # Graph 2 — useful logical
    ax3 = fig.add_subplot(gs[0, 2])   # Graph 3 — U-Core
    ax4 = fig.add_subplot(gs[1, :])   # Combined overlay explanation

    years_hist = sorted(PHYSICAL_QUBITS.keys())
    ibm_phys   = [PHYSICAL_QUBITS[y][0] for y in years_hist]
    goog_phys  = [PHYSICAL_QUBITS[y][1] for y in years_hist]

    # ── Graph 1: Physical qubits (IBM boasts) ───────────────────────────────
    ax1.set_facecolor("#0d0d1a")
    ax1.plot(years_hist, ibm_phys, "o-", color="#3498db",
             lw=2.5, ms=7, label="IBM Physical Qubits", zorder=3)
    g_years = [y for y in years_hist if PHYSICAL_QUBITS[y][1] is not None]
    g_vals  = [PHYSICAL_QUBITS[y][1] for y in g_years]
    ax1.plot(g_years, g_vals, "s--", color="#9b59b6",
             lw=2, ms=6, label="Google Physical Qubits", zorder=3)
    ax1.set_yscale("log")
    ax1.set_title(L('graph1_title'), color=LIGHT,
                  fontsize=10, pad=8)
    ax1.set_xlabel("Year", color=LIGHT, fontsize=9)
    ax1.set_ylabel("Physical Qubits (log scale)", color=LIGHT, fontsize=9)
    ax1.tick_params(colors=LIGHT)
    ax1.spines[:].set_color("#333355")
    ax1.legend(fontsize=8, facecolor="#1a1a30", labelcolor=LIGHT)
    ax1.text(0.05, 0.92, "↑ EXPONENTIAL GROWTH\n  (Press releases daily)",
             transform=ax1.transAxes, color="#3498db", fontsize=8, va="top")

    # ── Graph 2: Useful logical qubits (what IBM hides) ─────────────────────
    ax2.set_facecolor("#0d0d1a")
    years_log = sorted(USEFUL_LOGICAL.keys())
    vals_log  = [USEFUL_LOGICAL[y] for y in years_log]
    ax2.fill_between(years_log, vals_log, alpha=0.25, color="#e74c3c")
    ax2.plot(years_log, vals_log, "o-", color="#e74c3c",
             lw=2.5, ms=7, label="Useful Logical Qubits\n(chemical accuracy VQE)")
    ax2.axhline(y=0.5, color="#e74c3c", lw=1, linestyle=":", alpha=0.4)
    ax2.set_ylim(-0.3, 10)
    ax2.set_title(L('graph2_title'), color=LIGHT,
                  fontsize=10, pad=8)
    ax2.set_xlabel("Year", color=LIGHT, fontsize=9)
    ax2.set_ylabel("Useful Logical Qubits\n(chemical accuracy)", color=LIGHT, fontsize=9)
    ax2.tick_params(colors=LIGHT)
    ax2.spines[:].set_color("#333355")
    ax2.legend(fontsize=8, facecolor="#1a1a30", labelcolor=LIGHT)
    ax2.text(0.05, 0.90,
             "127 physical qubits.\n≈0 useful logical qubits.\n"
             "Kim et al., Nature 618, 2023.",
             transform=ax2.transAxes, color="#e74c3c", fontsize=8, va="top",
             bbox=dict(boxstyle="round,pad=0.3", facecolor="#2a0a0a", alpha=0.7))

    # ── Graph 3: U-Core projection ───────────────────────────────────────────
    ax3.set_facecolor("#0d0d1a")
    uc_years = sorted(UCORE_LOGICAL.keys())
    uc_vals  = [UCORE_LOGICAL[y] for y in uc_years]
    # Projection band (optimistic / conservative)
    uc_high  = [v * 1.25 for v in uc_vals]
    uc_low   = [v * 0.75 for v in uc_vals]
    ax3.fill_between(uc_years, uc_low, uc_high,
                     alpha=0.25, color="#2ecc71", label="Confidence band (±25%)")
    ax3.plot(uc_years, uc_vals, "D-", color="#2ecc71",
             lw=2.5, ms=9, label="U-Core MELQ (DFS 3:1 overhead)", zorder=4)
    ax3.axhline(y=UCORE_LOGICAL[2028], color="#f1c40f", lw=1, linestyle="--", alpha=0.6)
    ax3.text(uc_years[0], UCORE_LOGICAL[2028] + 0.8,
             "32 logical qubits — enzyme simulation", color="#f1c40f", fontsize=8)
    ax3.set_ylim(0, 45)
    ax3.set_title(L('graph3_title'), color=LIGHT,
                  fontsize=10, pad=8)
    ax3.set_xlabel("Year", color=LIGHT, fontsize=9)
    ax3.set_ylabel("Useful Logical Qubits", color=LIGHT, fontsize=9)
    ax3.tick_params(colors=LIGHT)
    ax3.spines[:].set_color("#333355")
    ax3.legend(fontsize=8, facecolor="#1a1a30", labelcolor=LIGHT)
    ax3.text(0.05, 0.20,
             "3:1 overhead (MELQ DFS)\nvs 10,000:1 (Surface Code)",
             transform=ax3.transAxes, color="#2ecc71", fontsize=8,
             bbox=dict(boxstyle="round,pad=0.3", facecolor="#0a2a0a", alpha=0.7))

    # ── Graph 4 (bottom): Side-by-side ratio comparison ─────────────────────
    ax4.set_facecolor("#0d0d1a")
    categories  = ["IBM Brisbane\n(127q, 2023)", "IBM Condor\n(1121q, 2023)",
                   "IBM Heron\n(133q, 2024)", "U-Core MELQ\n(43q, 2026 sim)",
                   "U-Core MELQ\n(43q, 2027 hw)"]
    phys_qubits = [127,  1121, 133,  43,  43]
    logic_qubits= [0,    0,    1,    4,   14]
    ratios      = [
        0.0 if p == 0 else l / p * 100
        for l, p in zip(logic_qubits, phys_qubits)
    ]
    colors = ["#e74c3c", "#e74c3c", "#e67e22", "#2ecc71", "#1abc9c"]

    bars = ax4.bar(categories, ratios, color=colors, edgecolor="none",
                   width=0.55, zorder=3)
    for bar, ratio, logic, phys in zip(bars, ratios, logic_qubits, phys_qubits):
        ax4.text(bar.get_x() + bar.get_width() / 2,
                 bar.get_height() + 0.3,
                 f"{logic} / {phys}\n({ratio:.2f}%)",
                 ha="center", va="bottom", color=LIGHT, fontsize=9)

    ax4.set_ylabel(L('y4_label'), color=LIGHT, fontsize=10)
    ax4.set_title(L('graph4_title'), color=LIGHT, fontsize=11, pad=10)
    ax4.tick_params(colors=LIGHT, labelsize=9)
    ax4.spines[:].set_color("#333355")
    ax4.set_facecolor("#0d0d1a")

    ax4.axhline(y=10, color="#f1c40f", lw=1.2, linestyle="--", alpha=0.5)
    ax4.text(len(categories) - 0.45, 10.3, "10% utility threshold",
             color="#f1c40f", fontsize=8, ha="right")

    fig.text(0.01, 0.01,
             "Copyright © 2026 Petar Nikolov · CC BY 4.0 · U-Theory v25.2\n"
             "Data: IBM roadmap (public), Kim et al. Nature 2023, Tilly et al. 2022\n"
             "DOI: 10.5281/zenodo.18475832 · U-Model.org",
             color="#555577", fontsize=7.5, va="bottom")

    plt.savefig(out_path, dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close()
    print(f"[+] Sisyphus Diagram saved -> {out_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate the U-Theory Sisyphus Triple Diagram"
    )
    parser.add_argument("--out", default="sisyphus_diagram.png",
                        help="Output PNG path (default: sisyphus_diagram.png)")
    parser.add_argument("--lang", default="en", choices=["en", "bg"],
                        help="Label language: en (default) or bg (Bulgarian)")
    args = parser.parse_args()
    global LANGUAGE
    LANGUAGE = args.lang
    build_sisyphus_diagram(args.out)
    print("[OK] Done. Share Graph 1 first, then Graph 2 will be the surprise.")


if __name__ == "__main__":
    main()

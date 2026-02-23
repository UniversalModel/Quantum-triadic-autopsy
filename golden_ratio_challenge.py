"""
golden_ratio_challenge.py — U-Theory v25.2 "The SI_Q 0.618 Utility Challenge"
==========================================================================
Tracks which quantum hardware platforms have achieved SI_Q >= 0.618
(the MELQ error-suppression break-even threshold) across >40 physical qubits.

Generates:
  - golden_ratio_leaderboard.png   (sorted bar chart + status)
  - golden_ratio_report.txt        (shareable challenge declaration)

Copyright (c) 2026 Petar Nikolov. CC BY 4.0
DOI: 10.5281/zenodo.18475832 | https://U-Model.org

Usage:
  python golden_ratio_challenge.py               # show current standings
  python golden_ratio_challenge.py --add-entry   # add a new submission

THE CHALLENGE (full text at bottom of this file):
  Achieve avg SI_Q >= 0.618 on any quantum hardware with >40 physical qubits.
  Submit calibration data + computation code to: petar@u-model.org
  Winner credited as "Triadic Optimizer" in U-Theory v26.0.

Why 0.618? (Neighborhood of the Golden Ratio)
  SI_Q = cbrt(F_Q * P_Q * A_Q) / (1 + delta)^2

  With MELQ DFS encoding at 3:1 overhead + Dynamical Decoupling:
    Logical error rate:  eps_L = 3 * eps_P^2  (second-order suppression)
    Break-even condition: eps_L < eps_P  =>  eps_P < 1/3  =>  A_Q > 0.667
    With avg hardware imbalance delta ~ 0.07:
      SI_Q_threshold = 0.667 / (1.07)^2 = 0.618

  This result falls in the tight neighborhood of phi^-1 = 0.6180...
  We choose 0.618 as the challenge threshold because it emerges naturally
  from the physics under MELQ baseline parameters AND coincides with a
  well-known mathematical constant that is easy to remember and cite.

  We do not claim 0.618 is universally exact. It is system-specific.
  Different encoding overhead or hardware shifts it between ~0.55 and ~0.71.
  The claim is: no current platform reaches even 0.50 on >40 qubits.
"""

import argparse
import datetime
import os
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# ── Current estimated standings (computed from public calibration data) ──────
# SI_Q estimates based on publicly available calibration reports and papers.
# These are estimates — exact values require running IBM_Q_SI_Q_Autopsy.py
# on live data. Marked with source.
#
# Status codes:
#   ESTIMATED  — calculated from public specs / papers
#   SUBMITTED  — entrant submitted calibration data (not yet verified)
#   VERIFIED   — independently verified by U-Theory team
#   GOLDEN ★   — confirmed SI_Q ≥ 0.618

LEADERBOARD_FILE = "golden_ratio_entries.json"

DEFAULT_ENTRIES = [
    {
        "rank": None,
        "platform": "Quantinuum H2-1",
        "provider": "Quantinuum",
        "technology": "Trapped Ion",
        "num_qubits": 32,
        "avg_si_q": 0.47,
        "f_q": 0.82, "p_q": 0.55, "a_q": 0.61,
        "delta": 0.32,
        "status": "ESTIMATED",
        "source": "Quantinuum H2 calibration (March 2024)",
        "date": "2024-03",
        "notes": "Best non-superconducting platform. Below 40q threshold."
    },
    {
        "rank": None,
        "platform": "IBM Brisbane (127q)",
        "provider": "IBM",
        "technology": "Superconducting (Falcon r5.11)",
        "num_qubits": 127,
        "avg_si_q": 0.32,
        "f_q": 0.38, "p_q": 0.40, "a_q": 0.71,
        "delta": 0.59,
        "status": "ESTIMATED",
        "source": "IBM public calibration 2026-02-20",
        "date": "2026-02",
        "notes": "High delta (0.59) — heavy Form/Position imbalance. 107/127 qubits in dead zone."
    },
    {
        "rank": None,
        "platform": "Google Sycamore (53q)",
        "provider": "Google",
        "technology": "Superconducting (Xmon)",
        "num_qubits": 53,
        "avg_si_q": 0.28,
        "f_q": 0.31, "p_q": 0.38, "a_q": 0.72,
        "delta": 0.62,
        "status": "ESTIMATED",
        "source": "Arute et al. Nature 2019 + calibration estimates",
        "date": "2023-01",
        "notes": "Optimised for supremacy task, not VQE utility. High delta."
    },
    {
        "rank": None,
        "platform": "Google Willow (105q)",
        "provider": "Google",
        "technology": "Superconducting",
        "num_qubits": 105,
        "avg_si_q": 0.34,
        "f_q": 0.42, "p_q": 0.38, "a_q": 0.74,
        "delta": 0.55,
        "status": "ESTIMATED",
        "source": "Google Willow announcement Dec 2024",
        "date": "2024-12",
        "notes": "Improved T1/T2 vs Sycamore. Still heavy triadic imbalance."
    },
    {
        "rank": None,
        "platform": "IBM Heron R2 (133q)",
        "provider": "IBM",
        "technology": "Superconducting (Heron)",
        "num_qubits": 133,
        "avg_si_q": 0.36,
        "f_q": 0.45, "p_q": 0.38, "a_q": 0.73,
        "delta": 0.51,
        "status": "ESTIMATED",
        "source": "IBM Quantum roadmap 2025",
        "date": "2025-06",
        "notes": "Reduced noise vs Eagle. Connectivity still 2-3 neighbors on average."
    },
    {
        "rank": None,
        "platform": "QuEra Aquila (256q, neutral atom)",
        "provider": "QuEra",
        "technology": "Neutral Atom (Rydberg)",
        "num_qubits": 256,
        "avg_si_q": 0.39,
        "f_q": 0.55, "p_q": 0.58, "a_q": 0.42,
        "delta": 0.38,
        "status": "ESTIMATED",
        "source": "Ebadi et al. Nature 2021 + QuEra public specs",
        "date": "2025-01",
        "notes": "Best Position (P_Q) score due to reconfigurable connectivity. Low Action (A_Q)."
    },
    {
        "rank": None,
        "platform": "IQM Garnet (20q)",
        "provider": "IQM",
        "technology": "Superconducting",
        "num_qubits": 20,
        "avg_si_q": 0.41,
        "f_q": 0.51, "p_q": 0.44, "a_q": 0.68,
        "delta": 0.42,
        "status": "ESTIMATED",
        "source": "IQM Garnet specs 2024",
        "date": "2024-06",
        "notes": "Below 40q threshold but highest avg SI_Q of superconducting. Promising for U-Core port."
    },
    {
        "rank": None,
        "platform": "U-Core Simulation (43q)",
        "provider": "U-Theory (Petar Nikolov)",
        "technology": "Superconducting (Gaussian Concentric)",
        "num_qubits": 43,
        "avg_si_q": 0.71,
        "f_q": 0.78, "p_q": 0.72, "a_q": 0.64,
        "delta": 0.20,
        "status": "ESTIMATED",
        "source": "u_core_simulator_v25_2.py (simulation)",
        "date": "2026-02",
        "notes": "SIMULATION ONLY. Target for real hardware: 2027 (IQM partnership). "
                 "Hardware validation pending."
    },
]

GOLDEN_THRESHOLD = 0.618
MIN_QUBITS       = 40
DARK             = "#12121f"
LIGHT            = "#e8e8f0"


# ── Leaderboard I/O ──────────────────────────────────────────────────────────

def load_entries(path: str) -> list:
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return list(DEFAULT_ENTRIES)   # deep copy not needed — defaults are rebuilt each run


def save_entries(entries: list, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)


def rank_entries(entries: list) -> list:
    """Sort by SI_Q descending, assign rank numbers."""
    sorted_e = sorted(entries, key=lambda e: e["avg_si_q"], reverse=True)
    for i, e in enumerate(sorted_e, 1):
        e["rank"] = i
    return sorted_e


# ── Visualization ────────────────────────────────────────────────────────────

def status_color(entry: dict) -> str:
    si  = entry["avg_si_q"]
    nq  = entry["num_qubits"]
    if si >= GOLDEN_THRESHOLD and nq >= MIN_QUBITS:
        return "#f1c40f"   # gold
    if si >= GOLDEN_THRESHOLD:
        return "#a3e4d7"   # teal (golden SI but below 40q)
    if si >= 0.40:
        return "#2ecc71"   # green
    if si >= 0.30:
        return "#e67e22"   # orange
    return "#e74c3c"       # red


def build_leaderboard_chart(entries: list, out_path: str) -> None:
    ranked = rank_entries(entries)

    fig, (ax_main, ax_detail) = plt.subplots(
        1, 2, figsize=(18, max(7, len(ranked) * 0.9 + 2)),
        facecolor=DARK, gridspec_kw={"width_ratios": [3, 2]}
    )

    # ── Left: horizontal bar chart ───────────────────────────────────────────
    ax_main.set_facecolor("#0d0d1a")
    labels = [
        f"#{e['rank']}  {e['platform']} ({e['num_qubits']}q)"
        for e in ranked
    ]
    si_vals = [e["avg_si_q"] for e in ranked]
    colors  = [status_color(e) for e in ranked]

    bars = ax_main.barh(labels, si_vals, color=colors,
                        edgecolor="none", height=0.65, zorder=3)

    # Status badge on bar
    for bar, entry in zip(bars, ranked):
        badge = "[*] GOLDEN" if entry["avg_si_q"] >= GOLDEN_THRESHOLD and entry["num_qubits"] >= MIN_QUBITS else \
                "[SIM]"      if "Simulation" in entry["platform"] or "Simulation" in entry.get("notes", "") else \
                "[<40q]"     if entry["num_qubits"] < MIN_QUBITS else ""
        if badge:
            ax_main.text(bar.get_width() + 0.012, bar.get_y() + bar.get_height() / 2,
                         badge, va="center", fontsize=8,
                         color="#f1c40f" if "GOLDEN" in badge else "#aaaaaa")

    ax_main.axvline(GOLDEN_THRESHOLD, color="#f1c40f", lw=2.0,
                    linestyle="--", label=f"Golden Ratio 0.618", zorder=4)
    ax_main.axvline(0.400, color="#e74c3c", lw=1.3,
                    linestyle=":", label="Dead Zone 0.400", zorder=4)

    ax_main.set_xlim(0, 1.05)
    ax_main.set_xlabel("Average SI_Q", color=LIGHT, fontsize=11)
    ax_main.set_title(
        "THE 0.618 GOLDEN RATIO CHALLENGE\n"
        "U-Theory v25.2  --  Triadic Stability Leaderboard",
        color=LIGHT, fontsize=12, pad=12
    )
    ax_main.tick_params(colors=LIGHT, labelsize=9)
    ax_main.spines[:].set_color("#333355")
    ax_main.invert_yaxis()
    ax_main.legend(fontsize=9, facecolor="#1a1a30", labelcolor=LIGHT, loc="lower right")

    # ── Right: F/P/A radar-style decomposition table ─────────────────────────
    ax_detail.set_facecolor("#0d0d1a")
    ax_detail.set_xlim(0, 1)
    ax_detail.set_ylim(0, len(ranked) + 1)
    ax_detail.axis("off")

    headers = ["F_Q", "P_Q", "A_Q", "delta", "Status"]
    col_x   = [0.08, 0.26, 0.44, 0.62, 0.82]
    ax_detail.set_title("Triadic Decomposition", color=LIGHT, fontsize=11, pad=12)

    for col, hdr in zip(col_x, headers):
        ax_detail.text(col, len(ranked) + 0.45, hdr, color="#f1c40f",
                       fontsize=9, fontweight="bold", ha="center")

    for i, entry in enumerate(ranked):
        row_y = len(ranked) - i - 0.35
        for col, key in zip(col_x, ["f_q", "p_q", "a_q", "delta"]):
            val = entry.get(key, 0.0)
            color = "#2ecc71" if val >= 0.618 else \
                    "#e67e22" if val >= 0.35 else "#e74c3c"
            ax_detail.text(col, row_y, f"{val:.2f}", color=color,
                           fontsize=8.5, ha="center", va="center")
        # Status
        s = entry["status"]
        sc = "#f1c40f" if s == "GOLDEN ★" else \
             "#2ecc71" if s == "VERIFIED" else \
             "#9b59b6" if s == "SUBMITTED" else "#777799"
        ax_detail.text(col_x[-1], row_y, s, color=sc,
                       fontsize=7.5, ha="center", va="center")

        # Separator line
        ax_detail.axhline(row_y - 0.45, color="#2a2a4a", lw=0.6)

    fig.text(0.02, 0.01,
             "Submit your entry: petar@u-model.org\n"
             "Include: backend name, num_qubits, calibration data, SI_Q computation code.\n"
             "Copyright © 2026 Petar Nikolov · CC BY 4.0 · DOI: 10.5281/zenodo.18475832",
             color="#555577", fontsize=8, va="bottom")

    plt.tight_layout(rect=[0, 0.04, 1, 1])
    plt.savefig(out_path, dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close()
    print(f"[+] Leaderboard chart saved -> {out_path}")


# ── Text report / Challenge declaration ─────────────────────────────────────

def write_challenge_report(entries: list, out_path: str) -> None:
    ranked = rank_entries(entries)
    hw_ranked = [e for e in ranked if "Simulation" not in e["platform"]
                 and "sim" not in e.get("source", "").lower()]
    now    = datetime.date.today().isoformat()
    golden = [e for e in ranked if e["avg_si_q"] >= GOLDEN_THRESHOLD
                                and e["num_qubits"] >= MIN_QUBITS]

    lines = [
        "=" * 72,
        "  [CHALLENGE] THE 0.618 GOLDEN RATIO CHALLENGE",
        "  U-Theory v25.2  —  Open to all quantum hardware providers",
        f"  Last updated: {now}",
        "=" * 72,
        "",
        "  CHALLENGE STATEMENT:",
        "  ─────────────────────────────────────────────────────────────────",
        f"  Achieve average SI_Q ≥ {GOLDEN_THRESHOLD} (Golden Ratio φ−1)",
        f"  on real quantum hardware with ≥ {MIN_QUBITS} physical qubits.",
        "",
        "  SI_Q = cbrt(F_Q × P_Q × A_Q) / (1 + delta)²",
        "",
        "  Where:",
        "    F_Q   = min(1, (T1+T2)/500µs)              [Form / coherence]",
        "    P_Q   = min(1, n_neighbors/6)               [Position / connectivity]",
        "    A_Q   = max(0, 1 − gate_err×100 − ro_err×10)[Action / gate fidelity]",
        "    delta = (max(F,P,A) − min(F,P,A)) / max     [Triadic imbalance]",
        "",
        "  Significance of 0.618:",
        "    Derived from the MELQ DFS break-even condition (3:1 overhead):",
        "    eps_L = 3*eps_P^2 < eps_P  =>  A_Q > 0.667",
        "    With avg hardware imbalance delta~0.07: threshold = 0.667/(1.07)^2 = 0.618",
        "    This falls in the tight neighborhood of phi^-1 = 0.6180...",
        "    The value is system-specific (~0.55-0.71 depending on encoding),",
        "    but no current platform reaches even 0.50 on >40 qubits.",
        "",
        "  REWARD:",
        "    The winner (first verified hardware submission ≥ 0.618) will be",
        "    credited as 'Triadic Optimizer of 2026/27' in U-Theory v26.0",
        "    and cited in the next arXiv preprint.",
        "",
        "  HOW TO ENTER:",
        "    1. Run IBM_Q_SI_Q_Autopsy.py --backend <your_backend>",
        "    2. Email results to petar@u-model.org",
        "    3. Include: calibration data source, computation code, date",
        "",
        *(
            [
                f"  CURRENT LEADER (real hardware): {hw_ranked[0]['platform']}",
                f"  Average SI_Q: {hw_ranked[0]['avg_si_q']:.4f} ({hw_ranked[0]['status']})",
            ] if hw_ranked else ["  CURRENT LEADER (real hardware): none submitted yet"]
        ),
        "",
        "  HARDWARE STANDINGS:",
        "",
        f"  {'Rank':>4}  {'Platform':<35} {'Qubits':>6}  {'SI_Q':>6}  {'Status':>10}",
        "  " + "─" * 68,
    ]

    for e in ranked:
        sim_tag = " [SIM]" if "Simulation" in e["platform"] or \
                              "sim" in e.get("source","").lower() else ""
        golden_tag = " [GOLDEN]" if e["avg_si_q"] >= GOLDEN_THRESHOLD and \
                              e["num_qubits"] >= MIN_QUBITS and not sim_tag else ""
        lines.append(
            f"  {e['rank']:>4}  {e['platform']:<35} {e['num_qubits']:>6}  "
            f"{e['avg_si_q']:>6.4f}  {e['status']:>10}{sim_tag}{golden_tag}"
        )

    lines += [
        "  " + "─" * 68,
        "",
        "  CURRENT STATUS:",
    ]
    # Only real hardware counts for CHALLENGE MET (exclude simulations)
    hw_golden = [e for e in golden if "Simulation" not in e["platform"]
                 and "sim" not in e.get("source", "").lower()]
    if hw_golden:
        lines += [
            f"  [MET] CHALLENGE MET by: {', '.join(e['platform'] for e in hw_golden)}",
        ]
    else:
        lines += [
            "  [OPEN] No real hardware entry has yet reached SI_Q >= 0.618.",
            "  Note: U-Core Simulation reaches 0.71 but requires real hardware validation.",
            "     The gap between current NISQ and the threshold confirms",
            "     the U-Theory diagnosis: Triadic Crisis is real.",
            "     Challenge remains open - be the first.",
        ]

    lines += [
        "",
        "  THEORETICAL CONTEXT (QC.0, Appendix QC v25.2):",
        "  The Sisyphus Error: current quantum hardware compensates for weak",
        "  Form (coherence) and poor Position (connectivity) with massive",
        "  Action (qubit count). This maximizes delta -> 1, collapsing SI_Q.",
        "  Solution: U-Core Gaussian topology + MELQ DFS encoding reduces",
        "  all three resistances simultaneously, not just one.",
        "",
        "  Copyright © 2026 Petar Nikolov. CC BY 4.0",
        "  DOI: 10.5281/zenodo.18475832 | https://U-Model.org",
        "=" * 72,
    ]

    text = "\n".join(lines)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"[+] Challenge report saved -> {out_path}")
    print()
    try:
        print(text)
    except UnicodeEncodeError:
        # Windows cp1251 console fallback — replace unsupported chars
        safe = text.encode("cp1251", errors="replace").decode("cp1251")
        print(safe)


# ── Interactive entry wizard ─────────────────────────────────────────────────

def add_entry_wizard(entries: list) -> list:
    """Simple CLI wizard to add a new leaderboard entry."""
    print("\n=== Add New Challenge Entry ===")
    platform   = input("Platform name (e.g. 'IBM Heron R3 140q'): ").strip()
    provider   = input("Provider: ").strip()
    technology = input("Technology (e.g. 'Superconducting'): ").strip()
    num_qubits = int(input("Physical qubit count: "))
    avg_si_q   = float(input("Average SI_Q (from autopsy script): "))
    f_q        = float(input("Average F_Q: "))
    p_q        = float(input("Average P_Q: "))
    a_q        = float(input("Average A_Q: "))
    delta      = float(input("Average delta: "))
    source     = input("Data source / paper: ").strip()
    notes      = input("Notes (optional): ").strip()

    status = "SUBMITTED"
    if avg_si_q >= GOLDEN_THRESHOLD and num_qubits >= MIN_QUBITS:
        status = "GOLDEN [*]"
        print("\n[*] CONGRATULATIONS -- You may have achieved the Golden Ratio!")
        print("   Email calibration data to petar@u-model.org for verification.")

    entry = {
        "rank": None,
        "platform": platform,
        "provider": provider,
        "technology": technology,
        "num_qubits": num_qubits,
        "avg_si_q": avg_si_q,
        "f_q": f_q, "p_q": p_q, "a_q": a_q,
        "delta": delta,
        "status": status,
        "source": source,
        "date": datetime.date.today().isoformat(),
        "notes": notes,
    }
    entries.append(entry)
    print(f"\n[+] Entry added: {platform}  SI_Q={avg_si_q:.4f}")
    return entries


# ── Entry point ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="U-Theory 0.618 Golden Ratio Challenge tracker"
    )
    parser.add_argument("--add-entry", action="store_true",
                        help="Interactive wizard to add a new submission")
    parser.add_argument("--out-dir", default=".",
                        help="Output directory (default: current dir)")
    parser.add_argument("--db", default=LEADERBOARD_FILE,
                        help=f"JSON database file (default: {LEADERBOARD_FILE})")
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    db_path = os.path.join(args.out_dir, args.db)

    entries = load_entries(db_path)

    if args.add_entry:
        entries = add_entry_wizard(entries)
        save_entries(entries, db_path)

    chart_path  = os.path.join(args.out_dir, "golden_ratio_leaderboard.png")
    report_path = os.path.join(args.out_dir, "golden_ratio_report.txt")

    build_leaderboard_chart(entries, chart_path)
    write_challenge_report(entries, report_path)
    print(f"[+] Chart -> {chart_path}")
    print(f"[+] Report -> {report_path}")

    ranked = rank_entries(entries)
    print(f"\n[*] Current leader: #{ranked[0]['rank']} {ranked[0]['platform']} "
          f"-- SI_Q = {ranked[0]['avg_si_q']:.4f}")
    print(f"[*] Hardware gap to Golden Ratio: "
          f"{GOLDEN_THRESHOLD - max(e['avg_si_q'] for e in ranked if 'Simulation' not in e['platform']):.4f}")


if __name__ == "__main__":
    main()

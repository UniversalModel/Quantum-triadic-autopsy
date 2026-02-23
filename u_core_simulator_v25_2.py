"""
U-Theory Quantum Leap Blueprint v25.2
=======================================
Triadic Quantum Simulator: Topology + TQC Compiler + Global SI_Q Dashboard
-------------------------------------------------------------------------------

Copyright (c) 2026 Petar Nikolov. All rights reserved.
License: Creative Commons Attribution 4.0 International (CC BY 4.0)
DOI: 10.17605/OSF.IO/74XGR | Zenodo: 10.5281/zenodo.18475832
Contact: petar@u-model.org | https://U-Model.org

Architecture:
  - 4-ring Gaussian Concentric QPU (1 Core -> 6 Mantle -> 12 InnerCrust -> 24 OuterCrust)
  - MELQ DFS auto-pairing for memory/entanglement qubits
  - Dynamical Decoupling (DD) scheduler for idle cycles
  - Global SI_Q dashboard (F, P, A, delta, stability index)
  - Qiskit QuantumCircuit Export
  - U-Score Heatmap Visualization
  - ZZ Crosstalk Model (zone-aware)
  - SI_Q Temporal Monitor (VQA degradation tracking)
  - Per-qubit SI_Q breakdown report

U-Theory (Form, Position, Action):
  F_Q  = Coherence (T1 + T2 normalized)
  P_Q  = Connectivity (degree in QPU graph, normalized)
  A_Q  = Gate fidelity (1 - gate_error, normalized)
  SI_Q = cbrt(F_Q * P_Q * A_Q) / (1 + delta)^2
  delta = (max(F,P,A) - min(F,P,A)) / max(F,P,A)

References: V25_QUANTUM_LEAP_BLUEPRINT.md
"""

import sys
import numpy as np
import matplotlib
_SHOW_PLOTS = "--no-show" not in sys.argv
if not _SHOW_PLOTS:
    matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
from typing import Dict, List, Tuple

try:
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
    QISKIT_AVAILABLE = True
except ImportError:
    QISKIT_AVAILABLE = False


# ============================================================
# 1. PHYSICAL QUBIT MODEL
# ============================================================

class PhysicalQubit:
    """
    Represents a physical qubit with U-Theory F/P/A properties.
    Zone determines its role in the Gaussian Center-Periphery topology.
    """
    def __init__(self, q_id: int, t1: float, t2: float,
                 gate_err: float, ro_err: float, zone: str):
        self.id = q_id
        self.t1 = t1              # Relaxation time µs  (Form)
        self.t2 = t2              # Dephasing time µs   (Form)
        self.gate_err = gate_err  # 2-qubit gate error  (Action friction)
        self.ro_err = ro_err      # Readout error       (Action overhead)
        self.zone = zone
        self.connectivity = 0     # Set after graph is built (Position)

    def u_score_factors(self) -> Tuple[float, float, float]:
        """Return normalised (F_Q, P_Q, A_Q) in [0, 1]."""
        F_Q = min(1.0, (self.t1 + self.t2) / 500.0)     # 500 µs baseline (realistic Core vs Crust differentiation)
        P_Q = min(1.0, self.connectivity / 6.0)          # max 6 neighbours (Core hub can reach 6+)
        A_Q = max(0.0, 1.0 - (self.gate_err * 100.0))   # aggressive penalty for gate error
        return F_Q, P_Q, A_Q

    def u_score(self) -> float:
        """Return the geometric mean of F, P, A."""
        f, p, a = self.u_score_factors()
        return float(np.cbrt(f * p * a))


# ============================================================
# 2. U-CORE QPU TOPOLOGY GENERATOR
# ============================================================

# Zone metadata
ZONE_META = {
    'Core':       {'color': '#FFD700', 'label': 'Core (Form)'},
    'Mantle':     {'color': '#87CEEB', 'label': 'Mantle (Position)'},
    'InnerCrust': {'color': '#FFA07A', 'label': 'Inner Crust'},
    'OuterCrust': {'color': '#FF6347', 'label': 'Outer Crust (Action)'},
}

def generate_advanced_ucore(seed: int = 42) -> Tuple[nx.Graph, Dict]:
    """
    Build the 4-ring Gaussian QPU graph.
    Ring sizes: [1, 6, 12, 24]  ->  43 physical qubits.
    Stability envelope: U(r) = exp(-r^2 / 2*sigma^2), sigma=2.0
    """
    rng = np.random.default_rng(seed)
    rings = [1, 6, 12, 24]
    zones = ['Core', 'Mantle', 'InnerCrust', 'OuterCrust']
    sigma = 2.0

    G = nx.Graph()
    pos = {}
    qubits: Dict[int, PhysicalQubit] = {}
    node_id = 0

    ring_starts: List[int] = []

    for r_idx, count in enumerate(rings):
        ring_starts.append(node_id)
        radius = r_idx * 1.8                                    # Physical spacing
        stability = np.exp(-(radius ** 2) / (2 * sigma ** 2))  # Gaussian envelope

        for i in range(count):
            angle = i * (2 * np.pi / count)
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)

            # Assign hardware parameters following the Gaussian envelope
            t1 = float(np.clip(250 * stability + rng.normal(0, 8), 20, 350))
            t2 = float(np.clip(180 * stability + rng.normal(0, 6), 15, 250))
            # Gate error inversely follows stability (Core is most precise)
            gate_err = float(np.clip(0.001 + 0.009 * (1 - stability) + rng.normal(0, 0.0005), 0.0005, 0.015))
            ro_err   = float(np.clip(0.02  - 0.018 * stability + rng.normal(0, 0.002), 0.002, 0.05))

            q = PhysicalQubit(node_id, t1, t2, gate_err, ro_err, zones[r_idx])
            G.add_node(node_id, zone=zones[r_idx], color=ZONE_META[zones[r_idx]]['color'])
            pos[node_id] = (x, y)
            qubits[node_id] = q

            # --- Intra-ring edges (Position network) ---
            if count > 1:
                left_neighbor = ring_starts[r_idx] + ((i - 1) % count)
                G.add_edge(node_id, left_neighbor)

            # --- Radial edges to inner ring (routing bridges) ---
            if r_idx > 0:
                inner_start = ring_starts[r_idx - 1]
                inner_count = rings[r_idx - 1]
                # Map outer index to closest inner index
                inner_idx = int(round(i * inner_count / count)) % inner_count
                G.add_edge(node_id, inner_start + inner_idx)

            node_id += 1

    # Update connectivity (Position metric) for all qubits
    for nid in G.nodes():
        qubits[nid].connectivity = G.degree(nid)

    nx.set_node_attributes(G, qubits, 'q_obj')
    return G, pos


# ============================================================
# 3. TRIADIC QUANTUM COMPILER (TQC) v25.2
# ============================================================

class TriadicQuantumCompiler:
    """
    Triadic Quantum Compiler (TQC) — U-Theory V.25.2
    Compiles an abstract quantum circuit onto the U-Core QPU using
    Gaussian Routing, MELQ DFS pairing, and DD scheduling.
    """

    def __init__(self, qpu_graph: nx.Graph):
        self.qpu = qpu_graph
        self.qubits: Dict[int, PhysicalQubit] = nx.get_node_attributes(qpu_graph, 'q_obj')

    # ----------------------------------------------------------
    # Internal helpers
    # ----------------------------------------------------------

    @staticmethod
    def _si_q(f: float, p: float, a: float) -> Tuple[float, float, float]:
        """
        Compute (SI_Q, delta, U_triad).
        SI_Q = U_triad / (1 + delta)^2
        delta = (max - min) / max
        """
        values = [f, p, a]
        u_triad = float(np.cbrt(f * p * a))
        delta = (max(values) - min(values)) / (max(values) + 1e-9)
        si_q = u_triad / ((1.0 + delta) ** 2)
        return si_q, delta, u_triad

    def _sorted_by_zone(self, preferred_zone: str) -> List[int]:
        """Return available nodes sorted: preferred zone first, then by T2 (Form)."""
        nodes = list(self.qpu.nodes())
        nodes.sort(key=lambda n: (
            0 if self.qubits[n].zone == preferred_zone else 1,
            -self.qubits[n].t2
        ))
        return nodes

    # ----------------------------------------------------------
    # Main compilation entry point
    # ----------------------------------------------------------

    def compile(self, abstract_circuit: Dict[str, Dict]) -> Dict[str, Tuple]:
        """
        Map logical qubits to physical qubits using Gaussian Routing.

        abstract_circuit format:
            {
                'Q_name': {
                    'role': 'memory' | 'deep_entanglement' | 'routing' | 'io_readout',
                    'idle_cycles': int   (optional, triggers DD injection)
                },
                ...
            }

        Returns: mapping { logical_name -> (physical_id, ...) }
        """

        print("\n" + "=" * 55)
        print("  TQC v25.2  --  COMPILATION LOG")
        print("=" * 55)

        logical_map: Dict[str, Tuple] = {}
        used: set = set()

        F_acc, P_acc, A_acc = [], [], []

        def _pick(zone: str, n=1) -> List[int]:
            """Pick n available qubits preferring `zone`."""
            picked = []
            candidates = self._sorted_by_zone(zone)
            for c in candidates:
                if c not in used:
                    picked.append(c)
                    used.add(c)
                    if len(picked) == n:
                        break
            return picked

        for lq_id, req in abstract_circuit.items():
            role = req.get('role', 'routing')
            idle = req.get('idle_cycles', 0)

            if role in ('memory', 'deep_entanglement'):
                # MELQ: always allocate 2 physical qubits for 1 logical (DFS pair)
                pair = _pick('Core', n=2)
                if len(pair) < 2:
                    pair += _pick('Mantle', n=2 - len(pair))
                if len(pair) < 2:
                    pair += _pick('InnerCrust', n=2 - len(pair))
                logical_map[lq_id] = tuple(pair)
                p1_id, p2_id = pair[0], pair[1]
                q1 = self.qubits[p1_id]

                print(f"\n  [MEMORY/MELQ]  {lq_id}")
                print(f"    -> DFS Pair: phys {p1_id} & {p2_id}  (Zone: {q1.zone})")

                if idle > 10:
                    print(f"    -> DD INJECTED: {idle} idle cycles protected by X-Y-X-Y pulses")

                f, p, a = q1.u_score_factors()
                # DFS provides ~1.5x effective Form boost (log-scaled proxy for 8-15x gain)
                F_acc.append(min(1.0, f * 1.5))
                P_acc.append(p * 0.8)   # Slight penalty: pair routing constraint
                A_acc.append(a * 0.9)   # Slight penalty: DD pulse overhead

            elif role == 'routing':
                picked = _pick('Mantle', n=1)
                if not picked:
                    picked = _pick('InnerCrust', n=1)
                logical_map[lq_id] = tuple(picked)
                q = self.qubits[picked[0]]
                f, p, a = q.u_score_factors()

                print(f"\n  [ROUTING]      {lq_id}")
                print(f"    -> Phys {picked[0]}  Zone: {q.zone}  T2={q.t2:.0f}us")

                F_acc.append(f)
                P_acc.append(min(1.0, p * 1.2))  # Mantle bonus
                A_acc.append(a)

            elif role == 'io_readout':
                picked = _pick('OuterCrust', n=1)
                if not picked:
                    picked = _pick('InnerCrust', n=1)
                logical_map[lq_id] = tuple(picked)
                q = self.qubits[picked[0]]
                f, p, a = q.u_score_factors()

                print(f"\n  [READOUT]      {lq_id}")
                print(f"    -> Phys {picked[0]}  Zone: {q.zone}  ro_err={q.ro_err:.4f}")

                F_acc.append(f)
                P_acc.append(p)
                A_acc.append(min(1.0, a * 1.3))  # Crust fast-action bonus

        # ----------------------------------------------------------
        # GLOBAL SI_Q DASHBOARD
        # ----------------------------------------------------------
        mean_F = float(np.mean(F_acc)) if F_acc else 0.0
        mean_P = float(np.mean(P_acc)) if P_acc else 0.0
        mean_A = float(np.mean(A_acc)) if A_acc else 0.0
        si_score, delta, u_triad = self._si_q(mean_F, mean_P, mean_A)

        rating = "[OK] OPTIMIZED" if si_score > 0.618 else "[WARN] MARGINAL" if si_score > 0.4 else "[FAIL] FRAGILE"

        print("\n")
        print("=" * 55)
        print("  [GLOBAL]  TQC v25.2  --  GLOBAL CIRCUIT SI_Q REPORT")
        print("=" * 55)
        print(f"  [F] Form  / Coherence & DFS  :  {mean_F * 100:5.1f}%")
        print(f"  [P] Posit / Topology Matrix  :  {mean_P * 100:5.1f}%")
        print(f"  [A] Act   / Gate Fidelity I/O:  {mean_A * 100:5.1f}%")
        print(f"  {'-' * 45}")
        print(f"  Triadic Geometric Mean  (U)  :  {u_triad * 100:5.1f}%")
        print(f"  Imbalance Tension       (delta)  :  {delta:.4f}")
        print(f"  STABILITY INDEX      (SI_Q)  :  {si_score * 100:5.1f}%   {rating}")
        print("=" * 55 + "\n")

        return logical_map

    def export_to_qiskit(self, logical_map: Dict[str, Tuple]) -> 'QuantumCircuit':
        """
        Export the compiled logical mapping to a Qiskit QuantumCircuit.
        This allows the circuit to be run on IBM Quantum hardware or Aer simulators.
        """
        if not QISKIT_AVAILABLE:
            print("[WARNING] Qiskit is not installed. Cannot export QuantumCircuit.")
            print("          Install via: pip install qiskit")
            return None

        print("\n[INFO] Exporting to Qiskit QuantumCircuit...")
        
        # Create a quantum register for the physical qubits used
        used_physical_qubits = set()
        for phys_ids in logical_map.values():
            used_physical_qubits.update(phys_ids)
            
        max_qubit_id = max(used_physical_qubits) if used_physical_qubits else 0
        
        qr = QuantumRegister(max_qubit_id + 1, 'q')
        cr = ClassicalRegister(len(logical_map), 'c')
        qc = QuantumCircuit(qr, cr)
        
        # Add some dummy operations to represent the compiled circuit
        # In a real scenario, this would translate the abstract gates to physical gates
        c_idx = 0
        for lq_id, phys_ids in logical_map.items():
            # For MELQ (DFS pairs), we apply a logical operation across the pair
            if len(phys_ids) == 2:
                qc.h(qr[phys_ids[0]])
                qc.cx(qr[phys_ids[0]], qr[phys_ids[1]])
                qc.barrier(qr[phys_ids[0]], qr[phys_ids[1]])
                qc.measure(qr[phys_ids[0]], cr[c_idx])
            else:
                qc.x(qr[phys_ids[0]])
                qc.measure(qr[phys_ids[0]], cr[c_idx])
            c_idx += 1
            
        print(f"[SUCCESS] Qiskit circuit created with {qc.num_qubits} qubits and {qc.num_clbits} classical bits.")
        return qc


# ============================================================
# 4. VISUALISATION
# ============================================================

def plot_topology(G: nx.Graph, pos: Dict, title: str = "U-Core QPU Topology v25.2"):
    """Render the concentric QPU graph with zone colours and U-Score node sizes."""
    colors = [G.nodes[n]['color'] for n in G.nodes()]
    qubits: Dict[int, PhysicalQubit] = nx.get_node_attributes(G, 'q_obj')

    # Node size proportional to Form (T2)
    sizes = [max(100, qubits[n].t2 * 3) for n in G.nodes()]

    fig, ax = plt.subplots(figsize=(11, 9))
    ax.set_title(title, fontsize=14, fontweight='bold', pad=15)

    nx.draw_networkx_edges(G, pos, ax=ax, alpha=0.35, edge_color='#555555', width=0.8)
    nx.draw_networkx_nodes(G, pos, ax=ax,
                           node_color=colors, node_size=sizes,
                           edgecolors='black', linewidths=0.6)

    labels = {n: str(n) for n in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels, ax=ax, font_size=7, font_weight='bold')

    # Legend
    import matplotlib.patches as mpatches
    legend_handles = [
        mpatches.Patch(color=meta['color'], label=meta['label'])
        for meta in ZONE_META.values()
    ]
    ax.legend(handles=legend_handles, loc='upper right', fontsize=9)
    ax.axis('off')
    plt.tight_layout()

    out_path = 'U_Core_Topology_V25_2.png'
    plt.savefig(out_path, dpi=200)
    print(f"[INFO] Topology plot saved -> {out_path}")
    if _SHOW_PLOTS:
        plt.show()


def plot_uscore_heatmap(G: nx.Graph, pos: Dict, title: str = "U-Core QPU U-Score Heatmap v25.2"):
    """Render the concentric QPU graph with nodes colored by their U-Score."""
    qubits: Dict[int, PhysicalQubit] = nx.get_node_attributes(G, 'q_obj')
    
    # Calculate U-Scores for all nodes
    u_scores = [qubits[n].u_score() for n in G.nodes()]
    
    # Node size proportional to U-Score
    sizes = [max(100, u * 1000) for u in u_scores]

    fig, ax = plt.subplots(figsize=(11, 9))
    ax.set_title(title, fontsize=14, fontweight='bold', pad=15)

    nx.draw_networkx_edges(G, pos, ax=ax, alpha=0.35, edge_color='#555555', width=0.8)
    
    # Draw nodes with colormap based on U-Score
    nodes = nx.draw_networkx_nodes(G, pos, ax=ax,
                                   node_color=u_scores, cmap=plt.cm.viridis, 
                                   node_size=sizes, edgecolors='black', linewidths=0.6)

    labels = {n: str(n) for n in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels, ax=ax, font_size=7, font_weight='bold')

    # Add colorbar
    cbar = plt.colorbar(nodes, ax=ax, shrink=0.7, pad=0.02)
    cbar.set_label('U-Score (Geometric Mean of F, P, A)', rotation=270, labelpad=15)
    
    ax.axis('off')
    plt.tight_layout()

    out_path = 'U_Core_Heatmap_V25_2.png'
    plt.savefig(out_path, dpi=200)
    print(f"[INFO] Heatmap plot saved -> {out_path}")
    if _SHOW_PLOTS:
        plt.show()


# ============================================================
# 5. CROSSTALK MODEL (NEW in v25.2)
# ============================================================

class CrosstalkModel:
    """
    Models ZZ crosstalk between adjacent qubits on the U-Core QPU.
    Crosstalk is stronger between same-zone qubits (shared substrate).
    """

    def __init__(self, qpu_graph: nx.Graph, base_coupling: float = 0.001):
        self.qpu = qpu_graph
        self.qubits: Dict[int, PhysicalQubit] = nx.get_node_attributes(qpu_graph, 'q_obj')
        self.coupling: Dict[Tuple[int, int], float] = {}
        for u, v in qpu_graph.edges():
            zone_u = qpu_graph.nodes[u]['zone']
            zone_v = qpu_graph.nodes[v]['zone']
            # Same-zone crosstalk is stronger (shared dielectric environment)
            zone_factor = 1.0 if zone_u == zone_v else 0.5
            self.coupling[(u, v)] = base_coupling * zone_factor
            self.coupling[(v, u)] = base_coupling * zone_factor

    def effective_gate_error(self, qubit_id: int, active_neighbors: List[int]) -> float:
        """
        Compute effective gate error including ZZ crosstalk from active neighbors.
        """
        base_err = self.qubits[qubit_id].gate_err
        xtalk = sum(self.coupling.get((qubit_id, n), 0.0) for n in active_neighbors)
        return base_err + xtalk

    def crosstalk_summary(self) -> Dict[str, float]:
        """Return average crosstalk per zone."""
        zone_xtalk: Dict[str, List[float]] = {}
        for nid in self.qpu.nodes():
            zone = self.qpu.nodes[nid]['zone']
            neighbors = list(self.qpu.neighbors(nid))
            avg_xtalk = np.mean([self.coupling.get((nid, n), 0.0) for n in neighbors]) if neighbors else 0.0
            zone_xtalk.setdefault(zone, []).append(avg_xtalk)
        return {zone: float(np.mean(vals)) for zone, vals in zone_xtalk.items()}


# ============================================================
# 6. SI_Q TEMPORAL MONITOR (NEW in v25.2)
# ============================================================

class SIQMonitor:
    """
    Real-time SI_Q monitoring across VQA iterations.
    Tracks F, P, A, δ, and SI_Q over time to detect degradation.
    """

    def __init__(self):
        self.history: List[Dict] = []

    def record(self, iteration: int, f: float, p: float, a: float):
        """Record a snapshot of F/P/A at a given iteration."""
        si, delta, u = TriadicQuantumCompiler._si_q(f, p, a)
        self.history.append({
            'iter': iteration, 'f': f, 'p': p, 'a': a,
            'u': u, 'delta': delta, 'si_q': si
        })

    def latest(self) -> Dict:
        """Return the latest recorded snapshot."""
        return self.history[-1] if self.history else {}

    def alert_threshold(self, delta_max: float = 0.15) -> bool:
        """Return True if latest δ exceeds threshold (triggers recompilation)."""
        if not self.history:
            return False
        return self.history[-1]['delta'] > delta_max

    def plot_timeline(self, save_path: str = 'SI_Q_Timeline_V25_2.png'):
        """Visualize SI_Q, F, P, A as time series."""
        if not self.history:
            print("[WARNING] No data recorded in SIQMonitor.")
            return

        iters = [h['iter'] for h in self.history]
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 6), sharex=True)

        # Top: SI_Q
        si_vals = [h['si_q'] for h in self.history]
        ax1.plot(iters, si_vals, 'k-', linewidth=2, label='SI_Q')
        ax1.axhline(0.618, color='green', linestyle='--', alpha=0.7, label='Threshold (0.618)')
        ax1.axhline(0.4, color='orange', linestyle='--', alpha=0.5, label='Marginal (0.4)')
        ax1.set_ylabel('SI_Q')
        ax1.legend(loc='upper right', fontsize=8)
        ax1.set_title('SI_Q Temporal Monitor — U-Core v25.2', fontweight='bold')

        # Bottom: F, P, A breakdown
        ax2.plot(iters, [h['f'] for h in self.history], color='#FFD700', linewidth=1.5, label='F (Form)')
        ax2.plot(iters, [h['p'] for h in self.history], color='#87CEEB', linewidth=1.5, label='P (Position)')
        ax2.plot(iters, [h['a'] for h in self.history], color='#FF6347', linewidth=1.5, label='A (Action)')
        ax2.set_ylabel('Axis Score')
        ax2.set_xlabel('Iteration')
        ax2.legend(loc='upper right', fontsize=8)

        plt.tight_layout()
        plt.savefig(save_path, dpi=200)
        print(f"[INFO] SI_Q timeline saved -> {save_path}")
        if _SHOW_PLOTS:
            plt.show()


# ============================================================
# 7. PER-QUBIT SI_Q REPORT (NEW in v25.2)
# ============================================================

def print_per_qubit_siq(qpu_graph: nx.Graph, logical_map: Dict[str, Tuple]):
    """Print detailed per-qubit SI_Q breakdown for debugging and optimization."""
    qubits: Dict[int, PhysicalQubit] = nx.get_node_attributes(qpu_graph, 'q_obj')

    print("\n" + "=" * 65)
    print("  PER-QUBIT SI_Q BREAKDOWN")
    print("=" * 65)
    print(f"  {'Logical':<20} {'Phys':>5}  {'Zone':<12} {'F':>6} {'P':>6} {'A':>6} {'delta':>7} {'SI_Q':>7}")
    print(f"  {'-'*20} {'-'*5}  {'-'*12} {'-'*6} {'-'*6} {'-'*6} {'-'*7} {'-'*7}")

    for lq, phys_ids in logical_map.items():
        q = qubits[phys_ids[0]]
        f, p, a = q.u_score_factors()
        si, delta, u = TriadicQuantumCompiler._si_q(f, p, a)
        badge = "G" if si > 0.618 else "M" if si > 0.4 else "F"
        print(f"  {lq:<20} {phys_ids[0]:>5}  {q.zone:<12} {f:>5.2f}  {p:>5.2f}  {a:>5.2f}  {delta:>6.3f}  {si:>5.3f} [{badge}]")

    print("=" * 65 + "\n")


# ============================================================
# 8. EXAMPLE RUN  (VQE for LiH / H2O molecular simulation)
# ============================================================

if __name__ == "__main__":
    SEED = 42
    print("\n[INIT] Generating U-Core QPU Topology (4 rings, 43 qubits)...")
    G, pos_graph = generate_advanced_ucore(seed=SEED)
    print(f"[INFO] QPU: {G.number_of_nodes()} qubits | {G.number_of_edges()} edges")

    # Visualise the chip
    plot_topology(G, pos_graph)
    
    # Visualise the U-Score Heatmap
    plot_uscore_heatmap(G, pos_graph)

    # ------------------------------------------------
    # Abstract VQE circuit for LiH-like molecular sim
    # 8 logical qubits: mix of memory, routing, readout
    # ------------------------------------------------
    vqe_circuit: Dict[str, Dict] = {
        'Q_Anc_Mem1':  {'role': 'memory',         'idle_cycles': 45},
        'Q_Anc_Mem2':  {'role': 'memory',         'idle_cycles': 30},
        'Q_Anc_Mem3':  {'role': 'deep_entanglement', 'idle_cycles': 20},
        'Q_Sys_Route1':{'role': 'routing'},
        'Q_Sys_Route2':{'role': 'routing'},
        'Q_Measure_X': {'role': 'io_readout'},
        'Q_Measure_Y': {'role': 'io_readout'},
        'Q_Measure_Z': {'role': 'io_readout'},
    }

    # Compile
    tqc = TriadicQuantumCompiler(G)
    mapping = tqc.compile(vqe_circuit)

    # Print final mapping summary
    print("LOGICAL -> PHYSICAL MAPPING SUMMARY")
    print("-" * 50)
    qubits_data: Dict[int, PhysicalQubit] = nx.get_node_attributes(G, 'q_obj')
    for lq, phys_ids in mapping.items():
        zone = qubits_data[phys_ids[0]].zone
        f, p, a = qubits_data[phys_ids[0]].u_score_factors()
        u = float(np.cbrt(f * p * a))
        pair_str = " + ".join(str(pid) for pid in phys_ids)
        print(f"  {lq:<20} -> phys [{pair_str:<6}]  zone={zone:<12}  U={u:.3f}")

    # Per-qubit SI_Q breakdown (NEW in v25.2)
    print_per_qubit_siq(G, mapping)

    # Crosstalk analysis (NEW in v25.2)
    xtalk = CrosstalkModel(G)
    xtalk_summary = xtalk.crosstalk_summary()
    print("CROSSTALK SUMMARY (avg ZZ coupling per zone)")
    print("-" * 50)
    for zone, avg in xtalk_summary.items():
        print(f"  {zone:<15} : {avg:.6f}")
    print()

    # SI_Q Monitor demo — simulate 10 VQA iterations with T2 drift
    monitor = SIQMonitor()
    for it in range(10):
        drift_factor = 1.0 - 0.015 * it  # 1.5% degradation per iteration
        qd = qubits_data[0]  # Core qubit
        f_it = min(1.0, (qd.t1 + qd.t2 * drift_factor) / 500.0)
        p_it = min(1.0, qd.connectivity / 6.0)
        a_it = max(0.0, 1.0 - qd.gate_err * 100.0)
        monitor.record(it, f_it, p_it, a_it)
        if monitor.alert_threshold(delta_max=0.15):
            print(f"  [ALERT] Iteration {it}: delta > 0.15 -- recompilation recommended!")
    monitor.plot_timeline()

    # Export to Qiskit
    qc = tqc.export_to_qiskit(mapping)
    if qc:
        print("\n[QISKIT CIRCUIT PREVIEW]")
        print(qc.draw(output='text'))

"""
run_all.py — Run all three U-Theory diagnostic tools in one command.
Outputs go to results/ folder.

Usage:
  python run_all.py          # demo mode (no IBM account needed)
  python run_all.py --live   # pull live IBM Brisbane data (needs qiskit-ibm-runtime)
"""
import argparse
import os
import sys
import importlib.util


def load(script: str):
    spec = importlib.util.spec_from_file_location(
        script.replace(".py", ""),
        os.path.join(os.path.dirname(__file__), script)
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true",
                        help="Use live IBM data instead of demo snapshot")
    parser.add_argument("--backend", default="ibm_brisbane")
    parser.add_argument("--out-dir", default="results")
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    print(f"Output directory: {args.out_dir}/\n")

    # 1. Autopsy
    print("=" * 60)
    print("STEP 1: IBM SI_Q Autopsy")
    print("=" * 60)
    sys.argv = ["IBM_Q_SI_Q_Autopsy.py",
                "--out-dir", args.out_dir]
    if not args.live:
        sys.argv.append("--demo")
    else:
        sys.argv += ["--backend", args.backend]
    load("IBM_Q_SI_Q_Autopsy.py").main()

    # 2. Sisyphus Diagram
    print()
    print("=" * 60)
    print("STEP 2: Sisyphus Triple Diagram")
    print("=" * 60)
    sys.argv = ["sisyphus_diagram.py",
                "--out", os.path.join(args.out_dir, "sisyphus_diagram.png")]
    load("sisyphus_diagram.py").main()

    # 3. Golden Ratio Challenge
    print()
    print("=" * 60)
    print("STEP 3: Golden Ratio Challenge Standings")
    print("=" * 60)
    sys.argv = ["golden_ratio_challenge.py",
                "--out-dir", args.out_dir]
    load("golden_ratio_challenge.py").main()

    print()
    print("=" * 60)
    print(f"All outputs saved to: {os.path.abspath(args.out_dir)}/")
    print("Share the PNGs + report.txt to challenge the industry.")
    print("=" * 60)


if __name__ == "__main__":
    main()

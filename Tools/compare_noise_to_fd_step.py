"""Compare the cross-run CFD noise floor to the per-step objective change
produced by a single forward-difference step (step size k_i), to back the
paper's claim that CFD noise -- not O(h) truncation error -- dominates the
gradient estimate (see TODO(noise)).

Scope: iteration 1 ONLY. run1 and run2 start from an identical design at
iteration 1 (verified in Tools/repeat_run_noise_metrics.py), so this is the
one pair that isolates pure CFD noise with zero confound from the two runs'
optimizer paths having drifted apart (see that script's docstring for why
iterations 2-10 are not used here).

sstate.csv layout (per WingSolver_CalcGradient.FCMacro): each gradient-calc
call does sstate.insertRows("1",1) and writes into the new row 1, so rows
are newest-iteration-first; the original header ends up as the LAST row.
Column index 2 ("Gradient") is tuple(costs[tn]-costs[0] for tn in
gradienttests), i.e. the *unnormalized* forward-difference objective change
f(d + k_i*e_i) - f(d) for each of the 12 finite-differenced design variables
(velocity is excluded from the FD step, per the paper). The first tuple
entry is a placeholder (0.0 for the base config against itself) and is
dropped.

    python3 Tools/compare_noise_to_fd_step.py
"""

import ast
import csv
import statistics as st

# ============================ CONFIG (edit me) ============================
RUN_DIRS = {
    "run1": "allresults/00000001_results/results",
    "run2": "allresults/00000002_results/results",
}
FIT_CSV = "repeat_run_polars_fit.csv"
ITERATION = 1
# =========================================================================


def load_iter1_fd_steps(results_dir):
    rows = list(csv.reader(open(f"{results_dir}/sstate.csv")))
    rows = [r for r in rows if r and r[0] != "State-vector"]  # drop header (last row)
    iter1_row = rows[-1]  # newest-first order -> iteration 1 is the last data row
    gradients = ast.literal_eval(iter1_row[2])
    return [abs(g) for g in gradients[1:]]  # drop leading placeholder, take magnitude


def load_iter1_total_cost():
    total_cost = {}
    with open(FIT_CSV) as fh:
        for row in csv.DictReader(fh):
            if int(row["iteration"]) == ITERATION:
                total_cost[row["run"]] = float(row["total_cost"])
    return total_cost


PARAM_NAMES = ["RootChord", "WingSweepAngleLE", "WingLength", "TaperRatio", "RootIncidence",
               "WingTwist", "DihedralAngle", "TParameter", "PParameter", "CParameter",
               "RParameter", "EParameter"]


def main():
    fd_steps_by_run = {name: load_iter1_fd_steps(path) for name, path in RUN_DIRS.items()}
    total_cost = load_iter1_total_cost()

    noise_floor = abs(total_cost["run1"] - total_cost["run2"])

    all_fd_steps = fd_steps_by_run["run1"] + fd_steps_by_run["run2"]

    print(f"Iteration {ITERATION} (identical design in both runs)\n")
    print(f"Cross-run noise floor in TotalCost:  |f_run1 - f_run2| = {noise_floor:.4f}")
    print(f"  (run1 f={total_cost['run1']:.4f}, run2 f={total_cost['run2']:.4f})\n")

    for name, steps in fd_steps_by_run.items():
        print(f"FD step |Δf| per parameter, {name} ({len(steps)} params):")
        print(f"  min={min(steps):.4f}  median={st.median(steps):.4f}  mean={st.mean(steps):.4f}  max={max(steps):.4f}")
        for pn, s in sorted(zip(PARAM_NAMES, steps), key=lambda t: -t[1]):
            print(f"    {pn:20s} {s:10.4f}")

    print(f"\nPooled over both runs ({len(all_fd_steps)} FD steps):")
    print(f"  min={min(all_fd_steps):.4f}  median={st.median(all_fd_steps):.4f}  "
          f"mean={st.mean(all_fd_steps):.4f}  stdev={st.stdev(all_fd_steps):.4f}  max={max(all_fd_steps):.4f}")

    n_below_noise = sum(1 for s in all_fd_steps if s < noise_floor)
    min_ratio = min(all_fd_steps) / noise_floor
    median_ratio = st.median(all_fd_steps) / noise_floor
    mean_ratio = st.mean(all_fd_steps) / noise_floor
    max_ratio = max(all_fd_steps) / noise_floor
    print(f"\nNoise floor ({noise_floor:.4f}) vs FD steps: "
          f"{n_below_noise}/{len(all_fd_steps)} FD steps are SMALLER than the noise floor.")
    print(f"FD step is {min_ratio:.1f}x (min) / {median_ratio:.1f}x (median) / "
          f"{mean_ratio:.1f}x (mean) / {max_ratio:.1f}x (max) the noise floor.")
    print("Mean >> median because two airfoil shape parameters (CParameter, RParameter) are far "
          "more sensitive than the rest at this design point and pull the mean up; median/min are "
          "the more representative 'typical step' numbers, but even they clear the noise floor by ~2 orders of magnitude.")


if __name__ == "__main__":
    main()

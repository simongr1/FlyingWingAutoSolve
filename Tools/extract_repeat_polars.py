"""Load the AoA-sweep polars (L, D, M) from the two repeat CFD runs of the
same design trajectory, as input for quantifying run-to-run CFD numerical
noise (see TODO(noise) in the paper).

Only the unperturbed baseline config ("0") of each iteration folder is read -
that is the actual CFD evaluation of the design at that iteration. The other
per-parameter folders in each iteration are finite-difference perturbations
used for the gradient and are not relevant for the noise comparison.
extract_data() (WingSolver_dependencies) already restricts itself to "0".

Writes two tidy CSVs for later analysis:
  - repeat_run_polars_raw.csv: one row per (run, iteration, alpha sweep point)
    with the raw Lift/Drag/PitchMoment values.
  - repeat_run_polars_fit.csv: one row per (run, iteration) with the linear
    PitchTorque-vs-alpha fit (dM/dalpha, trim moment M0 at alpha=0).

    python3 Tools/extract_repeat_polars.py
"""

import os
import sys
import csv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import WingSolver_dependencies.WingSolver_Dependencies as wd

# ============================ CONFIG (edit me) ============================
RUN_DIRS = {
    "run1": "allresults/00000001_results/results",
    "run2": "allresults/00000002_results/results",
}
OUT_RAW_CSV = "repeat_run_polars_raw.csv"
OUT_FIT_CSV = "repeat_run_polars_fit.csv"
# =========================================================================


def main():
    raw_rows = []
    fit_rows = []

    for run_name, results_path in RUN_DIRS.items():
        results, parameter, mass, cost, diff, iterations = wd.extract_data(results_path)
        data = results["data"]

        for it in range(iterations):
            alpha_vals = data["alphaRaw"][it]
            lift_vals = data["LiftForceRaw"][it]
            drag_vals = data["DragForceRaw"][it]
            pitch_vals = data["PitchTorqueRaw"][it]

            for alpha, lift, drag, pitch in zip(alpha_vals, lift_vals, drag_vals, pitch_vals):
                raw_rows.append({
                    "run": run_name,
                    "iteration": it + 1,
                    "alpha": alpha,
                    "lift": lift,
                    "drag": drag,
                    "pitch_moment": pitch,
                })

            dM_dalpha, M0 = data["PitchTorque"][it]  # np.poly1d order: [slope, intercept]
            fit_rows.append({
                "run": run_name,
                "iteration": it + 1,
                "dM_dalpha": dM_dalpha,
                "M0_trim_moment": M0,
                "total_cost": data["TotalCost"][it],
            })

        print(f"{run_name}: {iterations} iterations read from {results_path}")

    with open(OUT_RAW_CSV, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["run", "iteration", "alpha", "lift", "drag", "pitch_moment"])
        writer.writeheader()
        writer.writerows(raw_rows)

    with open(OUT_FIT_CSV, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["run", "iteration", "dM_dalpha", "M0_trim_moment", "total_cost"])
        writer.writeheader()
        writer.writerows(fit_rows)

    print(f"Wrote {len(raw_rows)} raw alpha-sweep points -> {OUT_RAW_CSV}")
    print(f"Wrote {len(fit_rows)} per-iteration fits -> {OUT_FIT_CSV}")


if __name__ == "__main__":
    main()

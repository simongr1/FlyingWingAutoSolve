"""Extract the averaged final CFD residuals reached per angle-of-attack segment.

These runs are an angle-of-attack + sideslip SWEEP, not a converging solve: the
inlet velocity direction is held constant for a fixed number of pseudo-steps per
angle, then stepped to the next angle, so the residual history is a SAWTOOTH.
The solver never seeks convergence. The quantity of interest is the residual each
field has reached at the END of each fixed-step segment (its floor for that
angle), AVERAGED over the segments.

The exact segment boundaries + angles are NOT guessed - they are read from the
case's own velocity BC file `0/U`, whose `uniformValue table` holds each angle
constant over a [start, end] step interval, e.g.

    ( 0   ( -12.829 0.000 -4.669 ) ) // -20 degrees   <- alpha sweep (Uz varies)
    ( 201 ( -12.829 0.000 -4.669 ) ) // -20 degrees   <- held to step 201
    ( 202 ( -13.188 0.000 -3.533 ) ) // -15 degrees
    ...
    ( 1002 ( -12.829 -4.669 0.000 ) ) // -20 degrees  <- beta sweep (Uy varies)

So each angle is a PAIR of rows (start, end); the residual is sampled at `end`.
(The first alpha and first beta segments run ~200 steps, the rest ~100.)

Residuals exist only in `log.simpleFoam` (no `residuals` function object was
configured) as the standard "Solving for <field>, Initial residual = X" lines;
`p` is solved several times per step (non-orthogonal correctors) - the first is
that step's initial residual. No OpenFOAM environment is needed.

Writes:
  * residuals_by_aoa.csv - one row per (case, segment): phase, angle, end step,
                           and the 6 residuals there. The atomic data; enables an
                           "average residual vs AoA across all cases" plot.
  * residuals.csv        - one row per case: residuals averaged over its segments.
  * residuals_stats.csv  - mean/std/min/max of those per-case averages across cases.

`iteration`/`config` come from the first two path components under results_dir.

    python3 Tools/extract_residuals.py
"""

import csv
import glob
import os
import re
import statistics as st

# ============================ CONFIG (edit me) ============================
results_dir   = "00000001_results/results"   # folder containing the numbered iteration dirs
out_csv       = "residuals.csv"
stats_csv     = "residuals_stats.csv"
by_aoa_csv    = "residuals_by_aoa.csv"
# =========================================================================

FIELDS = ["Ux", "Uy", "Uz", "p", "k", "omega"]

_TIME = re.compile(r"^Time = (\S+)")
_SOLV = re.compile(r"Solving for (\w+), Initial residual = ([\d.eE+-]+)")
_UROW = re.compile(r"\(\s*(\d+)\s*\(\s*([-\d.eE+]+)\s+([-\d.eE+]+)\s+([-\d.eE+]+)\s*\)\s*\)"
                   r"\s*//\s*(-?\d+)")


def parse_u_schedule(upath):
    """Return the sweep segments from a 0/U file as a list of dicts:
    {start, end, phase ('alpha'/'beta'), angle}. Rows come in (start, end)
    pairs holding one direction; phase from which lateral component varies."""
    rows = []
    with open(upath, errors="replace") as fh:
        for line in fh:
            m = _UROW.search(line)
            if m:
                t, ux, uy, uz, ang = (int(m.group(1)), float(m.group(2)),
                                      float(m.group(3)), float(m.group(4)), int(m.group(5)))
                rows.append((t, uy, uz, ang))
    segs, phase = [], "alpha"
    for i in range(0, len(rows) - 1, 2):
        start, end, uy, uz, ang = rows[i][0], rows[i + 1][0], rows[i + 1][1], rows[i + 1][2], rows[i + 1][3]
        if uy != 0:
            phase = "beta"
        elif uz != 0:
            phase = "alpha"          # else: 0-deg row -> keep current phase
        segs.append({"start": start, "end": end, "phase": phase, "angle": ang})
    return segs


def residuals_at(logpath, end_times):
    """Parse log.simpleFoam; return {step: {field: initial residual}} for the
    requested end-of-segment steps only."""
    want = set(end_times)
    at, cur, t = {}, {}, None
    with open(logpath, errors="replace") as fh:
        for line in fh:
            m = _TIME.match(line)
            if m:
                if t is not None and t in want:
                    at[t] = cur
                t, cur = int(float(m.group(1).rstrip("s"))), {}
                continue
            s = _SOLV.search(line)
            if s and s.group(1) not in cur:
                cur[s.group(1)] = float(s.group(2))
    if t is not None and t in want:
        at[t] = cur
    return at


def _iter_config(logpath):
    parts = os.path.relpath(logpath, results_dir).split(os.sep)
    return parts[0], parts[1]


def _sort_key(logpath):
    it, cfg = _iter_config(logpath)
    return (int(it) if it.isdigit() else 1 << 30, cfg != "0", cfg)


def main():
    logs = sorted(glob.glob(os.path.join(results_dir, "**", "log.simpleFoam"),
                            recursive=True), key=_sort_key)
    if not logs:
        print(f"No log.simpleFoam found under {results_dir}")
        return

    case_rows, aoa_rows = [], []
    for logpath in logs:
        it, cfg = _iter_config(logpath)
        casedir = os.path.dirname(logpath)
        upath = os.path.join(casedir, "0", "U")
        crow = {"iteration": it, "config": cfg, "error": ""}
        try:
            segs = parse_u_schedule(upath)
            if not segs:
                raise ValueError("no sweep table in 0/U")
            at = residuals_at(logpath, [s["end"] for s in segs])
            per_field = {f: [] for f in FIELDS}
            for s in segs:
                res = at.get(s["end"], {})
                aoa_rows.append({"iteration": it, "config": cfg, "phase": s["phase"],
                                 "angle": s["angle"], "end_step": s["end"],
                                 **{f: res.get(f) for f in FIELDS}})
                for f in FIELDS:
                    if res.get(f) is not None:
                        per_field[f].append(res[f])
            crow["n_segments"] = len(segs)
            for f in FIELDS:
                crow[f"res_{f}"] = st.mean(per_field[f]) if per_field[f] else None
        except Exception as e:
            crow["error"] = repr(e)
        case_rows.append(crow)
        print(f"[{it}/{cfg}] segs={crow.get('n_segments')} "
              f"res_p={crow.get('res_p')} res_Ux={crow.get('res_Ux')} {crow['error']}")

    # atomic per-segment data (enables average-vs-AoA plots)
    with open(by_aoa_csv, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["iteration", "config", "phase", "angle",
                                           "end_step"] + FIELDS)
        w.writeheader()
        w.writerows(aoa_rows)

    # per-case averaged final residuals
    cols = ["iteration", "config", "n_segments"] + [f"res_{f}" for f in FIELDS] + ["error"]
    with open(out_csv, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(case_rows)

    # stats of the per-case averages across cases
    with open(stats_csv, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["field", "mean", "std", "min", "max", "n"])
        for f in FIELDS:
            v = [r[f"res_{f}"] for r in case_rows if r.get(f"res_{f}") is not None]
            if not v:
                continue
            s = st.stdev(v) if len(v) > 1 else 0.0
            w.writerow([f, f"{st.mean(v):.4e}", f"{s:.4e}",
                        f"{min(v):.4e}", f"{max(v):.4e}", len(v)])

    print(f"\nWrote {len(case_rows)} cases -> {out_csv}, {len(aoa_rows)} segments -> "
          f"{by_aoa_csv}, per-field stats -> {stats_csv}")


if __name__ == "__main__":
    main()

"""Run OpenFOAM checkMesh over every saved mesh case and collect the mesh
characteristics (the data behind the paper's `tab:mesh_parameters`) into one CSV.

The optimizer saves each config's mesh under results/<iteration>/<config>/ , because
workingdir is overwritten every iteration. The meshCase folder can sit directly there
(WingSolver_OuterLoop.FCMacro) or nested in a per-config backup, e.g.
results/<iter>/<config>/fullbackup/FlyingWingAutoSolve_newParamater/meshCase . This
discovers `meshCase` folders at ANY depth under each <iter>/<config>, runs `checkMesh`
on each, and reads the cfMesh system/meshDict for the sizing/boundary-layer settings.

`iteration` and `config` are taken from the first two path components under
`results_dir`, so point `results_dir` at the folder that directly contains the
numbered iteration folders (e.g. .../00000001_results/results).

Standalone script - run with a normal system Python (no FreeCAD needed):

    python Tools/analyse_meshes.py

EDIT the three paths in the CONFIG block below before running.
Point `results_dir` at `workingdir` to test against a single freshly-meshed case.
"""

import csv
import glob
import os
import re
import subprocess

# ============================ CONFIG (edit me) ============================
results_dir     = "results"                                        # root holding <iter>/<config>/meshCase
openfoam_bashrc = "/usr/lib/openfoam/openfoam2412/etc/bashrc"      # sourced for each checkMesh call
output_csv      = "results/mesh_characteristics.csv"
# =========================================================================

COLUMNS = [
    "iteration", "config",
    "base_size_mm", "refinement_levels", "refined_size_mm", "domain_radius_m",
    "n_layers", "thickness_ratio",
    "total_cells", "hex_fraction_pct",
    "max_non_ortho_deg", "avg_non_ortho_deg", "severe_non_ortho_faces",
    "max_skewness", "highly_skew_faces", "max_aspect_ratio",
    "mesh_ok", "error",
]


def _search(pattern, text, group=1, cast=float, default=None):
    """Return the captured group cast to `cast`, or `default` if not found."""
    m = re.search(pattern, text)
    if not m:
        return default
    try:
        return cast(m.group(group))
    except (ValueError, IndexError):
        return default


def run_checkmesh(meshcase):
    """Source OpenFOAM and run checkMesh on `meshcase`; return combined output."""
    cmd = (f'source "{openfoam_bashrc}" && '
           f'checkMesh -allGeometry -allTopology -case "{meshcase}"')
    proc = subprocess.run(["bash", "-lc", cmd], capture_output=True, text=True)
    return proc.stdout + proc.stderr


def parse_checkmesh(text):
    """Extract the mesh-quality metrics from checkMesh output."""
    out = {}
    total = _search(r"(?m)^\s*cells:\s+(\d+)", text, cast=int)
    hexa = _search(r"(?m)^\s*hexahedra:\s+(\d+)", text, cast=int)
    out["total_cells"] = total
    out["hex_fraction_pct"] = (round(100.0 * hexa / total, 2)
                               if total and hexa is not None else None)

    # "Mesh non-orthogonality Max: 80.1 average: 8.1"
    m = re.search(r"non-orthogonality Max:\s*([\d.eE+-]+)\s*average:\s*([\d.eE+-]+)", text)
    out["max_non_ortho_deg"] = round(float(m.group(1)), 3) if m else None
    out["avg_non_ortho_deg"] = round(float(m.group(2)), 3) if m else None
    # "*Number of severely non-orthogonal (> 70 degrees) faces: 143." (absent when none)
    out["severe_non_ortho_faces"] = _search(
        r"severely non-orthogonal \(> ?70 degrees\) faces:\s*(\d+)",
        text, cast=int, default=0)

    # "Max skewness = 5.11, 32 highly skew faces ..." OR "Max skewness = X OK."
    out["max_skewness"] = _search(r"Max skewness\s*=\s*([\d.eE+-]+)", text)
    out["highly_skew_faces"] = _search(r"([\d]+)\s+highly skew faces", text,
                                       cast=int, default=0)

    out["max_aspect_ratio"] = _search(r"Max aspect ratio\s*=\s*([\d.eE+-]+)", text)
    out["mesh_ok"] = bool(re.search(r"\bMesh OK\.", text))

    # "Overall domain bounding box (xmin ymin zmin) (xmax ymax zmax)" -> radius
    bb = re.search(r"Overall domain bounding box \(([-\d.eE+ ]+)\) \(([-\d.eE+ ]+)\)", text)
    if bb:
        lo = [float(v) for v in bb.group(1).split()]
        hi = [float(v) for v in bb.group(2).split()]
        out["domain_radius_m"] = round(max(h - l for h, l in zip(hi, lo)) / 2.0, 3)
    else:
        out["domain_radius_m"] = None
    return out


def parse_meshdict(meshcase):
    """Read cfMesh system/meshDict for sizing + boundary-layer settings."""
    out = {"base_size_mm": None, "refinement_levels": None, "refined_size_mm": None,
           "n_layers": None, "thickness_ratio": None}
    path = os.path.join(meshcase, "system", "meshDict")
    try:
        with open(path) as fh:
            txt = fh.read()
    except OSError:
        return out
    base_m = _search(r"maxCellSize\s+([\d.eE+-]+)", txt)          # metres
    levels = _search(r"additionalRefinementLevels\s+(\d+)", txt, cast=int)
    out["base_size_mm"] = round(base_m * 1000.0, 3) if base_m is not None else None
    out["refinement_levels"] = levels
    if base_m is not None and levels is not None:
        out["refined_size_mm"] = round(base_m * 1000.0 / (2 ** levels), 3)
    out["n_layers"] = _search(r"nLayers\s+(\d+)", txt, cast=int)
    out["thickness_ratio"] = _search(r"thicknessRatio\s+([\d.eE+-]+)", txt)
    return out


def _iter_config(meshcase):
    """iteration, config = first two path components under results_dir."""
    parts = os.path.relpath(meshcase, results_dir).split(os.sep)
    return parts[0], parts[1]


def _sort_key(meshcase):
    iteration, config = _iter_config(meshcase)
    it = int(iteration) if iteration.isdigit() else 1 << 30
    return (it, config != "0", config)   # numeric iteration, base "0" first


def find_mesh_cases():
    """All `meshCase` dirs at any depth under results_dir/<iter>/<config>/ that
    hold an actual mesh (constant/polyMesh)."""
    found = []
    for mc in glob.glob(os.path.join(results_dir, "**", "meshCase"), recursive=True):
        if not os.path.isdir(os.path.join(mc, "constant", "polyMesh")):
            continue
        if len(os.path.relpath(mc, results_dir).split(os.sep)) < 3:
            continue   # need at least <iter>/<config>/.../meshCase
        found.append(mc)
    return sorted(found, key=_sort_key)


def main():
    meshcases = find_mesh_cases()
    if not meshcases:
        print(f"No mesh cases (with constant/polyMesh) found under {results_dir}")
        return

    rows = []
    for meshcase in meshcases:
        iteration, config = _iter_config(meshcase)
        row = dict.fromkeys(COLUMNS)
        row["iteration"], row["config"], row["error"] = iteration, config, ""
        row.update(parse_meshdict(meshcase))
        try:
            row.update(parse_checkmesh(run_checkmesh(meshcase)))
            if row["total_cells"] is None:
                row["error"] = "checkMesh produced no cell count (see meshCase logs)"
        except Exception as e:   # keep going on a bad case
            row["error"] = repr(e)
        status = ("OK" if row["mesh_ok"] else "FAILED CHECKS") if not row["error"] else "ERROR"
        print(f"[{iteration}/{config}] cells={row['total_cells']} "
              f"maxNonOrtho={row['max_non_ortho_deg']} maxSkew={row['max_skewness']} -> {status}")
        rows.append(row)

    os.makedirs(os.path.dirname(output_csv) or ".", exist_ok=True)
    with open(output_csv, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nWrote {len(rows)} rows to {output_csv}")


if __name__ == "__main__":
    main()

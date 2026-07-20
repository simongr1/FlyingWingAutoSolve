"""Summarise mesh_characteristics.csv: mean / std / min / max per numeric column.

Reads the CSV produced by Tools/analyse_meshes.py and writes one summary row
per numeric column (mean, sample std, min, max, N) to mesh_stats.csv - the
aggregate mesh-quality numbers for the paper's mesh table.

    python3 Tools/mesh_stats.py
"""

import csv
import statistics as st

# ============================ CONFIG (edit me) ============================
input_csv  = "mesh_characteristics.csv"
output_csv = "mesh_stats.csv"
# =========================================================================

# numeric columns to summarise (identifiers/flags excluded)
NUMERIC = ["base_size_mm", "refinement_levels", "refined_size_mm", "domain_radius_m",
           "n_layers", "thickness_ratio", "total_cells", "hex_fraction_pct",
           "max_non_ortho_deg", "avg_non_ortho_deg", "severe_non_ortho_faces",
           "max_skewness", "highly_skew_faces", "max_aspect_ratio"]


def main():
    rows = list(csv.DictReader(open(input_csv)))
    n = len(rows)
    with open(output_csv, "w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["metric", "mean", "std", "min", "max", "n"])
        for col in NUMERIC:
            vals = [float(r[col]) for r in rows if r.get(col) not in (None, "")]
            if not vals:
                continue
            std = st.stdev(vals) if len(vals) > 1 else 0.0
            writer.writerow([col, f"{st.mean(vals):.4f}", f"{std:.4f}",
                             f"{min(vals):.4f}", f"{max(vals):.4f}", len(vals)])
    print(f"Summarised {n} meshes -> {output_csv}")


if __name__ == "__main__":
    main()

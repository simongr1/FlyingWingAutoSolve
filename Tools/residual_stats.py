"""
This script reads the output of extract_residuals.py
Then for each Angle (seperated for alpha and beta) it calculates mean, min, max and std for the residual.
"""
import pandas as pd

# 1. Load the CSV file
# Change 'your_file.csv' to your actual file name.
# If your file uses spaces/tabs instead of commas, use sep=r'\s+'
file_path = 'residuals/00000001_results/residuals_by_aoa.csv'  # Update this path as needed
df = pd.read_csv(file_path, sep=',')
print("Actual columns found in file:", list(df.columns))
# Clean up column names to remove any trailing spaces
df.columns = df.columns.str.strip()

# 2. Define the target columns and statistics
columns_to_analyze = ['Ux', 'Uy', 'Uz', 'p', 'k', 'omega']
stats_functions = ['mean', 'min', 'max', 'std']

# 3. Group by config, phase, and angle to keep alpha and beta separate
# This ensures rows like (1, 0, alpha, -20) and (1, 0, beta, -20) are calculated independently
group_cols = [col for col in ['config', 'phase', 'angle'] if col in df.columns]

print(f"Grouping data by: {group_cols}")
grouped_stats = df.groupby(group_cols)[columns_to_analyze].agg(stats_functions)

# 4. Flatten the multi-level columns for a clean output (e.g., Ux_mean, Ux_min...)
grouped_stats.columns = [f'{col}_{stat}' for col, stat in grouped_stats.columns]
grouped_stats = grouped_stats.reset_index()

# 5. Save the final separated results to a new CSV
output_file = 'stats_separated_by_phase.csv'
grouped_stats.to_csv(output_file, index=False)

print(f"\nSuccess! Results saved to '{output_file}'. Here is a preview:")
print(grouped_stats.head())
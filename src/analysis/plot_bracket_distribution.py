import os
import pandas as pd
import matplotlib.pyplot as plt


def plot(json_stats_csv: str, result_dir: str):
    df = pd.read_csv(json_stats_csv)

    # Sort by SIZE_BYTES ascending
    df = df.sort_values("SIZE_BYTES")

    # Ensure result directory exists
    os.makedirs(result_dir, exist_ok=True)

    # Create stacked bar plot
    fig, ax = plt.subplots(figsize=(12, 6))

    # ax.bar(df["JSON"], df["CURLY_PERCENT"], label="Curly %")
    # ax.bar(df["JSON"], df["SQUARY_PERCENT"], bottom=df["CURLY_PERCENT"], label="Squary %")

    ax.bar(df["JSON"], df["SQUARY_PERCENT"], label="Squary %")
    ax.bar(df["JSON"], df["CURLY_PERCENT"],
           bottom=df["SQUARY_PERCENT"], label="Curly %")

    # Formatting
    ax.set_ylabel("Percent")
    ax.set_xlabel("JSON Files (sorted by size)")
    ax.set_title("Curly vs Squary Percent in JSON Files")
    ax.legend()
    ax.tick_params(axis='x', rotation=45)
    ax.grid(True, axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()

    # Save plot
    plot_filename = os.path.join(result_dir, "json_curly_squary_percent.png")
    plt.savefig(plot_filename)
    print(f"Generated: {plot_filename}")
    plt.close()


#
if __name__ == "__main__":
    # Input CSV file (with columns: JSON,SIZE_BYTES,NUM_BRACKETS,CURLY_PERCENT,SQUARY_PERCENT)
    json_stats_csv = "res/data/analysis/bracket_distribution/bracket_distribution.csv"
    result_dir = "res/plots/analysis/bracket_distribution"

    plot(json_stats_csv, result_dir)

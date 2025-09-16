import os
import pandas as pd
import matplotlib.pyplot as plt


def plot_positive_negative(csv_path: str, result_dir: str):
    # Ensure result directory exists
    os.makedirs(result_dir, exist_ok=True)

    # Read CSV into DataFrame
    df = pd.read_csv(csv_path)

    # Sort by cutoff numerically
    df = df.sort_values(by="CUTOFF", key=lambda x: x.astype(int))

    # Treat cutoffs as strings (categorical axis)
    df["CUTOFF"] = df["CUTOFF"].astype(str)

    # Plot
    plt.figure(figsize=(10, 6))

    # Softer, prettier colors
    green_tone = "#2ecc71"  # emerald green
    red_tone = "#e74c3c"    # soft red

    # Positive bars (green, upward)
    plt.bar(df["CUTOFF"], df["SUM_POSITIVE"], color=green_tone, label="Sum Positive")

    # Negative bars (red, downward)
    plt.bar(df["CUTOFF"], -df["SUM_NEGATIVE"], color=red_tone, label="Sum Negative")

    # Labels and formatting
    plt.xlabel("Cutoff")
    plt.ylabel("Values")
    plt.title("Positive vs Negative Sums by Cutoff")
    plt.xticks(rotation=45, ha="right")  # rotate labels
    plt.legend()
    plt.grid(axis="y", linestyle="--", alpha=0.7)

    # Save figure to result directory
    output_path = os.path.join(result_dir, "positive_negative_plot.png")
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"Plot saved to: {output_path}")


if __name__ == "__main__":
    csv_path = "res/plots/speed/server/find_best_cutoff/summary_combined.csv"
    result_dir = "res/plots/speed/server/find_best_cutoff/plots"

    plot_positive_negative(csv_path, result_dir)

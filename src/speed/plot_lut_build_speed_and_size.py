import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def plot(build_csv: str, output_dir: str = "plots"):
    # Read data
    build_df = pd.read_csv(build_csv)

    # Ensure cutoffs are treated as categorical for bar plots
    build_df["CUTOFF"] = build_df["CUTOFF"].astype(str)

    # Convert size from bytes to MB
    build_df["SIZE_MB"] = build_df["SIZE_IN_BYTES"] / (1024 * 1024)

    # Compute build-only time (excluding collection)
    build_df["BUILD_ONLY_SECONDS"] = build_df["BUILD_TIME_SECONDS"] - build_df["COLLECTION_TIME_SECONDS"]

    # Create output directory if it doesn’t exist
    os.makedirs(output_dir, exist_ok=True)

    # Get list of unique JSON datasets
    json_files = build_df["JSON"].unique()

    for json_name in json_files:
        df = build_df[build_df["JSON"] == json_name]
        repetitions = df["REPETITIONS"].iloc[0]

        fig, axes = plt.subplots(2, 1, figsize=(8, 6), sharex=True)
        fig.suptitle(
            f"{json_name} (Repetitions = {repetitions})",
            fontsize=14,
            fontweight="bold"
        )

        # --- Build Time (stacked bar) ---
        axes[0].bar(
            df["CUTOFF"],
            df["COLLECTION_TIME_SECONDS"],
            label="Collection",
            color="skyblue"
        )
        axes[0].bar(
            df["CUTOFF"],
            df["BUILD_ONLY_SECONDS"],
            bottom=df["COLLECTION_TIME_SECONDS"],
            label="Build",
            color="navy"
        )
        axes[0].set_ylabel("LUT Build Time (s)")
        axes[0].set_xlabel("")
        axes[0].legend()

        # --- Size (in MB) ---
        sns.barplot(
            data=df,
            x="CUTOFF",
            y="SIZE_MB",
            hue="CUTOFF",
            ax=axes[1],
            palette=["#6AA84F"] * df["CUTOFF"].nunique(),
            legend=False
        )
        axes[1].set_ylabel("LUT Size (MB)")
        axes[1].set_xlabel("Cutoff")

        plt.tight_layout(rect=[0, 0, 1, 0.95])

        # Save plot
        safe_name = json_name.replace(" ", "_").replace("(", "").replace(")", "").replace("/", "_")
        filepath = os.path.join(output_dir, f"{safe_name}.png")
        print(f"Saved to {filepath}")
        plt.savefig(filepath, dpi=150)
        plt.close(fig)

# Run with: python src/speed/plot_lut_build_speed_and_size.py
#
# Generate stacked bar plots for build and collection times, along with size plots,
# for each JSON dataset in a CSV file.
#
# Example csv:
#   JSON,CUTOFF,BUILD_TIME_SECONDS,COLLECTION_TIME_SECONDS,SIZE_IN_BYTES,REPETITIONS
#   bestbuy_large_record_(1GB),0,0.5320961592000001,0.3920479680000001,16103794,10
#   bestbuy_large_record_(1GB),64,0.4090446436,0.37976783839999995,3635750,10
#   ...
#
# For each dataset:
#     1. The top plot shows a stacked bar chart of collection time and build-only time.
#     2. The bottom plot shows a bar chart of the output size in MB.
#
# The resulting plots are saved as PNG files in the specified output directory,
# with filenames derived from the dataset names.
if __name__ == "__main__":
    # Input
    build_csv = "res/data/speed/server/lut_build_speed_and_size/build_repetitions=10.csv"
    result_dir = "res/plots/speed/server/lut_build_speed_and_size"

    plot(build_csv, result_dir)

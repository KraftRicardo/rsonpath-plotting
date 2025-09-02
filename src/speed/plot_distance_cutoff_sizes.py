import os
import re

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import pandas as pd
import seaborn as sns

# Custom color palette
PLOT_COLORS = [
    'red', 'skyblue', 'blue', 'orange', 'green',
    'coral', 'purple', 'pink', 'cyan', 'magenta',
    'brown', 'turquoise', 'darkgreen', 'darkred', 'darkcyan',
    'darkorange', 'darkviolet', 'lime', 'indigo', 'gold',
    'darkblue', 'chartreuse', 'teal', 'yellow', 'salmon',
    'darkkhaki', 'crimson', 'peru', 'forestgreen', 'mediumpurple', 'black',
]


def extract_size(json_name: str) -> float:
    match = re.search(r"\(([\d.]+)([MG]B)\)", json_name)
    if not match:
        return float('inf')
    size, unit = match.groups()
    size = float(size)
    return size * 1024 if unit == "GB" else size


def plot_build(data_dir_path: str, result_dir: str, cutoffs):
    os.makedirs(result_dir, exist_ok=True)

    build_time_png_path = os.path.join(result_dir, "build_time.png")
    size_png_path = os.path.join(result_dir, "size.png")
    combined_png_path = os.path.join(result_dir, "build_time_and_size.png")

    all_data = []

    for cutoff in cutoffs:
        build_csv_path = f"{data_dir_path}/{cutoff}/build.csv"
        if not os.path.exists(build_csv_path):
            print(f"Warning: {build_csv_path} not found, skipping...")
            continue

        df = pd.read_csv(build_csv_path)
        df["CUTOFF"] = str(cutoff)
        df["SIZE_MB"] = df["SIZE_IN_BYTES"] / (1024 * 1024)
        df["JSON_SIZE_SORT"] = df["JSON"].apply(extract_size)

        all_data.append(df[["JSON", "BUILD_TIME_SECONDS", "SIZE_MB", "CUTOFF", "JSON_SIZE_SORT"]])

    if not all_data:
        print("No data available to plot.")
        return

    df = pd.concat(all_data).sort_values("JSON_SIZE_SORT")
    sorted_cutoffs = [str(c) for c in sorted(cutoffs)]

    # --- Normalize relative to cutoff=0 ---
    base_df = df[df["CUTOFF"] == "0"].set_index("JSON")
    df = df.join(
        base_df[["BUILD_TIME_SECONDS", "SIZE_MB"]],
        on="JSON",
        rsuffix="_BASE"
    )
    df["BUILD_TIME_REL"] = df["BUILD_TIME_SECONDS"] / df["BUILD_TIME_SECONDS_BASE"] * 100
    df["SIZE_MB_REL"] = df["SIZE_MB"] / df["SIZE_MB_BASE"] * 100

    sns.set_theme(style="whitegrid")
    palette = {cutoff: PLOT_COLORS[i % len(PLOT_COLORS)] for i, cutoff in enumerate(sorted_cutoffs)}

    # --- Plot 1: Absolute Build Time ---
    plt.figure(figsize=(14, 6))
    ax = sns.barplot(
        data=df,
        x="JSON",
        y="BUILD_TIME_SECONDS",
        hue="CUTOFF",
        hue_order=sorted_cutoffs,
        palette=palette,
    )
    plt.xticks(rotation=45, ha="right")
    plt.ylabel("Build Time (seconds)")
    plt.title("Build Time per JSON File by Cutoff")
    plt.tight_layout(rect=[0, 0, 0.85, 1])
    ax.legend(title="Cutoff", bbox_to_anchor=(1.02, 1), loc="upper left", borderaxespad=0)
    plt.savefig(build_time_png_path)
    print(f"Generated {build_time_png_path}")
    plt.close()

    # --- Plot 2: Absolute LUT Size ---
    plt.figure(figsize=(14, 6))
    ax = sns.barplot(
        data=df,
        x="JSON",
        y="SIZE_MB",
        hue="CUTOFF",
        hue_order=sorted_cutoffs,
        palette=palette,
    )
    plt.xticks(rotation=45, ha="right")
    plt.ylabel("LUT Size (MB)")
    plt.title("LUT Size in MB per JSON File by Cutoff")
    plt.tight_layout(rect=[0, 0, 0.85, 1])
    ax.legend(title="Cutoff", bbox_to_anchor=(1.02, 1), loc="upper left", borderaxespad=0)
    plt.savefig(size_png_path)
    print(f"Generated {size_png_path}")
    plt.close()

    # --- Plot 3: Combined (relative %) ---
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)

    # Build Time subplot
    sns.barplot(
        data=df,
        x="JSON",
        y="BUILD_TIME_REL",
        hue="CUTOFF",
        hue_order=sorted_cutoffs,
        palette=palette,
        ax=ax1,
    )
    ax1.set_ylabel("Build Time (% of cutoff=0)")
    ax1.set_title("Relative Build Time per JSON File by Cutoff")
    ax1.yaxis.set_major_formatter(mtick.PercentFormatter())
    ax1.legend(title="Cutoff", bbox_to_anchor=(1.02, 1), loc="upper left")

    # Size subplot
    sns.barplot(
        data=df,
        x="JSON",
        y="SIZE_MB_REL",
        hue="CUTOFF",
        hue_order=sorted_cutoffs,
        palette=palette,
        ax=ax2,
    )
    ax2.set_ylabel("LUT Size (% of cutoff=0)")
    ax2.set_title("Relative LUT Size per JSON File by Cutoff")
    ax2.yaxis.set_major_formatter(mtick.PercentFormatter())
    ax2.legend_.remove()
    ax2.set_xticklabels(ax2.get_xticklabels(), rotation=45, ha="right")

    plt.tight_layout(rect=[0, 0, 0.85, 1])
    plt.savefig(combined_png_path)
    print(f"Generated {combined_png_path}")
    plt.close()

# Run with: python src/speed/plot_distance_cutoff_sizes.py
# Run with: python src/speed/plot_ptrhash_double_empty_list_opt.py
#
# This function expects a "dir_path" to the directory holding all the data. Per given cutoffs it expects a subdirectory
# (named after the cutoff) that contains the .csv with data.
# The .csv files have to follow this structure:
#   QUERY_ID,QUERY_TEXT,QUERY_TIME_SECONDS
#   1,$.products[4].categoryPath[2],0.00954
#   2,$.products[*].categoryPath[2],0.26674
#   3,$.products[*].quantityLimit,0.32806
#   4,$.products[*].frequentlyPurchasedWith[*],0.26628
#   ...
#
# Every cutoff subfolder needs to hold the same .csv files but of course with different data values.
# The result plots will be saved in the new folder named "plots". The code will generate the build_time.png and
# size.png plots. Adapt "dir_path" and the "cutoffs" list to your wishes.
if __name__ == "__main__":
    # Input
    dir_path = "res/data/speed/server/distance_cutoff"
    result_dir = "res/plots/speed/server/distance_cutoff_sizes"
    cutoffs = [0, 64, 128, 192, 256, 320, 384, 448, 512, 1024, 2048, 4096, 8192]

    plot_build(dir_path, result_dir, cutoffs)

import os
import re

import matplotlib.pyplot as plt
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


def plot_build(data_dir_path: str, cutoffs):
    all_build_times = []
    all_sizes = []

    for cutoff in cutoffs:
        build_csv_path = f"{data_dir_path}/{cutoff}/build.csv"
        if not os.path.exists(build_csv_path):
            print(f"Warning: {build_csv_path} not found, skipping...")
            continue

        df = pd.read_csv(build_csv_path)
        df["CUTOFF"] = str(cutoff)
        df["SIZE_MB"] = df["SIZE_IN_BYTES"] / (1024 * 1024)
        df["JSON_SIZE_SORT"] = df["JSON"].apply(extract_size)

        all_build_times.append(df[["JSON", "BUILD_TIME_SECONDS", "CUTOFF", "JSON_SIZE_SORT"]])
        all_sizes.append(df[["JSON", "SIZE_MB", "CUTOFF", "JSON_SIZE_SORT"]])

    if not all_build_times or not all_sizes:
        print("No data available to plot.")
        return

    build_df = pd.concat(all_build_times).sort_values("JSON_SIZE_SORT")
    size_df = pd.concat(all_sizes).sort_values("JSON_SIZE_SORT")

    plots_path = os.path.join(data_dir_path, "plots")
    os.makedirs(plots_path, exist_ok=True)

    sns.set(style="whitegrid")
    sorted_cutoffs = [str(c) for c in sorted(cutoffs)]

    # Truncate color palette if needed
    palette = {cutoff: PLOT_COLORS[i % len(PLOT_COLORS)] for i, cutoff in enumerate(sorted_cutoffs)}

    # --- Plot: Build Time ---
    plt.figure(figsize=(14, 6))
    ax = sns.barplot(
        data=build_df,
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
    path = os.path.join(plots_path, "build_time.png")
    plt.savefig(path)
    print(f"Generated {path}")
    plt.close()

    # --- Plot: Size in MB ---
    plt.figure(figsize=(14, 6))
    ax = sns.barplot(
        data=size_df,
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
    path = os.path.join(plots_path, "size.png")
    plt.savefig(path)
    print(f"Generated {path}")
    plt.close()


# Run with: python python/speed/plot_ptrhash_double_empty_list_opt.py
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
    dir_path = ".a_extern_final_results/speed/lut_ptrhash_double_empty_list_opt"
    cutoffs = [64, 128, 192, 256, 320, 384, 448, 512, 1024, 2048, 4096, 8192]

    plot_build(dir_path, cutoffs)

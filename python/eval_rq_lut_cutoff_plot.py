import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re


def plot_all(data_dir_path: str, cutoffs):
    plot_build(data_dir_path, cutoffs)
    plot_query()


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
    plt.savefig(os.path.join(plots_path, "build_time.png"))
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
    plt.savefig(os.path.join(plots_path, "size.png"))
    plt.close()


def plot_query():
    # TODO: implement later
    pass


if __name__ == "__main__":
    # Input
    result_dir_path = ".a_extern_final_results/speed/lut_ptrhash_double_empty_list_opt"
    cutoffs = [64, 128, 192, 256, 320, 384, 448, 512, 1024, 2048, 4096, 8192]

    plot_all(result_dir_path, cutoffs)

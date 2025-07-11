import os
import re

import matplotlib.pyplot as plt
import pandas as pd


def increment_filename(path: str) -> str:
    """If the file exists, add (1), (2), etc. before the extension."""
    base, ext = os.path.splitext(path)
    counter = 1
    new_path = path
    while os.path.exists(new_path):
        new_path = f"{base} ({counter}){ext}"
        counter += 1
    return new_path


def plot(
        csv_btree: str,
        csv_indexmap: str,
        result_dir_path: str,
):
    os.makedirs(result_dir_path, exist_ok=True)

    # Read input CSVs
    data1 = pd.read_csv(csv_btree)
    data2 = pd.read_csv(csv_indexmap)

    # Rename columns for internal consistency
    rename_map = {
        "NAME": "name",
        "ORIGINAL_BYTES": "file_size",
        "HEAP_BYTES": "heap_bytes",
        "PARSE_TIME_SEC": "build_time"
    }

    data1 = data1.rename(columns=rename_map)
    data2 = data2.rename(columns=rename_map)

    # Sort by original file size
    data1 = data1.sort_values(by="file_size")
    data2 = data2.set_index("name").reindex(data1["name"]).reset_index()

    names = data1["name"]
    names = data1["name"].apply(
        lambda s: re.search(r"(\d+)MB", s).group(1) if re.search(r"(\d+)MB", s) else s
    )

    # Compute heap_bytes / file_size ratio
    ratio1 = data1["heap_bytes"] / data1["file_size"]
    ratio2 = data2["heap_bytes"] / data2["file_size"]

    # Get build times
    build_time1 = data1["build_time"]
    build_time2 = data2["build_time"]

    # Create side-by-side subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    # Font size configuration
    label_fontsize = 18
    tick_fontsize = 16
    legend_fontsize = 16
    title_fontsize = 18

    # Plot 1: Heap Ratio
    ax1.plot(names, ratio1, marker="o", label="BTree")
    ax1.plot(names, ratio2, marker="o", label="IndexMap")
    ax1.set_title("Serde vs. JSON size", fontsize=title_fontsize)
    ax1.set_xlabel("JSON Size in MB", fontsize=label_fontsize)
    ax1.set_ylabel("Size Ratio", fontsize=label_fontsize)
    ax1.legend(fontsize=legend_fontsize)
    ax1.tick_params(axis='x', labelsize=tick_fontsize, rotation=45)
    ax1.tick_params(axis='y', labelsize=tick_fontsize)

    # Plot 2: Parse Time
    ax2.plot(names, build_time1, marker="o", label="BTree")
    ax2.plot(names, build_time2, marker="o", label="IndexMap")
    ax2.set_title("Serde Build Time", fontsize=title_fontsize)
    ax2.set_xlabel("JSON Size in MB", fontsize=label_fontsize)
    ax2.set_ylabel("Time (s)", fontsize=label_fontsize)
    ax2.legend(fontsize=legend_fontsize)
    ax2.tick_params(axis='x', labelsize=tick_fontsize, rotation=45)
    ax2.tick_params(axis='y', labelsize=tick_fontsize)

    plt.tight_layout()
    result_png_path = f"{result_dir_path}/serde_size_and_build_time.png"
    result_png_path = increment_filename(result_png_path)
    plt.savefig(result_png_path)
    print(f"Plot saved to: {result_png_path}")

# Run with: python src/analysis/plot_serde_size_and_build_time.py
#
# Create build time and build size plot for serde measurement data.
#
# "btree_csv_path" is the path to the .csv holding all the btree data. Structure:
#   NAME,ORIGINAL_BYTES,PARSE_TIME_SEC,HEAP_BYTES
#   google_map_short_(107MB).json,106896877,2.590639,739103679
#   pokemon_(173MB).json,173196913,5.177957,1632773152
#   bestbuy_short_(103MB).json,103231582,3.672334,518063638
#   ...
# "indexmap_csv_path" is the same as the btree_csv_path but holds the data about the indexmap implementation of serde.
# Both .csv need to cover the same JSON files in order for the plot to make sense.
# "result_png_path" is the path where the code saves the resulting plot image. Will add a (2), (3), ... to the name if
# the image already exists.
if __name__ == "__main__":
    # Input
    btree_csv_path = "res/data/analysis/serde_size_and_build_time/MB_100_btree.csv"
    indexmap_csv_path = "res/data/analysis/serde_size_and_build_time/MB_100_indexmap.csv"
    result_dir_path = "res/plots/analysis/serde_size_and_build_time"

    plot(btree_csv_path, indexmap_csv_path, result_dir_path)

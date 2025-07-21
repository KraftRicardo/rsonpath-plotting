import os

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


def plot_binned_frequencies(df: pd.DataFrame, directory: str, file_base_name: str) -> None:
    # Build bins
    bin_edges = [0] + [2 ** i for i in range(1, 41)]
    df['binned_distance'] = pd.cut(df['distance'], bins=bin_edges, right=False, include_lowest=True)
    binned_df = df.groupby('binned_distance', observed=False).agg({'frequency': 'sum'}).reset_index()
    binned_df['frequency'] = binned_df['frequency'].fillna(0)

    # Calculate total frequency
    max_distance = df["distance"].max()
    total_frequency = binned_df['frequency'].sum()
    binned_df['percentage'] = (binned_df['frequency'] / total_frequency) * 100

    # Plotting the binned distances
    plt.figure(figsize=(12, 8))
    bars = plt.bar(binned_df['binned_distance'].astype(
        str), binned_df['percentage'], color='skyblue')
    plt.xticks(rotation=90)  # Rotate x-axis labels for better readability
    plt.xlabel('Distance (Binned)')
    plt.ylabel('Percentage of Total Frequency')
    plt.title(f'Distance Distribution in {file_base_name}\n'
              f'Sum of all Frequencies: {total_frequency}, Max Distance: {max_distance}')
    plt.grid(True)

    # Add labels over each bar
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, yval, f'{int(yval * total_frequency / 100)}',
                 ha='center', va='bottom', fontsize=10, color="blue", rotation=90)

    # Add vertical red line
    index_2_17 = binned_df[binned_df['binned_distance'].astype(str).str.contains('131072')].index[0]
    plt.axvline(x=index_2_17 - 0.5, color='red', linestyle='--', linewidth=2, label='2^17')

    # Add vertical red line
    index_2_33 = binned_df[binned_df['binned_distance'].astype(str).str.contains('8589934592')].index[0]
    plt.axvline(x=index_2_33 - 0.5, color='orange', linestyle='--', linewidth=2, label='2^33')

    plt.legend()

    # Save plot
    plt.tight_layout()
    save_path = f"{directory}/{file_base_name}.png"
    plt.savefig(save_path)
    print(f"Generated: {save_path}")
    plt.close()


def plot_binned_frequencies_short(df: pd.DataFrame, directory: str, file_base_name: str) -> None:
    bin_edges = [0] + [2 ** i for i in range(1, 41)]
    df['binned_distance'] = pd.cut(df['distance'], bins=bin_edges, right=False, include_lowest=True)
    binned_df = df.groupby('binned_distance', observed=False).agg({'frequency': 'sum'}).reset_index()
    binned_df['frequency'] = binned_df['frequency'].fillna(0)

    total_frequency = binned_df['frequency'].sum()
    binned_df['percentage'] = (binned_df['frequency'] / total_frequency) * 100

    # Trim to first 34 bins (i.e., 2^1 to 2^34)
    trimmed_df = binned_df.iloc[:34].copy()
    trimmed_df['bin_number'] = range(1, 35)

    # Plotting
    plt.figure(figsize=(12, 8))
    bars = plt.bar(trimmed_df['bin_number'], trimmed_df['percentage'], color='skyblue')
    plt.xlabel('Bin Number')
    plt.ylabel('Percentage of Total Frequency')
    plt.grid(True)

    # Labels over bars
    for bar, freq in zip(bars, trimmed_df['frequency']):
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, yval, f'{int(freq)}',
                 ha='center', va='bottom', fontsize=10, color="blue", rotation=90)

    # Add vertical lines at bin 17 and 33
    plt.axvline(x=17 - 0.5, color='red', linestyle='--', linewidth=2, label='2^17')
    plt.axvline(x=33 - 0.5, color='orange', linestyle='--', linewidth=2, label='2^33')

    plt.xticks(ticks=range(1, 35))
    plt.legend()

    plt.tight_layout()
    save_path = f"{directory}/{file_base_name}.png"
    plt.savefig(save_path)
    print(f"Generated: {save_path}")
    plt.close()


def plot_binned_frequencies_64(df: pd.DataFrame, directory: str, file_base_name: str) -> None:
    # Define bin edges (inclusive on both sides by offsetting)
    bin_edges = [
        2,  # bin 1: 0–1
        3, 65,  # bin 2: 2–64
        129, 193,
        257, 321,
        385, 449,
        513, 577,
        641, 705,
        769, 833,
        897, 961,
        1025, 1089,
        1153, 1217,
        1281, 1345,
        1409, 1473,
        1537, 1601,
        1665, 1729,
        1793, 1857,
        1921, 1985,
        2049, float("inf")  # REST
    ]
    bin_labels = [
        "1",
        "2–64",
        "65–128",
        "129–192",
        "193–256",
        "257–320",
        "321–384",
        "385–448",
        "449–512",
        "513–576",
        "577–640",
        "641–704",
        "705–768",
        "769–832",
        "833–896",
        "897–960",
        "961–1024",
        "1025–1088",
        "1089–1152",
        "1153–1216",
        "1217–1280",
        "1281–1344",
        "1345–1408",
        "1409–1472",
        "1473–1536",
        "1537–1600",
        "1601–1664",
        "1665–1728",
        "1729–1792",
        "1793–1856",
        "1857–1920",
        "1921–1984",
        "1985–2048",
        "REST"
    ]

    # Create the bins (left AND right inclusive via workaround)
    df['custom_bin'] = pd.cut(
        df['distance'],
        bins=bin_edges,
        labels=bin_labels,
        right=True,
        include_lowest=True
    )

    binned_df = df.groupby('custom_bin', observed=False)['frequency'].sum().reset_index()
    binned_df['frequency'] = binned_df['frequency'].fillna(0)

    total_frequency = binned_df['frequency'].sum()
    max_distance = df["distance"].max()
    binned_df['percentage'] = (binned_df['frequency'] / total_frequency) * 100

    # Plotting
    plt.figure(figsize=(14, 8))
    bars = plt.bar(binned_df['custom_bin'], binned_df['percentage'], color='mediumpurple')
    plt.xticks(rotation=90)
    plt.xlabel('Distance Bins')
    plt.ylabel('Percentage of Total Frequency')
    plt.title(f'Custom Distance Distribution in {file_base_name}\n'
              f'Total Freq: {total_frequency}, Max Distance: {max_distance}')
    plt.grid(True)

    # Add frequency labels on bars
    for bar, freq in zip(bars, binned_df['frequency']):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, height, f'{int(freq)}',
                 ha='center', va='bottom', fontsize=9, color='black', rotation=90)

    plt.tight_layout()
    save_path = os.path.join(directory, f"{file_base_name}_custom.png")
    plt.savefig(save_path)
    print(f"Generated: {save_path}")
    plt.close()


def plot_all(data_dir_path: str, result_dir_path: str):
    # Create output directories
    plots_dir_path = os.path.join(result_dir_path, "plots")
    os.makedirs(plots_dir_path, exist_ok=True)
    plots_short_dir_path = os.path.join(result_dir_path, "plots_short")
    os.makedirs(plots_short_dir_path, exist_ok=True)
    plot_64_dir_path = os.path.join(result_dir_path, "plots_64")
    os.makedirs(plot_64_dir_path, exist_ok=True)

    # Get all JSON files in the directory
    for filename in os.listdir(data_dir_path):
        if filename.endswith(".csv"):
            file_path = os.path.join(data_dir_path, filename)

            # Read the JSON file as a DataFrame
            df = pd.read_csv(file_path)

            # Call plotting functions
            file_base_name = os.path.splitext(filename)[0].removesuffix("_distances")
            print(f"Process: {file_base_name}")
            plot_binned_frequencies(df, plots_dir_path, file_base_name)
            plot_binned_frequencies_short(df, plots_short_dir_path, file_base_name)
            plot_binned_frequencies_64(df, plot_64_dir_path, file_base_name)


# Run with: python src/analysis/plot_distance_distribution.py
#
# Plot the distance distribution of their brackets for individual JSON files.
#
# "data_dir_path" is the path to the folder holding all the .csv files. These follow this structure:
#   distance,frequency
#   1475,1
#   49,10
#   1493,1
#   48,3
# There is one .csv file per analyzed JSON so the csv should be named after the analyzed JSON file.
if __name__ == "__main__":
    # Input
    data_dir_path = "res/data/analysis/distance_distribution"
    result_dir_path = "res/plots/analysis/distance_distribution"

    plot_all(data_dir_path, result_dir_path)

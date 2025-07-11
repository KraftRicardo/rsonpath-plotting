import os

import matplotlib.pyplot as plt
import pandas as pd


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
    save_path = f"{directory}/{file_base_name}_plot.png"
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
    save_path = f"{directory}/{file_base_name}_short.png"
    plt.savefig(save_path)
    print(f"Generated: {save_path}")
    plt.close()


def plot_all(data_dir_path: str, result_dir_path: str):
    # Create output directories
    plots_dir_path = os.path.join(result_dir_path, "plots")
    os.makedirs(plots_dir_path, exist_ok=True)
    plots_short_dir_path = os.path.join(result_dir_path, "plots_short")
    os.makedirs(plots_short_dir_path, exist_ok=True)

    # Get all JSON files in the directory
    for filename in os.listdir(data_dir_path):
        if filename.endswith(".csv"):
            file_path = os.path.join(data_dir_path, filename)

            # Read the JSON file as a DataFrame
            df = pd.read_csv(file_path)

            file_base_name = os.path.splitext(filename)[0]
            base_name = file_base_name.removesuffix("_distances")

            # Call plotting functions
            plot_binned_frequencies(df, plots_dir_path, base_name)
            plot_binned_frequencies_short(df, plots_short_dir_path, base_name)


# Run with: python python/analysis/plot_distance_distribution.py
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

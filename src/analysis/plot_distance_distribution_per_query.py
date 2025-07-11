import sys
import os
import pandas as pd
import matplotlib.pyplot as plt

COLOR_1 = "#458AF5"
COLOR_2 = "#F5BA45"


def plot_binned_frequencies(df: pd.DataFrame, result_dir_path: str, file_base_name: str) -> None:
    if df.shape[1] != 3:
        raise ValueError("DataFrame should have exactly three columns: distance, frequency, and skip_type")

    # Build bins
    bin_edges = [0] + [2 ** i for i in range(1, 41)]
    df['binned_distance'] = pd.cut(df['distance'], bins=bin_edges, right=False, include_lowest=True)

    # Aggregate by binned distance and skip_type
    binned_df = df.groupby(['binned_distance', 'skip_type'], observed=False)['frequency'].sum().unstack(
        fill_value=0).reset_index()

    # Compute total frequency for percentages
    total_frequency = binned_df.get('lut', pd.Series(0, index=binned_df.index)).sum() + binned_df.get('ite',
                                                                                                      pd.Series(0,
                                                                                                                index=binned_df.index)).sum()
    binned_df['lut_percentage'] = (binned_df.get('lut', 0) / total_frequency) * 100
    binned_df['ite_percentage'] = (binned_df.get('ite', 0) / total_frequency) * 100

    # Plotting
    plt.figure(figsize=(12, 8))
    bar_width = 0.4
    x_labels = binned_df['binned_distance'].astype(str)
    x = range(len(x_labels))

    plt.bar(
        [i - bar_width / 2 for i in x],
        binned_df['lut_percentage'],
        width=bar_width,
        label='LUT',
        color=COLOR_1,
        align='center'
    )
    plt.bar(
        [i + bar_width / 2 for i in x],
        binned_df['ite_percentage'],
        width=bar_width,
        label='ITE',
        color=COLOR_2,
        align='center'
    )

    # Add labels on top of bars only if value is nonzero
    for i in x:
        frequency = binned_df.get('lut', pd.Series([0] * len(binned_df)))[i]
        if frequency > 0:
            plt.text(
                i - bar_width / 2, binned_df['lut_percentage'][i] + 0.5,
                f'{frequency:.0f}',
                ha='center',
                fontsize=10,
                color=COLOR_1
            )

        frequency = binned_df.get('ite', pd.Series([0] * len(binned_df)))[i]
        if frequency > 0:
            plt.text(
                i + bar_width / 2, binned_df['ite_percentage'][i] + 0.5,
                f'{frequency:.0f}',
                ha='center',
                fontsize=10,
                color=COLOR_2
            )

    plt.xticks(x, x_labels, rotation=90)
    plt.xlabel('Distance (Binned)')
    plt.ylabel('Percentage of Total Frequency')
    plt.title(
        f'Tracking of skip distances and their frequencies in {file_base_name}\nTotal Frequency: {total_frequency}')
    plt.legend()
    plt.grid(True, axis='y')

    # Add vertical reference lines
    index_2_17 = binned_df[binned_df['binned_distance'].astype(str).str.contains('131072')].index[0]
    plt.axvline(x=index_2_17 - 0.5, color='red', linestyle='--', linewidth=2, label='2^17')

    index_2_33 = binned_df[binned_df['binned_distance'].astype(str).str.contains('8589934592')].index[0]
    plt.axvline(x=index_2_33 - 0.5, color='orange', linestyle='--', linewidth=2, label='2^33')

    plt.legend()
    plt.tight_layout()

    # Save plot
    csv_path = f"{result_dir_path}/{file_base_name}.png"
    plt.savefig(csv_path)
    print(f"Generated: {csv_path}")
    plt.close()


def plot_all(data_dir_path: str, result_dir_path: str):
    os.makedirs(result_dir_path, exist_ok=True)

    for filename in os.listdir(data_dir_path):
        if filename.endswith(".csv"):
            file_path = os.path.join(data_dir_path, filename)
            file_base_name = os.path.splitext(filename)[0]

            df = pd.read_csv(file_path)
            plot_binned_frequencies(df, result_dir_path, file_base_name.removesuffix("_distances"))


# TODO
# Run with: python src/analysis/plot_distance_distribution_per_query.py
#
# Plot the distance jumps taken by each individual query.
#
# Expected .csv strucutre:
#   distance,frequency,skip_type
#   20118,6,lut
#   173266,1,lut
#   ...
# There is only one .csv per query.
if __name__ == "__main__":
    # Input
    data_dir_path = "res/data/analysis/distance_distribution_per_query/cutoff=0"
    result_dir_path = "res/plots/analysis/distance_distribution_per_query/cutoff=0"

    plot_all(data_dir_path, result_dir_path)

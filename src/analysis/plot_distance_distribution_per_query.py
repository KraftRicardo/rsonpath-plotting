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
    df['binned_distance'] = pd.cut(df['DISTANCE'], bins=bin_edges, right=False, include_lowest=True)

    # Aggregate by binned distance and skip_type
    binned_df = df.groupby(['binned_distance', 'SKIP_TYPE'], observed=False)['FREQUENCY'].sum().unstack(
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
                color=COLOR_1,
                rotation=90
            )

        frequency = binned_df.get('ite', pd.Series([0] * len(binned_df)))[i]
        if frequency > 0:
            plt.text(
                i + bar_width / 2, binned_df['ite_percentage'][i] + 0.5,
                f'{frequency:.0f}',
                ha='center',
                fontsize=10,
                color=COLOR_2,
                rotation=90
            )

    plt.xticks(x, x_labels, rotation=90)
    plt.xlabel('Distance (Binned)')
    plt.ylabel('Percentage of Total Frequency')
    plt.title(
        f'Distance Distribution per query {file_base_name}\nTotal Frequency: {total_frequency}')
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


def plot_binned_frequencies_64(df: pd.DataFrame, result_dir_path: str, file_base_name: str) -> None:
    bin_edges = [
        1,  # bin 1: 0–1
        2, 65,
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

    # Bin distances
    df['custom_bin'] = pd.cut(
        df['DISTANCE'],
        bins=bin_edges,
        labels=bin_labels,
        right=True,
        include_lowest=True
    )

    # Group and aggregate
    binned_df = df.groupby(['custom_bin', 'SKIP_TYPE'], observed=False)['FREQUENCY'].sum().unstack(
        fill_value=0).reset_index()

    total_frequency = binned_df.get('lut', pd.Series(0)).sum() + binned_df.get('ite', pd.Series(0)).sum()
    binned_df['lut_percentage'] = (binned_df.get('lut', 0) / total_frequency) * 100
    binned_df['ite_percentage'] = (binned_df.get('ite', 0) / total_frequency) * 100

    # Plotting
    plt.figure(figsize=(14, 8))
    bar_width = 0.4
    x_labels = binned_df['custom_bin'].astype(str)
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

    # Add labels
    for i in x:
        lut_val = binned_df.get('lut', pd.Series([0] * len(binned_df)))[i]
        if lut_val > 0:
            plt.text(i - bar_width / 2, binned_df['lut_percentage'][i] + 0.5, f"{lut_val:.0f}",
                     ha='center', fontsize=10, color=COLOR_1, rotation=90)

        ite_val = binned_df.get('ite', pd.Series([0] * len(binned_df)))[i]
        if ite_val > 0:
            plt.text(i + bar_width / 2, binned_df['ite_percentage'][i] + 0.5, f"{ite_val:.0f}",
                     ha='center', fontsize=10, color=COLOR_2, rotation=90)

    plt.xticks(x, x_labels, rotation=90)
    plt.xlabel('Distance (Binned)')
    plt.ylabel('Percentage of Total Frequency')
    plt.title(f'Binned Distance Distribution (64-step) for {file_base_name}\nTotal Frequency: {total_frequency}')
    plt.legend()
    plt.grid(True, axis='y')

    # Save
    out_path = f"{result_dir_path}/{file_base_name}.png"
    plt.tight_layout()
    plt.savefig(out_path)
    print(f"Generated: {out_path}")
    plt.close()


def plot_all(data_dir_path: str, result_dir_path: str):
    plots_dir_path = os.path.join(result_dir_path, "plots")
    os.makedirs(plots_dir_path, exist_ok=True)
    plot_64_dir_path = os.path.join(result_dir_path, "plots_64")
    os.makedirs(plot_64_dir_path, exist_ok=True)

    for filename in os.listdir(data_dir_path):
        if filename.endswith(".csv"):
            file_path = os.path.join(data_dir_path, filename)
            file_base_name = os.path.splitext(filename)[0]

            df = pd.read_csv(file_path)
            # Skip if CSV is empty
            if df.empty:
                print(f"Skipping empty file: {filename}")
                continue

            name = file_base_name.removesuffix("_distances")
            plot_binned_frequencies(df, plots_dir_path, name)
            plot_binned_frequencies_64(df, plot_64_dir_path, name)


# Run with: python src/analysis/plot_distance_distribution_per_query.py
#
# Plot the distance jumps taken by each individual query.
#
# Expected .csv structure:
#   distance,frequency,skip_type
#   20118,6,lut
#   173266,1,lut
#   ...
# There is only one .csv per query.
if __name__ == "__main__":
    # Input
    data_dir_path = "res/data/analysis/distance_distribution_per_query/track/cutoff=0"
    result_dir_path = "res/plots/analysis/distance_distribution_per_query/track/cutoff=0"

    plot_all(data_dir_path, result_dir_path)

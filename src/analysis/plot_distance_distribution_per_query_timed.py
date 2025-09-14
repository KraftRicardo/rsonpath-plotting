import os

import matplotlib.pyplot as plt
import pandas as pd

COLOR_1 = "#458AF5"
COLOR_2 = "#F5BA45"


def plot_binned_frequencies_64(df: pd.DataFrame, result_dir_path: str, file_base_name: str) -> None:
    if df.empty:
        print(f"Skipping plot for {file_base_name}: empty DataFrame")
        return

    bin_edges = [
        1, 2, 65, 129, 193, 257, 321, 385, 449, 513, 577, 641, 705, 769,
        833, 897, 961, 1025, 1089, 1153, 1217, 1281, 1345, 1409, 1473,
        1537, 1601, 1665, 1729, 1793, 1857, 1921, 1985, 2049, float("inf")
    ]
    bin_labels = [
        "1", "2–64", "65–128", "129–192", "193–256", "257–320", "321–384",
        "385–448", "449–512", "513–576", "577–640", "641–704", "705–768",
        "769–832", "833–896", "897–960", "961–1024", "1025–1088", "1089–1152",
        "1153–1216", "1217–1280", "1281–1344", "1345–1408", "1409–1472",
        "1473–1536", "1537–1600", "1601–1664", "1665–1728", "1729–1792",
        "1793–1856", "1857–1920", "1921–1984", "1985–2048", "REST"
    ]

    # Bin distances
    df['custom_bin'] = pd.cut(
        df['DISTANCE'],
        bins=bin_edges,
        labels=bin_labels,
        right=True,
        include_lowest=True
    )

    # Group for frequency bars
    binned_df = df.groupby(['custom_bin', 'SKIP_TYPE'], observed=False)['FREQUENCY'].sum().unstack(
        fill_value=0).reset_index()

    # Group for time line plot
    time_df = df.groupby('custom_bin', observed=False)['TIME_NANOS'].sum().reset_index()

    # Merge for plotting
    merged_df = pd.merge(binned_df, time_df, on='custom_bin', how='left')
    total_time = merged_df['TIME_NANOS'].sum()
    merged_df['TIME_PERCENTAGE'] = (merged_df['TIME_NANOS'] / total_time) * 100

    total_frequency = merged_df.get('lut', pd.Series(0)).sum() + merged_df.get('ite', pd.Series(0)).sum()
    merged_df['LUT_PERCENTAGE'] = (merged_df.get('lut', 0) / total_frequency) * 100
    merged_df['ITE_PERCENTAGE'] = (merged_df.get('ite', 0) / total_frequency) * 100

    # Plot
    plt.figure(figsize=(14, 8))
    bar_width = 0.4
    x_labels = merged_df['custom_bin'].astype(str)
    x = list(range(len(x_labels)))

    plt.bar(
        [i - bar_width / 2 for i in x],
        merged_df['LUT_PERCENTAGE'],
        width=bar_width,
        label='LUT (Frequency %)',
        color=COLOR_1,
        align='center'
    )
    plt.bar(
        [i + bar_width / 2 for i in x],
        merged_df['ITE_PERCENTAGE'],
        width=bar_width,
        label='ITE (Frequency %)',
        color=COLOR_2,
        align='center'
    )

    # Line plot (time percentage)
    plt.plot(x, merged_df['TIME_PERCENTAGE'], marker='o', linestyle='-', color='black', label='Time % (Total)',
             linewidth=2)

    # Optional: Annotate time % on line
    for i, perc in enumerate(merged_df['TIME_PERCENTAGE']):
        if perc > 0.5:
            plt.text(i, perc + 1, f"{perc:.1f}%", ha='center', va='bottom', fontsize=9, color='black')

    # Annotate bar values
    for i in x:
        lut_val = merged_df.get('lut', pd.Series([0] * len(merged_df)))[i]
        if lut_val > 0:
            plt.text(i - bar_width / 2, merged_df['LUT_PERCENTAGE'][i] + 0.5, f"{lut_val:.0f}",
                     ha='center', fontsize=9, color=COLOR_1, rotation=90)
        ite_val = merged_df.get('ite', pd.Series([0] * len(merged_df)))[i]
        if ite_val > 0:
            plt.text(i + bar_width / 2, merged_df['ITE_PERCENTAGE'][i] + 0.5, f"{ite_val:.0f}",
                     ha='center', fontsize=9, color=COLOR_2, rotation=90)

    # Extract number of repetitions (assumed constant)
    repetitions = df['REPETITIONS'].iloc[0] if 'REPETITIONS' in df.columns else -1

    plt.xticks(x, x_labels, rotation=90)
    plt.xlabel('Distance (Binned)')
    plt.ylabel('Percentage of Total Frequency / Time')

    plt.title(
        f'Distance Distribution: {file_base_name}\n'
        f'Total Frequency: {total_frequency}, Total Time: {total_time:.0f} ns, Repetitions: {repetitions}'
    )

    plt.legend()
    plt.grid(True, axis='y')

    # Save
    out_path = f"{result_dir_path}/{file_base_name}.png"
    plt.tight_layout()
    plt.savefig(out_path)
    print(f"Generated: {out_path}")
    plt.close()


def plot_all(data_dir_path: str, result_dir_path: str):
    plot_64_dir_path = os.path.join(result_dir_path, "plots_64")
    os.makedirs(plot_64_dir_path, exist_ok=True)

    for filename in os.listdir(data_dir_path):
        if filename.endswith(".csv"):
            file_path = os.path.join(data_dir_path, filename)
            file_base_name = os.path.splitext(filename)[0]

            df = pd.read_csv(file_path)

            # Do not plot if empty
            if len(df) == 0:
                print(f" - NO PLOT: {file_path} has 0 rows")
                continue

            name = file_base_name.removesuffix("_distances")
            plot_binned_frequencies_64(df, plot_64_dir_path, name)


# Run with: python src/analysis/plot_distance_distribution_per_query_timed.py
#
# Plot the distance jumps taken by each individual query.
#
# Expected .csv structure:
#   DISTANCE,FREQUENCY,SKIP_TYPE,TIME_NANOS,REPETITIONS
#   2165,75,ite,21678,1
#   2234,12,ite,3957,1
#   2552,1,ite,200,1
#   ...
# There is only one .csv per query.
if __name__ == "__main__":
    # Input
    data_dir_path = "res/data/analysis/distance_distribution_per_query/track_timed/cutoff=0"
    result_dir_path = "res/plots/analysis/distance_distribution_per_query/track_timed/cutoff=0"

    plot_all(data_dir_path, result_dir_path)

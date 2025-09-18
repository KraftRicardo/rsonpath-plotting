import os

import matplotlib.pyplot as plt
import pandas as pd


def plot(
        rq_legacy_skip_time: str,
        rq_legacy_time_csv: str,
        rq_lut_time_csv: str,
        counter_folder: str,
        cutoffs: list,
        result_dir: str,
):
    legacy_skip_data = pd.read_csv(rq_legacy_skip_time)
    legacy_data = pd.read_csv(rq_legacy_time_csv)
    lut_data = pd.read_csv(rq_lut_time_csv)

    # Convert QUERY_ID to string type to treat as categorical data
    legacy_data['QUERY_ID'] = legacy_data['QUERY_ID'].astype(str)
    legacy_skip_data['QUERY_ID'] = legacy_skip_data['QUERY_ID'].astype(str)
    lut_data['QUERY_ID'] = lut_data['QUERY_ID'].astype(str)
    lut_data['QUERY_TIME_SECONDS'] = pd.to_numeric(lut_data['QUERY_TIME_SECONDS'], errors='coerce')

    # Merge the two dataframes on JSON and QUERY_ID to calculate the optimal time
    merged_data = pd.merge(
        legacy_data,
        legacy_skip_data[['JSON', 'QUERY_ID', 'SKIP_TIME_NANO_SECONDS']],
        on=['JSON', 'QUERY_ID'],
        how='left'
    )

    # Calculate the optimal query time (OPTIMAL_TIME)
    merged_data['OPTIMAL_TIME'] = merged_data['QUERY_TIME_SECONDS'] - (merged_data['SKIP_TIME_NANO_SECONDS'] / 1e9)

    # Ensure the result directory exists
    os.makedirs(result_dir, exist_ok=True)

    # Create a colormap with enough distinct colors for the given cutoff values
    cmap = plt.cm.get_cmap('tab20', len(cutoffs))  # Using 'tab20' colormap
    colors = [cmap(i) for i in range(len(cutoffs))]

    # Create a plot for each JSON
    for json_name, group in merged_data.groupby('JSON'):
        fig, ax = plt.subplots(2, 1, figsize=(10, 12))  # 2 rows, 1 column

        # --- Plot 2: Skip Percentages (Bar Plot) ---
        counter_file = os.path.join(counter_folder, f"{json_name}.csv")

        if os.path.exists(counter_file):
            counter_data = pd.read_csv(counter_file)
            counter_data['QUERY_ID'] = counter_data['QUERY_ID'].astype(str)
            counter_data_sorted = counter_data.sort_values(by='SKIP_PERCENTAGE', ascending=True)

            ax[1].bar(counter_data_sorted['QUERY_ID'], counter_data_sorted['SKIP_PERCENTAGE'])
            sorted_query_ids = counter_data_sorted['QUERY_ID'].values

            ax[1].set_title(f'Skip Percentage per Query ID for {json_name}')
            ax[1].set_xlabel('Query ID')
            ax[1].set_ylabel('Skip Percentage')
            ax[1].tick_params(axis='x', rotation=45)
            ax[1].grid(True)
        else:
            sorted_query_ids = group['QUERY_ID'].unique()

        # --- Plot 1: Query Times (Line Plot) ---
        group_sorted = group.drop_duplicates(subset=['QUERY_ID'])
        group_sorted = group_sorted.set_index('QUERY_ID').reindex(sorted_query_ids).reset_index()

        # Original legacy time
        ax[0].plot(group_sorted['QUERY_ID'], group_sorted['QUERY_TIME_SECONDS'], marker='o', linestyle='-', color='red',
                   label='Original Query Time')

        # Optimal time (dashed line)
        ax[0].plot(
            group_sorted['QUERY_ID'],
            group_sorted['OPTIMAL_TIME'],
            marker='o',
            linestyle='--',
            color='red',
            label='Optimal Time'
        )

        # LUT time (solid lines)
        lut_subset = lut_data[lut_data['JSON'] == json_name]
        for i, cutoff in enumerate(cutoffs):
            lut_cutoff_group = lut_subset[lut_subset['CUTOFF'] == f"{cutoff}"]
            lut_cutoff_group = lut_cutoff_group.set_index('QUERY_ID').reindex(sorted_query_ids).reset_index()
            ax[0].plot(
                lut_cutoff_group['QUERY_ID'],
                lut_cutoff_group['QUERY_TIME_SECONDS'],
                marker='x',
                linestyle='-',
                color=colors[i],
                label=f'LUT Time (CUTOFF={cutoff})'
            )

        ax[0].set_title(f'Query Time for {json_name}')
        ax[0].set_xlabel('QUERY_ID')
        ax[0].set_ylabel('Query Time (Seconds)')
        ax[0].tick_params(axis='x', rotation=45)
        ax[0].grid(True)
        ax[0].legend()

        plt.tight_layout()
        plot_filename = os.path.join(result_dir, f"{json_name}_count.png")
        plt.savefig(plot_filename)
        print(f"Generated: {plot_filename}")

        # --- Save "short" version with only top plot ---
        short_dir = os.path.join(result_dir, "short")
        os.makedirs(short_dir, exist_ok=True)

        fig_short, ax_short = plt.subplots(figsize=(10, 6))

        # Replot only the top plot here
        ax_short.plot(group_sorted['QUERY_ID'], group_sorted['QUERY_TIME_SECONDS'],
                      marker='o', linestyle='-', color='red', label='Original Query Time')

        ax_short.plot(group_sorted['QUERY_ID'], group_sorted['OPTIMAL_TIME'],
                      marker='o', linestyle='--', color='red', label='Optimal Time')

        lut_subset = lut_data[lut_data['JSON'] == json_name]
        for i, cutoff in enumerate(cutoffs):
            lut_cutoff_group = lut_subset[lut_subset['CUTOFF'] == f"{cutoff}"]
            lut_cutoff_group = lut_cutoff_group.set_index('QUERY_ID').reindex(sorted_query_ids).reset_index()
            ax_short.plot(
                lut_cutoff_group['QUERY_ID'],
                lut_cutoff_group['QUERY_TIME_SECONDS'],
                marker='x', linestyle='-', color=colors[i],
                label=f'LUT Time (CUTOFF={cutoff})'
            )

        ax_short.set_title(f'Query Time for {json_name}')
        ax_short.set_xlabel('QUERY_ID')
        ax_short.set_ylabel('Query Time (Seconds)')
        ax_short.tick_params(axis='x', rotation=45)
        ax_short.grid(True)
        ax_short.legend()

        plt.tight_layout()
        short_filename = os.path.join(short_dir, f"{json_name}_count_short.png")
        plt.savefig(short_filename)
        print(f"Generated short plot: {short_filename}")
        plt.close(fig_short)

        # Close the original figure
        plt.close(fig)


# Run with: python src/speed/plot_optimal.py
#
# This code expects following structure for the given .csv files:
# optimal_time_csv:
#   JSON,QUERY_ID,QUERY_TEXT,SKIP_TIME_NANO_SECONDS
#   crossref1_(551MB),1,$.items[2].resource.primary.URL,66067533.6
#   crossref1_(551MB),1,$.items[2].resource.primary.URL,66067022.6
#   ...
# rq_legacy_time_csv:
#   JSON,QUERY_ID,QUERY_TEXT,QUERY_TIME_SECONDS
#   crossref1_(551MB),1,$.items[2].resource.primary.URL,0.13103
#   crossref1_(551MB),2,$.items[*].URL,0.13692
#   ...
# rq_lut_time_csv:
#   JSON,CUTOFF,QUERY_ID,QUERY_TEXT,QUERY_TIME_SECONDS
#   crossref1_(551MB),0,1,$.items[2].resource.primary.URL,0.00300
#   crossref1_(551MB),0,2,$.items[*].URL,0.03756
#   ...
# "counter_folder" is the path to the folder that contains the skip-counter information in .csv files with this
# structure:
#   QUERY_ID,QUERY_TEXT,RESULT,SKIP_PERCENTAGE
#   1,$..freeShipping,230089,0
#   2,$.products[*].videoChapters,769,0.09227438889806847
#   3,$.products[*].additionalFeatures[*],61098,0.10084738573733328
#   ...
# the name of this .csv is "COUNTER_bestbuy_large_record_(1GB).csv" and there needs to be one .csv per different JSON
# that was analyzed.
# "result_dir" is the path to the folder where the plots will be saved.
# "cutoffs" defines which cutoff will be covered in the plots
if __name__ == "__main__":
    # Input
    rq_legacy_skip_time = "res/data/speed/server/rq_legacy_skip_time/query_count/rq_legacy_skip_time_repetitions=20.csv"
    rq_legacy_time_csv = "res/data/speed/server/rq_legacy/query_count/rq_legacy_time_repetitions=20.csv"
    rq_lut_time_csv = "res/data/speed/server/rq_lut/query_count/rq_lut_time_repetitions=20.csv"
    result_dir = "res/plots/speed/server/optimal"
    counter_folder = "res/data/analysis/query"

    # cutoffs = [0, 64, 128, 192, 256, 320, 384, 448, 512, 576, 640, 1024, 2048, 4096, 8192, 1099511627776]
    # cutoffs = [0, 640, 1024]
    # cutoffs = [1024]
    # cutoffs = [0, 1024]
    # cutoffs = [1099511627776]
    # cutoffs = [4096, 8192,]
    cutoffs = []
    plot(rq_legacy_skip_time, rq_legacy_time_csv, rq_lut_time_csv, counter_folder, cutoffs, result_dir)

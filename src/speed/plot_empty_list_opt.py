import os
import pandas as pd
import matplotlib.pyplot as plt


def plot(
        rq_legacy_time_csv: str,
        rq_legacy_empty_list_opt_off_time_csv: str,
        counter_folder: str,
        result_dir: str,
):
    legacy_data = pd.read_csv(rq_legacy_time_csv)
    legacy_data_2 = pd.read_csv(rq_legacy_empty_list_opt_off_time_csv)

    # Convert QUERY_ID to string type
    legacy_data['QUERY_ID'] = legacy_data['QUERY_ID'].astype(str)
    legacy_data_2['QUERY_ID'] = legacy_data_2['QUERY_ID'].astype(str)

    # Ensure the result directory exists
    os.makedirs(result_dir, exist_ok=True)

    # Plot for each JSON file
    for json_name, group in legacy_data.groupby('JSON'):
        fig, ax = plt.subplots(2, 1, figsize=(10, 12))  # 2 rows, 1 column

        # Load corresponding group from legacy_data_2
        group_2 = legacy_data_2[legacy_data_2['JSON'] == json_name]

        # --- Plot 2: Skip Percentages ---
        counter_file = os.path.join(counter_folder, f"{json_name}.csv")
        if os.path.exists(counter_file):
            counter_data = pd.read_csv(counter_file)
            counter_data['QUERY_ID'] = counter_data['QUERY_ID'].astype(str)
            counter_data_sorted = counter_data.sort_values(by='SKIP_PERCENTAGE', ascending=True)
            sorted_query_ids = counter_data_sorted['QUERY_ID'].values

            ax[1].bar(counter_data_sorted['QUERY_ID'], counter_data_sorted['SKIP_PERCENTAGE'])
            ax[1].set_title(f'Skip Percentage per Query ID for {json_name}')
            ax[1].set_xlabel('Query ID')
            ax[1].set_ylabel('Skip Percentage')
            ax[1].tick_params(axis='x', rotation=45)
            ax[1].grid(True)
        else:
            sorted_query_ids = group['QUERY_ID'].unique()

        # --- Plot 1: Query Times ---
        # Align both datasets to sorted QUERY_IDs
        group_sorted = group.drop_duplicates(subset=['QUERY_ID']).set_index('QUERY_ID').reindex(sorted_query_ids).reset_index()
        group_2_sorted = group_2.drop_duplicates(subset=['QUERY_ID']).set_index('QUERY_ID').reindex(sorted_query_ids).reset_index()

        # Plot legacy
        ax[0].plot(group_sorted['QUERY_ID'], group_sorted['QUERY_TIME_SECONDS'],
                   marker='o', linestyle='-', color='red', label='rq-legacy')

        # Plot legacy (empty list opt OFF)
        ax[0].plot(group_2_sorted['QUERY_ID'], group_2_sorted['QUERY_TIME_SECONDS'],
                   marker='o', linestyle='-', color='blue', label='rq-legacy (empty-list-opt: OFF)')

        ax[0].set_title(f'Query Time Comparison for {json_name}')
        ax[0].set_xlabel('QUERY_ID')
        ax[0].set_ylabel('Query Time (Seconds)')
        ax[0].tick_params(axis='x', rotation=45)
        ax[0].grid(True)
        ax[0].legend()

        # Save the figure
        plt.tight_layout()
        plot_filename = os.path.join(result_dir, f"{json_name}_combined_plot.png")
        plt.savefig(plot_filename)
        print(f"Generated: {plot_filename}")
        plt.close()

# Run with: python src/speed/plot_empty_list_opt.py
#
# This script compares query execution times between:
#   1. rq-legacy (with empty-list optimization enabled), and
#   2. rq-legacy (with empty-list optimization explicitly disabled).
#
# INPUTS:
#   - rq_legacy_time_csv:
#       CSV file containing query timings for rq-legacy with empty-list optimization ON.
#       Expected columns: JSON, QUERY_ID, QUERY_TIME_SECONDS, REPETITIONS
#       Example rows:
#           JSON,QUERY_ID,QUERY_TIME_SECONDS,REPETITIONS
#           bestbuy_large_record_(1GB),1,1.39657,20
#           bestbuy_large_record_(1GB),2,0.12507,20
#
#   - rq_legacy_empty_list_opt_off_time_csv:
#       CSV file containing query timings for rq-legacy with empty-list optimization OFF.
#       Same format and JSON/QUERY_IDs as above.
#
#   - counter_folder:
#       Directory with per-JSON CSV files containing skip statistics.
#       Each file is named <JSON>.csv and must contain columns:
#           QUERY_ID, SKIP_PERCENTAGE
#
#   - result_dir:
#       Directory where the output plots will be saved. Will be created if it doesn’t exist.
#
# OUTPUT:
#   For each JSON value in the input CSVs, one PNG file is generated in result_dir:
#       <JSON>_combined_plot.png
#
#   Each figure has two rows:
#       Row 1: Line plot of query execution times:
#              - Red solid line with circles = rq-legacy (default, opt ON)
#              - Blue solid line with circles = rq-legacy (empty-list-opt OFF)
#       Row 2: Bar plot of skip percentage per query (if counter data is available).
#
# This allows direct comparison of the effect of disabling empty-list optimization.
if __name__ == "__main__":
    rq_legacy_time_csv = "res/data/speed/server/rq_legacy/query_count/rq_legacy_time_repetitions=20.csv"
    rq_legacy_empty_list_opt_off_time_csv = "res/data/speed/server/rq_legacy_empty_list_opt_off/rq_legacy_empty_list_opt_off_time_repetitions=20.csv"
    result_dir = "res/plots/speed/server/empty_list_opt"
    counter_folder = "res/data/analysis/query"

    plot(rq_legacy_time_csv, rq_legacy_empty_list_opt_off_time_csv, counter_folder, result_dir)

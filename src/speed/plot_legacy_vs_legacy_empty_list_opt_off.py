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
        counter_file = os.path.join(counter_folder, f"COUNTER_{json_name}.csv")

        if os.path.exists(counter_file):
            counter_data = pd.read_csv(counter_file)
            counter_data['QUERY_NAME'] = counter_data['QUERY_NAME'].astype(str)
            counter_data_sorted = counter_data.sort_values(by='TOTAL_PERCENT_SKIP', ascending=True)
            sorted_query_ids = counter_data_sorted['QUERY_NAME'].values

            ax[1].bar(counter_data_sorted['QUERY_NAME'], counter_data_sorted['TOTAL_PERCENT_SKIP'])
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

# Run with: python src/speed/plot_legacy_vs_legacy_empty_list_opt_off.py
#
# This code expects following structure for the given .csv files:
# rq_legacy_time_csv and rq_legacy_empty_list_opt_off_time_csv:
#   JSON,QUERY_ID,QUERY_TEXT,QUERY_TIME_SECONDS
#   crossref1_(551MB),1,$.items[2].resource.primary.URL,0.13103
#   crossref1_(551MB),2,$.items[*].URL,0.13692
#   ...
# "counter_folder" is the path to the folder that contains the skip-counter information in .csv files with this
# structure:
#   FILENAME,QUERY_NAME,LUT_PERCENT_SKIP,ITE_PERCENT_SKIP,TOTAL_PERCENT_SKIP,LUT_COUNT,ITE_COUNT,TOTAL_COUNT,LUT_DISTANCE,ITE_DISTANCE,TOTAL_DISTANCE,FILE_SIZE
#   bestbuy_large_record_(1GB),1,0.999999,0.000000,0.999999,6,0,6,1044618238,0,1044618238,1044619305
#   bestbuy_large_record_(1GB),2,0.827555,0.000000,0.827555,363995,0,363995,864479540,0,864479540,1044619305
#   ...
# the name of this .csv is "COUNTER_bestbuy_large_record_(1GB).csv" and there needs to be one .csv per different JSON
# that was analyzed.
# "result_dir" is the path to the folder where the plots will be saved.
if __name__ == "__main__":
    rq_legacy_time_csv = "res/data/speed/server/rq_legacy/rq_legacy_time_repetitions=10.csv"
    rq_legacy_empty_list_opt_off_time_csv = "res/data/speed/server/rq_legacy_empty_list_opt_off/rq_legacy_empty_list_opt_off_time_repetitions=10.csv"
    # rq_legacy_empty_list_opt_off_time_csv = "res/data/speed/server/rq_legacy2/rq_legacy_time.csv"
    result_dir = "res/plots/speed/server/legacy_vs_legacy_empty_list_opt_off"
    counter_folder = "res/data/analysis/skip_counter"

    plot(rq_legacy_time_csv, rq_legacy_empty_list_opt_off_time_csv, counter_folder, result_dir)

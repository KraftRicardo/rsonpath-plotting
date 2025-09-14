import os

import matplotlib.pyplot as plt
import pandas as pd


def plot(
        rq_legacy_skip_time: str,
        rq_legacy_time_csv: str,
        rq_lut_time_csv: str,
        rq_text_time_csv: str,  # NEW
        counter_folder: str,
        cutoffs: list,
        result_dir: str,
):
    legacy_skip_df = pd.read_csv(rq_legacy_skip_time)
    legacy_df = pd.read_csv(rq_legacy_time_csv)
    lut_df = pd.read_csv(rq_lut_time_csv)
    serde_df = pd.read_csv(rq_text_time_csv)  # NEW

    # Convert QUERY_ID to string type
    legacy_df['QUERY_ID'] = legacy_df['QUERY_ID'].astype(str)
    legacy_skip_df['QUERY_ID'] = legacy_skip_df['QUERY_ID'].astype(str)
    lut_df['QUERY_ID'] = lut_df['QUERY_ID'].astype(str)
    lut_df['CUTOFF'] = lut_df['CUTOFF'].astype(str)
    lut_df['QUERY_TIME_SECONDS'] = pd.to_numeric(lut_df['QUERY_TIME_SECONDS'], errors='coerce')
    serde_df['QUERY_ID'] = serde_df['QUERY_ID'].astype(str)  # NEW

    # Merge legacy + skip
    merged_data = pd.merge(
        legacy_df,
        legacy_skip_df[['JSON', 'QUERY_ID', 'SKIP_TIME_NANO_SECONDS']],
        on=['JSON', 'QUERY_ID'],
        how='left'
    )
    merged_data['OPTIMAL_TIME'] = merged_data['QUERY_TIME_SECONDS'] - (merged_data['SKIP_TIME_NANO_SECONDS'] / 1e9)

    os.makedirs(result_dir, exist_ok=True)

    cmap = plt.get_cmap('tab20', len(cutoffs))
    colors = [cmap(i) for i in range(len(cutoffs))]

    for json_name, group in merged_data.groupby('JSON'):
        fig, ax = plt.subplots(2, 1, figsize=(10, 12))

        # Skip Percentage Bar Plot
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

        # Query Time Line Plot
        group_sorted = group.drop_duplicates(subset=['QUERY_ID'])
        group_sorted = group_sorted.set_index('QUERY_ID').reindex(sorted_query_ids).reset_index()

        # Legacy times
        ax[0].plot(group_sorted['QUERY_ID'], group_sorted['QUERY_TIME_SECONDS'],
                   marker='o', linestyle='-', color='red', label='Original Query Time')

        ax[0].plot(group_sorted['QUERY_ID'], group_sorted['OPTIMAL_TIME'],
                   marker='o', linestyle='--', color='red', label='Optimal Time')

        # Serde times (NEW, striped blue line)
        serde_subset_df = serde_df[serde_df['JSON'] == json_name]
        serde_subset_df = serde_subset_df.set_index('QUERY_ID').reindex(sorted_query_ids).reset_index()
        ax[0].plot(
            serde_subset_df['QUERY_ID'],
            serde_subset_df['QUERY_TIME_SECONDS'],
            marker='s',
            linestyle=':',
            color='blue',
            label='Serde'
        )

        # LUT times
        lut_subset_df = lut_df[lut_df['JSON'] == json_name]
        for i, cutoff in enumerate(cutoffs):
            lut_cutoff_group = lut_subset_df[lut_subset_df['CUTOFF'] == f"{cutoff}"]
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
        plot_filename = os.path.join(result_dir, f"{json_name}_node.png")
        plt.savefig(plot_filename)
        print(f"Generated: {plot_filename}")
        plt.close()



# Run with: python src/speed/plot_optimal_node.py
if __name__ == "__main__":
    # Input
    rq_legacy_skip_time = "res/data/speed/server/rq_legacy_skip_time/query_count/rq_legacy_skip_time_repetitions=20.csv"
    rq_legacy_time_csv = "res/data/speed/server/rq_legacy/query_node/rq_legacy_time_node_repetitions=20.csv"
    rq_lut_time_csv = "res/data/speed/server/rq_lut/query_node/rq_lut_time_node_repetitions=20.csv"
    rq_serde_time_csv = "res/data/speed/server/serde/serde_time_repetitions=20.csv"  # NEW
    result_dir = "res/plots/speed/server/optimal_node"
    counter_folder = "res/data/analysis/query"

    # cutoffs = [0, 64, 128, 192, 256, 320, 384, 448, 512, 576, 640, 1024, 2048, 4096, 8192, 1099511627776]
    cutoffs = [0, 1024]
    plot(rq_legacy_skip_time, rq_legacy_time_csv, rq_lut_time_csv, rq_serde_time_csv, counter_folder, cutoffs, result_dir)

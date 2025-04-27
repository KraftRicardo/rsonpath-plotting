import pandas as pd
import matplotlib.pyplot as plt
import os
import matplotlib.cm as cm

def plot(rq_speed_csv: str, cutoff_csv: str, result_dir: str, counter_folder: str, cutoff_values_to_plot: list):
    # Load the CSV data (original times)
    data = pd.read_csv(rq_speed_csv)

    # Convert QUERY_ID to string type to treat as categorical data
    data['QUERY_ID'] = data['QUERY_ID'].astype(str)

    # Load the CSV data (cutoff times)
    cutoff_data = pd.read_csv(cutoff_csv)

    # Ensure that QUERY_ID is treated as a string in both dataframes
    cutoff_data['QUERY_ID'] = cutoff_data['QUERY_ID'].astype(str)

    # Merge the two dataframes on JSON and QUERY_ID to calculate the optimal time
    merged_data = pd.merge(data, cutoff_data[['JSON', 'QUERY_ID', 'CUTOFF', 'SKIP_TIME_NANO_SECONDS']],
                           on=['JSON', 'QUERY_ID'], how='left')

    # Calculate the optimal query time (OPTIMAL_TIME)
    merged_data['OPTIMAL_TIME'] = merged_data['QUERY_TIME_SECONDS'] - (merged_data['SKIP_TIME_NANO_SECONDS'] / 1e9)

    # Group data by JSON
    json_groups = merged_data.groupby('JSON')

    # Ensure the result directory exists
    os.makedirs(result_dir, exist_ok=True)

    # Create a colormap with enough distinct colors for the given cutoff values
    cmap = plt.cm.get_cmap('tab20', len(cutoff_values_to_plot))  # Using 'tab20' colormap
    colors = [cmap(i) for i in range(len(cutoff_values_to_plot))]

    # Create a plot for each JSON
    for json_name, group in json_groups:
        fig, ax = plt.subplots(2, 1, figsize=(10, 12))  # 2 rows, 1 column

        # --- Plot 2: Skip Percentages (Bar Plot) ---
        # Get the corresponding COUNTER file for the JSON
        counter_file = os.path.join(counter_folder, f"COUNTER_{json_name}.csv")  # Use the same JSON name

        if os.path.exists(counter_file):
            # Read the COUNTER file
            counter_data = pd.read_csv(counter_file)

            # Ensure QUERY_ID is treated as a string
            counter_data['QUERY_NAME'] = counter_data['QUERY_NAME'].astype(str)

            # Sort the data by TOTAL_PERCENT_SKIP in ascending order
            counter_data_sorted = counter_data.sort_values(by='TOTAL_PERCENT_SKIP', ascending=True)

            # Create the bar plot for skip percentage
            ax[1].bar(counter_data_sorted['QUERY_NAME'], counter_data_sorted['TOTAL_PERCENT_SKIP'])

            # Save the sorted x-axis order from the second plot for later use
            sorted_query_ids = counter_data_sorted['QUERY_NAME'].values

            # Title and labels for the second plot
            ax[1].set_title(f'Skip Percentage per Query ID for {json_name}')
            ax[1].set_xlabel('Query ID')
            ax[1].set_ylabel('Skip Percentage')
            ax[1].tick_params(axis='x', rotation=45)
            ax[1].grid(True)

        # --- Plot 1: Query Times (Line Plot) ---
        # Remove duplicates from the group data (if any) by keeping the first occurrence
        group_sorted = group.drop_duplicates(subset=['QUERY_ID', 'CUTOFF'])

        # Reindex by both QUERY_ID and CUTOFF, ensuring the same order as the second plot
        group_sorted = group_sorted.set_index(['QUERY_ID', 'CUTOFF']).reindex(
            pd.MultiIndex.from_product([sorted_query_ids, cutoff_values_to_plot], names=['QUERY_ID', 'CUTOFF'])
        ).reset_index()

        # Plot the original query time (without any adjustments)
        ax[0].plot(group_sorted['QUERY_ID'], group_sorted['QUERY_TIME_SECONDS'], marker='o', linestyle='-', color='red', label='Original Query Time')

        # Plot the optimal times for the specified cutoff values
        for i, cutoff in enumerate(cutoff_values_to_plot):
            cutoff_group = group_sorted[group_sorted['CUTOFF'] == cutoff]
            color = colors[i]  # Get the color from the colormap

            # Plot each optimal time with the respective color
            ax[0].plot(cutoff_group['QUERY_ID'], cutoff_group['OPTIMAL_TIME'], marker='o', linestyle='--', color=color, label=f'Optimal Time (CUTOFF={cutoff})')

        # Title and labels for the first plot
        ax[0].set_title(f'Query Time for {json_name}')
        ax[0].set_xlabel('QUERY_ID')
        ax[0].set_ylabel('Query Time (Seconds)')
        ax[0].tick_params(axis='x', rotation=45)
        ax[0].grid(True)
        ax[0].legend()

        # Tight layout to avoid overlap
        plt.tight_layout()

        # Save the combined plot to the specified directory
        plot_filename = os.path.join(result_dir, f"{json_name}_combined_plot.png")
        plt.savefig(plot_filename)
        plt.close()  # Close the figure to avoid memory issues

if __name__ == "__main__":
    rq_speed_csv = ".a_extern_final_results/speed/optimal/bundled.csv"
    cutoff_csv = ".a_extern_final_results/speed/optimal/query.csv"  # specify the cutoff CSV file
    result_dir = ".a_extern_final_results/speed/optimal/plots"  # specify your desired directory
    counter_folder = ".a_extern_final_results/distance_cutoff_evaluation/skip_counter"  # specify the folder containing COUNTER files

    # Specify the cutoff values you want to plot
    cutoff_values_to_plot = [0, 64, 128, 512, 2048]

    plot(rq_speed_csv, cutoff_csv, result_dir, counter_folder, cutoff_values_to_plot)

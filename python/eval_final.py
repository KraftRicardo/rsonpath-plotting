import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def plot(input_dir_path: str):
    # Load CSVs
    build_df = pd.read_csv(f"{input_dir_path}/build.csv")
    query_df = pd.read_csv(f"{input_dir_path}/query.csv")

    # Group queries by JSON file
    json_files = query_df['JSON'].unique()

    for json_file in json_files:
        subset_build = build_df[build_df['JSON'] == json_file]
        subset_query = query_df[query_df['JSON'] == json_file]

        query_ids = subset_query['QUERY_ID'].unique()

        for query_id in query_ids:
            query_subset = subset_query[subset_query['QUERY_ID'] == query_id]

            plt.figure(figsize=(10, 8))

            query_text = query_subset['QUERY_TEXT'].iloc[0]
            plt.title(f'{json_file}\nQ:{query_id}= {query_text}', fontsize=20)  # Bigger title

            x = np.arange(0, 100)
            y_values = {}

            # Store y-values for each algorithm
            for algorithm in query_subset['ALGORITHM'].unique():
                avg_time = query_subset[query_subset['ALGORITHM'] == algorithm]['AVERAGE_TIME'].values[0]
                build_time = subset_build[subset_build['ALGORITHM'] == algorithm]['BUILD_TIME_SECONDS'].values[0]

                y = build_time + avg_time * x
                y_values[algorithm] = y

                plt.plot(x, y, label=algorithm)

            # Find intersection points and highlight them
            intersections = []

            for alg1, y1 in y_values.items():
                for alg2, y2 in y_values.items():
                    if alg1 != alg2:
                        for i in range(len(x) - 1):
                            if (y1[i] - y2[i]) * (y1[i + 1] - y2[i + 1]) < 0:
                                intersection_x = (x[i] + x[i + 1]) / 2
                                intersection_y = (y1[i] + y2[i]) / 2

                                plt.plot([intersection_x, intersection_x], [0, intersection_y], 'k--')

                                intersections.append(intersection_x)

            # Add markers and labels for intersections
            for intersection_x in intersections:
                plt.scatter(intersection_x, 0, color='blue', zorder=5)
                plt.text(intersection_x, -0.1, f'{intersection_x:.1f}',
                         ha='center', va='top', color='blue', fontsize=16)

            # Set x and y axis to start from 0, without white gaps
            plt.axis([0, 100, 0, max([max(y) for y in y_values.values()]) + 1])

            plt.xlabel('Repetitions', fontsize=16)
            plt.ylabel('Cumulative Time (s)', fontsize=16)
            plt.xticks(fontsize=16)
            plt.yticks(fontsize=16)
            plt.legend(fontsize=16)
            plt.grid(True)
            plt.tight_layout()
            plt.savefig(f'{input_dir_path}/plots/{json_file}_query_{query_id}.png')
            plt.close()

    print("Done generating plots!")

# Run with: python python/eval_final.py
if __name__ == "__main__":
    input_dir_path = ".a_extern_final_results/speed/final"

    plot(input_dir_path)

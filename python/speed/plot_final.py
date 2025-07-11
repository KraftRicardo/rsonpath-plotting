import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os


def plot(input_dir_path: str, omit_labels: bool = False):
    # Load CSVs
    build_df = pd.read_csv(f"{input_dir_path}/build.csv")
    query_df = pd.read_csv(f"{input_dir_path}/query.csv")

    # Create plots directory if it doesn't exist
    os.makedirs(f"{input_dir_path}/plots", exist_ok=True)

    # Group queries by JSON file
    json_files = query_df['JSON'].unique()

    for json_file in json_files:
        subset_build = build_df[build_df['JSON'] == json_file]
        subset_query = query_df[query_df['JSON'] == json_file]

        query_ids = subset_query['QUERY_ID'].unique()

        for query_id in query_ids:
            query_subset = subset_query[subset_query['QUERY_ID'] == query_id]

            plt.figure(figsize=(10, 8))

            if not omit_labels:
                query_text = query_subset['QUERY_TEXT'].iloc[0]
                plt.title(f'{json_file}\nQ:{query_id}= {query_text}', fontsize=20)

            x = np.arange(0, 100)
            y_values = {}

            for algorithm in query_subset['ALGORITHM'].unique():
                avg_time = query_subset[query_subset['ALGORITHM'] == algorithm]['AVERAGE_TIME'].values[0]
                build_time = subset_build[subset_build['ALGORITHM'] == algorithm]['BUILD_TIME_SECONDS'].values[0]

                y = build_time + avg_time * x
                y_values[algorithm] = y
                plt.plot(x, y, label=algorithm)

            # Find and mark intersection points
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

            for intersection_x in intersections:
                plt.scatter(intersection_x, 0, color='blue', zorder=5)
                if not omit_labels:
                    plt.text(intersection_x, -0.1, f'{intersection_x:.1f}',
                             ha='center', va='top', color='blue', fontsize=16)

            plt.axis([0, 100, 0, max([max(y) for y in y_values.values()]) + 1])

            if not omit_labels:
                plt.xlabel('Repetitions', fontsize=16)
                plt.ylabel('Cumulative Time (s)', fontsize=16)
                plt.xticks(fontsize=16)
                plt.yticks(fontsize=16)
                plt.legend(fontsize=16)
            else:
                plt.xlabel('', fontsize=16)
                plt.ylabel('', fontsize=16)
                plt.xticks([])
                plt.yticks([])

            plt.grid(True)
            plt.tight_layout()
            plt.savefig(f'{input_dir_path}/plots/{json_file}_query_{query_id}.png')
            print(f"Generated: {input_dir_path}/plots/{json_file}_query_{query_id}.png")
            plt.close()

    print("Done generating plots!")


# Run with: python python/speed/plot_final.py
#
# This function expects a build.csv and query.csv inside the "input_dir_path" directory with following structures:
# build.csv:
#   JSON,ALGORITHM,BUILD_TIME_SECONDS
#   google_map_large_record_(1.1GB),SERDE,11.21755
#   google_map_large_record_(1.1GB),rq-legacy,0
#   google_map_large_record_(1.1GB),rq-lut-cutoff-0,0.68384
#   google_map_large_record_(1.1GB),rq-lut-cutoff-512,0.49180
#   ...
# query.csv:
#   JSON,ALGORITHM,QUERY_ID,QUERY_TEXT,AVERAGE_TIME
#   google_map_large_record_(1.1GB),SERDE,0,$[4000].routes[*].bounds,0.00000
#   google_map_large_record_(1.1GB),rq-legacy,0,$[4000].routes[*].bounds,0.20223
#   google_map_large_record_(1.1GB),rq-lut-cutoff-0,0,$[4000].routes[*].bounds,0.05353
#   google_map_large_record_(1.1GB),rq-lut-cutoff-512,0,$[4000].routes[*].bounds,0.05474
#   ...
#
# Then the code will create a directory called "plots" in the directory defined by the variable "input_dir_path"
# and save there all generated images. Set omit_labels=True if you want to suppress labels.
if __name__ == "__main__":
    # Input
    input_dir_path = ".a_extern_final_results/speed/final"
    omit_labels = False

    plot(input_dir_path=input_dir_path, omit_labels=omit_labels)

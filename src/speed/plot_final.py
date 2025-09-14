import os

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt


def construct_input_csvs(
        serde_build_csv_path: str,
        rq_lut_build_csv_path: str,
        serde_query_csv_path: str,
        rq_lut_query_csv_path: str,
        rq_legacy_query_csv_path: str,
        cutoffs,
        output_dir: str,
):
    # --- BUILD CSV ---
    build_records = []

    # Serde build
    serde_build_df = pd.read_csv(serde_build_csv_path)
    for _, row in serde_build_df.iterrows():
        build_records.append({
            "JSON": row["JSON"],
            "ALGORITHM": "SERDE",
            "BUILD_TIME_SECONDS": row["BUILD_TIME_SECONDS"]
        })

    # RQ-LUT build (filter cutoffs)
    rq_lut_build_df = pd.read_csv(rq_lut_build_csv_path)
    rq_lut_build_df = rq_lut_build_df[rq_lut_build_df["CUTOFF"].astype(str).isin(cutoffs)]
    print(f"CUTOFF len:{len(rq_lut_build_df)}")
    for _, row in rq_lut_build_df.iterrows():
        build_records.append({
            "JSON": row["JSON"],
            "ALGORITHM": f"rq-lut-cutoff-{row['CUTOFF']}",
            "BUILD_TIME_SECONDS": row["BUILD_TIME_SECONDS"]
        })

    # RQ-legacy has no build cost
    for json_file in serde_build_df["JSON"].unique():
        build_records.append({
            "JSON": json_file,
            "ALGORITHM": "rq-legacy",
            "BUILD_TIME_SECONDS": 0.0
        })

    build_df = pd.DataFrame(build_records)
    build_df.to_csv(f"{output_dir}/build.csv", index=False)

    # --- QUERY CSV ---
    query_records = []

    # Serde query
    serde_query_df = pd.read_csv(serde_query_csv_path)
    for _, row in serde_query_df.iterrows():
        query_records.append({
            "JSON": row["JSON"],
            "ALGORITHM": "SERDE",
            "QUERY_ID": row["QUERY_ID"],
            "QUERY_TEXT": row["QUERY_TEXT"],
            "AVERAGE_TIME": row["QUERY_TIME_SECONDS"]
        })

    # RQ-lut query (filter cutoffs)
    rq_lut_query_df = pd.read_csv(rq_lut_query_csv_path)
    rq_lut_query_df = rq_lut_query_df[rq_lut_query_df["CUTOFF"].astype(str).isin(cutoffs)]
    print(f"CUTOFF len:{len(rq_lut_query_df)}")
    for _, row in rq_lut_query_df.iterrows():
        query_records.append({
            "JSON": row["JSON"],
            "ALGORITHM": f"rq-lut-cutoff-{row['CUTOFF']}",
            "QUERY_ID": row["QUERY_ID"],
            "QUERY_TEXT": row["QUERY_TEXT"],
            "AVERAGE_TIME": row["QUERY_TIME_SECONDS"]
        })

    # RQ-legacy query
    rq_legacy_query_df = pd.read_csv(rq_legacy_query_csv_path)
    for _, row in rq_legacy_query_df.iterrows():
        query_records.append({
            "JSON": row["JSON"],
            "ALGORITHM": "rq-legacy",
            "QUERY_ID": row["QUERY_ID"],
            "QUERY_TEXT": row["QUERY_TEXT"],
            "AVERAGE_TIME": row["QUERY_TIME_SECONDS"]
        })

    query_df = pd.DataFrame(query_records)
    query_df.to_csv(f"{output_dir}/query.csv", index=False)

    print("Generated build.csv and query.csv ✅")


def plot(input_dir_path: str, result_dir_path: str, omit_labels: bool = False):
    os.makedirs(result_dir_path, exist_ok=True)

    # Load CSVs
    build_df = pd.read_csv(f"{input_dir_path}/build.csv")
    query_df = pd.read_csv(f"{input_dir_path}/query.csv")

    # Group queries by JSON file
    json_files = query_df['JSON'].unique()
    for json_file in json_files:
        build_df_per_json = build_df[build_df['JSON'] == json_file]
        query_df_per_json = query_df[query_df['JSON'] == json_file]

        query_ids = query_df_per_json['QUERY_ID'].unique()
        # Group by query id
        for query_id in query_ids:
            query_df_per_json_query = query_df_per_json[query_df_per_json['QUERY_ID'] == query_id]

            plt.figure(figsize=(10, 8))

            if not omit_labels:
                query_text = query_df_per_json_query['QUERY_TEXT'].iloc[0]
                plt.title(f'{json_file}\nQ:{query_id}= {query_text}', fontsize=20)

            x = np.arange(0, 100)
            y_values = {}

            for algorithm in query_df_per_json_query['ALGORITHM'].unique():
                avg_time = query_df_per_json_query[query_df_per_json_query['ALGORITHM'] == algorithm]['AVERAGE_TIME'].values[0]
                build_time = build_df_per_json[build_df_per_json['ALGORITHM'] == algorithm]['BUILD_TIME_SECONDS'].values[0]

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
            save_path = f'{result_dir_path}/{json_file}_query_{query_id}.png'
            plt.savefig(save_path)
            print(f"Generated: {save_path}")
            plt.close()

    print("Done generating plots!")

# Run with: python src/speed/plot_final.py
#
# Entry point for generating build/query CSVs and plots.
#
# This script takes CSV files produced by different benchmarking pipelines
# (Serde, RQ-LUT, RQ-legacy), normalizes them, and produces:
# - `build.csv` containing build times for each algorithm
# - `query.csv` containing query times for each algorithm
# - Plots of cumulative time (build + repetitions * average query time)
#
# Inputs
# ------
# - serde_build_csv_path: CSV with Serde build times
#   Example (2 rows):
#   JSON,BUILD_TIME_SECONDS
#   bestbuy_large_record_(1GB).json,2.1534
#   bestbuy_small_record.json,0.1542
#
# - rq_lut_build_csv_path: CSV with RQ-LUT build times (must include CUTOFF column)
#   Example (2 rows):
#   JSON,CUTOFF,BUILD_TIME_SECONDS
#   bestbuy_large_record_(1GB).json,0,5.634
#   bestbuy_large_record_(1GB).json,1024,7.821
#
# - serde_query_csv_path: CSV with Serde query times
#   Example (2 rows):
#   JSON,QUERY_ID,QUERY_TEXT,QUERY_TIME_SECONDS
#   bestbuy_large_record_(1GB).json,1,$..freeShipping,0.1345
#   bestbuy_large_record_(1GB).json,2,$.products[*].videoChapters,0.9421
#
# - rq_lut_query_csv_path: CSV with RQ-LUT query times (must include CUTOFF column)
#   Example (2 rows):
#   JSON,CUTOFF,QUERY_ID,QUERY_TEXT,QUERY_TIME_SECONDS
#   bestbuy_large_record_(1GB).json,0,1,$..freeShipping,0.16615
#   bestbuy_large_record_(1GB).json,1024,2,$.products[*].videoChapters,1.24851
#
# - rq_legacy_query_csv_path: CSV with RQ-legacy query times
#   Example (2 rows):
#   JSON,QUERY_ID,QUERY_TEXT,QUERY_TIME_SECONDS
#   bestbuy_large_record_(1GB).json,1,$..freeShipping,0.4235
#   bestbuy_large_record_(1GB).json,2,$.products[*].videoChapters,1.8214
#
# Parameters
# ----------
# cutoffs : list of str
#   Which cutoff values to keep from the RQ-LUT CSVs, e.g. ["0", "1024"].
# output_dir : str
#   Directory where build.csv, query.csv, and plots will be written.
if __name__ == "__main__":
    # Input
    serde_build_csv_path = "res/data/speed/server/serde/serde_build_repetitions=3.csv"
    rq_lut_build_csv_path = "res/data/speed/server/lut_build_speed_and_size/build_repetitions=10.csv"
    serde_query_csv_path = "res/data/speed/server/serde/serde_time_repetitions=20.csv"
    rq_lut_query_csv_path = "res/data/speed/server/rq_lut/query_node/rq_lut_time_node_repetitions=20.csv"
    rq_legacy_query_csv_path = "res/data/speed/server/rq_legacy/query_node/rq_legacy_time_node_repetitions=20.csv"
    output_dir = "res/plots/speed/server/final"
    cutoffs = ["0", "1024"]

    # Construct csv
    construct_input_csvs(
        serde_build_csv_path,
        rq_lut_build_csv_path,
        serde_query_csv_path,
        rq_lut_query_csv_path,
        rq_legacy_query_csv_path,
        cutoffs,
        output_dir
    )
    # Plot
    plot(output_dir, f"{output_dir}/labeled", False)
    plot(output_dir, f"{output_dir}/unlabeled", True)

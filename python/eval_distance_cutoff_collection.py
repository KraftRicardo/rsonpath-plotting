import os
import pandas as pd
from collections import defaultdict


def collect_build(result_dir_path, cutoffs):
    build_data = defaultdict(list)

    for cutoff in cutoffs:
        cutoff_dir_path = os.path.join(result_dir_path, str(cutoff))
        build_csv_path = os.path.join(cutoff_dir_path, "build.csv")

        if not os.path.exists(build_csv_path):
            continue

        try:
            df = pd.read_csv(build_csv_path)
        except Exception as e:
            print(f"Could not read {build_csv_path}: {e}")
            continue

        for _, row in df.iterrows():
            json_name = row["JSON"]
            build_data[json_name].append({
                "JSON": json_name,
                "CUTOFF": cutoff,
                "BUILD_TIME_SECONDS": row["BUILD_TIME_SECONDS"],
                "SIZE_IN_BYTES": row["SIZE_IN_BYTES"]
            })

    output_dir = os.path.join(result_dir_path, "../../distance_cutoff_evaluation/builds_by_json")
    os.makedirs(output_dir, exist_ok=True)

    for json_name, rows in build_data.items():
        df = pd.DataFrame(rows)
        df.sort_values(by=["CUTOFF"], inplace=True)
        output_path = os.path.join(output_dir, f"{json_name}.csv")
        df.to_csv(output_path, index=False)


def collect_query(result_dir_path, cutoffs):
    # Dictionary to collect per-filename rows
    file_rows = defaultdict(list)

    for cutoff in cutoffs:
        cutoff_dir_path = os.path.join(result_dir_path, str(cutoff))
        if not os.path.exists(cutoff_dir_path):
            continue

        for csv_file in os.listdir(cutoff_dir_path):
            if not csv_file.endswith(".csv") or "build" in csv_file:
                continue

            file_path = os.path.join(cutoff_dir_path, csv_file)
            try:
                df = pd.read_csv(file_path)
            except Exception as e:
                print(f"Skipping {file_path}: {e}")
                continue

            json_name = os.path.splitext(csv_file)[0]

            for _, row in df.iterrows():
                file_rows[json_name].append({
                    "JSON": json_name,
                    "CUTOFF": cutoff,
                    "QUERY_ID": row["QUERY_ID"],
                    "QUERY_TIME_SECONDS": row["QUERY_TIME_SECONDS"]
                })

    output_dir = os.path.join(result_dir_path, "../../distance_cutoff_evaluation/queries_by_json")
    os.makedirs(output_dir, exist_ok=True)

    for json_name, rows in file_rows.items():
        df = pd.DataFrame(rows)
        df.sort_values(by=["CUTOFF", "QUERY_ID"], inplace=True)
        output_path = os.path.join(output_dir, f"{json_name}.csv")
        df.to_csv(output_path, index=False)
        print(f"Wrote: {output_path}")

# Run with: python python/eval_distance_cutoff_collection.py
if __name__ == "__main__":
    result_dir_path = ".a_extern_final_results/speed/lut_ptrhash_double_empty_list_opt"

    cutoffs = [0, 1, 2, 64, 128, 192, 256, 320, 384, 448, 512, 1024, 2048, 4096, 8192]

    collect_build(result_dir_path, cutoffs);
    collect_query(result_dir_path, cutoffs);

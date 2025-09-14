import os
import pandas as pd


def plot_per_json(rq_legacy_time: str, rq_lut_time: str, percent_threshold: float, result_dir_path: str):
    """
    Compare baseline query runtimes with LUT (cutoff) runtimes to evaluate performance per JSON.
    Saves one CSV per JSON.
    """
    legacy_df = pd.read_csv(rq_legacy_time)
    lut_df = pd.read_csv(rq_lut_time)

    # Ensure QUERY_ID columns are strings
    legacy_df["QUERY_ID"] = legacy_df["QUERY_ID"].astype(str)
    lut_df["QUERY_ID"] = lut_df["QUERY_ID"].astype(str)

    # Ensure numeric
    legacy_df["QUERY_TIME_SECONDS"] = pd.to_numeric(legacy_df["QUERY_TIME_SECONDS"], errors="coerce")
    lut_df["QUERY_TIME_SECONDS"] = pd.to_numeric(lut_df["QUERY_TIME_SECONDS"], errors="coerce")
    lut_df["CUTOFF"] = pd.to_numeric(lut_df["CUTOFF"], errors="coerce")
    lut_df = lut_df.dropna(subset=["CUTOFF"])
    lut_df["CUTOFF"] = lut_df["CUTOFF"].astype(int)

    legacy_df["JSON"] = legacy_df["JSON"].astype(str).str.strip()
    lut_df["JSON"] = lut_df["JSON"].astype(str).str.strip()

    os.makedirs(result_dir_path, exist_ok=True)

    # Process each JSON separately
    for json_name, legacy_group in legacy_df.groupby("JSON"):
        lut_subset = lut_df[lut_df["JSON"] == json_name]

        if lut_subset.empty:
            print(f"No LUT data for JSON: {json_name}, skipping.")
            continue

        merged = lut_subset.merge(
            legacy_group[["QUERY_ID", "QUERY_TIME_SECONDS"]],
            on="QUERY_ID",
            suffixes=("_cutoff", "_baseline")
        )

        merged["DIFF"] = merged["QUERY_TIME_SECONDS_baseline"] - merged["QUERY_TIME_SECONDS_cutoff"]
        merged["POSITIVE"] = merged["DIFF"].apply(lambda x: x if x > 0 else 0)
        merged["NEGATIVE"] = merged["DIFF"].apply(lambda x: -x if x < 0 else 0)
        merged["NEGATIVE_COUNT"] = merged.apply(
            lambda row: 1 if row["QUERY_TIME_SECONDS_cutoff"] > percent_threshold * row["QUERY_TIME_SECONDS_baseline"] else 0,
            axis=1
        )
        merged["POSITIVE_COUNT"] = merged.apply(
            lambda row: 1 if row["QUERY_TIME_SECONDS_cutoff"] <= percent_threshold * row["QUERY_TIME_SECONDS_baseline"] else 0,
            axis=1
        )

        summary = merged.groupby("CUTOFF").agg(
            SUM_POSITIVE=("POSITIVE", "sum"),
            SUM_NEGATIVE=("NEGATIVE", "sum"),
            NEGATIVE_COUNT=("NEGATIVE_COUNT", "sum"),
            POSITIVE_COUNT=("POSITIVE_COUNT", "sum")
        ).reset_index()

        summary = summary.sort_values(
            by=["NEGATIVE_COUNT", "SUM_NEGATIVE", "SUM_POSITIVE"],
            ascending=[True, True, False]
        )

        summary_file = os.path.join(result_dir_path, f"{json_name}_summary.csv")
        summary.to_csv(summary_file, index=False)
        print(f"Saved summary for JSON '{json_name}' -> {summary_file}")

        total_time = legacy_group["QUERY_TIME_SECONDS"].sum()
        print(f"JSON: {json_name}, total baseline query time: {total_time:.6f} seconds")


def plot_combined_summary(rq_legacy_time: str, rq_lut_time: str, percent_threshold: float, result_dir_path: str):
    """
    Original behavior: combine all JSONs into a single summary CSV.
    """
    legacy_df = pd.read_csv(rq_legacy_time)
    lut_df = pd.read_csv(rq_lut_time)

    legacy_df["QUERY_ID"] = legacy_df["QUERY_ID"].astype(str)
    lut_df["QUERY_ID"] = lut_df["QUERY_ID"].astype(str)

    legacy_df["QUERY_TIME_SECONDS"] = pd.to_numeric(legacy_df["QUERY_TIME_SECONDS"], errors="coerce")
    lut_df["QUERY_TIME_SECONDS"] = pd.to_numeric(lut_df["QUERY_TIME_SECONDS"], errors="coerce")
    lut_df["CUTOFF"] = pd.to_numeric(lut_df["CUTOFF"], errors="coerce")
    lut_df = lut_df.dropna(subset=["CUTOFF"])
    lut_df["CUTOFF"] = lut_df["CUTOFF"].astype(int)

    legacy_df["JSON"] = legacy_df["JSON"].astype(str).str.strip()
    lut_df["JSON"] = lut_df["JSON"].astype(str).str.strip()

    merged_df = lut_df.merge(
        legacy_df[["JSON", "QUERY_ID", "QUERY_TIME_SECONDS"]],
        on=["JSON", "QUERY_ID"],
        suffixes=("_cutoff", "_baseline")
    )

    merged_df["DIFF"] = merged_df["QUERY_TIME_SECONDS_baseline"] - merged_df["QUERY_TIME_SECONDS_cutoff"]
    merged_df["POSITIVE"] = merged_df["DIFF"].apply(lambda x: x if x > 0 else 0)
    merged_df["NEGATIVE"] = merged_df["DIFF"].apply(lambda x: -x if x < 0 else 0)
    merged_df["NEGATIVE_COUNT"] = merged_df.apply(
        lambda row: 1 if row["QUERY_TIME_SECONDS_cutoff"] > percent_threshold * row["QUERY_TIME_SECONDS_baseline"] else 0,
        axis=1
    )
    merged_df["POSITIVE_COUNT"] = merged_df.apply(
        lambda row: 1 if row["QUERY_TIME_SECONDS_cutoff"] <= percent_threshold * row["QUERY_TIME_SECONDS_baseline"] else 0,
        axis=1
    )

    summary = merged_df.groupby("CUTOFF").agg(
        SUM_POSITIVE=("POSITIVE", "sum"),
        SUM_NEGATIVE=("NEGATIVE", "sum"),
        NEGATIVE_COUNT=("NEGATIVE_COUNT", "sum"),
        POSITIVE_COUNT=("POSITIVE_COUNT", "sum")
    ).reset_index()

    total_time = legacy_df["QUERY_TIME_SECONDS"].sum()
    print(f"Original sum of query time: {total_time:.6f} seconds")

    summary = summary.sort_values(
        by=["NEGATIVE_COUNT", "SUM_NEGATIVE", "SUM_POSITIVE"],
        ascending=[True, True, False]
    )

    os.makedirs(result_dir_path, exist_ok=True)
    summary_file = os.path.join(result_dir_path, "summary_combined.csv")
    summary.to_csv(summary_file, index=False)

    print(summary)
    print(f"Saved combined summary -> {summary_file}")

# python src/speed/find_best_cutoff.py
if __name__ == "__main__":
    rq_legacy_time = "res/data/speed/server/rq_legacy/query_count/rq_legacy_time_repetitions=20.csv"
    rq_lut_time = "res/data/speed/server/rq_lut/query_count/rq_lut_time_repetitions=20.csv"
    result_dir_path = "res/plots/speed/server/find_best_cutoff"
    percent_threshold = 1.03

    # Choose one:
    plot_per_json(rq_legacy_time, rq_lut_time, percent_threshold, result_dir_path)
    plot_combined_summary(rq_legacy_time, rq_lut_time, percent_threshold, result_dir_path)

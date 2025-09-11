import pandas as pd
import matplotlib.pyplot as plt

def plot(rq_legacy_time: str, rq_lut_time: str, percent_threshold: float):
    """
    Compare baseline query runtimes with LUT (cutoff) runtimes to evaluate performance.

    Args:
        rq_legacy_time (str): Path to CSV file with baseline timings (repetitions=1).
        rq_lut_time (str): Path to CSV file with LUT timings (repetitions=20, includes CUTOFF column).
        percent_threshold (float): Threshold multiplier (e.g., 1.03 means LUT is considered slower
                                   if its runtime is more than 3% slower than baseline).

    Behavior:
        - Merges baseline and LUT runtime data on JSON and QUERY_ID.
        - Computes runtime differences: positive when LUT is faster, negative when slower.
        - Counts how many queries are slower than the given threshold (NEGATIVE_COUNT).
        - Counts how many queries are faster within the threshold (POSITIVE_COUNT).
        - Aggregates results per cutoff value.
        - Prints the summary table and saves it to `cutoff_summary.csv`.
        - Plots:
            * Bar chart of SUM_POSITIVE and SUM_NEGATIVE differences.
            * Line plot of NEGATIVE_COUNT and POSITIVE_COUNT per cutoff.
    """
    legacy_df = pd.read_csv(rq_legacy_time)
    lut_df = pd.read_csv(rq_lut_time)

    # Merge on JSON + QUERY_ID to align baseline with cutoff runs
    merged = lut_df.merge(
        legacy_df[["JSON", "QUERY_ID", "QUERY_TIME_SECONDS"]],
        on=["JSON", "QUERY_ID"],
        suffixes=("_cutoff", "_baseline")
    )

    # Compute difference: baseline - cutoff
    merged["DIFF"] = merged["QUERY_TIME_SECONDS_baseline"] - merged["QUERY_TIME_SECONDS_cutoff"]

    # Separate into positive (cutoff faster) and negative (cutoff slower)
    merged["POSITIVE"] = merged["DIFF"].apply(lambda x: x if x > 0 else 0)
    merged["NEGATIVE"] = merged["DIFF"].apply(lambda x: -x if x < 0 else 0)

    # Mark NEGATIVE_COUNT where LUT is slower than threshold
    merged["NEGATIVE_COUNT"] = merged.apply(
        lambda row: 1 if row["QUERY_TIME_SECONDS_cutoff"] > percent_threshold * row["QUERY_TIME_SECONDS_baseline"] else 0,
        axis=1
    )

    # Mark POSITIVE_COUNT as the opposite (LUT not exceeding the threshold)
    merged["POSITIVE_COUNT"] = merged.apply(
        lambda row: 1 if row["QUERY_TIME_SECONDS_cutoff"] <= percent_threshold * row["QUERY_TIME_SECONDS_baseline"] else 0,
        axis=1
    )

    # Aggregate sums by cutoff
    summary = merged.groupby("CUTOFF").agg(
        SUM_POSITIVE=("POSITIVE", "sum"),
        SUM_NEGATIVE=("NEGATIVE", "sum"),
        NEGATIVE_COUNT=("NEGATIVE_COUNT", "sum"),
        POSITIVE_COUNT=("POSITIVE_COUNT", "sum")
    ).reset_index()

    # Sort: ascending NEGATIVE_COUNT, then SUM_NEGATIVE, then descending SUM_POSITIVE
    summary = summary.sort_values(by=["NEGATIVE_COUNT", "SUM_NEGATIVE", "SUM_POSITIVE"], ascending=[True, True, False])

    print(summary)


if __name__ == "__main__":
    # Paths to input CSV files
    rq_legacy_time = "res/data/speed/server/rq_legacy/query_count/rq_legacy_time_repetitions=1.csv"
    rq_lut_time = "res/data/speed/server/rq_lut/query_count/rq_lut_time_repetitions=20.csv"

    # Performance threshold: LUT is considered slower if >3% slower than baseline
    percent_threshold = 1.03

    # This will:
    # 1. Load the baseline and LUT timings
    # 2. Compute positive/negative time differences
    # 3. Count queries where LUT is >3% slower (NEGATIVE_COUNT)
    # 4. Count queries where LUT is within or faster than threshold (POSITIVE_COUNT)
    # 5. Aggregate results per cutoff value
    # 6. Print the summary to CSV
    plot(rq_legacy_time, rq_lut_time, percent_threshold)
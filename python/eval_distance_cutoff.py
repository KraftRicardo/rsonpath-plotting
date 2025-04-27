import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import sys
import os
from collections import defaultdict

# Custom color palette
PLOT_COLORS = [
    'red', 'skyblue', 'blue', 'orange', 'green',
    'coral', 'purple', 'pink', 'cyan', 'magenta',
    'brown', 'turquoise', 'darkgreen', 'darkred', 'darkcyan',
    'darkorange', 'darkviolet', 'lime', 'indigo', 'gold',
    'darkblue', 'chartreuse', 'teal', 'yellow', 'salmon',
    'darkkhaki', 'crimson', 'peru', 'forestgreen', 'mediumpurple', 'black',
]


def plot_all(build_csv_path: str, query_csv_path: str, counter_csv_path: str, top_image_path, cutoffs):
    # Load CSV files
    query_df = pd.read_csv(query_csv_path)
    build_df = pd.read_csv(build_csv_path)
    counter_df = pd.read_csv(counter_csv_path)

    # --- FILTER only requested cutoffs ---
    query_df = query_df[query_df["CUTOFF"].isin(cutoffs)]
    build_df = build_df[build_df["CUTOFF"].isin(cutoffs)]

    # Normalize query times relative to CUTOFF=0
    base_times = query_df[query_df["CUTOFF"] == 0][["QUERY_ID", "QUERY_TIME_SECONDS"]].copy()
    base_times = base_times.set_index("QUERY_ID")["QUERY_TIME_SECONDS"]
    query_df["BASE_TIME"] = query_df["QUERY_ID"].map(base_times)
    query_df["RELATIVE_QUERY_TIME"] = query_df["QUERY_TIME_SECONDS"] / query_df["BASE_TIME"]

    # Sort counter_df by TOTAL_PERCENT_SKIP & filter relevant query names
    counter_df = counter_df.sort_values(
        by=["TOTAL_PERCENT_SKIP", "QUERY_NAME"])
    counter_df = counter_df[counter_df["QUERY_NAME"].isin(
        query_df["QUERY_ID"])]

    # Merge and sort query_df
    query_df = query_df.merge(
        counter_df[['QUERY_NAME', 'TOTAL_PERCENT_SKIP']],
        left_on='QUERY_ID',
        right_on='QUERY_NAME',
        how='left'
    )
    query_df = query_df.sort_values(by=["TOTAL_PERCENT_SKIP", "QUERY_ID"])

    # Convert size to MB and sort
    build_df = build_df.sort_values("CUTOFF")
    build_df["SIZE_MB"] = build_df["SIZE_IN_BYTES"] / (1024 * 1024)

    # Output filename
    output_dir = os.path.dirname(os.path.abspath(build_csv_path))
    json_filename = build_df["JSON"].iloc[0]
    output_filename = os.path.join(output_dir, f"../plots/{json_filename}.png")

    # Setup figure
    fig = plt.figure(figsize=(16, 14))

    # Load and display image
    if os.path.exists(top_image_path):
        img = mpimg.imread(top_image_path)
        ax_img = fig.add_axes([0, 0.6, 1, 0.4])
        ax_img.imshow(img)
        ax_img.axis('off')

    # Create cutoff color map using the custom color palette
    cutoff_color_map = {
        cutoff: PLOT_COLORS[i % len(PLOT_COLORS)]
        for i, cutoff in enumerate(cutoffs)
    }

    # --- Plot 1: Relative Query Time Line Plot ---
    ax1 = fig.add_subplot(2, 2, 1)
    for i, (cutoff, group) in enumerate(query_df.groupby("CUTOFF")):
        ax1.plot(
            group["QUERY_ID"].astype(str),
            group["RELATIVE_QUERY_TIME"],
            marker='o',
            label=f"Cutoff {cutoff}",
            color=cutoff_color_map.get(cutoff, "gray"),  # fallback color
            alpha=0.4
        )
    ax1.set_xlabel("Query ID")
    ax1.set_ylabel("Relative Query Time")
    ax1.set_title("Relative Query Time by Query ID (Normalized to CUTOFF=0)")
    ax1.grid(True)
    ax1.set_xticklabels(group["QUERY_ID"].astype(str), rotation=90, fontsize=9)

    # --- Plot 2: Build Time ---
    ax2 = fig.add_subplot(2, 2, 2)
    ax2.bar(
        build_df["CUTOFF"].astype(str),
        build_df["BUILD_TIME_SECONDS"],
        color=[cutoff_color_map.get(cutoff, "gray") for cutoff in build_df["CUTOFF"]]
    )
    ax2.set_xlabel("Cutoff")
    ax2.set_ylabel("Build Time (seconds)")
    ax2.set_title("Build Time by Cutoff")

    # --- Plot 3: Total Percent Skip ---
    ax3 = fig.add_subplot(2, 2, 3)
    counter_df.plot(
        x="QUERY_NAME",
        y="TOTAL_PERCENT_SKIP",
        kind="bar",
        ax=ax3,
        color="#1f77b4"
    )
    ax3.set_xlabel("Query ID")
    ax3.set_ylabel("Total Percent Skip (%)")
    ax3.set_title("Total Percent Skip by Query ID")
    ax3.set_xticklabels(counter_df["QUERY_NAME"], rotation=90, fontsize=9)

    # --- Plot 4: Size in MB ---
    ax4 = fig.add_subplot(2, 2, 4)
    ax4.bar(
        build_df["CUTOFF"].astype(str),
        build_df["SIZE_MB"],
        color=[cutoff_color_map.get(cutoff, "gray") for cutoff in build_df["CUTOFF"]]
    )
    ax4.set_xlabel("Cutoff")
    ax4.set_ylabel("LUT Size (MB)")
    ax4.set_title("LUT Size by Cutoff")

    # Layout tweaks
    plt.subplots_adjust(hspace=0.5, top=0.6)
    plt.savefig(output_filename)
    plt.close(fig)

    print(f"Combined plot saved to: {output_filename}")


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

# Run with: lut-no-lut
if __name__ == "__main__":
    result_dir_path = ".a_extern_final_results/speed/lut_ptrhash_double_empty_list_opt"
    input_dir_path = ".a_extern_final_results/distance_cutoff_evaluation/builds_by_json"
    # cutoffs = [0, 1, 2, 64, 128, 192, 256, 320, 384, 448, 512, 1024, 2048, 4096, 8192]
    cutoffs = [0, 64, 128, 512, 8192]

    print("Collecting data in one big csv")
    collect_build(result_dir_path, cutoffs)
    collect_query(result_dir_path, cutoffs)

    # Automatically read all JSON names (without .csv extension)
    names = [
        os.path.splitext(f)[0]
        for f in os.listdir(input_dir_path)
        if f.endswith(".csv")
    ]

    for name in names:
        build_results = f".a_extern_final_results/distance_cutoff_evaluation/builds_by_json/{name}.csv"
        query_results = f".a_extern_final_results/distance_cutoff_evaluation/queries_by_json/{name}.csv"
        counter_csv_path = f".a_extern_final_results/distance_cutoff_evaluation/skip_counter/COUNTER_{name}.csv"
        top_image_path = f".a_extern_final_results/distance_cutoff_evaluation/distance_distribution/{name}_plot.png"

        plot_all(build_results, query_results, counter_csv_path, top_image_path, cutoffs)
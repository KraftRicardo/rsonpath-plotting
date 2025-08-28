import os

import matplotlib.pyplot as plt
import pandas as pd


def plot(df: pd.DataFrame, directory: str, file_base_name: str) -> None:
    # Sort by ascending SKIP_PERCENTAGE
    df_sorted = df.sort_values(by="QUERY_ID", ascending=True)

    # Plot
    plt.figure(figsize=(12, 6))
    _ = plt.bar(df_sorted["QUERY_ID"].astype(str), df_sorted["SKIP_PERCENTAGE"], color="royalblue")

    # Labels and title
    plt.xlabel("Query ID")
    plt.ylabel("Skip Percentage")
    plt.title(f"Skip Percentage by Query ID - {file_base_name}")
    plt.xticks(rotation=90)

    # Save plot
    output_path = os.path.join(directory, f"{file_base_name}_skip_percentage.png")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"Generated: {output_path}")


def plot_all(data_dir_path: str, result_dir_path: str):
    os.makedirs(result_dir_path, exist_ok=True)

    # Get all JSON files in the directory
    for filename in os.listdir(data_dir_path):
        if filename.endswith(".csv"):
            file_path = os.path.join(data_dir_path, filename)

            # Read the JSON file as a DataFrame
            df = pd.read_csv(file_path)

            # Call plotting functions
            file_base_name = os.path.splitext(filename)[0].removesuffix("_distances")
            print(f"Process: {file_base_name}")
            plot(df, result_dir_path, file_base_name)


# Run with: python src/analysis/plot_query_skip_percentage.py
#
# Plot the distance distribution of their brackets for individual JSON files.
#
# "data_dir_path" is the path to the folder holding all the .csv files. These follow this structure:
#   QUERY_ID,QUERY_TEXT,COUNT_RESULT,SKIP_PERCENTAGE
#   1,$..freeShipping,230089,0.0000000000000000
#   2,$.products[*].videoChapters,769,0.0922743888980685
#   3,$.products[*].additionalFeatures[*],61098,0.1008473857373333
#   ...
# There is one .csv file per analyzed JSON so the csv should be named after the analyzed JSON file.
if __name__ == "__main__":
    # Input
    data_dir_path = "res/data/analysis/query"
    result_dir_path = "res/plots/analysis/query"

    plot_all(data_dir_path, result_dir_path)

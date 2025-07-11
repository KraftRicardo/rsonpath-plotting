import os
import pandas as pd


def bundle_csvs(input_folder: str, output_file: str):
    all_data = []

    for filename in os.listdir(input_folder):
        if filename.endswith(".csv"):
            filepath = os.path.join(input_folder, filename)
            df = pd.read_csv(filepath)
            json_name = os.path.splitext(filename)[0]  # Remove '.csv'
            df.insert(0, "JSON", json_name)  # Insert new 'JSON' column at the beginning
            all_data.append(df)

    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
        final_df.to_csv(output_file, index=False)
        print(f"✅ Successfully written {output_file} with {len(final_df)} rows.")
    else:
        print("⚠️ No CSV files found in the specified folder.")


if __name__ == "__main__":
    # input_folder = ".a_extern_final_results/speed/rq-lut-no-lut"
    # output_file = ".a_extern_final_results/speed/rq-lut-no-lut/bundled_output.csv"

    input_folder = ".a_extern_final_results/speed/rq-legacy"
    output_file = ".a_extern_final_results/speed/rq-legacy/bundled_output.csv"

    bundle_csvs(input_folder, output_file)

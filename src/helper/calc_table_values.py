import pandas as pd

# Original dataset (name, size, num_brackets)
data = [
    ("walmart_short", "95MB", 35183),
    ("twitter_short", "80MB", 474122),
    ("bestbuy_short", "103MB", 680183),
    ("google_map_short", "107MB", 1030012),
    ("crossref0", "320MB", 3130672),
    ("crossref1", "551MB", 5789238),
    ("twitter_large_record", "843MB", 4676467),
    ("walmart_large_record", "995MB", 362598),
    ("bestbuy_large_record", "1.00GB", 6799457),
    ("crossref2", "1.10GB", 11451863),
    ("wiki_large_record", "1.10GB", 23827952),
    ("google_map_large_record", "1.10GB", 10401370),
    ("nspl_large_record", "1.20GB", 3510428),
    ("crossref4", "2.10GB", 22476255),
    ("nested_col", "27.70GB", 92986053)
]

# Helper to convert size strings to bytes
def size_to_bytes(size_str):
    size_str = size_str.strip().upper().replace("\\,", "")  # clean LaTeX commas
    if "MB" in size_str:
        return float(size_str.replace("MB", "")) * 1024**2
    elif "GB" in size_str:
        return float(size_str.replace("GB", "")) * 1024**3
    else:
        raise ValueError(f"Unknown size unit in: {size_str}")

# Process and print
for name, size_str, num_brackets in data:
    size_bytes = size_to_bytes(size_str)
    brackets_per_byte = num_brackets / size_bytes
    print(f"{name:<25} & {brackets_per_byte} \\\\")

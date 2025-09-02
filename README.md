# rsonpath-plotting

A Python project for generating plots to analyze and visualize results from **[rsonpath](https://github.com/rsonpath/rsonpath)** experiments
and its lookup-table (LUT) modification.

---

## ✨ Features

This repository includes multiple plotting scripts, each producing specialized figures for different aspects of `rsonpath` performance.  
All figures below are automatically generated using real benchmark data.

---

### 🔎 Query Skip Percentage
**`plot_query_skip_percentage`**  
Visualizes the percentage of skipped bytes for different queries on a JSON file.

![plot_query_skip_percentage](res/readme_figures/plot_query_skip_percentage.png)

---

### 📏 Distance Distributions (per JSON)

**`plot_distance_distribution_per_json`**  
Plots the distance distribution of a JSON. Three variants:

- Default: x-axis doubles each step  
  ![plot_distance_distribution_per_json](res/readme_figures/plot_distance_distribution_per_json.png)

- Omit labels and titles (compact mode)  
  ![plot_distance_distribution_per_json_short](res/readme_figures/plot_distance_distribution_per_json_short.png)

- Fixed-step (64) x-axis growth  
  ![plot_distance_distribution_per_json_64](res/readme_figures/plot_distance_distribution_per_json_64.png)

---

### 📏 Distance Distributions (per Query)

**`plot_distance_distribution_per_query`**  
Plots the distance distribution of all jumps taken during a query on a given JSON.

- Default: x-axis doubles each step  
  ![plot_distance_distribution_per_query](res/readme_figures/plot_distance_distribution_per_query.png)

- Fixed-step (64) x-axis growth  
  ![plot_distance_distribution_per_query_64](res/readme_figures/plot_distance_distribution_per_query_64.png)

- With execution time spent in each bucket (relative to total skip time)  
  ![plot_distance_distribution_per_query_timed](res/readme_figures/plot_distance_distribution_per_query_timed.png)

---

### ⚡ Serde Size and Build Time
**`plot_serde_size_and_build_time`**  
Plots Serde’s build time and heap ratio compared to the input JSON.

![plot_serde_size_and_build_time](res/readme_figures/plot_serde_size_and_build_time.png)

---

### 🔧 Distance Cutoff Experiments

**`plot_distance_cutoff`**  
Compares query speed for the LUT implementation at different cutoffs. Also shows LUT size and build time.

![plot_distance_cutoff](res/readme_figures/plot_distance_cutoff.png)

---

**`plot_distance_cutoff_sizes`**  
Visualizes LUT sizes and build times per cutoff and JSON:

- LUT sizes (MB)  
  ![plot_distance_cutoff_sizes_size](res/readme_figures/plot_distance_cutoff_sizes_size.png)

- LUT build times (s)  
  ![plot_distance_cutoff_sizes_build_time](res/readme_figures/plot_distance_cutoff_sizes_build_time.png)

- Relative to cutoff = 0 (percent scale)  
  ![plot_distance_cutoff_sizes_combined](res/readme_figures/plot_distance_cutoff_sizes_combined.png)

---

### 🪶 Empty List Optimization
**`plot_empty_list_opt`**  
Compares `rq_legacy` vs. `rq_legacy_empty_list_opt` to evaluate the effect of the `empty_list_opt` feature.

![plot_empty_list_opt](res/readme_figures/plot_empty_list_opt.png)

---

### 🧱 LUT Construction
**`plot_lut_construction`**  
Compares different LUT implementations in build-time, query-time, and heap size.

![plot_lut_construction](res/readme_figures/plot_lut_construction.png)

---

### 🏁 Final Comparison
**`plot_final`**  
Compares, for each query, how fast `rq`, `rq-lut`, and `serde` are.  
Includes build times for LUTs and the Serde DOM.  
(`rq` build time = 0, as it is a streaming approach.)

- With labels  
  ![plot_final_labeled](res/readme_figures/plot_final_labeled.png)

- Without labels  
  ![plot_final_unlabeled](res/readme_figures/plot_final_unlabeled.png)

---

### 🥇 Optimal vs. Implementations
**`plot_optimal`**  
Compares query speed of `rq-legacy` vs. the theoretical optimal vs. `rq-lut` with varying cutoffs.

![plot_optimal](res/readme_figures/plot_optimal.png)

---


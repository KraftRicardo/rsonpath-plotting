# rsonpath-plotting

A Python project for generating plots to analyze and visualize results from **[rsonpath-lut](https://github.com/KraftRicardo/rsonpath/tree/main)** experiments
and its lookup-table (LUT) modification.

---

## ✨ Features

This repository includes multiple plotting scripts, each producing specialized figures for different aspects of `rsonpath-lut` performance.  
All figures below are automatically generated using the data generated from there.

---

Bracket Distribution
How many curly and how many squary brackets each json has in relation per json.
![plot_query_skip_percentage](res/readme_figures/plot_json_curly_squary_percent.png)



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

[//]: # (### 🔧 Distance Cutoff Experiments)

[//]: # ()
[//]: # (**`plot_distance_cutoff`**  )

[//]: # (Compares query speed for the LUT implementation at different cutoffs. Also shows LUT size and build time.)

[//]: # ()
[//]: # (![plot_distance_cutoff]&#40;res/readme_figures/plot_distance_cutoff.png&#41;)

[//]: # ()
[//]: # (---)

[//]: # ()
[//]: # (**`plot_distance_cutoff_sizes`**  )

[//]: # (Visualizes LUT sizes and build times per cutoff and JSON:)

[//]: # ()
[//]: # (- LUT sizes &#40;MB&#41;  )

[//]: # (  ![plot_distance_cutoff_sizes_size]&#40;res/readme_figures/plot_distance_cutoff_sizes_size.png&#41;)

[//]: # ()
[//]: # (- LUT build times &#40;s&#41;  )

[//]: # (  ![plot_distance_cutoff_sizes_build_time]&#40;res/readme_figures/plot_distance_cutoff_sizes_build_time.png&#41;)

[//]: # ()
[//]: # (- Relative to cutoff = 0 &#40;percent scale&#41;  )

[//]: # (  ![plot_distance_cutoff_sizes_combined]&#40;res/readme_figures/plot_distance_cutoff_sizes_combined.png&#41;)

[//]: # ()
[//]: # (---)

### 🪶 Empty List Optimization
**`plot_empty_list_opt`**  
Compares `rq_legacy` vs. `rq_legacy_empty_list_opt` to evaluate the effect of the `empty_list_opt` feature.

![plot_empty_list_opt](res/readme_figures/plot_empty_list_opt.png)

---
### 🪶 RQ-LUT-NO-LUT
**`plot_empty_list_opt`**  
Compares `rq_legacy` vs. `rq_lut_no_lut` to evaluate the effect of the base code changes on the speed.

![plot_rq_lut_no_lut](res/readme_figures/plot_rq_lut_no_lut.png)

---

### 🧱 LUT Construction
**`plot_lut_construction`**  
Compares different LUT implementations in build-time, query-time, and heap size.

![plot_lut_construction](res/readme_figures/plot_lut_construction.png)


After deciding for a LUT implementation one can now plot the LUT build speed and size for different cutoffs, while
also tracking how long the collection step of the brackets takes.

![lut_build_speed_and_size](res/readme_figures/plot_lut_build_speed_and_size.png)
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
Compares query speed of `rq-legacy` vs. the theoretical optimal vs. `rq-lut` with varying cutoffs for the COUNT queries.

![plot_optimal](res/readme_figures/plot_optimal.png)

A table to find the best cutoff based on that data.

![find_best_cutoff_table](res/readme_figures/find_best_cutoff_table.png)

Like plot optimal but this time we queried for the complete results (NODE and not COUNT) which means we can also compare
it with serde.

![plot_optimal_node](res/readme_figures/plot_optimal_node.png)

---


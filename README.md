# rsonpath-plotting

A small Python project for generating plots to analyze and visualize results from **rsonpath** experiments.  
It provides convenient plotting functions to turn raw experiment outputs into informative figures.

---

## Features

The following plots can be generated (work in progress):

- **`plot_query_skip_percentage`**  
  Visualizes the total percentage of skipped bytes for different queries on a JSON.  
  ![plot_query_skip_percentage](res/readme_figures/plot_query_skip_percentage.png)

- **`plot_distance_distribution_per_json`**  
  Plot the distance distribution of a json. Has three options:
  - Default plot with x-axis doubling each step
  ![plot_distance_distribution_per_json](res/readme_figures/plot_distance_distribution_per_json.png)
  - When you want to omit labels and titles
  ![plot_distance_distribution_per_json_short](res/readme_figures/plot_distance_distribution_per_json_short.png)
  - When you want the x-axis to grow by 64 each step
  ![plot_distance_distribution_per_json_64](res/readme_figures/plot_distance_distribution_per_json_64.png)

- **`plot_distance_distribution_per_query`**  
  Plot the distance distribution of all the jumps taken during a query on a given json. Has 2 options:
  - Default plot with x-axis doubling each step
  ![plot_distance_distribution_per_query](res/readme_figures/plot_distance_distribution_per_query.png)
  - When you want the x-axis to grow by 64 each step
  ![plot_distance_distribution_per_query_64](res/readme_figures/plot_distance_distribution_per_query_64.png)

- **`plot_distance_distribution_per_query`**
  When you additionally want to know how much time is spent in each bucket in relation to the total skip time.
  ![plot_distance_distribution_per_query_timed](res/readme_figures/plot_distance_distribution_per_query_timed.png)

- **`plot_serde_size_and_build_time`**
  When you want to plot serde's build time and heap ratio compared to the input json.
  ![plot_serde_size_and_build_time](res/readme_figures/plot_serde_size_and_build_time.png)

- **`plot_distance_cutoff`**
  Plot the performance of the query speed of the LUT implementation for different cutoffs. Also shows the size and build time for each LUT.
  ![plot_distance_cutoff](res/readme_figures/plot_distance_cutoff.png)

- **`plot_distance_cutoff_sizes`**
  - Plot the LUT sizes for different cutoffs and different json.
  ![plot_distance_cutoff_sizes](res/readme_figures/plot_distance_cutoff_sizes_size.png)
  - Plot the LUT build times for different cutoffs and different json.
  ![plot_distance_cutoff_sizes](res/readme_figures/plot_distance_cutoff_sizes_build_time.png)
  - Plot the LUT build times and sizes for different cutoffs and different json in relation to cutoff=0.
  ![plot_distance_cutoff_sizes](res/readme_figures/plot_distance_cutoff_sizes_combined.png)

- **`plot_empty_list_opt`**
Compare rq_legacy vs. rq_legacy_empty_list_opt to see what the effects of the empty_list_opt feature are.
![plot_empty_list_opt](res/readme_figures/plot_empty_list_opt.png)

- **`plot_lut_construction`**
  Compare different LUT implementations in build-time, query-time and heap size.
  ![plot_lut_construction](res/readme_figures/plot_lut_construction.png)

- **`plot_final`**
Final plot where we compare for each query how fast rq, rq-lut and serde are. This plot also considers the build time
for the LUTs and or the serde DOM. rq has a build time = 0 due to being a full streaming approach.
  - Labeled
    ![plot_final_labeled](res/readme_figures/plot_final_labeled.png)
  - Unlabeled
    ![plot_final_unlabeled](res/readme_figures/plot_final_unlabeled.png)

- **`plot_optimal`**
  Compare the query speed of rq-legacy vs. the theoretical optimal time vs. the rq-lut with different cutoffs.
  ![plot_optimal](res/readme_figures/plot_optimal.png)
---
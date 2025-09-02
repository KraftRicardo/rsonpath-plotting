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
---
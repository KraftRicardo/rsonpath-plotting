import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Colors for the lines in the line plots
PLOT_COLORS = [
    'red', 'skyblue', 'blue', 'orange', 'green',
    'coral', 'purple', 'pink', 'cyan', 'magenta',
    'brown', 'turquoise', 'darkgreen', 'darkred', 'darkcyan',
    'darkorange', 'darkviolet', 'lime', 'indigo', 'gold',
    'darkblue', 'chartreuse', 'teal', 'yellow', 'salmon',
    'darkkhaki', 'crimson', 'peru', 'forestgreen', 'mediumpurple', 'black',
]

AXIS_LABEL_FONT_SIZE = 14

def to_pretty_name(column_name: str, column_suffix: str) -> str:
    res = column_name.removesuffix(column_suffix)
    res = res.replace('_', ' ')
    return res


def plot_all(file_path: str) -> None:
    directory, filename = os.path.split(file_path)
    file_base_name = os.path.splitext(filename)[0]
    save_path = os.path.join(directory, f"{file_base_name}_combined_plot.png")

    df = pd.read_csv(file_path)
    df = df.sort_values(by='num_keys')

    fig, axes = plt.subplots(3, 2, figsize=(18, 18))
    axes = axes.flatten()

    plot_configs = [
        {'column_suffix': '_BUILD', 'ylabel': 'Build time in seconds', 'per_key': False},
        {'column_suffix': '_QUERY', 'ylabel': 'Sum of query time in seconds', 'per_key': False},
        {'column_suffix': '_HEAP', 'ylabel': 'Heap size in bytes', 'per_key': False},
        {'column_suffix': '_BUILD', 'ylabel': 'Average build time in seconds per key', 'per_key': True},
        {'column_suffix': '_QUERY', 'ylabel': 'Average query time in seconds per key', 'per_key': True},
        {'column_suffix': '_HEAP', 'ylabel': 'Heap size in bytes per key', 'per_key': True},
    ]

    axes = axes.reshape(3, 2)
    col1_axes = axes[:, 0]
    col2_axes = axes[:, 1]

    handles, labels = [], []

    for ax, config in zip(np.concatenate((col1_axes, col2_axes)), plot_configs):
        column_suffix = config['column_suffix']
        per_key = config['per_key']
        filtered_columns = [col for col in df.columns if col.endswith(column_suffix)]

        for (i, column) in enumerate(filtered_columns):
            name = to_pretty_name(column, column_suffix)
            if per_key:
                line, = ax.plot(df['num_keys'], df[column] / df['num_keys'],
                                alpha=0.6, marker='o', label=name, color=PLOT_COLORS[i])
            else:
                line, = ax.plot(df['num_keys'], df[column], alpha=0.6,
                                marker='o', label=name, color=PLOT_COLORS[i])

            if name not in labels:
                handles.append(line)
                labels.append(name)

        ax.set_ylabel(config['ylabel'], fontweight='bold', fontsize=AXIS_LABEL_FONT_SIZE)
        ax.grid(True)

    col1_axes[0].set_title("Absolute Values", fontweight='bold', fontsize=14)
    col2_axes[0].set_title("Per Key Values", fontweight='bold', fontsize=14)

    for ax in np.concatenate((col1_axes, col2_axes)):
        ax.set_xticks(df['num_keys'])
        ax.set_xticklabels(df['num_keys'], rotation=45)

    for ax in [col1_axes[-1], col2_axes[-1]]:
        ax.set_xlabel('Number of keys', fontweight='bold', fontsize=AXIS_LABEL_FONT_SIZE)

    fig.text(
        x=0.76,
        y=0.52,
        s='Strategies',
        horizontalalignment='left',
        verticalalignment='top',
        style='italic',
        fontsize=20,
        bbox={'facecolor': (0.7, 0.8, 1), 'boxstyle': 'round'}
    )

    fig.legend(
        handles,
        labels,
        loc='upper left',
        bbox_to_anchor=(0.76, 0.5),
        fontsize=14,
        fancybox=True,
        shadow=True
    )

    fig.text(
        x=0.76,
        y=0.88,
        s='Data',
        horizontalalignment='left',
        verticalalignment='top',
        style='italic', fontsize=20,
        bbox={'facecolor': (0.7, 0.8, 1), 'boxstyle': 'round'}
    )

    text_content = "\n".join(f"{name}:\n  {num_keys}" for name, num_keys in zip(df['name'], df['num_keys']))
    fig.text(
        x=0.76,
        y=0.85,
        s=text_content,
        horizontalalignment='left',
        verticalalignment='top',
        fontsize=14,
        bbox={'facecolor': 'white', 'boxstyle': 'round'}
    )

    plt.subplots_adjust(right=0.75)
    plt.savefig(save_path)
    print(f"Generated: {save_path}")

# Run with: python python/speed/plot_lut_construction.py
#
# This function expects a file path to a "<FILENAME>.csv" with following structure:
# build.csv:
#   name,input_size_bytes,num_keys,hash_map_double_BUILD,hash_map_double_QUERY,hash_map_double_HEAP,#2048_λ=1:phf_group_BUILD,#2048_λ=1:phf_group_QUERY,#2048_λ=1:phf_group_HEAP,#4096_λ=1:phf_group_BUILD,#4096_λ=1:phf_group_QUERY,#4096_λ=1:phf_group_HEAP,#8192_λ=1:phf_group_BUILD,#8192_λ=1:phf_group_QUERY,#8192_λ=1:phf_group_HEAP,#2048_λ=5:phf_group_BUILD,#2048_λ=5:phf_group_QUERY,#2048_λ=5:phf_group_HEAP,#4096_λ=5:phf_group_BUILD,#4096_λ=5:phf_group_QUERY,#4096_λ=5:phf_group_HEAP,#8192_λ=5:phf_group_BUILD,#8192_λ=5:phf_group_QUERY,#8192_λ=5:phf_group_HEAP,
#   bestbuy_large_record_(1GB),1044619305,6799457,0.7701935596666667,0.611544818,142606436,0.9796494743333334,0.5533069434000001,68289530,1.0195999213333333,0.559336849,68584442,1.0807553516666666,0.5896918266,69174266,0.6775244473333334,0.4446728994,24779554,0.70940738,0.4492791542000001,25080882,0.7656126896666667,0.47424940600000004,25683994,
#   crossref1_(551MB),550523996,5789238,0.5892176459999999,0.5133634828,142615072,0.7634968123333333,0.4387181536,58197252,0.7921743723333333,0.44430835700000004,58492164,0.8428166859999999,0.4695093748,59081988,0.5081259483333334,0.3755787986,21152572,0.5343990163333333,0.38200665100000003,21454060,0.5757434626666668,0.3988796362,22057420,
#   crossref2_(1.1GB),1075392435,11451863,1.2492186633333333,1.1496990644,285230112,1.5186646953333334,1.1454835676000001,114834614,1.5679860440000002,1.1571361002,115129526,1.651779375,1.2062598392,115719350,1.0283180630000002,0.7880162256,41548246,1.0494727493333336,0.7973497592000001,41850190,1.1226313693333332,0.8408736874,42453734,
#   ...
#
# Then the code will create a plot .png image in the same folder named "<FILENAME>_combined_plot.png".
if __name__ == "__main__":
    # Input
    file_path = ".a_extern_final_results/speed/lut_construction/1 GB ptr_hash_solo/result.csv"

    plot_all(file_path)

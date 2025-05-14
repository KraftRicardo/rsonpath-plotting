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


def plot_all(df: pd.DataFrame, save_path: str) -> None:
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


if __name__ == "__main__":
    file_path = ".a_extern_final_results/speed/lut_construction/result.csv"
    directory, filename = os.path.split(file_path)
    file_base_name = os.path.splitext(filename)[0]
    df = pd.read_csv(file_path)
    plot_all(df, os.path.join(directory, f"{file_base_name}_combined_plot.png"))

import matplotlib.pyplot as plt
import os

def plot_totalnodes_to_numssp_ratio(graph_name, c_list, output_folder):
    """
    Plot the ratio of TotalNodes / NumSSP for each node.

    Args:
        graph_name (str): Name of the graph being analyzed.
        dataset_file (str): Path to the dataset file containing TotalNodes and NumSSP values.
    """

    plt.figure(figsize=(12, 6))
    x = list(range(1, 31))

    for c in c_list:
        averaged_file = os.path.join(output_folder, f'{graph_name}_averaged_results3_c{c}.txt')
        with open(averaged_file, 'r') as f:
            lines = f.readlines()[1:]  # Skip the header
            for line in lines:
                parts = line.strip().split()
                print(parts)
            averaged_results = {int(line.split()[0]): float(line.split()[2]) for line in lines}

            top_nodes = sorted(averaged_results.keys(), reverse=True)[:30]
            averaged_values = [averaged_results[node] for node in top_nodes]
            print(averaged_values)
        
        plt.plot(x, averaged_values, label=f'Approximated BC (c={c})', marker='o')


    plt.title(f'Ratio SSP/Totalnodes for {graph_name}')
    plt.xlabel('Top 30 Nodes')
    plt.ylabel('Ratio')
    plt.legend()
    plt.grid()
    plt.tight_layout()

    # Save the plot
    output_plot_path = os.path.join(output_folder, f'{graph_name}_ratio_plot3.png')
    plt.savefig(output_plot_path)
    plt.show()
    print(f" plot saved to {output_plot_path}")

# Example usage
graph_names = ['Rand', 'Cite', 'Crawl', 'Pref-attach', 'Road']
c_list = [2, 3, 4, 5]
output_folder = 'Averages'
for graph_name in graph_names:
    plot_totalnodes_to_numssp_ratio(graph_name, c_list, output_folder)
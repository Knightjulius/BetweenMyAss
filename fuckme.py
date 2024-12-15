import matplotlib.pyplot as plt
import os
from main2 import load_true_betweenness

def plot_approximated_bc(graph_name, c_list, output_folder):
    """
    Plot the averaged approximated BC for every node across all c values.
    """

    plt.figure(figsize=(12, 6))
    x = list(range(1, 31))

    for c in c_list:
        averaged_file = os.path.join(output_folder, f'{graph_name}_averaged_results3_c{c}.txt')
        with open(averaged_file, 'r') as f:
            lines = f.readlines()[1:]  # Skip the header
            averaged_results = {int(line.split()[0]): float(line.split()[1]) for line in lines}

            top_nodes = sorted(averaged_results.keys(), reverse=True)[:30]  # Get top 30 keys
            averaged_values = [averaged_results[node] for node in top_nodes]
            print(averaged_values)
        
        plt.scatter(x, averaged_values, label=f'Approximated BC (c={c})', marker='o')


    plt.title(f'Averaged Approximated BC for {graph_name}')
    plt.xlabel('Top 30 Nodes')
    plt.ylabel('Averaged Approximated BC')
    plt.legend()
    plt.grid()
    plt.tight_layout()

    # Save the plot
    output_plot_path = os.path.join(output_folder, f'{graph_name}_approximated_bc_plot3.png')
    plt.savefig(output_plot_path)
    plt.show()
    print(f"Averaged BC plot saved to {output_plot_path}")

# Example usage for all graphs
graph_names = ['Rand', 'Cite', 'Crawl', 'Pref-attach', 'Road']
c_list = [2, 3, 4, 5]
output_folder = 'Averages'

for graph_name in graph_names:
    plot_approximated_bc(graph_name, c_list, output_folder)

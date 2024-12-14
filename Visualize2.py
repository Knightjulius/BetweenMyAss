import matplotlib.pyplot as plt
import os
from main2 import load_true_betweenness

def plot_error_comparison(graph_name, c_list, output_folder):
    """
    Plot the error between true BC and averaged approximated BC for all c values.
    """
    # Plot the errors
    plt.figure(figsize=(12, 6))
    x = range(1, 31)  # Top 30 nodes
    true_bc_file_path = os.path.join('BetweennessCentrality', f'betweenness_centrality_{graph_name}.txt')
    true_bc = load_true_betweenness(true_bc_file_path)

    # Sort nodes by true BC values and select the top 30 nodes
    top_nodes = sorted(true_bc, key=true_bc.get, reverse=True)[:30]

    for c in c_list:
        averaged_file = os.path.join(output_folder, f'{graph_name}_averaged_results_c{c}.txt')
        with open(averaged_file, 'r') as f:
            lines = f.readlines()[1:]  # Skip the header
            averaged_results = {int(line.split()[0]): float(line.split()[1]) for line in lines}
        
        # Calculate error for top nodes
        error_values = []
        for node in top_nodes:
            true_value = true_bc[node]
            approx_value = averaged_results.get(int(node), 0)
            print(approx_value)
            if true_value != 0:
                error = abs((true_value - approx_value) / true_value) * 100  # Percentage error
            else:
                error = 0  # Handle division by zero
            error_values.append(error)

        plt.plot(x, error_values, label=f'Error (c={c})', marker='x')

    plt.title(f'Error Comparison for {graph_name}')
    plt.xlabel('Top 30 Nodes')
    plt.ylabel('Error Percentage')
    plt.legend()
    plt.grid()
    plt.tight_layout()

    # Save the plot
    output_plot_path = os.path.join(output_folder, f'{graph_name}_error_comparison_plot.png')
    plt.savefig(output_plot_path)
    plt.show()
    print(f"Error plot saved to {output_plot_path}")

# Example usage for all graphs
graph_names = ['Rand', 'Cite', 'Crawl', 'Pref-attach', 'Road']
c_list = [2, 3, 4, 5]
output_folder = 'Averages'

for graph_name in graph_names:
    plot_error_comparison(graph_name, c_list, output_folder)
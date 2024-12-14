from main2 import load_true_betweenness
import networkx as nx
import os

def load_approximated_bc(file_path, top_nodes):
    """
    Load approximated betweenness centrality for top nodes from a result file.
    """
    approximated_bc = {}
    with open(file_path, 'r') as f:
        lines = f.readlines()
        for line in lines[3:]:  # Skip the first 3 lines (metadata and header)
            parts = line.strip().split()
            node_id = int(parts[0])  # Node ID
            approx_bc = float(parts[3])  # Approximated_BC column
            if node_id in top_nodes:
                approximated_bc[node_id] = approx_bc
    return approximated_bc


def average_approx_BC(graph_name, c, output_folder):
    true_bc_file_path = os.path.join('BetweennessCentrality', f'betweenness_centrality_{graph_name}.txt')
    true_bc = load_true_betweenness(true_bc_file_path)

    # Sort nodes by true BC values and select the top 30 nodes
    top_nodes = sorted(true_bc, key=true_bc.get, reverse=True)[:30]

    # Dictionary to store averages
    averaged_results = {}

    for node in top_nodes:
        approx_bc_list = []  # List to store approximated BC for all repetitions
        for rep in range(5):
            result_file = os.path.join('Results2', f'Results_c{c}', f'{graph_name}_results_c{c}_rep{rep}.txt')
            with open(result_file, 'r') as f:
                lines = f.readlines()
                for line in lines[4:]:  # Skip the first 3 lines (metadata and header)
                    parts = line.strip().split()
                    node_id = int(parts[0])  # Node ID
                    if node_id == int(node):
                        approx_bc = float(parts[3])  # Approximated_BC column
                        approx_bc_list.append(approx_bc)

        # Compute the average approximated BC for the node
        averaged_results[node] = sum(approx_bc_list) / len(approx_bc_list) if approx_bc_list else 0

    # Write the averaged results to an output file
    output_file = os.path.join(output_folder, f'{graph_name}_averaged_results_c{c}.txt')
    os.makedirs(output_folder, exist_ok=True)
    with open(output_file, 'w') as f:
        f.write("Node\tAverage_Approximated_BC\n")
        for node, avg_bc in averaged_results.items():
            f.write(f"{node}\t{avg_bc}\n")

    print(f"Averaged results written to {output_file}")
            


graph_names = ['Rand', 'Cite', 'Crawl', 'Pref-attach', 'Road']
c_list = [2,3,4,5]
output_folder = 'Averages'
for graph_name in graph_names:
    for c in c_list:
        average_approx_BC(graph_name, c, output_folder)
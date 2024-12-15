from main2 import load_true_betweenness
import networkx as nx
import os

def average_approx_BC(graph_name, c, output_folder):
    true_bc_file_path = os.path.join('BetweennessCentrality', f'betweenness_centrality_{graph_name}.txt')
    true_bc = load_true_betweenness(true_bc_file_path)

    # Sort nodes by true BC values and select the top 30 nodes
    top_nodes = sorted(true_bc, key=true_bc.get, reverse=True)[:30]

    # Dictionary to store averages
    averaged_results = {}

    for node in top_nodes:
        approx_bc_list = []  # List to store approximated BC for all repetitions
        num_ssp_list = []
        for rep in range(5):
            result_file = os.path.join('Results2', f'ResultsAlt3_c{c}', f'{graph_name}_results_c{c}_rep{rep}.txt')
            with open(result_file, 'r') as f:
                lines = f.readlines()
                for line in lines[4:]:  # Skip the first 3 lines (metadata and header)
                    parts = line.strip().split()
                    node_id = int(parts[0])  # Node ID
                    if node_id == int(node):
                        approx_bc = float(parts[3])  # Approximated_BC column
                        num_ssp = float(parts[6])
                        approx_bc_list.append(approx_bc)
                        num_ssp_list.append(num_ssp)

        # Compute the average approximated BC for the node
        avg_approx_bc = sum(approx_bc_list) / len(approx_bc_list) if approx_bc_list else 0
        avg_num_ssp = sum(num_ssp_list) / len(num_ssp_list) if num_ssp_list else 0
        averaged_results[node] = (avg_approx_bc, avg_num_ssp)

    # Write the averaged results to an output file
    output_file = os.path.join(output_folder, f'{graph_name}_averaged_results3_c{c}.txt')
    os.makedirs(output_folder, exist_ok=True)
    with open(output_file, 'w') as f:
        f.write("Node\tAverage_Approximated_BC\tTotal/Numssp\n")
        for node, (avg_bc, avg_num_ssp) in averaged_results.items():
            f.write(f"{node}\t{avg_bc}\t{avg_num_ssp}\n")

    print(f"Averaged results written to {output_file}")
            


graph_names = ['Rand', 'Cite', 'Crawl', 'Pref-attach', 'Road']
c_list = [2,3,4,5]
output_folder = 'Averages'
for graph_name in graph_names:
    for c in c_list:
        average_approx_BC(graph_name, c, output_folder)
import networkx as nx
import os
import random
import time

class GraphCentralityCalculator:
    def __init__(self, graph, graph_name):
        self.G = graph
        self.graph_name = graph_name  # Save the graph name
        self.node_list = self.G.nodes
        self.shortest_paths = {node: {other_node: [] for other_node in self.node_list} for node in self.node_list}
        self.betweenness = {node: 0 for node in self.node_list}

    def save_num_SSP_to_file(self, num_SSP_dict, output_folder, file_name, calculation_time):
        """Save number of SSPs for each node to a text file."""
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Get the total number of nodes
        total_nodes = len(self.G.nodes)

        # Include the graph name in the file path
        file_path = os.path.join(output_folder, f"{self.graph_name}_{file_name}")
        with open(file_path, 'w') as f:
            f.write(f"Calculation Time (seconds): {calculation_time}\n")
            f.write(f"Total Number of Nodes: {total_nodes}\n")
            f.write("Node\tNumSSP\tNumSSP/TotalNodes\n")
            
            # Write the SSP values and ratios for each node
            for node, num_SSP in num_SSP_dict.items():
                num_SSP_per_node = num_SSP / total_nodes if total_nodes > 0 else 0
                f.write(f"{node}\t{num_SSP}\t{num_SSP_per_node:.6f}\n")

        print(f"Number of SSPs and additional results saved to {file_path}")

    def save_centrality_to_file(self, centrality_dict, output_folder, file_name):
        """Save betweenness centrality results to a text file."""
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Include the graph name in the file path
        file_path = os.path.join(output_folder, f"{self.graph_name}_{file_name}")
        with open(file_path, 'w') as f:
            f.write("Node\tBetweennessCentrality\n")
            for node, centrality in centrality_dict.items():
                f.write(f"{node}\t{centrality}\n")

        print(f"Centrality results saved to {file_path}")

    def save_error_percentage(self, true_bc, approx_bc, output_folder, file_name):
        """Calculate and save the error percentage between true and approximated BC values."""
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        file_path = os.path.join(output_folder, f"{self.graph_name}_{file_name}")
        with open(file_path, 'w') as f:
            f.write("Node\tErrorPercentage\n")
            for node in true_bc:
                if true_bc[node] > 0:
                    error_percentage = (abs(true_bc[node] - approx_bc[node]) / true_bc[node]) * 100
                else:
                    error_percentage = 0  # Avoid division by zero for nodes with true BC == 0
                f.write(f"{node}\t{error_percentage:.6f}\n")

        print(f"Error percentage saved to {file_path}")

    def shortest_path_calculation(self, s):
        for node in self.node_list:
            if len(self.shortest_paths[s][node]) == 0:  # Only calculate if the shortest path is empty
                if nx.has_path(self.G, node, s):  # Check if a path exists
                    new_path = nx.shortest_path(self.G, source=node, target=s)  # Get the shortest path from node to s
                    self.shortest_paths[s][node] = new_path

                    # Propagate the reverse shortest path as well (i.e., from node to s)
                    self.shortest_paths[node][s] = new_path[::-1]  # Reverse the path from s to node

                    # Automatically propagate shortest paths to other nodes
                    for i in range(len(new_path) - 1):
                        u = new_path[i]
                        v = new_path[i + 1]
                        if len(self.shortest_paths[u][v]) == 0:  # If we haven't already added the path
                            self.shortest_paths[u][v] = [u, v]
                            self.shortest_paths[v][u] = [v, u]  # Also store the reverse path
                else:
                    # No path exists between node and s, mark it as empty or some placeholder
                    self.shortest_paths[s][node] = []
                    self.shortest_paths[node][s] = []

    def approximate_BC(self, c):
        n = self.G.number_of_nodes()
        num_SSP_dict = {node: 0 for node in self.node_list}  # Track num_SSP for each node

        for v in self.node_list:
            print(f'Looking at node {v} out of {n}')
            Degree = self.G.degree(v)
            if Degree == 0 or Degree == 1:  # if the degree of v is 0 or 1 then the BC is automatically 0
                self.betweenness[v] = 0
            else:
                S = 0
                k = 0  # Counter for the number of samples

                start_time = time.time()  # Track the start time of the calculations

                while S < c * n:
                    s = random.choice(list(self.G.nodes))  # sample a random node
                    k += 1  # Increment the number of samples
                    self.shortest_path_calculation(s)  # calculate all shortest paths from s to all other nodes
                    num_SSP_dict[v] += 1  # increase number of SSP calcs done for this specific node
                    predecessors = {node: set() for node in self.node_list}  # add all predecessors from the paths from s
                    for target, path in self.shortest_paths[s].items():
                        for i in range(1, len(path)):  # Skip the source vertex
                            predecessors[path[i]].add(path[i-1])  # Add the predecessor to the set
                    total_dependency = 0
                    for target, path in self.shortest_paths[s].items():
                        if target == s:  # Skip the source vertex
                            continue
                        if v in path:
                            total_dependency += 1
                    S += total_dependency
                # used to be = n * S / k
                self.betweenness[v] = S / (k * (n - 1) * (n - 2))

                end_time = time.time()  # Track the end time of the calculations
                calculation_time = end_time - start_time  # Calculate the total calculation time

        return self.betweenness, num_SSP_dict, calculation_time


def load_true_betweenness(file_path):
    """Load true betweenness centrality values from a file."""
    true_bc = {}
    with open(file_path, 'r') as f:
        next(f)  # Skip header
        for line in f:
            node, bc_value = line.strip().split('\t')
            true_bc[node] = float(bc_value)
    return true_bc


def process_graph(input_file, output_folder, c_values):
    # Load the graph from the specified file
    G = nx.read_graphml(input_file)
    graph_name = os.path.basename(input_file).split('.')[0]  # Extract graph name from the file name
    print(f"Processing graph: {graph_name}")
    
    calculator = GraphCentralityCalculator(G, graph_name)

    # Load true betweenness centrality values from the corresponding file
    true_bc_file_path = os.path.join('BetweennessCentrality', f'betweenness_centrality_{graph_name}.txt')
    true_bc = load_true_betweenness(true_bc_file_path)

    for c in c_values:
        print(f"Calculating Betweenness Centrality for c={c}...")
        betweenness, num_SSP_dict, calculation_time = calculator.approximate_BC(c)

        # Create output subfolders for the specific value of c
        c_output_folder_betweenness = os.path.join(output_folder, f"BetweennessResults_{c}")
        c_output_folder_ssp = os.path.join(output_folder, f"SSPCalcs_{c}")
        c_output_folder_error = os.path.join(output_folder, f"ErrorResults_{c}")
        
        if not os.path.exists(c_output_folder_betweenness):
            os.makedirs(c_output_folder_betweenness)
        if not os.path.exists(c_output_folder_ssp):
            os.makedirs(c_output_folder_ssp)
        if not os.path.exists(c_output_folder_error):
            os.makedirs(c_output_folder_error)

        # Save betweenness centrality to the BetweennessResults folder
        calculator.save_centrality_to_file(betweenness, c_output_folder_betweenness, f"betweenness_c{c}.txt")
        
        # Save number of SSP calculations to the SSPCalcs folder
        calculator.save_num_SSP_to_file(num_SSP_dict, c_output_folder_ssp, f"num_SSP_c{c}.txt", calculation_time)
        
        # Calculate and save the error percentage
        calculator.save_error_percentage(true_bc, betweenness, c_output_folder_error, f"error_percentage_c{c}.txt")


def process_all_graphs(input_folder, output_folder, c_values):
    for file_name in os.listdir(input_folder):
        if file_name.endswith('.graphml'):  # Handle .graphml files
            file_path = os.path.join(input_folder, file_name)
            process_graph(file_path, output_folder, c_values)

# Input and output folders, and c values to process
input_folder = 'GraphsNetworkX'  # Folder containing the graph files
output_folder = 'Results'  # Parent folder to save the results
c_values = [2, 3, 4, 5, 8, 10, 15, 20]  # Values of c to iterate over

# Uncomment the next line to process all graphs in the folder
# process_all_graphs(input_folder, output_folder, c_values)


single_graph = "GraphsNetworkX/Test1.graphml"  # Specify the graph file you want to process
c_values = [5]  # Values of c to iterate over
process_graph(single_graph, output_folder, c_values)

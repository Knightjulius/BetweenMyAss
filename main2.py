import networkx as nx
import os
import random
import time
import math

class GraphCentralityCalculator:
    def __init__(self, graph, graph_name):
        self.G = graph
        self.graph_name = graph_name  # Save the graph name
        self.node_list = list(self.G.nodes)
        self.shortest_paths = {node: {other_node: [] for other_node in self.node_list} for node in self.node_list}
        self.betweenness = {node: 0 for node in self.node_list}
        self.betweenness2 = {node: 0 for node in self.node_list}
        self.betweenness3 = {node: 0 for node in self.node_list}
        self.degrees = {node: self.G.degree(node) for node in self.node_list}  # Calculate degrees of nodes
        self.dependencies = {}  # Store dependencies for memoization

    def save_results_to_file(self, true_bc, approx_bc, num_SSP_dict, output_folder, file_name, calculation_time):
        """Save all results to a single file in the specified format."""
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        total_nodes = len(self.G.nodes)

        file_path = os.path.join(output_folder, f"{self.graph_name}_{file_name}")
        with open(file_path, 'w') as f:
            # Write the header
            f.write(f"Total Nodes: {total_nodes}\n")
            f.write(f"Calculation Time (seconds): {calculation_time}\n\n")
            f.write("Node\tDegree\tTrue_BC\tApproximated_BC\tErrorPercentage\tNumSSP\tNumSSP/TotalNodes\n")

            # Write the data for each node
            for node in true_bc:
                degree = self.degrees.get(node, 0)  # Get the degree of the node
                true_bc_value = true_bc[node]
                approx_bc_value = approx_bc.get(node, 0)  # Get the approximated BC value
                error_percentage = (abs(true_bc_value - approx_bc_value) / true_bc_value) * 100 if true_bc_value > 0 else 0
                num_SSP = num_SSP_dict.get(node, 0)  # Get the number of SSP calculations for the node
                num_SSP_per_node = num_SSP / total_nodes if total_nodes > 0 else 0

                f.write(f"{node}\t{degree}\t{true_bc_value}\t{approx_bc_value}\t{error_percentage:.6f}\t{num_SSP}\t{num_SSP_per_node:.6f}\n")

        print(f"Results saved to {file_path}")

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

    def calculate_dependency(self, s, t, v, predecessors):
        # Base case: if s == t, dependency is zero
        if s == t:
            return 0
        
        # Memoize the dependency for the pair (s, t)
        if (s, t, v) in self.dependencies:
            return self.dependencies[(s, t, v)]

        # Initialize the dependency for the pair (s, t)
        dependency = 0

        # Iterate over the predecessors of t
        for w in predecessors[t]:
            # Recursively calculate the dependency for (s, w)
            dep_w = self.calculate_dependency(s, w, v, predecessors)
            # Add to the dependency of (s, t) for vertex v
            dependency += (1 + dep_w)

        # Memoize the result
        self.dependencies[(s, t, v)] = dependency
        return dependency

    def approximate_BC(self, c, top_nodes):
        n = self.G.number_of_nodes()
        num_SSP_dict = {node: 0 for node in self.node_list}  # Track num_SSP for each node
        for v in top_nodes:  # Only iterate over the top nodes
            print(f'Looking at node {v} out of {n}')
            Degree = self.G.degree(v)
            if Degree == 0 or Degree == 1:  # if the degree of v is 0 or 1 then the BC is automatically 0
                self.betweenness[v] = 0
                self.betweenness2[v] = 0
                self.betweenness3[v] = 0
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
                            total_dependency += self.calculate_dependency(s, target, v, predecessors)
                    S += total_dependency
                self.betweenness[v] = S / (k * (n - 1) * (n - 2))
                denominator = 1
                for i in range(1, k + 1):
                    denominator *= (n - i)
                self.betweenness2[v] =  S/ denominator
                self.betweenness3[v] = (n*S)/k

                end_time = time.time()  # Track the end time of the calculations
                calculation_time = end_time - start_time  # Calculate the total calculation time

        return self.betweenness, self.betweenness2, self.betweenness3, num_SSP_dict, calculation_time


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

    # Sort nodes by true BC values and select the top 30 nodes
    top_nodes = sorted(true_bc, key=true_bc.get, reverse=True)[:30]

    for c in c_values:
        print(f"Calculating Betweenness Centrality for c={c}...")

        # Create output folder for the specific value of c
        c_output_folder = os.path.join(output_folder, f"Results_c{c}")
        c_output_folder2 = os.path.join(output_folder, f"ResultsAlt2_c{c}")
        c_output_folder3 = os.path.join(output_folder, f"ResultsAlt3_c{c}")
        
        if not os.path.exists(c_output_folder):
            os.makedirs(c_output_folder)
        if not os.path.exists(c_output_folder2):
            os.makedirs(c_output_folder2)
        if not os.path.exists(c_output_folder3):
            os.makedirs(c_output_folder3)

        for rep in range(5):
            print(f'Repetition {rep}')
            betweenness, betweenness2, betweenness3, num_SSP_dict, calculation_time = calculator.approximate_BC(c, top_nodes)

            # Save all results in a single file
            calculator.save_results_to_file(true_bc, betweenness, num_SSP_dict, c_output_folder, f"results_c{c}_rep{rep}.txt", calculation_time)
            calculator.save_results_to_file(true_bc, betweenness2, num_SSP_dict, c_output_folder2, f"results_c{c}_rep{rep}.txt", calculation_time)
            calculator.save_results_to_file(true_bc, betweenness3, num_SSP_dict, c_output_folder3, f"results_c{c}_rep{rep}.txt", calculation_time)

def process_all_graphs(input_folder, output_folder, c_values):
    for file_name in os.listdir(input_folder):
        if file_name.endswith('.graphml'):  # Handle .graphml files
            file_path = os.path.join(input_folder, file_name)
            process_graph(file_path, output_folder, c_values)

if __name__ == "__main__":

    # Input and output folders, and c values to process
    input_folder = 'GraphsNetworkX'  # Folder containing the graph files
    output_folder = 'Results2'  # Parent folder to save the results
    c_values = [2, 3, 4, 5]  # Values of c to iterate over

    # Uncomment the next line to process all graphs in the folder
    process_all_graphs(input_folder, output_folder, c_values)


    #single_graph = "GraphsNetworkX/Rand.graphml"  # Specify the graph file you want to process
    #process_graph(single_graph, output_folder, c_values)

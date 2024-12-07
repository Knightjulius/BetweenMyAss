import networkx as nx
import os
import random
import time

class GraphCentralityCalculator:
    def __init__(self, graph):
        self.G = graph
        self.node_list = self.G.nodes
        self.shortest_paths = {node: {other_node: [] for other_node in self.node_list} for node in self.node_list}
        self.betweenness = {node: 0 for node in self.node_list}
        self.num_SSP = 0

    def save_centrality_to_file(self, centrality_dict, output_folder, file_name):
        """Save centrality results to a text file."""
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        file_path = os.path.join(output_folder, file_name)
        with open(file_path, 'w') as f:
            f.write("Node\tBetweennessCentrality\n")
            for node, centrality in centrality_dict.items():
                f.write(f"{node}\t{centrality}\n")

        print(f"Centrality results saved to {file_path}")

    def save_num_SSP_to_file(self, num_SSP, output_folder, file_name):
        """Save number of SSPs and additional performance data to a text file."""
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Get the number of nodes in the graph
        num_nodes = self.G.number_of_nodes()
        
        # Calculate the ratio of num_SSP to number of nodes
        num_SSP_per_node = num_SSP / num_nodes if num_nodes > 0 else 0

        # Calculate the time taken for the calculation
        start_time = time.time()  # Starting time at the beginning of the calculation

        # Perform the calculations (assuming some method here)
        approx_time = time.time() - start_time  # Time taken for the calculation

        # Save to file
        file_path = os.path.join(output_folder, file_name)
        with open(file_path, 'w') as f:
            f.write(f"Total Number of SSPs: {num_SSP}\n")
            f.write(f"Number of Nodes: {num_nodes}\n")
            f.write(f"SSP/Number of Nodes: {num_SSP_per_node}\n")
            f.write(f"Calculation Time (seconds): {approx_time}\n")

        print(f"Number of SSP and additional results saved to {file_path}")

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

    def calculate_dependency(self, predecessors, num_paths, dependency, source, nodes_sorted):
        for w in nodes_sorted:
            for v in predecessors[w]:
                fraction = num_paths[v] / num_paths[w]
                dependency[v] += fraction * (1 + dependency[w])
            if w != source:
                pass
        return dependency

    def approximate_BC(self, c):
        n = self.G.number_of_nodes()
        for v in self.node_list:
            print(f'Looking at node{v}') 
            if G.degree(v) == 0: # if the degree of v is 0 then the BC is automatically 0
                self.betweenness[v] = 0
            else:
                S = 0
                k = 0  # Counter for the number of samples

                while S < c * n:
                    s = random.choice(list(self.G.nodes)) # sample a random node
                    k += 1  # Increment the number of samples
                    self.shortest_path_calculation(s) # calculate all shortest paths from s to all other nodes
                    self.num_SSP += 1 # increase number of SSP calcs done
                    predecessors = {node: set() for node in self.node_list} # add all predecessors from the paths from s
                    for target, path in self.shortest_paths[s].items():
                        for i in range(1, len(path)):  # Skip the source vertex
                            predecessors[path[i]].add(path[i-1])  # Add the predecessor to the set
                    total_dependency = 0
                    for target, path in self.shortest_paths[s].items():
                        if target == s:  # Skip the source vertex
                            continue
                        if v in predecessors[target]:
                            total_dependency += 1
                    S += total_dependency
                    print(s, S, c*n)
                self.betweenness[v] = n * S / k
        return self.betweenness


def process_graph(input_file, output_folder, c_values):
    # Load the graph from the specified file
    G = nx.read_graphml(input_file)
    print(f"Processing graph: {input_file}")
    
    calculator = GraphCentralityCalculator(G)

    for c in c_values:
        print(f"Calculating Betweenness Centrality for c={c}...")
        betweenness = calculator.approximate_BC(c)

        # Create output subfolder for the specific value of c
        c_output_folder = os.path.join(output_folder, f"BCApproxC={c}")
        if not os.path.exists(c_output_folder):
            os.makedirs(c_output_folder)

        # Save betweenness centrality and number of SSP to separate files
        calculator.save_centrality_to_file(betweenness, c_output_folder, f"betweenness_c{c}.txt")
        calculator.save_num_SSP_to_file(calculator.num_SSP, c_output_folder, f"num_SSP_c{c}.txt")


def process_all_graphs(input_folder, output_folder, c_values):
    for file_name in os.listdir(input_folder):
        if file_name.endswith('.graphml'):  # Handle .graphml files
            file_path = os.path.join(input_folder, file_name)
            process_graph(file_path, output_folder, c_values)



input_folder = 'GraphsNetworkX'  # Folder containing the graph files
output_folder = 'BetweennessResults'  # Folder to save the results
c_values = [2, 3, 4, 5, 8, 10, 15, 20]  # Values of c to iterate over

# Uncomment the next line to process all graphs in the folder
# process_all_graphs(input_folder, output_folder, c_values)

# Uncomment the next lines to process a single specified graph
# Test for small test graph
n = 20  # Number of vertices
m = 30  # Number of edges
# Generate Erdos-Renyi random graph
G = nx.gnm_random_graph(n, m, seed=42)
nx.write_graphml(G, "GraphsNetworkX/Test1.graphml")
single_graph = "GraphsNetworkX/Test1.graphml"  # Specify the graph file you want to process
c_values = [1]  # Values of c to iterate over
process_graph(single_graph, output_folder, c_values)

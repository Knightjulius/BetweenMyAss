import networkx as nx
import scipy.io
import numpy as np
import tarfile
import requests
import random
import matplotlib as plt
from collections import Counter
import os
import pandas as pd
import time

# Function to read .mtx files (both weighted and unweighted) and create a graph
def read_mtx_file(file_path, weighted=True):
    G = nx.Graph()  # or nx.DiGraph() if the graph is directed
    
    with open(file_path, 'r') as f:
        lines = f.readlines()
        
    # Skip header lines that start with '%%' (Matrix Market metadata)
    matrix_data = [line for line in lines if not line.startswith('%%') and line.strip()]
    
    # Read the edges from the matrix data and add them to the graph
    for line in matrix_data:
        try:
            # Split the line into components
            parts = line.split()
            u, v = int(parts[0]), int(parts[1])  # Convert nodes to integers
            
            if weighted:
                # If the graph is weighted, assume the third element is the weight
                weight = float(parts[2])
                G.add_edge(u, v, weight=weight)
            else:
                # If unweighted, just add the edge without weight
                G.add_edge(u, v)
        except ValueError:
            print(f"Skipping invalid line: {line.strip()}")
    
    return G

def save_centrality_to_file(centrality_dict, output_folder, file_name):
    """Save centrality results to a text file."""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    file_path = os.path.join(output_folder, file_name)
    with open(file_path, 'w') as f:
        f.write("Node\tBetweennessCentrality\n")
        for node, centrality in centrality_dict.items():
            f.write(f"{node}\t{centrality}\n")
    
    print(f"Centrality results saved to {file_path}")

# TODO Donny ik heb dit toegevoegd
# Function to calculate shortest paths
def shortest_path_calculation(shortest_paths, node_list, s, G):
    for node in node_list:
        if len(shortest_paths[s][node]) == 0:  # Only calculate if the shortest path is empty
            new_path = nx.shortest_path(G, source=node, target=s)  # Get the shortest path from node to s
            shortest_paths[s][node] = new_path
            
            # Propagate the reverse shortest path as well (i.e., from node to s)
            shortest_paths[node][s] = new_path[::-1]  # Reverse the path from s to node
            
            # Automatically propagate shortest paths to other nodes
            # If we have A -> B -> C, then we also know B -> C
            for i in range(len(new_path) - 1):
                u = new_path[i]
                v = new_path[i + 1]
                if len(shortest_paths[u][v]) == 0:  # If we haven't already added the path
                    shortest_paths[u][v] = [u, v]
                    shortest_paths[v][u] = [v, u]  # Also store the reverse path

    return shortest_paths

def calculate_dependency(predecessors, num_paths, dependency, source, nodes_sorted):
    for w in nodes_sorted:
        for v in predecessors[w]:
            # λ_sv / λ_sw * (1 + δ_s*(w))
            fraction = num_paths[v] / num_paths[w]
            dependency[v] += fraction * (1 + dependency[w])
        if w != source:
            pass  # Dependency is not propagated to the source
    return dependency

def approximate_BC(G, c):
    n = G.number_of_nodes()
    k = 0  # Counter for the number of samples
    # TODO Donny ik heb dit toegevoegd
    # Initialize shortest paths as a dict with empty entries
    node_list = G.nodes
    shortest_paths = {node: {other_node: [] for other_node in node_list} for node in node_list}
    # running sum set to 0
    # TODO change v
    v = 1
    S = 0
    while S < c * n:
        # Step 4: Choose a random source node
        s = random.choice(list(G.nodes))
        # Step 5: Compute shortest paths from the source
        shortest_paths = shortest_path_calculation(shortest_paths, node_list, s, G)

        # Step 6: get predecessors and lambda
        lambda_sw = {node: 0 for node in node_list}
        lambda_sw[s] = 1

        predecessors = {node: [] for node in node_list}

        for target, path in shortest_paths[s].items():
            # gives all predecessors to s in a path minus s itself
            predecessors[target] = path[:-1]
            # if v is in the path then update the lambda value
            if v in path:
                lambda_sw[target] += 1
    
    	# TODO calculate dependency and update running sum, division by zero error
        # Step 7: calculate dependency
        dependency = {node: 0 for node in node_list}
        # for all nodes in the list 
        for w in node_list:
            # for a predecessor of the node being looked at
            for v in predecessors[w]:

                # λ_sv / λ_sw * (1 + δ_s*(w))
                fraction = lambda_sw[v] / lambda_sw[w]
                S += fraction * (1 + dependency[w])

        
        k += 1  # Increment the number of samples

    # Normalize the betweenness centrality
    betweenness = n*S/k
    return betweenness

# Create a simple graph
G = nx.Graph()
G.add_edges_from([('A', 'B'), ('B', 'C'), ('A', 'D'), ('B', 'E'), ('D', 'E')])

# List of nodes
node_list = list(G.nodes)
c = 1
B = approximate_BC(G, c)
print(B)

import random
import networkx as nx
import time
import os

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

def calculate_dependency(predecessors, num_paths, dependency, source, nodes_sorted):
    for w in nodes_sorted:
        for v in predecessors[w]:
            # λ_sv / λ_sw * (1 + δ_s*(w))
            fraction = num_paths[v] / num_paths[w]
            dependency[v] += fraction * (1 + dependency[w])
        if w != source:
            dependency[w] += 0  # Dependency is not propagated to the source
    return dependency

def calculate_dependency(predecessors, num_paths, dependency, source, nodes_sorted):
    for w in nodes_sorted:
        for v in predecessors[w]:
            # λ_sv / λ_sw * (1 + δ_s*(w))
            fraction = num_paths[v] / num_paths[w]
            dependency[v] += fraction * (1 + dependency[w])
        if w != source:
            dependency[w] += 0  # Dependency is not propagated to the source
    return dependency

def approximate_BC(G, c):
    n = G.number_of_nodes()
    betweenness = {node: 0 for node in G.nodes}  # Initialize betweenness centrality for all nodes
    k = 0  # Counter for the number of samples

    while any(b < c * n for b in betweenness.values()):
        # Step 4: Choose a random source node
        s = random.choice(list(G.nodes))
        # Step 5: Compute shortest paths from the source
        shortest_paths = nx.single_source_shortest_path_length(G, s)
        # Step 6: Initialize λ_sw and predecessors
        lambda_sw = {node: 0 for node in G.nodes}
        lambda_sw[s] = 1
        predecessors = {node: [] for node in G.nodes}

        for node, dist in sorted(shortest_paths.items(), key=lambda x: x[1]):
            for neighbor in G.neighbors(node):
                if shortest_paths.get(neighbor, float('inf')) == dist - 1:
                    lambda_sw[node] += lambda_sw[neighbor]
                    predecessors[node].append(neighbor)

        # Calculate dependencies
        dependency = {node: 0 for node in G.nodes}
        nodes_sorted = sorted(shortest_paths, key=shortest_paths.get, reverse=True)
        dependency = calculate_dependency(predecessors, lambda_sw, dependency, s, nodes_sorted)

        # Update betweenness centrality for all nodes
        for v in G.nodes:
            if v != s:
                betweenness[v] += dependency[v]
        
        k += 1  # Increment the number of samples

    # Normalize the betweenness centrality
    betweenness = {node: b * n / k for node, b in betweenness.items()}
    return betweenness

# Generate Erdos-Renyi random graph
G = nx.read_edgelist('wiki-Vote.txt.gz')
c = 10  # Threshold constant

start_time = time.time()
approx_centrality = approximate_BC(G, c)
approx_time = time.time() - start_time
average_approx_bc = sum(approx_centrality.values()) / len(approx_centrality)
print(f"Approximate Betweenness Centrality for all nodes computed in {approx_time:.4f} seconds")
print(f"Average Approximate Betweenness Centrality: {average_approx_bc:.4f}")

# Measure time for exact betweenness centrality
start_time = time.time()
exact_centrality = nx.betweenness_centrality(G, normalized=False)
exact_time = time.time() - start_time
average_exact_bc = sum(exact_centrality.values()) / len(exact_centrality)
print(f"Exact Betweenness Centrality for all nodes computed in {exact_time:.4f} seconds")
print(f"Average Exact Betweenness Centrality: {average_exact_bc:.4f}")
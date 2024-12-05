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

def approximate_BC(G, v, c):
    #step 1
    sum = 0 
    #step 2
    k = 0 
    #step 3
    n = G.number_of_nodes()
    while sum < c * n:
        #step 4
        s = random.choice(list(G.nodes))
        #step 5
        shortest_paths = nx.single_source_shortest_path_length(G, s)
        #step 6
        lambda_sw = {node: 0 for node in G.nodes} 
        lambda_sw[s] = 1
        predecessors = {node: [] for node in G.nodes}  # P_s(w)

        for node, dist in sorted(shortest_paths.items(), key=lambda x: x[1]):
            for neighbor in G.neighbors(node):
                if shortest_paths.get(neighbor, float('inf')) == dist - 1:
                    lambda_sw[node] += lambda_sw[neighbor]
                    predecessors[node].append(neighbor)

        # fill dependency dictionary
        dependency = {node: 0 for node in G.nodes}
        nodes_sorted = sorted(shortest_paths, key=shortest_paths.get, reverse=True)
        dependency = calculate_dependency(predecessors, lambda_sw, dependency, s, nodes_sorted)

        #step 7
        if v in dependency:
            sum += dependency[v]
        #step 8
        k += 1

    return sum * n / k if k > 0 else 0

# Generate Erdos-Renyi random graph
G = nx.read_edgelist('wiki-Vote.txt.gz')
c = 10  # Threshold constant

start_time = time.time()
approx_centrality = {node: approximate_BC(G, node, c) for node in G.nodes}
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
import random
import networkx as nx
import time

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
G = nx.read_edgelist('output_directory/wb-cs-stanford/wb-cs-stanford.mtx')
target_node = list(G.nodes)[0]
c = 10  # Threshold constant

start_time = time.time()
approx_centrality = approximate_BC(G, target_node, c)
approx_time = time.time() - start_time
print(f"Approximate Betweenness Centrality for node {target_node}: {approx_centrality} (computed in {approx_time:.4f} seconds)")

# Measure time for exact betweenness centrality
start_time = time.time()
exact_centrality = nx.betweenness_centrality(G, normalized=False)
exact_time = time.time() - start_time
print(f"Exact Betweenness Centrality for node {target_node}: {exact_centrality[target_node]} (computed in {exact_time:.4f} seconds)")
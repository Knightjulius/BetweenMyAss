import os
import pandas as pd
import numpy as np

# Define the paths to the folders
true_betweenness_path = "BetweennessCentrality"
approx_betweenness_path = "BetweennessResults"
error_comparison_path = "Errorcomparison"

# Create the Errorcomparison folder if it doesn't exist
if not os.path.exists(error_comparison_path):
    os.makedirs(error_comparison_path)

# List subfolders in BetweennessResults (representing different C values)
c_values = [folder for folder in os.listdir(approx_betweenness_path) if os.path.isdir(os.path.join(approx_betweenness_path, folder))]

# Function to compute the error between true and approximated betweenness centrality
def compute_error(true_bc, approx_bc):
    # Merge true and approximated BC on Node
    merged = pd.merge(true_bc, approx_bc, on='Node', suffixes=('_true', '_approx'))
    
    # Compute the absolute error
    merged['Error'] = np.abs(merged['BetweennessCentrality_true'] - merged['BetweennessCentrality_approx'])
    
    # Compute the percentage error
    merged['PercentageError'] = (merged['Error'] / merged['BetweennessCentrality_true']) * 100
    
    return merged[['Node', 'BetweennessCentrality_true', 'BetweennessCentrality_approx', 'Error', 'PercentageError']]

# Iterate through each value of C
for c_value in c_values:
    c_folder = os.path.join(approx_betweenness_path, c_value)
    
    # Create subfolder for this C value in Errorcomparison
    error_folder = os.path.join(error_comparison_path, c_value)
    if not os.path.exists(error_folder):
        os.makedirs(error_folder)
    
    # List the files in the C folder
    approx_files = [f for f in os.listdir(c_folder) if f.endswith('.txt')]
    
    # Process each graph file
    for approx_file in approx_files:
        graph_name = approx_file.split('_betweenness_c1.txt')[0]  # Extract the graph name
        
        # Load the true and approximated BC data
        true_file_path = os.path.join(true_betweenness_path, f"betweenness_centrality_{graph_name}.txt")
        approx_file_path = os.path.join(c_folder, approx_file)
        
        true_bc = pd.read_csv(true_file_path, sep='\t')
        approx_bc = pd.read_csv(approx_file_path, sep='\t')
        
        # Compute the error
        error_data = compute_error(true_bc, approx_bc)
        
        # Save the error data to a new file in the corresponding error folder
        error_file_path = os.path.join(error_folder, f"error_{graph_name}.txt")
        error_data.to_csv(error_file_path, sep='\t', index=False)
        
        print(f"Processed {graph_name} for C={c_value}")

print("Error computation completed.")
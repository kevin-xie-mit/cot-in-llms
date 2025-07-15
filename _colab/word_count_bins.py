import json
import os

# Bin ranges with labels
bins = {
    (   0,   37): "bin_0", # Bin 1: 0-37 words
    (  37,   70): "bin_1", # Bin 2: 37-70 words
    (  70,  101): "bin_2", # Bin 3: 70-101 words
    ( 101,  137): "bin_3", # Bin 4: 101-137 words
    ( 137,  181): "bin_4", # Bin 5: 137-181 words
    ( 181,  233): "bin_5", # Bin 6: 181-233 words
    ( 233,  297): "bin_6", # Bin 7: 233-297 words
    ( 297,  407): "bin_7", # Bin 8: 297-407 words
    ( 407,  644): "bin_8", # Bin 9: 407-644 words
    ( 644, 12616): "bin_9", # Bin 10: 644-12616 words
}

cot_data_path = "/content/drive/MyDrive/cot-analysis/cot_length"
output_data_path = "/content/drive/MyDrive/cot-analysis/word_count"

for percentile_folder_name in os.listdir(cot_data_path):
    path_0 = os.path.join(cot_data_path, percentile_folder_name)
    for task_folder_name in os.listdir(path_0):
        path_1 = os.path.join(path_0, task_folder_name)
        for model_folder_name in os.listdir(path_1):
            path_2 = os.path.join(path_1, model_folder_name)
            
            # Initialize variables for this model folder
            cot_data = None
            direct_data = None
            cot_file_name = None
            direct_file_name = None
            
            # Load both CoT and direct files
            for file_name in os.listdir(path_2):
                file_path = os.path.join(path_2, file_name)

                if "-cot-" in file_name:
                    with open(file_path, 'r') as f:
                        cot_data = json.load(f)
                        cot_file_name = file_name
                elif "-direct" in file_name:
                    with open(file_path, 'r') as f:
                        direct_data = json.load(f)
                        direct_file_name = file_name

            # Check if both files were found
            if cot_data is None or direct_data is None:
                print(f"ERROR: Missing CoT or direct file in {path_2}")
                continue

            # Create a dictionary for quick lookup of direct data by ID
            direct_data_dict = {d["id"]: d for d in direct_data}

            # Initialize bin collections for this model folder
            bin_collections = {}
            for _, bin_name in bins.items():
                bin_collections[bin_name] = {
                    'cot_outputs': [],
                    'direct_outputs': []
                }

            # Process each CoT output and collect by bin
            for cot_output in cot_data:
                task_id = cot_output["id"]
                output_wc = cot_output["CoT Length"]

                # Find corresponding direct data
                direct_output = direct_data_dict.get(task_id)
                if direct_output is None:
                    print(f"ERROR: No direct data found for task ID {task_id}")
                    continue

                # Find the appropriate bin and collect outputs
                for bin_ranges, bin_name in bins.items():
                    _min, _max = bin_ranges
                    if _min <= output_wc < _max:
                        bin_collections[bin_name]['cot_outputs'].append(cot_output)
                        bin_collections[bin_name]['direct_outputs'].append(direct_output)
                        break

            # Write collected outputs to files for each bin
            for bin_name, collections in bin_collections.items():
                if collections['cot_outputs']:  # Only create files if there are outputs in this bin
                    # Create bin directory structure
                    bin_dir = os.path.join(output_data_path, bin_name, task_folder_name, model_folder_name)
                    os.makedirs(bin_dir, exist_ok=True)

                    # Create file paths using original filenames
                    cot_file_path = os.path.join(bin_dir, cot_file_name)
                    direct_file_path = os.path.join(bin_dir, direct_file_name)

                    # Handle CoT file - append to existing data if file exists
                    if os.path.exists(cot_file_path):
                        with open(cot_file_path, 'r') as f:
                            existing_cot_data = json.load(f)
                        # Append new outputs to existing data
                        combined_cot_data = existing_cot_data + collections['cot_outputs']
                    else:
                        combined_cot_data = collections['cot_outputs']
                    
                    # Write combined CoT data
                    with open(cot_file_path, 'w') as f:
                        json.dump(combined_cot_data, f, indent=2)

                    # Handle direct file - append to existing data if file exists
                    if os.path.exists(direct_file_path):
                        with open(direct_file_path, 'r') as f:
                            existing_direct_data = json.load(f)
                        # Append new outputs to existing data
                        combined_direct_data = existing_direct_data + collections['direct_outputs']
                    else:
                        combined_direct_data = collections['direct_outputs']
                    
                    # Write combined direct data
                    with open(direct_file_path, 'w') as f:
                        json.dump(combined_direct_data, f, indent=2)
                    
                    print(f"Added {len(collections['cot_outputs'])} outputs to {bin_name}/{task_folder_name}/{model_folder_name}")

def analyze_word_count_distributions(data_path=None):
    """
    Analyze and display the distribution of word counts in specified ranges:
    <50, 50-100, 100-150, 150-250, 250-450, >450
    """
    # Define the new bins according to user's specification
    distribution_bins = {
        "<50": (0, 50),
        "50-100": (50, 100),
        "100-150": (100, 150),
        "150-250": (150, 250),
        "250-450": (250, 450),
        ">450": (450, float('inf'))
    }
    
    # Initialize counters for each bin
    bin_counts = {bin_name: 0 for bin_name in distribution_bins.keys()}
    total_count = 0
    word_counts = []
    
    # Use the existing cot_data_path if no custom path is provided
    if data_path is None:
        data_path = cot_data_path
    
    print(f"Analyzing word count distributions from: {data_path}")
    print("=" * 60)
    
    # Traverse the directory structure to collect all word counts
    if os.path.exists(data_path):
        for percentile_folder_name in os.listdir(data_path):
            path_0 = os.path.join(data_path, percentile_folder_name)
            if not os.path.isdir(path_0):
                continue
                
            for task_folder_name in os.listdir(path_0):
                path_1 = os.path.join(path_0, task_folder_name)
                if not os.path.isdir(path_1):
                    continue
                    
                for model_folder_name in os.listdir(path_1):
                    path_2 = os.path.join(path_1, model_folder_name)
                    if not os.path.isdir(path_2):
                        continue
                    
                    # Process each CoT file in this directory
                    for file_name in os.listdir(path_2):
                        if "-cot-" in file_name:
                            file_path = os.path.join(path_2, file_name)
                            try:
                                with open(file_path, 'r') as f:
                                    cot_data = json.load(f)
                                
                                # Extract word counts from this file
                                for item in cot_data:
                                    if "CoT Length" in item:
                                        word_count = item["CoT Length"]
                                        word_counts.append(word_count)
                                        total_count += 1
                                        
                                        # Categorize into appropriate bin
                                        for bin_name, (min_val, max_val) in distribution_bins.items():
                                            if min_val <= word_count < max_val:
                                                bin_counts[bin_name] += 1
                                                break
                                                
                            except (json.JSONDecodeError, FileNotFoundError) as e:
                                print(f"Error reading {file_path}: {e}")
                                continue
    else:
        print(f"Warning: Data path {data_path} does not exist!")
        return
    
    # Display the results
    print(f"Total samples analyzed: {total_count}")
    print(f"Word count range: {min(word_counts) if word_counts else 'N/A'} - {max(word_counts) if word_counts else 'N/A'}")
    print("\nWord Count Distribution:")
    print("-" * 40)
    
    for bin_name, count in bin_counts.items():
        percentage = (count / total_count * 100) if total_count > 0 else 0
        print(f"{bin_name:>10}: {count:>6} samples ({percentage:>5.1f}%)")
    
    print("-" * 40)
    print(f"{'Total':>10}: {total_count:>6} samples (100.0%)")
    
    # Additional statistics
    if word_counts:
        import statistics
        print(f"\nStatistics:")
        print(f"Mean word count: {statistics.mean(word_counts):.1f}")
        print(f"Median word count: {statistics.median(word_counts):.1f}")
        print(f"Standard deviation: {statistics.stdev(word_counts):.1f}")
    
    return bin_counts, word_counts

# Run the analysis if this script is executed directly
if __name__ == "__main__":
    # First run the existing binning code (commented out to avoid execution unless needed)
    # print("Running existing word count binning...")
    
    # Run the new distribution analysis
    print("Analyzing word count distributions...")
    analyze_word_count_distributions()







                
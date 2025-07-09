import os
import json
import subprocess

# For direct

path = '/content/drive/MyDrive/cot-analysis/combined-results'

destination_path = '/content/drive/MyDrive/cot-analysis/cot-length'

def copy_cot_files_with_rsync():
    for task_name in os.listdir(path):
        task_path = os.path.join(path, task_name)
        
        if not os.path.isdir(task_path):
            continue
             
        for model in os.listdir(task_path):
            model_path = os.path.join(task_path, model)
            
            if not os.path.isdir(model_path):
                continue
            
            cot_file = f"{task_name}-cot-greedy-42.result.json"
            cot_src_file = os.path.join(model_path, cot_file)  # Path to source file

            dst_file = os.path.join(os.path.join(destination_path, task_name, model), f"{cot_file}")  # Destination

            if os.path.exists(cot_src_file):
                try:
                    # Process the file and get augmented JSON data
                    augmented_cot_data = aug_cot_length(cot_src_file)  # json content
                    
                    # Ensure destination directory exists
                    os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                    
                    # Save the augmented JSON data to destination file
                    with open(dst_file, 'w', encoding='utf-8') as f:
                        json.dump(augmented_cot_data, f, indent=2, ensure_ascii=False)
                    
                    print(f"Processed and saved: {dst_file}")
                    
                except Exception as e:
                    print(f"Error processing {cot_src_file}: {e}")
            else:
                print(f"File not found: {cot_src_file}")

# Run the processing
print("Starting CoT length analysis and file creation...")
copy_cot_files_with_rsync()

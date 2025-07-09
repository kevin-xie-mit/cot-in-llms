import json
import os

# <50, 50-100, 100-150, 150-250, 250-450, > 450
splits = {
    (0, 49): "0_49",
    (50, 99): "50_99",
    (100, 149): "100_149",
    (150, 249): "150_249",
    (250, 449): "250_449",
    450: "450_"
}

data_path = '/content/drive/MyDrive/cot-analysis/cot-length'
output_path = '/content/drive/MyDrive/cot-analysis/word-count'


def get_direct_mapping(direct_data):
    """
    Given the data to the "Direct" output file, return a dictionary
    mapping task ID --> its corres. output
    """

    mapping = {}  # Dictionary mapping task ID --> the output entry

    for out in direct_data:
        _id = out["id"]

        mapping[_id] = out

    return mapping

def get_bin(cot_length):


    if cot_length >= 450:
        return "450_"

    for _min, _max in splits.keys():
        if _min <= cot_length < _max:
            return splits[(_min, _max)]
            break

    return "NO BIN RANGE FOUND"


def process_file(cot_file_path, direct_file_path):
    """
    For each CoT-Direct file pair, it splits the files into each
    bin.

    Then, it returns a dictionary of them for it to be saved later.
    """

    cot_outputs = {
        "0_49": [],
        "50_99": [],
        "100_149": [],
        "150_249": [],
        "250_449": [],
        "450_": []
    }

    direct_outputs = {
        "0_49": [],
        "50_99": [],
        "100_149": [],
        "150_249": [],
        "250_449": [],
        "450_": []
    }

    # Load the CoT file
    with open(cot_file_path, 'r') as f:
        cot_data = json.load(f)

    # Load the Direct file
    with open(direct_file_path, 'r') as f:
        direct_data = json.load(f)

    direct_mapping = get_direct_mapping(direct_data)  # Get the ID --> output mappings for easy file creation

    # Iterates through each output entry in the CoT file
    for d in cot_data:
        cot_id = d["id"]
        bin = get_bin(d["CoT Length"])  # "bin" is a string for the file path --> this will be the key for the mappings (CoT and Direct)

        cot_outputs[bin].append(d)  # Append that entry to CoT outputs

        # Find the direct_d
        try:
            direct_d = direct_mapping[cot_id]  # Find the same entry
            direct_outputs[bin].append(direct_d)
        except:
            print(f"ERROR: No direct corresponding entry found for {cot_file_path} and {direct_file_path}")

    return cot_outputs, direct_outputs

def create_wc_splits():
    for task_name in os.listdir(data_path):
        task_path = os.path.join(data_path, task_name)

        for model_name in os.listdir(task_path):
            model_path = os.path.join(task_path, model_name)

            cot_file_path = os.path.join(model_path, f"{task_name}-cot-greedy-42.result.json")
            direct_file_path = os.path.join(model_path, f"{task_name}-direct-greedy-42.result.json")

            if not os.path.exists(cot_file_path) or not os.path.exists(direct_file_path):
                print("CoT File Exists? ", os.path.exists(cot_file_path))
                print("Direct File Exists? ", os.path.exists(direct_file_path))
                print("Skipping this path!", cot_file_path)
                print("************")
                continue

            cot_outputs, direct_outputs = process_file(cot_file_path, direct_file_path)

            # cot_outputs, direct_outputs are both dictionaries with lists.
            # Iterate through, output in the correct paths

            for bin_name, cot_data in cot_outputs.items():
                out_dir = os.path.join(output_path, bin_name, task_name, model_name)

                cot_out_file_path = os.path.join(out_dir, f"{task_name}-cot-greedy-42.result.json")
                direct_out_file_path = os.path.join(out_dir, f"{task_name}-direct-greedy-42.result.json")

                os.makedirs(out_dir, exist_ok=True)

                # Dump out CoT
                with open(cot_out_file_path, 'w') as cot_f:
                    json.dump(cot_data, cot_f, indent=4, ensure_ascii=False)

                # Dump out corresponding Direct
                with open(direct_out_file_path, 'w') as direct_f:
                    json.dump(direct_outputs[bin_name], direct_f, indent=4, ensure_ascii=False)


    print("Done!")

    return None
        

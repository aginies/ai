import json
import os

lorafile = "lora.json"
def create_lora_json(directory):
    # List to hold file information
    files_info = []
    
    for filename in os.listdir(directory):
        if filename.endswith(".safetensors"):
            description = f"{filename.split('.')[0]}"
            file_info = {
                "filename": filename,
                "description": description
            }
            files_info.append(file_info)
    
    lora_json_path = os.path.join(directory, lorafile)
    
    with open(lora_json_path, 'w') as json_file:
        json.dump(files_info, json_file, indent=4)
    
    print(f"{lorafile} has been created at: {lora_json_path}")

# Replace with the path to your directory
directory_path = '.' 
create_lora_json(directory_path)

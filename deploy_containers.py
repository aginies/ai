#!/usr/bin/python3
"""
 quickly deploy all AI services
 Apache_tika  OpenWebUI  SearXNG ComfyUI_AMD ollama
# antoine@ginies.org
"""

import shutil
import subprocess
import os
import systemd.daemon
import systemd.journal
import yaml

# USER VALUE
VALUE_IPADDR = "10.0.1.38"
VALUE_MODELS = "/mnt/data/models"
VALUE_DATADIR = "/home/aginies/"
VALUE_GFX = "11.0.0"

# SERVICE TO ENABLE
SERVICES = ["Apache_tika", "ollama", "SearXNG", "OpenWebUI", "ComfyUI_AMD"]

# SYSTEM VAR CHANGE ONLY IF YOU NEED TO DO IT
SYSTEMDSYS = "/etc/systemd/system"

def copy_service_file(source_path, destination_path):
    """ copy the service file to correct place on the system """
    # source_service_file = "/path/to/your/service-file.service"
    # destination_service_file = "/etc/systemd/system/service-file.service"
    try:
        # Ensure the destination directory exists
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)

        # Copy the file
        shutil.copy2(source_path, destination_path)
        print(f"Successfully copied {source_path} to {destination_path}")
    except Exception as err:
        print(f"Failed to copy file: {err}")

def reload_systemd():
    """ reload list of services """
    try:
        # Execute systemctl daemon-reload command
        subprocess.run(["systemctl", "daemon-reload"], check=True)
        print("Systemd daemon reloaded successfully")
    except subprocess.CalledProcessError as err:
        print(f"Failed to reload systemd daemon: {err}")


def enable_service(srv_name):
    """ enable the systemd servive """
    try:
        # Construct the systemctl command to enable the service
        cmd = f"systemctl enable {srv_name}"
        os.system(cmd)
        systemd.journal.send(f"Enabled service: {srv_name}")
    except Exception as err:
        systemd.journal.send(f"Failed to enable service {srv_name}: {err}", priority=systemd.journal.LOG_ERR)

def start_service(srv_name):
    """ start systemd service """
    try:
        # Construct the systemctl command to start the service
        cmd = f"systemctl start {srv_name}"
        os.system(cmd)
        systemd.journal.send(f"Started service: {srv_name}")
    except Exception as err:
        systemd.journal.send(f"Failed to start service {srv_name}: {err}", priority=systemd.journal.LOG_ERR)

def find_service_file(directory):
    """ find the service file """
    try:
        # List all files in the directory
        for file_name in os.listdir(directory):
            if file_name.endswith(".service"):
                return os.path.join(directory, file_name)
        return None
    except Exception as err:
        print(f"Failed to find service file in {directory}: {err}")
        return None

def find_docker_compose_file(directory):
    try:
        # List all files in the directory
        for file_name in os.listdir(directory):
            if file_name == "docker-compose.yaml":
                return os.path.join(directory, file_name)
        return None
    except Exception as e:
        print(f"Failed to find docker-compose.yaml in {directory}: {e}")
        return None

def modify_env_var_in_srv_file(file_path, var, value):
    """ modify the service file to reflect user need"""
    try:
    # Read the content of the file
        with open(file_path, 'r') as file:
            lines = file.readlines()

            # Modify the line if it contains the environment variable to change
            modified_lines = []
            for line in lines:
                if line.startswith(f"Environment={var}="):
                    # Split the line into parts and replace the value of the environment variable
                    parts = line.split('=')
                    parts[1] = f"{value}:{parts[1].split(':')[1]}"
                    modified_lines.append('='.join(parts))
                else:
                    modified_lines.append(line)

            # Write the modified content back to the file
            with open(file_path, 'w') as file:
                file.writelines(modified_lines)

            print(f"Successfully modified {file_path}")
    except Exception as err:
        print(f"Failed to modify {file_path}: {err}")

def modify_volumes_in_docker_compose_file(file_path, srv_name, new_volumes):
    try:
        # Read the content of the file
        with open(file_path, 'r') as file:
            compose_data = yaml.safe_load(file)
        if compose_data and isinstance(compose_data, dict) and 'services' in compose_data:
            services = compose_data['services']
            services[srv_name]['volumes'] = new_volumes
            with open(file_path, 'w') as file:
                yaml.safe_dump(compose_data, file)
                print(f"Successfully modified volumes in {file_path} for service {srv_name}")
        else:
            print(f"Service '{srv_name}' not found in docker-compose.yaml")

    except Exception as err:
        print(f"Failed to modify {file_path}: {err}")

if __name__ == "__main__":
    """
    Main actions of the script
    """
    ENV_VARS = {
        "MODELS": VALUE_MODELS,
        "IPADDR": VALUE_IPADDR,
        "DATADIR": VALUE_DATADIR,
        "GFX": VALUE_GFX,
    }
    all_srv = ""
    for service_name in SERVICES:
        all_srv = service_name+" "+all_srv
    print(f"Script to deploy {all_srv} containers")
    print("The following environment variables will be used:")
    for key, value in ENV_VARS.items():
        print(f"{key}: {value}")

    USER_INPUT = input("Press Enter to continue...")    
    if USER_INPUT != "":
        print("Script execution aborted.")
        exit()

    for service_name in SERVICES:
        src_dir = service_name
        src_srv_file = find_service_file(src_dir)
        if src_srv_file is None:
            print(f"No .service file found in {src_dir}.")
            continue
        else:
            dest_srv_file = os.path.join(SYSTEMDSYS, os.path.basename(src_srv_file))
            # Copy the service file
            copy_service_file(src_srv_file, dest_srv_file)
            for ENV_VARS, value in ENV_VARS.items():
                modify_env_var_in_srv_file(dest_srv_file, ENV_VARS, value)

            # Reload systemd to recognize the new services
            reload_systemd()

            enable_service(src_srv_file)
            start_service(src_srv_file)

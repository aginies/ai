#!/usr/bin/python3
"""
 quickly deploy all AI services
 Apache_tika  OpenWebUI  SearXNG ollama
 ComfyUI_AMD
 antoine@ginies.org
"""

import shutil
import subprocess
import os
import sys
import systemd.journal
from systemd import journal
import yaml
import time

# USER VALUE; ADJUST TO YOUR NEED
VALUE_IPADDR_SEARXNG = "192.168.122.99"
VALUE_IPADDR_COMFYUI = "192.168.122.99"
VALUE_IPADDR_OLLAMA = "192.168.122.99"
VALUE_IPADDR_NGINX = "192.168.122.99"
VALUE_MODELS = "/data/models"
VALUE_DATADIR = "/data/"
VALUE_GFX = "11.0.0"

class ServiceData:
    def __init__(self, name, containername, imagename, servicename, ):
        self.name = name
        self.containername = containername
        self.imagename = imagename
        self.servicename = servicename

apache_tika = ServiceData(name='Apache_tika',
                          containername='tika',
                          imagename='docker.io/apache/tika:latest-full',
                          servicename='apache-tika.service',
                          )
ollama = ServiceData(name='ollama',
                     containername='ollama',
                     imagename='docker.io/ollama/ollama:rocm',
                     servicename='ollama.service',
                     )
searxng = ServiceData(name='SearXNG',
                     containername='searxng',
                     imagename='docker.io/searxng/searxng',
                     servicename='searxng.service',
                      )
open_webui = ServiceData(name='OpenWebUI',
                     containername='open-webui',
                         imagename='ghcr.io/open-webui/open-webui:main',
                     servicename='openwebui.service',
                      )

# container name
CONTAINERS = ["apache-tika", "searxng", "ollama", "open-webui"]
# SERVICE TO ENABLE
#SERVICES = ["Apache_tika", "ollama", "SearXNG", "OpenWebUI"] #, "ComfyUI_AMD"]
DATA_SERVICES = [apache_tika, searxng, ollama, open_webui]

SERVICES = [service.name for service in DATA_SERVICES]
SERVICES_TO_REMOVE = [service.servicename for service in DATA_SERVICES]
CONTAINERS = [service.containername for service in DATA_SERVICES]
IMAGES = [service.imagename for service in DATA_SERVICES]

SYSTEMDSYS = "/etc/systemd/system"

ENV_VARS = {
    "IPADDR_SEARXNG": VALUE_IPADDR_SEARXNG,
    "IPADDR_COMFYUI": VALUE_IPADDR_COMFYUI,
    "IPADDR_OLLAMA": VALUE_IPADDR_OLLAMA,
    "MODELS": VALUE_MODELS,
    "DATADIR": VALUE_DATADIR,
    "GFX": VALUE_GFX,
}

def system_command(cmd):
    """
    Launch a system command
    """
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    proc.wait()
    out, errs = proc.communicate(timeout=5)
    #out = str(out, 'UTF-8')
    out = out.decode('utf-8')
    errs = errs.decode('utf-8')
    print(out, errs)
    return out, errs

def cleanup():
    """ clean everything wich has been done """
    for srv_name in SERVICES_TO_REMOVE:
        srv_file = os.path.join(SYSTEMDSYS, os.path.basename(srv_name))
        print(srv_file)
        if os.path.exists(srv_file) == False:
            print(f"No {srv_file} found.")
            continue
        else:
            print(f"Stopping {srv_file}")
            stop_service(srv_name)
            print(f"Removing {srv_file}")
            rm_command = "rm -f " + srv_file
            system_command(rm_command)

    for container in CONTAINERS:
        print(f"Removing {container}")
        podman_rm_command = "podman rm -f "+ container
        system_command(podman_rm_command)

    for image in IMAGES:
        print(f"Removing {image}")
        podman_rmi_command = "podman rmi -f "+ image
        system_command(podman_rmi_command)

def ensure_directories_exist(directories):
    for directory in directories:
        # Check if the directory exists, if not create it
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")
        else:
            print(f"Directory already exists: {directory}")


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
    try:
        # Run the systemctl command to start the service
        result = subprocess.run(['systemctl', 'start', srv_name], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print((result.stdout).decode('utf-8'))
    except subprocess.CalledProcessError as err:
        print(f"Failed to start service '{srv_name}'. Error: {err.stderr}")

def stop_service(srv_name):
    try:
        result = subprocess.run(['systemctl', 'stop', srv_name], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print((result.stdout).decode('utf-8'))
    except subprocess.CalledProcessError as err:
        print(f"Failed to stop service '{srv_name}'. Error: {err.stderr}")

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

def modify_env_var_in_srv_file(file_path):
    """ modify the service file to reflect user needs"""
    try:
        for var, value in ENV_VARS.items():
            modified = False
            with open(file_path, 'r') as file:
                content = file.readlines()
            # Iterate over each line in the file
            for i, line in enumerate(content):
                # Strip any leading or trailing whitespace
                stripped_line = line.strip()
                #print(f"Line {i}: '{stripped_line}'")
                if stripped_line.startswith(f"Environment={var}="):
                    content[i] = f"Environment={var}={value}\n"
                    modified = True
                    break
            if modified:
                with open(file_path, 'w') as file:
                    file.writelines(content)

    except Exception as err:
        print(f"Failed to modify {file_path}: {err}")

def modify_searxng_settings():
    file_path = '/etc/searxng/settings.yml'
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)

    if 'ui' in data and 'formats' in data['ui']:
        if '- html' in data['ui']['formats']:
            # Append '- json' to the formats list
            data['ui']['formats'].append('- json')
        else:
            print("'- html' not found in the formats list.")
    else:
        print("'ui' section or 'formats' key not found.")

    with open(file_path, 'w') as file:
        yaml.safe_dump(data, file, default_flow_style=False)

    print("YAML file has been updated successfully.")

def replace_ip_in_nginx_config(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    # Replace occurrences of 10.0.1.38 with the new IP address
    updated_content = content.replace('10.0.1.38', VALUE_IPADDR_NGINX)

    with open(file_path, 'w') as file:
        file.write(updated_content)

def install_and_configure_nginx():
    # Run zypper to install nginx
    install_command = "zypper in -y nginx"
    system_command(install_command)
    # Create the nginx/certificates directory
    mkdir_cmd = "mkdir -p /etc/nginx/certificates"
    system_command(mkdir_cmd)

    # Run openssl to generate certificates
    openssl_cmd = "openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/nginx/certificates/selfsigned.key -out /etc/nginx/certificates/selfsigned.crt"
    system_command(openssl_cmd)

    # Copy the OpenWebUI configuration to nginx's conf.d directory
    cp_command = "cp OpenWebUI/open-webui.conf /etc/nginx/conf.d"
    system_command(cp_command)
    subprocess.run(cp_command, check=True)
    replace_ip_in_nginx_config("/etc/nginx/conf.d/open-webui.conf")

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
    if len(sys.argv) > 1 and sys.argv[1] == "--clean":
        cleanup()
        exit(0)

    directories_to_check = [ VALUE_DATADIR, VALUE_MODELS ]
    ensure_directories_exist(directories_to_check)
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

    # nginx is not a container yet...
    install_and_configure_nginx()
    start_service(nginx)

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
            print("Doing all adjustement if needed")
            modify_env_var_in_srv_file(dest_srv_file)

            # Reload systemd to recognize the new services
            reload_systemd()
            srv_file = os.path.basename(dest_srv_file)
            enable_service(srv_file)
            start_service(srv_file)
            # need to modify the searxng config to support json, do it after starting the servive
            # to be sure that the settings.yml is present
            if srv_file == "searxng.service" :
                print("Waiting 10 sec to get service up")
                time.sleep(10)
                stop_service(srv_file)
                modify_searxng_settings()
                print("Re starting the service with new config")
                start_service(srv_file)
